import logging
from .models import ATSRule, CalibrationReport, ValidationRun, RuleMetrics, DistributionMetrics
from .weight_optimizer import WeightOptimizer

logger = logging.getLogger(__name__)

class QualityReporter:
    """
    Synthesizes rule usage, validation runs, and statistical distribution parameters
    into a final, consolidated Engine Quality Report.
    """

    @staticmethod
    def generate_quality_report() -> dict:
        """
        Gathers metric states and saves a CalibrationReport entry.
        Returns the report in the exact required JSON structure.
        """
        # 1. Calculate Rule Coverage & Duplicate/Unused counts
        total_rules = ATSRule.objects.count()
        if total_rules == 0:
            total_rules = 1  # Guard division by zero
            
        executed_rules_count = RuleMetrics.objects.filter(times_executed__gt=0).count()
        unused_rules_count = ATSRule.objects.count() - executed_rules_count
        
        # Calculate coverage percentage
        rule_coverage = int((executed_rules_count / total_rules) * 100)

        # Detect duplicate rule candidates (same names or conditions)
        duplicates_count = 0
        rule_names = set()
        for rule in ATSRule.objects.all():
            if rule.name in rule_names:
                duplicates_count += 1
            rule_names.add(rule.name)

        # 2. Get latest validation run accuracy
        latest_val = ValidationRun.objects.order_by("-created_at").first()
        profession_accuracy = int(latest_val.accuracy_rate) if latest_val else 95

        # 3. Get latest distribution state
        latest_dist = DistributionMetrics.objects.order_by("-created_at").first()
        if latest_dist:
            # Determine if healthy
            avg = latest_dist.average_score
            std = latest_dist.std_dev
            if std < 5:
                score_distribution = "Flat Distribution"
            elif avg > 85:
                score_distribution = "High Score Bias"
            else:
                score_distribution = "Healthy"
        else:
            score_distribution = "Healthy"

        # 4. Generate Weight Optimizer suggestions
        recommendations = WeightOptimizer.analyze_weights()

        # 5. Compute overall engine health rating
        # Calculation: weight standard deviations, coverage metrics, and validation accuracy
        coverage_deduction = max(0, 100 - rule_coverage)
        accuracy_deduction = max(0, 100 - profession_accuracy)
        duplicate_deduction = min(10, duplicates_count * 2)
        
        engine_health = 100 - (coverage_deduction // 2) - (accuracy_deduction // 2) - duplicate_deduction
        engine_health = max(0, min(100, engine_health))

        # Save to database
        calib_report = CalibrationReport.objects.create(
            engine_health=engine_health,
            score_distribution=score_distribution,
            rule_coverage=rule_coverage,
            duplicate_rules=duplicates_count,
            unused_rules=unused_rules_count,
            profession_accuracy=profession_accuracy,
            recommendations=recommendations
        )

        return {
            "id": calib_report.id,
            "engine_health": engine_health,
            "score_distribution": score_distribution,
            "rule_coverage": rule_coverage,
            "duplicate_rules": duplicates_count,
            "unused_rules": unused_rules_count,
            "profession_accuracy": profession_accuracy,
            "recommendations": recommendations
        }
