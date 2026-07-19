import logging
import re
from datetime import datetime

from apps.ats.weight_manager import WeightManager, RULE_CATEGORIES
from apps.ats.contact_engine import ContactEngine
from apps.ats.summary_engine import SummaryEngine
from apps.ats.skills_engine import SkillsEngine
from apps.ats.experience_engine import ExperienceEngine
from apps.ats.projects_engine import ProjectsEngine
from apps.ats.education_engine import EducationEngine
from apps.ats.certification_engine import CertificationEngine
from apps.ats.achievement_engine import AchievementEngine
from apps.ats.keyword_engine import KeywordEngine
from apps.ats.grammar_engine import GrammarEngine
from apps.ats.format_engine import FormatEngine
from apps.ats.career_engine import CareerEngine

# Try importing related models to evaluate ATS Compatibility and Consistency
try:
    from apps.resumes.models import ConfidenceScore, SemanticValidation, RecoveryLog, ConsistencyReport
except ImportError:
    ConfidenceScore = None
    SemanticValidation = None
    RecoveryLog = None
    ConsistencyReport = None

logger = logging.getLogger(__name__)

class CategoryManager:
    """
    Central orchestrator for the 20-category Quality-Based ATS Scoring Engine.
    Executes sub-engines, retrieves profile-specific weights, calculates
    contributions, and computes the overall quality score.
    """

    @classmethod
    def evaluate_resume(cls, profile, resume, profile_data: dict) -> dict:
        """
        Runs quality evaluations across all 20 categories.
        Returns a structured dictionary with breakdowns, subscores, and overall ATS score.
        """
        # 1. Fetch category weights based on the Profession Profile
        weights = WeightManager.get_category_weights(profile_data.get("weights", {}))

        # 2. Run all sub-engines
        results = {}

        # 1. Contact Information
        results["Contact Information"] = ContactEngine.analyze(profile, resume)

        # 2. Professional Summary
        results["Professional Summary"] = SummaryEngine.analyze(profile, resume)

        # 3. Skills
        results["Skills"] = SkillsEngine.analyze(profile, resume, profile_data)

        # 4. Experience
        results["Experience"] = ExperienceEngine.analyze(profile, resume)

        # 5. Projects
        results["Projects"] = ProjectsEngine.analyze(profile, resume)

        # 6. Education
        results["Education"] = EducationEngine.analyze(profile, resume, profile_data)

        # 7. Certifications
        results["Certifications"] = CertificationEngine.analyze(profile, resume, profile_data)

        # 8. Achievements
        results["Achievements"] = AchievementEngine.analyze(profile, resume)

        # 9. Formatting
        results["Formatting"] = FormatEngine.analyze(profile, resume)

        # 10. Grammar
        results["Grammar"] = GrammarEngine.analyze_grammar(profile, resume)

        # 11. Keywords
        results["Keywords"] = KeywordEngine.analyze(profile, resume, profile_data)

        # 12. Readability
        results["Readability"] = GrammarEngine.analyze_readability(profile, resume)

        # 13. ATS Compatibility
        results["ATS Compatibility"] = cls._evaluate_ats_compatibility(resume)

        # 14. GitHub
        results["GitHub"] = cls._evaluate_github(profile)

        # 15. Portfolio
        results["Portfolio"] = cls._evaluate_portfolio(profile)

        # 16. LinkedIn
        results["LinkedIn"] = cls._evaluate_linkedin(profile)

        # 17. Leadership
        results["Leadership"] = CareerEngine.analyze_leadership(profile, resume)

        # 18. Soft Skills
        results["Soft Skills"] = cls._evaluate_soft_skills(profile, profile_data)

        # 19. Career Progression
        results["Career Progression"] = CareerEngine.analyze_career_progression(profile, resume)

        # 20. Consistency
        results["Consistency"] = cls._evaluate_consistency(profile, resume)

        # 3. Compute contributions and overall weighted ATS score
        category_breakdowns = []
        overall_score = 0.0

        for cat in RULE_CATEGORIES:
            res = results.get(cat, {
                "category": cat,
                "score": 50.0,
                "strengths": [],
                "weaknesses": ["Analysis defaulted."],
                "recommendations": [],
                "confidence": 80
            })
            
            cat_weight = weights.get(cat, 0.05)
            score_val = res.get("score") if isinstance(res, dict) else None
            if score_val is None:
                logger.error(f"Category '{cat}' returned invalid result (missing score): {res}")
                score_val = 50.0

            contribution = score_val * cat_weight
            overall_score += contribution

            category_breakdowns.append({
                "category": cat,
                "score": score_val,
                "weight": cat_weight,
                "contribution": round(contribution, 2),
                "strengths": res.get("strengths", []) if isinstance(res, dict) else [],
                "weaknesses": res.get("weaknesses", []) if isinstance(res, dict) else ["Analysis error."],
                "recommendations": res.get("recommendations", []) if isinstance(res, dict) else [],
                "confidence": res.get("confidence", 80) if isinstance(res, dict) else 80
            })

        overall_score = max(0.0, min(100.0, overall_score))

        # Extract unified strengths, weaknesses, and recommendations for reports
        strengths_all = []
        weaknesses_all = []
        recommendations_all = []

        for breakdown in category_breakdowns:
            if breakdown["score"] >= 85:
                strengths_all.extend(breakdown["strengths"][:1])
            elif breakdown["score"] < 70:
                weaknesses_all.extend(breakdown["weaknesses"][:1])
                recommendations_all.extend(breakdown["recommendations"][:1])

        # Filter empty strings or duplicates
        strengths_all = list(set(filter(None, strengths_all)))
        weaknesses_all = list(set(filter(None, weaknesses_all)))
        recommendations_all = list(set(filter(None, recommendations_all)))

        # Default fallback messages if list is empty
        if not strengths_all: strengths_all = ["Resume sections are logically structured."]
        if not weaknesses_all: weaknesses_all = ["Some category scores could be optimized."]
        if not recommendations_all: recommendations_all = ["Review subscores to identify opportunities for enhancement."]

        return {
            "overall_score": round(overall_score, 2),
            "category_scores": category_breakdowns,
            "strengths": strengths_all,
            "weaknesses": weaknesses_all,
            "recommendations": recommendations_all
        }

    @classmethod
    def _evaluate_ats_compatibility(cls, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Check Confidence scores in DB
        avg_confidence = 90.0
        if ConfidenceScore:
            scores = ConfidenceScore.objects.filter(resume=resume)
            if scores.exists():
                avg_confidence = sum(s.score for s in scores) / scores.count()

        if avg_confidence < 80.0:
            score -= 15.0
            weaknesses.append("Low entity parsing confidence detected.")
            recommendations.append("Ensure your resume uses standard typography and no text boxes to help parsing accuracy.")
        else:
            strengths.append("High overall parsing confidence.")

        # Check Semantic validation
        has_semantic_errors = False
        if SemanticValidation:
            errors = SemanticValidation.objects.filter(resume=resume, status="invalid")
            if errors.exists():
                has_semantic_errors = True
                score -= len(errors) * 5.0
                weaknesses.append("Semantic validation warnings found (e.g. invalid dates, formatting mismatches).")
                recommendations.append("Resolve formatting and date discrepancies to ensure data consistency.")

        if not has_semantic_errors:
            strengths.append("Successfully passed semantic validation tests.")

        # Check Recovery Engine activities
        if RecoveryLog:
            recoveries = RecoveryLog.objects.filter(resume=resume)
            if recoveries.exists():
                score -= min(15.0, recoveries.count() * 3.0)
                weaknesses.append("Parsing recovered errors from formatting layouts.")
                recommendations.append("Simplify complex layouts to prevent parser failures.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "ATS Compatibility",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 95
        }

    @classmethod
    def _evaluate_github(cls, profile) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Find GitHub url in links
        links = profile.links if hasattr(profile, 'links') and profile.links else []
        if isinstance(links, str):
            links = [links]

        github_link = ""
        for link in links:
            if "github.com" in link.lower():
                github_link = link
                break

        if not github_link:
            score = 0.0
            weaknesses.append("GitHub profile link is missing.")
            recommendations.append("Add your GitHub URL to showcase your open-source projects and code contributions.")
        else:
            if not github_link.startswith(("http://", "https://")):
                score -= 20.0
                weaknesses.append("GitHub link is malformed (missing https:// protocol).")
                recommendations.append("Enter a fully qualified URL for GitHub (e.g. https://github.com/username).")
            else:
                strengths.append("GitHub profile link is present.")
                
                # Check for active repository details in projects
                projects_with_github = False
                projects = list(profile.projects.all()) if (hasattr(profile, 'projects') and hasattr(profile.projects, 'all')) else []
                for p in projects:
                    p_url = getattr(p, 'github_url', '') or getattr(p, 'url', '') or ""
                    if "github.com" in p_url.lower():
                        projects_with_github = True

                if projects_with_github:
                    strengths.append("Individual projects map directly to public repositories.")
                else:
                    score -= 10.0
                    weaknesses.append("None of the listed projects reference specific GitHub repositories.")
                    recommendations.append("Incorporate specific GitHub repository URLs for individual projects.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "GitHub",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 90
        }

    @classmethod
    def _evaluate_portfolio(cls, profile) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        links = profile.links if hasattr(profile, 'links') and profile.links else []
        if isinstance(links, str):
            links = [links]

        portfolio_link = ""
        for link in links:
            link_lower = link.lower()
            if any(x in link_lower for x in ["portfolio", "personal", "site", "web"]):
                portfolio_link = link
                break

        if not portfolio_link:
            score = 0.0
            weaknesses.append("No personal portfolio or website URL provided.")
            recommendations.append("Add a personal portfolio site or professional link (e.g., Behance, personal domain) to showcase visual/hands-on work.")
        else:
            if not portfolio_link.startswith(("http://", "https://")):
                score -= 20.0
                weaknesses.append("Portfolio link is malformed.")
                recommendations.append("Ensure portfolio website uses complete URL protocols (https://).")
            else:
                strengths.append("Professional portfolio/website link provided.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "Portfolio",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 90
        }

    @classmethod
    def _evaluate_linkedin(cls, profile) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        links = profile.links if hasattr(profile, 'links') and profile.links else []
        if isinstance(links, str):
            links = [links]

        linkedin_link = ""
        for link in links:
            if "linkedin.com" in link.lower():
                linkedin_link = link
                break

        if not linkedin_link:
            score = 0.0
            weaknesses.append("LinkedIn URL is missing.")
            recommendations.append("Incorporate your LinkedIn profile link to present a complete digital professional presence.")
        else:
            if not re.search(r"linkedin\.com/in/[a-zA-Z0-9\-_]+", linkedin_link.lower()):
                score -= 30.0
                weaknesses.append("LinkedIn URL appears malformed or lacks standard pathing structure (/in/).")
                recommendations.append("Use a direct LinkedIn profile link format (e.g., https://linkedin.com/in/username).")
            else:
                strengths.append("Professional LinkedIn profile link detected.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "LinkedIn",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 90
        }

    @classmethod
    def _evaluate_soft_skills(cls, profile, profile_data: dict) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Soft skills listed
        candidate_skills = []
        if hasattr(profile, 'skills') and profile.skills:
            if hasattr(profile.skills, 'all'):
                candidate_skills = [getattr(s, 'skill_name', getattr(s, 'name', '')) for s in profile.skills.all()]
            elif isinstance(profile.skills, list):
                candidate_skills = profile.skills

        candidate_skills_lower = [s.lower().strip() for s in candidate_skills]
        target_soft = [s.lower().strip() for s in profile_data.get("soft_skills", [])]

        matched_soft = [s for s in target_soft if s in candidate_skills_lower]
        
        if target_soft:
            soft_ratio = len(matched_soft) / len(target_soft)
            if soft_ratio < 0.3:
                score -= 30.0
                weaknesses.append("Lacks essential soft/interpersonal skills target for this role.")
                recommendations.append(f"Add key collaborative soft skills: {', '.join(target_soft[:2])}.")
            else:
                strengths.append("Soft skills list aligns with professional profile requirements.")
        else:
            # Fallback
            soft_keywords = ["communication", "collaboration", "leadership", "problem solving", "adaptability", "teamwork"]
            matched_fallback = [s for s in soft_keywords if s in candidate_skills_lower]
            if not matched_fallback:
                score -= 20.0
                weaknesses.append("No common interpersonal soft skills listed.")
                recommendations.append("Include 2-3 standard soft skills (e.g. Communication, Problem Solving).")

        # Evidence check (evaluates whether experience description includes soft skills usage context)
        experiences_text = " ".join([getattr(exp, 'description', '') or "" for exp in (profile.experiences.all() if hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all') else [])]).lower()
        
        has_evidence = False
        evidence_words = ["collaborated", "negotiated", "managed", "presented", "facilitated", "mentored", "communicated"]
        for word in evidence_words:
            if word in experiences_text:
                has_evidence = True
                break

        if has_evidence:
            strengths.append("Evidence-based soft skills integration found in work descriptions.")
        else:
            score -= 15.0
            weaknesses.append("Soft skills are only listed, without evidence of application in work history.")
            recommendations.append("Showcase soft skills (e.g. 'Collaborated with design team', 'Mentored juniors') inside work experience bullets.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "Soft Skills",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 90
        }

    @classmethod
    def _evaluate_consistency(cls, profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # 1. Timeline gaps & overlapping dates
        experiences = list(profile.experiences.all()) if (hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all')) else []
        
        overlapping_detected = False
        chronology_issue = False

        for i in range(len(experiences)):
            for j in range(i + 1, len(experiences)):
                start_i = getattr(experiences[i], 'start_date', None)
                end_i = getattr(experiences[i], 'end_date', None) or datetime.now().date()
                start_j = getattr(experiences[j], 'start_date', None)
                end_j = getattr(experiences[j], 'end_date', None) or datetime.now().date()

                if start_i and start_j:
                    # Check overlap (if start_i <= end_j and start_j <= end_i)
                    if start_i <= end_j and start_j <= end_i:
                        overlapping_detected = True

        if overlapping_detected:
            score -= 20.0
            weaknesses.append("Timeline overlap detected in job experiences.")
            recommendations.append("Ensure employment start and end dates do not conflict or overlap unless explaining dual roles.")
        else:
            strengths.append("No chronological conflicts or overlaps in professional history.")

        # 2. Check Consistency Checker models in DB
        if ConsistencyReport:
            reports = ConsistencyReport.objects.filter(resume=resume)
            if reports.exists():
                latest_report = reports.first()
                # Check for anomalies
                anomalies = getattr(latest_report, 'anomalies_found', []) or []
                if anomalies:
                    score -= len(anomalies) * 10.0
                    weaknesses.append(f"Content inconsistency anomalies detected ({len(anomalies)} issues).")
                    recommendations.append("Align skill mentions in experience sections with the registered skills list.")
                else:
                    strengths.append("Passed content consistency check.")

        score = max(0.0, min(100.0, score))
        return {
            "category": "Consistency",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": 90
        }
