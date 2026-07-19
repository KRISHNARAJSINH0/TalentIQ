"""
ATS Views – API views for evaluating resumes via the Rule Engine and managing rules.
"""

import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction

from apps.resumes.models import Resume
from apps.profiles.models import Profile

from .models import (
    ATSScore,
    ATSReport,
    ATSHistory,
    ATSBenchmark,
    RuleCategory,
    ATSRule,
    RuleExecution,
    ProfessionProfile,
    CategoryScore,
    ExplanationReport,
    RecommendationHistory,
    ImprovementSimulation,
    CalibrationReport,
    ValidationRun,
    RuleMetrics,
    DistributionMetrics
)
from .serializers import (
    ATSScoreSerializer,
    ATSReportSerializer,
    ATSHistorySerializer,
    ATSRuleSerializer,
    RuleCategorySerializer,
    RuleExecutionSerializer,
    ProfessionProfileSerializer,
    CategoryScoreSerializer,
    ExplanationReportSerializer,
    RecommendationHistorySerializer,
    ImprovementSimulationSerializer,
    CalibrationReportSerializer,
    ValidationRunSerializer,
    RuleMetricsSerializer,
    DistributionMetricsSerializer
)
from .rule_executor import RuleExecutor
from .rule_reporter import RuleReporter
from .rule_loader import RuleLoader
from .rule_validator import RuleValidator
from .profile_loader import ProfileLoader
from .category_manager import CategoryManager
from .weight_manager import RULE_CATEGORIES
from .explanation_engine import ExplanationEngine
from .improvement_simulator import ImprovementSimulator


logger = logging.getLogger(__name__)


