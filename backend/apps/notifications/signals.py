import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from .models import Notification

logger = logging.getLogger(__name__)

@receiver(post_save, sender=apps.get_model("resumes", "Resume"))
def handle_resume_save(sender, instance, created, **kwargs):
    """
    Triggers notifications for Resume Uploaded and Resume Parsed status updates.
    """
    from .services import NotificationService
    if created:
        NotificationService.create_notification(
            user=instance.user,
            title="Resume Uploaded",
            message=f"Your resume '{instance.resume_title}' has been uploaded successfully.",
            type_name=Notification.Type.RESUME_UPLOADED,
            priority=Notification.Priority.NORMAL,
            metadata={"resume_id": str(instance.id)}
        )
    else:
        # Check if parsing status changed to completed
        # Retrieve previous state from DB if possible
        if instance.parsing_status == "completed":
            # Avoid duplicate signals by checking if we already notified
            exists = Notification.objects.filter(
                user=instance.user,
                type=Notification.Type.RESUME_PARSED,
                metadata__resume_id=str(instance.id)
            ).exists()
            if not exists:
                NotificationService.create_notification(
                    user=instance.user,
                    title="Resume Parsed Successfully",
                    message=f"Parsing for '{instance.resume_title}' is done. Review verified profile items.",
                    type_name=Notification.Type.RESUME_PARSED,
                    priority=Notification.Priority.HIGH,
                    metadata={"resume_id": str(instance.id)}
                )


@receiver(post_save, sender=apps.get_model("ats", "ATSScore"))
def handle_ats_save(sender, instance, created, **kwargs):
    """
    Triggers notifications when ATS scores are completed, highlighting score changes.
    """
    from .services import NotificationService
    if created:
        # Fetch previous score if available
        ats_model = apps.get_model("ats", "ATSScore")
        prev = ats_model.objects.filter(
            resume=instance.resume
        ).exclude(id=instance.id).order_by("-ats_completed_at").first()

        score = float(instance.ats_score)
        
        if prev:
            prev_score = float(prev.ats_score)
            if score > prev_score:
                title = "ATS Score Improved!"
                msg = f"Great work! Your ATS score improved from {prev_score} to {score}."
                type_name = Notification.Type.ATS_IMPROVED
                priority = Notification.Priority.HIGH
            elif score < prev_score:
                title = "ATS Score Decreased"
                msg = f"Your ATS score decreased from {prev_score} to {score}. Check recommended fixes."
                type_name = Notification.Type.ATS_DECREASED
                priority = Notification.Priority.NORMAL
            else:
                title = "ATS Analysis Completed"
                msg = f"Your ATS evaluation score is {score}."
                type_name = Notification.Type.ATS_IMPROVED
                priority = Notification.Priority.NORMAL
        else:
            title = "ATS Evaluation Completed"
            msg = f"Your resume has been analyzed with an initial ATS score of {score}."
            type_name = Notification.Type.ATS_IMPROVED
            priority = Notification.Priority.NORMAL

        NotificationService.create_notification(
            user=instance.resume.user,
            title=title,
            message=msg,
            type_name=type_name,
            priority=priority,
            metadata={"ats_score_id": str(instance.id), "resume_id": str(instance.resume.id)}
        )


@receiver(post_save, sender=apps.get_model("portfolio", "Portfolio"))
def handle_portfolio_save(sender, instance, created, **kwargs):
    """
    Triggers notification when a new portfolio is published.
    """
    from .services import NotificationService
    if created:
        NotificationService.create_notification(
            user=instance.profile.user,
            title="Portfolio Published",
            message=f"Your professional portfolio site is now live at /u/{instance.slug}.",
            type_name=Notification.Type.PORTFOLIO_SHARED,
            priority=Notification.Priority.HIGH,
            metadata={"portfolio_slug": instance.slug}
        )


@receiver(post_save, sender=apps.get_model("profiles", "Skill"))
def handle_skill_save(sender, instance, created, **kwargs):
    """
    Triggers automated recommendation reminders when a skill is saved.
    """
    from .services import NotificationService
    if created:
        NotificationService.create_notification(
            user=instance.profile.user,
            title="Skill Registered",
            message=f"You added '{instance.skill_name}'. Check Career AI to discover matching jobs.",
            type_name=Notification.Type.SKILL_RECOMMENDATION,
            priority=Notification.Priority.LOW,
            metadata={"skill_name": instance.skill_name}
        )


@receiver(post_save, sender=apps.get_model("career", "CareerProfile"))
def handle_career_profile_save(sender, instance, created, **kwargs):
    """
    Triggers notification when career scores are calculated or improved.
    """
    from .services import NotificationService
    if not created:
        # Check if score increased
        # Compare with default or retrieve previous state
        # For simplicity, we alert that analysis was compiled
        NotificationService.create_notification(
            user=instance.profile.user,
            title="Career Scores Updated",
            message=f"Your career readiness score is evaluated at {instance.career_readiness}%. Discover suggestions.",
            type_name=Notification.Type.CAREER_SUGGESTION,
            priority=Notification.Priority.NORMAL
        )


@receiver(post_save, sender=apps.get_model("career", "LearningProgressLog"))
def handle_learning_progress_save(sender, instance, created, **kwargs):
    """
    Triggers notifications for roadmap milestone checkmarks.
    """
    from .services import NotificationService
    if instance.is_completed:
        # Prevent double alerts by looking for recent history in this transaction
        exists = Notification.objects.filter(
            user=instance.user,
            type=Notification.Type.ROADMAP_MILESTONE,
            metadata__item_name=instance.item_name
        ).exists()
        if not exists:
            NotificationService.create_notification(
                user=instance.user,
                title="Milestone Completed!",
                message=f"You marked '{instance.item_name}' as completed in your roadmap.",
                type_name=Notification.Type.ROADMAP_MILESTONE,
                priority=Notification.Priority.NORMAL,
                metadata={"item_name": instance.item_name}
            )


@receiver(post_save, sender=apps.get_model("career", "CoverLetter"))
def handle_cover_letter_save(sender, instance, created, **kwargs):
    """
    Triggers notification when a new cover letter is generated.
    """
    from .services import NotificationService
    if created:
        NotificationService.create_notification(
            user=instance.user,
            title="Cover Letter Generated",
            message=f"Your cover letter for '{instance.position}' at '{instance.company}' is ready.",
            type_name=Notification.Type.COVER_LETTER_GENERATED,
            priority=Notification.Priority.NORMAL,
            metadata={"cover_letter_id": str(instance.id)}
        )
