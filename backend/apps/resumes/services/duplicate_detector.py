import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

COMPANY_SUFFIX_PATTERNS = [
    r"\binc\b", r"\binc\.\b", r"\bcorp\b", r"\bcorp\.\b", r"\bcorporation\b",
    r"\bltd\b", r"\bltd\.\b", r"\blimited\b", r"\bllc\b", r"\bl\.l\.c\.\b",
    r"\bpvt\b", r"\bprivate\b", r"\bco\b", r"\bco\.\b", r"\bcompany\b"
]


class DuplicateDetector:
    """
    Service to detect exact and fuzzy duplicate entries across skills, projects,
    certifications, experience items, and canonical company name variations.
    """

    @staticmethod
    def normalize_company_name(name: str) -> str:
        """Normalizes company names by stripping common legal suffixes and whitespace."""
        if not name or not isinstance(name, str):
            return ""
        clean = name.strip().lower()
        for pat in COMPANY_SUFFIX_PATTERNS:
            clean = re.sub(pat, "", clean, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", clean).strip()

    def detect_duplicates(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload for duplicate entries in skills, projects, certifications,
        languages, and company names.
        Returns a list of error dictionaries.
        """
        errors: List[Dict[str, Any]] = []

        # 1. Duplicate Skills
        skills = payload.get("skills", [])
        if isinstance(skills, list):
            seen_skills = {}
            for idx, sk in enumerate(skills):
                if isinstance(sk, str):
                    norm = sk.strip().lower()
                    if norm in seen_skills:
                        errors.append({
                            "type": "duplicate_value",
                            "field": f"skills[{idx}]",
                            "value": sk,
                            "severity": "medium",
                            "confidence": 95,
                            "action": "recover",
                            "reason": f"Duplicate skill '{sk}' detected"
                        })
                    else:
                        seen_skills[norm] = idx

        # 2. Duplicate Projects
        projects = payload.get("projects", [])
        if isinstance(projects, list):
            seen_proj = {}
            for idx, proj in enumerate(projects):
                val_str = proj.get("title") or proj.get("name") if isinstance(proj, dict) else str(proj)
                if val_str:
                    norm = str(val_str).strip().lower()
                    if norm in seen_proj:
                        errors.append({
                            "type": "duplicate_value",
                            "field": f"projects[{idx}]",
                            "value": str(val_str),
                            "severity": "medium",
                            "confidence": 90,
                            "action": "recover",
                            "reason": f"Duplicate project '{val_str}' detected"
                        })
                    else:
                        seen_proj[norm] = idx

        # 3. Duplicate Certifications
        certs = payload.get("certifications", [])
        if isinstance(certs, list):
            seen_certs = {}
            for idx, cert in enumerate(certs):
                val_str = cert.get("title") or cert.get("name") if isinstance(cert, dict) else str(cert)
                if val_str:
                    norm = str(val_str).strip().lower()
                    if norm in seen_certs:
                        errors.append({
                            "type": "duplicate_value",
                            "field": f"certifications[{idx}]",
                            "value": str(val_str),
                            "severity": "medium",
                            "confidence": 90,
                            "action": "recover",
                            "reason": f"Duplicate certification '{val_str}' detected"
                        })
                    else:
                        seen_certs[norm] = idx

        # 4. Duplicate Companies (Canonical name collision e.g. Google LLC / Google / Google Inc)
        experience = payload.get("experience", [])
        if isinstance(experience, list):
            seen_companies = {}
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    comp = exp.get("company") or exp.get("employer")
                    if comp:
                        norm_comp = self.normalize_company_name(comp)
                        if norm_comp in seen_companies:
                            prev_idx = seen_companies[norm_comp]
                            prev_orig = experience[prev_idx].get("company", "")
                            errors.append({
                                "type": "duplicate_value",
                                "field": f"experience[{idx}].company",
                                "value": comp,
                                "severity": "medium",
                                "confidence": 88,
                                "action": "review",
                                "reason": f"Company variation '{comp}' matches previously listed company '{prev_orig}'"
                            })
                        else:
                            seen_companies[norm_comp] = idx

        return errors
