from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.ats.models import ATSScore
from apps.resumes.models import Resume
from .models import AuditLog

User = get_user_model()


class AdminIntelligenceTests(APITestCase):
    """Test suite for Admin Intelligence dashboard permissions and analytics API endpoints."""

    def setUp(self):
        # Create normal user
        self.user = User.objects.create_user(
            username="normaluser",
            email="normal@test.com",
            password="testpassword123",
            first_name="Normal",
            last_name="User",
            role=User.Role.USER
        )

        # Create admin user
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@test.com",
            password="adminpassword123",
            first_name="Admin",
            last_name="User",
            role=User.Role.ADMIN
        )

        # URLs
        self.dashboard_url = reverse("admin-dashboard")
        self.analytics_url = reverse("admin-analytics")
        self.system_url = reverse("admin-system")
        self.reports_url = reverse("admin-reports")
        self.export_url = reverse("admin-export")
        self.users_list_url = reverse("admin-users-list")

    def test_unauthenticated_access_blocked(self):
        """Verify anonymous requests are rejected."""
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_non_admin_access_blocked(self):
        """Verify normal role users are forbidden from viewing admin endpoints."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.get(self.users_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_access_allowed(self):
        """Verify authorized admin role users can view dashboard stats successfully."""
        self.client.force_authenticate(user=self.admin_user)
        
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("metrics", response.data)
        self.assertIn("logs", response.data)

        # Verify audit log was created
        self.assertTrue(AuditLog.objects.filter(admin=self.admin_user, action="dashboard_view").exists())

    def test_user_management_search(self):
        """Verify searching user database returns correct matches."""
        self.client.force_authenticate(user=self.admin_user)

        # Search for normal user
        response = self.client.get(self.users_list_url, {"search": "normal"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that result matches search query
        results = response.data.get("results", response.data)
        self.assertTrue(len(results) >= 1)
        self.assertEqual(results[0]["email"], "normal@test.com")

    def test_suspend_user_action(self):
        """Verify toggling active status on users succeeds."""
        self.client.force_authenticate(user=self.admin_user)
        
        suspend_url = reverse("admin-users-suspend-user", kwargs={"pk": str(self.user.id)})
        response = self.client.post(suspend_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check model state changed
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

    def test_reports_export(self):
        """Verify downloading CSV statistics report works."""
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.export_url, {"report_type": "users"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("attachment", response["Content-Disposition"])
