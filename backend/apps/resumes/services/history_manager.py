import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HistoryManager:
    """
    Manages immutable field-level modification histories and version change logs.
    """

    def record_change(
        self,
        field_name: str,
        previous_value: Any,
        current_value: Any,
        source: str,
        reason: str = "",
        confidence: float = 100.0,
        user_id: Optional[int] = None,
        version: int = 1
    ) -> Dict[str, Any]:
        """
        Creates a structured change log entry.
        """
        return {
            "field": field_name,
            "previous": str(previous_value) if previous_value is not None else "",
            "current": str(current_value) if current_value is not None else "",
            "source": source,
            "reason": reason or f"Updated via {source}",
            "confidence": float(confidence),
            "user_id": user_id,
            "version": version,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    def format_history_list(self, history_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats raw history records for API exposure.
        """
        formatted = []
        for rec in history_records:
            if isinstance(rec, dict):
                formatted.append({
                    "field": rec.get("field"),
                    "previous_value": rec.get("previous") or rec.get("previous_value"),
                    "current_value": rec.get("current") or rec.get("current_value"),
                    "source": rec.get("source"),
                    "reason": rec.get("reason"),
                    "confidence": rec.get("confidence", 100.0),
                    "version": rec.get("version", 1),
                    "timestamp": rec.get("timestamp")
                })
        return formatted
