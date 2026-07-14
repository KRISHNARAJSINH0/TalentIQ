from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.resumes.models import Resume
from apps.profiles.models import Profile, Skill, Experience, Project, Certification
from apps.ats.models import ATSScore
from apps.portfolio.models import Portfolio
from apps.timeline.models import TimelineEvent, ResumeVersion, SkillHistory, ATSHistory, CareerProgress, LearningHistory
from apps.timeline.services import TimelineService, VersionService, ComparisonService, GrowthAnalyticsService

User = get_user_model()


class TimelineTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="timetest",
            email="time@test.com",
            password="TimePass123!"
        )
        self.client.force_authenticate(user=self.user)
        # Profile is auto-created by signal

    def test_log_event_service(self):
        event = TimelineService.log_event(
            user=self.user,
            event_type=TimelineEvent.EventType.THEME_CHANGED,
            title="Theme updated",
            description="Changed theme to Dark Mode",
            metadata={"theme": "dark"}
        )
        self.assertEqual(event.event_type, TimelineEvent.EventType.THEME_CHANGED)
        self.assertEqual(event.title, "Theme updated")
        self.assertEqual(TimelineEvent.objects.filter(user=self.user).count(), 1)

    def test_create_custom_event_api(self):
        url = reverse("timeline:timeline-event-create")
        data = {
            "event_type": "theme_changed",
            "title": "API Log Theme",
            "description": "Log test",
            "metadata": {"val": 123}
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "API Log Theme")

    def test_timeline_list_api(self):
        TimelineService.log_event(self.user, TimelineEvent.EventType.SKILL_ADDED, "Skill 1")
        TimelineService.log_event(self.user, TimelineEvent.EventType.SKILL_ADDED, "Skill 2")

        url = reverse("timeline:timeline-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_resume_save_signal(self):
        # Initial create
        resume = Resume.objects.create(
            user=self.user,
            resume_title="Developer CV 2026",
            file_size=1024,
            is_active=True
        )
        # Triggers post_save: logs 'Resume Uploaded' event and creates ResumeVersion
        self.assertTrue(TimelineEvent.objects.filter(event_type=TimelineEvent.EventType.RESUME_UPLOADED).exists())
        self.assertEqual(ResumeVersion.objects.filter(user=self.user).count(), 1)

    def test_skill_signals(self):
        profile = Profile.objects.get(user=self.user)
        skill = Skill.objects.create(
            profile=profile,
            skill_name="Docker",
            skill_level=Skill.SkillLevel.ADVANCED,
            skill_type=Skill.SkillType.TECHNICAL
        )
        # Skill Added log
        self.assertTrue(TimelineEvent.objects.filter(event_type=TimelineEvent.EventType.SKILL_ADDED).exists())
        self.assertTrue(SkillHistory.objects.filter(user=self.user, skill_name="Docker", is_active=True).exists())

        # Delete skill
        skill.delete()
        self.assertTrue(TimelineEvent.objects.filter(event_type=TimelineEvent.EventType.SKILL_REMOVED).exists())
        self.assertFalse(SkillHistory.objects.filter(user=self.user, skill_name="Docker", is_active=True).exists())

    def test_comparison_service(self):
        v1 = VersionService.create_version(self.user, summary="V1")
        
        # Add skill & experience, generate V2
        profile = Profile.objects.get(user=self.user)
        Skill.objects.create(profile=profile, skill_name="Kubernetes")
        Experience.objects.create(
            profile=profile,
            company="Google",
            designation="Staff Architect",
            start_date=timezone.now().date()
        )
        v2 = VersionService.create_version(self.user, summary="V2")

        comparison = ComparisonService.compare_versions(v1, v2)
        self.assertIn("Kubernetes", comparison["diff_v1_v2"]["added_skills"])
        self.assertEqual(len(comparison["diff_v1_v2"]["new_experience"]), 1)
        self.assertEqual(comparison["diff_v1_v2"]["new_experience"][0]["company"], "Google")

    def test_analytics_and_history_api(self):
        # Create some progress records
        CareerProgress.objects.create(
            user=self.user,
            career_score=85.0,
            growth_score=90.0,
            learning_score=70.0,
            market_alignment=80.0
        )
        LearningHistory.objects.create(
            user=self.user,
            topic="System Design",
            progress=100,
            status="Completed"
        )
        url = reverse("timeline:timeline-history")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["career_trends"]), 1)
        self.assertEqual(len(response.data["learning_progress"]), 1)
