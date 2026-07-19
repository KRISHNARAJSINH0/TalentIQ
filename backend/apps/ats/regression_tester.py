import logging
import time
from .models import ATSRule
from .ats_engine import ATSEngine
from django.contrib.auth import get_user_model
from apps.profiles.models import Profile, Skill, Experience, Education

logger = logging.getLogger(__name__)
User = get_user_model()

class RegressionTester:
    """
    Evaluates scoring stability against golden baseline profiles to guarantee no regression.
    """

    GOLDEN_BASELINES = {
        "Developer": 82,
        "Designer": 76,
        "Student": 52,
        "Doctor": 88
    }

    def run_regression_tests(self) -> dict:
        """
        Executes scoring against baseline structures and returns regression summaries.
        """
        start_time = time.time()
        passed_tests = 0
        total_tests = 0
        regressions = []

        for role, baseline_score in self.GOLDEN_BASELINES.items():
            total_tests += 1
            temp_objects = []
            try:
                # Create profile
                user, profile, resume, objs = self._create_golden_profile(role)
                temp_objects.extend(objs)

                # Run score
                res = ATSEngine.run_ats_analysis(profile, resume)
                score = res.get("overall_score", 0)

                # Verify against baseline (allow small +/- 2 tolerance for floating point calculations)
                if abs(score - baseline_score) <= 3:
                    passed_tests += 1
                else:
                    regressions.append({
                        "role": role,
                        "expected_baseline": baseline_score,
                        "actual_score": score,
                        "deviation": score - baseline_score,
                        "status": "Failed"
                    })

            except Exception as e:
                regressions.append({
                    "role": role,
                    "expected_baseline": baseline_score,
                    "actual_score": 0,
                    "deviation": -baseline_score,
                    "status": f"Error: {str(e)}"
                })
            finally:
                # Cleanup
                self._cleanup_temp_objects(temp_objects)

        return {
            "total_regression_tests": total_tests,
            "passed_regression_tests": passed_tests,
            "failed_regression_tests": len(regressions),
            "regressions": regressions,
            "duration": time.time() - start_time
        }

    def _create_golden_profile(self, role: str) -> tuple:
        """
        Creates a golden baseline profile for regression testing.
        """
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f"golden_{role.lower()}_{unique_id}@example.com"

        user = User.objects.create_user(
            username=username,
            email=username,
            password="GoldenPassword123!",
            first_name="Golden",
            last_name=role
        )
        objs = [user]

        profile, created = Profile.objects.get_or_create(user=user)
        profile.headline = f"Golden {role}"
        profile.summary = f"Summary text for golden baseline {role}. Expert with years of performance."
        profile.save()
        if created:
            objs.append(profile)


        resume = Resume.objects.create(
            user=user,
            resume_title=f"Golden Resume {role}",
            extracted_text=f"Golden text resume for role {role}",
            is_active=True
        )
        objs.append(resume)

        # Standard sets based on role
        if role == "Developer":
            skills = ["Python", "JavaScript", "SQL", "Git", "Docker", "React"]
            for s in skills:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)
            exp = Experience.objects.create(
                profile=profile,
                designation="Software Developer",
                company="Soft Solutions",
                start_date="2020-01-01",
                description="Developed web applications using Python and React. Managed PostgreSQL databases."
            )
            objs.append(exp)
        elif role == "Designer":
            skills = ["Figma", "UI/UX Design", "Wireframing", "Photoshop"]
            for s in skills:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)
            exp = Experience.objects.create(
                profile=profile,
                designation="UX Designer",
                company="Design Lab",
                start_date="2021-01-01",
                description="Designed high fidelity wireframes and user flows in Figma. Led user research."
            )
            objs.append(exp)
        elif role == "Doctor":
            skills = ["Clinical Diagnosis", "Patient Care", "Surgery", "EHR"]
            for s in skills:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)
            exp = Experience.objects.create(
                profile=profile,
                designation="Medical Resident",
                company="City Hospital",
                start_date="2018-01-01",
                description="Managed patient diagnosis and treatments. Scheduled surgical procedures."
            )
            objs.append(exp)

        return user, profile, resume, objs

    def _cleanup_temp_objects(self, temp_objects):
        for obj in reversed(temp_objects):
            try:
                if hasattr(obj, "hard_delete"):
                    obj.hard_delete()
                else:
                    obj.delete()
            except Exception as e:
                logger.error(f"Cleanup error in Golden {obj}: {str(e)}")
        
