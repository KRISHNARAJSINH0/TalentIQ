from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# pyrefly: ignore [missing-import]
from apps.profiles.models import Profile
# pyrefly: ignore [missing-import]
from .models import CareerProfile, CoverLetter, LearningProgressLog

User = get_user_model()


class CareerAssistantTests(APITestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password="securepassword123",
            first_name="Jane",
            last_name="Doe"
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # URLs
        self.analyze_url = reverse("career:career-analyze")
        self.detail_url = reverse("career:career-detail")
        self.roadmap_url = reverse("career:career-roadmap")
        self.skills_url = reverse("career:career-skills")
        self.cover_letter_url = reverse("career:career-cover-letter")
        self.history_url = reverse("career:career-history")
        self.progress_url = reverse("career:career-progress")

    def test_analyze_without_profile(self):
        # Delete auto-created profile to trigger Profile.DoesNotExist
        Profile.objects.filter(user=self.user).delete()
        response = self.client.post(self.analyze_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No professional profile found", response.data["error"])

    def test_analyze_unverified_profile(self):
        # Update existing auto-created profile to be unverified
        profile = Profile.objects.get(user=self.user)
        profile.headline = "Software Engineer"
        profile.is_verified = False
        profile.save()
        
        response = self.client.post(self.analyze_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("not verified yet", response.data["error"])

    def test_career_lifecycle_verified(self):
        # 1. Update existing profile to be verified
        profile = Profile.objects.get(user=self.user)
        profile.headline = "Software Engineer"
        profile.is_verified = True
        profile.save()

        # pyrefly: ignore [missing-import]
        from apps.profiles.models import Skill
        Skill.objects.create(
            profile=profile,
            skill_name="Python",
            skill_type="technical"
        )
        Skill.objects.create(
            profile=profile,
            skill_name="SQL",
            skill_type="technical"
        )

        # 2. Trigger profile analysis
        response = self.client.post(self.analyze_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("career_readiness", response.data)
        self.assertIn("career_json", response.data)
        self.assertIn("roadmap_json", response.data)

        # 3. Retrieve details
        detail_res = self.client.get(self.detail_url)
        self.assertEqual(detail_res.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_res.data["career_readiness"], response.data["career_readiness"])

        # 4. Retrieve roadmap milestones
        roadmap_res = self.client.get(self.roadmap_url)
        self.assertEqual(roadmap_res.status_code, status.HTTP_200_OK)
        self.assertIn("milestones", roadmap_res.data)

        # 5. Retrieve skill gaps
        skills_res = self.client.get(self.skills_url)
        self.assertEqual(skills_res.status_code, status.HTTP_200_OK)
        self.assertIn("current_skills", skills_res.data)
        self.assertIn("missing_skills", skills_res.data)

        # 6. Update progress checklist item
        # Get one milestone and item name from roadmap
        milestone = roadmap_res.data["milestones"][0]
        m_title = milestone["milestone_title"]
        item_name = milestone["items"][0]["name"]

        progress_res = self.client.patch(self.progress_url, {
            "milestone_title": m_title,
            "item_name": item_name,
            "is_completed": True
        })
        self.assertEqual(progress_res.status_code, status.HTTP_200_OK)
        self.assertTrue(progress_res.data["is_completed"])

        # Check that it reflects in roadmap GET request
        roadmap_updated = self.client.get(self.roadmap_url)
        item_updated = roadmap_updated.data["milestones"][0]["items"][0]
        self.assertTrue(item_updated["is_completed"])

    def test_generate_cover_letter(self):
        # Update existing profile to be verified
        profile = Profile.objects.get(user=self.user)
        profile.headline = "Software Engineer"
        profile.is_verified = True
        profile.save()

        payload = {
            "company": "Stark Industries",
            "position": "AI Research Scientist",
            "job_description": "Building next-generation deep learning platforms.",
            "tone": "Startup",
            "cover_letter_type": "Job Application"
        }
        
        # Generate cover letter
        response = self.client.post(self.cover_letter_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["company"], "Stark Industries")
        self.assertEqual(response.data["position"], "AI Research Scientist")

        # Check history
        history_res = self.client.get(self.history_url)
        self.assertEqual(history_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_res.data), 1)
        self.assertEqual(history_res.data[0]["company"], "Stark Industries")
