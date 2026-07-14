import logging
from django.utils import timezone
# pyrefly: ignore [missing-import]
from apps.profiles.models import Profile 

# pyrefly: ignore [missing-import]
from apps.resumes.models import Resume 

# pyrefly: ignore [missing-import]
from apps.ats.models import ATSScore

# pyrefly: ignore [missing-import]
from apps.ats.services import ATSScoringService, IndustryMatcherService

from .models import ResumeReputation, Badge
from .score_engine import ScoreEngine
from .market_engine import MarketEngine
from .badge_engine import BadgeEngine
from .ranking_engine import RankingEngine
from .comparison_engine import ComparisonEngine

logger = logging.getLogger(__name__)


class ReputationEngine:
    """
    Central orchestrator for the Resume Reputation System.
    Aggregates sub-scores, awards credentials/badges, assigns tiers/percentiles,
    and persists ResumeReputation records in the database.
    """

    @classmethod
    def calculate_reputation(cls, resume: Resume) -> ResumeReputation:
        """
        Orchestrates full reputation score calculation, badges evaluation,
        and database persistence.
        """
        try:
            profile = Profile.objects.get(user=resume.user)
        except Profile.DoesNotExist:
            raise ValueError("User must have a verified profile to generate career reputation.")

        # 1. Obtain ATS Score (reuse existing or run analysis if missing)
        ats_record = ATSScore.objects.filter(resume=resume).order_by("-ats_completed_at").first()
        if not ats_record:
            logger.info("No ATS score found for resume %s. Running quick analysis.", resume.id)
            analysis = ATSScoringService.run_analysis(profile, resume.id)
            ats_record = ATSScore.objects.create(
                resume=resume,
                ats_score=analysis["overall_score"],
                ats_json=analysis,
                ats_processing_time=analysis["metadata"]["processing_time"],
                industry_match=analysis["metadata"]["industry_matches"],
                missing_skills=analysis["missing_skills"],
                suggestions=analysis["suggestions"]
            )

        ats_score = float(ats_record.ats_score)

        # 2. Identify Industry from profile text (for ranking & matching context)
        skills = list(profile.skills.all())
        experiences = list(profile.experiences.all())
        projects = list(profile.projects.all())
        
        profile_text_parts = [
            profile.summary or "",
            ", ".join([s.skill_name for s in skills]),
            " ".join([exp.designation + " " + exp.company + " " + (exp.description or "") for exp in experiences]),
            " ".join([proj.project_name + " " + (proj.description or "") + " " + proj.technologies for proj in projects])
        ]
        profile_text = " ".join(profile_text_parts)
        industry_matches = IndustryMatcherService.analyze(profile, profile_text)
        primary_industry = list(industry_matches.keys())[0] if industry_matches else "Software Engineering"

        # 3. Calculate Sub-scores
        skills_score = ScoreEngine.calculate_skills_score(profile)
        projects_score = ScoreEngine.calculate_projects_score(profile)
        portfolio_score = ScoreEngine.calculate_portfolio_score(profile)
        experience_score = ScoreEngine.calculate_experience_score(profile)
        consistency_score = ScoreEngine.calculate_consistency_score(profile, resume)
        learning_score = ScoreEngine.calculate_learning_score(profile)

        career_score = MarketEngine.calculate_career_score(profile)
        demand_score = MarketEngine.calculate_demand_score(profile)
        growth_score = MarketEngine.calculate_growth_score(profile)
        market_score = MarketEngine.calculate_market_score(profile, demand_score, growth_score)

        # 4. Aggregate Weighted Overall Score
        # ATS (25%), Skills (15%), Projects (15%), Portfolio (10%), Experience (10%),
        # Consistency (10%), Career (5%), Demand (5%), Growth (5%), Learning (5%)
        raw_overall = (
            (ats_score * 0.25) +
            (skills_score * 0.15) +
            (projects_score * 0.15) +
            (portfolio_score * 0.10) +
            (experience_score * 0.10) +
            (consistency_score * 0.10) +
            (career_score * 0.05) +
            (demand_score * 0.05) +
            (growth_score * 0.05) +
            (learning_score * 0.05)
        )
        reputation_score = int(round(raw_overall))

        # 5. Evaluate Credentials & Badges
        scores_payload = {
            "ats_score": ats_score,
            "skills_score": skills_score,
            "projects_score": projects_score,
            "portfolio_score": portfolio_score,
            "experience_score": experience_score,
            "learning_score": learning_score,
            "career_score": career_score,
            "demand_score": demand_score,
            "reputation_score": reputation_score
        }
        badges_earned = BadgeEngine.evaluate_badges(scores_payload)
        
        # Save earned badges to database
        current_badges = []
        for b in badges_earned:
            badge_obj, created = Badge.objects.get_or_create(resume=resume, badge=b["name"])
            current_badges.append(b["name"])
        
        # Clean up stale badges that are no longer earned
        Badge.objects.filter(resume=resume).exclude(badge__in=current_badges).delete()

        # 6. Apply Tiers & Ranks
        tier = RankingEngine.get_tier(reputation_score)
        rank_details = RankingEngine.get_industry_rank(
            reputation_score, str(resume.user.id), resume.user.username, primary_industry
        )

        # 7. Collect Benchmarking comparisons
        benchmarks = ComparisonEngine.get_benchmarks(reputation_score)

        # 8. Compile strengths, weaknesses, and improvement recommendations
        strengths = []
        weaknesses = []
        suggestions = []

        if ats_score >= 85: strengths.append("High compatibility with industry-standard ATS screening.")
        else: weaknesses.append("Resume layout or keyword density could trigger ATS parser errors.")

        if portfolio_score >= 80: strengths.append("Outstanding digital web presence with active theme layout.")
        else: weaknesses.append("No active web portfolio found to present project showcases.")

        if skills_score >= 80: strengths.append("Demonstrates a diverse and complete industry skillset.")
        else: weaknesses.append("Skills section has gaps matching target industry definitions.")

        if projects_score >= 80: strengths.append("Projects section is robust and includes live demonstration links.")
        else: weaknesses.append("Projects require quantitative metrics and repository link references.")

        if learning_score >= 80: strengths.append("High commitment to training, roadmap sequencing, and certification.")

        # Auto-recommendations list
        if ats_score < 90:
            suggestions.append({"priority": "critical", "points": 3, "category": "ATS Score", "text": "Optimize keywords and section headers to match ATS guidelines."})
        if portfolio_score < 85:
            suggestions.append({"priority": "important", "points": 2, "category": "Portfolio", "text": "Generate and publish your customized web portfolio to increase visibility."})
        if skills_score < 80:
            suggestions.append({"priority": "important", "points": 2, "category": "Skills", "text": "Incorporate missing high-demand keywords and skill categories."})
        if projects_score < 85:
            suggestions.append({"priority": "important", "points": 2, "category": "Projects", "text": "Add quantitative metrics (e.g. percentages, scale) and source code links to projects."})
        if learning_score < 80:
            suggestions.append({"priority": "optional", "points": 1, "category": "Learning", "text": "Add professional credentials or complete outstanding milestones on your learning roadmap."})

        # Detailed details payload to persist
        details_json = {
            "sub_scores": {
                "ats": ats_score,
                "skills": skills_score,
                "projects": projects_score,
                "portfolio": portfolio_score,
                "experience": experience_score,
                "consistency": consistency_score,
                "career": career_score,
                "demand": demand_score,
                "growth": growth_score,
                "learning": learning_score
            },
            "market_score": market_score,
            "primary_industry": primary_industry,
            "industry_rank": rank_details,
            "benchmarks": benchmarks,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "suggestions": suggestions,
            "badges": badges_earned
        }

        # 9. Save Reputation to DB
        reputation_record = ResumeReputation.objects.create(
            resume=resume,
            score=reputation_score,
            tier=tier,
            career_score=int(career_score),
            growth_score=int(growth_score),
            market_score=int(market_score),
            details_json=details_json
        )

        return reputation_record
