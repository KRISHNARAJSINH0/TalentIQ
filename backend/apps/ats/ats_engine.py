import logging
import re
import time
from datetime import datetime
from django.utils import timezone

# pyrefly: ignore [missing-import]
from apps.profiles.models import Profile, Skill, Education, Experience, Project, Certification
# pyrefly: ignore [missing-import]
from apps.resumes.models import Resume, ConsistencyReport
# pyrefly: ignore [missing-import]
from apps.resumes.services.consistency_checker import ConsistencyChecker 
# pyrefly: ignore [missing-import]
from apps.reputation.models import ResumeReputation

# pyrefly: ignore [missing-import]
from .profession_engine import ProfessionEngine
from .weight_engine import WeightEngine
from .keyword_engine import KeywordEngine
from .achievement_engine import AchievementEngine
from .format_engine import FormatEngine
from .grammar_engine import GrammarEngine
from .benchmark_engine import BenchmarkEngine
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

class ATSEngine:
    """
    Central orchestrator for the ATS Intelligence Engine.
    Evaluates resumes in Generic or Job-Specific mode.
    """

    @staticmethod
    def run_ats_analysis(profile: Profile, resume: Resume, job_description: str = None) -> dict:
        start_time = time.time()

        # 1. Fetch related data
        skills = list(profile.skills.all())
        educations = list(profile.educations.all())
        experiences = list(profile.experiences.all())
        projects = list(profile.projects.all())
        certifications = list(profile.certifications.all())

        related_data = {
            "skills": skills,
            "educations": educations,
            "experiences": experiences,
            "projects": projects,
            "certifications": certifications
        }

        # Combine profile texts
        skills_text = ", ".join([s.skill_name for s in skills])
        exp_text = " ".join([f"{e.designation} at {e.company}: {e.description or ''}" for e in experiences])
        proj_text = " ".join([f"{p.project_name} using {p.technologies}: {p.description or ''}" for p in projects])
        profile_text = f"{profile.summary or ''} {skills_text} {exp_text} {proj_text}"

        # 2. Profession / Role Detection
        profile_data_dict = {
            "headline": profile.headline or "",
            "summary": profile.summary or "",
            "skills": [{"skill_name": s.skill_name} for s in skills],
            "experiences": [{"designation": e.designation, "company": e.company, "description": e.description or ""} for e in experiences],
            "projects": [{"project_name": p.project_name, "technologies": p.technologies, "description": p.description or ""} for p in projects]
        }
        profession = ProfessionEngine.detect_profession(profile_data_dict)

        # 3. Load Profession-specific Weights
        weights = WeightEngine.get_weights(profession)

        # 4. Keyword Analysis
        skills_list = [s.skill_name for s in skills]
        keyword_results = KeywordEngine.analyze_keywords(profile_text, profession, skills_list)

        # 5. Achievement & Strong Verbs Analysis
        achievement_results = AchievementEngine.analyze_achievements(profile_text)

        # 6. Formatting Analysis
        formatting_results = FormatEngine.analyze_formatting(profile, related_data)

        # 7. Readability & Grammar Analysis
        grammar_results = GrammarEngine.analyze_grammar(profile, related_data)

        # 8. Consistency Score
        consistency_checker = ConsistencyChecker()
        consistency_res = consistency_checker.check_consistency(profile_data_dict)
        consistency_score = float(consistency_res.get("consistency_score", 70.0))

        # 9. Individual Subscores calculations (all 25)
        subscores = {}
        subscores["structure"] = float(formatting_results["structure_score"])
        subscores["compatibility"] = float(formatting_results["compatibility_score"])
        
        # contact
        contact_points = 30.0
        if profile.user.email: contact_points += 30.0
        if profile.user.phone: contact_points += 20.0
        if profile.address: contact_points += 20.0
        subscores["contact"] = contact_points

        # summary
        summary_words = len((profile.summary or "").split())
        if summary_words == 0:
            summary_score = 0.0
        elif summary_words < 30:
            summary_score = 60.0
        elif summary_words > 200:
            summary_score = 70.0
        else:
            summary_score = 100.0
        subscores["summary"] = summary_score

        subscores["skills"] = min(100.0, len(skills) * 10.0)
        subscores["skill_relevance"] = float(keyword_results["skill_relevance_score"])
        subscores["experience"] = min(100.0, len(experiences) * 35.0)

        # experience quality
        exp_qual = 50.0
        if len(achievement_results["strong_verbs_detected"]) >= 4:
            exp_qual += 25.0
        if len(achievement_results["quantified_metrics_detected"]) >= 2:
            exp_qual += 25.0
        subscores["experience_quality"] = min(100.0, exp_qual)

        subscores["projects"] = min(100.0, len(projects) * 35.0)
        
        # project quality
        proj_qual = 0.0
        if projects:
            proj_qual = 70.0
            if any(p.github_url or p.live_url for p in projects):
                proj_qual += 30.0
        subscores["project_quality"] = proj_qual

        subscores["education"] = min(100.0, len(educations) * 50.0)
        subscores["certifications"] = min(100.0, len(certifications) * 35.0)
        subscores["achievements"] = float(achievement_results["achievements_score"])

        # leadership
        has_leadership = any(any(w in (exp.description or "").lower() or w in (exp.designation or "").lower() for w in ["led", "managed", "head", "team", "coordinator", "lead"]) for exp in experiences)
        subscores["leadership"] = 100.0 if has_leadership else 50.0

        subscores["keywords"] = float(keyword_results["keywords_score"])
        subscores["formatting"] = float(formatting_results["formatting_score"])
        subscores["readability"] = float(grammar_results["readability_score"])
        subscores["grammar"] = float(grammar_results["grammar_score"])
        subscores["action_verbs"] = float(achievement_results["action_verbs_score"])
        subscores["quantified_achievements"] = float(achievement_results["quantified_achievements_score"])

        subscores["portfolio"] = 100.0 if profile.portfolio_url else 0.0
        subscores["linkedin"] = 100.0 if profile.linkedin else 0.0
        subscores["github"] = 100.0 if profile.github else 0.0

        # progression
        subscores["progression"] = 90.0 if len(experiences) >= 2 else (60.0 if experiences else 40.0)
        subscores["consistency"] = consistency_score

        # Calculate base overall score using weights
        overall_score = 0.0
        for sub, weight in weights.items():
            overall_score += subscores.get(sub, 50.0) * weight
        overall_score = round(max(0.0, min(100.0, overall_score)))

        # 10. Job-Specific Mode
        job_specific_results = {}
        if job_description:
            # Simple keyword matching against job description
            jd_clean = job_description.lower()
            
            # Find job skills
            matched_jd_skills = []
            for s in skills:
                if s.skill_name.lower() in jd_clean:
                    matched_jd_skills.append(s.skill_name)
            
            skill_match_pct = (len(matched_jd_skills) / max(1, len(skills))) * 100.0
            
            # Check experience requirements (e.g. looking for "years", "\d+\s*years")
            exp_matches = re.findall(r'(\d+)\s*(?:\+)?\s*(?:year|yr)s?', jd_clean)
            req_years = int(exp_matches[0]) if exp_matches else 0
            
            # Candidate experience calculation
            total_days = 0
            for exp in experiences:
                start = exp.start_date
                end = exp.end_date or datetime.today().date()
                total_days += (end - start).days
            candidate_years = total_days / 365.25
            
            if req_years == 0 or candidate_years >= req_years:
                experience_match_pct = 100.0
            else:
                experience_match_pct = (candidate_years / req_years) * 100.0
            
            # Overall job match score
            job_match_score = round((skill_match_pct * 0.5) + (experience_match_pct * 0.3) + (overall_score * 0.2))
            
            job_specific_results = {
                "job_match": job_match_score,
                "keyword_match": round(skill_match_pct, 2), # Using skill match as keyword match proxy
                "skill_match": round(skill_match_pct, 2),
                "experience_match": round(experience_match_pct, 2),
                "education_match": 100.0 if educations else 50.0,
                "certification_match": 100.0 if certifications else 50.0,
                "industry_match": 100.0 if profession in jd_clean.title() else 60.0,
                "estimated_ats_job": round(job_match_score)
            }
            
            # Adjust overall score to reflect the job match
            overall_score = round((overall_score * 0.4) + (job_match_score * 0.6))

        subscores["overall"] = overall_score

        # 11. Strengths, Weaknesses and Recommendations
        strengths = []
        weaknesses = []

        if subscores["skills"] >= 80: strengths.append("High skills density matching core keywords.")
        else: weaknesses.append("Add more specific tools and technical skills to your profile.")

        if subscores["projects"] >= 70: strengths.append("Solid project accomplishments with link proofs.")
        else: weaknesses.append("Provide public repository URLs for your key projects.")

        if subscores["experience_quality"] >= 75: strengths.append("Experience entries feature high-impact action verbs.")
        else: weaknesses.append("Focus your work experience statements on quantified achievements.")

        # Ensure we always return at least some strengths/weaknesses
        if not strengths: strengths.append("Basic resume sections are present.")
        if not weaknesses: weaknesses.append("Consider listing a direct online portfolio website.")

        recommendations = RecommendationEngine.generate_recommendations(
            profile, related_data, keyword_results, grammar_results, formatting_results
        )

        # 12. Parse quality & confidence (calculated from self-healing metrics or default values)
        parsing_quality = 95
        confidence = 90
        # If reputation exists, we can use it, else default
        try:
            rep = ResumeReputation.objects.filter(resume=resume).first()
            if rep:
                confidence = int(rep.score)
        except Exception:
            pass

        job_ready = overall_score >= 80

        processing_time = round(time.time() - start_time, 4)

        report_payload = {
            "overall_score": overall_score,
            "confidence": confidence,
            "job_ready": job_ready,
            "parsing_quality": parsing_quality,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "subscores": subscores,
            "metadata": {
                "profession": profession,
                "weights": weights,
                "processing_time": processing_time,
                "timestamp": timezone.now().isoformat(),
                "job_specific_results": job_specific_results,
                "keyword_density": keyword_results.get("keyword_density_pct", 0),
                "spelling_issues": grammar_results.get("spelling_errors", [])
            }
        }

        return report_payload
