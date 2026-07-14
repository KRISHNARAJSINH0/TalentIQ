import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from apps.resumes.models import Resume
from apps.ats.models import ATSScore
from apps.profiles.models import Skill, Experience, Project, Certification
from apps.portfolio.models import Portfolio
from apps.timeline.models import TimelineEvent, SkillHistory, ATSHistory, CareerProgress, ResumeVersion
from apps.timeline.services import TimelineService, VersionService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Resume)
def handle_resume_save(sender, instance, created, **kwargs):
    try:
        user = instance.user
        if created:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.RESUME_UPLOADED,
                title="New Resume Uploaded",
                description=f"Uploaded resume: '{instance.resume_title}'",
                metadata={"resume_id": str(instance.id), "title": instance.resume_title}
            )
            # Create a version for it
            VersionService.create_version(user, resume=instance, summary=f"Initial version for {instance.resume_title}")
        else:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.RESUME_UPDATED,
                title="Resume Updated",
                description=f"Updated resume: '{instance.resume_title}'",
                metadata={"resume_id": str(instance.id), "title": instance.resume_title}
            )
    except Exception as e:
        logger.exception("Error in handle_resume_save signal: %s", str(e))


@receiver(post_save, sender=ATSScore)
def handle_ats_save(sender, instance, created, **kwargs):
    try:
        resume = instance.resume
        user = resume.user
        score_val = float(instance.ats_score)
        
        # Save to ATSHistory
        ATSHistory.objects.create(
            user=user,
            resume=resume,
            overall_score=instance.ats_score,
            keyword_score=instance.ats_score * 0.9,
            industry_score=instance.ats_score * 0.95,
            completion_score=resume.completion_percentage,
            date=timezone.now().date()
        )

        TimelineService.log_event(
            user=user,
            event_type=TimelineEvent.EventType.ATS_IMPROVED,
            title="ATS Score Analyzed",
            description=f"ATS Score of {score_val}/100 calculated for resume '{resume.resume_title}'",
            metadata={"resume_id": str(resume.id), "ats_score": score_val}
        )

        # Update CareerProgress
        CareerProgress.objects.create(
            user=user,
            career_score=score_val * 0.8 + (float(resume.completion_percentage) * 0.2),
            growth_score=score_val * 1.1 if score_val < 90 else 100.0,
            learning_score=75.0,
            industry_match=instance.industry_match or {},
            market_alignment=score_val * 0.85,
            date=timezone.now().date()
        )
    except Exception as e:
        logger.exception("Error in handle_ats_save signal: %s", str(e))


@receiver(post_save, sender=Skill)
def handle_skill_save(sender, instance, created, **kwargs):
    try:
        user = instance.profile.user
        if created:
            # Create SkillHistory
            SkillHistory.objects.create(
                user=user,
                skill_name=instance.skill_name,
                skill_category=instance.get_skill_type_display(),
                source="Manual",
                is_active=True,
                added_date=timezone.now().date()
            )

            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.SKILL_ADDED,
                title="Skill Added",
                description=f"Added skill: '{instance.skill_name}'",
                metadata={"skill_name": instance.skill_name}
            )
    except Exception as e:
        logger.exception("Error in handle_skill_save signal: %s", str(e))


@receiver(post_delete, sender=Skill)
def handle_skill_delete(sender, instance, **kwargs):
    try:
        user = instance.profile.user
        # Mark in SkillHistory
        hist = SkillHistory.objects.filter(user=user, skill_name=instance.skill_name, is_active=True).first()
        if hist:
            hist.is_active = False
            hist.removed_date = timezone.now().date()
            hist.save()

        TimelineService.log_event(
            user=user,
            event_type=TimelineEvent.EventType.SKILL_REMOVED,
            title="Skill Removed",
            description=f"Removed skill: '{instance.skill_name}'",
            metadata={"skill_name": instance.skill_name}
        )
    except Exception as e:
        logger.exception("Error in handle_skill_delete signal: %s", str(e))


@receiver(post_save, sender=Project)
def handle_project_save(sender, instance, created, **kwargs):
    try:
        user = instance.profile.user
        if created:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.PROJECT_ADDED,
                title="Project Added",
                description=f"Added project: '{instance.project_name}'",
                metadata={"project_name": instance.project_name}
            )
    except Exception as e:
        logger.exception("Error in handle_project_save signal: %s", str(e))


@receiver(post_save, sender=Experience)
def handle_experience_save(sender, instance, created, **kwargs):
    try:
        user = instance.profile.user
        if created:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.EXPERIENCE_ADDED,
                title="Experience Added",
                description=f"Added experience: '{instance.designation}' at '{instance.company}'",
                metadata={"company": instance.company, "designation": instance.designation}
            )
    except Exception as e:
        logger.exception("Error in handle_experience_save signal: %s", str(e))


@receiver(post_save, sender=Certification)
def handle_certification_save(sender, instance, created, **kwargs):
    try:
        user = instance.profile.user
        if created:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.CERTIFICATE_ADDED,
                title="Certificate Added",
                description=f"Added certification: '{instance.certificate_name}' from '{instance.organization}'",
                metadata={"name": instance.certificate_name, "organization": instance.organization}
            )
    except Exception as e:
        logger.exception("Error in handle_certification_save signal: %s", str(e))


@receiver(post_save, sender=Portfolio)
def handle_portfolio_save(sender, instance, created, **kwargs):
    try:
        user = instance.profile.user
        if created:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.PORTFOLIO_PUBLISHED,
                title="Portfolio Published",
                description=f"Portfolio created with theme: '{instance.get_theme_display()}'",
                metadata={"slug": instance.slug, "theme": instance.theme}
            )
        else:
            TimelineService.log_event(
                user=user,
                event_type=TimelineEvent.EventType.PORTFOLIO_UPDATED,
                title="Portfolio Updated",
                description=f"Portfolio updated with theme: '{instance.get_theme_display()}'",
                metadata={"slug": instance.slug, "theme": instance.theme}
            )
    except Exception as e:
        logger.exception("Error in handle_portfolio_save signal: %s", str(e))
