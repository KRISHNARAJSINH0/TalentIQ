import re
from datetime import datetime

class EducationEngine:
    """
    Evaluates the quality, degree relevance, GPAs, and timelines of Education details.
    """

    @staticmethod
    def analyze(profile, resume, profile_data: dict) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Get educations
        educations = []
        if hasattr(profile, 'educations') and profile.educations:
            if hasattr(profile.educations, 'all'):
                educations = list(profile.educations.all())
            elif isinstance(profile.educations, list):
                educations = profile.educations

        if not educations:
            return {
                "category": "Education",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No education details listed on your profile."],
                "recommendations": ["Add your degree, school name, major, and graduation year to complete your education section."],
                "confidence": 95
            }

        # 1. Degree completeness and quality
        has_degree = False
        has_field = False
        gpa_list = []
        field_matches = False
        
        # Keywords matching desired education field from the profile role
        # We can extract the main industry or role to verify relevance
        role = profile_data.get("role", "").lower()
        tech_keywords = ["computer", "software", "information technology", "engineering", "science", "math", "physics"]
        biz_keywords = ["business", "management", "administration", "marketing", "finance", "economics", "mba"]
        creative_keywords = ["design", "art", "media", "fashion", "fine arts", "animation"]

        for edu in educations:
            degree = (getattr(edu, 'degree', '') or getattr(edu, 'degree_name', '') or "").strip()
            field = (getattr(edu, 'field_of_study', '') or getattr(edu, 'major', '') or "").strip()
            school = (getattr(edu, 'school_name', '') or getattr(edu, 'institution', '') or "").strip()
            gpa = (getattr(edu, 'gpa', '') or getattr(edu, 'cgpa', '') or "").strip()
            
            # Check fields
            if degree:
                has_degree = True
            if field:
                has_field = True

            # Relevance check
            field_lower = field.lower()
            if any(tk in role for tk in ["engineer", "developer", "scientist", "analyst", "tech", "devops"]):
                if any(tk in field_lower for tk in tech_keywords):
                    field_matches = True
            elif any(bk in role for bk in ["manager", "executive", "sales", "hr", "accountant", "analyst"]):
                if any(bk in field_lower for bk in biz_keywords):
                    field_matches = True
            elif any(ck in role for ck in ["designer", "animator", "artist", "editor", "photographer"]):
                if any(ck in field_lower for ck in creative_keywords):
                    field_matches = True

            # GPA checks
            if gpa:
                # Extract GPA numbers e.g. "3.8/4.0", "9.2/10", "3.8"
                numbers = re.findall(r"\b\d+(?:\.\d+)?\b", gpa)
                if len(numbers) >= 1:
                    val = float(numbers[0])
                    gpa_list.append(val)

        # Apply score deductions/increases
        if not has_degree:
            score -= 20.0
            weaknesses.append("Degree name/type is missing.")
            recommendations.append("Specify the full name of the degree earned (e.g. Bachelor of Science).")
        else:
            strengths.append("Degree type is clearly presented.")

        if not has_field:
            score -= 15.0
            weaknesses.append("Major or field of study is missing.")
            recommendations.append("Specify your major or field of study for all degrees.")
        else:
            strengths.append("Major/Field of study is present.")

        # Relevance feedback
        if has_field:
            if field_matches:
                strengths.append("Degree major aligns perfectly with the target role.")
            else:
                score -= 10.0
                weaknesses.append("Degree field of study appears unrelated to the target role.")
                recommendations.append("If your degree is in a different field, add relevant certifications or bootcamps to bridge the gap.")

        # GPA analysis
        if gpa_list:
            avg_gpa = sum(gpa_list) / len(gpa_list)
            # If standard 4.0 scale
            if avg_gpa <= 4.0:
                if avg_gpa >= 3.5:
                    strengths.append(f"Excellent academic performance (GPA: {avg_gpa}/4.0).")
                elif avg_gpa < 2.5:
                    score -= 10.0
                    weaknesses.append(f"Relatively low GPA score ({avg_gpa}/4.0).")
                    recommendations.append("If your GPA is below 3.0, consider removing it from your resume and focusing on project work instead.")
            # If 10.0 scale (common in India)
            elif avg_gpa <= 10.0:
                if avg_gpa >= 8.5:
                    strengths.append(f"Excellent academic performance (CGPA: {avg_gpa}/10.0).")
                elif avg_gpa < 6.5:
                    score -= 10.0
                    weaknesses.append(f"Relatively low CGPA score ({avg_gpa}/10.0).")
                    recommendations.append("Consider leaving off lower GPAs/CGPAs and letting your practical projects stand out.")
        else:
            # Missing GPA is neutral (neither penalty nor positive)
            pass

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Education",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
