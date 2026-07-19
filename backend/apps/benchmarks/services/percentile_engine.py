import hashlib
from typing import Dict, Any


class PercentileEngine:
    """
    Sub-system to calculate user percentiles and map them to benchmark ranges.
    """

    @staticmethod
    def calculate_percentile(score: float, salt: str = "") -> float:
        """
        Deterministically calculates a realistic percentile percentage (1.0 to 99.0)
        based on the user's score and optional string salt (e.g. username or resume title).
        """
        # Base percentile is derived from score: high score = low rank number (Top X%)
        # A score of 100 means Top 1%, score of 0 means Top 99%
        base_val = 100.0 - score
        
        # Apply a deterministic hash-based fluctuation to make it unique per user/resume
        hash_val = int(hashlib.md5(salt.encode()).hexdigest(), 16) if salt else 0
        offset = (hash_val % 7) - 3  # -3 to +3 fluctuation
        
        percentile = base_val + offset
        
        # Keep inside bounds [1.0, 99.0]
        percentile = max(1.0, min(99.0, percentile))
        return round(percentile, 1)

    @classmethod
    def get_percentile_label(cls, percentile: float) -> str:
        """
        Translates a percentile float (e.g., 12.4 means Top 12.4%) to a category rank.
        Categories: Top 1%, Top 5%, Top 10%, Top 25%, Top 50%, Average, Below Average.
        """
        if percentile <= 1.0:
            return "Top 1%"
        elif percentile <= 5.0:
            return "Top 5%"
        elif percentile <= 10.0:
            return "Top 10%"
        elif percentile <= 25.0:
            return "Top 25%"
        elif percentile <= 50.0:
            return "Top 50%"
        elif percentile <= 70.0:
            return "Average"
        else:
            return "Below Average"

    @classmethod
    def format_rank(cls, percentile: float) -> str:
        """
        Formats percentile as 'Top X%' or category name.
        """
        if percentile < 50.0:
            return f"Top {int(percentile)}%"
        return cls.get_percentile_label(percentile)
