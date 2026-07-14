import logging
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.resumes.models import Resume
from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileMasterSerializer

from .models import JobRecommendation, SkillGap
from .serializers import JobRecommendationSerializer, SkillGapSerializer
from .services.job_engine import JobIntelligenceEngine, JobsGeminiService

logger = logging.getLogger(__name__)


class BaseJobView(APIView):
    """
    Base view containing helper methods for profile and resume retrieval.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_resume_and_profile(self, request):
        # 1. Fetch latest completed resume
        resume = Resume.objects.filter(
            user=request.user,
            validation_status="completed"
        ).order_by("-updated_at").first()

        if not resume:
            # Check for any resume if no completed one exists
            resume = Resume.objects.filter(user=request.user).order_by("-updated_at").first()

        # 2. Fetch or initialize professional profile
        try:
            profile = Profile.objects.get(user=request.user)
            if not profile.is_verified and resume:
                from apps.profiles.views import initialize_profile_from_resume
                initialize_profile_from_resume(profile, resume)
                profile.is_verified = True
                profile.save()
        except Profile.DoesNotExist:
            if resume:
                profile = Profile.objects.create(user=request.user)
                from apps.profiles.views import initialize_profile_from_resume
                initialize_profile_from_resume(profile, resume)
                profile.is_verified = True
                profile.save()
            else:
                profile = None

        return resume, profile


class JobMatchView(BaseJobView):
    """
    POST: /api/jobs/match/
    Calculates and persists JobRecommendations and SkillGaps for the active resume.
    """
    def post(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume or profile found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile_data = ProfileMasterSerializer(profile).data
            # Run engine evaluation
            result = JobIntelligenceEngine.evaluate_profile(resume, profile_data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Job Match generation failed: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to calculate job matches: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobPredictView(BaseJobView):
    """
    POST: /api/jobs/predict/
    Returns instant mock predictions for custom role/skills inputs, or user profile if empty.
    """
    def post(self, request):
        custom_payload = request.data.get("payload")
        
        # If payload is provided, run predictions directly without persisting
        if custom_payload:
            service = JobsGeminiService()
            result = service.generate_intelligence(custom_payload)
            return Response(result, status=status.HTTP_200_OK)

        # Fall back to user active profile
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No profile found for predictions. Please upload a resume or provide a payload."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile_data = ProfileMasterSerializer(profile).data
            service = JobsGeminiService()
            result = service.generate_intelligence(profile_data)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Prediction failed: {e}", exc_info=True)
            return Response(
                {"error": f"Prediction failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class JobRecommendationsView(BaseJobView):
    """
    GET: /api/jobs/recommendations/
    Returns stored recommended jobs. Automatically triggers calculation if none exist.
    """
    def get(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        recs = JobRecommendation.objects.filter(resume=resume)
        if not recs.exists():
            # Auto-trigger evaluation if database records do not exist
            profile_data = ProfileMasterSerializer(profile).data
            JobIntelligenceEngine.evaluate_profile(resume, profile_data)
            recs = JobRecommendation.objects.filter(resume=resume)

        serializer = JobRecommendationSerializer(recs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobMarketView(BaseJobView):
    """
    GET: /api/jobs/market/
    Returns market demand and trending skills.
    """
    def get(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_data = ProfileMasterSerializer(profile).data
        service = JobsGeminiService()
        result = service.generate_intelligence(profile_data)
        
        market_data = {
            "market_demand": result.get("market_demand", "High"),
            "market_score": result.get("market_score", 85),
            "trending_skills": result.get("trending_skills", []),
            "remote_eligibility": result.get("remote_eligibility", {})
        }
        return Response(market_data, status=status.HTTP_200_OK)


class JobSalaryView(BaseJobView):
    """
    GET: /api/jobs/salary/
    Returns forecasted salary metrics.
    """
    def get(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_data = ProfileMasterSerializer(profile).data
        service = JobsGeminiService()
        result = service.generate_intelligence(profile_data)
        
        return Response(result.get("salary_forecast", {}), status=status.HTTP_200_OK)


class JobCompaniesView(BaseJobView):
    """
    GET: /api/jobs/companies/
    Returns recommended companies.
    """
    def get(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile_data = ProfileMasterSerializer(profile).data
        service = JobsGeminiService()
        result = service.generate_intelligence(profile_data)
        
        companies_data = {
            "companies": result.get("companies", []),
            "countries": result.get("countries", [])
        }
        return Response(companies_data, status=status.HTTP_200_OK)


class JobSkillsGapView(BaseJobView):
    """
    GET: /api/jobs/skills-gap/
    Returns stored skill gaps. Automatically triggers calculations if none exist.
    """
    def get(self, request):
        resume, profile = self.get_resume_and_profile(request)
        if not resume or not profile:
            return Response(
                {"error": "No resume found. Please upload a resume first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        gaps = SkillGap.objects.filter(resume=resume)
        if not gaps.exists():
            # Auto-trigger evaluation if database records do not exist
            profile_data = ProfileMasterSerializer(profile).data
            JobIntelligenceEngine.evaluate_profile(resume, profile_data)
            gaps = SkillGap.objects.filter(resume=resume)

        serializer = SkillGapSerializer(gaps, many=True)
        
        # Pull advanced recommendations also to provide complete roadmap solutions
        service = JobsGeminiService()
        profile_data = ProfileMasterSerializer(profile).data
        result = service.generate_intelligence(profile_data)

        response_data = {
            "gaps": serializer.data,
            "recommendations": result.get("recommendations", {})
        }
        return Response(response_data, status=status.HTTP_200_OK)
