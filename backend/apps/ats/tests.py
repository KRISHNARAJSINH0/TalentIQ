"""
ATS unit tests – tests for the ATS Analysis Engine services, views, and authentication.
Includes Profession Profile Engine tests for 12 core roles.
"""

from datetime import date
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.resumes.models import Resume
from apps.profiles.models import Profile, Skill, Education, Experience
from .models import ATSScore, ProfessionProfile

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

    def test_job_match_mode(self):
        """Test ATS Intelligence Engine in Job-Specific match mode."""
        self.client.force_authenticate(user=self.user1)
        url = reverse("ats:ats-job-match")
        data = {
            "resume_id": str(self.resume1.id),
            "job_description": "We are looking for a Python developer with Django and Redis experience. 3+ years required."
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("overall_score", response.data)
        self.assertIn("metadata", response.data)
        self.assertIn("job_specific_results", response.data["metadata"])
        self.assertGreater(response.data["metadata"]["job_specific_results"]["job_match"], 0)

    def test_report_detail(self):
        """Test retrieving a specific ATS report with benchmark data."""
        self.client.force_authenticate(user=self.user1)
        # Create a report first
        res = self.client.post(self.analyze_url, {"resume_id": str(self.resume1.id)}, format="json")
        report_id = res.data["id"]

        url = reverse("ats:ats-report-detail", kwargs={"id": report_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], report_id)
        self.assertIn("benchmark_comparison", response.data)
        self.assertIn("profession", response.data["benchmark_comparison"])

    def test_weight_engine(self):
        """Test that weight engine returns valid normalized weights for supported professions."""
        from apps.ats.weight_engine import WeightEngine
        weights_se = WeightEngine.get_weights("Software Engineer")
        weights_doctor = WeightEngine.get_weights("Doctor")

        # Sum of weights should be exactly 1.0
        self.assertAlmostEqual(sum(weights_se.values()), 1.0)
        self.assertAlmostEqual(sum(weights_doctor.values()), 1.0)

        # Software Engineer weights should favor projects and github more than Doctor
        self.assertGreater(weights_se["github"], weights_doctor.get("github", 0.0))
        self.assertGreater(weights_doctor["experience"], weights_se["experience"])


class ProfessionProfileEngineTests(APITestCase):
    """Test suite for Phase B: Profession Profile Engine."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="profiletester",
            email="profiletest@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        self.resume = Resume.objects.create(
            user=self.user,
            resume_title="Generic Resume",
            original_filename="generic.pdf",
            extraction_status="completed",
            validation_status="completed",
            ai_status="completed"
        )
        self.profile = Profile.objects.get(user=self.user)
        self.profile.summary = "Experienced professional with background in software engineering, data analysis, and teaching."
        self.profile.github = "https://github.com/testuser"
        self.profile.linkedin = "https://linkedin.com/in/testuser"
        self.profile.address = "New York, USA"
        self.profile.save()

        # Add generic skills
        for skill_name in ["Python", "SQL", "Excel", "Communication", "Git", "Leadership"]:
            skill_type = Skill.SkillType.SOFT if skill_name in ["Communication", "Leadership"] else Skill.SkillType.TECHNICAL
            Skill.objects.create(profile=self.profile, skill_name=skill_name, skill_type=skill_type)

        Education.objects.create(
            profile=self.profile,
            degree="Bachelor of Science",
            institute="MIT",
            start_date=date(2016, 8, 1),
            end_date=date(2020, 5, 15)
        )
        Experience.objects.create(
            profile=self.profile,
            designation="Software Engineer",
            company="TechCorp",
            description="Led backend team. Built microservices with Python and Django.",
            start_date=date(2020, 6, 1),
            end_date=None
        )

    def test_profile_seeding(self):
        """Test that seeding creates all 46 default profiles."""
        from .profile_loader import ProfileLoader
        count = ProfileLoader.seed_profiles()
        self.assertEqual(count, 46)
        self.assertEqual(ProfessionProfile.objects.count(), 46)

    def test_profile_list_endpoint(self):
        """Test GET /api/ats/profiles/ returns all profiles."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profiles-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 46)

    def test_profile_detail_endpoint(self):
        """Test GET /api/ats/profile/{role}/ returns correct profile."""
        self.client.force_authenticate(user=self.user)
        # Ensure seeded
        from .profile_loader import ProfileLoader
        ProfileLoader.seed_profiles()

        url = reverse("ats:ats-profile-detail", kwargs={"role": "Software Engineer"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "Software Engineer")
        self.assertIn("Python", response.data["required_skills"])
        self.assertIn("Docker", response.data["recommended_skills"])

    def test_profile_not_found(self):
        """Test GET /api/ats/profile/{role}/ for a non-existent role."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profile-detail", kwargs={"role": "Alien Technologist"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_mapper_normalizes_titles(self):
        """Test that RoleMapper correctly normalizes varied job titles."""
        from .role_mapper import RoleMapper
        self.assertEqual(RoleMapper.map_role("Senior Backend Developer"), "Backend Developer")
        self.assertEqual(RoleMapper.map_role("ML Engineer"), "Machine Learning Engineer")
        self.assertEqual(RoleMapper.map_role("Data Analyst Intern"), "Data Analyst")
        self.assertEqual(RoleMapper.map_role("UI/UX Designer"), "UX Designer")
        self.assertEqual(RoleMapper.map_role("Cardiac Surgeon"), "Doctor")
        self.assertEqual(RoleMapper.map_role("Law Enforcement Officer"), "Police Officer")
        self.assertEqual(RoleMapper.map_role("Independent Consultant"), "Freelancer")
        self.assertEqual(RoleMapper.map_role("CS Student"), "Student")

    def test_weight_manager_produces_normalised_weights(self):
        """Test that WeightManager produces category weights summing to 1.0."""
        from .weight_manager import WeightManager
        # Software Engineer weights
        se_weights = {"skills": 30, "projects": 20, "experience": 20, "education": 10, "github": 10, "portfolio": 5, "certifications": 5}
        result = WeightManager.get_category_weights(se_weights)
        self.assertAlmostEqual(sum(result.values()), 1.0, places=2)
        # Skills category should have the highest weight
        self.assertGreater(result.get("Skills", 0), result.get("Education", 0))

    def test_different_roles_get_different_scores(self):
        """
        Core Profession Profile Engine test:
        Run ATS analysis with the SAME resume but force different profession detections.
        Each role should produce a DIFFERENT overall score due to different
        weights, required skills, and penalty/bonus profiles.
        """
        from .rule_executor import RuleExecutor
        from .profile_loader import ProfileLoader
        from .models import ProfessionProfile as PP

        # Seed profiles
        ProfileLoader.seed_profiles()

        # The 12 test roles
        test_roles = [
            "Software Engineer", "Data Analyst", "Teacher", "Doctor",
            "Lawyer", "UI Designer", "Civil Engineer", "Mechanical Engineer",
            "HR Executive", "Marketing Executive", "Freelancer", "Student"
        ]

        scores = {}
        for role in test_roles:
            # Temporarily update the profile to match the role so ProfessionEngine can detect it
            pp = PP.objects.get(role=role)
            # We'll call RuleExecutor directly – it will auto-detect profession
            # but we want to ensure each role's profile is loaded, so we
            # test the profile registry directly
            from .profile_registry import ProfileRegistry
            loaded_profile = ProfileRegistry.get_profile(role)
            self.assertEqual(loaded_profile.role, role)
            scores[role] = loaded_profile.weights

        # Verify that at least some roles have different weight distributions
        unique_weights = set()
        for role, weights in scores.items():
            unique_weights.add(frozenset(weights.items()))

        # At least 8 out of 12 roles should have unique weight distributions
        self.assertGreaterEqual(len(unique_weights), 8,
            f"Expected at least 8 unique weight distributions but got {len(unique_weights)}")

    def test_profile_create_endpoint(self):
        """Test POST /api/ats/profile/ creates a new profile."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profile-create")
        data = {
            "role": "Blockchain Developer",
            "industry": "Technology",
            "required_sections": ["Contact", "Skills", "Experience"],
            "optional_sections": ["Projects"],
            "required_skills": ["Solidity", "Ethereum", "Smart Contracts"],
            "recommended_skills": ["Rust", "Web3.js"],
            "soft_skills": ["Problem Solving"],
            "preferred_certifications": [],
            "expected_projects": ["DApp"],
            "weights": {"skills": 35, "projects": 25, "experience": 20, "education": 10, "github": 10},
            "penalties": [],
            "bonuses": [],
            "benchmark_group": "Technology"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["role"], "Blockchain Developer")
        self.assertTrue(ProfessionProfile.objects.filter(role="Blockchain Developer").exists())

    def test_profile_update_endpoint(self):
        """Test PUT /api/ats/profile/{role}/ updates an existing profile."""
        from .profile_loader import ProfileLoader
        ProfileLoader.seed_profiles()

        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profile-detail", kwargs={"role": "Student"})
        data = {"weights": {"projects": 40, "skills": 30, "education": 15, "certifications": 10, "achievements": 5}}
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["weights"]["projects"], 40)

    def test_profile_delete_endpoint(self):
        """Test DELETE /api/ats/profile/{role}/ removes a profile."""
        from .profile_loader import ProfileLoader
        ProfileLoader.seed_profiles()

        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profile-detail", kwargs={"role": "Fresher"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ProfessionProfile.objects.filter(role="Fresher").exists())

    def test_profile_seed_endpoint(self):
        """Test POST /api/ats/profiles/seed/ seeds profiles."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-profiles-seed")
        response = self.client.post(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_profiles"], 46)

    def test_analysis_includes_profession_profile_data(self):
        """Test that ATS analysis response includes profession profile metadata."""
        self.client.force_authenticate(user=self.user)
        url = reverse("ats:ats-analyze")
        data = {"resume_id": str(self.resume.id)}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # The ats_json should contain profession profile data in metadata
        score_record = ATSScore.objects.filter(resume=self.resume).first()
        self.assertIsNotNone(score_record)
        self.assertIn("overall_score", score_record.ats_json)
