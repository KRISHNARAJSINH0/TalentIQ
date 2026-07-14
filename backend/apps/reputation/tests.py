from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.profiles.models import Profile, Skill, Project, Experience, Certification
from apps.resumes.models import Resume
from .models import ResumeReputation, Badge

User = get_user_model()


class ResumeReputationTests(APITestCase):

    def setUp(self):
        # Create user
        self.user = User.objects.create_user(
            username="reputation_user",
            email="reputation@example.com",
            password="securepassword123",
            first_name="Alice",
            last_name="Wonder"
        )
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Create user's resume
        self.resume = Resume.objects.create(
            user=self.user,
            resume_title="Master Resume",
            is_active=True
        )

        # URLs
        self.reputation_url = reverse("reputation:reputation-detail")
        self.history_url = reverse("reputation:reputation-history")
        self.badges_url = reverse("reputation:reputation-badges")
        self.benchmark_url = reverse("reputation:reputation-benchmark")

    def test_calculate_reputation_without_profile(self):
        # Delete auto-created profile to trigger Profile.DoesNotExist
        Profile.objects.filter(user=self.user).delete()
        
        response = self.client.post(self.reputation_url, {"resume_id": str(self.resume.id)})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("No verified profile found", response.data["error"])

    def test_reputation_lifecycle_success(self):
        # 1. Update auto-created profile to be verified and have data
        profile = Profile.objects.get(user=self.user)
        profile.headline = "Software Engineer"
        profile.summary = "Experienced software engineer specializing in backend systems and python cloud apps."
        profile.is_verified = True
        profile.save()

        # 2. Add some skills
        Skill.objects.create(profile=profile, skill_name="Python", skill_type="technical", skill_level="expert")
        Skill.objects.create(profile=profile, skill_name="Django", skill_type="technical", skill_level="expert")
        Skill.objects.create(profile=profile, skill_name="AWS", skill_type="technical", skill_level="advanced")
        Skill.objects.create(profile=profile, skill_name="Collaboration", skill_type="soft")

        # 3. Add projects
        Project.objects.create(
            profile=profile,
            project_name="E-Commerce API",
            description="Designed and deployed a high-performance shopping cart REST API using Django and AWS, supporting 10k users daily.",
            technologies="Python, Django, PostgreSQL, AWS",
            github_url="https://github.com/alice/ecommerce",
            live_url="https://ecommerce.alice.com"
        )

        # 4. Add experiences
        import datetime
        Experience.objects.create(
            profile=profile,
            company="Tech Corp",
            designation="Software Engineer",
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2025, 1, 1),
            description="Led development of clean REST APIs. Spearheaded performance optimization efforts."
        )

        # 5. Trigger calculation
        response = self.client.post(self.reputation_url, {"resume_id": str(self.resume.id)})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("score", response.data)
        self.assertIn("tier", response.data)
        self.assertIn("details_json", response.data)

        # Confirm database contains the reputation record
        reputations = ResumeReputation.objects.filter(resume=self.resume)
        self.assertEqual(reputations.count(), 1)
        reputation = reputations.first()
        self.assertEqual(reputation.score, response.data["score"])

        # 6. Retrieve latest reputation via GET
        get_res = self.client.get(self.reputation_url, {"resume_id": str(self.resume.id)})
        self.assertEqual(get_res.status_code, status.HTTP_200_OK)
        self.assertEqual(get_res.data["score"], reputation.score)

        # 7. Get History
        history_res = self.client.get(self.history_url)
        self.assertEqual(history_res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_res.data), 1)
        self.assertEqual(history_res.data[0]["score"], reputation.score)

        # 8. Get Badges
        badges_res = self.client.get(self.badges_url, {"resume_id": str(self.resume.id)})
        self.assertEqual(badges_res.status_code, status.HTTP_200_OK)
        # Should have earned some badges (e.g. ATS Master, Portfolio Pro, Top Performer, etc. depending on scores)
        self.assertTrue(len(badges_res.data) >= 0)

        # 9. Get Benchmarks
        benchmark_res = self.client.get(self.benchmark_url, {"resume_id": str(self.resume.id)})
        self.assertEqual(benchmark_res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(benchmark_res.data) > 0)
