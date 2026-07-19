import logging

logger = logging.getLogger(__name__)

SIMULATABLE_ACTIONS = {
    "add_required_skill": {
        "name": "Add Missing Required Skill",
        "points": 3,
        "category": "Skills",
        "description": "Add a required technical skill mentioned in the job description or profession profile."
    },
    "add_recommended_skill": {
        "name": "Add Missing Recommended Skill",
        "points": 1,
        "category": "Skills",
        "description": "Add a recommended technical skill mentioned in the profession profile."
    },
    "add_github": {
        "name": "Link GitHub Profile",
        "points": 5,
        "category": "GitHub",
        "description": "Link your active public GitHub profile to showcase code quality."
    },
    "add_linkedin": {
        "name": "Link LinkedIn Profile",
        "points": 4,
        "category": "LinkedIn",
        "description": "Add a properly formatted LinkedIn profile URL to verify your identity."
    },
    "add_portfolio": {
        "name": "Link Portfolio Website",
        "points": 3,
        "category": "Portfolio",
        "description": "Add a personal website or portfolio link to showcase visual or live projects."
    },
    "add_project_links": {
        "name": "Add Project Demo Links",
        "points": 4,
        "category": "Projects",
        "description": "Add live deployment links and GitHub repositories to your individual projects."
    },
    "quantify_experience": {
        "name": "Quantify Work Achievements",
        "points": 5,
        "category": "Experience",
        "description": "Use percentages, dollar amounts, and specific counts to detail project sizes and cost savings."
    },
    "optimize_summary_length": {
        "name": "Optimize Summary Length",
        "points": 2,
        "category": "Professional Summary",
        "description": "Adjust summary word count to be between 30 and 100 words."
    },
    "add_certification": {
        "name": "Add Professional Certification",
        "points": 3,
        "category": "Certifications",
        "description": "Add AWS, GCP, Scrum, or other industry certifications."
    },
    "fix_timeline_overlap": {
        "name": "Resolve Timeline Overlap",
        "points": 3,
        "category": "Consistency",
        "description": "Adjust dates in work history so they do not overlap chronologically."
    }
}

class ImprovementSimulator:
    """
    Calculates simulated ATS score enhancements and suggests custom actions.
    """

    @classmethod
    def simulate(cls, current_score: int, actions: list) -> dict:
        """
        Calculates the estimated ATS score based on selected actions.
        """
        estimated_score = float(current_score)
        applied_actions = []

        for action_id in actions:
            if action_id in SIMULATABLE_ACTIONS:
                detail = SIMULATABLE_ACTIONS[action_id]
                estimated_score += detail["points"]
                applied_actions.append({
                    "action_id": action_id,
                    "name": detail["name"],
                    "points": detail["points"],
                    "category": detail["category"]
                })

        estimated_score = min(100.0, max(0.0, estimated_score))

        return {
            "current_score": current_score,
            "estimated_score": round(estimated_score),
            "score_boost": round(estimated_score - current_score),
            "applied_actions": applied_actions
        }

    @classmethod
    def get_suggested_actions(cls, profile, resume, missing_elements: dict) -> list:
        """
        Inspects profile and missing elements to return suggested simulation actions.
        """
        suggestions = []

        # Check GitHub
        links = profile.links if hasattr(profile, "links") and profile.links else []
        if isinstance(links, str):
            links = [links]
        
        has_github = any("github.com" in l.lower() for l in links)
        has_linkedin = any("linkedin.com" in l.lower() for l in links)
        has_portfolio = any(any(x in l.lower() for x in ["portfolio", "personal", "site"]) for l in links)

        if not has_github:
            action = SIMULATABLE_ACTIONS["add_github"].copy()
            action["action_id"] = "add_github"
            suggestions.append(action)

        if not has_linkedin:
            action = SIMULATABLE_ACTIONS["add_linkedin"].copy()
            action["action_id"] = "add_linkedin"
            suggestions.append(action)

        if not has_portfolio:
            action = SIMULATABLE_ACTIONS["add_portfolio"].copy()
            action["action_id"] = "add_portfolio"
            suggestions.append(action)

        # Check missing required skills
        missing_req = missing_elements.get("missing_required_skills", [])
        if missing_req:
            action = SIMULATABLE_ACTIONS["add_required_skill"].copy()
            action["action_id"] = "add_required_skill"
            action["name"] = f"Add Required Skill: {missing_req[0]}"
            action["points"] = 3 * min(3, len(missing_req))  # Cap boost
            action["description"] = f"Add missing required skills: {', '.join(missing_req[:3])}."
            suggestions.append(action)

        # Check missing recommended skills
        missing_rec = missing_elements.get("missing_recommended_skills", [])
        if missing_rec:
            action = SIMULATABLE_ACTIONS["add_recommended_skill"].copy()
            action["action_id"] = "add_recommended_skill"
            action["name"] = f"Add Recommended Skill: {missing_rec[0]}"
            action["points"] = min(3, len(missing_rec))
            action["description"] = f"Add missing recommended skills: {', '.join(missing_rec[:3])}."
            suggestions.append(action)

        # Check project links
        projects = list(profile.projects.all()) if hasattr(profile, "projects") else []
        has_project_links = all(getattr(p, "github_url", None) or getattr(p, "live_url", None) for p in projects) if projects else False
        if projects and not has_project_links:
            action = SIMULATABLE_ACTIONS["add_project_links"].copy()
            action["action_id"] = "add_project_links"
            suggestions.append(action)

        # Check quantified experience (metrics)
        experiences = list(profile.experiences.all()) if hasattr(profile, "experiences") else []
        has_metrics = False
        import re
        for exp in experiences:
            desc = getattr(exp, "description", "") or ""
            if re.search(r'\b\d+%\b|\b\d+\s*(?:million|k|usd|dollars|users|hours|seconds|percent)\b|\b\$\d+', desc.lower()):
                has_metrics = True
                break
        if experiences and not has_metrics:
            action = SIMULATABLE_ACTIONS["quantify_experience"].copy()
            action["action_id"] = "quantify_experience"
            suggestions.append(action)

        # Summary length
        summary = getattr(profile, "summary", "") or ""
        words = len(summary.split())
        if words < 30 or words > 100:
            action = SIMULATABLE_ACTIONS["optimize_summary_length"].copy()
            action["action_id"] = "optimize_summary_length"
            suggestions.append(action)

        # Certifications
        certifications = list(profile.certifications.all()) if hasattr(profile, "certifications") else []
        if not certifications:
            action = SIMULATABLE_ACTIONS["add_certification"].copy()
            action["action_id"] = "add_certification"
            suggestions.append(action)

        return suggestions
