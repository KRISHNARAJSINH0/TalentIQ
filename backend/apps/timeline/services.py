from django.utils import timezone
from apps.timeline.models import (
    TimelineEvent,
    ResumeVersion,
    ProfileSnapshot,
    ATSHistory,
    SkillHistory,
    CareerProgress,
    LearningHistory
)
from apps.profiles.serializers import ProfileMasterSerializer
from apps.profiles.models import Profile


class TimelineService:
    """
    Handles logging and tracking of user career timeline events.
    """
    @staticmethod
    def log_event(user, event_type, title, description="", metadata=None):
        if metadata is None:
            metadata = {}
        event = TimelineEvent.objects.create(
            user=user,
            event_type=event_type,
            title=title,
            description=description,
            metadata=metadata
        )
        return event


class VersionService:
    """
    Manages capturing resume/profile versions and snapshot history.
    """
    @staticmethod
    def create_version(user, resume=None, summary="Manual Snapshot"):
        # Fetch current profile snapshot
        try:
            profile = Profile.objects.get(user=user)
            profile_data = ProfileMasterSerializer(profile).data
        except Profile.DoesNotExist:
            profile_data = {}

        # Save to ProfileSnapshot
        ProfileSnapshot.objects.create(
            user=user,
            profile_data=profile_data
        )

        # Get latest ATS score if exists
        ats_score = 0.0
        if resume:
            latest_ats = resume.ats_analyses.order_by("-ats_completed_at").first()
            if latest_ats:
                ats_score = float(latest_ats.ats_score)
        
        # Calculate completion percentage
        completion_score = 0.0
        if resume:
            completion_score = float(resume.completion_percentage)
        elif profile_data:
            # Estimate completion from profile fields
            total_fields = len(profile_data)
            filled_fields = sum(1 for k, v in profile_data.items() if v)
            completion_score = (filled_fields / total_fields * 100) if total_fields else 0.0

        # Calculate version number
        last_version = ResumeVersion.objects.filter(user=user).order_by("-version_number").first()
        version_number = (last_version.version_number + 1) if last_version else 1

        # Calculate change_count by diffing with the last version's snapshot
        change_count = 0
        if last_version and last_version.profile_snapshot:
            for key, val in profile_data.items():
                if last_version.profile_snapshot.get(key) != val:
                    change_count += 1

        # Create the ResumeVersion
        version = ResumeVersion.objects.create(
            user=user,
            resume=resume,
            version_number=version_number,
            ats_score=ats_score,
            completion_score=completion_score,
            profile_snapshot=profile_data,
            summary=summary,
            change_count=change_count,
            is_active=True
        )

        # Deactivate previous versions
        ResumeVersion.objects.filter(user=user).exclude(id=version.id).update(is_active=False)

        # Log timeline event
        TimelineService.log_event(
            user=user,
            event_type=TimelineEvent.EventType.RESUME_GENERATED if resume else TimelineEvent.EventType.RESUME_UPDATED,
            title=f"Resume Version {version_number} Generated",
            description=f"Summary of changes: {summary}",
            metadata={"version_number": version_number, "version_id": str(version.id)}
        )

        return version


