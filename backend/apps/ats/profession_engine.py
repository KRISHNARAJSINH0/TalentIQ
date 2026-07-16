import logging
from apps.jobs.services.role_predictor import RolePredictor

logger = logging.getLogger(__name__)

# List of standard professions that we support for benchmarking/weighting
SUPPORTED_PROFESSIONS = [
    "Software Engineer",
    "Data Analyst",
    "AI Engineer",  # Also ML Engineer/AI Engineer
    "UI Designer",  # Also UI UX Designer
    "Teacher",
    "Doctor",
    "Lawyer",
    "Civil Engineer",
    "Mechanical Engineer",
    "Chemical Engineer",
    "Freelancer",
    "Student",
    "Marketing",
    "HR",
]

class ProfessionEngine:
    """
    Detects/normalizes candidate's profession and maps it to industry benchmarks/criteria.
    """
    @staticmethod
    def detect_profession(profile_data: dict) -> str:
        """
        Uses the existing RolePredictor to identify candidate's profession,
        then normalizes it to our supported set.
        """
        raw_role = RolePredictor.predict_role(profile_data)
        logger.info(f"RolePredictor identified raw role: {raw_role}")

        # Normalize to supported professions
        role_lower = raw_role.lower()
        if "student" in role_lower or "intern" in role_lower:
            return "Student"
        elif "freelancer" in role_lower or "independent" in role_lower or "consultant" in role_lower:
            return "Freelancer"
        elif "data analyst" in role_lower or "business analyst" in role_lower or "statistics" in role_lower:
            return "Data Analyst"
        elif "ai" in role_lower or "machine learning" in role_lower or "ml" in role_lower or "deep learning" in role_lower:
            return "AI Engineer"
        elif "software" in role_lower or "developer" in role_lower or "programmer" in role_lower:
            return "Software Engineer"
        elif "ui" in role_lower or "ux" in role_lower or "design" in role_lower:
            return "UI Designer"
        elif "teacher" in role_lower or "professor" in role_lower or "instructor" in role_lower or "tutor" in role_lower:
            return "Teacher"
        elif "doctor" in role_lower or "physician" in role_lower or "surgeon" in role_lower or "medical" in role_lower or "clinical" in role_lower:
            return "Doctor"
        elif "lawyer" in role_lower or "attorney" in role_lower or "legal" in role_lower or "counsel" in role_lower:
            return "Lawyer"
        elif "civil" in role_lower:
            return "Civil Engineer"
        elif "mechanical" in role_lower:
            return "Mechanical Engineer"
        elif "chemical" in role_lower:
            return "Chemical Engineer"
        elif "marketing" in role_lower or "brand" in role_lower or "seo" in role_lower:
            return "Marketing"
        elif "hr" in role_lower or "human resource" in role_lower or "recruitment" in role_lower or "talent" in role_lower:
            return "HR"

        # Fallback to Software Engineer as a default base model
        return "Software Engineer"
