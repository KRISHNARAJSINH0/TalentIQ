import uuid
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from apps.resumes.models import Resume, SemanticValidation
from apps.resumes.services.knowledge_base import KnowledgeBase
from apps.resumes.services.ontology_engine import OntologyEngine
from apps.resumes.services.semantic_matcher import SemanticMatcher
from apps.resumes.services.entity_classifier import EntityClassifier
from apps.resumes.services.semantic_validator import SemanticValidator

User = get_user_model()


class SemanticValidatorEngineTestCase(TestCase):
    """
    Test suite for KnowledgeBase, OntologyEngine, SemanticMatcher, EntityClassifier,
    SemanticValidator, and 11 distinct resume genres.
    """

    def setUp(self):
        self.user = User.objects.create_user(
            username="semantic_tester",
            email="semantic@example.com",
            password="Password123!"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.kb = KnowledgeBase()
        self.ontology = OntologyEngine()
        self.classifier = EntityClassifier()
        self.validator = SemanticValidator()

    def test_knowledge_base_loading(self):
        """Verify all 8 JSON dictionaries are loaded in KnowledgeBase."""
        self.assertTrue(self.kb.is_exact_entity("SKILL", "Python"))
        self.assertTrue(self.kb.is_exact_entity("COMPANY", "Google"))
        self.assertTrue(self.kb.is_exact_entity("UNIVERSITY", "MIT"))
        self.assertTrue(self.kb.is_exact_entity("DESIGNATION", "Software Engineer"))
        self.assertTrue(self.kb.is_exact_entity("CERTIFICATE", "AWS Certified Solutions Architect"))
        self.assertTrue(self.kb.is_exact_entity("LANGUAGE", "English"))

    def test_ontology_engine_rules(self):
        """Verify semantic ontology rules for person names, universities, dates, and designations."""
        # Person name with designation should fail
        is_valid, score, reason = self.ontology.validate_person_name("Software Engineer")
        self.assertFalse(is_valid)
        self.assertIn("designation", reason.lower())

        # Valid person name
        is_valid_name, score_name, _ = self.ontology.validate_person_name("John Doe")
        self.assertTrue(is_valid_name)
        self.assertGreaterEqual(score_name, 90.0)

        # University keyword matching
        is_univ, score_u, _ = self.ontology.validate_university("Massachusetts Institute of Technology")
        self.assertTrue(is_univ)
        self.assertGreaterEqual(score_u, 90.0)

        # Date format matching
        is_date, score_d, _ = self.ontology.validate_date("05/2024")
        self.assertTrue(is_date)
        self.assertGreaterEqual(score_d, 90.0)

    def test_semantic_matcher_similarity(self):
        """Verify vector cosine similarity and text matching."""
        sim = SemanticMatcher.cosine_similarity("Python Data Science", "Python Machine Learning")
        self.assertGreater(sim, 0.0)

        match_score = SemanticMatcher.match_against_category(
            "Stanford University",
            ["Stanford University", "MIT"],
            ["university", "college"]
        )
        self.assertEqual(match_score, 100.0)

    def test_entity_classifier(self):
        """Verify entity classification across validation categories."""
        res_univ = self.classifier.classify_entity("MIT")
        self.assertEqual(res_univ["top_category"], "UNIVERSITY")

        res_skill = self.classifier.classify_entity("React")
        self.assertIn(res_skill["top_category"], ["SKILL", "TECHNOLOGY"])

        res_desig = self.classifier.classify_entity("Backend Developer")
        self.assertIn(res_desig["top_category"], ["DESIGNATION", "ROLE"])

    def test_semantic_anomaly_detection_problem_example(self):
        """
        Tests the problem scenario from prompt specification:
        {
          "name": "Software Engineer",
          "education": ["Python"],
          "skills": ["MIT"],
          "company": "Backend Developer",
          "project": "Google"
        }
        """
        problem_payload = {
            "name": "Software Engineer",
            "education": ["Python"],
            "skills": ["MIT"],
            "company": "Backend Developer",
            "project": "Google"
        }

        report = self.validator.validate_payload(problem_payload)
        validations = {v["field"]: v for v in report["validations"]}

        # 1. MIT inside Skills -> Detected University, status invalid, action move_to_education
        mit_val = validations.get("skills[0]")
        self.assertIsNotNone(mit_val)
        self.assertEqual(mit_val["value"], "MIT")
        self.assertEqual(mit_val["category"], "University")
        self.assertEqual(mit_val["expected_category"], "Skill")
        self.assertEqual(mit_val["status"], "invalid")
        self.assertEqual(mit_val["action"], "move_to_education")
        self.assertIn("university", mit_val["reason"].lower())

        # 2. Python inside Education -> Detected Skill, status invalid, action move_to_skills
        py_val = validations.get("education[0]")
        self.assertIsNotNone(py_val)
        self.assertEqual(py_val["value"], "Python")
        self.assertIn(py_val["category"], ["Skill", "Technology"])
        self.assertEqual(py_val["status"], "invalid")
        self.assertEqual(py_val["action"], "move_to_skills")

        # 3. Software Engineer inside Name -> Detected Designation, status invalid
        name_val = validations.get("name")
        self.assertIsNotNone(name_val)
        self.assertEqual(name_val["value"], "Software Engineer")
        self.assertIn(name_val["category"], ["Designation", "Role"])
        self.assertEqual(name_val["status"], "invalid")

        # 4. Google inside Project -> Maybe company. Review.
        proj_val = validations.get("project")
        self.assertIsNotNone(proj_val)
        self.assertEqual(proj_val["value"], "Google")
        self.assertEqual(proj_val["action"], "review")
        self.assertEqual(proj_val["reason"], "Maybe company. Review.")

    def test_resume_genre_software(self):
        """Tests Software Engineer Resume."""
        payload = {
            "name": "Alex Mercer",
            "company": "Google",
            "education": ["Stanford University"],
            "skills": ["Python", "Docker", "Kubernetes", "Redis"],
            "certifications": ["AWS Certified Solutions Architect"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_academic_cv(self):
        """Tests Academic CV."""
        payload = {
            "name": "Dr. Eleanor Vance",
            "university": "University of Oxford",
            "publications": ["IEEE Journal of Quantum Computing 2024"],
            "awards": ["Gold Medalist Fellowship"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_designer(self):
        """Tests Designer Resume."""
        payload = {
            "name": "Sophia Chen",
            "designation": "UI/UX Designer",
            "skills": ["Figma", "Photoshop", "Wireframing"],
            "company": "Adobe"
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_medical_cv(self):
        """Tests Medical CV."""
        payload = {
            "name": "Dr. Robert House",
            "designation": "Physician",
            "university": "Harvard University",
            "skills": ["Communication", "Problem Solving"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_research_cv(self):
        """Tests Research CV."""
        payload = {
            "name": "Alan Turing",
            "university": "University of Cambridge",
            "skills": ["Machine Learning", "Mathematics"],
            "publications": ["ACM Computing Surveys"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_law(self):
        """Tests Law Resume."""
        payload = {
            "name": "Harvey Specter",
            "designation": "Attorney",
            "company": "Pearson Hardman",
            "university": "Harvard Law School"
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_teacher(self):
        """Tests Teacher Resume."""
        payload = {
            "name": "Clara Oswald",
            "designation": "High School Teacher",
            "university": "Delhi University",
            "languages": ["English", "French"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_student(self):
        """Tests Student Resume."""
        payload = {
            "name": "Rohan Sharma",
            "university": "BITS Pilani",
            "skills": ["Java", "C++", "SQL"],
            "projects": ["Portfolio Web App"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_two_column(self):
        """Tests Two-Column Resume."""
        payload = {
            "name": "David Miller",
            "designation": "DevOps Engineer",
            "skills": ["Terraform", "Ansible", "AWS"],
            "company": "Microsoft"
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_creative(self):
        """Tests Creative Resume."""
        payload = {
            "name": "Maya Lin",
            "designation": "Creative Director",
            "skills": ["Illustrator", "InDesign", "Prototyping"],
            "company": "Canva"
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_resume_genre_canva(self):
        """Tests Canva Resume."""
        payload = {
            "name": "Liam Nelson",
            "designation": "Product Manager",
            "company": "Salesforce",
            "skills": ["Jira", "Agile", "Scrum"]
        }
        report = self.validator.validate_payload(payload)
        self.assertGreaterEqual(report["metrics"]["semantic_accuracy"], 95.0)

    def test_semantic_validation_api_post(self):
        """Tests POST /api/resume/semantic/ endpoint with payload."""
        response = self.client.post("/api/resume/semantic/", {
            "payload": {
                "name": "John Doe",
                "skills": ["MIT"]
            }
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("validations", data)
        self.assertIn("metrics", data)

    def test_semantic_validation_api_post_with_resume_id(self):
        """Tests POST /api/resume/semantic/ endpoint with resume_id."""
        resume = Resume.objects.create(
            user=self.user,
            resume_title="Test Resume",
            master_resume_json={"name": "Jane Smith", "skills": ["Python"]}
        )
        response = self.client.post("/api/resume/semantic/", {
            "resume_id": str(resume.id)
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["resume_id"], str(resume.id))
        self.assertTrue(SemanticValidation.objects.filter(resume=resume).exists())

    def test_semantic_validation_api_get_detail(self):
        """Tests GET /api/resume/semantic/{id} endpoint."""
        resume = Resume.objects.create(
            user=self.user,
            resume_title="Test Resume 2",
            master_resume_json={"name": "Jane Smith"}
        )
        val = SemanticValidation.objects.create(
            resume=resume,
            field="name",
            value="Jane Smith",
            category="Person",
            expected_category="Person",
            semantic_score=95.0,
            reason="Valid name",
            status="valid",
            action="accept"
        )
        response = self.client.get(f"/api/resume/semantic/{val.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["field"], "name")
        self.assertEqual(data["category"], "Person")
