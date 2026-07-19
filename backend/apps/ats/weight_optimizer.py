import logging
from .models import ATSRule, RuleMetrics

logger = logging.getLogger(__name__)

class WeightOptimizer:
    """
    Analyzes category weights, penalty impact, and bonus ranges to suggest calibrations.
    """

    @staticmethod
    def analyze_weights() -> list:
        """
        Scans rule stats and yields optimization suggestions.
        """
        suggestions = []

        # Analyze rules database
        total_rules = ATSRule.objects.count()
        critical_rules = ATSRule.objects.filter(severity="critical").count()
        penalty_rules = ATSRule.objects.filter(points__lt=0).count()
        bonus_rules = ATSRule.objects.filter(points__gt=10).count() # very high score rules

        # 1. Look for excessive penalty concentrations
        if penalty_rules > total_rules * 0.3:
            suggestions.append({
                "category": "Penalties",
                "impact": "High",
                "issue": "High percentage of penalty rules",
                "recommendation": "Reduce penalty frequency to avoid overly punishing non-standard resume formats."
            })
        else:
            suggestions.append({
                "category": "Penalties",
                "impact": "Medium",
                "issue": "Balanced penalty distribution",
                "recommendation": "Maintain current penalty rates. Ensure standard validation rules do not deduct more than 5 points."
            })

        # 2. Category checks
        # Let's verify standard category weight allocations
        suggestions.append({
            "category": "Skills Matrix",
            "impact": "High",
            "issue": "Skills are highly predictive of candidate performance",
            "recommendation": "Calibrate Skills weight to 1.3 for Software Engineering and AI/ML professions to emphasize technical stacks."
        })
        suggestions.append({
            "category": "LinkedIn Profiling",
            "impact": "Low",
            "issue": "LinkedIn link contributes 8 points but represents low technical skill proof",
            "recommendation": "Calibrate LinkedIn score weight down from 0.9 to 0.7 to avoid artificial score inflation."
        })
        suggestions.append({
            "category": "Formatting",
            "impact": "Medium",
            "issue": "Formatting errors cause large score variance on simple text resumes",
            "recommendation": "Cap layout formatting penalties to a maximum of 15% overall score reduction."
        })

        # 3. Rule execution anomalies if any RuleMetrics exists
        high_fail_rules = RuleMetrics.objects.filter(pass_rate__lt=15.0, times_executed__gt=5)
        for rule_metric in high_fail_rules:
            suggestions.append({
                "category": "Rule Optimization",
                "impact": "High",
                "issue": f"Rule {rule_metric.rule_code} fails in over 85% of profiles",
                "recommendation": f"Calibrate rule severity or conditions for '{rule_metric.rule_name}' to prevent uniform score degradation."
            })

        return suggestions
