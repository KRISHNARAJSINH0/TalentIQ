import re
from datetime import date
from django.utils.timezone import now

class PenaltyEngine:
    """
    Evaluates ATS penalties based on various categories:
    Contact, Summary, Skills, Projects, Experience, Education, Certifications, Formatting, Grammar.
    Clamps the total penalty score to a maximum deduction of -30.
    """

    @staticmethod
    def calculate_penalties(profile, resume, profession_name="Software Engineer") -> tuple:
        """
        Calculates all active penalties.
        Returns:
            (total_penalty_points, list_of_penalty_reports)
        """
        penalties = []
        
        # Helper: add penalty
        def add_penalty(category, name, points):
            penalties.append({
                "category": category,
                "name": name,
                "points": int(points)
            })

        # Fetch related objects safely
        skills = list(profile.skills.all()) if hasattr(profile, 'skills') else []
        experiences = list(profile.experiences.all()) if hasattr(profile, 'experiences') else []
        projects = list(profile.projects.all()) if hasattr(profile, 'projects') else []
        educations = list(profile.educations.all()) if hasattr(profile, 'educations') else []
        certifications = list(profile.certifications.all()) if hasattr(profile, 'certifications') else []

        # Get full text for text checks
        summary_text = (profile.summary or "").strip()
        extracted_text = getattr(resume, "extracted_text", "") or ""
        experiences_text = " ".join([exp.designation + " " + (exp.description or "") for exp in experiences])
        projects_text = " ".join([proj.project_name + " " + (proj.description or "") + " " + (proj.technologies or "") for proj in projects])
        full_text = f"{summary_text} {experiences_text} {projects_text} {extracted_text}".strip()
        full_text_lower = full_text.lower()

        # Normalize profession name for checks
        prof_lower = (profession_name or "").lower()

        # ----------------------------------------------------
        # 1. CONTACT PENALTIES
        # ----------------------------------------------------
        email = (profile.user.email or "").strip() if (profile.user and hasattr(profile.user, 'email')) else ""
        phone = (profile.user.phone or "").strip() if (profile.user and hasattr(profile.user, 'phone')) else ""
        
        if not email:
            add_penalty("Contact", "Missing Email", -15)
        else:
            # simple email regex check
            if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
                add_penalty("Contact", "Invalid Email", -20)

        if not phone:
            add_penalty("Contact", "Missing Phone", -10)
        else:
            # invalid phone if less than 7 digits or non-supported characters
            digits_only = re.sub(r"\D", "", phone)
            if len(digits_only) < 7:
                add_penalty("Contact", "Invalid Phone", -15)

        linkedin = (profile.linkedin or "").strip() if hasattr(profile, 'linkedin') else ""
        if not linkedin:
            add_penalty("Contact", "Missing LinkedIn", -4)

        github = (profile.github or "").strip() if hasattr(profile, 'github') else ""
        if not github:
            if "software" in prof_lower or "developer" in prof_lower or "engineer" in prof_lower:
                add_penalty("Contact", "Missing GitHub", -6)
            elif "data" in prof_lower or "analyst" in prof_lower:
                add_penalty("Contact", "Missing GitHub", -3)
            elif "teacher" in prof_lower:
                pass
            elif "doctor" in prof_lower:
                pass

        # ----------------------------------------------------
        # 2. SUMMARY PENALTIES
        # ----------------------------------------------------
        summary_words = summary_text.split()
        if not summary_text:
            add_penalty("Summary", "Missing Summary", -4)
        elif len(summary_text) < 50 or len(summary_words) < 10:
            add_penalty("Summary", "Very Short Summary", -4)

        # Generic summary
        generic_phrases = [
            "looking for a challenging opportunity",
            "seeking a challenging position",
            "utilize my skills",
            "hardworking individual",
            "self-motivated professional",
            "dynamic professional",
            "proven track record",
            "results-oriented professional",
            "seeking to leverage"
        ]
        if summary_text and any(phrase in summary_text.lower() for phrase in generic_phrases):
            add_penalty("Summary", "Generic Summary", -5)

        # Objective instead of summary
        objective_indicators = [
            "career objective",
            "objective:",
            "seeking an entry-level position",
            "seeking a position where I can",
            "seeking to secure a position"
        ]
        if summary_text and any(ind in summary_text.lower() for ind in objective_indicators):
            add_penalty("Summary", "Career Objective Instead of Summary", -4)

        # Grammar/Spelling Errors in Summary
        # Quick summary spelling test: check if common typos in summary
        from apps.ats.services import COMMON_TYPOS
        summary_spelling_errors = 0
        for typo in COMMON_TYPOS:
            if re.search(r'\b' + re.escape(typo) + r'\b', summary_text.lower()):
                summary_spelling_errors += 1
        if summary_spelling_errors > 0:
            add_penalty("Summary", "Grammar Errors", -3)

        # No keywords in Summary
        # Check if at least 1 keyword or skill name is mentioned in summary
        has_kw_in_summary = False
        if summary_text:
            for skill in skills:
                if skill.skill_name.lower() in summary_text.lower():
                    has_kw_in_summary = True
                    break
        if summary_text and not has_kw_in_summary:
            add_penalty("Summary", "No Keywords", -5)

        # ----------------------------------------------------
        # 3. SKILL PENALTIES
        # ----------------------------------------------------
        skill_names = [s.skill_name.lower().strip() for s in skills]
        
        # Duplicate skills
        duplicates = len(skill_names) - len(set(skill_names))
        if duplicates > 0:
            add_penalty("Skills", "Duplicate Skills", -2)

        # Only Generic Skills
        # If all skills are soft/general and zero technical
        from apps.profiles.models import Skill
        has_tech = any(s.skill_type == Skill.SkillType.TECHNICAL for s in skills)
        if skills and not has_tech:
            add_penalty("Skills", "Only Generic Skills", -10)

        # No Role Skills
        # If skills list is empty, or none match the profession keyword list
        # Check for role keywords
        role_keywords = {
            "software engineer": ["python", "java", "javascript", "c++", "c#", "go", "rust", "react", "django", "node", "docker", "kubernetes", "aws", "git", "sql", "postgresql"],
            "data analyst": ["sql", "python", "r", "tableau", "power bi", "excel", "pandas", "numpy", "statistics", "data visualization", "cleaning", "modeling"],
            "designer": ["figma", "sketch", "photoshop", "illustrator", "ui", "ux", "wireframe", "prototype", "behance", "dribbble"]
        }
        target_kws = role_keywords.get(prof_lower, ["python", "management", "excel", "communication"])
        has_role_skill = any(kw in skill_names for kw in target_kws) if skills else False
        if not has_role_skill:
            add_penalty("Skills", "No Role Skills", -12)

        # Outdated Technologies
        outdated_tech = ["fortran", "cobol", "cvs", "subversion", "windows 95", "windows 98", "mac os 9", "silverlight", "flash", "actionscript", "pascal", "delphi", "coldfusion"]
        has_outdated = any(tech in skill_names for tech in outdated_tech)
        if has_outdated:
            add_penalty("Skills", "Outdated Technologies", -5)

        # Keyword Stuffing
        if len(skills) > 25:
            add_penalty("Skills", "Keyword Stuffing", -4)

        # ----------------------------------------------------
        # 4. PROJECT PENALTIES
        # ----------------------------------------------------
        if not projects:
            add_penalty("Projects", "No Projects", -15)
        else:
            # Check No Technologies Mentioned
            no_tech = any(not (proj.technologies or "").strip() for proj in projects)
            if no_tech:
                add_penalty("Projects", "No Technologies Mentioned", -5)

            # Check No Descriptions
            no_desc = any(not (proj.description or "").strip() for proj in projects)
            if no_desc:
                add_penalty("Projects", "No Descriptions", -4)

            # Check No GitHub Link (across all projects)
            no_github = all(not (proj.github_url or "").strip() for proj in projects)
            if no_github:
                add_penalty("Projects", "No GitHub Link", -3)

            # Check No Live Demo (across all projects)
            no_live = all(not (proj.live_url or "").strip() for proj in projects)
            if no_live:
                add_penalty("Projects", "No Live Demo", -2)

            # No Business Impact (lack of metrics, %, $, or impact verbs)
            impact_pattern = re.compile(r"(\d+%|\$\d+|improved|optimized|saved|reduced|increased|led|spearheaded|delivered)", re.IGNORECASE)
            no_impact = any(not impact_pattern.search(proj.description or "") for proj in projects)
            if no_impact:
                add_penalty("Projects", "No Business Impact", -5)

        # ----------------------------------------------------
        # 5. EXPERIENCE PENALTIES
        # ----------------------------------------------------
        if not experiences:
            if "student" in prof_lower:
                pass
            else:
                add_penalty("Experience", "No Experience", -12)
        else:
            # Timeline Conflict
            timeline_conflict = False
            for i, exp1 in enumerate(experiences):
                start1 = exp1.start_date
                end1 = exp1.end_date or date.today()
                
                # basic integrity check
                if start1 > end1:
                    timeline_conflict = True
                    break
                    
                # overlap check
                for j, exp2 in enumerate(experiences):
                    if i != j:
                        start2 = exp2.start_date
                        end2 = exp2.end_date or date.today()
                        # check overlap: if exp1 starts inside exp2
                        if start2 < start1 < end2 and start2 < end1 < end2:
                            # if it's completely inside, could be concurrent but let's count timeline conflict if dates are identical
                            if start1 == start2 and end1 == end2:
                                timeline_conflict = True
                                break
            if timeline_conflict:
                add_penalty("Experience", "Timeline Conflict", -8)

            # Missing Company
            if any(not (exp.company or "").strip() for exp in experiences):
                add_penalty("Experience", "Missing Company", -3)

            # Missing Responsibilities
            if any(not (exp.description or "").strip() for exp in experiences):
                add_penalty("Experience", "Missing Responsibilities", -5)

            # No achievements
            achievement_pattern = re.compile(r"(\d+%|\$\d+|achieved|accomplished|led|managed|delivered|optimized|saved)", re.IGNORECASE)
            no_ach = any(not achievement_pattern.search(exp.description or "") for exp in experiences)
            if no_ach:
                add_penalty("Experience", "No Achievements", -4)

        # ----------------------------------------------------
        # 6. EDUCATION PENALTIES
        # ----------------------------------------------------
        if educations:
            if any(not (edu.degree or "").strip() for edu in educations):
                add_penalty("Education", "Missing Degree", -8)
            if any(not (edu.institute or "").strip() for edu in educations):
                add_penalty("Education", "Missing University", -5)
            if any(edu.end_date is None for edu in educations):
                add_penalty("Education", "Missing Graduation Year", -3)

        # ----------------------------------------------------
        # 7. CERTIFICATION PENALTIES
        # ----------------------------------------------------
        if not certifications:
            if "cloud engineer" in prof_lower or "devops" in prof_lower:
                add_penalty("Certifications", "No Certifications", -8)
            elif "ai engineer" in prof_lower or "machine learning" in prof_lower:
                add_penalty("Certifications", "No Certifications", -5)
            elif "teacher" in prof_lower:
                add_penalty("Certifications", "No Certifications", -2)
            else:
                add_penalty("Certifications", "No Certifications", -2)

        # ----------------------------------------------------
        # 8. FORMATTING PENALTIES
        # ----------------------------------------------------
        # Check for Tables
        if "|" in extracted_text or "\t\t" in extracted_text or " +---" in extracted_text:
            add_penalty("Formatting", "Tables", -5)

        # Check for Icons
        # Look for typical emoji ranges or unicode symbols
        emoji_pattern = re.compile(r"[\u2600-\u27BF\U0001f300-\U0001f64f\U0001f680-\U0001f6c0✉☎📞📂🔗🎓💼]")
        if emoji_pattern.search(extracted_text) or emoji_pattern.search(summary_text):
            add_penalty("Formatting", "Icons", -2)

        # Check for Images
        if any(term in extracted_text.lower() for term in ["image:", "logo:", "[image]", "[logo]", "graphic:"]):
            add_penalty("Formatting", "Images", -3)

        # Check for Unreadable Fonts
        if "garbled" in extracted_text.lower() or "cid:" in extracted_text:
            add_penalty("Formatting", "Unreadable Fonts", -5)

        # Too Many Columns
        if len(re.findall(r"\s{4,}", extracted_text)) > 50:
            add_penalty("Formatting", "Too Many Columns", -4)

        # ----------------------------------------------------
        # 9. GRAMMAR PENALTIES
        # ----------------------------------------------------
        # Spelling Errors: -1 each (capped at -10)
        spelling_errors = 0
        for typo in COMMON_TYPOS:
            spelling_errors += len(re.findall(r'\b' + re.escape(typo) + r'\b', full_text_lower))
        if spelling_errors > 0:
            add_penalty("Grammar", f"Spelling Errors ({spelling_errors})", -min(10, spelling_errors))

        # Grammar Errors (Passive voice examples): -1 each (capped at -10)
        passive_matches = re.findall(r'\b(was|were|been|being|is|are|am|be)\b\s+([a-zA-Z]+ed|done|made|built|run|written|held)\b', full_text_lower)
        if len(passive_matches) > 0:
            add_penalty("Grammar", f"Grammar/Passive Errors ({len(passive_matches)})", -min(10, len(passive_matches)))

        # Repeated Words
        repeated_word_pattern = re.compile(r"\b([a-zA-Z]+)\s+\1\b", re.IGNORECASE)
        if repeated_word_pattern.search(full_text):
            add_penalty("Grammar", "Repeated Words", -2)

        # Compute raw total penalties
        raw_total = sum(p["points"] for p in penalties)
        
        # Clamp to max negative deduction of -30
        clamped_total = max(-30, raw_total)

        return clamped_total, penalties
