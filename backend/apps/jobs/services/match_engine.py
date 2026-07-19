import re
import logging

logger = logging.getLogger(__name__)

# Predefined keyword maps for categorizations
SOFT_SKILLS = ["communication", "teamwork", "leadership", "mentoring", "collaboration", "problem solving", "critical thinking", "agile", "organization"]
LEADERSHIP_KEYWORDS = ["lead", "manage", "mentor", "spearhead", "director", "head", "architect", "ownership", "strategic"]
ACHIEVEMENT_KEYWORDS = ["achieved", "won", "first place", "award", "percent", "saved", "impact", "delivered", "successful"]

class MatchEngine:
    """
    Evaluates 16 detailed match categories between candidate profile and target job description.
    """
    @staticmethod
    def calculate_categories(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        
        # Pull candidate data
        summary = (profile_data.get("summary") or "").lower()
        skills = [s.get("skill_name", "").lower() for s in profile_data.get("skills", [])]
        experiences = profile_data.get("experiences", [])
        projects = profile_data.get("projects", [])
        educations = profile_data.get("educations", [])
        certifications = profile_data.get("certifications", [])
        
        github = profile_data.get("github") or ""
        linkedin = profile_data.get("linkedin") or ""
        portfolio = profile_data.get("portfolio_url") or ""

        # Helper checks
        candidate_designations = [exp.get("designation", "").lower() for exp in experiences]
        
        # Calculate text overlaps to make scores unique to the JD content
        jd_words = set(re.findall(r'\b\w{3,15}\b', jd_lower))
        profile_text = (summary + " " + " ".join(skills) + " " + 
                        " ".join([exp.get("description", "").lower() for exp in experiences]) + " " + 
                        " ".join([p.get("description", "").lower() for p in projects]))
        profile_words = set(re.findall(r'\b\w{3,15}\b', profile_text.lower()))
        overlap_count = len(jd_words.intersection(profile_words))
        
        # 1. Role Match (0-100)
        role_score = 40 + min(20, overlap_count * 2)
        words_in_jd = set(re.findall(r'\b\w{3,15}\b', jd_lower))
        for d in candidate_designations:
            d_words = set(re.findall(r'\b\w{3,15}\b', d))
            if d_words.intersection(words_in_jd):
                role_score = min(100, role_score + 25)
        if any("engineer" in jd_lower and "engineer" in d for d in candidate_designations):
            role_score = min(100, role_score + 20)
        role_score = min(100, max(20, role_score))

        # 2. Skill Match (0-100)
        matched_skills = [s for s in skills if s in jd_lower]
        skill_score = 30 + min(20, overlap_count)
        if skills:
            skill_score = int((len(matched_skills) / max(1, len(skills))) * 80) + 20
        skill_score = min(100, max(20, skill_score))

        # 3. Keyword Match (0-100)
        kw_score = 35 + min(25, overlap_count * 2)

        # 4. Experience Match (0-100)
        exp_score = min(100, 30 + len(experiences) * 15 + min(20, overlap_count))

        # 5. Education Match (0-100)
        edu_score = 45 + min(15, len(jd_words) % 15)
        for edu in educations:
            deg = (edu.get("degree") or "").lower()
            field = (edu.get("field_of_study") or "").lower()
            if "computer" in field or "software" in field or "engineering" in field or "science" in field:
                edu_score = min(100, edu_score + 25)
            if "mbbs" in deg or "medical" in field or "md" in deg:
                if "doctor" in jd_lower:
                    edu_score = 100
        edu_score = min(100, max(20, edu_score))

        # 6. Certification Match (0-100)
        cert_score = 30 + min(10, len(jd_words) % 10)
        if certifications:
            cert_score = 70
            for cert in certifications:
                c_name = (cert.get("certificate_name") or "").lower()
                if c_name in jd_lower or any(p in jd_lower for p in c_name.split()):
                    cert_score = 100
                    break

        # 7. Industry Match (0-100)
        ind_score = 50 + min(20, overlap_count * 2)
        ind_words = ["tech", "software", "healthcare", "education", "finance", "legal", "construction", "mechanical"]
        matched_ind = [w for w in ind_words if w in jd_lower and any(w in (exp.get("description") or "").lower() for exp in experiences)]
        if matched_ind:
            ind_score = min(100, ind_score + 20)

        # 8. Responsibility Match (0-100)
        resp_score = 40 + min(20, overlap_count)
        resp_verbs = ["designed", "built", "implemented", "managed", "coded", "tested", "developed"]
        matched_verbs = [v for v in resp_verbs if v in jd_lower and any(v in (exp.get("description") or "").lower() for exp in experiences)]
        resp_score = min(100, resp_score + len(matched_verbs) * 10)

        # 9. Technology Match (0-100)
        tech_words = ["python", "javascript", "docker", "kubernetes", "aws", "react", "django", "sql", "java", "typescript"]
        matched_tech = [t for t in tech_words if t in jd_lower and t in skills]
        tech_score = 30 + min(20, overlap_count * 2) + len(matched_tech) * 10

        # 10. Soft Skill Match (0-100)
        matched_soft = [s for s in SOFT_SKILLS if s in jd_lower and (s in skills or s in summary)]
        soft_score = 50 + min(15, overlap_count) + len(matched_soft) * 10

        # 11. Leadership Match (0-100)
        lead_score = 35 + min(15, overlap_count)
        matched_lead = [l for l in LEADERSHIP_KEYWORDS if l in jd_lower and any(l in (exp.get("description") or "").lower() for exp in experiences)]
        lead_score = min(100, lead_score + len(matched_lead) * 15)

        # 12. Project Match (0-100)
        proj_score = min(100, 40 + len(projects) * 15 + min(20, overlap_count))

        # 13. Achievement Match (0-100)
        ach_score = 45 + min(15, len(jd_words) % 15)
        matched_ach = [a for a in ACHIEVEMENT_KEYWORDS if any(a in (exp.get("description") or "").lower() for exp in experiences)]
        ach_score = min(100, ach_score + len(matched_ach) * 15)

        # 14. Portfolio Match (0-100)
        port_score = 100 if portfolio else 0

        # 15. GitHub Match (0-100)
        git_score = 100 if github else 0

        # 16. LinkedIn Match (0-100)
        li_score = 100 if linkedin else 0

        return {
            "role_match": min(100, role_score),
            "skills_match": min(100, skill_score),
            "keyword_match": min(100, kw_score),
            "experience_match": min(100, exp_score),
            "education_match": min(100, edu_score),
            "certification_match": min(100, cert_score),
            "industry_match": min(100, ind_score),
            "responsibility_match": min(100, resp_score),
            "technology_match": min(100, tech_score),
            "soft_skill_match": min(100, soft_score),
            "leadership_match": min(100, lead_score),
            "project_match": min(100, proj_score),
            "achievement_match": min(100, ach_score),
            "portfolio_match": port_score,
            "github_match": git_score,
            "linkedin_match": li_score
        }
