"""
ATS Rule Executor – Runs rules against candidate profile data and logs executions.
"""

import logging
import time
from datetime import datetime
from django.db import transaction
from django.utils import timezone

from apps.profiles.models import Profile, Skill, Education, Experience, Project, Certification
from apps.resumes.models import Resume, ConsistencyReport
from apps.resumes.services.consistency_checker import ConsistencyChecker
from apps.reputation.models import ResumeReputation

from .models import RuleCategory, ATSRule, RuleExecution
from .rule_loader import RuleLoader
from .rule_registry import REGISTERED_HELPERS
from .profession_engine import ProfessionEngine
from .profile_registry import ProfileRegistry
from .weight_manager import WeightManager

logger = logging.getLogger(__name__)


class RuleExecutor:
    """Executes ATS Rule Engine checks on resumes."""

    @classmethod
    def execute_rules(cls, profile: Profile, resume: Resume, job_description: str = None) -> dict:
        """
        Executes all applicable ATS rules against the candidate profile and resume.
        Saves RuleExecution records to the database.
        """
        start_time = time.time()

        # 1. Self-Healing check: If no rules in DB, seed them first!
        if ATSRule.objects.count() == 0:
            logger.warning("No ATS rules found. Automatically seeding rules...")
            RuleLoader.seed_rules()

        # 2. Gather profile details
        skills = list(profile.skills.all())
        educations = list(profile.educations.all())
        experiences = list(profile.experiences.all())
        projects = list(profile.projects.all())
        certifications = list(profile.certifications.all())
        languages = list(profile.languages.all()) if hasattr(profile, "languages") else []

        skills_count = len(skills)
        experiences_count = len(experiences)
        projects_count = len(projects)
        educations_count = len(educations)
        certifications_count = len(certifications)
        languages_count = len(languages)

        # Prepare combined lowercase search text
        skills_text = ", ".join([s.skill_name for s in skills])
        exp_text = " ".join([f"{e.designation} at {e.company}: {e.description or ''}" for e in experiences])
        proj_text = " ".join([f"{p.project_name} using {p.technologies}: {p.description or ''}" for p in projects])
        profile_text = f"{profile.summary or ''} {skills_text} {exp_text} {proj_text}".lower()

        # 3. Detect candidate profession
        profile_data_dict = {
            "headline": profile.headline or "",
            "summary": profile.summary or "",
            "skills": [{"skill_name": s.skill_name} for s in skills],
            "experiences": [{"designation": e.designation, "company": e.company, "description": e.description or ""} for e in experiences],
            "projects": [{"project_name": p.project_name, "technologies": p.technologies, "description": p.description or ""} for p in projects]
        }
        profession = ProfessionEngine.detect_profession(profile_data_dict)

        # 3b. Load Profession Profile from registry
        profession_profile = ProfileRegistry.get_profile(profession)
        logger.info(f"Loaded ProfessionProfile: {profession_profile.role} (industry: {profession_profile.industry})")

        # 4. Invoke background analysis services to get grammar, formatting, keywords and consistency metrics
        from .keyword_engine import KeywordEngine
        from .grammar_engine import GrammarEngine
        from .format_engine import FormatEngine

        skills_list = [s.skill_name for s in skills]
        keyword_results = KeywordEngine.analyze_keywords(profile_text, profession, skills_list)
        grammar_results = GrammarEngine.analyze_grammar(profile, {"skills": skills, "experiences": experiences})
        formatting_results = FormatEngine.analyze_formatting(profile, {"skills": skills, "educations": educations, "experiences": experiences, "projects": projects})

        # Consistency score
        consistency_checker = ConsistencyChecker()
        consistency_res = consistency_checker.check_consistency(profile_data_dict)

        # 5. Build context variables for execution
        ctx = {
            "profile": profile,
            "skills": skills,
            "skills_count": skills_count,
            "experiences": experiences,
            "experiences_count": experiences_count,
            "projects": projects,
            "projects_count": projects_count,
            "educations": educations,
            "educations_count": educations_count,
            "certifications": certifications,
            "certifications_count": certifications_count,
            "languages": languages,
            "languages_count": languages_count,
            "profile_text": profile_text,
            "grammar_results": grammar_results,
            "formatting_results": formatting_results,
            "keyword_results": keyword_results,
            "consistency_results": consistency_res,
            "profession": profession,
            "job_description": job_description,
            "profession_profile": profession_profile
        }

        # 6. Load enabled rules matching target profession or 'All'
        rules = ATSRule.objects.filter(enabled=True).select_related("category")
        applicable_rules = []
        for r in rules:
            if r.profession == "All" or r.profession.lower() == profession.lower():
                applicable_rules.append(r)

        # 7. Evaluate each rule
        execution_results = []
        
        with transaction.atomic():
            # Delete any previous executions for this resume
            RuleExecution.objects.filter(resume=resume).delete()

            for r in applicable_rules:
                status = "skipped"
                score_impact = 0
                reason = ""
                recommendation = r.recommendation

                try:
                    # Evaluate condition
                    condition_result = eval(r.condition, REGISTERED_HELPERS, ctx)
                    
                    if condition_result:
                        status = "passed"
                        # Positive points are awarded if it passes. Penalty rules (negative points) award 0 on pass.
                        score_impact = r.points if r.points > 0 else 0
                        reason = f"Condition met: {r.explanation}"
                    else:
                        status = "failed"
                        # Penalty rules (negative points) subtract points if they fail.
                        score_impact = r.points if r.points < 0 else 0
                        reason = f"Condition not met: {r.description}"
                except Exception as e:
                    logger.error(f"Error evaluating rule {r.rule_code}: {str(e)}")
                    status = "skipped"
                    score_impact = 0
                    reason = f"Evaluation error: {str(e)}"

                # Create RuleExecution log
                execution = RuleExecution.objects.create(
                    resume=resume,
                    rule=r,
                    status=status,
                    score_impact=score_impact,
                    reason=reason,
                    recommendation=recommendation
                )
                
                execution_results.append({
                    "rule_code": r.rule_code,
                    "name": r.name,
                    "category": r.category.name,
                    "status": status,
                    "score_impact": score_impact,
                    "severity": r.severity,
                    "reason": reason,
                    "recommendation": recommendation,
                    "explanation": r.explanation,
                    "points": r.points
                })

        # 8. Apply Profession Profile skill checks
        profile_penalties = 0
        profile_bonuses = 0
        missing_required = []
        missing_recommended = []
        skills_lower = [s.skill_name.lower() for s in skills]

        for req_skill in profession_profile.required_skills:
            if req_skill.lower() not in skills_lower:
                missing_required.append(req_skill)
                profile_penalties += 3  # 3-point penalty per missing required skill

        for rec_skill in profession_profile.recommended_skills:
            if rec_skill.lower() not in skills_lower:
                missing_recommended.append(rec_skill)
                profile_penalties += 1  # 1-point penalty per missing recommended skill

        # Apply profile-level penalty/bonus rules
        for penalty_rule in profession_profile.penalties:
            try:
                if not eval(penalty_rule.get("condition", "False"), REGISTERED_HELPERS, ctx):
                    profile_penalties += penalty_rule.get("deduction", 0)
            except Exception:
                pass

        for bonus_rule in profession_profile.bonuses:
            try:
                if eval(bonus_rule.get("condition", "False"), REGISTERED_HELPERS, ctx):
                    profile_bonuses += bonus_rule.get("bonus", 0)
            except Exception:
                pass

        # 9. Invoke CategoryManager to run the quality scoring engine
        from .category_manager import CategoryManager
        
        prof_data = {
            "role": profession_profile.role,
            "industry": profession_profile.industry,
            "required_skills": profession_profile.required_skills,
            "recommended_skills": profession_profile.recommended_skills,
            "soft_skills": profession_profile.soft_skills,
            "preferred_certifications": profession_profile.preferred_certifications,
            "expected_projects": profession_profile.expected_projects,
            "weights": profession_profile.weights,
            "penalties": profession_profile.penalties,
            "bonuses": profession_profile.bonuses,
            "benchmark_group": profession_profile.benchmark_group
        }
        
        cat_analysis = CategoryManager.evaluate_resume(profile, resume, prof_data)
        
        # Format subscores for backward compatibility
        subscores = {}
        for breakdown in cat_analysis["category_scores"]:
            subscores[breakdown["category"].lower()] = breakdown["score"]

        overall_score = cat_analysis["overall_score"]
        
        # Apply profession profile penalties and bonuses
        overall_score = max(0.0, min(100.0, overall_score - profile_penalties + profile_bonuses))


        # Adjust score if in Job-Specific match mode
        job_match_score = None
        if job_description:
            # Match condition: calculate matched requirements dynamically
            job_match_rules = [res for res in execution_results if res["category"] == "Job Match"]
            job_match_passed = sum(1 for res in job_match_rules if res["status"] == "passed")
            job_match_total = len(job_match_rules) if job_match_rules else 1
            job_match_score = round((job_match_passed / job_match_total) * 100.0)
            
            # Combine overall ATS score with job match score
            overall_score = round((overall_score * 0.4) + (job_match_score * 0.6))

        processing_time = round(time.time() - start_time, 4)

        return {
            "overall_score": overall_score,
            "profession": profession,
            "profession_profile": {
                "role": profession_profile.role,
                "industry": profession_profile.industry,
                "required_skills": profession_profile.required_skills,
                "recommended_skills": profession_profile.recommended_skills,
                "missing_required_skills": missing_required,
                "missing_recommended_skills": missing_recommended,
                "weights": profession_profile.weights,
                "benchmark_group": profession_profile.benchmark_group
            },
            "subscores": subscores,
            "rules_executed_count": len(applicable_rules),
            "passed_count": sum(1 for res in execution_results if res["status"] == "passed"),
            "failed_count": sum(1 for res in execution_results if res["status"] == "failed"),
            "skipped_count": sum(1 for res in execution_results if res["status"] == "skipped"),
            "execution_results": execution_results,
            "processing_time": processing_time,
            "job_match_score": job_match_score,
            "profile_penalties": profile_penalties,
            "profile_bonuses": profile_bonuses,
            "category_scores": cat_analysis["category_scores"],
            "strengths": cat_analysis["strengths"],
            "weaknesses": cat_analysis["weaknesses"],
            "recommendations": cat_analysis["recommendations"]
        }

