"""
Profiles views – Phase 10.
"""

import logging
import re
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.resumes.models import Resume
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
from .serializers import ProfileMasterSerializer

logger = logging.getLogger(__name__)


def parse_date(date_str):
    """Safely parse date strings into DateField format, returning None if current/invalid."""
    if not date_str:
        return None
    date_str = str(date_str).strip().lower()
    if date_str in ["current", "present", "now", "ongoing", "current_job"]:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%m/%Y", "%Y", "%B %Y", "%b %Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    # Regex fallback for 4-digit year
    match = re.search(r"\b(19|20)\d{2}\b", date_str)
    if match:
        try:
            return datetime(int(match.group(0)), 1, 1).date()
        except Exception:
            pass
    return None


@transaction.atomic
def initialize_profile_from_resume(profile, resume):
    """Initialize profile and related records from a resume's master JSON."""
    data = resume.master_resume_json or {}
    if not data:
        return

    # Clear existing related records to prevent duplication
    profile.skills.all().delete()
    profile.educations.all().delete()
    profile.experiences.all().delete()
    profile.projects.all().delete()
    profile.certifications.all().delete()
    profile.languages.all().delete()
    profile.achievements.all().delete()
    profile.awards.all().delete()
    profile.volunteer_work.all().delete()
    profile.publications.all().delete()
    profile.hobbies.all().delete()
    profile.references.all().delete()

    # Update User info
    user = profile.user
    name = data.get("name", "").strip()
    if name:
        parts = name.split(" ", 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ""
    
    email = data.get("email", "").strip()
    if email and not user.email:
        user.email = email
    
    phone = data.get("phone", "").strip()
    if phone and not user.phone:
        user.phone = phone
    user.save()

    # Update Profile info
    profile.summary = data.get("summary", "") or ""
    profile.address = data.get("address", "") or ""
    profile.city = data.get("city", "") or ""
    profile.state = data.get("state", "") or ""
    profile.country = data.get("country", "") or ""
    profile.postal_code = data.get("postal_code", "") or ""
    profile.website = data.get("website", "") or ""
    profile.github = data.get("github", "") or ""
    profile.linkedin = data.get("linkedin", "") or ""
    profile.portfolio_url = data.get("portfolio", data.get("portfolio_url", "")) or ""
    
    # Initialize source map
    source_map = {}
    for key in ["summary", "address", "city", "state", "country", "postal_code", "website", "github", "linkedin", "portfolio_url"]:
        source_map[key] = "gemini" if resume.ai_status == "completed" else "regex"
    profile.source_of_value = source_map
    profile.save()

    # Log profile creation
    ProfileEditHistory.objects.create(
        profile=profile,
        section="profile",
        field_name="initialized_from_resume",
        old_value=None,
        new_value=f"Resume ID: {resume.id}",
        source="system",
    )

    # 1. Skills
    skills = data.get("skills", [])
    if isinstance(skills, list):
        for s in skills:
            if isinstance(s, str) and s.strip():
                Skill.objects.get_or_create(profile=profile, skill_name=s.strip(), skill_type=Skill.SkillType.GENERAL)
    
    # Technical & Soft Skills lists if present
    tech_skills = data.get("technical_skills", [])
    if isinstance(tech_skills, list):
        for s in tech_skills:
            if isinstance(s, str) and s.strip():
                Skill.objects.get_or_create(profile=profile, skill_name=s.strip(), skill_type=Skill.SkillType.TECHNICAL)
                
    soft_skills = data.get("soft_skills", [])
    if isinstance(soft_skills, list):
        for s in soft_skills:
            if isinstance(s, str) and s.strip():
                Skill.objects.get_or_create(profile=profile, skill_name=s.strip(), skill_type=Skill.SkillType.SOFT)

    # 2. Education
    educations = data.get("education", [])
    if isinstance(educations, list):
        for edu in educations:
            if isinstance(edu, dict):
                Education.objects.create(
                    profile=profile,
                    institute=edu.get("institution", edu.get("institute", "Unknown Institution")),
                    degree=edu.get("degree", "Unknown Degree"),
                    field_of_study=edu.get("field_of_study", "") or "",
                    start_date=parse_date(edu.get("start_date", edu.get("start_year"))) or datetime.today().date(),
                    end_date=parse_date(edu.get("end_date", edu.get("end_year"))),
                    grade=edu.get("grade", "") or "",
                )

    # 3. Experience
    experiences = data.get("experience", [])
    if isinstance(experiences, list):
        for exp in experiences:
            if isinstance(exp, dict):
                # Handle employment type mapping
                emp_type_raw = exp.get("employment_type", "full_time").strip().lower()
                emp_type = Experience.EmploymentType.FULL_TIME
                for choice in Experience.EmploymentType.choices:
                    if choice[0] in emp_type_raw:
                        emp_type = choice[0]
                        break

                Experience.objects.create(
                    profile=profile,
                    company=exp.get("company", "Unknown Company"),
                    designation=exp.get("designation", exp.get("designation_title", "Unknown Role")),
                    employment_type=emp_type,
                    start_date=parse_date(exp.get("start_date")) or datetime.today().date(),
                    end_date=parse_date(exp.get("end_date")),
                    description=exp.get("description", "") or "",
                )

    # 4. Projects
    projects = data.get("projects", [])
    if isinstance(projects, list):
        for proj in projects:
            if isinstance(proj, dict):
                techs = proj.get("technologies", [])
                tech_str = techs if isinstance(techs, str) else ", ".join(techs) if isinstance(techs, list) else ""
                Project.objects.create(
                    profile=profile,
                    project_name=proj.get("project_name", proj.get("title", "Unknown Project")),
                    technologies=tech_str,
                    description=proj.get("description", "") or "",
                    github_url=proj.get("github_url", "") or "",
                    live_url=proj.get("live_url", "") or "",
                )

    # 5. Certifications
    certs = data.get("certifications", [])
    if isinstance(certs, list):
        for cert in certs:
            if isinstance(cert, dict):
                Certification.objects.create(
                    profile=profile,
                    certificate_name=cert.get("certificate_name", cert.get("name", "Unknown Certification")),
                    organization=cert.get("organization", cert.get("issuer", "Unknown Issuer")),
                    issue_date=parse_date(cert.get("issue_date", cert.get("date"))) or datetime.today().date(),
                    credential_url=cert.get("credential_url", "") or "",
                )

    # 6. Languages
    languages = data.get("languages", [])
    if isinstance(languages, list):
        for lang in languages:
            if isinstance(lang, str) and lang.strip():
                Language.objects.get_or_create(
                    profile=profile,
                    language_name=lang.strip(),
                    proficiency=Language.Proficiency.PROFESSIONAL,
                )
            elif isinstance(lang, dict) and lang.get("language_name"):
                Language.objects.get_or_create(
                    profile=profile,
                    language_name=lang.get("language_name").strip(),
                    proficiency=lang.get("proficiency", Language.Proficiency.PROFESSIONAL),
                )

    # 7. Achievements
    achieve = data.get("achievements", [])
    if isinstance(achieve, list):
        for ach in achieve:
            if isinstance(ach, str) and ach.strip():
                Achievement.objects.create(profile=profile, description=ach.strip())

    # 8. Awards
    awards = data.get("awards", [])
    if isinstance(awards, list):
        for awd in awards:
            if isinstance(awd, dict):
                Award.objects.create(
                    profile=profile,
                    title=awd.get("title", "Unknown Award"),
                    issuer=awd.get("issuer", "") or "",
                    date_awarded=parse_date(awd.get("date_awarded", awd.get("date"))),
                )

    # 9. Volunteer Work
    volunteer = data.get("volunteer_work", [])
    if isinstance(volunteer, list):
        for vol in volunteer:
            if isinstance(vol, dict):
                VolunteerWork.objects.create(
                    profile=profile,
                    organization=vol.get("organization", "Unknown Organization"),
                    role=vol.get("role", "Volunteer"),
                    start_date=parse_date(vol.get("start_date")),
                    end_date=parse_date(vol.get("end_date")),
                    description=vol.get("description", "") or "",
                )

    # 10. Publications
    pubs = data.get("publications", [])
    if isinstance(pubs, list):
        for pub in pubs:
            if isinstance(pub, dict):
                Publication.objects.create(
                    profile=profile,
                    title=pub.get("title", "Unknown Publication"),
                    publisher=pub.get("publisher", "") or "",
                    publication_date=parse_date(pub.get("publication_date", pub.get("date"))),
                    url=pub.get("url", "") or "",
                )

    # 11. Hobbies
    hobbies = data.get("hobbies", [])
    if isinstance(hobbies, list):
        for hob in hobbies:
            if isinstance(hob, str) and hob.strip():
                Hobby.objects.get_or_create(profile=profile, hobby_name=hob.strip())

    # 12. References
    refs = data.get("references", [])
    if isinstance(refs, list):
        for ref in refs:
            if isinstance(ref, dict):
                Reference.objects.create(
                    profile=profile,
                    name=ref.get("name", "Unknown Reference"),
                    relationship=ref.get("relationship", "") or "",
                    company=ref.get("company", "") or "",
                    contact=ref.get("contact", "") or "",
                )


class ProfileMasterView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        logger.info("Profile viewed by user %s", request.user.username)
        profile, created = Profile.objects.get_or_create(user=request.user)

        # Check if we should initialize/import from a resume
        resume_id = request.query_params.get("resume_id")
        reset_param = request.query_params.get("reset", "false").lower() == "true"
        should_init = created or not profile.summary

        if resume_id:
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            already_initialized = ProfileEditHistory.objects.filter(
                profile=profile,
                field_name="initialized_from_resume",
                new_value=f"Resume ID: {resume.id}"
            ).exists()
            if not already_initialized or reset_param:
                initialize_profile_from_resume(profile, resume)
        elif should_init:
            # Fallback to the latest completed resume
            latest_resume = Resume.objects.filter(user=request.user, validation_status="completed").order_by("-updated_at").first()
            if latest_resume:
                already_initialized = ProfileEditHistory.objects.filter(
                    profile=profile,
                    field_name="initialized_from_resume",
                    new_value=f"Resume ID: {latest_resume.id}"
                ).exists()
                if not already_initialized or reset_param:
                    initialize_profile_from_resume(profile, latest_resume)

        serializer = ProfileMasterSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileMasterSerializer(profile, data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            logger.info("Profile updated by user %s", request.user.username)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileSectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        section = request.data.get("section")
        data = request.data.get("data")
        if not section:
            return Response({"error": "Section name is required."}, status=status.HTTP_400_BAD_REQUEST)

        profile, _ = Profile.objects.get_or_create(user=request.user)

        # Map frontend section name to ProfileMasterSerializer fields
        payload = {}
        if section == "personal":
            personal_fields = [
                "first_name", "last_name", "email", "phone", "headline", "summary",
                "address", "city", "state", "country", "postal_code", "website",
                "github", "linkedin", "portfolio_url"
            ]
            for field in personal_fields:
                if field in data:
                    payload[field] = data[field]
        elif section == "skills":
            payload = {"skills": data}
        elif section == "education":
            payload = {"educations": data}
        elif section == "experience":
            payload = {"experiences": data}
        elif section == "projects":
            payload = {"projects": data}
        elif section == "certifications":
            payload = {"certifications": data}
        elif section == "languages":
            payload = {"languages": data}
        elif section == "achievements":
            payload = {"achievements": data}
        elif section == "awards":
            payload = {"awards": data}
        elif section == "volunteer_work":
            payload = {"volunteer_work": data}
        elif section == "publications":
            payload = {"publications": data}
        elif section == "hobbies":
            payload = {"hobbies": data}
        elif section == "references":
            payload = {"references": data}
        else:
            return Response({"error": f"Invalid section name '{section}'."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProfileMasterSerializer(profile, data=payload, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            logger.info("Section '%s' updated by user %s", section, request.user.username)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        section = request.data.get("section")
        is_verified = request.data.get("is_verified", True)

        profile, _ = Profile.objects.get_or_create(user=request.user)

        if not section:
            profile.is_verified = is_verified
            profile.save()
            logger.info("Profile verification updated to %s by user %s", is_verified, request.user.username)
            ProfileEditHistory.objects.create(
                profile=profile,
                section="profile",
                field_name="is_verified",
                old_value=str(not is_verified),
                new_value=str(is_verified),
                source="manual",
                edited_by=request.user,
            )
        else:
            logger.info("Section '%s' verification updated to %s by user %s", section, is_verified, request.user.username)
            ProfileEditHistory.objects.create(
                profile=profile,
                section=section,
                field_name="is_verified",
                old_value=None,
                new_value=str(is_verified),
                source="manual",
                edited_by=request.user,
            )

        serializer = ProfileMasterSerializer(profile)
        return Response(serializer.data)


class ProfileExportView(APIView):
    """
    API view to export the user's verified profile data.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileMasterSerializer(profile)
        return Response(serializer.data)

