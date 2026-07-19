from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from apps.resumes.models import Resume
from apps.profiles.models import Profile
from apps.ats.models import ATSScore
from .models import BenchmarkReport, RankingHistory, CareerRanking
from .services.benchmark_engine import BenchmarkEngine
from .services.career_ranker import CareerRanker

User = get_user_model()


class BenchmarkTestCase(TestCase):
    """
    Test suite for Phase F: Benchmark & Ranking Engine.
    """

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="candidate",
            email="candidate@example.com",
            password="testpassword123",
            role="candidate"
        )
        self.client.force_authenticate(user=self.user)

    def create_mock_candidate(self, resume_title, job_title, exp_years, industry, country):
        """Helper to set up a test user, profile, and resume."""
        # Clean up any existing resume and profile for self.user
        Resume.objects.filter(user=self.user).delete()
        Profile.objects.filter(user=self.user).delete()
        
        resume = Resume.objects.create(
            user=self.user,
            resume_title=resume_title,
            extracted_text="Extracted text data for " + resume_title,
            parsed_json={
                "experience_years": exp_years,
                "current_role": job_title,
                "overall_score": 85
            }
        )
        
        # Create profile
        profile = Profile.objects.create(
            user=self.user,
            headline=job_title,
            country=country
        )
        
        # Create experiences if exp_years > 0 to match
        from datetime import date, timedelta
        if exp_years > 0:
            from apps.profiles.models import Experience
            Experience.objects.create(
                profile=profile,
                company="Mock Corp",
                designation=job_title,
                start_date=date.today() - timedelta(days=exp_years * 365),
                end_date=date.today()
            )

        # Inject custom attributes to Profile if not present on model
        try:
            profile.primary_industry = industry
            profile.save()
        except Exception:
            pass

        return resume, profile

    def test_student_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Student Resume", "Student / Intern", 0, "AI", "India"
        )
        
        # Test CareerRanker logic
        level = CareerRanker.determine_career_level(resume, profile)
        self.assertEqual(level, "Student")
        
        group = CareerRanker.get_benchmark_group(level)
        self.assertEqual(group, "Students")
        
        # Generate report
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report)
        self.assertEqual(report.resume, resume)
        self.assertTrue(len(report.strengths) > 0)
        self.assertTrue(len(report.weaknesses) > 0)
        
    def test_fresher_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Fresher Resume", "Junior Software Developer", 1, "Cloud", "USA"
        )
        level = CareerRanker.determine_career_level(resume, profile)
        self.assertEqual(level, "Junior")
        
        report = BenchmarkEngine.generate_report(resume)
        self.assertTrue(report.experience_rank.startswith("Top") or "Average" in report.experience_rank)

    def test_software_engineer_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Senior SE Resume", "Software Engineer", 6, "FinTech", "Germany"
        )
        level = CareerRanker.determine_career_level(resume, profile)
        self.assertEqual(level, "Senior")
        
        report = BenchmarkEngine.generate_report(resume)
        self.assertTrue(report.overall_rank.startswith("Top") or "Average" in report.overall_rank)

    def test_ai_engineer_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "AI Engineer Resume", "AI Engineer", 4, "AI", "US"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.profession_rank)

    def test_data_analyst_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Data Analyst Resume", "Data Analyst", 2, "Analytics", "UK"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.industry_rank)

    def test_doctor_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Doctor Resume", "Doctor", 8, "Healthcare", "Canada"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_teacher_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Teacher Resume", "Teacher", 5, "Education", "Australia"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_civil_engineer_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Civil Eng Resume", "Civil Engineer", 7, "Construction", "Singapore"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_marketing_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Marketing Lead Resume", "Marketing", 9, "Retail", "India"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_hr_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "HR Resume", "HR Manager", 11, "Corporate", "USA"
        )
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_freelancer_benchmarking(self):
        resume, profile = self.create_mock_candidate(
            "Freelance Dev Resume", "Freelancer", 3, "Gaming", "Remote"
        )
        level = CareerRanker.determine_career_level(resume, profile)
        group = CareerRanker.get_benchmark_group(level, is_freelancer=True)
        self.assertEqual(group, "Freelancers")
        
        report = BenchmarkEngine.generate_report(resume)
        self.assertIsNotNone(report.overall_rank)

    def test_api_endpoints(self):
        resume, profile = self.create_mock_candidate(
            "API Test Resume", "Full Stack Developer", 4, "FinTech", "USA"
        )
        
        # Test POST Trigger
        res = self.client.post("/api/benchmark/", {"resume_id": str(resume.id)})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("overall_rank", res.data)
        
        # Test GET Report
        res = self.client.get(f"/api/benchmark/report/?resume_id={resume.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("overall_rank", res.data)
        
        # Test GET History
        res = self.client.get(f"/api/benchmark/history/?resume_id={resume.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) > 0)
        
        # Test GET Rank (Leaderboard)
        res = self.client.get(f"/api/rank/?resume_id={resume.id}")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("career_comparison", res.data)
        self.assertIn("industry_comparison", res.data)
