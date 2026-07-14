import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class RecoveryRules:
    """
    Defines recovery confidence mapping, decision thresholds, and status flags.

    Confidence Tiers:
    - 95+: Auto Fix (Status: recovered) -> User edits < 5%
    - 85-95: Fix & Review Later (Status: reviewed)
    - 70-85: Suggest Fix (Status: suggested)
    - Below 70: Ask User (Status: manual)
    """

    AUTO_FIX_THRESHOLD = 95.0
    REVIEW_LATER_THRESHOLD = 85.0
    SUGGEST_THRESHOLD = 70.0

    @classmethod
    def determine_status(cls, confidence: float) -> Tuple[str, str]:
        """
        Returns (status, action_tier) based on confidence score.
        Status: accepted, reviewed, recovered, suggested, manual, rejected
        """
        if confidence >= cls.AUTO_FIX_THRESHOLD:
            return ("recovered", "auto_fix")
        elif confidence >= cls.REVIEW_LATER_THRESHOLD:
            return ("reviewed", "fix_review_later")
        elif confidence >= cls.SUGGEST_THRESHOLD:
            return ("suggested", "suggest")
        else:
            return ("manual", "ask_user")

    @classmethod
    def get_ui_color_code(cls, status: str) -> str:
        """
        Maps status to UI highlight color standards:
        - recovered / auto_fix -> Green
        - reviewed -> Blue
        - suggested / manual -> Orange
        - rejected -> Red
        """
        mapping = {
            "recovered": "green",
            "accepted": "green",
            "reviewed": "blue",
            "suggested": "orange",
            "manual": "orange",
            "rejected": "red"
        }
        return mapping.get(status.lower(), "blue")
