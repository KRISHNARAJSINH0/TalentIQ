import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MemoryEngine:
    """
    Learns and enforces user-specific preferences (e.g. React vs ReactJS, institution names).
    """

    PREFERENCE_MAPPINGS = {
        "reactjs": "React",
        "react.js": "React",
        "node.js": "Node.js",
        "lj institute": "LJ University",
        "lj institute of technology": "LJ University"
    }

    def apply_user_preferences(self, master_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes extracted entities based on stored user preference signals.
        """
        updated = master_json.copy()

        # Normalize skills
        if "skills" in updated and isinstance(updated["skills"], list):
            new_skills = []
            for s in updated["skills"]:
                s_lower = str(s).lower().strip()
                new_skills.append(self.PREFERENCE_MAPPINGS.get(s_lower, s))
            updated["skills"] = list(dict.fromkeys(new_skills))  # Unique list

        # Normalize education institution names
        if "education" in updated and isinstance(updated["education"], list):
            for ed in updated["education"]:
                if isinstance(ed, dict) and "institution" in ed:
                    inst_lower = str(ed["institution"]).lower().strip()
                    if inst_lower in self.PREFERENCE_MAPPINGS:
                        ed["institution"] = self.PREFERENCE_MAPPINGS[inst_lower]

        return updated
