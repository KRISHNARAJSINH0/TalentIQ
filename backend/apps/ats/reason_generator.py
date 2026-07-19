import logging

logger = logging.getLogger(__name__)

class ReasonGenerator:
    """
    Generates human-readable, context-aware reasons for category scores.
    """

    @classmethod
    def generate_reason(cls, category: str, score: float, strengths: list, weaknesses: list, profile) -> str:
        """
        Generates a custom explanation string based on the category, score, strengths, and weaknesses.
        """
        cat_lower = category.lower()
        
        # Format lists for inclusion
        weakness_str = f" (e.g., {', '.join(weaknesses[:2])})" if weaknesses else ""
        strength_str = f" (e.g., {', '.join(strengths[:2])})" if strengths else ""

        if "contact" in cat_lower:
            if score >= 90:
                return f"Your contact section is outstanding{strength_str}. All critical channels (email, phone, LinkedIn) are present and verified."
            elif score >= 70:
                return f"Your contact details are mostly complete, but some professional links or location details are missing{weakness_str}."
            else:
                return f"Critical contact details are missing or malformed{weakness_str}. This heavily restricts recruiter reach."

        elif "summary" in cat_lower or "professional summary" in cat_lower:
            if score >= 90:
                return f"Your professional summary is exceptionally structured, using active voice and outlining clear industry alignments{strength_str}."
            elif score >= 70:
                return f"Your summary is present but lacks active voice, strong action verbs, or role-specific jargon{weakness_str}."
            else:
                return f"Your professional summary is missing or extremely brief{weakness_str}, missing a vital elevator pitch opportunity."

        elif "skill" in cat_lower:
            if score >= 90:
                return f"Your skills profile is highly competitive and covers the essential technical stack and soft skills required for the role{strength_str}."
            elif score >= 70:
                return f"Your skill alignment is moderate, but you are missing some key required or recommended skills{weakness_str}."
            else:
                return f"Significant skill gaps detected{weakness_str}. You must add more industry-relevant core competencies to match search filters."

        elif "project" in cat_lower:
            if score >= 90:
                return f"Excellent projects showcase{strength_str}, indicating hands-on capability with repository links and detailed tech stacks."
            elif score >= 70:
                return f"Projects are present but lack live demo links, repository references, or clear technology descriptions{weakness_str}."
            else:
                return f"No projects or highly brief projects listed{weakness_str}. Adding detailed projects is crucial to demonstrate practical ability."

        elif "experience" in cat_lower or "work experience" in cat_lower:
            if score >= 90:
                return f"Your professional history shows strong career progression, detailed designations, and impact-driven descriptions{strength_str}."
            elif score >= 70:
                return f"Work experience is present but description bullets are too brief or lack action verbs and quantified achievements{weakness_str}."
            else:
                return f"Your experience section is either missing, extremely short, or has critical formatting issues{weakness_str}."

        elif "education" in cat_lower:
            if score >= 90:
                return f"Your education section is well-structured and aligns with typical requirements for this profession{strength_str}."
            elif score >= 70:
                return f"Your education records are present but missing key fields such as graduation dates, GPAs, or fields of study{weakness_str}."
            else:
                return f"Your education credentials are not properly detailed or are completely missing{weakness_str}."

        elif "achievement" in cat_lower:
            if score >= 90:
                return f"Strong validation of your professional success, showcasing awards, publications, or competitive achievements{strength_str}."
            elif score >= 70:
                return f"Achievements are listed but could be framed more effectively to highlight their business or technical impact{weakness_str}."
            else:
                return f"No key achievements or certifications are listed{weakness_str}, missing an opportunity to stand out from other candidates."

        # Fallback for other categories
        if score >= 85:
            return f"Excellent performance in {category} scoring{strength_str}."
        elif score >= 70:
            return f"Satisfactory {category} alignment, but has room for improvement{weakness_str}."
        else:
            return f"Needs immediate attention in {category}{weakness_str}."
