import logging
import time
import statistics
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.profiles.models import Profile, Skill, Education, Experience, Project, Certification
from apps.resumes.models import Resume, ConsistencyReport
from .models import ATSRule, ValidationRun, RuleMetrics
from .ats_engine import ATSEngine
from .rule_loader import INDUSTRY_SKILLS

logger = logging.getLogger(__name__)
User = get_user_model()

class ValidationEngine:
    """
    Automated Testing and Validation Framework for the ATS Intelligence Engine.
    Runs sweeps across different professions, quality groups, and consistency tests.
    """

    QUALITY_GROUPS = {
        "Very Poor": (20, 40),
        "Poor": (40, 55),
        "Average": (55, 70),
        "Good": (70, 85),
        "Excellent": (85, 95),
        "Elite": (95, 100)
    }

    PROFESSIONS = [
        "Software Engineering",
        "Full Stack",
        "Backend",
        "Frontend",
        "AI/ML",
        "Data Science",
        "Mechanical",
        "Civil",
        "Electrical",
        "Chemical",
        "HR",
        "Marketing",
        "Finance",
        "Accounting",
        "Doctor",
        "Teacher",
        "Lawyer",
        "Freelancer",
        "Student",
        "Designer"
    ]

    def run_validation_sweep(self) -> dict:
        """
        Executes a validation sweep across all professions and quality tiers.
        Verifies score ranges, score consistency, and rule coverage.
        Saves a ValidationRun entry.
        """
        from apps.notifications.services import NotificationService
        original_create_notification = NotificationService.create_notification
        NotificationService.create_notification = staticmethod(lambda *args, **kwargs: None)
        try:
            return self._run_validation_sweep_internal()
        finally:
            NotificationService.create_notification = original_create_notification

    def _run_validation_sweep_internal(self) -> dict:
        start_time = time.time()
        total_tests = 0
        successful_tests = 0
        failed_tests = 0
        error_log = []
        scores_collected = []

        # Track rule executions
        rule_executions_tracker = {}

        # 1. Sweep professions and quality tiers
        for profession in self.PROFESSIONS:
            for quality_name, (min_score, max_score) in self.QUALITY_GROUPS.items():
                total_tests += 1
                temp_objects = []
                try:
                    # Create mock profile & resume
                    user, profile, resume, objs = self._create_mock_profile(profession, quality_name)
                    temp_objects.extend(objs)

                    # Run ATS analysis
                    res = ATSEngine.run_ats_analysis(profile, resume)
                    score = res.get("overall_score", 0)
                    scores_collected.append(score)

                    # Verify rule executions and track frequency
                    from .models import RuleExecution
                    executions = RuleExecution.objects.filter(resume=resume)
                    for exec_obj in executions:
                        code = exec_obj.rule.rule_code
                        name = exec_obj.rule.name
                        if code not in rule_executions_tracker:
                            rule_executions_tracker[code] = {"name": name, "passed": 0, "failed": 0}
                        if exec_obj.status == "passed":
                            rule_executions_tracker[code]["passed"] += 1
                        elif exec_obj.status == "failed":
                            rule_executions_tracker[code]["failed"] += 1

                    # Check score range validation
                    if min_score <= score <= max_score:
                        successful_tests += 1
                    else:
                        failed_tests += 1
                        error_log.append({
                            "type": "Score Range Deviation",
                            "profession": profession,
                            "quality_group": quality_name,
                            "expected_range": f"{min_score}-{max_score}",
                            "actual_score": score,
                            "detail": f"The calculated score of {score} is out of target boundaries for {quality_name}."
                        })

                except Exception as e:
                    failed_tests += 1
                    error_log.append({
                        "type": "Execution Error",
                        "profession": profession,
                        "quality_group": quality_name,
                        "detail": f"Crash during validation evaluation: {str(e)}"
                    })
                    logger.error(f"Error validating {profession} - {quality_name}: {str(e)}")
                finally:
                    # Cleanup immediately to prevent database clutter
                    self._cleanup_temp_objects(temp_objects)

        # 2. Consistency Checks (Evaluate 1 profile 10 times to verify variance is 0)
        temp_objects = []
        try:
            user, profile, resume, objs = self._create_mock_profile("Software Engineering", "Good")
            temp_objects.extend(objs)
            
            consistency_scores = []
            for _ in range(10):
                res = ATSEngine.run_ats_analysis(profile, resume)
                consistency_scores.append(res.get("overall_score", 0))

            score_variance = statistics.variance(consistency_scores) if len(consistency_scores) > 1 else 0
            if score_variance != 0:
                failed_tests += 1
                error_log.append({
                    "type": "Consistency Violation",
                    "profession": "Software Engineering",
                    "quality_group": "Good",
                    "detail": f"Evaluation is not deterministic. Scores variance is {score_variance} over repeated executions."
                })
            else:
                successful_tests += 1
        except Exception as e:
            failed_tests += 1
            error_log.append({
                "type": "Consistency Execution Failure",
                "detail": str(e)
            })
        finally:
            self._cleanup_temp_objects(temp_objects)

        # 3. Job Description Differentiation Checks
        temp_objects = []
        try:
            user, profile, resume, objs = self._create_mock_profile("Backend", "Average")
            temp_objects.extend(objs)

            # Evaluate with generic (None) JD
            res_generic = ATSEngine.run_ats_analysis(profile, resume)
            score_generic = res_generic.get("overall_score", 0)

            # Evaluate with highly aligned JD
            aligned_jd = "Looking for a Backend Developer skilled in Python, Django, FastAPI, PostgreSQL, Redis, Docker, and AWS."
            res_aligned = ATSEngine.run_ats_analysis(profile, resume, job_description=aligned_jd)
            score_aligned = res_aligned.get("overall_score", 0)

            # Evaluate with non-aligned JD
            misaligned_jd = "Looking for a Civil Engineer skilled in Revit, AutoCAD, Project Estimation, and Structural Analysis."
            res_misaligned = ATSEngine.run_ats_analysis(profile, resume, job_description=misaligned_jd)
            score_misaligned = res_misaligned.get("overall_score", 0)

            if score_generic == score_aligned == score_misaligned:
                failed_tests += 1
                error_log.append({
                    "type": "Job Specific Differentiation Failure",
                    "detail": "Job description matching engine did not influence ATS score variations."
                })
            else:
                successful_tests += 1
        except Exception as e:
            failed_tests += 1
            error_log.append({
                "type": "JD Differentiation Execution Failure",
                "detail": str(e)
            })
        finally:
            self._cleanup_temp_objects(temp_objects)

        # Save metrics to RuleMetrics in database
        for code, tracker in rule_executions_tracker.items():
            total = tracker["passed"] + tracker["failed"]
            rate = (tracker["passed"] / total * 100) if total > 0 else 0
            RuleMetrics.objects.update_or_create(
                rule_code=code,
                defaults={
                    "rule_name": tracker["name"],
                    "times_executed": total,
                    "times_passed": tracker["passed"],
                    "times_failed": tracker["failed"],
                    "pass_rate": rate
                }
            )

        # Create ValidationRun
        accuracy_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        run_obj = ValidationRun.objects.create(
            run_type="automated_sweep",
            total_tests=total_tests,
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            accuracy_rate=accuracy_rate,
            error_log=error_log
        )

        return {
            "validation_run_id": run_obj.id,
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "accuracy_rate": accuracy_rate,
            "error_log": error_log,
            "duration": time.time() - start_time
        }

    def _create_mock_profile(self, profession: str, quality: str) -> tuple:
        """
        Creates a temporary mock user, profile, resume, and related career data in the DB.
        """
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        username = f"temp_user_{unique_id}@example.com"
        email = username

        # Create User
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name="Mock",
            last_name="Candidate"
        )
        objs = [user]

        # Create/Get Profile
        profile, created = Profile.objects.get_or_create(user=user)
        profile.headline = f"{profession} Consultant"
        profile.summary = f"Summary for quality {quality} - {profession}"
        profile.save()
        if created:
            objs.append(profile)


        # Create Resume
        resume = Resume.objects.create(
            user=user,
            resume_title=f"Mock Resume {profession}",
            extracted_text=f"Extracted resume details for {profession} and tier {quality}",
            is_active=True
        )
        objs.append(resume)

        # Set default target skills
        skills_available = INDUSTRY_SKILLS.get(profession, ["Python", "SQL", "Git"])

        if quality == "Very Poor":
            # Incomplete fields
            user.first_name = ""
            user.last_name = ""
            user.email = "bademail"
            user.save()
            profile.summary = ""
            profile.save()

        elif quality == "Poor":
            # Incomplete profile, few poor entries
            user.email = "bademail"
            user.save()
            profile.summary = "Looking for work."
            profile.save()
            
            # 2 skills
            for s in skills_available[:2]:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)
            
            # 1 poor experience
            exp = Experience.objects.create(
                profile=profile,
                designation="Worker",
                company="Shop",
                start_date="2020-01-01",
                description="Did stuff."
            )
            objs.append(exp)

        elif quality == "Average":
            # Mid tier profile
            profile.summary = f"Dedicated specialist in {profession}. Good communicator and team player."
            profile.address = "Main Street, NY"
            profile.save()

            # 6 skills
            for s in skills_available[:6]:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)

            # 2 experiences
            exp1 = Experience.objects.create(
                profile=profile,
                designation=f"{profession} Analyst",
                company="Tech Corp",
                start_date="2021-01-01",
                end_date="2023-01-01",
                description="Designed basic code modules. Executed SQL queries and maintained projects."
            )
            objs.append(exp1)
            exp2 = Experience.objects.create(
                profile=profile,
                designation=f"Junior {profession}",
                company="Global Inc",
                start_date="2019-01-01",
                end_date="2021-01-01",
                description="Assisted in developers tasks. Drafted requirements documentation."
            )
            objs.append(exp2)

            # 1 Project
            proj = Project.objects.create(
                profile=profile,
                project_name="Management Script",
                technologies="Python, SQL",
                description="Built a script that parses text files."
            )
            objs.append(proj)

            # 1 Education
            edu = Education.objects.create(
                profile=profile,
                degree="B.S. Computer Science",
                institute="State University",
                start_date="2015-01-01",
                end_date="2019-01-01"
            )
            objs.append(edu)

        elif quality == "Good":
            # Good tier profile
            profile.summary = f"Dedicated {profession} Engineer with over 5 years of experience building modern architectures. Proven track record of optimizing database queries and collaborating with teams."
            profile.address = "Silicon Valley, CA"
            profile.linkedin = "https://linkedin.com/in/mockuser"
            profile.github = "https://github.com/mockuser"
            profile.save()

            # 11 skills
            for s in skills_available[:11]:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)

            # 3 experiences
            for i in range(3):
                exp = Experience.objects.create(
                    profile=profile,
                    designation=f"Senior {profession} Developer",
                    company=f"Innovate Lab {i}",
                    start_date=f"202{i}-01-01",
                    end_date=f"202{i+1}-01-01",
                    description=f"Developed secure APIs using {skills_available[0]}; improved query efficiency by 25%. Directed local development teams."
                )
                objs.append(exp)

            # 2 Projects
            for i in range(2):
                proj = Project.objects.create(
                    profile=profile,
                    project_name=f"Project System {i}",
                    technologies=f"{skills_available[0]}, Git",
                    description="Created a scalable platform with responsive components.",
                    github_url="https://github.com/mock/project"
                )
                objs.append(proj)

            # 1 Education
            edu = Education.objects.create(
                profile=profile,
                degree="Bachelor of Engineering",
                institute="Tech Institute",
                start_date="2012-01-01",
                end_date="2016-01-01"
            )

            objs.append(edu)

        elif quality in ["Excellent", "Elite"]:
            # High tier profile
            profile.summary = f"Distinguished lead in {profession} with over 10 years of pioneering experience in building massive distributed systems, machine learning pipelines, and cloud-native applications. Recognized for leadership, mentoring top-performing teams, and driving $10M+ in business revenue."
            profile.address = "New York, NY"
            profile.linkedin = "https://linkedin.com/in/eliteuser"
            profile.github = "https://github.com/eliteuser"
            profile.portfolio_url = "https://eliteuser.dev"
            profile.save()

            # 16-22 skills
            for s in skills_available[:20]:
                skill = Skill.objects.create(profile=profile, skill_name=s, skill_type="technical")
                objs.append(skill)
            
            # Soft skill
            soft_skill = Skill.objects.create(profile=profile, skill_name="Leadership", skill_type="soft")
            objs.append(soft_skill)

            # 4 experiences
            for i in range(4):
                exp = Experience.objects.create(
                    profile=profile,
                    designation=f"Principal {profession} Architect",
                    company=f"Mega Enterprise {i}",
                    start_date=f"201{i}-01-01",
                    end_date=f"201{i+1}-01-01",
                    description=f"Architected enterprise-grade systems handling 1M+ active users; increased user engagement by 45% and drove $5M annual recurring revenue. Directed a team of 15 developers in Scrum environments."
                )
                objs.append(exp)

            # 3 Projects
            for i in range(3):
                proj = Project.objects.create(
                    profile=profile,
                    project_name=f"Enterprise Engine {i}",
                    technologies=f"{skills_available[0]}, AWS, Docker",
                    description="Implemented automated CI/CD pipeline reducing release cycles by 40%.",
                    github_url="https://github.com/elite/enterprise"
                )
                objs.append(proj)

            # 2 Educations
            edu1 = Education.objects.create(
                profile=profile,
                degree="M.S. in Computer Science",
                institute="Stanford University",
                start_date="2010-01-01",
                end_date="2012-01-01"
            )
            objs.append(edu1)
            edu2 = Education.objects.create(
                profile=profile,
                degree="B.S. in Computer Science",
                institute="MIT",
                start_date="2006-01-01",
                end_date="2010-01-01"
            )

            objs.append(edu2)

            # 1 Certification
            cert = Certification.objects.create(
                profile=profile,
                certificate_name="AWS Certified Solutions Architect",
                organization="Amazon Web Services",
                issue_date="2020-01-01"
            )

            objs.append(cert)

        return user, profile, resume, objs

    def _cleanup_temp_objects(self, temp_objects):
        """
        Deletes all temporary objects created during mock execution.
        Order of deletion respects foreign key constraints.
        """
        for obj in reversed(temp_objects):
            try:
                # To bypass soft-delete logic for Resumes
                if hasattr(obj, "hard_delete"):
                    obj.hard_delete()
                else:
                    obj.delete()
            except Exception as e:
                logger.error(f"Cleanup error on {obj}: {str(e)}")
