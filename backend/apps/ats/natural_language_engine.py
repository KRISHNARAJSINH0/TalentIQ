import logging

logger = logging.getLogger(__name__)

class NaturalLanguageEngine:
    """
    Synthesizes the numerical scores and categorical insights into a cohesive, 
    professional natural language explanation paragraph.
    """

    @classmethod
    def generate_report(cls, overall_score: int, profession: str, category_scores: list, strengths: list, weaknesses: list) -> str:
        """
        Creates a custom summary text explaining the score details.
        """
        # Determine standing based on score
        if overall_score >= 90:
            standing = "an exceptionally strong, ATS-optimized candidate profile"
            critique = "It excels across all core criteria, including tech stack density, formatted layout, and quantified professional proof."
        elif overall_score >= 80:
            standing = "a highly competitive candidate profile"
            critique = "You satisfy almost all industry criteria and have a well-structured layout. With a few minor adjustments, it can easily reach top-tier status."
        elif overall_score >= 70:
            standing = "an average, decent candidate profile"
            critique = "Your foundational sections are present and readable. However, to stand out in automated ATS filters, you need to address specific skill gaps and optimize project documentation."
        else:
            standing = "a profile requiring immediate, comprehensive enhancements"
            critique = "Critical structural areas are currently lacking or not optimized, which will result in low parsing confidence and high rejection rates in automated screeners."

        # Pick key strengths and weaknesses
        strength_points = f" Notable strengths include your {', and your '.join(strengths[:2]).lower()}." if strengths else ""
        weakness_points = f" However, key drawbacks limiting your visibility are {', and '.join(weaknesses[:2]).lower()}." if weaknesses else ""

        # Construct final paragraph
        report = (
            f"Your resume evaluates to an overall ATS score of {overall_score}/100, indicating {standing} "
            f"for {profession} positions. {critique}{strength_points}{weakness_points} We recommend reviewing "
            f"the prioritized action items below to systematically address these weaknesses and boost your score."
        )

        return report
