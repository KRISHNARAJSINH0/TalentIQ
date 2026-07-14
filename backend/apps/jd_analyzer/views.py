"""
JD Analyzer views — Phase 22.

Provides REST endpoints for uploading JDs, running analysis,
and retrieving reports, gap analysis, and ATS predictions.
"""

import logging
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import JobDescription, JobAnalysis
from .serializers import (
    JobDescriptionSerializer,
    JobDescriptionUploadSerializer,
    JobAnalysisSerializer,
    JobAnalysisListSerializer,
)
from .services.analyzer import JDAnalyzerService

logger = logging.getLogger(__name__)


class JDUploadView(APIView):
    """POST /api/jd/upload/ — Upload and parse a job description."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = JobDescriptionUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            service = JDAnalyzerService()
            jd = service.upload_and_parse(
                user=request.user,
                content=serializer.validated_data["content"],
                source_type=serializer.validated_data.get("source_type", "text"),
            )
            return Response(
                JobDescriptionSerializer(jd).data,
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error("JD upload failed: %s", str(e))
            return Response(
                {"error": f"Failed to parse job description: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class JDAnalyzeView(APIView):
    """POST /api/jd/analyze/ — Run full analysis (upload + analyze in one step)."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = request.data.get("content", "")
        jd_id = request.data.get("jd_id", None)

        if not content and not jd_id:
            return Response(
                {"error": "Provide either 'content' (JD text) or 'jd_id' (existing JD)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if content and len(content.strip()) < 50:
            return Response(
                {"error": "Job description must be at least 50 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            service = JDAnalyzerService()
            analysis = service.analyze(
                user=request.user,
                jd_id=jd_id,
                jd_content=content if content else None,
            )
            return Response(
                JobAnalysisSerializer(analysis).data,
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except JobDescription.DoesNotExist:
            return Response(
                {"error": "Job description not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error("JD analysis failed: %s", str(e), exc_info=True)
            return Response(
                {"error": f"Analysis failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class JDHistoryView(APIView):
    """GET /api/jd/history/ — List past analyses for the current user."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        analyses = JobAnalysis.objects.filter(
            user=request.user
        ).select_related("job_description").order_by("-created_at")[:20]

        return Response(
            JobAnalysisListSerializer(analyses, many=True).data,
            status=status.HTTP_200_OK,
        )


class JDReportView(APIView):
    """GET /api/jd/report/<uuid>/ — Full analysis report."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            analysis = JobAnalysis.objects.select_related(
                "job_description"
            ).get(id=pk, user=request.user)
            return Response(
                JobAnalysisSerializer(analysis).data,
                status=status.HTTP_200_OK,
            )
        except JobAnalysis.DoesNotExist:
            return Response(
                {"error": "Analysis not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class JDGapsView(APIView):
    """GET /api/jd/gaps/<uuid>/ — Gap analysis for a specific report."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            analysis = JobAnalysis.objects.get(id=pk, user=request.user)
            report = analysis.report or {}
            return Response({
                "missing_skills": analysis.missing_skills,
                "matching_skills": analysis.matching_skills,
                "gap_analysis": report.get("gap_analysis", {}),
                "skills_match": analysis.skills_match,
                "experience_match": analysis.experience_match,
                "education_match": analysis.education_match,
            })
        except JobAnalysis.DoesNotExist:
            return Response(
                {"error": "Analysis not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


class JDATSView(APIView):
    """GET /api/jd/ats/<uuid>/ — ATS prediction for a specific report."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            analysis = JobAnalysis.objects.get(id=pk, user=request.user)
            report = analysis.report or {}
            return Response({
                "ats_score": analysis.ats_score,
                "ats_prediction": report.get("ats_prediction", {}),
                "suggestions": analysis.suggestions,
            })
        except JobAnalysis.DoesNotExist:
            return Response(
                {"error": "Analysis not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
