import logging

logger = logging.getLogger(__name__)


class RolePredictor:
    """
    Predicts/infers the candidate's core professional role based on their profile data (designation, headline, skills).
    """
    @staticmethod
    def predict_role(profile_data: dict, gemini_response: str = None) -> str:
        # If Gemini responded with a role, clean and use it
        if gemini_response:
            role = gemini_response.strip()
            if role:
                return role

        import re

        # Prioritize actual designation from the most recent experience entry
        role_raw = ""
        experiences = profile_data.get("experiences", [])
        if experiences:
            # Sort experiences by end_date (or start_date) to find the most recent one
            # Experiences are usually pre-sorted in reverse chronological order, 
            # but we will look for the first non-empty designation.
            for exp in experiences:
                desig = exp.get("designation", "").strip()
                if desig:
                    role_raw = desig
                    break

        # Fall back to headline if no experiences
        if not role_raw:
            headline = profile_data.get("headline", "").strip()
            if headline:
                role_raw = headline

        # Clean the role string to extract the core title (e.g. "Senior React Developer Intern" -> "React Developer")
        if role_raw:
            role_clean = role_raw.lower()
            # Remove noise words and common seniority prefixes/suffixes
            noise_words = [
                r"\bsenior\b", r"\bjunior\b", r"\bassociate\b", r"\blead\b", 
                r"\bprincipal\b", r"\bstaff\b", r"\bintern\b", r"\btrainee\b", 
                r"\bii\b", r"\biii\b", r"\biv\b", r"\bv\b", r"\bcontractor\b", 
                r"\bfreelance\b", r"\bfreelancer\b", r"\bco-op\b"
            ]
            for term in noise_words:
                role_clean = re.sub(term, "", role_clean)
            
            # Clean up double spaces and special characters
            role_clean = re.sub(r"[^\w\s\-\/\+]", "", role_clean)
            role_clean = re.sub(r"\s+", " ", role_clean).strip()
            role_clean = role_clean.title()
            
            # Normalize common designations to standard industry roles
            normalizer_map = {
                "Backend Dev": "Backend Engineer",
                "Backend Developer": "Backend Engineer",
                "Software Dev": "Software Engineer",
                "Software Developer": "Software Engineer",
                "Ai Researcher": "ML Engineer",
                "Ml Researcher": "ML Engineer",
                "Ai Engineer": "AI Engineer",
                "Civil Design Manager": "Civil Engineer",
                "General Practitioner": "Doctor",
                "High School Instructor": "Teacher",
                "Corporate Counsel": "Lawyer",
                "Product Designer": "UI UX Designer",
                "Business Analyst": "Data Analyst",
                "R D Scientist": "Researcher",
                "Rd Scientist": "Researcher",
                "R&D Scientist": "Researcher",
                "Growth Marketer": "Marketing Manager",
                "Hr Generalist": "HR Specialist",
                "Chartered Accountant": "Accountant",
                "Undergrad": "Student",
                "Undergrad Intern": "Student",
                "Independent Consultant": "Freelancer",
            }
            if role_clean in normalizer_map:
                return normalizer_map[role_clean]

            if role_clean:
                return role_clean

        # Fallback dynamic rule-based matching based on skills & designation
        skills = [s.get("skill_name", "").lower() for s in profile_data.get("skills", [])]
        headline_lower = (profile_data.get("headline") or "").lower()
        designations = [exp.get("designation", "").lower() for exp in experiences]

        all_text_context = " ".join(skills) + " " + headline_lower + " " + " ".join(designations)

        # 1. Doctor
        if any(w in all_text_context for w in ["doctor", "physician", "clinical", "mbbs", "md", "patient care", "diagnosis"]):
            return "Doctor"
        
        # 2. Teacher
        if any(w in all_text_context for w in ["teacher", "professor", "pedagogy", "curriculum", "lesson planning", "classroom"]):
            return "Teacher"
        
        # 3. Accountant
        if any(w in all_text_context for w in ["accountant", "cpa", "bookkeeping", "tax", "audit", "accounting", "quickbooks"]):
            return "Accountant"

        # 4. Lawyer
        if any(w in all_text_context for w in ["lawyer", "attorney", "legal", "counsel", "compliance", "litigation", "contract drafting"]):
            return "Lawyer"
        
        # 5. Civil Engineer
        if any(w in all_text_context for w in ["civil engineer", "structural", "autocad", "revit", "construction", "civil 3d"]):
            return "Civil Engineer"
            
        # 6. ML / AI Engineer
        if any(w in all_text_context for w in ["pytorch", "tensorflow", "scikit", "keras", "deep learning", "machine learning", "ml engineer", "ai engineer", "nlp"]):
            return "ML Engineer"
            
        # 7. Researcher
        if any(w in all_text_context for w in ["researcher", "scientific", "experimental design", "academia", "r&d"]):
            return "Researcher"

        # 8. Designer
        if any(w in all_text_context for w in ["figma", "illustrator", "photoshop", "ui ux", "design", "wireframing", "product designer"]):
            return "UI UX Designer"
            
        # 9. Data Analyst
        if any(w in all_text_context for w in ["powerbi", "excel", "sql", "tableau", "data analyst", "analytics", "data visualization"]):
            return "Data Analyst"
            
        # 10. Marketing
        if any(w in all_text_context for w in ["marketing", "seo", "brand", "growth hack", "content strategy", "copywriting"]):
            return "Marketing Manager"
            
        # 11. HR
        if any(w in all_text_context for w in ["hr", "human resources", "recruiting", "talent acquisition", "onboarding", "people operations"]):
            return "HR Specialist"

        # 12. Student
        if any(w in all_text_context for w in ["student", "intern", "university", "graduate assistant"]):
            return "Student"

        # 13. Freelancer
        if any(w in all_text_context for w in ["freelancer", "independent consultant", "contractor", "solopreneur"]):
            return "Freelancer"

        # 14. Default to Backend Engineer (or Software Engineer) if technical skills found
        if any(w in all_text_context for w in ["python", "django", "fastapi", "postgres", "docker", "java", "node", "backend"]):
            return "Backend Engineer"

        # General Default
        return "Software Engineer"
