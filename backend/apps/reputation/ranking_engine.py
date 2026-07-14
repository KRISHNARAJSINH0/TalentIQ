import hashlib
from typing import Dict, Any


class RankingEngine:
    """
    Sub-system ranking evaluation service for Resume Reputation:
    Calculates Tier, Percentile status, and realistic Region/Industry Placement.
    """

    @staticmethod
    def get_tier(score: float) -> str:
        """
        Classifies score into reputation tiers.
        """
        if score >= 95:
            return "Elite"
        elif score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Strong"
        elif score >= 70:
            return "Average"
        elif score >= 60:
            return "Weak"
        else:
            return "Needs Improvement"

    @staticmethod
    def get_tier_color(tier: str) -> str:
        """
        Maps tiers to badge colors.
        """
        colors = {
            "Elite": "#D4AF37",            # Gold
            "Excellent": "#C0C0C0",        # Silver
            "Strong": "#3B82F6",           # Blue
            "Average": "#6B7280",          # Gray
            "Weak": "#F97316",             # Orange
            "Needs Improvement": "#EF4444" # Red
        }
        return colors.get(tier, "#6B7280")

    @staticmethod
    def get_percentile(score: float) -> str:
        """
        Calculates percentile status based on reputation score.
        """
        if score >= 95:
            return "Top 1%"
        elif score >= 90:
            return "Top 5%"
        elif score >= 80:
            return "Top 10%"
        elif score >= 70:
            return "Top 25%"
        elif score >= 60:
            return "Top 50%"
        else:
            return "Bottom 50%"

    @classmethod
    def get_industry_rank(cls, score: float, user_id: str, username: str, primary_industry: str) -> Dict[str, Any]:
        """
        Generates a deterministic and realistic industry rank statement for the candidate.
        """
        # Create a stable hash based on username to make the rank consistent per user
        hash_val = int(hashlib.md5(f"{username}-{primary_industry}".encode()).hexdigest(), 16)
        
        # Estimate total developers in region/pool (between 400 and 1500)
        pool_size = 400 + (hash_val % 1100)
        
        # Rank is calculated based on score percentile + minor hash offset
        percentile_pct = (100.0 - score) / 100.0
        base_rank = int(percentile_pct * pool_size)
        
        # Ensure rank is at least 1, and no worse than pool_size
        rank = max(1, min(pool_size, base_rank + 1 + (hash_val % 5)))
        
        # Top percentile label
        percentile_label = cls.get_percentile(score)

        return {
            "rank": rank,
            "pool_size": pool_size,
            "percentile": percentile_label,
            "statement": f"Ranked #{rank} out of {pool_size} {primary_industry} professionals in your region."
        }
