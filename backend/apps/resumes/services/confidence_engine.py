import logging
from django.db import transaction
from ..models import Resume, ResumeSection, ConfidenceScore
from .confidence_rules import (
    SOURCE_RELIABILITY,
    ENTITY_BOOSTS,
    SECTION_BOOSTS,
    determine_status,
    check_name_semantic,
    check_skill_semantic,
    check_company_semantic,
)
from .confidence_utils import AgreementCalculator, ContextAnalyzer

logger = logging.getLogger(__name__)


class ConfidenceEngine:
    """
    Orchestrator to calculate, persist, and explain entity confidence scores.
    """

    def __init__(self):
        pass

    def evaluate_field(self, field_name: str, value, resume: Resume) -> dict:
        """
        Calculates confidence score, source, rationale, and status for a single field/value.
        """
        if value is None or value == "" or value == []:
            return {
                "value": "",
                "confidence": 0.0,
                "source": "gemini",
                "reason": "Field is empty or null",
                "status": "rejected"
            }

        regex_data = resume.regex_json or {}
        spacy_data = resume.spacy_json or {}
        gemini_data = resume.ai_json or {}

        # 1. Infer primary source
        source = self._infer_source(field_name, value, regex_data, spacy_data, gemini_data)
        base_score = SOURCE_RELIABILITY.get(source, 90.0)
        reasons = [f"Base score {base_score} ({source})"]

        # 2. Agreement Boost/Override
        # If we have multiple sources extracting, we boost
        agreement_override, agreed_sources = AgreementCalculator.calculate_agreement(
            field_name, value, regex_data, spacy_data, gemini_data
        )

        score = base_score
        if agreement_override == 100.0:
            score = 100.0
            reasons.append("Full agreement across multiple sources (100)")
        elif agreement_override > 0:
            score += agreement_override
            reasons.append(f"Partial agreement boost (+{agreement_override}) from {', '.join(agreed_sources)}")

        # 3. Position / Context Boost
        # Header boost for contact details/name
        is_header_field = field_name in ["name", "email", "phone", "linkedin", "github", "portfolio", "personal_website"]
        if is_header_field and resume.extracted_text:
            if ContextAnalyzer.is_in_header(value, resume.extracted_text):
                score += 10.0
                reasons.append("Header area boost (+10)")

        # 4. Section Boost
        sections_qs = ResumeSection.objects.filter(resume=resume)
        
        # Education block boost
        if field_name == "education" or "education" in field_name:
            if ContextAnalyzer.is_in_section(value, "education", sections_qs):
                score += 10.0
                reasons.append("Education section match boost (+10)")
        
        # Skills block boost
        if field_name in ["skills", "technical_skills", "soft_skills"] or "skill" in field_name:
            if ContextAnalyzer.is_in_section(value, "skills", sections_qs):
                score += 10.0
                reasons.append("Skills section match boost (+10)")

        # Experience block boost
        if field_name == "experience" or "company" in field_name or "experience" in field_name:
            if ContextAnalyzer.is_in_section(value, "experience", sections_qs):
                score += 10.0
                reasons.append("Experience section match boost (+10)")

        # Projects block boost
        if field_name == "projects" or "project" in field_name:
            if ContextAnalyzer.is_in_section(value, "projects", sections_qs):
                score += 10.0
                reasons.append("Projects section match boost (+10)")

        # 5. Entity Boosts
        if field_name == "name":
            score += ENTITY_BOOSTS.get("PERSON", 10.0)
            reasons.append("PERSON entity boost (+10)")
        elif field_name == "email":
            score += ENTITY_BOOSTS.get("EMAIL", 20.0)
            reasons.append("EMAIL entity boost (+20)")
        elif field_name == "phone":
            score += ENTITY_BOOSTS.get("PHONE", 20.0)
            reasons.append("PHONE entity boost (+20)")
        elif field_name in ["linkedin", "github", "portfolio"]:
            entity_key = field_name.upper()
            score += ENTITY_BOOSTS.get(entity_key, 20.0)
            reasons.append(f"{entity_key} entity boost (+20)")

        # 6. Semantic Drops (Penalties)
        if field_name == "name":
            penalty, penalty_reason = check_name_semantic(str(value))
            if penalty < 0:
                score += penalty
                reasons.append(f"{penalty_reason} ({penalty})")
        
        if field_name in ["skills", "technical_skills", "soft_skills"] or "skill" in field_name:
            penalty, penalty_reason = check_skill_semantic(str(value))
            if penalty < 0:
                score += penalty
                reasons.append(f"{penalty_reason} ({penalty})")

        if "company" in field_name:
            penalty, penalty_reason = check_company_semantic(str(value))
            if penalty < 0:
                score += penalty
                reasons.append(f"{penalty_reason} ({penalty})")

        # Clamp score between 0 and 100
        final_score = max(0.0, min(100.0, score))
        if final_score != score:
            reasons.append(f"Clamped to final score {final_score}")

        status = determine_status(final_score)

        return {
            "value": str(value),
            "confidence": round(final_score, 1),
            "source": source,
            "reason": "; ".join(reasons),
            "status": status
        }

    def evaluate_resume(self, resume: Resume) -> dict:
        """
        Parses all fields of master_resume_json and returns a full confidence map.
        """
        master_json = resume.master_resume_json or {}
        confidence_map = {}

        for field_name, value in master_json.items():
            if value is None or value == "" or value == []:
                confidence_map[field_name] = {
                    "value": "",
                    "confidence": 0.0,
                    "source": "gemini",
                    "reason": "Field is empty",
                    "status": "rejected"
                }
                continue

            # Check complex fields vs simple fields
            if isinstance(value, list):
                if not value:
                    confidence_map[field_name] = {
                        "value": "[]",
                        "confidence": 0.0,
                        "source": "gemini",
                        "reason": "List is empty",
                        "status": "rejected"
                    }
                elif all(isinstance(x, str) for x in value):
                    # List of strings (e.g. skills, certifications)
                    sub_results = [self.evaluate_field(field_name, item, resume) for item in value]
                    avg_conf = sum(x["confidence"] for x in sub_results) / len(sub_results)
                    reasons = [x["reason"] for x in sub_results]
                    confidence_map[field_name] = {
                        "value": ", ".join(value),
                        "confidence": round(avg_conf, 1),
                        "source": sub_results[0]["source"] if sub_results else "gemini",
                        "reason": f"Averaged over list items: {'; '.join(list(set(reasons))[:3])}",
                        "status": determine_status(avg_conf)
                    }
                else:
                    # List of complex objects (e.g. education, experience, projects)
                    sub_results = []
                    for idx, obj in enumerate(value):
                        if not isinstance(obj, dict):
                            continue
                        # Evaluate key fields of the objects (like institution or company)
                        if field_name == "education":
                            sub_val = obj.get("institution") or obj.get("degree") or ""
                        elif field_name == "experience":
                            sub_val = obj.get("company") or obj.get("designation") or ""
                        elif field_name == "projects":
                            sub_val = obj.get("title") or ""
                        else:
                            sub_val = str(obj)

                        sub_results.append(self.evaluate_field(f"{field_name}_{idx}", sub_val, resume))

                    if sub_results:
                        avg_conf = sum(x["confidence"] for x in sub_results) / len(sub_results)
                        confidence_map[field_name] = {
                            "value": f"List of {len(value)} entries",
                            "confidence": round(avg_conf, 1),
                            "source": "gemini",
                            "reason": f"Averaged over {len(sub_results)} complex objects",
                            "status": determine_status(avg_conf)
                        }
                    else:
                        confidence_map[field_name] = {
                            "value": "[]",
                            "confidence": 90.0,
                            "source": "gemini",
                            "reason": "Parsed structure list contains no valid fields",
                            "status": "accepted"
                        }
            else:
                # Flat field string/number
                confidence_map[field_name] = self.evaluate_field(field_name, value, resume)

        return confidence_map

    @transaction.atomic
    def evaluate_and_save(self, resume: Resume) -> dict:
        """
        Calculates confidence scores, saves them to ConfidenceScore model database records, and returns the result map.
        """
        confidence_map = self.evaluate_resume(resume)

        # Clear old values
        ConfidenceScore.objects.filter(resume=resume).delete()

        # Save new values
        for field_name, details in confidence_map.items():
            ConfidenceScore.objects.create(
                resume=resume,
                field=field_name,
                value=details["value"],
                confidence=details["confidence"],
                source=details["source"],
                reason=details["reason"],
                status=details["status"]
            )

        return confidence_map

    def _infer_source(self, field_name: str, value: str, regex_data: dict, spacy_data: dict, gemini_data: dict) -> str:
        """
        Infers which engine originally extracted this value.
        """
        val_clean = str(value).strip().lower()

        # 1. Check regex match
        r_val = regex_data.get(field_name)
        if r_val:
            if isinstance(r_val, list):
                if any(str(x).strip().lower() == val_clean for x in r_val):
                    return "regex"
            elif str(r_val).strip().lower() == val_clean:
                return "regex"

        # 2. Check spacy match
        s_val = spacy_data.get(field_name)
        if s_val:
            if isinstance(s_val, list):
                if any(str(x).strip().lower() == val_clean for x in s_val):
                    return "spacy"
            elif str(s_val).strip().lower() == val_clean:
                return "spacy"

        # 3. Check gemini match
        g_val = gemini_data.get(field_name)
        if g_val:
            if isinstance(g_val, list):
                if any(str(x).strip().lower() == val_clean for x in g_val):
                    return "gemini"
            elif str(g_val).strip().lower() == val_clean:
                return "gemini"

        # Default fallback rules based on field priority
        if field_name in ["email", "phone", "linkedin", "github", "portfolio"]:
            return "regex"
        elif field_name == "name":
            return "spacy"
        return "gemini"
