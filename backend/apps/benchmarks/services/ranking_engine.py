from typing import Dict, Any, List
from .percentile_engine import PercentileEngine


class RankingEngine:
    """
    Sub-system to calculate ranks, strengths, and weaknesses from percentiles.
    """

    @classmethod
    def identify_strengths_and_weaknesses(cls, metrics_percentiles: Dict[str, float]) -> Dict[str, List[str]]:
        """
        Sorts the metrics by percentile (lower percentile is better)
        to identify the top strengths and top weaknesses.
        """
        # Sort key = percentile value (ascending, lower is better)
        sorted_metrics = sorted(metrics_percentiles.items(), key=lambda item: item[1])
        
        # Filter out "Overall ATS" from the list of strength/weakness candidates
        candidates = [item for item in sorted_metrics if item[0] != "Overall ATS"]
        
        # Top 2-3 are strengths
        strengths = [item[0] for item in candidates[:3]]
        
        # Bottom 2-3 are weaknesses
        weaknesses = [item[0] for item in candidates[-3:]]
        # Reverse weaknesses so the absolute worst is listed first
        weaknesses.reverse()
        
        return {
            "strengths": strengths,
            "weaknesses": weaknesses
        }

    @classmethod
    def calculate_ranks(cls, base_ats_score: float, salt: str = "") -> Dict[str, float]:
        """
        Calculates distinct percentiles for different scopes:
        Overall, Profession, Industry, Country, Experience.
        """
        # Seed various values with slight deterministic variations
        overall_pct = PercentileEngine.calculate_percentile(base_ats_score, f"{salt}-overall")
        
        # Profession variance
        prof_pct = PercentileEngine.calculate_percentile(base_ats_score, f"{salt}-profession")
        # Ensure it stays within realistic boundaries, maybe slightly better if score is high
        
        industry_pct = PercentileEngine.calculate_percentile(base_ats_score, f"{salt}-industry")
        country_pct = PercentileEngine.calculate_percentile(base_ats_score, f"{salt}-country")
        experience_pct = PercentileEngine.calculate_percentile(base_ats_score, f"{salt}-experience")
        
        return {
            "overall": overall_pct,
            "profession": prof_pct,
            "industry": industry_pct,
            "country": country_pct,
            "experience": experience_pct
        }
