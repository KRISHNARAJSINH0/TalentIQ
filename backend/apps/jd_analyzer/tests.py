"""
JD Analyzer tests — Phase 22.

Tests JD parsing, skill matching, gap analysis, ATS prediction,
keyword extraction, recommendation generation, and API endpoints.
"""

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.resumes.models import Resume
from apps.profiles.models import Profile, Skill, Education, Experience, Project, Certification

from .services.jd_parser import JDParser
from .services.skill_matcher import SkillMatcher
from .services.gap_engine import GapAnalyzer
from .services.ats_predictor import ATSPredictor
from .services.keyword_engine import KeywordEngine
from .services.recommendation_engine import RecommendationEngine
from .models import JobDescription, JobAnalysis

User = get_user_model()

# ── Sample JDs for testing ──────────────────────────────────────────────────

SOFTWARE_ENGINEER_JD = """
Senior Software Engineer

Company: TechCorp Inc.
Location: San Francisco, CA (Hybrid)
Employment Type: Full-time

About the Role:
We are looking for a Senior Software Engineer to join our platform team.
You will design, build, and maintain scalable backend services.

Responsibilities:
- Design and implement RESTful APIs using Python and Django
- Build microservices with Docker and Kubernetes
- Collaborate with frontend engineers on React integration
- Write comprehensive unit tests and maintain CI/CD pipelines
- Mentor junior developers and participate in code reviews
- Optimize database queries and improve system performance

Requirements:
- 5+ years of professional software engineering experience
- Strong proficiency in Python, Django, and PostgreSQL
- Experience with Docker, Kubernetes, and AWS
- Familiarity with React or similar frontend frameworks
- Bachelor's degree in Computer Science or related field
- Experience with CI/CD, Git, and Agile methodologies

Nice to Have:
- Experience with Redis, Elasticsearch, and message queues
- Knowledge of system design and distributed systems
- AWS certifications

Salary: $130,000 - $180,000/yr
"""

ML_ENGINEER_JD = """
Machine Learning Engineer

About:
Join our AI team to build cutting-edge ML models.

Requirements:
- 3+ years experience in ML/AI
- Python, TensorFlow, PyTorch
- Experience with NLP and computer vision
- Master's degree in Computer Science or related field
- SQL and data pipeline experience
- Experience with AWS SageMaker or similar

Responsibilities:
- Develop and deploy ML models
- Build data pipelines with Spark
- Collaborate with data scientists
"""

DATA_ANALYST_JD = """
Data Analyst

We need a detail-oriented Data Analyst.

Requirements:
- 2+ years of data analysis experience
- SQL, Excel, and Python
- Experience with Tableau or Power BI
- Bachelor's degree in Statistics or related field
- Strong communication skills

Responsibilities:
- Analyze business data and create reports
- Build dashboards and visualizations
"""


