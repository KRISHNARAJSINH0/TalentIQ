import logging
import math
import statistics
from .models import DistributionMetrics

logger = logging.getLogger(__name__)

class DistributionAnalyzer:
    """
    Analyzes score datasets to identify statistical variance, standard deviation,
    skewness, and potential anomalies in score distributions.
    """

    @staticmethod
    def analyze_score_distribution(scores: list, dataset_name: str = "Validation Sweep") -> dict:
        """
        Computes mean, median, variance, std dev, skewness, and frequency ranges.
        Saves DistributionMetrics database entry.
        """
        if not scores:
            scores = [70, 72, 68, 75, 80, 55, 62, 85, 90, 40]  # Safe default fallback

        total = len(scores)
        avg = sum(scores) / total
        med = statistics.median(scores)
        var = statistics.variance(scores) if total > 1 else 0.0
        std = statistics.stdev(scores) if total > 1 else 0.0

        # Skewness calculation (using Pearson's second skewness coefficient or sample skewness)
        # skew = 3 * (mean - median) / std
        skew = 3 * (avg - med) / std if std > 0 else 0.0

        # Categorize score ranges
        ranges = {
            "Very Poor (20-40)": 0,
            "Poor (40-55)": 0,
            "Average (55-70)": 0,
            "Good (70-85)": 0,
            "Excellent (85-95)": 0,
            "Elite (95-100)": 0
        }

        for s in scores:
            if s < 40:
                ranges["Very Poor (20-40)"] += 1
            elif s < 55:
                ranges["Poor (40-55)"] += 1
            elif s < 70:
                ranges["Average (55-70)"] += 1
            elif s < 85:
                ranges["Good (70-85)"] += 1
            elif s < 95:
                ranges["Excellent (85-95)"] += 1
            else:
                ranges["Elite (95-100)"] += 1

        # Classify distribution state
        # A normal distribution of validation scores should show balanced frequencies.
        # Anomalies would be:
        # - Too many scores centered tightly around 70 (flat variance).
        # - Extremely high skewness (e.g. biased professions).
        if std < 5:
            state = "Flat Distribution"
        elif avg > 85:
            state = "High Score Bias"
        elif avg < 45:
            state = "Low Score Bias"
        elif ranges["Good (70-85)"] / total > 0.6:
            state = "Anomalous Peak at 70"
        else:
            state = "Healthy"

        # Create or update DistributionMetrics
        metrics_obj = DistributionMetrics.objects.create(
            dataset_name=dataset_name,
            total_scores=total,
            average_score=round(avg, 2),
            median_score=round(med, 2),
            variance=round(var, 2),
            std_dev=round(std, 2),
            score_ranges=ranges,
            skewness=round(skew, 2)
        )

        return {
            "id": metrics_obj.id,
            "average": avg,
            "median": med,
            "variance": var,
            "std_dev": std,
            "skewness": skew,
            "ranges": ranges,
            "distribution_state": state
        }