class ATSAnalyzeView(APIView):
    """
    POST /api/ats/analyze/
    Triggers an ATS analysis on the user's verified profile using the Rule Engine.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "resume_id is required to link the analysis."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            logger.error("ATS analysis failed: Profile does not exist for user %s", request.user.username)
            return Response(
                {"error": "Profile does not exist. Please initialize and verify your master profile first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("ATS Rule Engine analysis started for resume %s by user %s", resume_id, request.user.username)

        try:
            # 1. Execute rules
            exec_data = RuleExecutor.execute_rules(profile, resume)
            
            # 2. Build report payload
            report_payload = RuleReporter.build_report(exec_data)
            
            # Apply adjustments (Phase D)
            from .score_adjuster import ScoreAdjuster
            adj_data = ScoreAdjuster.adjust_score(profile, resume, report_payload["overall_score"])
            final_adjusted_score = adj_data["final_score"]
            report_payload["overall_score"] = final_adjusted_score
            
            if "metadata" not in report_payload or not isinstance(report_payload["metadata"], dict):
                report_payload["metadata"] = {}
            report_payload["metadata"]["adjustments"] = adj_data
            
            with transaction.atomic():
                # 3. Create or update ATSReport
                report = ATSReport.objects.create(
                    resume=resume,
                    overall_score=report_payload["overall_score"],
                    confidence=90, # default or dynamically set
                    job_ready=report_payload["overall_score"] >= 80,
                    parsing_quality=95,
                    strengths=report_payload["strengths"],
                    weaknesses=report_payload["weaknesses"],
                    recommendations=report_payload["recommendations"],
                    subscores=report_payload["subscores"],
                    metadata=report_payload["metadata"]
                )

                # 4. Create ATSHistory link
                history_log = ATSHistory.objects.create(
                    resume=resume,
                    overall_score=report_payload["overall_score"],
                    report=report
                )

                # 5. Store in legacy ATSScore model for backward compatibility
                # Convert the new report payload structure to the legacy ats_json keys
                legacy_json = {
                    "overall_score": report_payload["overall_score"],
                    "keyword_score": report_payload["subscores"].get("keyword quality", 70.0),
                    "skills_score": report_payload["subscores"].get("skills", 70.0),
                    "experience_score": report_payload["subscores"].get("experience", 70.0),
                    "education_score": report_payload["subscores"].get("education", 70.0),
                    "grammar_score": report_payload["subscores"].get("grammar", 70.0),
                    "formatting_score": report_payload["subscores"].get("formatting", 70.0),
                    "completion_score": report_payload["subscores"].get("contact", 80.0),
                    "industry_score": report_payload["subscores"].get("skills", 70.0),
                    "missing_skills": [],
                    "suggestions": report_payload["recommendations"],
                    "strengths": report_payload["strengths"],
                    "weaknesses": report_payload["weaknesses"],
                    "metadata": {
                        "primary_industry": report_payload["metadata"]["profession"],
                        "processing_time": report_payload["metadata"]["processing_time"],
                        "industry_matches": {report_payload["metadata"]["profession"]: 100.0}
                    }
                }

                ats_score_record = ATSScore.objects.create(
                    resume=resume,
                    ats_score=report_payload["overall_score"],
                    ats_json=legacy_json,
                    ats_processing_time=report_payload["metadata"]["processing_time"],
                    industry_match={report_payload["metadata"]["profession"]: 100.0},
                    missing_skills=[],
                    suggestions=report_payload["recommendations"]
                )

                # 6. Save quality-based CategoryScore records
                for breakdown in exec_data.get("category_scores", []):
                    CategoryScore.objects.update_or_create(
                        resume=resume,
                        category=breakdown["category"],
                        defaults={
                            "score": int(breakdown["score"]),
                            "confidence": int(breakdown["confidence"])
                        }
                    )


            logger.info("ATS Rule Engine completed for resume %s (Score: %s)", 
                        resume_id, ats_score_record.ats_score)

            from .benchmark_engine import BenchmarkEngine
            profession = report_payload["metadata"]["profession"]
            benchmark_data = BenchmarkEngine.get_benchmark_comparison(profession, report_payload["overall_score"])
            
            response_data = {
                "id": str(report.id),
                "resume": str(resume.id),
                "resume_title": resume.resume_title,
                "ats_score": report_payload["overall_score"],
                "overall_score": report_payload["overall_score"],
                "confidence": 90,
                "job_ready": report_payload["overall_score"] >= 80,
                "parsing_quality": 95,
                "strengths": report_payload["strengths"],
                "weaknesses": report_payload["weaknesses"],
                "recommendations": report_payload["recommendations"],
                "subscores": report_payload["subscores"],
                "metadata": report_payload["metadata"],
                "benchmark_comparison": benchmark_data,
                "ats_json": legacy_json,
                "industry_match": {profession: 100.0},
                "missing_skills": [],
                "suggestions": report_payload["recommendations"],
                "ats_completed_at": report.created_at.isoformat(),
                "ats_processing_time": report_payload["metadata"]["processing_time"]
            }
            return Response(response_data, status=status.HTTP_201_CREATED)


        except Exception as e:
            logger.exception("Unexpected error occurred during ATS Rule Engine analysis for user %s", request.user.username)
            return Response(
                {"error": f"An unexpected error occurred during ATS Rule Engine analysis: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ATSDetailView(APIView):
    """
    GET /api/ats/{resume_id}/
    Retrieves the latest completed ATS score for a specific resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, resume_id):
        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        # Check if new report exists
        latest_report = ATSReport.objects.filter(resume=resume).order_by("-created_at").first()
        
        if not latest_report:
            # Fallback to legacy ATSScore
            latest_score = ATSScore.objects.filter(resume=resume).order_by("-ats_completed_at").first()
            if not latest_score:
                return Response(
                    {"detail": "No ATS analysis has been run for this resume yet."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            ats_json = latest_score.ats_json or {}
            score = latest_score.ats_score or ats_json.get("overall_score", 0)
            metadata = ats_json.get("metadata", {})
            profession = metadata.get("primary_industry", "Software Engineer")
            
            from .benchmark_engine import BenchmarkEngine
            benchmark_data = BenchmarkEngine.get_benchmark_comparison(profession, score)
            
            data = {
                "id": str(latest_score.id),
                "resume": str(resume.id),
                "resume_title": resume.resume_title,
                "ats_score": score,
                "overall_score": score,
                "confidence": 90,
                "job_ready": score >= 80,
                "parsing_quality": 95,
                "strengths": ats_json.get("strengths", []),
                "weaknesses": ats_json.get("weaknesses", []),
                "recommendations": ats_json.get("suggestions", ats_json.get("recommendations", [])),
                "subscores": {
                    "keywords": ats_json.get("keyword_score", 70.0),
                    "skills": ats_json.get("skills_score", 70.0),
                    "skill_relevance": ats_json.get("industry_score", 70.0),
                    "formatting": ats_json.get("formatting_score", 70.0),
                    "experience_quality": ats_json.get("experience_score", 70.0),
                    "consistency": ats_json.get("completion_score", 70.0),
                },
                "metadata": {
                    "profession": profession,
                    "processing_time": latest_score.ats_processing_time,
                    "adjustments": metadata.get("adjustments", {})
                },
                "benchmark_comparison": benchmark_data,
                "ats_json": ats_json,
                "industry_match": latest_score.industry_match or {profession: 100.0},
                "missing_skills": latest_score.missing_skills or [],
                "suggestions": latest_score.suggestions or [],
                "ats_completed_at": latest_score.ats_completed_at.isoformat() if latest_score.ats_completed_at else None,
                "ats_processing_time": latest_score.ats_processing_time
            }
            return Response(data)

        # Build combined payload for dashboard compatibility
        profession = latest_report.metadata.get("profession", "Software Engineer")
        from .benchmark_engine import BenchmarkEngine
        benchmark_data = BenchmarkEngine.get_benchmark_comparison(profession, latest_report.overall_score)

        data = {
            "id": str(latest_report.id),
            "resume": str(resume.id),
            "resume_title": resume.resume_title,
            "ats_score": latest_report.overall_score,
            "overall_score": latest_report.overall_score,
            "confidence": latest_report.confidence,
            "job_ready": latest_report.job_ready,
            "parsing_quality": latest_report.parsing_quality,
            "strengths": latest_report.strengths,
            "weaknesses": latest_report.weaknesses,
            "recommendations": latest_report.recommendations,
            "subscores": latest_report.subscores,
            "metadata": latest_report.metadata,
            "benchmark_comparison": benchmark_data,
            "ats_json": {
                "overall_score": latest_report.overall_score,
                "strengths": latest_report.strengths,
                "weaknesses": latest_report.weaknesses,
                "recommendations": latest_report.recommendations,
                "subscores": latest_report.subscores,
                "metadata": latest_report.metadata,
                "suggestions": latest_report.recommendations,
                "missing_skills": []
            },
            "industry_match": {profession: 100.0},
            "missing_skills": [],
            "suggestions": latest_report.recommendations,
            "ats_completed_at": latest_report.created_at.isoformat(),
            "ats_processing_time": latest_report.metadata.get("processing_time", 0.05)
        }
        return Response(data)



class ATSHistoryView(APIView):
    """
    GET /api/ats/history/
    Retrieves the history of all ATS analysis runs for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logs = ATSHistory.objects.filter(resume__user=request.user).select_related("resume").order_by("-completed_at")
        serializer = ATSHistorySerializer(logs, many=True)
        return Response(serializer.data)


class ATSReportDetailView(APIView):
    """
    GET /api/ats/report/{id}/
    Retrieves detailed ATS report by ID, with profession-specific benchmarks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        report = get_object_or_404(ATSReport, id=id, resume__user=request.user)
        profession = report.metadata.get("profession", "Software Engineer")
        
        # Calculate/get benchmark comparison
        benchmark, _ = ATSBenchmark.objects.get_or_create(
            profession=profession,
            defaults={
                "percentile_25": 55,
                "percentile_50": 70,
                "percentile_75": 82,
                "percentile_90": 92,
                "average_score": 68
            }
        )

        score = report.overall_score
        standing = "Average"
        percentile_range = "50th-75th"
        if score >= benchmark.percentile_90:
            standing = "Top Talent"
            percentile_range = "90th+"
        elif score >= benchmark.percentile_75:
            standing = "Strong"
            percentile_range = "75th-90th"
        elif score >= benchmark.percentile_50:
            standing = "Above Average"
            percentile_range = "50th-75th"
        else:
            standing = "Needs Improvement"
            percentile_range = "Below 50th"

        benchmark_data = {
            "profession": profession,
            "percentile_25": benchmark.percentile_25,
            "percentile_50": benchmark.percentile_50,
            "percentile_75": benchmark.percentile_75,
            "percentile_90": benchmark.percentile_90,
            "average_score": benchmark.average_score,
            "candidate_standing": standing,
            "candidate_percentile_range": percentile_range
        }

        serializer = ATSReportSerializer(report)
        data = serializer.data
        data["benchmark_comparison"] = benchmark_data
        
        # Backward compatibility dashboard properties
        data["ats_score"] = score
        data["ats_json"] = {
            "overall_score": score,
            "strengths": report.strengths,
            "weaknesses": report.weaknesses,
            "recommendations": report.recommendations,
            "subscores": report.subscores,
            "metadata": report.metadata,
            "suggestions": report.recommendations,
            "missing_skills": []
        }
        
        return Response(data)


class ATSJobMatchView(APIView):
    """
    POST /api/ats/job-match/
    Runs job description matching analysis.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        job_description = request.data.get("job_description")

        if not resume_id or not job_description:
            return Response(
                {"error": "resume_id and job_description are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        profile = get_object_or_404(Profile, user=request.user)

        try:
            exec_data = RuleExecutor.execute_rules(profile, resume, job_description)
            report_payload = RuleReporter.build_report(exec_data)

            # Store in ATSReport
            report = ATSReport.objects.create(
                resume=resume,
                overall_score=report_payload["overall_score"],
                confidence=90,
                job_ready=report_payload["overall_score"] >= 80,
                parsing_quality=95,
                strengths=report_payload["strengths"],
                weaknesses=report_payload["weaknesses"],
                recommendations=report_payload["recommendations"],
                subscores=report_payload["subscores"],
                job_description_text=job_description,
                metadata=report_payload["metadata"]
            )

            serializer = ATSReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Job match execution failed.")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ATSRuleListView(APIView):
    """
    GET /api/ats/rules/
    POST /api/ats/rules/
    Returns list of all rules, or creates a new custom rule (Admin only).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rules = ATSRule.objects.all().select_related("category")
        category = request.query_params.get("category")
        profession = request.query_params.get("profession")
        
        if category:
            rules = rules.filter(category__name__iexact=category)
        if profession:
            rules = rules.filter(profession__iexact=profession)

        serializer = ATSRuleSerializer(rules, many=True)
        return Response(serializer.data)

    def post(self, request):
        # Allow only staff or authentic users to customize rules
        if not request.user.is_staff:
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
            
        data = request.data
        try:
            RuleValidator.validate_rule(data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        category_name = data.get("category_name") or "Contact"
        category, _ = RuleCategory.objects.get_or_create(
            name=category_name,
            defaults={"description": f"Custom rules category {category_name}"}
        )

        rule = ATSRule.objects.create(
            rule_code=data["rule_code"],
            name=data["name"],
            category=category,
            description=data["description"],
            condition=data["condition"],
            points=int(data["points"]),
            severity=data.get("severity", "medium"),
            profession=data.get("profession", "All"),
            enabled=data.get("enabled", True),
            recommendation=data.get("recommendation", "Review rule specification."),
            explanation=data.get("explanation", "Custom configured evaluation logic.")
        )

        serializer = ATSRuleSerializer(rule)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ATSRuleDetailView(APIView):
    """
    GET, PUT, DELETE /api/ats/rules/{id}/
    Admin actions for single rule configuration.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        rule = get_object_or_404(ATSRule, pk=pk)
        serializer = ATSRuleSerializer(rule)
        return Response(serializer.data)

    def put(self, request, pk):
        # Require staff for rule modification
        if not request.user.is_staff:
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
            
        rule = get_object_or_404(ATSRule, pk=pk)
        data = request.data

        if "condition" in data:
            try:
                RuleValidator.validate_condition(data["condition"])
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Update fields
        for field in ["name", "description", "condition", "points", "severity", "profession", "enabled", "recommendation", "explanation"]:
            if field in data:
                val = data[field]
                if field == "points":
                    val = int(val)
                elif field == "enabled":
                    val = bool(val)
                setattr(rule, field, val)

        rule.save()
        serializer = ATSRuleSerializer(rule)
        return Response(serializer.data)

    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
            
        rule = get_object_or_404(ATSRule, pk=pk)
        rule.delete()
        return Response(status=status.HTTP_24_NO_CONTENT or status.HTTP_204_NO_CONTENT)


class ATSEvaluateView(APIView):
    """
    POST /api/ats/evaluate/
    Evaluates a resume's profile explicitly using the Rule Engine.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        job_description = request.data.get("job_description")

        if not resume_id:
            return Response({"error": "resume_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        profile = get_object_or_404(Profile, user=request.user)

        try:
            exec_data = RuleExecutor.execute_rules(profile, resume, job_description)
            report_payload = RuleReporter.build_report(exec_data)
            return Response(report_payload)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ATSRuleExecutionView(APIView):
    """
    GET /api/ats/execution/
    Returns list of executions for a resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response({"error": "resume_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        executions = RuleExecution.objects.filter(resume=resume).select_related("rule", "rule__category")
        serializer = RuleExecutionSerializer(executions, many=True)
        return Response(serializer.data)


class ATSRuleImportExportView(APIView):
    """
    GET /api/ats/rules/import-export/
    POST /api/ats/rules/import-export/
    Admin only: Import or export rules configurations.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        json_str = RuleLoader.export_rules_to_json()
        return Response(json.loads(json_str))

    def post(self, request):
        if not request.user.is_staff:
            return Response({"error": "Admin credentials required."}, status=status.HTTP_403_FORBIDDEN)
        rules_json = request.data.get("rules")
        if not rules_json:
            return Response({"error": "rules payload is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            count = RuleLoader.import_rules_from_json(rules_json if isinstance(rules_json, str) else json.dumps(rules_json))
            return Response({"message": f"Successfully imported {count} rules."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Import failed: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class ProfessionProfileListView(APIView):
    """
    GET /api/ats/profiles/
    Returns list of all profession profiles.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Ensure profiles are seeded
        if ProfessionProfile.objects.count() == 0:
            ProfileLoader.seed_profiles()

        profiles = ProfessionProfile.objects.all()
        industry = request.query_params.get("industry")
        enabled_only = request.query_params.get("enabled")

        if industry:
            profiles = profiles.filter(industry__iexact=industry)
        if enabled_only and enabled_only.lower() == "true":
            profiles = profiles.filter(enabled=True)

        serializer = ProfessionProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class ProfessionProfileDetailView(APIView):
    """
    GET /api/ats/profile/{role}/
    POST /api/ats/profile/
    PUT /api/ats/profile/{role}/
    DELETE /api/ats/profile/{role}/
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, role=None):
        if not role:
            return Response({"error": "Role name is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure profiles are seeded
        if ProfessionProfile.objects.count() == 0:
            ProfileLoader.seed_profiles()

        profile = ProfessionProfile.objects.filter(role__iexact=role).first()
        if not profile:
            return Response({"error": f"Profile for role '{role}' not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfessionProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request, role=None):
        """Create a new profession profile."""
        serializer = ProfessionProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, role=None):
        """Update an existing profession profile."""
        if not role:
            return Response({"error": "Role name is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile = ProfessionProfile.objects.filter(role__iexact=role).first()
        if not profile:
            return Response({"error": f"Profile for role '{role}' not found."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data
        for field in ["industry", "required_sections", "optional_sections", "required_skills",
                      "recommended_skills", "soft_skills", "preferred_certifications",
                      "expected_projects", "weights", "penalties", "bonuses",
                      "benchmark_group", "enabled"]:
            if field in data:
                setattr(profile, field, data[field])

        profile.save()
        serializer = ProfessionProfileSerializer(profile)
        return Response(serializer.data)

    def delete(self, request, role=None):
        """Delete a profession profile."""
        if not role:
            return Response({"error": "Role name is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile = ProfessionProfile.objects.filter(role__iexact=role).first()
        if not profile:
            return Response({"error": f"Profile for role '{role}' not found."}, status=status.HTTP_404_NOT_FOUND)

        profile.delete()
        return Response({"message": f"Profile '{role}' deleted."}, status=status.HTTP_204_NO_CONTENT)


class ProfessionProfileSeedView(APIView):
    """
    POST /api/ats/profiles/seed/
    Seeds or reseeds all default profession profiles.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        overwrite = request.data.get("overwrite", False)
        count = ProfileLoader.seed_profiles(overwrite=bool(overwrite))
        return Response({
            "message": f"Successfully seeded {count} profession profiles.",
            "total_profiles": ProfessionProfile.objects.count()
        })


class CategoryListView(APIView):
    """
    GET /api/ats/categories/
    Returns the list of 20 categories used by the Category Scoring Engine.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({
            "categories": RULE_CATEGORIES
        }, status=status.HTTP_200_OK)


class CategoryScoreDetailView(APIView):
    """
    POST /api/ats/category-score/
    Recalculates quality scores for a given resume.
    If 'category' is specified, recalculates/returns only that category.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        target_category = request.data.get("category")

        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        profile = get_object_or_404(Profile, user=request.user)

        # Trigger analysis to get latest calculations
        exec_data = RuleExecutor.execute_rules(profile, resume)

        if target_category:
            # Check if category is valid
            matched_breakdown = None
            for breakdown in exec_data.get("category_scores", []):
                if breakdown["category"].lower() == target_category.lower():
                    matched_breakdown = breakdown
                    break

            if not matched_breakdown:
                return Response(
                    {"error": f"Category '{target_category}' is invalid or not evaluated."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve/Update saved object
            score_obj, _ = CategoryScore.objects.update_or_create(
                resume=resume,
                category=matched_breakdown["category"],
                defaults={
                    "score": int(matched_breakdown["score"]),
                    "confidence": int(matched_breakdown["confidence"])
                }
            )
            return Response(CategoryScoreSerializer(score_obj).data, status=status.HTTP_200_OK)

        # Recalculate/Update all
        saved_scores = []
        for breakdown in exec_data.get("category_scores", []):
            score_obj, _ = CategoryScore.objects.update_or_create(
                resume=resume,
                category=breakdown["category"],
                defaults={
                    "score": int(breakdown["score"]),
                    "confidence": int(breakdown["confidence"])
                }
            )
            saved_scores.append(score_obj)

        return Response(
            CategoryScoreSerializer(saved_scores, many=True).data,
            status=status.HTTP_200_OK
        )


class CategoryReportView(APIView):
    """
    GET /api/ats/category-report/
    Retrieves the detailed category quality score breakdown for a specific resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "resume_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        # Get existing scores
        scores = CategoryScore.objects.filter(resume=resume)

        if not scores.exists():
            # If no scores computed yet, run them on the fly
            try:
                profile = Profile.objects.get(user=request.user)
                RuleExecutor.execute_rules(profile, resume)
                scores = CategoryScore.objects.filter(resume=resume)
            except Profile.DoesNotExist:
                return Response(
                    {"error": "Profile must be initialized to run category scores."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CategoryScoreSerializer(scores, many=True)
        return Response({
            "resume_id": resume.id,
            "resume_title": resume.resume_title,
            "category_scores": serializer.data
        }, status=status.HTTP_200_OK)


class ATSAdjustmentsView(APIView):
    """
    POST /api/ats/adjustments/
    Takes resume_id and returns the base score, penalty score, bonus score, final score and breakdown report lists.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "resume_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile must be initialized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve or run report to get base score
        report = ATSReport.objects.filter(resume=resume).first()
        if not report:
            # Run rule execution first to build the report
            exec_data = RuleExecutor.execute_rules(profile, resume)
            report_payload = RuleReporter.build_report(exec_data)
            report = ATSReport.objects.create(
                resume=resume,
                overall_score=report_payload["overall_score"],
                confidence=90,
                job_ready=report_payload["overall_score"] >= 80,
                parsing_quality=95,
                strengths=report_payload["strengths"],
                weaknesses=report_payload["weaknesses"],
                recommendations=report_payload["recommendations"],
                subscores=report_payload["subscores"],
                metadata=report_payload["metadata"]
            )

        # Now calculate adjustments using the metadata or running on the fly
        adj = report.metadata.get("adjustments")
        if not adj:
            from .score_adjuster import ScoreAdjuster
            # Calculate on the fly
            # Let's get the base score: if adjustments not yet saved, overall_score is the base score
            base = report.overall_score
            adj = ScoreAdjuster.adjust_score(profile, resume, base)
            
            # Save it back to report metadata & overall_score
            report.overall_score = adj["final_score"]
            if not isinstance(report.metadata, dict):
                report.metadata = {}
            report.metadata["adjustments"] = adj
            report.save()
            
            # Update history and legacy ATSScore too for consistency
            ATSHistory.objects.filter(report=report).update(overall_score=adj["final_score"])
            ATSScore.objects.filter(resume=resume).update(ats_score=adj["final_score"])

        return Response(adj, status=status.HTTP_200_OK)


class ATSPenaltiesView(APIView):
    """
    GET /api/ats/penalties/
    Returns the active penalties breakdown for a given resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "resume_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile must be initialized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        report = ATSReport.objects.filter(resume=resume).first()
        adj = report.metadata.get("adjustments") if report else None

        if not adj:
            # calculate on the fly
            from .score_adjuster import ScoreAdjuster
            base = report.overall_score if report else 70
            adj = ScoreAdjuster.adjust_score(profile, resume, base)
            
            if report:
                report.overall_score = adj["final_score"]
                if not isinstance(report.metadata, dict):
                    report.metadata = {}
                report.metadata["adjustments"] = adj
                report.save()

        return Response({
            "resume_id": resume.id,
            "total_penalties": adj["penalties"],
            "penalty_report": adj["penalty_report"]
        }, status=status.HTTP_200_OK)


class ATSBonusesView(APIView):
    """
    GET /api/ats/bonuses/
    Returns the active bonuses breakdown for a given resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response(
                {"error": "resume_id query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile must be initialized."},
                status=status.HTTP_400_BAD_REQUEST
            )

        report = ATSReport.objects.filter(resume=resume).first()
        adj = report.metadata.get("adjustments") if report else None

        if not adj:
            # calculate on the fly
            from .score_adjuster import ScoreAdjuster
            base = report.overall_score if report else 70
            adj = ScoreAdjuster.adjust_score(profile, resume, base)
            
            if report:
                report.overall_score = adj["final_score"]
                if not isinstance(report.metadata, dict):
                    report.metadata = {}
                report.metadata["adjustments"] = adj
                report.save()

        return Response({
            "resume_id": resume.id,
            "total_bonuses": adj["bonuses"],
            "bonus_report": adj["bonus_report"]
        }, status=status.HTTP_200_OK)


class ExplainScoreView(APIView):
    """
    POST /api/ats/explain/
    Generates and returns an Explainability Report for a resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        if not resume_id:
            return Response({"error": "resume_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        try:
            report = ExplanationEngine.generate_explanation(resume)
            serializer = ExplanationReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error generating ATS explanation: {str(e)}")
            return Response({"error": f"Failed to generate explanation: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExplanationDetailView(APIView):
    """
    GET /api/ats/explanation/
    Retrieves the latest Explanation Report for a resume.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response({"error": "resume_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        report = ExplanationReport.objects.filter(resume=resume).first()

        if not report:
            # Generate on the fly
            try:
                report = ExplanationEngine.generate_explanation(resume)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                logger.error(f"Error generating explanation on the fly: {str(e)}")
                return Response({"error": "No explanation report exists and generation failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = ExplanationReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SimulateScoreView(APIView):
    """
    POST /api/ats/simulate/
    Simulates ATS score improvement based on selected actions.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        actions = request.data.get("actions", [])

        if not resume_id:
            return Response({"error": "resume_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        # Get current score
        latest_report = ExplanationReport.objects.filter(resume=resume).first()
        if latest_report:
            current_score = latest_report.overall_score
        else:
            # fallback to legacy or run explanation on the fly
            try:
                report = ExplanationEngine.generate_explanation(resume)
                current_score = report.overall_score
            except Exception:
                current_score = 50

        # Perform simulation
        sim_data = ImprovementSimulator.simulate(current_score, actions)

        # Save simulation record
        sim_obj = ImprovementSimulation.objects.create(
            resume=resume,
            current_score=sim_data["current_score"],
            simulated_actions=sim_data["applied_actions"],
            estimated_score=sim_data["estimated_score"]
        )

        # Fetch suggestions to help user explore more
        try:
            profile = Profile.objects.get(user=request.user)
            # Find missing skills to pass to suggestions
            latest_run = RuleExecutor.execute_rules(profile, resume)
            missing_elements = {
                "missing_required_skills": latest_run["profession_profile"].get("missing_required_skills", []),
                "missing_recommended_skills": latest_run["profession_profile"].get("missing_recommended_skills", [])
            }
            suggestions = ImprovementSimulator.get_suggested_actions(profile, resume, missing_elements)
        except Exception:
            suggestions = []

        response_data = {
            "simulation": ImprovementSimulationSerializer(sim_obj).data,
            "score_boost": sim_data["score_boost"],
            "suggested_actions": suggestions
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ActionPlanView(APIView):
    """
    GET /api/ats/action-plan/
    Returns the prioritized step-by-step roadmap from recommendation history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        if not resume_id:
            return Response({"error": "resume_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        resume = get_object_or_404(Resume, id=resume_id, user=request.user)
        
        recs = RecommendationHistory.objects.filter(resume=resume, implemented=False)
        
        # If no recommendation history, generate on the fly
        if not recs.exists():
            try:
                ExplanationEngine.generate_explanation(resume)
                recs = RecommendationHistory.objects.filter(resume=resume, implemented=False)
            except Exception as e:
                logger.error(f"Failed to generate action plan: {str(e)}")

        serializer = RecommendationHistorySerializer(recs, many=True)
        return Response({
            "resume_id": resume.id,
            "action_plan": serializer.data
        }, status=status.HTTP_200_OK)


class CalibrateView(APIView):
    """
    POST /api/ats/calibrate/
    Triggers automated calibration sweep.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        from .calibration_engine import CalibrationEngine
        engine = CalibrationEngine()
        results = engine.run_calibration_sweep()
        return Response(results, status=status.HTTP_200_OK)


class ValidateView(APIView):
    """
    POST /api/ats/validate/
    Triggers automated validation sweep.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        from .validation_engine import ValidationEngine
        engine = ValidationEngine()
        results = engine.run_validation_sweep()
        return Response(results, status=status.HTTP_200_OK)


class EngineHealthView(APIView):
    """
    GET /api/ats/health/
    Returns the overall ATS engine health stats.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        latest_calib = CalibrationReport.objects.order_by("-created_at").first()
        latest_val = ValidationRun.objects.order_by("-created_at").first()
        
        calib_data = CalibrationReportSerializer(latest_calib).data if latest_calib else None
        val_data = ValidationRunSerializer(latest_val).data if latest_val else None

        # Fetch rule usage metrics
        rule_metrics = RuleMetrics.objects.order_by("-pass_rate")
        rule_metrics_data = RuleMetricsSerializer(rule_metrics, many=True).data

        return Response({
            "latest_calibration": calib_data,
            "latest_validation": val_data,
            "rule_metrics": rule_metrics_data
        }, status=status.HTTP_200_OK)


class DistributionView(APIView):
    """
    GET /api/ats/distribution/
    Returns score distribution data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        latest_dist = DistributionMetrics.objects.order_by("-created_at").first()
        dist_data = DistributionMetricsSerializer(latest_dist).data if latest_dist else None
        return Response({
            "latest_distribution": dist_data
        }, status=status.HTTP_200_OK)


class QualityReportView(APIView):
    """
    GET /api/ats/quality/
    Returns the latest structured quality report JSON.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from .quality_reporter import QualityReporter
        report = QualityReporter.generate_quality_report()
        return Response(report, status=status.HTTP_200_OK)




