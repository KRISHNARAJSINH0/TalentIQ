import copy
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ResumeEditor:
    """
    Executes programmatic modifications on Master Resume JSON structures.
    """

    def add_skill(self, master_json: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
        updated = copy.deepcopy(master_json)
        skills = updated.get("skills", [])
        if not isinstance(skills, list):
            skills = []

        if skill_name and skill_name not in skills:
            skills.append(skill_name)

        updated["skills"] = skills
        return updated

    def remove_skill(self, master_json: Dict[str, Any], skill_name: str) -> Dict[str, Any]:
        updated = copy.deepcopy(master_json)
        skills = updated.get("skills", [])
        if not isinstance(skills, list):
            skills = []

        skill_lower = skill_name.lower()
        skills = [s for s in skills if s.lower() != skill_lower]

        updated["skills"] = skills
        return updated

    def update_summary(self, master_json: Dict[str, Any], summary_text: str) -> Dict[str, Any]:
        updated = copy.deepcopy(master_json)
        if "profile" not in updated or not isinstance(updated["profile"], dict):
            updated["profile"] = {}
        updated["profile"]["summary"] = summary_text
        return updated

    def fix_education(self, master_json: Dict[str, Any], education_item: Dict[str, Any]) -> Dict[str, Any]:
        updated = copy.deepcopy(master_json)
        education = updated.get("education", [])
        if not isinstance(education, list):
            education = []

        education.append(education_item)
        updated["education"] = education
        return updated
