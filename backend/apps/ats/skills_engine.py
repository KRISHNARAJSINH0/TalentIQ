import re

class SkillsEngine:
    """
    Evaluates the quality, depth, alignment, and distribution of the skills section.
    """

    @staticmethod
    def analyze(profile, resume, profile_data: dict) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Get list of candidate skills
        candidate_skills = []
        if hasattr(profile, 'skills') and profile.skills:
            # Check if skills is a relation or queryset
            if hasattr(profile.skills, 'all'):
                candidate_skills = [getattr(s, 'skill_name', getattr(s, 'name', '')) for s in profile.skills.all()]
            elif isinstance(profile.skills, list):
                candidate_skills = profile.skills
            else:
                candidate_skills = []


        if not candidate_skills:
            return {
                "category": "Skills",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No skills registered on your profile."],
                "recommendations": ["Add relevant technical and soft skills matching your desired profession."],
                "confidence": 90
            }

        candidate_skills_lower = [s.lower().strip() for s in candidate_skills]

        # Get target skills from ProfessionProfile configuration
        req_skills = [s.lower().strip() for s in profile_data.get("required_skills", [])]
        rec_skills = [s.lower().strip() for s in profile_data.get("recommended_skills", [])]
        soft_skills_target = [s.lower().strip() for s in profile_data.get("soft_skills", [])]

        # 1. Required Skills Match
        matched_req = [s for s in req_skills if s in candidate_skills_lower]
        if req_skills:
            req_ratio = len(matched_req) / len(req_skills)
            if req_ratio < 0.5:
                score -= 30.0
                weaknesses.append(f"Missing critical required skills for {profile_data.get('role')}.")
                missing_req = [s for s in req_skills if s not in candidate_skills_lower]
                recommendations.append(f"Add required core skills: {', '.join(missing_req[:4])}.")
            elif req_ratio < 0.9:
                score -= 10.0
                missing_req = [s for s in req_skills if s not in candidate_skills_lower]
                recommendations.append(f"Strengthen alignment by adding: {', '.join(missing_req[:3])}.")
            else:
                strengths.append("All key required role skills are present.")
        else:
            # If profile has no required skills, fallback to positive check on total count
            if len(candidate_skills) < 5:
                score -= 20.0
                weaknesses.append("Very few skills listed.")
                recommendations.append("List at least 8-12 skills to demonstrate breadth of expertise.")

        # 2. Recommended Skills Match
        matched_rec = [s for s in rec_skills if s in candidate_skills_lower]
        if rec_skills:
            rec_ratio = len(matched_rec) / len(rec_skills)
            if rec_ratio >= 0.5:
                strengths.append("Good coverage of recommended advanced skills.")
            else:
                score -= 10.0
                missing_rec = [s for s in rec_skills if s not in candidate_skills_lower]
                recommendations.append(f"Enhance competitiveness by learning/listing: {', '.join(missing_rec[:3])}.")

        # 3. Soft Skills & Diversity
        matched_soft = [s for s in soft_skills_target if s in candidate_skills_lower]
        soft_ratio = len(matched_soft) / max(1, len(soft_skills_target))
        if soft_ratio > 0:
            strengths.append("Includes critical soft skills matching the role.")
        
        # Check overall soft skill ratio (should not be >50% of all skills, nor 0%)
        # Let's count soft skills manually using common soft skill indicator terms
        generic_soft_indicators = ["communication", "leadership", "teamwork", "problem solving", "time management", "adaptability", "critical thinking"]
        soft_count = sum(1 for s in candidate_skills_lower if any(x in s for x in generic_soft_indicators + soft_skills_target))
        
        if len(candidate_skills) > 0:
            soft_percentage = (soft_count / len(candidate_skills)) * 100.0
            if soft_percentage > 50.0:
                score -= 15.0
                weaknesses.append("Skills section is too soft-skill heavy.")
                recommendations.append("Shift focus towards hard technical skills rather than over-indexing on soft skills.")
            elif soft_percentage == 0:
                score -= 5.0
                weaknesses.append("No soft skills or interpersonal competencies listed.")
                recommendations.append("Add 2-3 key soft skills (e.g., Team Collaboration, Problem Solving) for balance.")

        # 4. Trivial / Generic Skills penalty (e.g. MS Office on senior software engineer resumes)
        trivial_skills = ["microsoft office", "ms office", "word", "powerpoint", "windows", "internet", "email", "typing"]
        matched_trivial = [s for s in trivial_skills if s in candidate_skills_lower]
        
        # Only penalize if they are high-tech/professional profiles (e.g., Software Engineers, AI Engineers)
        tech_roles = ["software engineer", "backend developer", "frontend developer", "full stack developer", "ai engineer", "machine learning engineer", "data scientist"]
        role_lower = profile_data.get("role", "").lower()
        if any(tr in role_lower for tr in tech_roles) and matched_trivial:
            score -= len(matched_trivial) * 5.0
            weaknesses.append(f"Contains generic/trivial skills: {', '.join(matched_trivial)}")
            recommendations.append("Remove basic skills like MS Office/Word to keep the resume highly professional and technical.")

        # 5. Duplicate Skills
        unique_skills = set(candidate_skills_lower)
        if len(unique_skills) < len(candidate_skills):
            score -= 10.0
            weaknesses.append("Duplicate or highly redundant skills detected.")
            recommendations.append("De-duplicate your skills section to make it concise and clean.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Skills",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
