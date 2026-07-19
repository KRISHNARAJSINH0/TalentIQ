from typing import Dict, Any, List
from apps.resumes.models import Resume
from apps.profiles.models import Profile


class CareerRanker:
    """
    Sub-system to categorize candidates into Career Levels and Benchmark Groups.
    """

    CAREER_LEVELS = [
        "Student",
        "Intern",
        "Junior",
        "Mid",
        "Senior",
        "Lead",
        "Architect",
        "Manager",
        "Director"
    ]

    BENCHMARK_GROUPS = [
        "Students",
        "Freshers",
        "Junior Professionals",
        "Mid-Level Professionals",
        "Senior Professionals",
        "Managers",
        "Architects",
        "Researchers",
        "Freelancers"
    ]

    @classmethod
    def determine_career_level(cls, resume: Resume, profile: Profile = None) -> str:
        """
        Determines the career level based on years of experience, current designation, and profile metadata.
        """
        years_exp = 0
        designation = ""
        
        if profile:
            # 1. Experience Years
            try:
                experiences = profile.experiences.all()
                if experiences.exists():
                    total_days = 0
                    from datetime import date
                    for exp in experiences:
                        start = exp.start_date
                        end = exp.end_date or date.today()
                        if start and end:
                            total_days += (end - start).days
                    years_exp = max(0, total_days // 365)
                elif resume.parsed_json:
                    years_exp = resume.parsed_json.get("experience_years", 0)
            except Exception:
                years_exp = 0
                
            # 2. Designation Title
            designation = getattr(profile, "headline", "") or ""
            if not designation:
                try:
                    latest_exp = profile.experiences.order_by("-start_date").first()
                    if latest_exp:
                        designation = latest_exp.designation
                except Exception:
                    pass
            if not designation and resume.parsed_json:
                designation = resume.parsed_json.get("current_role", "")
            designation = designation.lower()
        else:
            # Try to read parsed details in resume model if available
            parsed = resume.parsed_json
            if isinstance(parsed, dict):
                years_exp = parsed.get("experience_years", 0)
                designation = parsed.get("current_role", "").lower()

        # Classification rules
        if "director" in designation or "vp" in designation or "head" in designation:
            return "Director"
        if "manager" in designation or "lead" in designation or "principal" in designation:
            if years_exp >= 10:
                return "Director"
            return "Manager" if "manager" in designation else "Lead"
        if "architect" in designation:
            return "Architect"
        
        # Years of experience rules
        if years_exp == 0:
            if "student" in designation or "intern" in designation:
                return "Student" if "student" in designation else "Intern"
            return "Student"
        elif years_exp < 2:
            return "Intern" if "intern" in designation else "Junior"
        elif years_exp < 5:
            return "Mid"
        elif years_exp < 8:
            return "Senior"
        elif years_exp < 12:
            return "Lead"
        else:
            return "Architect"

    @classmethod
    def get_benchmark_group(cls, career_level: str, is_freelancer: bool = False, is_researcher: bool = False) -> str:
        """
        Maps a career level to a benchmark group.
        """
        if is_freelancer:
            return "Freelancers"
        if is_researcher:
            return "Researchers"
            
        mapping = {
            "Student": "Students",
            "Intern": "Freshers",
            "Junior": "Junior Professionals",
            "Mid": "Mid-Level Professionals",
            "Senior": "Senior Professionals",
            "Lead": "Senior Professionals",
            "Architect": "Architects",
            "Manager": "Managers",
            "Director": "Managers"
        }
        return mapping.get(career_level, "Mid-Level Professionals")
