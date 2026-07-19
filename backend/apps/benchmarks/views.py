import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from apps.resumes.models import Resume
from .models import BenchmarkReport, RankingHistory, CareerRanking
from .serializers import BenchmarkReportSerializer, RankingHistorySerializer, CareerRankingSerializer
from .services.benchmark_engine import BenchmarkEngine

logger = logging.getLogger(__name__)


class HelperMixin:
    """
    Common helper functions to resolve resumes for logged in user.
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


class BenchmarkTriggerView(HelperMixin, APIView):
    """
    POST /api/benchmark/ -> Triggers and computes a fresh benchmark analysis report.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        resume_id = request.data.get("resume_id")
        resume = self.get_resume(request, resume_id)
        
        if not resume:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            report = BenchmarkEngine.generate_report(resume)
            serializer = BenchmarkReportSerializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Failed to calculate benchmark report.")
            return Response(
                {"error": f"Failed to calculate benchmark: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BenchmarkReportView(HelperMixin, APIView):
    """
    GET /api/benchmark/report/ -> Gets the latest benchmark report.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)
        
        if not resume:
            return Response(
                {"error": "No resume found."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        report = BenchmarkReport.objects.filter(resume=resume).order_by("-created_at").first()
        
        # If no report exists, trigger one automatically
        if not report:
            try:
                report = BenchmarkEngine.generate_report(resume)
            except Exception as e:
                logger.exception("Failed to auto-generate benchmark report.")
                return Response(
                    {"error": f"Failed to auto-generate benchmark: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        serializer = BenchmarkReportSerializer(report)
        return Response(serializer.data)


class BenchmarkHistoryView(HelperMixin, APIView):
    """
    GET /api/benchmark/history/ -> Gets ranking evaluation history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)
        
        if not resume:
            return Response([])
            
        history = RankingHistory.objects.filter(resume=resume).order_by("recorded_at")
        serializer = RankingHistorySerializer(history, many=True)
        return Response(serializer.data)


class RankLeaderboardView(HelperMixin, APIView):
    """
    GET /api/rank/ -> Fetches leaderboard and distribution comparisons across industry/demographics.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        resume_id = request.query_params.get("resume_id")
        resume = self.get_resume(request, resume_id)
        
        if not resume:
            return Response({"error": "No active resume found."}, status=status.HTTP_400_BAD_REQUEST)
            
        # Retrieve latest report for details
        report = BenchmarkReport.objects.filter(resume=resume).order_by("-created_at").first()
        if not report:
            # Auto-generate if missing
            try:
                report = BenchmarkEngine.generate_report(resume)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        details = report.details_json
        
        # Construct mock distribution comparisons to populate the leaderboard UI
        leaderboard_data = {
            "career_comparison": [
                {"group": "Architects", "average_score": 91, "your_level": details.get("experience_level") == "Architect"},
                {"group": "Senior Professionals", "average_score": 85, "your_level": details.get("experience_level") in ["Senior", "Lead"]},
                {"group": "Mid-Level Professionals", "average_score": 77, "your_level": details.get("experience_level") == "Mid"},
                {"group": "Junior Professionals", "average_score": 68, "your_level": details.get("experience_level") == "Junior"},
                {"group": "Freshers", "average_score": 58, "your_level": details.get("experience_level") == "Intern"},
                {"group": "Students", "average_score": 45, "your_level": details.get("experience_level") == "Student"}
            ],
            "industry_comparison": [
                {"industry": "AI", "average_score": 88, "active": details.get("industry") == "AI"},
                {"industry": "Cybersecurity", "average_score": 84, "active": details.get("industry") == "Cybersecurity"},
                {"industry": "FinTech", "average_score": 81, "active": details.get("industry") == "FinTech"},
                {"industry": "Cloud", "average_score": 79, "active": details.get("industry") == "Cloud"},
                {"industry": "Healthcare", "average_score": 74, "active": details.get("industry") == "Healthcare"},
                {"industry": "Education", "average_score": 65, "active": details.get("industry") == "Education"}
            ],
            "top_strengths": report.strengths,
            "top_weaknesses": report.weaknesses
        }
        
        return Response(leaderboard_data)
