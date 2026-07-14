import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

SOURCE_COLOR_MAP = {
    "regex": "#3B82F6",         # Blue
    "spacy": "#8B5CF6",         # Purple
    "gemini": "#F97316",        # Orange
    "recovery_engine": "#10B981", # Green
    "consistency_checker": "#EC4899", # Pink
    "section_detector": "#6366F1", # Indigo
    "semantic_validator": "#14B8A6", # Teal
    "user_edit": "#06B6D4",      # Cyan
    "manual": "#6B7280",         # Gray
    "rejected": "#EF4444",       # Red
    "imported": "#84CC16"        # Lime
}


class SourceTracker:
    """
    Service to map and track field-level origin, confidence score, status,
    reasoning, and UI hover color across extraction & repair engines.
    """

    @staticmethod
    def get_ui_color(source_name: str) -> str:
        s_clean = str(source_name).lower().replace(" ", "_")
        return SOURCE_COLOR_MAP.get(s_clean, "#6B7280")

    def track_field_sources(
        self,
        payload: Dict[str, Any],
        engine_origins: Optional[Dict[str, Any]] = None,
        recoveries: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Constructs a comprehensive field-level provenance map for the master payload.
        """
        provenance: Dict[str, Any] = {}
        engine_origins = engine_origins or {}
        recoveries = recoveries or []

        # Map recoveries for fast lookup
        recovered_fields = {r.get("to") or r.get("field"): r for r in recoveries if isinstance(r, dict)}

        for field_name, value in payload.items():
            if value is None:
                continue

            # Check if updated by Recovery Engine
            if field_name in recovered_fields:
                rec_info = recovered_fields[field_name]
                src = "recovery_engine"
                conf = float(rec_info.get("confidence", 95))
                reason = rec_info.get("reason", f"Recovered by AI Recovery Engine from {rec_info.get('from')}")
                status_val = rec_info.get("status", "recovered")
            else:
                # Default origin resolution based on field type conventions
                origin_info = engine_origins.get(field_name, {})
                src = origin_info.get("source") or self._infer_default_source(field_name, value)
                conf = float(origin_info.get("confidence") or self._infer_default_confidence(src))
                reason = origin_info.get("reason") or f"Extracted via {src.title()} engine"
                status_val = origin_info.get("status", "extracted")

            provenance[field_name] = {
                "value": value,
                "source": src,
                "confidence": conf,
                "status": status_val,
                "reason": reason,
                "ui_color": self.get_ui_color(src),
                "modified_by": None
            }

        return provenance

    def _infer_default_source(self, field_name: str, value: Any) -> str:
        field_lower = field_name.lower()
        if field_lower in ["email", "phone", "links", "url", "github", "linkedin"]:
            return "regex"
        elif field_lower in ["name", "location", "address", "organization"]:
            return "spacy"
        else:
            return "gemini"

    def _infer_default_confidence(self, source_name: str) -> float:
        if source_name == "regex":
            return 100.0
        elif source_name == "spacy":
            return 95.0
        elif source_name == "recovery_engine":
            return 92.0
        elif source_name == "gemini":
            return 88.0
        return 90.0
