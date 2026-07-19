import logging
from django.utils import timezone

from apps.profiles.models import Profile
from apps.resumes.models import Resume
from .models import ExplanationReport, RecommendationHistory
from .rule_executor import RuleExecutor
from .reason_generator import ReasonGenerator
from .evidence_engine import EvidenceEngine
from .priority_engine import PriorityEngine
from .natural_language_engine import NaturalLanguageEngine
from .improvement_simulator import ImprovementSimulator

logger = logging.getLogger(__name__)

class ExplanationEngine:
    """
    Central service for compiling explainable ATS insights, score breakdowns, 
    and prioritized recommendation histories.
    """

    @classmethod
    def generate_explanation(cls, resume: Resume) -> ExplanationReport:
        """
        Runs ATS rules, generates explanation, and saves it in the database.
        """
        # Fetch profile
        try:
            profile = Profile.objects.get(user=resume.user)
        except Profile.DoesNotExist:
            logger.error(f"Profile does not exist for resume {resume.id}")
            raise ValueError("Profile does not exist. Please initialize and verify your master profile first.")

        # 1. Run ATS Rule Engine
        analysis = RuleExecutor.execute_rules(profile, resume)

        overall_score = round(analysis["overall_score"])
        profession = analysis["profession"]
        category_scores = analysis["category_scores"]
        strengths = analysis.get("strengths", [])
        weaknesses = analysis.get("weaknesses", [])

        # Context dict for evidence check
        ctx = {
            "missing_required_skills": analysis["profession_profile"].get("missing_required_skills", []),
            "missing_recommended_skills": analysis["profession_profile"].get("missing_recommended_skills", []),
            "profession_profile": analysis["profession_profile"]
        }

        # 2. Loop through the 7 core categories to compile category explanations
        # Categories mapping:
        core_categories = [
            "Contact Information",
            "Professional Summary",
            "Skills",
            "Projects",
            "Experience",
            "Education",
            "Achievements"
        ]

        category_explanations = {}

        for cat in core_categories:
            # Find matching breakdown in category_scores
            breakdown = next((c for c in category_scores if c["category"] == cat), None)
            if not breakdown:
                # Provide standard fallback if not evaluated
                breakdown = {
                    "score": 50.0,
                    "weight": 0.05,
                    "strengths": [],
                    "weaknesses": ["Section details need review."],
                    "recommendations": ["Optimize this category details."],
                    "confidence": 80
                }

            cat_score = round(breakdown["score"])
            cat_weight = breakdown["weight"]
            cat_strengths = breakdown.get("strengths", [])
            cat_weaknesses = breakdown.get("weaknesses", [])
            cat_recs = breakdown.get("recommendations", [])
            cat_confidence = breakdown.get("confidence", 90)

            # Generate reason & evidence
            reason = ReasonGenerator.generate_reason(cat, cat_score, cat_strengths, cat_weaknesses, profile)
            evidence = EvidenceEngine.gather_evidence(cat, profile, resume, ctx)

            # Calculate impact & estimated improvement
            # Impact represents points lost: (100 - score) * weight
            lost_points = (100 - cat_score) * cat_weight
            impact = round(lost_points)
            estimated_improvement = round(lost_points)

            rec_text = cat_recs[0] if cat_recs else "Ensure this section is complete and well-structured."

            category_explanations[cat] = {
                "score": cat_score,
                "reason": reason,
                "evidence": evidence,
                "impact": impact,
                "recommendation": rec_text,
                "estimated_improvement": estimated_improvement,
                "confidence": cat_confidence
            }

        # 3. Create overall score breakdown
        # Map subscores for charts
        skills_score = round(category_explanations.get("Skills", {}).get("score", 50))
        projects_score = round(category_explanations.get("Projects", {}).get("score", 50))
        experience_score = round(category_explanations.get("Experience", {}).get("score", 50))
        education_score = round(category_explanations.get("Education", {}).get("score", 50))

        score_breakdown = {
            "Skills": skills_score,
            "Projects": projects_score,
            "Experience": experience_score,
            "Education": education_score,
            "Penalties": abs(analysis.get("profile_penalties", 0)),
            "Bonuses": analysis.get("profile_bonuses", 0),
            "Final": overall_score
        }

        # 4. Generate natural language paragraph report
        nl_report = NaturalLanguageEngine.generate_report(
            overall_score, profession, category_scores, strengths, weaknesses
        )

        # 5. Save ExplanationReport
        # Check if one already exists for the resume, delete to store latest
        ExplanationReport.objects.filter(resume=resume).delete()

        report_obj = ExplanationReport.objects.create(
            resume=resume,
            overall_score=overall_score,
            confidence=95,
            natural_language_report=nl_report,
            category_explanations=category_explanations,
            ats_score_breakdown=score_breakdown
        )

        # 6. Save Prioritized Recommendations in RecommendationHistory
        prioritized_recs = PriorityEngine.prioritize_recommendations(category_scores)
        
        # We replace old suggestions with the new run to reflect latest edits
        RecommendationHistory.objects.filter(resume=resume, implemented=False).delete()

        for item in prioritized_recs:
            RecommendationHistory.objects.get_or_create(
                resume=resume,
                category=item["category"],
                recommendation_text=item["recommendation_text"],
                priority=item["priority"],
                score_impact=item["score_impact"],
                implemented=False
            )

        return report_obj
