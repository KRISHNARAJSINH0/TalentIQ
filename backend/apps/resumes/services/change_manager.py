import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ChangeManager:
    """
    Manages action execution history and stack-based Undo/Redo operations.
    """

    def undo_action(self, action_record: Any) -> Dict[str, Any]:
        """
        Reverts action by returning previous_state.
        """
        if not action_record:
            return {}

        return action_record.previous_state or {}

    def redo_action(self, action_record: Any) -> Dict[str, Any]:
        """
        Re-applies action by returning new_state.
        """
        if not action_record:
            return {}

        return action_record.new_state or {}
