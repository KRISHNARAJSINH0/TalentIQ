import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SuggestionEngine:
    """
    Generates proactive contextual suggestions for resume enhancement.
    """

    def generate_suggestions(self, master_json: Dict[str, Any]) -> List[Dict[str, Any]]:
        suggestions = []

        # Check links / GitHub
        links = master_json.get("social_links", master_json.get("links", []))
        has_github = any("github" in str(link).lower() for link in links) if isinstance(links, list) else False
        if not has_github:
            suggestions.append({
                "type": "missing_github",
                "title": "Missing GitHub Profile",
                "description": "Adding a GitHub profile link boosts technical credibility and ATS ranking.",
                "action": "add_link"
            })

        # Check projects
        projects = master_json.get("projects", [])
        if not projects or len(projects) == 0:
            suggestions.append({
                "type": "missing_projects",
                "title": "Missing Projects",
                "description": "Adding 2+ technical projects improves ATS relevance by up to 15%.",
                "action": "add_project"
            })

        # Check certifications
        certifications = master_json.get("certifications", [])
        if not certifications or len(certifications) == 0:
            suggestions.append({
                "type": "suggest_certifications",
                "title": "Suggested Certifications",
                "description": "Recommended: AWS Certified Cloud Practitioner or Docker Certified Associate.",
                "action": "add_certification"
            })

        return suggestions
