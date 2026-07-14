import logging
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import (
    Notification,
    NotificationPreference,
    EmailQueue,
    NotificationHistory,
    Reminder,
    Digest,
    Announcement
)

User = get_user_model()
logger = logging.getLogger(__name__)

class PreferenceService:
    """
    Handles user notification preferences.
    """
    @staticmethod
    def get_preferences(user):
        pref, _ = NotificationPreference.objects.get_or_create(user=user)
        return pref

    @staticmethod
    def update_preferences(user, data):
        pref = PreferenceService.get_preferences(user)
        for key, val in data.items():
            if hasattr(pref, key):
                setattr(pref, key, val)
        pref.save()
        logger.info(f"Preferences updated for user: {user.email}")
        return pref


class NotificationService:
    """
    Manages generation, filters, and logs of In-App and Email alerts.
    """
    @staticmethod
    def create_notification(user, title, message, type_name, priority="normal", metadata=None):
        if metadata is None:
            metadata = {}

        # Default system announcement for global broadcasts
        if not user:
            notification = Notification.objects.create(
                user=None,
                title=title,
                message=message,
                type=type_name,
                priority=priority,
                status=Notification.Status.DELIVERED,
                delivered_at=timezone.now(),
                metadata=metadata
            )
            return notification

        # Check user preferences
        pref = PreferenceService.get_preferences(user)
        
        # Mapping notification type to user preferences filters
        should_send = True
        if type_name in [Notification.Type.ATS_IMPROVED, Notification.Type.ATS_DECREASED, Notification.Type.NEW_RESUME_VERSION]:
            should_send = pref.enable_ats_alerts
        elif type_name in [Notification.Type.CAREER_SUGGESTION, Notification.Type.SKILL_RECOMMENDATION, Notification.Type.MISSING_SKILLS]:
            should_send = pref.enable_career_alerts
        elif type_name in [Notification.Type.PORTFOLIO_VIEWED, Notification.Type.PORTFOLIO_SHARED]:
            should_send = pref.enable_portfolio_alerts
        elif type_name in [Notification.Type.WEEKLY_REPORT]:
            should_send = pref.enable_weekly_reports
        elif type_name in [Notification.Type.MONTHLY_REPORT]:
            should_send = pref.enable_monthly_reports
        elif type_name in [Notification.Type.SECURITY_ALERT]:
            should_send = pref.enable_security_notifications

        if not should_send:
            logger.info(f"Notification of type {type_name} blocked by preference for user: {user.email}")
            return None

        # Create in-app notification
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            type=type_name,
            priority=priority,
            status=Notification.Status.DELIVERED,
            delivered_at=timezone.now(),
            metadata=metadata
        )

        # Log delivery history
        NotificationHistory.objects.create(
            user=user,
            notification_type=type_name,
            title=title,
            delivery_method="In-App"
        )
        logger.info(f"Notification sent to user {user.email}: {title}")

        # Queue Email if preferred
        if pref.enable_email:
            subject = f"[ResumeAI Alert] {title}"
            EmailQueue.objects.create(
                user=user,
                subject=subject,
                body=message,
                status=EmailQueue.Status.PENDING
            )
            NotificationHistory.objects.create(
                user=user,
                notification_type=type_name,
                title=title,
                delivery_method="Email"
            )
            logger.info(f"Email notification queued for user: {user.email}")

        return notification

    @staticmethod
    def mark_as_read(user, notification_ids=None):
        queryset = Notification.objects.filter(user=user, read=False)
        if notification_ids:
            queryset = queryset.filter(id__in=notification_ids)
        
        count = queryset.update(read=True)
        logger.info(f"Marked {count} notifications as read for user: {user.email}")
        return count

    @staticmethod
    def delete_notification(user, notification_id):
        # Allow archive/deletion by removing the record
        count, _ = Notification.objects.filter(user=user, id=notification_id).delete()
        return count > 0


class ReminderService:
    """
    Schedules and triggers alerts for roadmap milestone actions or resume reviews.
    """
    @staticmethod
    def create_reminder(user, title, description, reminder_type, due_date):
        reminder = Reminder.objects.create(
            user=user,
            title=title,
            description=description,
            reminder_type=reminder_type,
            due_date=due_date
        )
        logger.info(f"Created reminder for user {user.email}: {title} on {due_date}")
        return reminder

    @staticmethod
    def check_pending_reminders():
        """
        Polls pending reminders that have crossed due date and generates notifications.
        Infrastructure is designed to be triggered by Celery beat or cron tasks.
        """
        now = timezone.now()
        pending = Reminder.objects.filter(due_date__lte=now, triggered=False)
        count = 0
        for rem in pending:
            NotificationService.create_notification(
                user=rem.user,
                title=f"Reminder: {rem.title}",
                message=rem.description or f"Your reminder '{rem.title}' is due.",
                type_name=Notification.Type.CERTIFICATE_REMINDER if rem.reminder_type == Reminder.ReminderType.CERTIFICATE else Notification.Type.ROADMAP_MILESTONE,
                priority=Notification.Priority.HIGH
            )
            rem.triggered = True
            rem.save()
            count += 1
        return count


class DigestService:
    """
    Compiles periodic analytics activity into summary digest profiles.
    """
    @staticmethod
    def generate_digest(user, digest_type="weekly"):
        days = 7 if digest_type == "weekly" else 30
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        # Pull aggregate data generated from other apps
        # (Resume uploads, ATS score averages, portfolio views)
        resumes_uploaded = user.resumes.filter(upload_date__date__range=[start_date, end_date]).count()
        
        # Calculate ATS average score changes in this period
        ats_scores = [
            float(a.ats_score)
            for r in user.resumes.all()
            for a in r.ats_analyses.filter(ats_completed_at__date__range=[start_date, end_date])
        ]
        avg_ats = sum(ats_scores) / len(ats_scores) if ats_scores else 0.0

        # Calculate views
        views = sum([
            p.views
            for p in (user.profile.portfolios.all() if hasattr(user, 'profile') else [])
        ])

        digest_data = {
            "resumes_uploaded": resumes_uploaded,
            "average_ats_score": avg_ats,
            "portfolio_views": views,
            "generated_cover_letters": resumes_uploaded  # placeholder metric
        }

        digest = Digest.objects.create(
            user=user,
            digest_type=digest_type,
            start_date=start_date,
            end_date=end_date,
            data=digest_data
        )

        # Send alert
        NotificationService.create_notification(
            user=user,
            title=f"Your {digest_type.capitalize()} Digest Report is ready",
            message=f"Summary: You uploaded {resumes_uploaded} resume(s), with an average ATS rating of {avg_ats} and {views} portfolio views.",
            type_name=Notification.Type.WEEKLY_REPORT if digest_type == "weekly" else Notification.Type.MONTHLY_REPORT,
            priority=Notification.Priority.NORMAL
        )

        return digest
