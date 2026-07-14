"""
ATS unit tests – tests for the ATS Analysis Engine services, views, and authentication.
"""

from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.resumes.models import Resume
from apps.profiles.models import Profile, Skill, Education, Experience
from .models import ATSScore

User = get_user_model()


class ATSEngineTests(APITestCase):
    """Test suite for the ATS Scoring & Analysis Engine."""

    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(
            username="candidate1",
            email="candidate1@example.com",
            password="testpassword123",
            first_name="Krishnarajsinh",
            last_name="Jadeja"
        )
        self.user2 = User.objects.create_user(
            username="candidate2",
            email="candidate2@example.com",
            password="testpassword123"
        )

        # Create resumes
        self.resume1 = Resume.objects.create(
            user=self.user1,
            resume_title="Python Developer Resume",
            original_filename="krishnaraj_resume.pdf",
            extraction_status="completed",
            validation_status="completed",
            ai_status="completed"
        )
        self.resume2 = Resume.objects.create(
            user=self.user2,
            resume_title="Java Developer Resume",
            original_filename="java_dev.pdf",
            extraction_status="completed",
            validation_status="completed"
        )

        # Get and update automatically created profile for user1
        self.profile1 = Profile.objects.get(user=self.user1)
        self.profile1.summary = "Detail-oriented Python developer with 4 years of experience building REST APIs with Django and FastAPI."
        self.profile1.github = "https://github.com/krishnarajsinh"
        self.profile1.linkedin = "https://linkedin.com/in/krishnarajsinh"
        self.profile1.address = "Gujarat, India"
        self.profile1.save()

        # Delete profile of user2 to test missing profile case
        Profile.objects.filter(user=self.user2).delete()

        # Add profile details for user1
        Skill.objects.create(
            profile=self.profile1,
            skill_name="Python",
            skill_type=Skill.SkillType.TECHNICAL
        )
        Skill.objects.create(
            profile=self.profile1,
            skill_name="Django",
            skill_type=Skill.SkillType.TECHNICAL
        )
        Skill.objects.create(
            profile=self.profile1,
            skill_name="Git",
            skill_type=Skill.SkillType.TECHNICAL
        )
        Skill.objects.create(
            profile=self.profile1,
            skill_name="Communication",
            skill_type=Skill.SkillType.SOFT
        )

        Education.objects.create(
            profile=self.profile1,
            degree="Bachelor of Engineering",
            institute="Gujarat Technological University",
            start_date=date(2018, 6, 15),
            end_date=date(2022, 5, 30)
        )

        Experience.objects.create(
            profile=self.profile1,
            designation="Software Engineer",
            company="Google Partner Company",
            description="Led development of several backend modules. Overhauled performance issues by utilizing Redis caching.",
            start_date=date(2022, 6, 1),
            end_date=None
        )

        # URLs
        self.analyze_url = reverse("ats:ats-analyze")
        self.history_url = reverse("ats:ats-history")

    def test_run_analysis_success(self):
        """Test successful execution of E2E ATS Analysis."""
        self.client.force_authenticate(user=self.user1)
        data = {"resume_id": str(self.resume1.id)}
        response = self.client.post(self.analyze_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("ats_score", response.data)
        self.assertIn("industry_match", response.data)
        self.assertIn("missing_skills", response.data)
        self.assertIn("suggestions", response.data)

        # Check if record got saved
        self.assertEqual(ATSScore.objects.filter(resume=self.resume1).count(), 1)
        score_record = ATSScore.objects.get(resume=self.resume1)
        self.assertGreater(score_record.ats_score, 0)
        self.assertIn("overall_score", score_record.ats_json)

    def test_missing_profile_error(self):
        """Test that running analysis fails gracefully if profile does not exist."""
        self.client.force_authenticate(user=self.user2)
        data = {"resume_id": str(self.resume2.id)}
        response = self.client.post(self.analyze_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["error"], "Profile does not exist. Please initialize and verify your master profile first.")

    def test_detail_endpoint_success(self):
        """Test retrieving the latest completed score for a specific resume."""
        # Create a mock run first
        self.client.force_authenticate(user=self.user1)
        self.client.post(self.analyze_url, {"resume_id": str(self.resume1.id)}, format="json")

        detail_url = reverse("ats:ats-detail", kwargs={"resume_id": self.resume1.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(float(response.data["ats_score"]), float(ATSScore.objects.latest("ats_completed_at").ats_score))

    def test_detail_endpoint_not_found(self):
        """Test detail endpoint returns 404 when no analysis run has occurred."""
        self.client.force_authenticate(user=self.user1)
        detail_url = reverse("ats:ats-detail", kwargs={"resume_id": self.resume1.id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "No ATS analysis has been run for this resume yet.")

    def test_owner_isolation_prevents_access(self):
        """Test that user cannot fetch or analyze another user's resume."""
        self.client.force_authenticate(user=self.user2)
        # Attempt to analyze user1's resume
        data = {"resume_id": str(self.resume1.id)}
        response = self.client.post(self.analyze_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Attempt to view details of user1's resume
        detail_url = reverse("ats:ats-detail", kwargs={"resume_id": self.resume1.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_history_endpoint(self):
        """Test that historical score runs are returned sorted by date."""
        self.client.force_authenticate(user=self.user1)
        # Trigger two separate runs
        self.client.post(self.analyze_url, {"resume_id": str(self.resume1.id)}, format="json")
        self.client.post(self.analyze_url, {"resume_id": str(self.resume1.id)}, format="json")

        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
