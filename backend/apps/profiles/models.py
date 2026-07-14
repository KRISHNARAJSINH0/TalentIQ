"""
Profiles models – User profile and related career data.

Contains the core profile entity and all related models:
Skill, Education, Experience, Project, Certification, Language.

All models use UUID primary keys, automatic timestamps via BaseModel,
and are linked to Profile via ForeignKey.
"""

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    URLValidator,
)
from django.db import models

from apps.common.models import BaseModel


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class Profile(BaseModel):
    """
    One-to-one extension of the User model.

    Stores professional headline, contact details, social links,
    and acts as the parent for all career-related records.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="User",
    )
    headline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Professional Headline",
        help_text="e.g. Full Stack Developer | React & Django",
    )
    summary = models.TextField(
        blank=True,
        verbose_name="Summary",
        help_text="Brief professional summary or bio.",
    )

    # Address
    address = models.CharField(max_length=255, blank=True, verbose_name="Address")
    city = models.CharField(max_length=100, blank=True, verbose_name="City", db_index=True)
    state = models.CharField(max_length=100, blank=True, verbose_name="State")
    country = models.CharField(max_length=100, blank=True, verbose_name="Country", db_index=True)
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="Postal Code")

    # Social / Web
    website = models.URLField(blank=True, verbose_name="Website")
    github = models.URLField(blank=True, verbose_name="GitHub URL")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn URL")
    portfolio_url = models.URLField(blank=True, verbose_name="Portfolio URL")

    # Tracking & Verification Fields
    last_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="edited_profiles",
        verbose_name="Last Edited By",
    )
    last_edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Edited At",
    )
    source_of_value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Source of Value Map",
        help_text="Maps field names to their source (e.g. 'regex', 'spacy', 'gemini', 'manual').",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Is Verified",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} – Profile"


# ---------------------------------------------------------------------------
# Skill
# ---------------------------------------------------------------------------

class Skill(BaseModel):
    """A professional skill associated with a user profile."""

    class SkillLevel(models.TextChoices):
        BEGINNER = "beginner", "Beginner"
        INTERMEDIATE = "intermediate", "Intermediate"
        ADVANCED = "advanced", "Advanced"
        EXPERT = "expert", "Expert"

    class SkillType(models.TextChoices):
        GENERAL = "general", "General"
        TECHNICAL = "technical", "Technical"
        SOFT = "soft", "Soft"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="skills",
        verbose_name="Profile",
    )
    skill_name = models.CharField(
        max_length=100,
        verbose_name="Skill Name",
        db_index=True,
    )
    skill_level = models.CharField(
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.INTERMEDIATE,
        verbose_name="Proficiency Level",
    )
    skill_type = models.CharField(
        max_length=20,
        choices=SkillType.choices,
        default=SkillType.GENERAL,
        verbose_name="Skill Type",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        unique_together = ["profile", "skill_name", "skill_type"]

    def __str__(self):
        return f"{self.skill_name} ({self.get_skill_level_display()} - {self.get_skill_type_display()})"


# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

class Education(BaseModel):
    """An educational qualification on a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="educations",
        verbose_name="Profile",
    )
    institute = models.CharField(
        max_length=255,
        verbose_name="Institute / University",
        db_index=True,
    )
    degree = models.CharField(
        max_length=200,
        verbose_name="Degree",
        help_text="e.g. Bachelor of Technology",
    )
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Field of Study",
        help_text="e.g. Computer Science",
    )
    start_date = models.DateField(
        verbose_name="Start Date",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
        help_text="Leave blank if currently studying.",
    )
    grade = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Grade / CGPA",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Education"
        verbose_name_plural = "Education Records"
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.degree} – {self.institute}"


# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

class Experience(BaseModel):
    """A work experience entry on a user profile."""

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full-Time"
        PART_TIME = "part_time", "Part-Time"
        INTERNSHIP = "internship", "Internship"
        FREELANCE = "freelance", "Freelance"
        CONTRACT = "contract", "Contract"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="experiences",
        verbose_name="Profile",
    )
    company = models.CharField(
        max_length=255,
        verbose_name="Company",
        db_index=True,
    )
    designation = models.CharField(
        max_length=200,
        verbose_name="Designation / Title",
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
        verbose_name="Employment Type",
    )
    start_date = models.DateField(
        verbose_name="Start Date",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
        help_text="Leave blank if currently working here.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
        help_text="Responsibilities and achievements.",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.designation} at {self.company}"


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------

