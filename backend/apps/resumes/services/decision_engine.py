import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DecisionEngine:
    """
    Decision & Auto-Approval Engine.
    Determines pipeline decisions (accept, review, recover, reject, escalate) and
    calculates approval tier thresholds based on final confidence scores.
    """

    def evaluate_decision(
        self,
        final_confidence: float,
        issues_found: int = 0,
        issues_fixed: int = 0,
        recovered_fields_count: int = 0
    ) -> Dict[str, Any]:
        """
        Determines pipeline decision status and approval tiers.
        """
        needs_review = max(0, issues_found - issues_fixed)

        if final_confidence >= 95.0 and needs_review == 0:
            decision = "accept"
            tier = "auto_approve"
            summary = f"High confidence ({final_confidence:.1f}%). All {issues_fixed} detected issues auto-repaired. Resume auto-approved."
        elif final_confidence >= 85.0:
            decision = "review"
            tier = "approve"
            summary = f"Strong confidence ({final_confidence:.1f}%). Repaired {issues_fixed} issues with {needs_review} minor items available for review."
        elif final_confidence >= 70.0:
            decision = "recover"
            tier = "ask_confirmation"
            summary = f"Moderate confidence ({final_confidence:.1f}%). Repaired {issues_fixed} issues; {needs_review} items require confirmation."
        else:
            decision = "escalate" if needs_review > 0 else "reject"
            tier = "manual_verification"
            summary = f"Low confidence ({final_confidence:.1f}%). {needs_review} critical issues require manual verification."

        return {
            "decision": decision,
            "approval_tier": tier,
            "confidence": final_confidence,
            "issues_found": issues_found,
            "issues_fixed": issues_fixed,
            "needs_review": needs_review,
            "recovered_fields_count": recovered_fields_count,
            "summary": summary
        }