class ComparisonService:
    """
    Diffs two or three resume/profile snapshots.
    """
    @staticmethod
    def compare_versions(v1, v2, v3=None):
        diff_v1_v2 = ComparisonService._diff_snapshots(v1.profile_snapshot, v2.profile_snapshot)
        
        result = {
            "v1": {
                "id": str(v1.id),
                "version_number": v1.version_number,
                "ats_score": float(v1.ats_score),
                "completion_score": v1.completion_score,
                "created_at": v1.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "v2": {
                "id": str(v2.id),
                "version_number": v2.version_number,
                "ats_score": float(v2.ats_score),
                "completion_score": v2.completion_score,
                "created_at": v2.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "diff_v1_v2": diff_v1_v2,
        }

        if v3:
            diff_v2_v3 = ComparisonService._diff_snapshots(v2.profile_snapshot, v3.profile_snapshot)
            diff_v1_v3 = ComparisonService._diff_snapshots(v1.profile_snapshot, v3.profile_snapshot)
            result["v3"] = {
                "id": str(v3.id),
                "version_number": v3.version_number,
                "ats_score": float(v3.ats_score),
                "completion_score": v3.completion_score,
                "created_at": v3.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            result["diff_v2_v3"] = diff_v2_v3
            result["diff_v1_v3"] = diff_v1_v3

        return result

    @staticmethod
    def _diff_snapshots(snap1, snap2):
        snap1 = snap1 or {}
        snap2 = snap2 or {}

        # Compare skills
        skills1 = {s.get("skill_name") for s in snap1.get("skills", []) if s.get("skill_name")}
        skills2 = {s.get("skill_name") for s in snap2.get("skills", []) if s.get("skill_name")}
        added_skills = list(skills2 - skills1)
        removed_skills = list(skills1 - skills2)

        # Compare experiences
        exp1 = {f"{e.get('company')}:{e.get('designation')}" for e in snap1.get("experiences", []) if e.get("company")}
        exp2 = {f"{e.get('company')}:{e.get('designation')}" for e in snap2.get("experiences", []) if e.get("company")}
        new_experience = [e for e in snap2.get("experiences", []) if f"{e.get('company')}:{e.get('designation')}" not in exp1]

        # Compare projects
        proj1 = {p.get("project_name") for p in snap1.get("projects", []) if p.get("project_name")}
        proj2 = {p.get("project_name") for p in snap2.get("projects", []) if p.get("project_name")}
        new_projects = [p for p in snap2.get("projects", []) if p.get("project_name") not in proj1]

        # Compare certifications
        cert1 = {c.get("certificate_name") for c in snap1.get("certifications", []) if c.get("certificate_name")}
        cert2 = {c.get("certificate_name") for c in snap2.get("certifications", []) if c.get("certificate_name")}
        new_certificates = [c for c in snap2.get("certifications", []) if c.get("certificate_name") not in cert1]

        return {
            "added_skills": added_skills,
            "removed_skills": removed_skills,
            "new_experience": new_experience,
            "new_projects": new_projects,
            "new_certificates": new_certificates,
        }


class GrowthAnalyticsService:
    """
    Computes time-series and aggregate career/learning metrics for visualizations.
    """
    @staticmethod
    def get_growth_analytics(user):
        # 1. ATS History
        ats_records = ATSHistory.objects.filter(user=user).order_by("date")
        ats_history = []
        ats_growth = 0.0
        if ats_records.exists():
            first_ats = ats_records.first().overall_score
            last_ats = ats_records.last().overall_score
            ats_growth = float(last_ats - first_ats)
            for r in ats_records:
                ats_history.append({
                    "date": r.date.strftime("%Y-%m-%d"),
                    "score": float(r.overall_score)
                })

        # 2. Skill Growth
        skills_added = SkillHistory.objects.filter(user=user).order_by("added_date")
        skill_trends = []
        active_skills_set = set()
        for s in skills_added:
            if s.is_active:
                active_skills_set.add(s.skill_name)
            else:
                active_skills_set.discard(s.skill_name)
            skill_trends.append({
                "date": s.added_date.strftime("%Y-%m-%d"),
                "count": len(active_skills_set)
            })

        # 3. Learning Progress
        learning_records = LearningHistory.objects.filter(user=user).order_by("created_at")
        learning_progress = []
        for l in learning_records:
            learning_progress.append({
                "topic": l.topic,
                "progress": l.progress,
                "status": l.status,
                "date": l.created_at.strftime("%Y-%m-%d")
            })

        # 4. Career trends
        career_records = CareerProgress.objects.filter(user=user).order_by("date")
        career_trends = []
        for c in career_records:
            career_trends.append({
                "date": c.date.strftime("%Y-%m-%d"),
                "career_score": c.career_score,
                "growth_score": c.growth_score,
                "learning_score": c.learning_score,
                "market_alignment": c.market_alignment
            })

        # 5. Resume Evolution / Versions
        versions = ResumeVersion.objects.filter(user=user).order_by("version_number")
        version_trends = []
        for v in versions:
            version_trends.append({
                "version_number": v.version_number,
                "ats_score": float(v.ats_score),
                "completion_score": v.completion_score,
                "change_count": v.change_count,
                "date": v.created_at.strftime("%Y-%m-%d")
            })

        return {
            "ats_growth": ats_growth,
            "ats_history": ats_history,
            "skill_trends": skill_trends,
            "learning_progress": learning_progress,
            "career_trends": career_trends,
            "version_trends": version_trends,
        }
