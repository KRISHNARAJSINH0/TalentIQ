import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class EvidenceEngine:
    """
    Extracts quantitative, concrete metrics from the candidate's profile and resume.
    """

    @classmethod
    def gather_evidence(cls, category: str, profile, resume, ctx: dict = None) -> str:
        """
        Extracts empirical data points from the profile for the specific category.
        """
        cat_lower = category.lower()

        # Safely load collections
        skills = list(profile.skills.all()) if hasattr(profile, "skills") else []
        experiences = list(profile.experiences.all()) if hasattr(profile, "experiences") else []
        projects = list(profile.projects.all()) if hasattr(profile, "projects") else []
        educations = list(profile.educations.all()) if hasattr(profile, "educations") else []
        certifications = list(profile.certifications.all()) if hasattr(profile, "certifications") else []

        if "contact" in cat_lower:
            channels = []
            if getattr(profile.user, "email", None): channels.append("Email")
            if getattr(profile.user, "phone", None) or getattr(profile, "phone", None): channels.append("Phone")
            
            # Check links
            links = profile.links if hasattr(profile, "links") and profile.links else []
            if isinstance(links, str):
                links = [links]
            
            has_linkedin = any("linkedin.com" in l.lower() for l in links)
            has_github = any("github.com" in l.lower() for l in links)
            
            if has_linkedin: channels.append("LinkedIn")
            if has_github: channels.append("GitHub")
            if getattr(profile, "address", None): channels.append("Location Details")

            evidence = f"Found {len(channels)} verified contact fields: {', '.join(channels)}."
            missing = []
            if "LinkedIn" not in channels: missing.append("LinkedIn profile")
            if "GitHub" not in channels: missing.append("GitHub link")
            if "Phone" not in channels: missing.append("phone number")
            
            if missing:
                evidence += f" Missing {', '.join(missing)}."
            return evidence

        elif "summary" in cat_lower or "professional summary" in cat_lower:
            summary = getattr(profile, "summary", "") or ""
            words = len(summary.split())
            if words == 0:
                return "No professional summary exists in your profile."
            
            # Simple active voice check
            active_verbs = ["lead", "led", "manage", "managed", "build", "built", "spearhead", "spearheaded", "design", "designed", "deliver", "delivered"]
            verb_count = sum(1 for v in active_verbs if v in summary.lower())
            
            evidence = f"Summary contains {words} words and utilizes {verb_count} strong action verbs."
            if words < 30:
                evidence += " Word count is under the recommended minimum of 30 words."
            elif words > 100:
                evidence += " Word count exceeds the recommended maximum of 100 words (keep it punchy)."
            return evidence

        elif "skill" in cat_lower:
            tech_count = sum(1 for s in skills if getattr(s, "skill_type", "") == "technical")
            soft_count = sum(1 for s in skills if getattr(s, "skill_type", "") == "soft")
            if not skills:
                return "Zero skills are registered in your profile."
            
            # Check profession profile skills from ctx
            missing_req = []
            if ctx and "missing_required_skills" in ctx:
                missing_req = ctx["missing_required_skills"]
            elif ctx and "profession_profile" in ctx:
                missing_req = ctx["profession_profile"].get("missing_required_skills", [])

            evidence = f"Profile contains {len(skills)} skills ({tech_count} technical, {soft_count} soft)."
            if missing_req:
                evidence += f" Missing {len(missing_req)} required role skills: {', '.join(missing_req[:3])}."
            else:
                evidence += " Matches all required skills in the profession profile."
            return evidence

        elif "project" in cat_lower:
            if not projects:
                return "No projects are registered on your profile."
            
            with_github = sum(1 for p in projects if getattr(p, "github_url", None) or "github.com" in (getattr(p, "url", "") or "").lower())
            with_live = sum(1 for p in projects if getattr(p, "live_url", None) or (getattr(p, "url", "") and "github.com" not in getattr(p, "url", "").lower()))
            
            return f"Found {len(projects)} listed projects. {with_github} have code repository links; {with_live} have live validation URLs."

        elif "experience" in cat_lower or "work experience" in cat_lower:
            if not experiences:
                return "No work experience history exists in your profile."
            
            total_years = 0
            for exp in experiences:
                start = getattr(exp, "start_date", None)
                end = getattr(exp, "end_date", None) or datetime.now().date()
                if start:
                    total_years += (end - start).days / 365.25
            
            # Check descriptions for metrics/numbers
            metric_descriptions = 0
            for exp in experiences:
                desc = getattr(exp, "description", "") or ""
                if re.search(r'\b\d+%\b|\b\d+\s*(?:million|k|usd|dollars|users|hours|seconds|percent)\b|\b\$\d+', desc.lower()):
                    metric_descriptions += 1
            
            evidence = f"Found {len(experiences)} work experience entries spanning {total_years:.1f} total years."
            if metric_descriptions > 0:
                evidence += f" {metric_descriptions} descriptions include quantified results or performance metrics."
            else:
                evidence += " Descriptions do not contain quantified achievements (e.g. %, $, numbers)."
            return evidence

        elif "education" in cat_lower:
            if not educations:
                return "No education history is registered in your profile."
            
            degrees = [getattr(e, "degree", "") for e in educations if getattr(e, "degree", "")]
            grades = sum(1 for e in educations if getattr(e, "grade", "") or getattr(e, "gpa", ""))
            
            evidence = f"Found {len(educations)} education records: {', '.join(degrees)}."
            if grades > 0:
                evidence += f" {grades} records have GPA/grade indicators."
            else:
                evidence += " Missing grades or GPAs for academic proof."
            return evidence

        elif "achievement" in cat_lower:
            achievement_count = 0
            # Check achievement text or other models
            achievements_text = getattr(profile, "achievements", None)
            if achievements_text:
                if isinstance(achievements_text, str):
                    achievement_count += len(achievements_text.split('\n'))
                else:
                    # It's a RelatedManager or similar list of achievement objects
                    try:
                        achievement_count += achievements_text.count()
                    except Exception:
                        try:
                            achievement_count += len(list(achievements_text.all()))
                        except Exception:
                            achievement_count = 0
            
            evidence = f"Found {len(certifications)} certifications and {achievement_count} achievement items."
            return evidence

        # Fallback
        return f"Evaluated details for category '{category}'."
