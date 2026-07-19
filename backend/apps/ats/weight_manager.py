import logging

logger = logging.getLogger(__name__)

# The 20 Categories for Phase C Category Scoring Engine
RULE_CATEGORIES = [
    "Contact Information",
    "Professional Summary",
    "Skills",
    "Experience",
    "Projects",
    "Education",
    "Certifications",
    "Achievements",
    "Formatting",
    "Grammar",
    "Keywords",
    "Readability",
    "ATS Compatibility",
    "GitHub",
    "Portfolio",
    "LinkedIn",
    "Leadership",
    "Soft Skills",
    "Career Progression",
    "Consistency"
]

class WeightManager:
    """
    Translates profile-defined weights into weights for the 20 Phase C quality categories,
    normalising them so that they sum to exactly 1.0.
    """

    @classmethod
    def get_category_weights(cls, profile_weights: dict) -> dict:
        """
        Translates a dictionary of profile weights, e.g.:
        {"skills": 30, "projects": 20, "experience": 20, "education": 10, "github": 10, "portfolio": 5, "certifications": 5}
        into weights for all 20 categories.
        """
        weights_clean = {k.lower(): float(v) for k, v in profile_weights.items()}

        category_weights = {}

        # 1. Contact Information
        category_weights["Contact Information"] = weights_clean.get("contact", 5.0)

        # 2. Professional Summary
        category_weights["Professional Summary"] = weights_clean.get("summary", 5.0)

        # 3. Skills
        skills_weight = weights_clean.get("skills", 0.0)
        # Handle specific Data Analyst skill weights
        for k in ["sql", "python", "power bi", "excel", "statistics"]:
            skills_weight += weights_clean.get(k, 0.0)

        if skills_weight > 0:
            category_weights["Skills"] = skills_weight * 0.7
            category_weights["Soft Skills"] = skills_weight * 0.3
        else:
            category_weights["Skills"] = 15.0
            category_weights["Soft Skills"] = 5.0

        # 4. Experience
        exp_weight = weights_clean.get("experience", 0.0)
        for k in ["teaching experience", "clinical experience", "client experience"]:
            exp_weight += weights_clean.get(k, 0.0)

        if exp_weight > 0:
            category_weights["Experience"] = exp_weight * 0.6
            category_weights["Leadership"] = exp_weight * 0.2
            category_weights["Career Progression"] = exp_weight * 0.2
        else:
            category_weights["Experience"] = 15.0
            category_weights["Leadership"] = 5.0
            category_weights["Career Progression"] = 5.0

        # 5. Projects
        proj_weight = weights_clean.get("projects", 0.0) + weights_clean.get("research", 0.0)
        if proj_weight > 0:
            category_weights["Projects"] = proj_weight
        else:
            category_weights["Projects"] = 10.0

        # 6. Education
        category_weights["Education"] = weights_clean.get("education", 10.0)

        # 7. Certifications
        cert_weight = weights_clean.get("certifications", 0.0) + weights_clean.get("certificates", 0.0) + weights_clean.get("medical registration", 0.0)
        if cert_weight > 0:
            category_weights["Certifications"] = cert_weight
        else:
            category_weights["Certifications"] = 5.0

        # 8. Achievements
        ach_weight = weights_clean.get("achievements", 0.0) + weights_clean.get("publications", 0.0) + weights_clean.get("reviews", 0.0)
        if ach_weight > 0:
            category_weights["Achievements"] = ach_weight
        else:
            category_weights["Achievements"] = 5.0

        # 9. Formatting
        category_weights["Formatting"] = weights_clean.get("formatting", 5.0)

        # 10. Grammar
        category_weights["Grammar"] = weights_clean.get("grammar", 5.0)

        # 11. Keywords
        category_weights["Keywords"] = weights_clean.get("keywords", 5.0)

        # 12. Readability
        category_weights["Readability"] = weights_clean.get("readability", 5.0)

        # 13. ATS Compatibility
        category_weights["ATS Compatibility"] = weights_clean.get("ats compatibility", 5.0)

        # 14. GitHub
        category_weights["GitHub"] = weights_clean.get("github", 5.0)

        # 15. Portfolio
        category_weights["Portfolio"] = weights_clean.get("portfolio", 5.0)

        # 16. LinkedIn
        category_weights["LinkedIn"] = weights_clean.get("linkedin", 5.0)

        # 17. Consistency
        category_weights["Consistency"] = weights_clean.get("consistency", 5.0)

        # Ensure all 20 categories exist in the output dict with at least default weights
        for cat in RULE_CATEGORIES:
            if cat not in category_weights:
                category_weights[cat] = 5.0

        # Normalise weights so they sum to exactly 1.0
        total = sum(category_weights.values())
        if total > 0:
            for cat in category_weights:
                category_weights[cat] = round(category_weights[cat] / total, 4)

        return category_weights
