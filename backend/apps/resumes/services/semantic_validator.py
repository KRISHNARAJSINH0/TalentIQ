import logging
from typing import Dict, List, Any, Optional, Tuple

from .entity_classifier import EntityClassifier
from .ontology_engine import VALIDATION_CATEGORIES

logger = logging.getLogger(__name__)

# Mapping from resume field keys to expected semantic categories & sections
FIELD_TO_EXPECTED_CATEGORY: Dict[str, Tuple[str, str]] = {
    "name": ("PERSON", "header"),
    "full_name": ("PERSON", "header"),
    "email": ("PERSON", "header"),
    "phone": ("PERSON", "header"),
    "company": ("COMPANY", "experience"),
    "employer": ("COMPANY", "experience"),
    "organization": ("ORGANIZATION", "experience"),
    "university": ("UNIVERSITY", "education"),
    "college": ("UNIVERSITY", "education"),
    "institution": ("UNIVERSITY", "education"),
    "school": ("UNIVERSITY", "education"),
    "degree": ("UNIVERSITY", "education"),
    "education": ("UNIVERSITY", "education"),
    "skills": ("SKILL", "skills"),
    "skill": ("SKILL", "skills"),
    "technical_skills": ("SKILL", "skills"),
    "soft_skills": ("SKILL", "skills"),
    "certifications": ("CERTIFICATE", "certifications"),
    "certification": ("CERTIFICATE", "certifications"),
    "certificate": ("CERTIFICATE", "certifications"),
    "designation": ("DESIGNATION", "experience"),
    "role": ("ROLE", "experience"),
    "title": ("DESIGNATION", "experience"),
    "job_title": ("DESIGNATION", "experience"),
    "projects": ("PROJECT", "projects"),
    "project": ("PROJECT", "projects"),
    "project_name": ("PROJECT", "projects"),
    "languages": ("LANGUAGE", "languages"),
    "language": ("LANGUAGE", "languages"),
    "country": ("COUNTRY", "header"),
    "city": ("CITY", "header"),
    "date": ("DATE", "experience"),
    "dates": ("DATE", "experience"),
    "publications": ("PUBLICATION", "publications"),
    "publication": ("PUBLICATION", "publications"),
    "awards": ("AWARD", "awards"),
    "award": ("AWARD", "awards")
}

CATEGORY_TO_MOVE_ACTION: Dict[str, str] = {
    "UNIVERSITY": "move_to_education",
    "SKILL": "move_to_skills",
    "TECHNOLOGY": "move_to_skills",
    "DESIGNATION": "move_to_experience",
    "ROLE": "move_to_experience",
    "COMPANY": "move_to_experience",
    "ORGANIZATION": "move_to_experience",
    "PERSON": "move_to_header",
    "CERTIFICATE": "move_to_certifications",
    "LANGUAGE": "move_to_languages",
    "PUBLICATION": "move_to_publications",
    "AWARD": "move_to_awards",
    "PROJECT": "move_to_projects",
    "DATE": "move_to_dates"
}


