import re
import time
import logging
import json
from django.utils import timezone
from .models import Resume

logger = logging.getLogger(__name__)


class ConflictResolutionService:
    """
    Combines fields from Regex, spaCy, and Gemini, resolving conflicts using priority rules.
    """

    def resolve_conflicts(self, regex_data: dict, spacy_data: dict, gemini_data: dict) -> dict:
        """
        Merges the three parsing dictionaries based on priority rules.
        """
        regex = regex_data or {}
        spacy = spacy_data or {}
        gemini = gemini_data or {}

        def get_value(field, primary_source, fallback_sources):
            """Helper to check primary source first, then try fallbacks."""
            val = primary_source.get(field)
            if val is not None and val != "" and val != []:
                return val
            for source in fallback_sources:
                val = source.get(field)
                if val is not None and val != "" and val != []:
                    return val
            return None

        # Regex priority
        email = get_value("email", regex, [gemini, spacy])
        phone = get_value("phone", regex, [gemini, spacy])
        linkedin = get_value("linkedin", regex, [gemini])
        github = get_value("github", regex, [gemini])
        portfolio = get_value("portfolio", regex, [gemini])
        personal_website = get_value("personal_website", regex, [gemini])
        stackoverflow = get_value("stackoverflow", regex, [gemini])
        kaggle = get_value("kaggle", regex, [gemini])
        medium = get_value("medium", regex, [gemini])
        twitter = get_value("twitter", regex, [gemini])
        address = get_value("address", regex, [gemini, spacy])
        pincode = get_value("pincode", regex, [gemini, spacy])
        other_urls = regex.get("other_urls") or gemini.get("other_urls") or []

        # spaCy priority
        name = get_value("name", spacy, [gemini, regex])
        organizations = spacy.get("organizations") or gemini.get("organizations") or []
        locations = spacy.get("locations") or gemini.get("locations") or []
        dates = spacy.get("dates") or gemini.get("dates") or []

        # Gemini priority
        summary = get_value("summary", gemini, [spacy])
        skills = gemini.get("skills") or []
        technical_skills = gemini.get("technical_skills") or []
        soft_skills = gemini.get("soft_skills") or []
        education = gemini.get("education") or []
        experience = gemini.get("experience") or []
        projects = gemini.get("projects") or []
        certifications = gemini.get("certifications") or []
        languages = gemini.get("languages") or []
        achievements = gemini.get("achievements") or []
        publications = gemini.get("publications") or []
        awards = gemini.get("awards") or []
        volunteer = gemini.get("volunteer") or []
        hobbies = gemini.get("hobbies") or []
        references = gemini.get("references") or []

        # Build master merged dictionary
        merged = {
            "name": name,
            "email": email,
            "phone": phone,
            "summary": summary,
            "skills": skills,
            "technical_skills": technical_skills,
            "soft_skills": soft_skills,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
            "personal_website": personal_website,
            "stackoverflow": stackoverflow,
            "kaggle": kaggle,
            "medium": medium,
            "twitter": twitter,
            "address": address,
            "pincode": pincode,
            "other_urls": other_urls,
            "organizations": organizations,
            "locations": locations,
            "dates": dates,
            "education": education,
            "experience": experience,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
            "achievements": achievements,
            "publications": publications,
            "awards": awards,
            "volunteer": volunteer,
            "hobbies": hobbies,
            "references": references,
        }

        logger.info("Conflicts resolved between parsing sources.")
        return merged


