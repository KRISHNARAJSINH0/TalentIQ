import re
from apps.profiles.models import Skill

class BonusEngine:
    """
    Evaluates ATS bonuses based on:
    General bonuses and role-specific bonuses.
    Clamps the total bonuses to a maximum boost of +20.
    """

    @staticmethod
    def calculate_bonuses(profile, resume, profession_name="Software Engineer") -> tuple:
        """
        Calculates all active bonuses.
        Returns:
            (total_bonus_points, list_of_bonus_reports)
        """
        bonuses = []
        
        # Helper: add bonus
        def add_bonus(category, name, points):
            bonuses.append({
                "category": category,
                "name": name,
                "points": int(points)
            })

        # Fetch related objects safely
        skills = list(profile.skills.all()) if hasattr(profile, 'skills') else []
        experiences = list(profile.experiences.all()) if hasattr(profile, 'experiences') else []
        projects = list(profile.projects.all()) if hasattr(profile, 'projects') else []
        publications = list(profile.publications.all()) if hasattr(profile, 'publications') else []
        volunteer = list(profile.volunteer_work.all()) if hasattr(profile, 'volunteer_work') else []

        # Get text contents
        summary_text = (profile.summary or "").strip()
        extracted_text = getattr(resume, "extracted_text", "") or ""
        experiences_text = " ".join([exp.designation + " " + (exp.description or "") for exp in experiences])
        projects_text = " ".join([proj.project_name + " " + (proj.description or "") + " " + (proj.technologies or "") for proj in projects])
        full_text = f"{summary_text} {experiences_text} {projects_text} {extracted_text}".strip()
        full_text_lower = full_text.lower()

        # Normalize profession name for checks
        prof_lower = (profession_name or "").lower()

        # ----------------------------------------------------
        # 1. GENERAL BONUSES
        # ----------------------------------------------------
        # Strong Summary (+5)
        # Length > 100 characters and contains achievements or keywords
        summary_words = summary_text.split()
        if len(summary_text) > 100 and len(summary_words) >= 15:
            # check if it contains a keyword or skill
            has_kw = any(s.skill_name.lower() in summary_text.lower() for s in skills)
            if has_kw:
                add_bonus("General", "Strong Summary", 5)

        # Leadership (+5)
        leadership_words = ["lead", "led", "managed", "headed", "spearheaded", "directed", "supervised", "coordinate", "coordinated"]
        if any(re.search(r"\b" + re.escape(w) + r"\b", full_text_lower) for w in leadership_words):
            add_bonus("General", "Leadership", 5)

        # Open Source (+6)
        if any(term in full_text_lower for term in ["open-source", "open source", "contributed to"]):
            add_bonus("General", "Open Source", 6)

        # Hackathon Winner (+5)
        if any(term in full_text_lower for term in ["hackathon", "hackathon winner", "won hackathon", "1st place"]):
            add_bonus("General", "Hackathon Winner", 5)

        # Research Paper (+8)
        if publications or any(term in full_text_lower for term in ["research paper", "ieee", "springer", "journal", "published paper", "conference paper"]):
            add_bonus("General", "Research Paper", 8)

        # Patent (+10)
        if any(term in full_text_lower for term in ["patent", "patented", "patent pending"]):
            add_bonus("General", "Patent", 10)

        # Portfolio (+5)
        portfolio_url = (profile.portfolio_url or "").strip() if hasattr(profile, 'portfolio_url') else ""
        if portfolio_url:
            add_bonus("General", "Portfolio", 5)

        # GitHub (+5)
        github_url = (profile.github or "").strip() if hasattr(profile, 'github') else ""
        if github_url:
            add_bonus("General", "GitHub", 5)

        # LinkedIn (+2)
        linkedin_url = (profile.linkedin or "").strip() if hasattr(profile, 'linkedin') else ""
        if linkedin_url:
            add_bonus("General", "LinkedIn", 2)

        # Internship (+4)
        if any("intern" in exp.designation.lower() or "internship" in exp.description.lower() for exp in experiences):
            add_bonus("General", "Internship", 4)

        # Published Article (+5)
        if len(publications) > 0:
            add_bonus("General", "Published Article", 5)

        # Volunteer Work (+3)
        if len(volunteer) > 0:
            add_bonus("General", "Volunteer Work", 3)

        # Mentoring (+3)
        mentor_words = ["mentor", "mentored", "coached", "trained", "teaching assistant"]
        if any(re.search(r"\b" + re.escape(w) + r"\b", full_text_lower) for w in mentor_words):
            add_bonus("General", "Mentoring", 3)

        # Strong Action Verbs (+4)
        action_verbs = ["created", "designed", "engineered", "implemented", "optimized", "developed", "delivered", "built"]
        if any(re.search(r"\b" + re.escape(w) + r"\b", full_text_lower) for w in action_verbs):
            add_bonus("General", "Strong Action Verbs", 4)

        # Quantified Achievements (+6)
        # Look for percentages or currency metrics in experiences
        achievement_pattern = re.compile(r"(\d+%\s*(increase|decrease|improvement|saved|reduction)|\$\d+(k|m|d)?|\d+\s*percent)")
        if achievement_pattern.search(experiences_text) or achievement_pattern.search(summary_text):
            add_bonus("General", "Quantified Achievements", 6)

        # Live Projects (+5)
        if any((proj.live_url or "").strip() for proj in projects):
            add_bonus("General", "Live Projects", 5)

        # ----------------------------------------------------
        # 2. ROLE-SPECIFIC BONUSES
        # ----------------------------------------------------
        skill_names = [s.skill_name.lower().strip() for s in skills]
        
        if "software engineer" in prof_lower or "developer" in prof_lower or "engineer" in prof_lower:
            # Software Engineer Role Bonuses
            if "docker" in skill_names or "docker" in full_text_lower:
                add_bonus("Role Specific", "Docker", 2)
            if "redis" in skill_names or "redis" in full_text_lower:
                add_bonus("Role Specific", "Redis", 2)
            if "aws" in skill_names or "aws" in full_text_lower:
                add_bonus("Role Specific", "AWS", 3)
            if "ci/cd" in skill_names or "ci/cd" in full_text_lower or "jenkins" in full_text_lower or "github actions" in full_text_lower:
                add_bonus("Role Specific", "CI/CD", 2)
            if "kubernetes" in skill_names or "kubernetes" in full_text_lower or "k8s" in full_text_lower:
                add_bonus("Role Specific", "Kubernetes", 3)

        elif "data analyst" in prof_lower or "scientist" in prof_lower or "analyst" in prof_lower:
            # Data Analyst Role Bonuses
            if "power bi" in skill_names or "power bi" in full_text_lower:
                add_bonus("Role Specific", "Power BI", 3)
            if "sql" in skill_names or "sql" in full_text_lower:
                add_bonus("Role Specific", "SQL", 3)
            if "statistics" in skill_names or "statistics" in full_text_lower:
                add_bonus("Role Specific", "Statistics", 2)
            if "machine learning" in skill_names or "machine learning" in full_text_lower or "ml" in full_text_lower:
                add_bonus("Role Specific", "Machine Learning", 3)

        elif "designer" in prof_lower or "ui" in prof_lower or "ux" in prof_lower:
            # Designer Role Bonuses
            if portfolio_url:
                add_bonus("Role Specific", "Portfolio Link", 6)
            if "behance" in full_text_lower:
                add_bonus("Role Specific", "Behance Profile", 4)
            if "dribbble" in full_text_lower:
                add_bonus("Role Specific", "Dribbble Profile", 4)

        # Compute raw total bonuses
        raw_total = sum(b["points"] for b in bonuses)
        
        # Clamp to max positive boost of +20
        clamped_total = min(20, raw_total)

        return clamped_total, bonuses
