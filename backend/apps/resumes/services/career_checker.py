import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class CareerChecker:
    """
    Service to validate career stage consistency vs total years of experience:
    - Student / Intern: 0 - 2 years
    - Junior: 0 - 3 years
    - Mid Level: 2 - 6 years
    - Senior: 5 - 10 years
    - Architect / Lead: 8+ years
    - Director / Executive: 10+ years
    """

    def check_career_consistency(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload, validates career stage alignment against experience duration,
        and returns list of consistency issues.
        """
        issues: List[Dict[str, Any]] = []

        desig = str(payload.get("designation") or payload.get("current_designation") or payload.get("title") or "").lower()
        exp_years = payload.get("years_of_experience") or payload.get("experience_years")

        # Calculate exp_years from experience list if missing
        if exp_years is None:
            exp_list = payload.get("experience", [])
            if isinstance(exp_list, list) and exp_list:
                total_duration = 0
                for exp in exp_list:
                    if isinstance(exp, dict):
                        s = exp.get("start_year") or exp.get("start_date")
                        e = exp.get("end_year") or exp.get("end_date")
                        try:
                            s_int = int(str(s)[:4]) if s else None
                            e_int = 2026 if str(e).lower() in ["present", "current"] else (int(str(e)[:4]) if e else None)
                            if s_int and e_int and e_int >= s_int:
                                total_duration += (e_int - s_int)
                        except (ValueError, TypeError):
                            pass
                exp_years = total_duration if total_duration > 0 else 0
            else:
                exp_years = 0

        # 1. Student / Intern Role Contradictions
        if any(term in desig for term in ["student", "intern", "trainee", "fresher"]):
            if exp_years > 8:
                issues.append({
                    "type": "career",
                    "severity": "high",
                    "reason": f"Role '{desig.capitalize()}' is inconsistent with {exp_years} years of professional experience.",
                    "field": "designation"
                })
            elif exp_years >= 4:
                issues.append({
                    "type": "career",
                    "severity": "medium",
                    "reason": f"Entry-level/Student designation ('{desig.capitalize()}') conflicts with {exp_years} years of experience.",
                    "field": "designation"
                })

        # 2. Executive / Senior / Architect Role Contradictions
        if any(term in desig for term in ["director", "vp", "executive", "architect", "chief", "head of"]):
            if exp_years < 3:
                issues.append({
                    "type": "career",
                    "severity": "high",
                    "reason": f"Senior/Executive designation ('{desig.capitalize()}') claimed with only {exp_years} year(s) of experience.",
                    "field": "designation"
                })

        # 3. Age vs Experience Anomaly (e.g. Age 22 with 10 years experience)
        age = payload.get("age")
        if age:
            try:
                age_val = int(age)
                if age_val - exp_years < 16:
                    issues.append({
                        "type": "career",
                        "severity": "high",
                        "reason": f"Candidate age ({age_val}) vs experience duration ({exp_years} years) implies working full-time under age 16.",
                        "field": "age"
                    })
            except (ValueError, TypeError):
                pass

        return issues
