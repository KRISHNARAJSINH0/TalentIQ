from apps.ats.adjustment_manager import AdjustmentManager

class ScoreAdjuster:
    """
    ScoreAdjuster helper class to apply adjustments to the overall score.
    """

    @staticmethod
    def adjust_score(profile, resume, base_score: int) -> dict:
        """
        Takes profile, resume, and base score, executes penalty & bonus engines,
        and returns the complete adjustments breakdown dictionary.
        """
        return AdjustmentManager.calculate_adjustments(profile, resume, base_score)
