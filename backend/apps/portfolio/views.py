import logging
from django.utils import timezone
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes

from apps.profiles.models import Profile
from apps.profiles.serializers import ProfileMasterSerializer
from .models import Portfolio, PortfolioAnalyticsLog
from .serializers import PortfolioSerializer, PortfolioAnalyticsLogSerializer

logger = logging.getLogger(__name__)


def log_portfolio_activity(portfolio, event_type, section_name=None, request=None):
    """
    Utility helper to log activity for portfolio views, downloads, shares.
    """
    ip_address = None
    user_agent = None
    if request:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(",")[0].strip()
        else:
            ip_address = request.META.get("REMOTE_ADDR")
        user_agent = request.META.get("HTTP_USER_AGENT")

    PortfolioAnalyticsLog.objects.create(
        portfolio=portfolio,
        event_type=event_type,
        section_name=section_name,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    # Increment main counters
    if event_type == PortfolioAnalyticsLog.EventType.VIEW:
        Portfolio.objects.filter(pk=portfolio.pk).update(views=models.F("views") + 1)
    elif event_type == PortfolioAnalyticsLog.EventType.DOWNLOAD:
        Portfolio.objects.filter(pk=portfolio.pk).update(downloads=models.F("downloads") + 1)
    elif event_type == PortfolioAnalyticsLog.EventType.SHARE:
        Portfolio.objects.filter(pk=portfolio.pk).update(shares=models.F("shares") + 1)


class PortfolioGenerateView(APIView):
    """
    POST /api/portfolio/generate/
    Generates or regenerates portfolio snapshot from verified master profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        # Check if profile is empty and auto-initialize from resume if possible
        if not profile.summary:
            from apps.resumes.models import Resume
            from apps.profiles.views import initialize_profile_from_resume
            latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
            if latest_resume:
                initialize_profile_from_resume(profile, latest_resume)
                profile.is_verified = True
                profile.save()

        # Get verified profile data
        profile_serializer = ProfileMasterSerializer(profile)
        master_data = profile_serializer.data

        # Create or update portfolio
        portfolio, created = Portfolio.objects.get_or_create(
            profile=profile,
            defaults={"theme": Portfolio.Theme.MODERN}
        )

        portfolio.portfolio_json = master_data
        portfolio.last_generated = timezone.now()
        portfolio.save()

        logger.info(
            "Portfolio %s for user %s (%s)",
            "created" if created else "regenerated",
            request.user.username,
            portfolio.slug,
        )

        serializer = PortfolioSerializer(portfolio, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioDetailView(APIView):
    """
    GET /api/portfolio/
    Retrieve authenticated user's portfolio. Auto-generates one if it doesn't exist yet.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)

        # Check if profile is empty and auto-initialize from resume if possible
        if not profile.summary:
            from apps.resumes.models import Resume
            from apps.profiles.views import initialize_profile_from_resume
            latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
            if latest_resume:
                initialize_profile_from_resume(profile, latest_resume)
                profile.is_verified = True
                profile.save()

        portfolio, created = Portfolio.objects.get_or_create(
            profile=profile,
            defaults={"theme": Portfolio.Theme.MODERN}
        )

        # Auto-generate portfolio data if none exists or if it contains placeholder empty data
        if created or not portfolio.portfolio_json or not portfolio.portfolio_json.get("first_name"):
            profile_serializer = ProfileMasterSerializer(profile)
            portfolio.portfolio_json = profile_serializer.data
            portfolio.last_generated = timezone.now()
            portfolio.save()

        serializer = PortfolioSerializer(portfolio, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioPublicDetailView(APIView):
    """
    GET /api/portfolio/<slug>/
    Retrieves public portfolio by slug. Tracks a view event in analytics.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, slug):
        portfolio = get_object_or_404(Portfolio.objects.select_related("profile__user"), slug=slug)

        # Auto-generate/update portfolio data if none exists or if it contains placeholder empty data
        if not portfolio.portfolio_json or not portfolio.portfolio_json.get("first_name"):
            profile_serializer = ProfileMasterSerializer(portfolio.profile)
            portfolio.portfolio_json = profile_serializer.data
            portfolio.last_generated = timezone.now()
            portfolio.save()

        # Check visibility
        if not portfolio.is_public:
            if not request.user.is_authenticated or str(portfolio.profile.user_id) != str(request.user.id):
                return Response(
                    {"error": "This portfolio is set to private."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # Log view activity
        log_portfolio_activity(
            portfolio=portfolio,
            event_type=PortfolioAnalyticsLog.EventType.VIEW,
            request=request,
        )

        # Refresh database metrics
        portfolio.refresh_from_db()

        serializer = PortfolioSerializer(portfolio, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class PortfolioUpdateThemeView(APIView):
    """
    PATCH /api/portfolio/theme/
    Updates theme and custom slug.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        portfolio = get_object_or_404(Portfolio, profile=profile)

        serializer = PortfolioSerializer(
            portfolio, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info("Portfolio theme/slug updated for user %s", request.user.username)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortfolioUpdatePrivacyView(APIView):
    """
    PATCH /api/portfolio/privacy/
    Updates is_public setting.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        portfolio = get_object_or_404(Portfolio, profile=profile)

        serializer = PortfolioSerializer(
            portfolio, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info("Portfolio privacy updated to %s for user %s", portfolio.is_public, request.user.username)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortfolioLogActivityView(APIView):
    """
    POST /api/portfolio/analytics/log/
    Logs client-triggered events like share, download, section views.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        slug = request.data.get("slug")
        event_type = request.data.get("event_type")
        section_name = request.data.get("section_name")

        if not slug or not event_type:
            return Response(
                {"error": "slug and event_type are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        portfolio = get_object_or_404(Portfolio.objects.select_related("profile__user"), slug=slug)

        # Log activity
        log_portfolio_activity(
            portfolio=portfolio,
            event_type=event_type,
            section_name=section_name,
            request=request,
        )

        return Response({"status": "success"}, status=status.HTTP_200_OK)


class PortfolioAnalyticsView(APIView):
    """
    GET /api/portfolio/analytics/
    Returns aggregated metrics and trends.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        portfolio = get_object_or_404(Portfolio, profile=profile)

        # 1. Base counts
        total_views = portfolio.views
        total_downloads = portfolio.downloads
        total_shares = portfolio.shares

        # 2. Section views count
        section_views = (
            PortfolioAnalyticsLog.objects.filter(
                portfolio=portfolio,
                event_type=PortfolioAnalyticsLog.EventType.SECTION_VIEW,
            )
            .values("section_name")
            .annotate(count=models.Count("id"))
            .order_by("-count")
        )

        # Convert queryset to dictionary
        sections_data = {item["section_name"]: item["count"] for item in section_views if item["section_name"]}

        # 3. Traffic trends (last 7 days views)
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        daily_trends = (
            PortfolioAnalyticsLog.objects.filter(
                portfolio=portfolio,
                event_type=PortfolioAnalyticsLog.EventType.VIEW,
                created_at__gte=seven_days_ago,
            )
            .extra(select={"day": "date(created_at)"})
            .values("day")
            .annotate(count=models.Count("id"))
            .order_by("day")
        )

        trends_data = {item["day"]: item["count"] for item in daily_trends}

        # Populate missing days in the last 7 days
        filled_trends = []
        for i in range(7):
            day_date = (timezone.now() - timezone.timedelta(days=6-i)).date()
            day_str = day_date.strftime("%Y-%m-%d")
            filled_trends.append({
                "date": day_str,
                "views": trends_data.get(day_str, 0)
            })

        analytics_data = {
            "total_views": total_views,
            "total_downloads": total_downloads,
            "total_shares": total_shares,
            "section_views": sections_data,
            "daily_trends": filled_trends,
        }

        return Response(analytics_data, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def portfolio_root(request):
    """Fallback portfolio root API endpoint."""
    return Response({"message": "Portfolio API – Online"})
