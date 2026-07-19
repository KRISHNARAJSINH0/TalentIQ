from apps.ats.penalty_engine import PenaltyEngine
from apps.ats.bonus_engine import BonusEngine
from apps.ats.profession_engine import ProfessionEngine

class AdjustmentManager:
    """
    Orchestrates the calculation of base scores, penalties, and bonuses
    to produce the final adjusted ATS score.
    """

    @staticmethod
    def calculate_adjustments(profile, resume, base_score: int) -> dict:
        """
        Calculates score adjustments.
        Returns:
            {
                "base_score": int,
                "penalties": int,
                "bonuses": int,
                "final_score": int,
                "penalty_report": list,
                "bonus_report": list
            }
        """
        # 1. Detect profession name
        profile_data = {
            "headline": profile.headline or "",
            "summary": profile.summary or "",
            "skills": [s.skill_name for s in profile.skills.all()] if hasattr(profile, 'skills') else [],
            "experience": [exp.designation + " " + (exp.description or "") for exp in profile.experiences.all()] if hasattr(profile, 'experiences') else []
        }
        
        try:
            profession = ProfessionEngine.detect_profession(profile_data)
        except Exception:
            profession = "Software Engineer"

        # 2. Calculate penalties (returns clamped value and list)
        penalty_score, penalty_report = PenaltyEngine.calculate_penalties(profile, resume, profession)

        # 3. Calculate bonuses (returns clamped value and list)
        bonus_score, bonus_report = BonusEngine.calculate_bonuses(profile, resume, profession)

        # 4. Calculate final score
        # Base ATS + Penalties + Bonuses
        # (Note: penalty_score is already negative or zero, e.g. -12, bonus_score is positive, e.g. +8)
        raw_final = base_score + penalty_score + bonus_score
        
        # Clamp final score between 0 and 100
        final_score = max(0, min(100, int(raw_final)))

        return {
            "base_score": int(base_score),
            "penalties": int(penalty_score),
            "bonuses": int(bonus_score),
            "final_score": int(final_score),
            "penalty_report": penalty_report,
            "bonus_report": bonus_report
        }
