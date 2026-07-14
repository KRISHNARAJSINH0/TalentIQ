import re
import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

COMPANY_SUFFIXES = [
    r"\binc\b\.?", r"\bllc\b\.?", r"\bcorp\b\.?", r"\bcorporation\b",
    r"\bltd\b\.?", r"\blimited\b", r"\bpvt\b\.?", r"\bprivate\b", r"\bco\b\.?", r"\bcompany\b"
]


class DuplicateResolver:
    """
    Service to resolve duplicates and canonicalize variations:
    - Case folding (e.g. Python, PYTHON, python -> Python)
    - Company legal suffix normalization (e.g. Google Inc., Google, Google LLC -> Google)
    - Deduplicating list sections (skills, projects, certifications, languages)
    """

    def canonicalize_company_name(self, name: str) -> str:
        """Strip legal suffixes and trim company names."""
        if not name:
            return ""
        clean = name.strip()
        for suffix in COMPANY_SUFFIXES:
            clean = re.sub(suffix, "", clean, flags=re.IGNORECASE).strip()
        clean = re.sub(r"[\,\.]", "", clean).strip()
        return clean if clean else name.strip()

    def resolve_duplicates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans payload, removes case duplicates, canonicalizes companies,
        and returns updated recovered payload + list of recovery audit records.
        """
        recovered = dict(payload)
        recoveries: List[Dict[str, Any]] = []

        # 1. Deduplicate Skills (Case Folding)
        skills = recovered.get("skills", [])
        if isinstance(skills, list) and len(skills) > 0:
            unique_skills: List[str] = []
            seen_skills: Dict[str, str] = {}  # lower -> original

            for sk in skills:
                if isinstance(sk, str) and sk.strip():
                    norm = sk.strip().lower()
                    if norm not in seen_skills:
                        seen_skills[norm] = sk.strip()
                        unique_skills.append(sk.strip())
                    else:
                        recoveries.append({
                            "type": "deduplicate",
                            "value": sk.strip(),
                            "from": "skills",
                            "to": "skills",
                            "confidence": 98,
                            "status": "recovered",
                            "reason": f"Deduplicated skill variant '{sk}' -> preserved canonical '{seen_skills[norm]}'"
                        })
            recovered["skills"] = unique_skills

        # 2. Deduplicate Experience Companies & Canonicalize Legal Suffixes
        experience = recovered.get("experience", [])
        if isinstance(experience, list) and len(experience) > 0:
            seen_companies: Dict[str, str] = {}  # canonical lower -> primary company name
            new_experience: List[Dict[str, Any]] = []

            for exp in experience:
                if isinstance(exp, dict):
                    raw_comp = str(exp.get("company") or exp.get("employer") or "").strip()
                    if raw_comp:
                        canonical = self.canonicalize_company_name(raw_comp)
                        canon_lower = canonical.lower()

                        if canon_lower not in seen_companies:
                            seen_companies[canon_lower] = canonical
                            exp["company"] = canonical
                            new_experience.append(exp)
                            if canonical != raw_comp:
                                recoveries.append({
                                    "type": "normalize",
                                    "value": raw_comp,
                                    "from": "experience.company",
                                    "to": "experience.company",
                                    "confidence": 95,
                                    "status": "recovered",
                                    "reason": f"Normalized company name '{raw_comp}' -> '{canonical}'"
                                })
                        else:
                            exp["company"] = seen_companies[canon_lower]
                            new_experience.append(exp)
                            recoveries.append({
                                "type": "deduplicate",
                                "value": raw_comp,
                                "from": "experience.company",
                                "to": "experience.company",
                                "confidence": 95,
                                "status": "recovered",
                                "reason": f"Merged duplicate employer variant '{raw_comp}' -> '{seen_companies[canon_lower]}'"
                            })
                    else:
                        new_experience.append(exp)
                else:
                    new_experience.append(exp)

            recovered["experience"] = new_experience

        # 3. Deduplicate Certifications
        certs = recovered.get("certifications", [])
        if isinstance(certs, list) and len(certs) > 0:
            unique_certs: List[str] = []
            seen_certs = set()

            for c in certs:
                val_str = c if isinstance(c, str) else str(c.get("name") or c.get("title") or "")
                if val_str:
                    norm = val_str.strip().lower()
                    if norm not in seen_certs:
                        seen_certs.add(norm)
                        unique_certs.append(c)
                    else:
                        recoveries.append({
                            "type": "deduplicate",
                            "value": val_str,
                            "from": "certifications",
                            "to": "certifications",
                            "confidence": 97,
                            "status": "recovered",
                            "reason": f"Deduplicated certification entry '{val_str}'"
                        })
            recovered["certifications"] = unique_certs

        return {
            "payload": recovered,
            "recoveries": recoveries
        }
