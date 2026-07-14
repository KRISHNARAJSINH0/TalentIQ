"""
Skill Matcher — Compares user's profile skills against JD-required skills.

Performs exact matching, synonym resolution, and categorization into
matching / missing / bonus skill buckets.
"""

import logging
from .jd_parser import SKILL_SYNONYMS

logger = logging.getLogger(__name__)


class SkillMatcher:
    """
    Compare candidate skills against JD-extracted skills.
    """

    def match(self, candidate_skills: list, jd_skills: list) -> dict:
        """
        Args:
            candidate_skills: list of skill name strings from the user's profile
            jd_skills:        list of skill name strings extracted from JD

        Returns dict with matching, missing, bonus lists and skills_match %.
        """
        # Normalize everything to lowercase
        norm_candidate = set()
        for s in candidate_skills:
            low = s.lower().strip()
            norm_candidate.add(SKILL_SYNONYMS.get(low, low))

        norm_jd = set()
        for s in jd_skills:
            low = s.lower().strip()
            norm_jd.add(SKILL_SYNONYMS.get(low, low))

        matching = sorted(norm_candidate & norm_jd)
        missing = sorted(norm_jd - norm_candidate)
        bonus = sorted(norm_candidate - norm_jd)

        # Calculate percentage
        if len(norm_jd) > 0:
            skills_match = round((len(matching) / len(norm_jd)) * 100)
        else:
            skills_match = 100  # No requirements = full match

        skills_match = min(skills_match, 100)

        logger.info(
            "SkillMatcher: %d matching, %d missing, %d bonus -> %d%%",
            len(matching), len(missing), len(bonus), skills_match,
        )

        return {
            "matching": matching,
            "missing": missing,
            "bonus": bonus,
            "skills_match": skills_match,
        }
