from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AdminDashboardView,
    AdminUserViewSet,
    AdminAnalyticsView,
    AdminSystemView,
    AdminReportsView,
    AdminExportView,
)

router = DefaultRouter()
router.register(r"users", AdminUserViewSet, basename="admin-users")

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("analytics/", AdminAnalyticsView.as_view(), name="admin-analytics"),
    path("system/", AdminSystemView.as_view(), name="admin-system"),
    path("reports/", AdminReportsView.as_view(), name="admin-reports"),
    path("export/", AdminExportView.as_view(), name="admin-export"),
    path("", include(router.urls)),
]
