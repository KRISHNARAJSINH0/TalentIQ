"""
ATS Views – API views for running and retrieving ATS analysis.
"""

import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.resumes.models import Resume
from apps.profiles.models import Profile
from .models import ATSScore
from .serializers import ATSScoreSerializer
from .services import ATSScoringService

logger = logging.getLogger(__name__)


class ATSAnalyzeView(APIView):
    """
    POST /api/ats/analyze/
    Triggers an ATS analysis on the user's verified profile.
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
        
        # Ensure user has a profile
        try:
            profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            logger.error("ATS analysis failed: Profile does not exist for user %s", request.user.username)
            return Response(
                {"error": "Profile does not exist. Please initialize and verify your master profile first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        logger.info("ATS analysis started for resume %s by user %s", resume_id, request.user.username)

        try:
            # Run the deterministic scoring service
            analysis = ATSScoringService.run_analysis(profile, resume_id)
            
            # Identify primary industry for logging
            primary_industry = analysis.get("metadata", {}).get("primary_industry", "Unknown")
            logger.info("ATS: Industry identified for user %s: %s", request.user.username, primary_industry)

            # Store in database
            ats_score_record = ATSScore.objects.create(
                resume=resume,
                ats_score=analysis["overall_score"],
                ats_json=analysis,
                ats_processing_time=analysis["metadata"]["processing_time"],
                industry_match=analysis["metadata"]["industry_matches"],
                missing_skills=analysis["missing_skills"],
                suggestions=analysis["suggestions"]
            )

            logger.info("ATS completed for resume %s (Score: %s) in %s seconds", 
                        resume_id, ats_score_record.ats_score, ats_score_record.ats_processing_time)

            serializer = ATSScoreSerializer(ats_score_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.exception("Unexpected error occurred during ATS analysis for user %s", request.user.username)
            return Response(
                {"error": f"An unexpected error occurred during ATS analysis: {str(e)}"},
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
        
        latest_score = ATSScore.objects.filter(resume=resume).order_by("-ats_completed_at").first()
        if not latest_score:
            return Response(
                {"detail": "No ATS analysis has been run for this resume yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ATSScoreSerializer(latest_score)
        return Response(serializer.data)


class ATSHistoryView(APIView):
    """
    GET /api/ats/history/
    Retrieves the history of all ATS analysis runs for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Retrieve all ATS analyses for resumes belonging to the user
        scores = ATSScore.objects.filter(resume__user=request.user).select_related("resume").order_by("-ats_completed_at")
        serializer = ATSScoreSerializer(scores, many=True)
        return Response(serializer.data)
