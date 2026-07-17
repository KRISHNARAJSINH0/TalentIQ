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
        then normalizes it using RoleMapper to one of the 47 supported roles.
        """
        raw_role = RolePredictor.predict_role(profile_data)
        logger.info(f"RolePredictor identified raw role: {raw_role}")

        # Delegate normalization to RoleMapper
        from .role_mapper import RoleMapper
        return RoleMapper.map_role(raw_role)
