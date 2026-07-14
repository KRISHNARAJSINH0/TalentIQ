import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.resumes.models import Resume
from apps.profiles.models import Profile
from .models import ResumeReputation, Badge
from .serializers import ResumeReputationSerializer, BadgeSerializer
from .reputation_engine import ReputationEngine

logger = logging.getLogger(__name__)


class HelperMixin:
    """
    Common helper functions for reputation views.
    """
    def get_resume(self, request, resume_id=None):
        if resume_id:
            return get_object_or_404(Resume, id=resume_id, user=request.user)
        
        # Fallback to active resume
        resume = Resume.objects.filter(user=request.user, is_active=True).first()
        if not resume:
            # Fallback to latest updated resume
            resume = Resume.objects.filter(user=request.user).order_by("-updated_at").first()
        return resume


class ReputationView(HelperMixin, APIView):
    """
    POST /api/ai/reputation/ -> Triggers/calculates reputation.
    GET /api/ai/reputation/ -> Retrieves the latest active reputation summary.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        resume = self.get_resume(request, resume_id)
        
        if not resume:
            return Response(
                {"error": "No resume found. Please upload or build a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has a profile
        if not Profile.objects.filter(user=request.user).exists():
            return Response(
                {"error": "No verified profile found. Please initialize and verify your master profile first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reputation = ReputationEngine.calculate_reputation(resume)
            serializer = ResumeReputationSerializer(reputation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Failed to calculate resume reputation.")
            return Response(
                {"error": f"Failed to compute reputation: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)

        if not resume:
            return Response(
                {"error": "No resume found. Please upload or build a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get latest computed reputation
        reputation = ResumeReputation.objects.filter(resume=resume).order_by("-created_at").first()
        if not reputation:
            # Check if user has a profile
            if not Profile.objects.filter(user=request.user).exists():
                return Response(
                    {"error": "No verified profile found. Please initialize and verify your master profile first."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Compute fresh
            try:
                reputation = ReputationEngine.calculate_reputation(resume)
            except Exception as e:
                logger.exception("Failed to compute initial resume reputation.")
                return Response(
                    {"error": f"Failed to compute reputation: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        serializer = ResumeReputationSerializer(reputation)
        return Response(serializer.data)


class ReputationHistoryView(APIView):
    """
    GET /api/ai/reputation/history/ -> Retrieves historical scores for the user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reputations = ResumeReputation.objects.filter(resume__user=request.user).order_by("-created_at")
        serializer = ResumeReputationSerializer(reputations, many=True)
        return Response(serializer.data)


class ReputationBadgesView(HelperMixin, APIView):
    """
    GET /api/ai/reputation/badges/ -> Retrieves earned badges.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)

        if not resume:
            return Response([])

        badges = Badge.objects.filter(resume=resume).order_by("-earned_at")
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data)


class ReputationBenchmarkView(HelperMixin, APIView):
    """
    GET /api/ai/reputation/benchmark/ -> Retrieves benchmarking comparisons.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)

        if not resume:
            return Response({"error": "No resume found."}, status=status.HTTP_400_BAD_REQUEST)

        reputation = ResumeReputation.objects.filter(resume=resume).order_by("-created_at").first()
        if not reputation:
            return Response(
                {"error": "No reputation report found. Please run a reputation analysis first."},
                status=status.HTTP_404_NOT_FOUND
            )

        benchmarks = reputation.details_json.get("benchmarks", [])
        return Response(benchmarks)
