import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.resumes.models import Resume
from apps.profiles.models import (
    Profile,
    Skill,
    Education,
    Experience,
    Project,
    Certification,
    Language,
    ProfileEditHistory,
)

User = get_user_model()


class ProfileReviewAPITests(APITestCase):
    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpassword123",
            first_name="John",
            last_name="Doe",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="testpassword123",
        )
        
        # Authenticate
        self.client.force_authenticate(user=self.user)

        # Create a test resume with master_resume_json
        self.resume_data = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "+12345678901",
            "summary": "Experienced python developer.",
            "address": "123 Main St",
            "city": "Tech City",
            "state": "CA",
            "country": "USA",
            "postal_code": "90001",
            "website": "https://johndoe.com",
            "github": "https://github.com/johndoe",
            "linkedin": "https://linkedin.com/in/johndoe",
            "portfolio": "https://portfolio.johndoe.com",
            "skills": ["Python", "Django", "React"],
            "technical_skills": ["SQL", "Docker"],
            "soft_skills": ["Leadership"],
            "education": [
                {
                    "institution": "MIT",
                    "degree": "B.S. Computer Science",
                    "field_of_study": "Computer Science",
                    "start_date": "2018-09-01",
                    "end_date": "2022-06-01",
                    "grade": "4.0 GPA",
                }
            ],
            "experience": [
                {
                    "company": "Google",
                    "designation": "Software Engineer",
                    "employment_type": "full_time",
                    "start_date": "2022-07-01",
                    "end_date": None,
                    "description": "Building cool things.",
                }
            ],
            "projects": [
                {
                    "project_name": "Resume Parser",
                    "technologies": "Django, React",
                    "description": "AI parsing system.",
                    "github_url": "https://github.com/johndoe/resume-parser",
                }
            ],
            "certifications": [
                {
                    "certificate_name": "AWS Solutions Architect",
                    "organization": "Amazon Web Services",
                    "issue_date": "2023-01-15",
                }
            ],
            "languages": ["English", {"language_name": "Spanish", "proficiency": "native"}],
        }

        self.resume = Resume.objects.create(
            user=self.user,
            resume_title="Test Resume",
            validation_status="completed",
            master_resume_json=self.resume_data,
        )

    def test_get_master_profile_creates_profile(self):
        """Test GET /api/profile/master/ returns a Profile successfully."""
        # The profile is auto-created by user post_save signal
        self.assertTrue(Profile.objects.filter(user=self.user).exists())
        
        url = reverse("profiles:profile-master")
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # User details should match
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["last_name"], "Doe")
        self.assertEqual(response.data["email"], "testuser@example.com")

    def test_get_master_profile_with_resume_id(self):
        """Test GET /api/profile/master/?resume_id=<id> parses and loads data."""
        # Get existing profile that was auto-created
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.summary, "")

        url = f"{reverse('profiles:profile-master')}?resume_id={self.resume.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        
        # Profile fields should be populated
        self.assertEqual(profile.summary, "Experienced python developer.")
        self.assertEqual(profile.city, "Tech City")
        self.assertEqual(profile.linkedin, "https://linkedin.com/in/johndoe")
        
        # Related entities should be created
        self.assertEqual(profile.skills.count(), 6)  # Python, Django, React, SQL, Docker, Leadership
        self.assertEqual(profile.educations.count(), 1)
        self.assertEqual(profile.experiences.count(), 1)
        self.assertEqual(profile.projects.count(), 1)
        self.assertEqual(profile.certifications.count(), 1)
        self.assertEqual(profile.languages.count(), 2)

        # Audit logs should exist for initialization
        self.assertTrue(profile.edit_history.filter(section="profile", field_name="initialized_from_resume").exists())

    def test_put_master_profile_updates_and_logs(self):
        """Test PUT /api/profile/master/ updates profile and nested items, logging history."""
        # Get auto-created profile and set initial values
        profile = Profile.objects.get(user=self.user)
        profile.summary = "Old summary"
        profile.save()
        
        url = reverse("profiles:profile-master")
        update_payload = {
            "first_name": "Johnny",
            "last_name": "D",
            "email": "johnny@example.com",
            "phone": "+19876543210",
            "headline": "Lead Developer",
            "summary": "New summary",
            "skills": [
                {"skill_name": "Go", "skill_type": "technical", "skill_level": "advanced"}
            ],
            "educations": [],
            "experiences": [],
            "projects": [],
            "certifications": [],
            "languages": [],
            "achievements": [],
            "awards": [],
            "volunteer_work": [],
            "publications": [],
            "hobbies": [],
            "references": [],
        }
        
        response = self.client.put(url, data=update_payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify db values
        profile.refresh_from_db()
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Johnny")
        self.assertEqual(profile.headline, "Lead Developer")
        self.assertEqual(profile.summary, "New summary")
        self.assertEqual(profile.skills.count(), 1)
        self.assertEqual(profile.skills.first().skill_name, "Go")
        self.assertEqual(profile.source_of_value.get("headline"), "manual")

        # Verify audit logging
        self.assertTrue(ProfileEditHistory.objects.filter(profile=profile, section="profile", field_name="headline", new_value="Lead Developer").exists())
        self.assertTrue(ProfileEditHistory.objects.filter(profile=profile, section="skills", field_name="created_skills_item").exists())

    def test_validation_rules(self):
        """Test serializer validation constraints (email, phone, duplicates)."""
        url = reverse("profiles:profile-master")
        
        # 1. Invalid email
        payload = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email-address",
            "phone": "+1234567890",
        }
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # 2. Invalid phone
        payload["email"] = "valid@example.com"
        payload["phone"] = "abc1234"
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("phone", response.data)

        # 3. Duplicate skills in same category
        payload["phone"] = "+1234567890"
        payload["skills"] = [
            {"skill_name": "Python", "skill_type": "technical"},
            {"skill_name": "python", "skill_type": "technical"}
        ]
        response = self.client.put(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("skills", response.data)

    def test_patch_profile_section(self):
        """Test PATCH /api/profile/section/ updates a specific section."""
        profile = Profile.objects.get(user=self.user)
        profile.headline = "Old Headline"
        profile.save()
        
        url = reverse("profiles:profile-section")
        payload = {
            "section": "personal",
            "data": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "testuser@example.com",
                "headline": "New Headline",
            }
        }
        
        response = self.client.patch(url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        profile.refresh_from_db()
        self.assertEqual(profile.headline, "New Headline")

    def test_verify_profile(self):
        """Test POST /api/profile/verify/ marks section or entire profile verified."""
        profile = Profile.objects.get(user=self.user)
        self.assertFalse(profile.is_verified)
        
        url = reverse("profiles:profile-verify")
        
        # Verify whole profile
        response = self.client.post(url, data={"is_verified": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        profile.refresh_from_db()
        self.assertTrue(profile.is_verified)

        # Verify specific section log
        response = self.client.post(url, data={"section": "experience", "is_verified": True}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(ProfileEditHistory.objects.filter(profile=profile, section="experience", field_name="is_verified", new_value="True").exists())


class ProfileExportAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="exportuser",
            email="exportuser@example.com",
            password="testpassword123",
            first_name="Jane",
            last_name="Doe",
        )
        self.client.force_authenticate(user=self.user)

    def test_export_profile_verified_data(self):
        """Test GET /api/profile/export/ returns the master resume format."""
        url = reverse("profiles:profile-export")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], "Jane")
        self.assertEqual(response.data["last_name"], "Doe")
        self.assertEqual(response.data["email"], "exportuser@example.com")


