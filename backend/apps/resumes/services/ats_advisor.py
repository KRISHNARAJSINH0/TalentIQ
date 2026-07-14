import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ATSAdvisor:
    """
    Calculates current ATS scores, predicts skill-based delta improvements,
    and identifies missing critical keywords.
    """

    HIGH_IMPACT_SKILLS = ["Docker", "AWS", "Redis", "GraphQL", "Kubernetes", "CI/CD", "TypeScript", "Python"]

    def analyze_ats(self, master_json: Dict[str, Any]) -> Dict[str, Any]:
        skills = master_json.get("skills", [])
        if not isinstance(skills, list):
            skills = []

        skills_lower = [str(s).lower() for s in skills]
        missing_skills = [s for s in self.HIGH_IMPACT_SKILLS if s.lower() not in skills_lower]

        base_score = 84.0
        skill_count_bonus = min(10.0, len(skills) * 0.5)
        current_ats = round(min(98.0, base_score + skill_count_bonus), 1)

        recommendations = []
        projected_gain = 0.0

        for skill in missing_skills[:4]:
            gain = 2.0 if skill in ["Docker", "AWS", "Kubernetes"] else 1.5
            recommendations.append({"skill": skill, "score_delta": gain})
            projected_gain += gain

        estimated_ats = round(min(98.0, current_ats + projected_gain), 1)

        return {
            "current_ats": current_ats,
            "estimated_ats": estimated_ats,
            "missing_skills": missing_skills[:5],
            "recommendations": recommendations
        }
