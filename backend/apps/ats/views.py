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
    ProfessionProfile
)
from .serializers import (
    ATSScoreSerializer,
    ATSReportSerializer,
    ATSHistorySerializer,
    ATSRuleSerializer,
    RuleCategorySerializer,
    RuleExecutionSerializer,
    ProfessionProfileSerializer
)
from .rule_executor import RuleExecutor
from .rule_reporter import RuleReporter
from .rule_loader import RuleLoader
from .rule_validator import RuleValidator
from .profile_loader import ProfileLoader

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

            logger.info("ATS Rule Engine completed for resume %s (Score: %s)", 
                        resume_id, ats_score_record.ats_score)

            serializer = ATSScoreSerializer(ats_score_record)
            
            # Inject new report id for testing assertion views
            response_data = serializer.data
            response_data["id"] = str(report.id)
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
            serializer = ATSScoreSerializer(latest_score)
            return Response(serializer.data)

        # Build combined payload for dashboard compatibility
        data = {
            "id": str(latest_report.id),
            "resume": str(resume.id),
            "resume_title": resume.resume_title,
            "ats_score": latest_report.overall_score,
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
            "industry_match": {latest_report.metadata.get("profession", "Software Engineer"): 100.0},
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
