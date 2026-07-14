from typing import List, Dict, Any


class BadgeEngine:
    """
    Evaluates scoring dimensions and profiles to award career badges and accolades.
    """

    BADGE_RULES = {
        "ATS Master": {
            "description": "Demonstrates exceptional keyword density, strong action verbs, and optimal formatting.",
            "icon": "HiOutlineCpuChip",
            "condition": lambda s: s.get("ats_score", 0) >= 90
        },
        "Portfolio Pro": {
            "description": "Showcases an outstanding, fully configured, and public web portfolio presence.",
            "icon": "HiOutlineGlobeAlt",
            "condition": lambda s: s.get("portfolio_score", 0) >= 85
        },
        "Top Performer": {
            "description": "Indicates deep domain expertise, leadership milestones, and technical project depth.",
            "icon": "HiOutlineCheckBadge",
            "condition": lambda s: s.get("experience_score", 0) >= 85 or s.get("projects_score", 0) >= 85
        },
        "Fast Learner": {
            "description": "Highlights high learning activity, roadmap completions, and certifications.",
            "icon": "HiOutlineAcademicCap",
            "condition": lambda s: s.get("learning_score", 0) >= 80
        },
        "Career Ready": {
            "description": "Equipped with complete technical, structural, and professional career attributes.",
            "icon": "HiOutlineShieldCheck",
            "condition": lambda s: s.get("career_score", 0) >= 80 and s.get("reputation_score", 0) >= 80
        },
        "High Demand Talent": {
            "description": "Possesses specialized capabilities in high-growth, high-salary industry domains.",
            "icon": "HiOutlineArrowTrendingUp",
            "condition": lambda s: s.get("demand_score", 0) >= 85
        },
        "Elite Candidate": {
            "description": "Stands in the top percentile of talent globally for resume and industry stature.",
            "icon": "HiOutlineSparkles",
            "condition": lambda s: s.get("reputation_score", 0) >= 90
        }
    }

    @classmethod
    def evaluate_badges(cls, scores: Dict[str, float]) -> List[Dict[str, str]]:
        """
        Evaluate scores against badge rules and return list of earned badge definitions.
        """
        earned = []
        for name, info in cls.BADGE_RULES.items():
            if info["condition"](scores):
                earned.append({
                    "name": name,
                    "description": info["description"],
                    "icon": info["icon"]
                })
        return earned
