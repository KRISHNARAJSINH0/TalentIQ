"""
Profiles serializers – Phase 10.
"""

import re
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from .models import (
    Profile,
    Skill,
    Education,
    Experience,
    Project,
    Certification,
    Language,
    Achievement,
    Award,
    VolunteerWork,
    Publication,
    Hobby,
    Reference,
    ProfileEditHistory,
)

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Skill
        fields = ["id", "skill_name", "skill_level", "skill_type"]


class EducationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Education
        fields = ["id", "institute", "degree", "field_of_study", "start_date", "end_date", "grade"]


class ExperienceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Experience
        fields = ["id", "company", "designation", "employment_type", "start_date", "end_date", "description"]


class ProjectSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Project
        fields = ["id", "project_name", "technologies", "description", "github_url", "live_url"]


class CertificationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Certification
        fields = ["id", "certificate_name", "organization", "issue_date", "credential_url"]


class LanguageSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Language
        fields = ["id", "language_name", "proficiency"]


class AchievementSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Achievement
        fields = ["id", "description"]


class AwardSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Award
        fields = ["id", "title", "issuer", "date_awarded"]


class VolunteerWorkSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = VolunteerWork
        fields = ["id", "organization", "role", "start_date", "end_date", "description"]


class PublicationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Publication
        fields = ["id", "title", "publisher", "publication_date", "url"]


class HobbySerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Hobby
        fields = ["id", "hobby_name"]


class ReferenceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = Reference
        fields = ["id", "name", "relationship", "company", "contact"]


class ProfileEditHistorySerializer(serializers.ModelSerializer):
    edited_by_username = serializers.CharField(source="edited_by.username", read_only=True)

    class Meta:
        model = ProfileEditHistory
        fields = [
            "id",
            "section",
            "field_name",
            "old_value",
            "new_value",
            "source",
            "edited_by_username",
            "created_at",
        ]


