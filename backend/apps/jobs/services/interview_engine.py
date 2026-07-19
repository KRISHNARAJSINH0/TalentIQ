import re
import logging

logger = logging.getLogger(__name__)

class InterviewEngine:
    """
    Evaluates interview readiness on key areas (Technical, Projects, Experience, Leadership, Communication).
    """
    @staticmethod
    def evaluate_readiness(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        skills = [s.get("skill_name", "").lower() for s in profile_data.get("skills", [])]
        experiences = profile_data.get("experiences", [])
        projects = profile_data.get("projects", [])
        
        # 1. Technical Skills score (0-100)
        # Check overlaps with JD
        tech_matches = 0
        all_text = jd_lower
        for s in skills:
            if s in all_text:
                tech_matches += 1
        tech_score = min(100, 30 + tech_matches * 10)
        if len(skills) > 12:
            tech_score = min(100, tech_score + 10)
            
        # 2. Projects score (0-100)
        # Check project count and live proofs
        proj_score = min(100, 40 + len(projects) * 15)
        for p in projects:
            if p.get("live_url"):
                proj_score = min(100, proj_score + 10)
            if p.get("github_url"):
                proj_score = min(100, proj_score + 5)
                
        # 3. Experience score (0-100)
        # Years of experience check
        exp_score = min(100, 40 + len(experiences) * 15)
        
        # 4. Leadership score (0-100)
        leadership_score = 40
        lead_words = ["managed", "spearheaded", "mentored", "lead", "leadership", "coordinated", "director"]
        combined_text = " ".join([exp.get("description", "").lower() for exp in experiences])
        for lw in lead_words:
            if lw in combined_text:
                leadership_score = min(100, leadership_score + 15)
                
        # 5. Communication score (0-100)
        comm_score = 50
        comm_words = ["presented", "authored", "wrote", "collaborated", "negotiated", "facilitated", "spoke", "communication", "team"]
        for cw in comm_words:
            if cw in combined_text or cw in (profile_data.get("summary") or "").lower():
                comm_score = min(100, comm_score + 10)
                
        # Overall readiness category
        avg_score = (tech_score + proj_score + exp_score + leadership_score + comm_score) / 5
        
        if avg_score >= 90:
            status = "Elite Candidate"
        elif avg_score >= 80:
            status = "Highly Competitive"
        elif avg_score >= 70:
            status = "Interview Ready"
        elif avg_score >= 50:
            status = "Needs Improvement"
        else:
            status = "Not Ready"
            
        # Build feedback
        feedback = []
        if tech_score < 75:
            feedback.append("Strengthen core technical stack by aligning skills with key JD requirements.")
        else:
            feedback.append("Technical competency aligned. Ready for algorithmic and systems rounds.")
            
        if proj_score < 70:
            feedback.append("Add live demonstration links or deploy code repos for key projects.")
        if leadership_score < 60:
            feedback.append("Highlight initiatives and mentorship details under experience entries to boost leadership ratings.")
            
        return {
            "technical_score": tech_score,
            "projects_score": proj_score,
            "experience_score": exp_score,
            "leadership_score": leadership_score,
            "communication_score": comm_score,
            "overall_readiness": status,
            "feedback": feedback
        }
