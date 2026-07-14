from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from datetime import timedelta

# pyrefly: ignore [missing-import]
from apps.resumes.models import Resume
# pyrefly: ignore [missing-import]
from apps.ats.models import ATSScore
from .models import Notification, NotificationPreference, Reminder, Digest
from .services import NotificationService, DigestService, ReminderService

User = get_user_model()


class NotificationsTestCase(APITestCase):
    """Test cases for the Notifications Platform."""

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username="userone",
            email="one@test.com",
            password="password123",
            first_name="User",
            last_name="One"
        )
        self.user2 = User.objects.create_user(
            username="usertwo",
            email="two@test.com",
            password="password123",
            first_name="User",
            last_name="Two"
        )

        # Create some notifications
        self.notif1 = Notification.objects.create(
            user=self.user1,
            title="Resume Uploaded",
            message="Test upload message",
            type=Notification.Type.RESUME_UPLOADED,
            priority=Notification.Priority.NORMAL
        )
        self.notif2 = Notification.objects.create(
            user=self.user2,
            title="ATS Score Improved",
            message="Test ATS message",
            type=Notification.Type.ATS_IMPROVED,
            priority=Notification.Priority.HIGH
        )

        # URLs
        self.list_url = reverse("notification-list")
        self.read_url = reverse("notification-read")
        self.delete_url = reverse("notification-delete-bulk")
        self.pref_url = reverse("notification-preferences")
        self.unread_url = reverse("notification-unread")

    def test_delete_notification(self):
        """Deleting a notification removes it from database."""
        self.client.force_authenticate(user=self.user1)
        # Delete using single endpoint <int:pk>/
        single_delete_url = reverse("notification-delete", kwargs={"pk": self.notif1.id})
        response = self.client.delete(single_delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Notification.objects.filter(id=self.notif1.id).exists())

        # Verify bulk delete
        notif_temp = Notification.objects.create(
            user=self.user1,
            title="Temp Notif",
            message="Message",
            type=Notification.Type.CAREER_SUGGESTION
        )
        response = self.client.post(self.delete_url, {"id": notif_temp.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Notification.objects.filter(id=notif_temp.id).exists())

    def test_anonymous_access_denied(self):
        """Anonymous requests must be rejected."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_own_notifications(self):
        """Users must only be allowed to view their own notifications."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data.get("results", response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Resume Uploaded")

    def test_mark_as_read(self):
        """Marking a notification as read updates status and count."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(self.read_url, {"id": self.notif1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.read)

        # Verify unread count is 0
        response = self.client.get(self.unread_url)
        self.assertEqual(response.data["unread_count"], 0)

    def test_update_preferences(self):
        """Updating preferences saves correctly."""
        self.client.force_authenticate(user=self.user1)
        # Fetch preferences
        response = self.client.get(self.pref_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["enable_email"])

        # Change preference
        response = self.client.post(self.pref_url, {"enable_email": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["enable_email"])

        pref = NotificationPreference.objects.get(user=self.user1)
        self.assertFalse(pref.enable_email)

    def test_automated_signal_trigger(self):
        """Saving an ATSScore must trigger a notification automatically via signals."""
        # Create a resume first
        resume = Resume.objects.create(
            user=self.user1,
            resume_title="Developer CV",
            extracted_text="Developer background details...",
            file_size=2048,
            parsing_status="completed"
        )

        # Verify resume uploaded signal created a notification
        self.assertTrue(Notification.objects.filter(
            user=self.user1,
            type=Notification.Type.RESUME_UPLOADED
        ).exists())

        # Generate ATS Score
        ATSScore.objects.create(
            resume=resume,
            ats_score=85.0,
            ats_json={},
            industry_match={},
            missing_skills=[],
            suggestions={},
            ats_processing_time=1.5
        )

        # Verify ATS signal created a notification
        self.assertTrue(Notification.objects.filter(
            user=self.user1,
            type=Notification.Type.ATS_IMPROVED
        ).exists())

    def test_weekly_digest_service(self):
        """DigestService generates a summary digest model and sends an alert."""
        digest = DigestService.generate_digest(self.user1, digest_type="weekly")
        self.assertIsNotNone(digest)
        self.assertEqual(digest.digest_type, "weekly")
        
        # Verify weekly report notification exists
        self.assertTrue(Notification.objects.filter(
            user=self.user1,
            type=Notification.Type.WEEKLY_REPORT
        ).exists())
