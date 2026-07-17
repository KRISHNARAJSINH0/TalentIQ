import logging
from .models import ProfessionProfile
from .profile_loader import ProfileLoader
from .role_mapper import RoleMapper

logger = logging.getLogger(__name__)

class ProfileRegistry:
    """
    Acts as a registry/cache for fast profile lookups.
    Ensures database is seeded and handles fallbacks.
    """
    _cached_profiles = {}

    @classmethod
    def get_profile(cls, role_name: str) -> ProfessionProfile:
        """
        Retrieves a ProfessionProfile for the given role title.
        Ensures the profiles are seeded if the table is empty.
        """
        # Ensure database contains profiles
        if ProfessionProfile.objects.count() == 0:
            logger.warning("No Profession Profiles found. Seeding default profiles...")
            ProfileLoader.seed_profiles()

        # Map/normalize role
        normalized_role = RoleMapper.map_role(role_name)
        logger.info(f"Looking up profile for normalized role: {normalized_role} (from raw: {role_name})")

        try:
            profile = ProfessionProfile.objects.get(role=normalized_role, enabled=True)
            return profile
        except ProfessionProfile.DoesNotExist:
            logger.warning(f"Profile for '{normalized_role}' not found or disabled. Falling back to Software Engineer.")
            # Fallback to Software Engineer as default
            try:
                fallback_profile = ProfessionProfile.objects.get(role="Software Engineer")
                return fallback_profile
            except ProfessionProfile.DoesNotExist:
                # Absolute fallback creation if database is completely wiped
                logger.error("Software Engineer fallback profile missing. Seeding and retrying.")
                ProfileLoader.seed_profiles(overwrite=True)
                return ProfessionProfile.objects.get(role="Software Engineer")

    @classmethod
    def clear_cache(cls):
        cls._cached_profiles.clear()
