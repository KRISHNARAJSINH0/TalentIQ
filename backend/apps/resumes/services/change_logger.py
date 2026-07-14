import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ChangeLogger:
    """
    Utility logger for transactional change logging across pipeline stages.
    """

    def __init__(self):
        self._logs: List[Dict[str, Any]] = []

    def log_change(
        self,
        field: str,
        previous: Any,
        current: Any,
        source: str,
        reason: str = "",
        confidence: float = 100.0
    ):
        entry = {
            "field": field,
            "previous": previous,
            "current": current,
            "source": source,
            "reason": reason,
            "confidence": confidence
        }
        self._logs.append(entry)
        logger.info(f"Change logged [{source}]: {field} = '{previous}' -> '{current}'")

    def get_logs(self) -> List[Dict[str, Any]]:
        return list(self._logs)

    def clear(self):
        self._logs.clear()