class Project(BaseModel):
    """A portfolio project on a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="Profile",
    )
    project_name = models.CharField(
        max_length=200,
        verbose_name="Project Name",
        db_index=True,
    )
    technologies = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Technologies Used",
        help_text="Comma-separated list: React, Django, PostgreSQL",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )
    github_url = models.URLField(
        blank=True,
        verbose_name="GitHub URL",
    )
    live_url = models.URLField(
        blank=True,
        verbose_name="Live Demo URL",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.project_name


# ---------------------------------------------------------------------------
# Certification
# ---------------------------------------------------------------------------

class Certification(BaseModel):
    """A professional certification on a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="certifications",
        verbose_name="Profile",
    )
    certificate_name = models.CharField(
        max_length=255,
        verbose_name="Certificate Name",
        db_index=True,
    )
    organization = models.CharField(
        max_length=255,
        verbose_name="Issuing Organization",
    )
    issue_date = models.DateField(
        verbose_name="Issue Date",
    )
    credential_url = models.URLField(
        blank=True,
        verbose_name="Credential URL",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["-issue_date"]

    def __str__(self):
        return f"{self.certificate_name} – {self.organization}"


# ---------------------------------------------------------------------------
# Language
# ---------------------------------------------------------------------------

class Language(BaseModel):
    """A spoken / written language on a user profile."""

    class Proficiency(models.TextChoices):
        ELEMENTARY = "elementary", "Elementary"
        LIMITED_WORKING = "limited_working", "Limited Working"
        PROFESSIONAL = "professional", "Professional Working"
        FULL_PROFESSIONAL = "full_professional", "Full Professional"
        NATIVE = "native", "Native / Bilingual"

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="languages",
        verbose_name="Profile",
    )
    language_name = models.CharField(
        max_length=100,
        verbose_name="Language",
    )
    proficiency = models.CharField(
        max_length=30,
        choices=Proficiency.choices,
        default=Proficiency.PROFESSIONAL,
        verbose_name="Proficiency",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Language"
        verbose_name_plural = "Languages"
        unique_together = ["profile", "language_name"]

    def __str__(self):
        return f"{self.language_name} ({self.get_proficiency_display()})"


# ---------------------------------------------------------------------------
# Achievement
# ---------------------------------------------------------------------------

class Achievement(BaseModel):
    """An achievement associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="achievements",
        verbose_name="Profile",
    )
    description = models.TextField(
        verbose_name="Achievement Description",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Achievement"
        verbose_name_plural = "Achievements"

    def __str__(self):
        return self.description[:50]


# ---------------------------------------------------------------------------
# Award
# ---------------------------------------------------------------------------

class Award(BaseModel):
    """An award associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="awards",
        verbose_name="Profile",
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Award Title",
    )
    issuer = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Award Issuer",
    )
    date_awarded = models.DateField(
        null=True,
        blank=True,
        verbose_name="Date Awarded",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Award"
        verbose_name_plural = "Awards"
        ordering = ["-date_awarded"]

    def __str__(self):
        return f"{self.title} - {self.issuer}"


# ---------------------------------------------------------------------------
# Volunteer Work
# ---------------------------------------------------------------------------

class VolunteerWork(BaseModel):
    """Volunteer work experience associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="volunteer_work",
        verbose_name="Profile",
    )
    organization = models.CharField(
        max_length=200,
        verbose_name="Organization",
    )
    role = models.CharField(
        max_length=200,
        verbose_name="Role / Designation",
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Start Date",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="End Date",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Description",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Volunteer Work"
        verbose_name_plural = "Volunteer Work Records"
        ordering = ["-end_date", "-start_date"]

    def __str__(self):
        return f"{self.role} at {self.organization}"


# ---------------------------------------------------------------------------
# Publication
# ---------------------------------------------------------------------------

class Publication(BaseModel):
    """A publication associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="publications",
        verbose_name="Profile",
    )
    title = models.CharField(
        max_length=255,
        verbose_name="Publication Title",
    )
    publisher = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Publisher / Journal",
    )
    publication_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Publication Date",
    )
    url = models.URLField(
        blank=True,
        verbose_name="Publication URL",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Publication"
        verbose_name_plural = "Publications"
        ordering = ["-publication_date"]

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# Hobby
# ---------------------------------------------------------------------------

class Hobby(BaseModel):
    """A hobby associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="hobbies",
        verbose_name="Profile",
    )
    hobby_name = models.CharField(
        max_length=100,
        verbose_name="Hobby Name",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Hobby"
        verbose_name_plural = "Hobbies"
        unique_together = ["profile", "hobby_name"]

    def __str__(self):
        return self.hobby_name


# ---------------------------------------------------------------------------
# Reference
# ---------------------------------------------------------------------------

class Reference(BaseModel):
    """A professional reference associated with a user profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="references",
        verbose_name="Profile",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Reference Name",
    )
    relationship = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Relationship",
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Company / Organization",
    )
    contact = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Contact Info",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Reference"
        verbose_name_plural = "References"

    def __str__(self):
        return f"{self.name} - {self.relationship}"


# ---------------------------------------------------------------------------
# ProfileEditHistory
# ---------------------------------------------------------------------------

class ProfileEditHistory(BaseModel):
    """Audit log for changes made to the user's profile."""

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="edit_history",
        verbose_name="Profile",
    )
    section = models.CharField(
        max_length=50,
        verbose_name="Profile Section",
        help_text="e.g. personal, skills, experience, education, projects",
    )
    field_name = models.CharField(
        max_length=100,
        verbose_name="Field Name",
    )
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    source = models.CharField(
        max_length=50,
        default="manual",
        verbose_name="Source of Value",
        help_text="e.g. regex, spacy, gemini, manual",
    )
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_edits",
        verbose_name="Edited By",
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Profile Edit History"
        verbose_name_plural = "Profile Edit Histories"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.profile.user.username} - {self.section}.{self.field_name} changed"
