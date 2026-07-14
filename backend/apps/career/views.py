from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileMasterSerializer
from .models import CareerProfile, CoverLetter, LearningProgressLog
from .serializers import CareerProfileSerializer, CoverLetterSerializer, LearningProgressLogSerializer
from .services import CareerAnalysisService, CoverLetterGeneratorService


class CareerAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            # Auto-initialize and auto-verify from latest completed resume if not verified/empty
            if not profile.is_verified or not profile.summary:
                from apps.resumes.models import Resume
                from apps.profiles.views import initialize_profile_from_resume
                latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
                if latest_resume:
                    if not profile.summary:
                        initialize_profile_from_resume(profile, latest_resume)
                    profile.is_verified = True
                    profile.save()
        except Profile.DoesNotExist:
            from apps.resumes.models import Resume
            latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
            if latest_resume:
                profile = Profile.objects.create(user=request.user)
                from apps.profiles.views import initialize_profile_from_resume
                initialize_profile_from_resume(profile, latest_resume)
                profile.is_verified = True
                profile.save()
            else:
                return Response(
                    {"error": "No professional profile found. Please upload a resume first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not profile.is_verified:
            return Response(
                {"error": "Your profile is not verified yet. Please review and verify it first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get master resume json using the ProfileMasterSerializer
        profile_data = ProfileMasterSerializer(profile).data

        # Get ATS results if any (from the user's latest ATSScore record)
        ats_results = {}
        try:
            from apps.ats.models import ATSScore
            latest_ats = ATSScore.objects.filter(resume__user=request.user).order_by("-created_at").first()
            if latest_ats:
                ats_results = {
                    "score": latest_ats.ats_score,
                    "keyword_feedback": latest_ats.ats_json.get("keyword_feedback", {}),
                    "skills_feedback": latest_ats.ats_json.get("skills_feedback", {}),
                }
        except Exception as e:
            logger.warning(f"Could not retrieve ATS scores: {e}")

        # Perform analysis
        analysis = CareerAnalysisService.analyze_profile(profile_data, ats_results)

        scores = analysis.get("scores", {})
        career_details = analysis.get("career_details", {})
        skill_gap = analysis.get("skill_gap", {})
        roadmap = analysis.get("roadmap", {})
        suggestions = analysis.get("suggestions", {})

        # Merge suggestions, skill_gap, and details into career_json
        career_json = {
            "career_details": career_details,
            "skill_gap": skill_gap,
            "suggestions": suggestions
        }

        # Update or create CareerProfile
        career_profile, created = CareerProfile.objects.update_or_create(
            profile=profile,
            defaults={
                "career_readiness": scores.get("career_readiness", 70),
                "growth_score": scores.get("growth_score", 70),
                "learning_score": scores.get("learning_score", 70),
                "industry_alignment": scores.get("industry_alignment", 70),
                "skill_strength": scores.get("skill_strength", 70),
                "market_demand": scores.get("market_demand", 70),
                "career_json": career_json,
                "roadmap_json": roadmap
            }
        )

        # Auto-create LearningProgressLog entries for the new roadmap milestones
        # to allow checklist tracking
        milestones = roadmap.get("milestones", [])
        for ms in milestones:
            milestone_title = ms.get("milestone_title")
            items = ms.get("items", [])
            for item in items:
                name = item.get("name")
                cat = item.get("category")
                if milestone_title and name:
                    LearningProgressLog.objects.get_or_create(
                        user=request.user,
                        milestone_title=milestone_title,
                        item_name=name,
                        defaults={"category": cat}
                    )

        serializer = CareerProfileSerializer(career_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CareerProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            career_profile = CareerProfile.objects.get(profile=profile)
        except (Profile.DoesNotExist, CareerProfile.DoesNotExist):
            return Response(
                {"error": "No career assistant analysis found. Please trigger an analysis first."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CareerProfileSerializer(career_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoadmapDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            career_profile = CareerProfile.objects.get(profile=profile)
        except (Profile.DoesNotExist, CareerProfile.DoesNotExist):
            return Response(
                {"error": "No career roadmap found. Please run profile analysis first."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get completed progress items to annotate checkboxes
        progress_logs = LearningProgressLog.objects.filter(user=request.user)
        progress_map = {f"{log.milestone_title}:{log.item_name}": log.is_completed for log in progress_logs}

        roadmap = career_profile.roadmap_json
        milestones = roadmap.get("milestones", [])
        for ms in milestones:
            m_title = ms.get("milestone_title")
            for item in ms.get("items", []):
                key = f"{m_title}:{item.get('name')}"
                item["is_completed"] = progress_map.get(key, False)

        return Response(roadmap, status=status.HTTP_200_OK)


class SkillGapDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            career_profile = CareerProfile.objects.get(profile=profile)
        except (Profile.DoesNotExist, CareerProfile.DoesNotExist):
            return Response(
                {"error": "No skill gap analysis found. Please run profile analysis first."},
                status=status.HTTP_404_NOT_FOUND
            )

        skill_gap = career_profile.career_json.get("skill_gap", {})
        return Response(skill_gap, status=status.HTTP_200_OK)


class CoverLetterGenerateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.data.get("company")
        position = request.data.get("position")
        job_description = request.data.get("job_description", "")
        tone = request.data.get("tone", "Professional")
        letter_type = request.data.get("cover_letter_type", "Job Application")

        if not company or not position:
            return Response(
                {"error": "Company and Position fields are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            profile = Profile.objects.get(user=request.user)
            # Auto-initialize and auto-verify from latest completed resume if not verified/empty
            if not profile.is_verified or not profile.summary:
                from apps.resumes.models import Resume
                from apps.profiles.views import initialize_profile_from_resume
                latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
                if latest_resume:
                    if not profile.summary:
                        initialize_profile_from_resume(profile, latest_resume)
                    profile.is_verified = True
                    profile.save()
        except Profile.DoesNotExist:
            from apps.resumes.models import Resume
            latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
            if latest_resume:
                profile = Profile.objects.create(user=request.user)
                from apps.profiles.views import initialize_profile_from_resume
                initialize_profile_from_resume(profile, latest_resume)
                profile.is_verified = True
                profile.save()
            else:
                return Response(
                    {"error": "Please create and verify your profile first."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not profile.is_verified:
            return Response(
                {"error": "Please create and verify your profile first."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Retrieve profile JSON data
        profile_data = ProfileMasterSerializer(profile).data

        # Generate cover letter
        content = CoverLetterGeneratorService.generate(
            profile_data=profile_data,
            company=company,
            position=position,
            description=job_description,
            tone=tone,
            letter_type=letter_type
        )

        cover_letter = CoverLetter.objects.create(
            user=request.user,
            company=company,
            position=position,
            job_description=job_description,
            tone=tone,
            cover_letter_type=letter_type,
            content=content
        )

        serializer = CoverLetterSerializer(cover_letter)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CoverLetterListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        letters = CoverLetter.objects.filter(user=request.user)
        serializer = CoverLetterSerializer(letters, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LearningProgressUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        milestone_title = request.data.get("milestone_title")
        item_name = request.data.get("item_name")
        is_completed = request.data.get("is_completed", False)

        if not milestone_title or not item_name:
            return Response(
                {"error": "Milestone title and item name are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        log, created = LearningProgressLog.objects.get_or_create(
            user=request.user,
            milestone_title=milestone_title,
            item_name=item_name,
            defaults={"category": "Technology"}
        )

        log.is_completed = is_completed
        log.completed_at = timezone.now() if is_completed else None
        log.save()

        serializer = LearningProgressLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)
