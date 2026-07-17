import logging

logger = logging.getLogger(__name__)

# List of 20 categories in our Rule Engine
RULE_CATEGORIES = [
    "Contact",
    "Summary",
    "Skills",
    "Experience",
    "Projects",
    "Education",
    "Certifications",
    "Achievements",
    "Formatting",
    "Grammar",
    "Portfolio",
    "GitHub",
    "LinkedIn",
    "ATS Parsing",
    "Consistency",
    "Keyword Quality",
    "Career Progression",
    "Leadership",
    "Soft Skills",
    "Job Match"
]

class WeightManager:
    """
    Translates profile-defined weights into weights for the 20 Rule Engine categories,
    normalising them so that they sum to a balanced total.
    """

    @classmethod
    def get_category_weights(cls, profile_weights: dict) -> dict:
        """
        Translates a dictionary of profile weights, e.g.:
        {"skills": 30, "projects": 20, "experience": 20, "education": 10, "github": 10, "portfolio": 5, "certifications": 5}
        into weights for all 20 categories.
        """
        # Convert keys in profile_weights to lowercase for easy lookup
        weights_clean = {k.lower(): float(v) for k, v in profile_weights.items()}

        category_weights = {}

        # 1. Map major categories
        # Contact
        category_weights["Contact"] = weights_clean.get("contact", 5.0)
        # Summary
        category_weights["Summary"] = weights_clean.get("summary", 5.0)

        # Skills & Keyword Quality
        # If skills has a weight, split/share it with Keyword Quality
        skills_weight = weights_clean.get("skills", 0.0)
        # Handle specific Data Analyst skill weights
        for k in ["sql", "python", "power bi", "excel", "statistics"]:
            skills_weight += weights_clean.get(k, 0.0)

        if skills_weight > 0:
            category_weights["Skills"] = skills_weight * 0.6
            category_weights["Keyword Quality"] = skills_weight * 0.4
        else:
            category_weights["Skills"] = 10.0
            category_weights["Keyword Quality"] = 5.0

        # Experience, Leadership & Career Progression
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

        # Projects & Research
        proj_weight = weights_clean.get("projects", 0.0) + weights_clean.get("research", 0.0)
        if proj_weight > 0:
            category_weights["Projects"] = proj_weight
        else:
            category_weights["Projects"] = 10.0

        # Education
        category_weights["Education"] = weights_clean.get("education", 10.0)

        # Certifications
        cert_weight = weights_clean.get("certifications", 0.0) + weights_clean.get("certificates", 0.0) + weights_clean.get("medical registration", 0.0)
        if cert_weight > 0:
            category_weights["Certifications"] = cert_weight
        else:
            category_weights["Certifications"] = 5.0

        # Achievements, Publications & Reviews
        ach_weight = weights_clean.get("achievements", 0.0) + weights_clean.get("publications", 0.0) + weights_clean.get("reviews", 0.0)
        if ach_weight > 0:
            category_weights["Achievements"] = ach_weight
        else:
            category_weights["Achievements"] = 5.0

        # GitHub
        category_weights["GitHub"] = weights_clean.get("github", 5.0)

        # Portfolio
        category_weights["Portfolio"] = weights_clean.get("portfolio", 5.0)

        # LinkedIn
        category_weights["LinkedIn"] = weights_clean.get("linkedin", 5.0)

        # Soft Skills / Communication
        soft_weight = weights_clean.get("communication", 0.0) + weights_clean.get("soft_skills", 0.0) + weights_clean.get("soft skills", 0.0)
        if soft_weight > 0:
            category_weights["Soft Skills"] = soft_weight
        else:
            category_weights["Soft Skills"] = 5.0

        # Formatting, Grammar, ATS Parsing, Job Match (Technical Baseline checks)
        category_weights["Formatting"] = weights_clean.get("formatting", 5.0)
        category_weights["Grammar"] = weights_clean.get("grammar", 5.0)
        category_weights["ATS Parsing"] = weights_clean.get("ats parsing", 5.0)
        category_weights["Consistency"] = weights_clean.get("consistency", 5.0)
        category_weights["Job Match"] = weights_clean.get("job match", 10.0)

        # Ensure all 20 categories exist in the output dict
        for cat in RULE_CATEGORIES:
            if cat not in category_weights:
                category_weights[cat] = 5.0

        # Normalise weights so they sum to exactly 1.0 (to make overall calculations clean)
        total = sum(category_weights.values())
        if total > 0:
            for cat in category_weights:
                category_weights[cat] = round(category_weights[cat] / total, 4)

        return category_weights
