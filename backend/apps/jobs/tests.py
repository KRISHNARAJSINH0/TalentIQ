from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.resumes.models import Resume
from apps.profiles.models import Profile, Skill, Experience
from .models import JobRecommendation, SkillGap
from .services.role_predictor import RolePredictor

User = get_user_model()


class JobIntelligenceTests(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            email="testuser@example.com"
        )
        self.client.force_authenticate(user=self.user)

        # Create resume record
        self.resume = Resume.objects.create(
            user=self.user,
            original_filename="resume.pdf",
            validation_status="completed",
            is_active=True
        )

        # Fetch auto-created profile from signal and update
        self.profile = Profile.objects.get(user=self.user)
        self.profile.summary = "A test profile"
        self.profile.is_verified = True
        self.profile.save()

    def test_role_predictor_fallback(self):
        """
        Verify the local predictor maps skills/headlines to correct roles.
        """
        roles_to_test = [
            {"skills": ["python", "django", "postgres"], "headline": "Backend dev", "expected": "Backend Engineer"},
            {"skills": ["pytorch", "tensorflow", "deep learning"], "headline": "AI researcher", "expected": "ML Engineer"},
            {"skills": ["autocad", "revit", "civil structural"], "headline": "Civil design manager", "expected": "Civil Engineer"},
            {"skills": ["patient care", "clinical diagnostic", "mbbs"], "headline": "General Practitioner", "expected": "Doctor"},
            {"skills": ["classroom", "lesson planning", "pedagogy"], "headline": "High School Instructor", "expected": "Teacher"},
            {"skills": ["litigation", "legal contract drafting", "compliance"], "headline": "Corporate Counsel", "expected": "Lawyer"},
            {"skills": ["figma", "wireframing", "ui ux designer"], "headline": "Product Designer", "expected": "UI UX Designer"},
            {"skills": ["powerbi", "sql", "excel formulas"], "headline": "Business Analyst", "expected": "Data Analyst"},
            {"skills": ["scientific writing", "experimental design", "spss"], "headline": "R&D Scientist", "expected": "Researcher"},
            {"skills": ["seo optimization", "copywriting", "brand marketing"], "headline": "Growth Marketer", "expected": "Marketing Manager"},
            {"skills": ["recruiting", "talent sourcing", "onboarding"], "headline": "HR Generalist", "expected": "HR Specialist"},
            {"skills": ["quickbooks", "tax compliance", "bookkeeper"], "headline": "Chartered Accountant", "expected": "Accountant"},
            {"skills": ["student intern", "university studies"], "headline": "Undergrad intern", "expected": "Student"},
            {"skills": ["freelance consultant", "independent contractor"], "headline": "Independent Consultant", "expected": "Freelancer"},
        ]

        for case in roles_to_test:
            mock_profile = {
                "headline": case["headline"],
                "skills": [{"skill_name": s} for s in case["skills"]],
                "experiences": []
            }
            predicted = RolePredictor.predict_role(mock_profile)
            self.assertEqual(predicted, case["expected"], f"Failed for {case['headline']}")

    def test_job_match_view(self):
        """
        Verify the POST /api/jobs/match/ view triggers calculation and saves to database.
        """
        # Create some skills and experience to match
        Skill.objects.create(profile=self.profile, skill_name="Python")
        Skill.objects.create(profile=self.profile, skill_name="Django")
        Experience.objects.create(
            profile=self.profile,
            company="Google",
            designation="Software Engineer",
            start_date="2020-01-01",
            description="Developing backend solutions using Python."
        )

        url = reverse("jobs:match")
        response = self.client.post(url, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("predicted_role", response.data)
        self.assertIn("recommended_jobs", response.data)
        
        # Verify database objects were persisted
        self.assertTrue(JobRecommendation.objects.filter(resume=self.resume).exists())
        self.assertTrue(SkillGap.objects.filter(resume=self.resume).exists())

    def test_job_predict_view(self):
        """
        Verify POST /api/jobs/predict/ accepts custom payload and returns matching predictions.
        """
        url = reverse("jobs:predict")
        custom_payload = {
            "payload": {
                "headline": "Doctor",
                "skills": [{"skill_name": "Clinical Diagnosis"}, {"skill_name": "Patient Care"}],
                "experiences": []
            }
        }
        response = self.client.post(url, custom_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["predicted_role"], "Doctor")

    def test_get_recommendations_endpoint(self):
        """
        Verify GET /api/jobs/recommendations/ returns list of recommendations.
        """
        url = reverse("jobs:recommendations")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0) # Triggered auto-generation

    def test_get_skills_gap_endpoint(self):
        """
        Verify GET /api/jobs/skills-gap/ returns gaps list.
        """
        url = reverse("jobs:skills-gap")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("gaps", response.data)
        self.assertIn("recommendations", response.data)
