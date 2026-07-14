import time
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, views, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .permissions import IsAdminUserRole
from .models import AuditLog, UsageAnalytics
from .serializers import AdminUserSerializer, AuditLogSerializer, UsageAnalyticsSerializer
from .services import AdminService, AnalyticsService, ReportingService, MonitoringService

User = get_user_model()


class AdminDashboardView(views.APIView):
    """GET /api/admin/dashboard/ - Summary counts, KPIs, and recent log snippets."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        summary = AdminService.get_dashboard_summary()
        logs = AdminService.get_recent_logs()

        # Log admin access to AuditLog
        AuditLog.objects.create(
            admin=request.user,
            action="dashboard_view",
            description="Viewed Admin Dashboard Summary KPIs",
            ip_address=request.META.get("REMOTE_ADDR")
        )

        return Response({
            "metrics": summary,
            "logs": logs
        }, status=status.HTTP_200_OK)


class AdminUserViewSet(viewsets.ModelViewSet):
    """
    CRUD + Actions for managing users.
    GET /api/admin/users/
    """
    serializer_class = AdminUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]
    queryset = User.objects.all().order_by("-date_joined")

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", "")
        role_filter = self.request.query_params.get("role", "")
        status_filter = self.request.query_params.get("is_active", "")

        if search_query:
            queryset = queryset.filter(
                email__icontains=search_query
            ) | queryset.filter(
                username__icontains=search_query
            ) | queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            )

        if role_filter:
            queryset = queryset.filter(role=role_filter)

        if status_filter:
            is_active = status_filter.lower() == "true"
            queryset = queryset.filter(is_active=is_active)

        return queryset

    @action(detail=True, methods=["post"], url_path="suspend")
    def suspend_user(self, request, pk=None):
        """POST /api/admin/users/<id>/suspend/"""
        user = self.get_object()
        if user == request.user:
            return Response({"error": "You cannot suspend yourself."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()

        AuditLog.objects.create(
            admin=request.user,
            action="user_suspend",
            target_user=user,
            description=f"Suspended user account: {user.email}",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response({"message": f"User {user.email} suspended successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate_user(self, request, pk=None):
        """POST /api/admin/users/<id>/activate/"""
        user = self.get_object()
        user.is_active = True
        user.save()

        AuditLog.objects.create(
            admin=request.user,
            action="user_activate",
            target_user=user,
            description=f"Activated user account: {user.email}",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response({"message": f"User {user.email} activated successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reset-profile")
    def reset_profile(self, request, pk=None):
        """POST /api/admin/users/<id>/reset-profile/"""
        user = self.get_object()
        # Delete related resumes and portfolios to clear profile data
        user.resumes.all().delete()
        if hasattr(user, 'profile'):
            user.profile.portfolios.all().delete()
            # clear summary
            user.profile.summary = ""
            user.profile.headline = ""
            user.profile.save()

        AuditLog.objects.create(
            admin=request.user,
            action="user_reset_profile",
            target_user=user,
            description=f"Reset resume/portfolio profile for user: {user.email}",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response({"message": f"Profile and resumes for user {user.email} reset successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="export-data")
    def export_user_data(self, request, pk=None):
        """GET /api/admin/users/<id>/export-data/"""
        user = self.get_object()
        data = {
            "user": AdminUserSerializer(user).data,
            "resumes": [
                {
                    "title": r.resume_title,
                    "size": r.file_size,
                    "parsing_status": r.parsing_status,
                    "completion": r.completion_percentage,
                }
                for r in user.resumes.all()
            ],
            "portfolios": [
                {
                    "theme": p.theme,
                    "slug": p.slug,
                    "views": p.views,
                    "downloads": p.downloads,
                }
                for p in (user.profile.portfolios.all() if hasattr(user, 'profile') else [])
            ]
        }

        AuditLog.objects.create(
            admin=request.user,
            action="user_export_data",
            target_user=user,
            description=f"Exported data dump for user: {user.email}",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response(data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "You cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)

        email = user.email
        super().destroy(request, *args, **kwargs)

        AuditLog.objects.create(
            admin=request.user,
            action="user_delete",
            description=f"Permanently deleted user: {email}",
            ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response({"message": f"User {email} deleted permanently."}, status=status.HTTP_200_OK)


class AdminAnalyticsView(views.APIView):
    """GET /api/admin/analytics/ - Growth charts, distributions, and skills insights."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        growth = AnalyticsService.get_user_growth_trend()
        ats_dist = AnalyticsService.get_ats_score_distribution()
        insights = AnalyticsService.get_industry_insights()

        return Response({
            "growth": growth,
            "ats_distribution": ats_dist,
            "insights": insights
        }, status=status.HTTP_200_OK)


class AdminSystemView(views.APIView):
    """GET /api/admin/system/ - Real-time CPU, RAM, Disk, DB connectivity health."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        health = MonitoringService.get_system_health()
        return Response(health, status=status.HTTP_200_OK)


class AdminReportsView(views.APIView):
    """GET /api/admin/reports/ - Table statistics of ATS, Resume, and Usage logs."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def get(self, request):
        # We can expose general analytics aggregates for the reports UI grid
        recent_uploads = Resume.objects.select_related("user").order_by("-upload_date")[:50]
        recent_portfolios = Portfolio.objects.select_related("profile__user").order_by("-created_at")[:50]
        recent_ats = ATSScore.objects.select_related("resume", "resume__user").order_by("-ats_completed_at")[:50]

        return Response({
            "resumes": [
                {
                    "id": str(r.id),
                    "email": r.user.email,
                    "title": r.resume_title,
                    "status": r.parsing_status,
                    "date": r.upload_date.isoformat(),
                    "size": r.file_size
                }
                for r in recent_uploads
            ],
            "portfolios": [
                {
                    "id": str(p.id),
                    "email": p.profile.user.email,
                    "slug": p.slug,
                    "theme": p.theme,
                    "views": p.views,
                    "downloads": p.downloads,
                    "shares": p.shares,
                    "date": p.created_at.isoformat()
                }
                for p in recent_portfolios
            ],
            "ats": [
                {
                    "id": str(a.id),
                    "email": a.resume.user.email,
                    "title": a.resume.resume_title,
                    "score": float(a.ats_score),
                    "duration": a.ats_processing_time,
                    "date": a.ats_completed_at.isoformat()
                }
                for a in recent_ats
            ]
        }, status=status.HTTP_200_OK)


class AdminExportView(views.APIView):
    """POST /api/admin/export/ - Download reports in CSV format."""
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    def post(self, request):
        report_type = request.data.get("report_type", "users")
        csv_data = ReportingService.generate_csv_report(report_type)

        AuditLog.objects.create(
            admin=request.user,
            action=f"export_{report_type}",
            description=f"Exported CSV report for {report_type}",
            ip_address=request.META.get("REMOTE_ADDR")
        )

        response = HttpResponse(csv_data, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{report_type}_report_{int(time.time())}.csv"'
        return response
