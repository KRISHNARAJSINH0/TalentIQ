import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)


class VersionTracker:
    """
    Manages resume versions (V1, V2 ... VN) and computes structured JSON diffs.
    """

    def compute_json_diff(
        self,
        old_json: Dict[str, Any],
        new_json: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates field-by-field differences between old_json and new_json.
        """
        old_json = old_json or {}
        new_json = new_json or {}

        added: Dict[str, Any] = {}
        removed: Dict[str, Any] = {}
        modified: Dict[str, Tuple[Any, Any]] = {}

        all_keys = set(old_json.keys()).union(set(new_json.keys()))

        for k in all_keys:
            if k not in old_json:
                added[k] = new_json[k]
            elif k not in new_json:
                removed[k] = old_json[k]
            elif old_json[k] != new_json[k]:
                modified[k] = {
                    "previous": old_json[k],
                    "current": new_json[k]
                }

        return {
            "has_changes": bool(added or removed or modified),
            "added_fields": added,
            "removed_fields": removed,
            "modified_fields": modified
        }
