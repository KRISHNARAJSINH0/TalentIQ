import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConversationEngine:
    """
    Parses conversational user prompts to classify intents and extract target parameters.
    """

    def parse_user_intent(self, message: str) -> Dict[str, Any]:
        msg_clean = message.strip()
        msg_lower = msg_clean.lower()

        # Undo / Redo
        if re.search(r"\bundo\b", msg_lower):
            return {"intent": "undo", "target": None}
        if re.search(r"\bredo\b", msg_lower):
            return {"intent": "redo", "target": None}

        # Add Skill
        add_skill_match = re.search(r"\b(?:add|include)\s+(?:skill\s+)?([a-zA-Z0-9\+\#\.\s]+)", msg_clean, re.IGNORECASE)
        if add_skill_match and not re.search(r"\b(?:education|experience|project|summary)\b", msg_lower):
            skill_name = add_skill_match.group(1).strip()
            return {"intent": "add_skill", "target": skill_name}

        # Remove Skill
        remove_skill_match = re.search(r"\b(?:remove|delete)\s+(?:skill\s+)?([a-zA-Z0-9\+\#\.\s]+)", msg_clean, re.IGNORECASE)
        if remove_skill_match and not re.search(r"\b(?:education|experience|project)\b", msg_lower):
            skill_name = remove_skill_match.group(1).strip()
            return {"intent": "remove_skill", "target": skill_name}

        # Education Fix / Question
        if "education" in msg_lower and ("wrong" in msg_lower or "fix" in msg_lower or "mistake" in msg_lower):
            return {"intent": "fix_education", "target": "education"}

        # Explain parser decisions / history / confidence
        if any(w in msg_lower for w in ["why is", "why", "parser mistakes", "low confidence", "what did ai modify", "show changes"]):
            return {"intent": "explain_parser", "target": msg_clean}

        # Improve ATS
        if "ats" in msg_lower or "score" in msg_lower:
            return {"intent": "improve_ats", "target": "ats"}

        # Generate / Improve Summary
        if "summary" in msg_lower:
            return {"intent": "generate_summary", "target": "summary"}

        return {"intent": "chat", "target": msg_clean}
