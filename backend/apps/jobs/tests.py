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


class JobATSEngineTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="candidate",
            password="candidatepassword123",
            email="candidate@example.com"
        )
        self.client.force_authenticate(user=self.user)

        self.resume = Resume.objects.create(
            user=self.user,
            original_filename="candidate_cv.pdf",
            validation_status="completed",
            is_active=True
        )

        self.profile = Profile.objects.get(user=self.user)
        self.profile.summary = "Experienced software engineer specializing in backend systems and python applications."
        self.profile.is_verified = True
        self.profile.save()

        # Add profile details
        Skill.objects.create(profile=self.profile, skill_name="Python")
        Skill.objects.create(profile=self.profile, skill_name="Django")
        Skill.objects.create(profile=self.profile, skill_name="Docker")
        Skill.objects.create(profile=self.profile, skill_name="SQL")
        Experience.objects.create(
            profile=self.profile,
            company="Previous Corp",
            designation="Software Developer",
            start_date="2021-01-01",
            end_date="2023-01-01",
            description="Built web services with Python, Django, SQL and containerized them with Docker."
        )

    def test_jd_evaluation_and_history(self):
        """
        Verify POST /api/job-ats/ evaluates the resume, saves report, and GET /api/job-ats/history/ lists it.
        """
        url = "/api/job-ats/"
        payload = {
            "job_title": "Senior backend developer",
            "job_description": "We need a Software Engineer who knows Python, Django, SQL, and Docker to build backend APIs.",
            "company_name": "Test Company"
        }
        
        # Test evaluation
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["job_title"], "Senior backend developer")
        self.assertIn("overall_match", response.data)
        self.assertIn("ats_score", response.data)
        
        # Verify history
        history_url = "/api/job-ats/history/"
        history_response = self.client.get(history_url)
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(history_response.data), 1)
        self.assertEqual(history_response.data[0]["job_title"], "Senior backend developer")

    def test_company_specific_success_criteria(self):
        """
        Success Criteria:
        Same resume evaluated against Google, Amazon, OpenAI, Netflix produces:
        - Google: 91
        - Amazon: 84
        - OpenAI: 67
        - Netflix: 79
        """
        url = "/api/job-ats/"
        companies_to_test = [
            {"company": "Google", "expected": 91, "jd": "We require solid algorithms, system design, and leadership skills."},
            {"company": "Amazon", "expected": 84, "jd": "We look for leadership principles, cloud architecture, and ownership."},
            {"company": "OpenAI", "expected": 67, "jd": "Research-focused AI team looking for Python, AI, LLMs experts."},
            {"company": "Netflix", "expected": 79, "jd": "We need specialists in distributed systems and microservices scale."}
        ]

        for case in companies_to_test:
            payload = {
                "job_title": "Software Engineer",
                "job_description": case["jd"],
                "company_name": case["company"]
            }
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data["overall_match"], case["expected"], f"Failed for {case['company']}")
            self.assertEqual(response.data["ats_score"], case["expected"], f"Failed for {case['company']}")

    def test_different_professions_and_jobs(self):
        """
        Verify different JDs (Teacher, Doctor, Lawyer, Civil/Mechanical Engineer, HR, Marketing) produce different scores.
        """
        url = "/api/job-ats/"
        jds_to_test = [
            {"title": "Software Engineer", "jd": "Looking for Python Django software developers.", "company": "Tech Corp"},
            {"title": "Data Analyst", "jd": "Requires SQL databases, statistics, Excel, and analytics reporting.", "company": "Analytics Corp"},
            {"title": "AI Engineer", "jd": "Build LLM agents, LangChain development, and PyTorch deep learning models.", "company": "AI startup"},
            {"title": "Teacher", "jd": "High school teaching credential, pedagogy expertise, classroom lessons planning.", "company": "Global School"},
            {"title": "Doctor", "jd": "Pediatric surgeon clinical diagnosis and MD degree required.", "company": "General Hospital"},
            {"title": "Lawyer", "jd": "Legal counsel corporate compliance litigation and contract reviews.", "company": "Legal Partners"},
            {"title": "Civil Engineer", "jd": "AutoCAD structural design civil planning and construction supervision.", "company": "Build Ltd"},
            {"title": "Mechanical Engineer", "jd": "Thermodynamics CAD modeling solidworks mechanical components testing.", "company": "Factory Inc"},
            {"title": "HR Specialist", "jd": "Recruiting talent acquisition onboarding people operations policies.", "company": "HR Services"},
            {"title": "Marketing Manager", "jd": "SEO campaign execution brand growth google analytics.", "company": "Marketing Agency"}
        ]

        scores = set()
        for case in jds_to_test:
            payload = {
                "job_title": case["title"],
                "job_description": case["jd"],
                "company_name": case["company"]
            }
            response = self.client.post(url, payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            scores.add(response.data["overall_match"])
            
        # Assert that we got different scores for different JDs (not all matching same default)
        self.assertGreater(len(scores), 1, "Scores for all JDs were identical!")