class SemanticValidator:
    """
    Main Semantic Validator Orchestrator for ResumeAI.
    Validates extracted entity meanings, detects semantic anomalies, assigns scores (0-100),
    determines status (valid, possible, suspicious, invalid), triggers actions (accept, review, recover, move, reject),
    and provides explainable semantic rationales.
    """

    def __init__(self):
        self.classifier = EntityClassifier()

    def validate_entity(self, field_name: str, value: Any) -> Dict[str, Any]:
        """
        Validates a single field/value pair semantically.
        """
        if value is None or value == "" or value == []:
            return {
                "value": "",
                "category": "UNKNOWN",
                "expected_category": self._get_expected_category(field_name),
                "semantic_score": 0,
                "status": "invalid",
                "action": "reject",
                "reason": "Value is null or empty"
            }

        val_str = str(value).strip()
        expected_cat, target_section = FIELD_TO_EXPECTED_CATEGORY.get(
            field_name.lower(), (self._infer_category_from_fieldname(field_name), "general")
        )

        # Classify the entity value
        classification = self.classifier.classify_entity(val_str, context_section=target_section)
        detected_cat = classification["top_category"]
        detected_score = classification["confidence_score"]
        explanation = classification["explanation"]

        # Check for category match vs anomaly
        is_category_match = self._are_categories_compatible(expected_cat, detected_cat)

        if is_category_match:
            semantic_score = int(min(100, max(0, detected_score)))
            status = self._score_to_status(semantic_score)
            action = "accept" if semantic_score >= 90 else ("review" if semantic_score >= 75 else "recover")
            reason = f"Valid entity. {explanation}"
        else:
            # Semantic Anomaly Detected!
            semantic_score = int(min(100, max(0, detected_score)))

            # Special case rule handling (e.g. Google inside Project -> Maybe company. Review.)
            if expected_cat in ["PROJECT", "ORGANIZATION"] and detected_cat == "COMPANY":
                status = "suspicious"
                action = "review"
                reason = "Maybe company. Review."
                semantic_score = 75
            else:
                status = "invalid" if semantic_score >= 80 or semantic_score < 50 else "suspicious"
                action = CATEGORY_TO_MOVE_ACTION.get(detected_cat, "move")
                reason = f"Entity matches {detected_cat.lower()} ontology, expected {expected_cat.capitalize()}. {explanation}"

        return {
            "value": val_str,
            "category": self._format_category_name(detected_cat),
            "expected_category": self._format_category_name(expected_cat),
            "semantic_score": semantic_score,
            "status": status,
            "action": action,
            "reason": reason
        }

    def validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates an entire extracted resume JSON dictionary payload.
        Handles flat string fields, arrays of strings, and lists of structured objects.
        """
        validations: List[Dict[str, Any]] = []
        valid_count = 0
        anomaly_count = 0
        total_score = 0

        for field_name, value in payload.items():
            if isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        # Validate sub-fields of object
                        for sub_k, sub_v in item.items():
                            res = self.validate_entity(sub_k, sub_v)
                            res["field"] = f"{field_name}[{idx}].{sub_k}"
                            validations.append(res)
                    else:
                        res = self.validate_entity(field_name, item)
                        res["field"] = f"{field_name}[{idx}]"
                        validations.append(res)
            elif isinstance(value, dict):
                for sub_k, sub_v in value.items():
                    res = self.validate_entity(sub_k, sub_v)
                    res["field"] = f"{field_name}.{sub_k}"
                    validations.append(res)
            else:
                res = self.validate_entity(field_name, value)
                res["field"] = field_name
                validations.append(res)

        total_entities = len(validations)
        if total_entities > 0:
            for v in validations:
                total_score += v["semantic_score"]
                if v["status"] == "valid":
                    valid_count += 1
                elif v["status"] in ["invalid", "suspicious"] or "move" in v["action"]:
                    anomaly_count += 1

            overall_accuracy = round((total_score / float(total_entities)), 1)
            false_positives = round((sum(1 for v in validations if v["status"] == "suspicious") / float(total_entities)) * 100.0, 1)
            misclassification = round((anomaly_count / float(total_entities)) * 100.0, 1)
        else:
            overall_accuracy = 100.0
            false_positives = 0.0
            misclassification = 0.0

        return {
            "validations": validations,
            "metrics": {
                "total_entities": total_entities,
                "valid_count": valid_count,
                "anomaly_count": anomaly_count,
                "semantic_accuracy": overall_accuracy,
                "false_positives_rate": false_positives,
                "misclassification_rate": misclassification
            }
        }

    def _score_to_status(self, score: float) -> str:
        if score >= 90:
            return "valid"
        elif score >= 75:
            return "possible"
        elif score >= 50:
            return "suspicious"
        else:
            return "invalid"

    def _get_expected_category(self, field_name: str) -> str:
        cat, _ = FIELD_TO_EXPECTED_CATEGORY.get(
            field_name.lower(), (self._infer_category_from_fieldname(field_name), "general")
        )
        return self._format_category_name(cat)

    def _infer_category_from_fieldname(self, field_name: str) -> str:
        fn = field_name.lower()
        if "name" in fn:
            return "PERSON"
        if "skill" in fn:
            return "SKILL"
        if "company" in fn or "employer" in fn:
            return "COMPANY"
        if "univ" in fn or "school" in fn or "college" in fn or "edu" in fn:
            return "UNIVERSITY"
        if "cert" in fn:
            return "CERTIFICATE"
        if "project" in fn:
            return "PROJECT"
        if "role" in fn or "title" in fn or "desig" in fn:
            return "DESIGNATION"
        if "lang" in fn:
            return "LANGUAGE"
        if "date" in fn:
            return "DATE"
        return "SKILL"

    def _are_categories_compatible(self, cat1: str, cat2: str) -> bool:
        c1, c2 = cat1.upper(), cat2.upper()
        if c1 == c2:
            return True
        # Equivalent pairings
        if c1 in ["SKILL", "TECHNOLOGY"] and c2 in ["SKILL", "TECHNOLOGY"]:
            return True
        if c1 in ["DESIGNATION", "ROLE"] and c2 in ["DESIGNATION", "ROLE"]:
            return True
        if c1 in ["COMPANY", "ORGANIZATION"] and c2 in ["COMPANY", "ORGANIZATION"]:
            return True
        return False

    def _format_category_name(self, category: str) -> str:
        cat_map = {
            "PERSON": "Person",
            "COMPANY": "Company",
            "UNIVERSITY": "University",
            "SKILL": "Skill",
            "CERTIFICATE": "Certificate",
            "TECHNOLOGY": "Technology",
            "PROJECT": "Project",
            "DESIGNATION": "Designation",
            "LANGUAGE": "Language",
            "COUNTRY": "Country",
            "CITY": "City",
            "DATE": "Date",
            "ROLE": "Role",
            "ORGANIZATION": "Organization",
            "PUBLICATION": "Publication",
            "AWARD": "Award"
        }
        return cat_map.get(category.upper(), category.capitalize())
