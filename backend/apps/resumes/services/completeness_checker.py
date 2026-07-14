import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class CompletenessChecker:
    """
    Service to score profile completeness across 10 core sections:
    Personal Info, Education, Experience, Projects, Skills, Certificates,
    Languages, Portfolio, GitHub, LinkedIn.
    """

    def check_completeness(self, payload: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Returns (completeness_score, list_of_completeness_issues).
        """
        issues: List[Dict[str, Any]] = []

        section_weights = {
            "name": 15.0,
            "email": 15.0,
            "phone": 10.0,
            "education": 15.0,
            "experience": 15.0,
            "skills": 15.0,
            "projects": 5.0,
            "certifications": 4.0,
            "languages": 3.0,
            "social_links": 3.0  # LinkedIn / GitHub / Portfolio
        }

        earned_score = 0.0

        if payload.get("name") or payload.get("full_name"):
            earned_score += section_weights["name"]

        if payload.get("email"):
            earned_score += section_weights["email"]

        if payload.get("phone"):
            earned_score += section_weights["phone"]

        if payload.get("education") and len(payload["education"]) > 0:
            earned_score += section_weights["education"]
        else:
            issues.append({
                "type": "completeness",
                "severity": "medium",
                "reason": "Missing Education section.",
                "field": "education"
            })

        if payload.get("experience") and len(payload["experience"]) > 0:
            earned_score += section_weights["experience"]
        else:
            issues.append({
                "type": "completeness",
                "severity": "medium",
                "reason": "Missing Experience section.",
                "field": "experience"
            })

        if payload.get("skills") and len(payload["skills"]) > 0:
            earned_score += section_weights["skills"]
        else:
            issues.append({
                "type": "completeness",
                "severity": "high",
                "reason": "Missing Skills section.",
                "field": "skills"
            })

        if payload.get("projects") and len(payload["projects"]) > 0:
            earned_score += section_weights["projects"]

        if payload.get("certifications") and len(payload["certifications"]) > 0:
            earned_score += section_weights["certifications"]

        if payload.get("languages") and len(payload["languages"]) > 0:
            earned_score += section_weights["languages"]

        if payload.get("linkedin") or payload.get("github") or payload.get("portfolio"):
            earned_score += section_weights["social_links"]

        return min(100.0, round(earned_score, 1)), issues