class JDParserTests(TestCase):
    """Test the JD Parser service."""

    def setUp(self):
        self.parser = JDParser()

    def test_parse_software_engineer_jd(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertIn("Senior Software Engineer", result["title"])
        self.assertEqual(result["seniority"], "Senior")
        self.assertGreater(len(result["skills"]), 3)
        self.assertIn("python", result["skills"])
        self.assertIn("django", result["skills"])
        self.assertEqual(result["experience_years"]["min"], 5)

    def test_parse_ml_engineer_jd(self):
        result = self.parser.parse(ML_ENGINEER_JD)
        self.assertIn("python", result["skills"])
        self.assertIn("tensorflow", result["skills"])
        self.assertEqual(result["experience_years"]["min"], 3)
        self.assertEqual(result["education"]["level"], "Master's")

    def test_parse_data_analyst_jd(self):
        result = self.parser.parse(DATA_ANALYST_JD)
        self.assertIn("sql", result["skills"])
        self.assertIn("python", result["skills"])
        self.assertEqual(result["experience_years"]["min"], 2)

    def test_empty_jd(self):
        result = self.parser.parse("")
        self.assertIn("error", result)

    def test_skills_extraction_count(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertGreaterEqual(len(result["skills"]), 5)

    def test_remote_detection(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertEqual(result["remote_status"], "hybrid")

    def test_section_detection(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        sections = result.get("sections", {})
        self.assertIsInstance(sections, dict)

    def test_requirements_extraction(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertGreater(len(result["requirements"]), 0)

    def test_responsibilities_extraction(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertGreater(len(result["responsibilities"]), 0)

    def test_salary_extraction(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertIn("min", result.get("salary_range", {}))

    def test_industry_detection(self):
        result = self.parser.parse(SOFTWARE_ENGINEER_JD)
        self.assertIsInstance(result["industry"], str)
        self.assertTrue(len(result["industry"]) > 0)


class SkillMatcherTests(TestCase):
    """Test the Skill Matcher service."""

    def setUp(self):
        self.matcher = SkillMatcher()

    def test_full_match(self):
        result = self.matcher.match(
            ["Python", "Django", "PostgreSQL"],
            ["python", "django", "postgresql"]
        )
        self.assertEqual(result["skills_match"], 100)
        self.assertEqual(len(result["missing"]), 0)

    def test_partial_match(self):
        result = self.matcher.match(
            ["Python", "Django"],
            ["python", "django", "docker", "aws"]
        )
        self.assertEqual(result["skills_match"], 50)
        self.assertIn("docker", result["missing"])
        self.assertIn("aws", result["missing"])

    def test_synonym_resolution(self):
        result = self.matcher.match(
            ["JavaScript", "Node.js"],
            ["js", "nodejs"]
        )
        self.assertEqual(result["skills_match"], 100)

    def test_empty_jd_skills(self):
        result = self.matcher.match(["Python"], [])
        self.assertEqual(result["skills_match"], 100)

    def test_bonus_skills(self):
        result = self.matcher.match(
            ["Python", "Django", "React", "Go"],
            ["python", "django"]
        )
        self.assertEqual(result["skills_match"], 100)
        self.assertGreater(len(result["bonus"]), 0)


class GapAnalyzerTests(TestCase):
    """Test the Gap Analyzer service."""

    def setUp(self):
        self.analyzer = GapAnalyzer()

    def test_experience_gap_meets(self):
        profile = {"experiences": [{"start_date": "2020-01-01", "end_date": "2025-01-01"}]}
        jd = {"experience_years": {"min": 3, "max": 5}}
        skill_result = {"missing": [], "matching": ["python"]}
        result = self.analyzer.analyze(profile, jd, skill_result)
        self.assertTrue(result["experience_gap"]["meets_requirement"])

    def test_experience_gap_not_meets(self):
        profile = {"experiences": [{"start_date": "2024-01-01", "end_date": "2025-01-01"}]}
        jd = {"experience_years": {"min": 5, "max": 7}}
        skill_result = {"missing": ["docker"], "matching": ["python"]}
        result = self.analyzer.analyze(profile, jd, skill_result)
        self.assertFalse(result["experience_gap"]["meets_requirement"])

    def test_education_gap_meets(self):
        profile = {"educations": [{"degree": "Bachelor of Technology", "field_of_study": "Computer Science"}]}
        jd = {"education": {"level": "Bachelor's", "field": "Computer Science"}}
        skill_result = {"missing": [], "matching": []}
        result = self.analyzer.analyze(profile, jd, skill_result)
        self.assertTrue(result["education_gap"]["meets_requirement"])

    def test_skill_gaps_priority(self):
        skill_result = {"missing": ["python", "docker", "kubernetes", "aws"], "matching": ["sql"]}
        result = self.analyzer.analyze({}, {"experience_years": {"min": 0, "max": 0}, "education": {}, "requirements": []}, skill_result)
        gaps = result["skill_gaps"]
        high_count = sum(1 for g in gaps if g["importance"] == "High")
        self.assertGreater(high_count, 0)


class ATSPredictorTests(TestCase):
    """Test the ATS Predictor service."""

    def setUp(self):
        self.predictor = ATSPredictor()

    def test_ats_score_range(self):
        profile = {
            "headline": "Software Engineer",
            "summary": "Experienced developer with 5 years of Python and Django.",
            "skills": [{"skill_name": "Python"}, {"skill_name": "Django"}],
            "experiences": [{"description": "Built APIs with Django."}],
            "educations": [{"degree": "B.Tech"}],
            "projects": [{"project_name": "API Project"}],
            "certifications": [],
        }
        skill_result = {"skills_match": 80, "missing": ["docker"]}
        keyword_result = {"keyword_match": 75}
        parsed_jd = {"skills": ["python", "django", "docker"]}

        result = self.predictor.predict(profile, parsed_jd, skill_result, keyword_result)
        self.assertGreaterEqual(result["ats_score"], 0)
        self.assertLessEqual(result["ats_score"], 100)
        self.assertIsInstance(result["suggestions"], list)

    def test_suggestions_generated(self):
        profile = {"skills": [], "experiences": [], "educations": [], "projects": [], "certifications": [], "summary": ""}
        skill_result = {"skills_match": 30, "missing": ["python", "docker", "aws", "kubernetes"]}
        keyword_result = {"keyword_match": 40}
        parsed_jd = {"skills": ["python", "docker", "aws", "kubernetes"]}

        result = self.predictor.predict(profile, parsed_jd, skill_result, keyword_result)
        self.assertGreater(len(result["suggestions"]), 0)
        self.assertGreater(result["potential_improvement"], 0)


class KeywordEngineTests(TestCase):
    """Test the Keyword Engine service."""

    def setUp(self):
        self.engine = KeywordEngine()

    def test_keyword_extraction(self):
        profile = {
            "headline": "Python Developer",
            "summary": "Experienced with Django and REST APIs.",
            "skills": [{"skill_name": "Python"}, {"skill_name": "Django"}],
            "experiences": [], "educations": [], "projects": [], "certifications": [],
        }
        result = self.engine.analyze(SOFTWARE_ENGINEER_JD, profile)
        self.assertGreater(result["keyword_match"], 0)
        self.assertGreater(result["total_keywords"], 0)
        self.assertIsInstance(result["action_verbs"], list)

    def test_no_profile(self):
        profile = {"skills": [], "experiences": [], "educations": [], "projects": [], "certifications": []}
        result = self.engine.analyze(SOFTWARE_ENGINEER_JD, profile)
        self.assertGreaterEqual(result["keyword_match"], 0)


class RecommendationEngineTests(TestCase):
    """Test the Recommendation Engine service."""

    def setUp(self):
        self.engine = RecommendationEngine()

    def test_learning_path(self):
        parsed_jd = {"title": "Software Engineer", "seniority": "Senior", "responsibilities": []}
        skill_result = {"missing": ["docker", "aws", "kubernetes"], "matching": ["python", "django"], "bonus": []}
        gap_result = {
            "experience_match": 80, "education_match": 90,
            "experience_gap": {"meets_requirement": True, "candidate_years": 5},
            "education_gap": {"meets_requirement": True, "candidate_level": "Bachelor's"},
            "certification_gaps": [],
        }
        result = self.engine.recommend(parsed_jd, skill_result, gap_result)
        self.assertGreater(len(result["learning_path"]), 0)
        self.assertIn("score", result["interview_readiness"])
        self.assertIn("min", result["salary_estimate"])

    def test_salary_estimate_senior(self):
        parsed_jd = {"title": "Senior Software Engineer", "seniority": "Senior"}
        result = self.engine.recommend(parsed_jd, {"missing": [], "matching": ["python"], "bonus": []}, {
            "experience_match": 90, "education_match": 95,
            "experience_gap": {"meets_requirement": True, "candidate_years": 6},
            "education_gap": {"meets_requirement": True, "candidate_level": "Master's"},
            "certification_gaps": [],
        })
        self.assertGreater(result["salary_estimate"]["min"], 100)


class JDAPITests(TestCase):
    """Test the JD Analyzer API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="jd_testuser",
            email="jdtest@example.com",
            password="testpass123",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a resume for the user
        self.resume = Resume.objects.create(
            user=self.user,
            resume_title="Test Resume",
            original_filename="test_resume.pdf",
            file_size=1024,
            mime_type="application/pdf",
            validation_status="completed",
        )

        # Get or create a profile (Resume post_save may auto-create one)
        self.profile, _ = Profile.objects.get_or_create(
            user=self.user,
            defaults={
                "headline": "Python Developer",
                "summary": "5 years of experience building web applications with Python and Django.",
            },
        )
        if not self.profile.headline:
            self.profile.headline = "Python Developer"
            self.profile.summary = "5 years of experience building web applications with Python and Django."
            self.profile.save()

        Skill.objects.get_or_create(profile=self.profile, skill_name="Python", defaults={"skill_level": "advanced"})
        Skill.objects.get_or_create(profile=self.profile, skill_name="Django", defaults={"skill_level": "advanced"})
        Skill.objects.get_or_create(profile=self.profile, skill_name="PostgreSQL", defaults={"skill_level": "intermediate"})
        Skill.objects.get_or_create(profile=self.profile, skill_name="Git", defaults={"skill_level": "advanced"})
        Skill.objects.get_or_create(profile=self.profile, skill_name="React", defaults={"skill_level": "intermediate"})
        Education.objects.get_or_create(
            profile=self.profile,
            institute="Test University",
            defaults={
                "degree": "Bachelor of Technology",
                "field_of_study": "Computer Science",
                "start_date": "2016-08-01",
                "end_date": "2020-06-01",
            },
        )
        Experience.objects.get_or_create(
            profile=self.profile,
            company="Tech Company",
            defaults={
                "designation": "Software Engineer",
                "start_date": "2020-07-01",
                "end_date": "2025-01-01",
                "description": "Built REST APIs with Python and Django. Used PostgreSQL for database.",
            },
        )

    def test_upload_jd(self):
        response = self.client.post("/api/jd/upload/", {
            "content": SOFTWARE_ENGINEER_JD,
            "source_type": "text",
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn("title", response.data)
        self.assertIn("parsed_data", response.data)

    def test_analyze_jd(self):
        response = self.client.post("/api/jd/analyze/", {
            "content": SOFTWARE_ENGINEER_JD,
        })
        self.assertEqual(response.status_code, 201)
        data = response.data
        self.assertIn("match_score", data)
        self.assertIn("ats_score", data)
        self.assertIn("skills_match", data)
        self.assertIn("missing_skills", data)
        self.assertIn("strengths", data)
        self.assertIn("suggestions", data)
        self.assertGreater(data["match_score"], 0)
        self.assertGreater(data["ats_score"], 0)

    def test_history(self):
        # First create an analysis
        self.client.post("/api/jd/analyze/", {"content": SOFTWARE_ENGINEER_JD})
        response = self.client.get("/api/jd/history/")
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

    def test_report(self):
        # Create an analysis
        res = self.client.post("/api/jd/analyze/", {"content": SOFTWARE_ENGINEER_JD})
        analysis_id = res.data["id"]
        response = self.client.get(f"/api/jd/report/{analysis_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("report", response.data)

    def test_gaps(self):
        res = self.client.post("/api/jd/analyze/", {"content": SOFTWARE_ENGINEER_JD})
        analysis_id = res.data["id"]
        response = self.client.get(f"/api/jd/gaps/{analysis_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("missing_skills", response.data)

    def test_ats_endpoint(self):
        res = self.client.post("/api/jd/analyze/", {"content": SOFTWARE_ENGINEER_JD})
        analysis_id = res.data["id"]
        response = self.client.get(f"/api/jd/ats/{analysis_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ats_score", response.data)

    def test_short_jd_rejected(self):
        response = self.client.post("/api/jd/analyze/", {"content": "Too short"})
        self.assertEqual(response.status_code, 400)

    def test_unauthenticated_rejected(self):
        client = APIClient()
        response = client.post("/api/jd/analyze/", {"content": SOFTWARE_ENGINEER_JD})
        self.assertEqual(response.status_code, 401)
