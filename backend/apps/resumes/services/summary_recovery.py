import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SummaryRecovery:
    """
    Service to recover misplaced or missing professional summary statements:
    - Extracts summary detected inside Work Experience
    - Infers missing summary from designation, top skills, and years of experience
    """

    def recover_summary(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans payload, extracts or generates professional summary if missing/misplaced,
        and returns updated recovered payload + recoveries audit records.
        """
        recovered = dict(payload)
        recoveries: List[Dict[str, Any]] = []

        existing_summary = recovered.get("summary")

        # 1. Check if summary is buried inside experience item
        experience = recovered.get("experience", [])
        if isinstance(experience, list):
            new_exp = []
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    desc = str(exp.get("description") or exp.get("summary") or "")
                    if (not existing_summary or len(str(existing_summary).strip()) < 15) and (
                        "professional summary" in desc.lower() or "career summary" in desc.lower() or "profile overview" in desc.lower()
                    ):
                        recovered["summary"] = desc
                        existing_summary = desc
                        recoveries.append({
                            "type": "move",
                            "value": desc[:60] + "...",
                            "from": f"experience[{idx}].description",
                            "to": "summary",
                            "confidence": 94,
                            "status": "recovered",
                            "reason": "Moved misplaced professional summary statement from experience section to summary field"
                        })
                    else:
                        new_exp.append(exp)
                else:
                    new_exp.append(exp)
            recovered["experience"] = new_exp

        # 2. Infer summary if completely missing
        if not existing_summary or not str(existing_summary).strip():
            desig = recovered.get("designation") or recovered.get("current_designation") or "Professional"
            skills = recovered.get("skills", [])
            skills_str = ", ".join(skills[:4]) if isinstance(skills, list) and skills else "technical"
            exp_years = recovered.get("years_of_experience") or 3

            inferred_summary = (
                f"Results-oriented {desig} with over {exp_years} years of experience specializing in "
                f"{skills_str}. Proven track record of delivering scalable solutions and contributing to high-performing teams."
            )
            recovered["summary"] = inferred_summary
            recoveries.append({
                "type": "infer",
                "value": inferred_summary[:60] + "...",
                "from": "experience/skills",
                "to": "summary",
                "confidence": 88,
                "status": "suggested",
                "reason": "Generated synthesized professional summary from extracted designation, skills, and experience metrics"
            })

        return {
            "payload": recovered,
            "recoveries": recoveries
        }
