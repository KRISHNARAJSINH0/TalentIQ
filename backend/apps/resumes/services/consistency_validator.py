import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """
    Service to validate cross-field logical consistency, detecting:
    - Student/Intern role claiming 10-15 years of experience
    - Fresher claiming Senior/Lead/Principal role at a major company
    - Intern current role with >5-10 years of experience
    """

    def validate_consistency(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload for cross-field contradictions and logical inconsistencies.
        Returns a list of error dictionaries.
        """
        errors: List[Dict[str, Any]] = []

        # Parse years of experience
        years_exp_raw = payload.get("years_of_experience")
        exp_years = 0
        if isinstance(years_exp_raw, (int, float)):
            exp_years = int(years_exp_raw)
        elif isinstance(years_exp_raw, str):
            match = re.search(r"\d+", years_exp_raw)
            if match:
                exp_years = int(match.group(0))

        # Infer from experience entries if missing top-level field
        experience = payload.get("experience", [])
        if exp_years == 0 and isinstance(experience, list):
            exp_years = len(experience) * 2  # Heuristic estimation

        # Parse current designation/role
        desig_raw = str(
            payload.get("current_designation") or
            payload.get("job_role") or
            payload.get("designation") or
            payload.get("job_title") or
            payload.get("name") or
            ""
        ).lower()

        summary_raw = str(payload.get("summary") or "").lower()

        # 1. Student / Intern with 10-15 years experience
        is_student_or_intern = any(kw in desig_raw or kw in summary_raw for kw in ["student", "intern", "trainee", "fresher"])
        if is_student_or_intern and exp_years >= 10:
            errors.append({
                "type": "contradictory_values",
                "field": "years_of_experience",
                "value": f"{desig_raw.title() if desig_raw else 'Student'} with {exp_years} years experience",
                "severity": "critical",
                "confidence": 96,
                "action": "review",
                "reason": f"Logical contradiction: '{desig_raw.title() or 'Student'}' title is incompatible with {exp_years} years of total experience"
            })
        elif is_student_or_intern and exp_years >= 5:
            errors.append({
                "type": "contradictory_values",
                "field": "years_of_experience",
                "value": f"{desig_raw.title() if desig_raw else 'Student'} with {exp_years} years experience",
                "severity": "high",
                "confidence": 90,
                "action": "review",
                "reason": f"Suspicious combination: '{desig_raw.title() or 'Student'}' role with {exp_years} years of experience"
            })

        # 2. Fresher claiming Senior/Lead/CTO role
        is_fresher = "fresher" in desig_raw or "fresher" in summary_raw or "entry level" in summary_raw
        is_senior_title = any(kw in desig_raw for kw in ["senior", "lead", "principal", "architect", "head", "cto", "vp", "director"])
        if is_fresher and is_senior_title:
            errors.append({
                "type": "contradictory_values",
                "field": "current_designation",
                "value": desig_raw,
                "severity": "critical",
                "confidence": 95,
                "action": "review",
                "reason": f"Logical contradiction: Profile marked as Fresher/Entry-level but holds senior title '{desig_raw.title()}'"
            })

        # 3. Current Role Intern with long experience in experience list
        if isinstance(experience, list):
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    title = str(exp.get("designation") or exp.get("title") or "").lower()
                    end_d = str(exp.get("end_date") or "").lower()
                    if ("intern" in title or "trainee" in title) and end_d in ["present", "current"] and exp_years >= 8:
                        errors.append({
                            "type": "consistency_error",
                            "field": f"experience[{idx}].designation",
                            "value": title,
                            "severity": "high",
                            "confidence": 92,
                            "action": "review",
                            "reason": f"Inconsistency: Active '{title.title()}' position paired with {exp_years} overall years of professional experience"
                        })

        return errors
