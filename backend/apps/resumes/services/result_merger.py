import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ResultMerger:
    """
    Merges extractions from Regex, spaCy, Gemini, Recovery Engine, and Consistency Checker
    using confidence-weighted conflict resolution.
    """

    def merge_stage_results(
        self,
        regex_data: Optional[Dict[str, Any]] = None,
        spacy_data: Optional[Dict[str, Any]] = None,
        gemini_data: Optional[Dict[str, Any]] = None,
        recovered_data: Optional[Dict[str, Any]] = None,
        user_edits: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Combines multi-engine data payloads into a single highest-confidence merged payload.
        """
        regex_data = regex_data or {}
        spacy_data = spacy_data or {}
        gemini_data = gemini_data or {}
        recovered_data = recovered_data or {}
        user_edits = user_edits or {}

        merged: Dict[str, Any] = {}
        all_keys = set().union(
            regex_data.keys(),
            spacy_data.keys(),
            gemini_data.keys(),
            recovered_data.keys(),
            user_edits.keys()
        )

        for key in all_keys:
            # 1. User edits take highest priority
            if key in user_edits and user_edits[key] is not None:
                merged[key] = user_edits[key]
                continue

            # 2. Recovered values take second priority if valid
            if key in recovered_data and recovered_data[key]:
                merged[key] = recovered_data[key]
                continue

            # 3. Evaluate extraction engine candidates
            candidates = []
            if key in regex_data and regex_data[key]:
                candidates.append((regex_data[key], 100.0, "regex"))
            if key in spacy_data and spacy_data[key]:
                candidates.append((spacy_data[key], 95.0, "spacy"))
            if key in gemini_data and gemini_data[key]:
                candidates.append((gemini_data[key], 88.0, "gemini"))

            if candidates:
                # Sort by confidence score descending
                candidates.sort(key=lambda x: x[1], reverse=True)
                merged[key] = candidates[0][0]

        return merged