class ResumeNormalizationService:
    """
    Handles normalizations for skills, companies, dates, capitalization, and duplicate removal.
    """

    SKILL_MAPPINGS = {
        "js": "JavaScript",
        "py": "Python",
        "node": "Node.js",
        "reactjs": "React",
        "react.js": "React",
    }

    COMPANY_MAPPINGS = {
        "tcs": "Tata Consultancy Services",
        "tata consultancy services": "Tata Consultancy Services",
        "infosys ltd": "Infosys",
        "infosys ltd.": "Infosys",
        "infosys limited": "Infosys",
    }

    MONTHS = {
        "jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
        "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12",
        "january": "01", "february": "02", "march": "03", "april": "04", "june": "06",
        "july": "07", "august": "08", "september": "09", "october": "10", "november": "11",
        "december": "12"
    }

    def normalize(self, data: dict) -> dict:
        """
        Normalizes lists and values in the merged dictionary.
        """
        normalized = {}

        # 1. Direct fields
        normalized["name"] = self._clean_string(data.get("name"))
        normalized["email"] = self._clean_string(data.get("email"))
        normalized["phone"] = self._clean_string(data.get("phone"))
        normalized["summary"] = self._clean_string(data.get("summary"))
        normalized["linkedin"] = self._clean_string(data.get("linkedin"))
        normalized["github"] = self._clean_string(data.get("github"))
        normalized["portfolio"] = self._clean_string(data.get("portfolio"))
        normalized["personal_website"] = self._clean_string(data.get("personal_website"))
        normalized["stackoverflow"] = self._clean_string(data.get("stackoverflow"))
        normalized["kaggle"] = self._clean_string(data.get("kaggle"))
        normalized["medium"] = self._clean_string(data.get("medium"))
        normalized["twitter"] = self._clean_string(data.get("twitter"))
        normalized["address"] = self._clean_string(data.get("address"))
        normalized["pincode"] = self._clean_string(data.get("pincode"))

        # 2. Skill lists
        normalized["skills"] = self._normalize_skills(data.get("skills") or [])
        normalized["technical_skills"] = self._normalize_skills(data.get("technical_skills") or [])
        normalized["soft_skills"] = self._normalize_skills(data.get("soft_skills") or [])

        # 3. Simple list fields (deduplicate and sort alphabetically)
        normalized["languages"] = self._normalize_simple_list(data.get("languages"))
        normalized["certifications"] = self._normalize_simple_list(data.get("certifications"))
        normalized["achievements"] = self._normalize_simple_list(data.get("achievements"))
        normalized["publications"] = self._normalize_simple_list(data.get("publications"))
        normalized["awards"] = self._normalize_simple_list(data.get("awards"))
        normalized["volunteer"] = self._normalize_simple_list(data.get("volunteer"))
        normalized["hobbies"] = self._normalize_simple_list(data.get("hobbies"))
        normalized["other_urls"] = self._normalize_simple_list(data.get("other_urls"))
        normalized["organizations"] = self._normalize_simple_list(data.get("organizations"))
        normalized["locations"] = self._normalize_simple_list(data.get("locations"))
        normalized["dates"] = self._normalize_simple_list(data.get("dates"))

        # 4. Complex objects list fields (deduplicate)
        normalized["experience"] = self._normalize_experience(data.get("experience") or [])
        normalized["education"] = self._normalize_education(data.get("education") or [])
        normalized["projects"] = self._normalize_projects(data.get("projects") or [])
        normalized["references"] = self._normalize_references(data.get("references") or [])

        logger.info("Normalization of merged resume data completed.")
        return normalized

    def _clean_string(self, val):
        if val is None:
            return None
        s = str(val).strip()
        return s if s else None

    def _normalize_skills(self, skills_list: list) -> list:
        cleaned = []
        seen = set()
        for skill in skills_list:
            if not skill:
                continue
            s_clean = str(skill).strip()
            # Normalize casing / mapped name
            mapped = self.SKILL_MAPPINGS.get(s_clean.lower(), s_clean)
            if mapped.lower() not in seen:
                seen.add(mapped.lower())
                cleaned.append(mapped)
        cleaned.sort()
        return cleaned

    def _normalize_simple_list(self, raw_list: list) -> list:
        if not raw_list:
            return []
        cleaned = []
        seen = set()
        for item in raw_list:
            if not item:
                continue
            item_clean = str(item).strip()
            if item_clean.lower() not in seen:
                seen.add(item_clean.lower())
                cleaned.append(item_clean)
        cleaned.sort()
        return cleaned

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalizes a date string into one format: MM/YYYY, Month YYYY, YYYY, or Present.
        """
        if not date_str:
            return None
        
        s = date_str.strip().lower()
        if s in ("present", "current", "now", "ongoing", "till date", "to date"):
            return "Present"

        # Regex for Month name and 4 digit year, e.g. "May 2021" or "January, 2020"
        month_year_match = re.search(r'([a-zA-Z]{3,9})[-.\s,]*(\d{4})', date_str)
        if month_year_match:
            month_name = month_year_match.group(1).lower()
            year = month_year_match.group(2)
            month_num = self.MONTHS.get(month_name) or self.MONTHS.get(month_name[:3])
            if month_num:
                return f"{month_num}/{year}"
            return f"{month_year_match.group(1).capitalize()} {year}"

        # Regex for MM/YYYY or M/YYYY, e.g. "05/2021" or "5-2021"
        numeric_match = re.search(r'(\d{1,2})[-/](\d{4})', date_str)
        if numeric_match:
            m = numeric_match.group(1).zfill(2)
            y = numeric_match.group(2)
            return f"{m}/{y}"

        # Regex for just YYYY
        year_match = re.search(r'\b(\d{4})\b', date_str)
        if year_match:
            return year_match.group(1)

        return date_str.strip()

    def _normalize_company(self, company_str: str) -> str:
        if not company_str:
            return None
        c_clean = company_str.strip()
        return self.COMPANY_MAPPINGS.get(c_clean.lower(), c_clean)

    def _normalize_experience(self, exp_list: list) -> list:
        cleaned = []
        seen = set()
        for exp in exp_list:
            if not isinstance(exp, dict):
                continue
            company = self._normalize_company(exp.get("company"))
            designation = self._clean_string(exp.get("designation"))
            start_date = self._normalize_date(exp.get("start_date"))
            end_date = self._normalize_date(exp.get("end_date"))
            description = self._clean_string(exp.get("description"))

            if not company and not designation:
                continue

            # Unique key definition
            key = (company.lower() if company else "", designation.lower() if designation else "", start_date or "")
            if key not in seen:
                seen.add(key)
                cleaned.append({
                    "company": company,
                    "designation": designation,
                    "start_date": start_date,
                    "end_date": end_date,
                    "description": description
                })
        return cleaned

    def _normalize_education(self, edu_list: list) -> list:
        cleaned = []
        seen = set()
        for edu in edu_list:
            if not isinstance(edu, dict):
                continue
            institution = self._clean_string(edu.get("institution"))
            degree = self._clean_string(edu.get("degree"))
            field_of_study = self._clean_string(edu.get("field_of_study"))
            start_year = self._normalize_date(edu.get("start_year"))
            end_year = self._normalize_date(edu.get("end_year"))

            if not institution and not degree:
                continue

            key = (institution.lower() if institution else "", degree.lower() if degree else "", field_of_study.lower() if field_of_study else "")
            if key not in seen:
                seen.add(key)
                cleaned.append({
                    "institution": institution,
                    "degree": degree,
                    "field_of_study": field_of_study,
                    "start_year": start_year,
                    "end_year": end_year
                })
        return cleaned

    def _normalize_projects(self, proj_list: list) -> list:
        cleaned = []
        seen = set()
        for proj in proj_list:
            if not isinstance(proj, dict):
                continue
            title = self._clean_string(proj.get("title"))
            description = self._clean_string(proj.get("description"))
            technologies = self._normalize_skills(proj.get("technologies") or [])

            if not title:
                continue

            key = title.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append({
                    "title": title,
                    "description": description,
                    "technologies": technologies
                })
        return cleaned

    def _normalize_references(self, ref_list: list) -> list:
        cleaned = []
        seen = set()
        for ref in ref_list:
            if not isinstance(ref, dict):
                continue
            name = self._clean_string(ref.get("name"))
            company = self._clean_string(ref.get("company"))
            contact = self._clean_string(ref.get("contact"))

            if not name:
                continue

            key = name.lower()
            if key not in seen:
                seen.add(key)
                cleaned.append({
                    "name": name,
                    "company": company,
                    "contact": contact
                })
        return cleaned


class ResumeValidationService:
    """
    Performs structural validation of the master resume JSON structure and formats.
    """

    def validate(self, data: dict) -> tuple[bool, list[str]]:
        """
        Validates the schema and patterns of the master resume profile.
        """
        logger.info("Validation of merged resume data started.")
        errors = []

        # Validate Email
        email = data.get("email")
        if email:
            email_pattern = re.compile(r'^[^@]+@[^@]+\.[^@]+$')
            if not email_pattern.match(email):
                errors.append(f"Invalid email format: '{email}'")

        # Validate Phone
        phone = data.get("phone")
        if phone:
            # Must contain at least 6 digits
            digits = re.sub(r'\D', '', phone)
            if len(digits) < 6:
                errors.append(f"Invalid phone number (too short): '{phone}'")

        # Validate structure of education
        education = data.get("education") or []
        for i, edu in enumerate(education):
            if not edu.get("institution"):
                errors.append(f"Education entry {i + 1} is missing institution name.")

        # Validate structure of experience
        experience = data.get("experience") or []
        for i, exp in enumerate(experience):
            if not exp.get("company"):
                errors.append(f"Experience entry {i + 1} is missing company name.")

        is_valid = len(errors) == 0
        return is_valid, errors


class ResumeMergeService:
    """
    Coordinates conflict resolution, normalization, and validation on resume sub-jsons.
    """

    def __init__(self):
        self.conflict_resolver = ConflictResolutionService()
        self.normalizer = ResumeNormalizationService()
        self.validator = ResumeValidationService()

    def merge_extractions(self, regex_json: dict, spacy_json: dict, ai_json: dict) -> tuple[dict, bool, list[str]]:
        """
        Runs the full merging, normalization, and validation pipeline.
        """
        logger.info("Merge started.")
        
        # 1. Resolve conflicts based on priority rules
        merged_data = self.conflict_resolver.resolve_conflicts(regex_json, spacy_json, ai_json)
        
        # 2. Normalize values
        normalized_data = self.normalizer.normalize(merged_data)
        
        # 3. Validate
        is_valid, errors = self.validator.validate(normalized_data)
        
        logger.info("Normalization completed.")
        return normalized_data, is_valid, errors


class MasterResumeBuilder:
    """
    Orchestrates the merge, calculates completion percentage, logs execution metrics, and saves results.
    """

    def build_master_profile(self, resume: Resume) -> bool:
        """
        Runs merge logic on a Resume instance, updates its master fields and metrics.
        Returns True on success, False on failure.
        """
        start_time = time.time()
        logger.info(f"Master Resume Builder started for Resume: {resume.id}")
        
        resume.validation_status = Resume.ValidationStatus.PROCESSING
        resume.save(update_fields=["validation_status"])

        try:
            # 1. Merge the extractions
            merge_service = ResumeMergeService()
            master_json, is_valid, errors = merge_service.merge_extractions(
                resume.regex_json,
                resume.spacy_json,
                resume.ai_json
            )

            # 2. Calculate completion percentage
            completion = self.calculate_completion(master_json)
            logger.info("Completion calculated.")

            # 3. Save updates to Resume instance
            execution_time = time.time() - start_time
            resume.master_resume_json = master_json
            resume.completion_percentage = completion
            resume.validation_time = timezone.now()
            resume.validation_status = Resume.ValidationStatus.COMPLETED if is_valid else Resume.ValidationStatus.FAILED
            resume.save(update_fields=[
                "master_resume_json",
                "completion_percentage",
                "validation_time",
                "validation_status"
            ])

            logger.info(
                f"Master profile built successfully for Resume {resume.id} "
                f"in {execution_time:.4f}s with completion {completion}%"
            )
            return True

        except Exception as e:
            logger.error(f"Error building master profile for Resume {resume.id}: {str(e)}", exc_info=True)
            resume.validation_status = Resume.ValidationStatus.FAILED
            resume.master_resume_json = {"error": str(e)}
            resume.save(update_fields=["validation_status", "master_resume_json"])
            return False

    def calculate_completion(self, profile: dict) -> float:
        """
        Calculates Overall Completion % based on profile sections.
        Weights:
        - Personal Info (name, email, phone): 15% (5% each)
        - Summary: 10%
        - Skills (skills, tech_skills, soft_skills): 15%
        - Experience: 20%
        - Education: 15%
        - Projects: 10%
        - Certificates: 10%
        - Languages: 5%
        Total: 100%
        """
        score = 0.0

        # Personal Info (15%)
        if profile.get("name"):
            score += 5.0
        if profile.get("email"):
            score += 5.0
        if profile.get("phone"):
            score += 5.0

        # Summary (10%)
        if profile.get("summary"):
            score += 10.0

        # Skills (15%)
        if profile.get("skills") or profile.get("technical_skills") or profile.get("soft_skills"):
            score += 15.0

        # Experience (20%)
        if profile.get("experience"):
            score += 20.0

        # Education (15%)
        if profile.get("education"):
            score += 15.0

        # Projects (10%)
        if profile.get("projects"):
            score += 10.0

        # Certifications (10%)
        if profile.get("certifications"):
            score += 10.0

        # Languages (5%)
        if profile.get("languages"):
            score += 5.0

        return score