class ProfileMasterSerializer(serializers.ModelSerializer):
    # Writable fields from User model
    first_name = serializers.CharField(source="user.first_name", required=True)
    last_name = serializers.CharField(source="user.last_name", required=True)
    email = serializers.EmailField(source="user.email", required=True)
    phone = serializers.CharField(source="user.phone", required=False, allow_blank=True, allow_null=True)

    # Nested relations
    skills = SkillSerializer(many=True, required=False)
    educations = EducationSerializer(many=True, required=False)
    experiences = ExperienceSerializer(many=True, required=False)
    projects = ProjectSerializer(many=True, required=False)
    certifications = CertificationSerializer(many=True, required=False)
    languages = LanguageSerializer(many=True, required=False)
    achievements = AchievementSerializer(many=True, required=False)
    awards = AwardSerializer(many=True, required=False)
    volunteer_work = VolunteerWorkSerializer(many=True, required=False)
    publications = PublicationSerializer(many=True, required=False)
    hobbies = HobbySerializer(many=True, required=False)
    references = ReferenceSerializer(many=True, required=False)

    edit_history = ProfileEditHistorySerializer(many=True, read_only=True)
    last_edited_by = serializers.PrimaryKeyRelatedField(
        read_only=True,
        pk_field=serializers.UUIDField(),
        allow_null=True
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "headline",
            "summary",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
            "website",
            "github",
            "linkedin",
            "portfolio_url",
            "last_edited_by",
            "last_edited_at",
            "source_of_value",
            "is_verified",
            # Nested relations
            "skills",
            "educations",
            "experiences",
            "projects",
            "certifications",
            "languages",
            "achievements",
            "awards",
            "volunteer_work",
            "publications",
            "hobbies",
            "references",
            "edit_history",
        ]
        read_only_fields = ["id", "last_edited_by", "last_edited_at", "edit_history"]

    def validate_email(self, value):
        """Validate email format."""
        email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        return value

    def validate_phone(self, value):
        """Validate phone format (9 to 15 digits)."""
        if value:
            phone_regex = r"^\+?1?\d{9,15}$"
            if not re.match(phone_regex, value):
                raise serializers.ValidationError("Enter a valid phone number (9-15 digits, optional leading +).")
        return value

    def validate_skills(self, value):
        """Validate duplicate skills."""
        seen = set()
        for item in value:
            name = item.get("skill_name", "").strip().lower()
            skill_type = item.get("skill_type", "general").strip().lower()
            key = (name, skill_type)
            if key in seen:
                raise serializers.ValidationError(f"Duplicate skill '{item.get('skill_name')}' under section '{skill_type}' is not allowed.")
            seen.add(key)
        return value

    def validate_projects(self, value):
        """Validate duplicate projects."""
        seen = set()
        for item in value:
            name = item.get("project_name", "").strip().lower()
            if name in seen:
                raise serializers.ValidationError(f"Duplicate project '{item.get('project_name')}' is not allowed.")
            seen.add(name)
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        request = self.context.get("request")
        current_user = request.user if request else None

        # Extract nested data
        user_data = validated_data.pop("user", {})
        skills_data = validated_data.pop("skills", None)
        educations_data = validated_data.pop("educations", None)
        experiences_data = validated_data.pop("experiences", None)
        projects_data = validated_data.pop("projects", None)
        certifications_data = validated_data.pop("certifications", None)
        languages_data = validated_data.pop("languages", None)
        achievements_data = validated_data.pop("achievements", None)
        awards_data = validated_data.pop("awards", None)
        volunteer_work_data = validated_data.pop("volunteer_work", None)
        publications_data = validated_data.pop("publications", None)
        hobbies_data = validated_data.pop("hobbies", None)
        references_data = validated_data.pop("references", None)

        # Track profile level changes for audit log
        changes = []
        source_map = instance.source_of_value or {}

        # 1. Update User model fields
        user_instance = instance.user
        for attr, value in user_data.items():
            old_val = getattr(user_instance, attr, None)
            if old_val != value:
                setattr(user_instance, attr, value)
                changes.append(("personal", attr, str(old_val), str(value)))
                source_map[attr] = "manual"
        user_instance.save()

        # 2. Update Profile fields
        for attr, value in validated_data.items():
            old_val = getattr(instance, attr, None)
            if old_val != value:
                setattr(instance, attr, value)
                changes.append(("profile", attr, str(old_val), str(value)))
                source_map[attr] = "manual"

        # Update last edited info
        instance.last_edited_by = current_user
        instance.last_edited_at = timezone.now()
        instance.source_of_value = source_map
        instance.save()

        # Save audit logs for profile level changes
        for section, field_name, old_val, new_val in changes:
            ProfileEditHistory.objects.create(
                profile=instance,
                section=section,
                field_name=field_name,
                old_value=old_val,
                new_value=new_val,
                source="manual",
                edited_by=current_user,
            )

        # Helper to sync related lists
        def sync_relation(manager, serializer_class, data, section_name):
            if data is None:
                return
            existing_items = {str(item.id): item for item in manager.all()}
            keep_ids = []

            for item_data in data:
                item_id = item_data.get("id")
                if item_id and str(item_id) in existing_items:
                    # Update
                    child_instance = existing_items[str(item_id)]
                    child_changes = []
                    for key, val in item_data.items():
                        if key == "id":
                            continue
                        old_val = getattr(child_instance, key, None)
                        if old_val != val:
                            setattr(child_instance, key, val)
                            child_changes.append((key, str(old_val), str(val)))
                    child_instance.save()
                    keep_ids.append(str(child_instance.id))

                    # Log child changes
                    for key, o_val, n_val in child_changes:
                        ProfileEditHistory.objects.create(
                            profile=instance,
                            section=section_name,
                            field_name=f"{key} (ID: {child_instance.id})",
                            old_value=o_val,
                            new_value=n_val,
                            source="manual",
                            edited_by=current_user,
                        )
                else:
                    # Create new
                    item_data.pop("id", None)
                    child_instance = manager.create(**item_data)
                    keep_ids.append(str(child_instance.id))
                    ProfileEditHistory.objects.create(
                        profile=instance,
                        section=section_name,
                        field_name=f"created_{section_name}_item",
                        old_value=None,
                        new_value=str(child_instance),
                        source="manual",
                        edited_by=current_user,
                    )

            # Delete removed items
            for item_id, item in existing_items.items():
                if item_id not in keep_ids:
                    ProfileEditHistory.objects.create(
                        profile=instance,
                        section=section_name,
                        field_name=f"deleted_{section_name}_item",
                        old_value=str(item),
                        new_value=None,
                        source="manual",
                        edited_by=current_user,
                    )
                    item.delete()

        # Sync all relations
        sync_relation(instance.skills, SkillSerializer, skills_data, "skills")
        sync_relation(instance.educations, EducationSerializer, educations_data, "educations")
        sync_relation(instance.experiences, ExperienceSerializer, experiences_data, "experiences")
        sync_relation(instance.projects, ProjectSerializer, projects_data, "projects")
        sync_relation(instance.certifications, CertificationSerializer, certifications_data, "certifications")
        sync_relation(instance.languages, LanguageSerializer, languages_data, "languages")
        sync_relation(instance.achievements, AchievementSerializer, achievements_data, "achievements")
        sync_relation(instance.awards, AwardSerializer, awards_data, "awards")
        sync_relation(instance.volunteer_work, VolunteerWorkSerializer, volunteer_work_data, "volunteer_work")
        sync_relation(instance.publications, PublicationSerializer, publications_data, "publications")
        sync_relation(instance.hobbies, HobbySerializer, hobbies_data, "hobbies")
        sync_relation(instance.references, ReferenceSerializer, references_data, "references")

        return instance
