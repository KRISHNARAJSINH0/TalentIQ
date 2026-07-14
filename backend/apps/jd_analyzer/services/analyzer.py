"""
JD Analyzer Service — Main orchestrator for Phase 22.

Coordinates all sub-engines (JDParser, SkillMatcher, GapAnalyzer,
ATSPredictor, KeywordEngine, RecommendationEngine) to produce a
complete analysis report comparing the user's Master Resume against a JD.
"""

import logging
from django.core.serializers.json import DjangoJSONEncoder
import json

from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileMasterSerializer
from apps.resumes.models import Resume

from ..models import JobDescription, JobAnalysis
from .jd_parser import JDParser
from .skill_matcher import SkillMatcher
from .gap_engine import GapAnalyzer
from .ats_predictor import ATSPredictor
from .keyword_engine import KeywordEngine
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


class JDAnalyzerService:
    """
    Orchestrates the full JD analysis pipeline.
    """

    def __init__(self):
        self.parser = JDParser()
        self.skill_matcher = SkillMatcher()
        self.gap_analyzer = GapAnalyzer()
        self.ats_predictor = ATSPredictor()
        self.keyword_engine = KeywordEngine()
        self.recommendation_engine = RecommendationEngine()

    def upload_and_parse(self, user, content: str, source_type: str = "text") -> JobDescription:
        """
        Step 1: Upload JD text, parse it, and persist the JobDescription.
        """
        parsed = self.parser.parse(content)

        jd = JobDescription.objects.create(
            user=user,
            title=parsed.get("title", ""),
            company=parsed.get("company", ""),
            industry=parsed.get("industry", "Technology"),
            content=content,
            parsed_data=parsed,
            source_type=source_type,
        )

        logger.info("JD uploaded and parsed: id=%s title=%s", jd.id, jd.title)
        return jd

    def analyze(self, user, jd_id=None, jd_content: str = None) -> JobAnalysis:
        """
        Step 2: Run full analysis comparing the user's Master Resume against a JD.

        Can accept either a jd_id (existing JD) or raw jd_content (upload + analyze).
        """
        # ── Get or create JD ────────────────────────────────────────
        if jd_id:
            jd = JobDescription.objects.get(id=jd_id, user=user)
        elif jd_content:
            jd = self.upload_and_parse(user, jd_content)
        else:
            raise ValueError("Either jd_id or jd_content must be provided.")

        parsed_jd = jd.parsed_data
        if not parsed_jd or parsed_jd.get("error"):
            parsed_jd = self.parser.parse(jd.content)
            jd.parsed_data = parsed_jd
            jd.save(update_fields=["parsed_data", "updated_at"])

        # ── Get user's Master Profile ───────────────────────────────
        resume = Resume.objects.filter(
            user=user, validation_status="completed"
        ).order_by("-updated_at").first()

        if not resume:
            resume = Resume.objects.filter(user=user).order_by("-updated_at").first()

        if not resume:
            raise ValueError("No resume found. Please upload a resume first.")

        # Get profile data
        try:
            profile = Profile.objects.get(user=user)
            serializer = ProfileMasterSerializer(profile)
            profile_data = json.loads(json.dumps(serializer.data, cls=DjangoJSONEncoder))
        except Profile.DoesNotExist:
            profile_data = {"skills": [], "experiences": [], "educations": [], "projects": [], "certifications": []}

        # ── Extract candidate skills list ───────────────────────────
        candidate_skills = [s.get("skill_name", "") for s in profile_data.get("skills", [])]
        jd_skills = parsed_jd.get("skills", [])

        # ── Run engines ─────────────────────────────────────────────
        skill_result = self.skill_matcher.match(candidate_skills, jd_skills)
        gap_result = self.gap_analyzer.analyze(profile_data, parsed_jd, skill_result)
        keyword_result = self.keyword_engine.analyze(jd.content, profile_data)
        ats_result = self.ats_predictor.predict(profile_data, parsed_jd, skill_result, keyword_result)
        rec_result = self.recommendation_engine.recommend(parsed_jd, skill_result, gap_result)

        # ── Compute composite match score ───────────────────────────
        match_score = round(
            skill_result["skills_match"] * 0.30
            + gap_result["experience_match"] * 0.25
            + gap_result["education_match"] * 0.10
            + keyword_result["keyword_match"] * 0.20
            + ats_result["ats_score"] * 0.15
        )
        match_score = max(0, min(100, match_score))

        # ── Persist analysis ────────────────────────────────────────
        analysis = JobAnalysis.objects.create(
            user=user,
            job_description=jd,
            resume=resume,
            match_score=match_score,
            ats_score=ats_result["ats_score"],
            skills_match=skill_result["skills_match"],
            experience_match=gap_result["experience_match"],
            education_match=gap_result["education_match"],
            keyword_match=keyword_result["keyword_match"],
            missing_skills=skill_result["missing"],
            matching_skills=skill_result["matching"],
            strengths=rec_result["strengths"],
            weaknesses=rec_result["weaknesses"],
            suggestions=ats_result["suggestions"],
            interview_readiness=rec_result["interview_readiness"],
            salary_estimate=rec_result["salary_estimate"],
            report={
                "parsed_jd": parsed_jd,
                "skill_analysis": skill_result,
                "gap_analysis": {
                    "skill_gaps": gap_result["skill_gaps"],
                    "experience_gap": gap_result["experience_gap"],
                    "education_gap": gap_result["education_gap"],
                    "certification_gaps": gap_result["certification_gaps"],
                },
                "ats_prediction": ats_result,
                "keyword_analysis": keyword_result,
                "recommendations": rec_result,
            },
        )

        logger.info(
            "JD Analysis complete: id=%s match=%d%% ats=%d%%",
            analysis.id, match_score, ats_result["ats_score"],
        )
        return analysis
