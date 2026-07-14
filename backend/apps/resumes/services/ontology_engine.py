import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

VALIDATION_CATEGORIES = [
    "PERSON",
    "COMPANY",
    "UNIVERSITY",
    "SKILL",
    "CERTIFICATE",
    "TECHNOLOGY",
    "PROJECT",
    "DESIGNATION",
    "LANGUAGE",
    "COUNTRY",
    "CITY",
    "DATE",
    "ROLE",
    "ORGANIZATION",
    "PUBLICATION",
    "AWARD"
]

FORBIDDEN_NAME_TITLE_WORDS = [
    "engineer", "developer", "analyst", "manager", "architect", "scientist",
    "professor", "consultant", "designer", "specialist", "intern", "director",
    "lead", "head", "officer", "executive", "administrator", "advisor", "founder",
    "co-founder", "cto", "ceo", "cfo", "vp", "president", "lead", "senior", "junior"
]

UNIVERSITY_KEYWORDS = [
    "university", "institute", "college", "academy", "school", "campus",
    "polytechnic", "iit", "nit", "bits", "mit", "stanford", "harvard", "oxford",
    "cambridge", "caltech", "eth", "imperial", "columbia", "princeton", "yale",
    "berkeley", "ucla", "nyu", "cmu", "faculty", "conservatory"
]

COMPANY_INDICATORS = [
    "inc", "inc.", "corp", "corp.", "corporation", "ltd", "ltd.", "limited",
    "llc", "l.l.c.", "technologies", "solutions", "services", "group", "global",
    "holdings", "labs", "studios", "worked at", "employer", "organization",
    "company", "current employer", "present", "systems", "pvt", "private"
]

CERTIFICATE_KEYWORDS = [
    "certified", "certificate", "training", "course", "diploma", "license",
    "credential", "certification", "accredited", "pmp", "csm", "cka", "ckad",
    "aws certified", "comptia", "cissp", "ceh"
]

DATE_PATTERNS = [
    r"^(0[1-9]|1[0-2])\/\d{4}$",                    # MM/YYYY
    r"^(19|20)\d{2}$",                             # YYYY
    r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}$", # Month YYYY
    r"^(present|current|ongoing|now)$",            # Present/Current
    r"^(19|20)\d{2}\s*[-–—]\s*(19|20)\d{2}|present|current$", # Range YYYY - YYYY / Present
    r"^(0[1-9]|1[0-2])\/(19|20)\d{2}\s*[-–—]\s*(0[1-9]|1[0-2])\/(19|20)\d{2}|present|current$"
]

LANGUAGES_LIST = [
    "english", "hindi", "gujarati", "french", "german", "spanish", "japanese",
    "chinese", "mandarin", "cantonese", "russian", "arabic", "portuguese",
    "italian", "korean", "bengali", "marathi", "telugu", "tamil", "urdu",
    "punjabi", "dutch", "swedish", "polish", "turkish", "vietnamese", "thai"
]

COUNTRIES_LIST = [
    "united states", "usa", "us", "india", "united kingdom", "uk", "canada",
    "germany", "france", "japan", "australia", "singapore", "china", "brazil",
    "russia", "netherlands", "switzerland", "sweden", "spain", "italy", "ireland"
]

CITIES_LIST = [
    "new york", "san francisco", "london", "mumbai", "bengaluru", "bangalore",
    "delhi", "ahmedabad", "berlin", "tokyo", "toronto", "paris", "sydney",
    "singapore", "chicago", "seattle", "austin", "boston", "vancouver"
]

PUBLICATION_KEYWORDS = [
    "journal", "ieee", "acm", "conference", "paper", "proceedings", "doi",
    "thesis", "dissertation", "published", "arxiv", "patent"
]

AWARD_KEYWORDS = [
    "award", "honors", "winner", "place", "scholarship", "gold medalist",
    "dean's list", "fellowship", "grant", "recognition", "hackathon winner"
]


class OntologyEngine:
    """
    Semantic Ontology Engine enforcing entity categories, semantic constraints,
    forbidden terms, keyword matches, and taxonomies across 16 categories.
    """

    @staticmethod
    def validate_person_name(value: str) -> Tuple[bool, float, str]:
        """
        Validates if a string value is a legitimate Person name.
        Names must NOT contain title/designation terms like Engineer, Developer, etc.
        """
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty or non-string value"

        clean_val = value.strip().lower()

        # Check for forbidden title terms
        for word in clean_val.split():
            if word in FORBIDDEN_NAME_TITLE_WORDS:
                return False, 10.0, f"Person names should not contain designation/title '{word.capitalize()}'"

        # Check if value looks like an email or URL
        if "@" in clean_val or "http" in clean_val or ".com" in clean_val:
            return False, 0.0, "Person name contains email or web address"

        # Check if value is pure numbers or date pattern
        if clean_val.isdigit() or any(re.match(p, clean_val, re.IGNORECASE) for p in DATE_PATTERNS[:2]):
            return False, 0.0, "Person name cannot be a number or date"

        # Valid name heuristic: 1 to 4 words, alphabetic characters / spaces / hyphens
        words = clean_val.split()
        if 1 <= len(words) <= 4 and all(re.match(r"^[a-zA-Z\.\'-]+$", w) for w in words):
            return True, 95.0, "Matches Person name format"

        return True, 75.0, "Acceptable Person name candidate"

    @staticmethod
    def validate_university(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a University/Institution."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        for kw in UNIVERSITY_KEYWORDS:
            if kw in clean_val:
                return True, 96.0, f"Entity matches university keyword/suffix '{kw.capitalize()}'"

        return False, 40.0, "Does not contain university indicators"

    @staticmethod
    def validate_company(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a Company/Employer."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        for ind in COMPANY_INDICATORS:
            if ind in clean_val:
                return True, 92.0, f"Entity matches company suffix/indicator '{ind}'"

        return False, 50.0, "Does not contain company indicators"

    @staticmethod
    def validate_certificate(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a Certificate/Diploma."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        for kw in CERTIFICATE_KEYWORDS:
            if kw in clean_val:
                return True, 95.0, f"Entity matches certification keyword '{kw}'"

        return False, 30.0, "Does not match certification keywords"

    @staticmethod
    def validate_date(value: str) -> Tuple[bool, float, str]:
        """Validates if value matches Date standards."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        for pat in DATE_PATTERNS:
            if re.search(pat, clean_val, re.IGNORECASE):
                return True, 98.0, "Matches standard date format"

        return False, 20.0, "Does not match date formats"

    @staticmethod
    def validate_language(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a spoken/written Language."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        if clean_val in LANGUAGES_LIST:
            return True, 99.0, "Matches spoken language ontology"

        return False, 30.0, "Not a recognized language"

    @staticmethod
    def validate_designation(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a Job Title / Designation."""
        if not value or not isinstance(value, str):
            return False, 0.0, "Empty value"

        clean_val = value.strip().lower()

        for word in clean_val.split():
            if word in FORBIDDEN_NAME_TITLE_WORDS:
                return True, 95.0, f"Matches designation title term '{word.capitalize()}'"

        return False, 45.0, "Does not contain designation title terms"

    @staticmethod
    def validate_country(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a Country."""
        if not value:
            return False, 0.0, "Empty value"
        clean_val = str(value).strip().lower()
        if clean_val in COUNTRIES_LIST:
            return True, 98.0, "Matches country list"
        return False, 30.0, "Not a recognized country"

    @staticmethod
    def validate_city(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a City."""
        if not value:
            return False, 0.0, "Empty value"
        clean_val = str(value).strip().lower()
        if clean_val in CITIES_LIST:
            return True, 95.0, "Matches city list"
        return False, 30.0, "Not a recognized city"

    @staticmethod
    def validate_publication(value: str) -> Tuple[bool, float, str]:
        """Validates if value is a Publication."""
        if not value:
            return False, 0.0, "Empty value"
        clean_val = str(value).strip().lower()
        for kw in PUBLICATION_KEYWORDS:
            if kw in clean_val:
                return True, 94.0, f"Matches publication keyword '{kw}'"
        return False, 40.0, "Not a recognized publication format"

    @staticmethod
    def validate_award(value: str) -> Tuple[bool, float, str]:
        """Validates if value is an Award/Honor."""
        if not value:
            return False, 0.0, "Empty value"
        clean_val = str(value).strip().lower()
        for kw in AWARD_KEYWORDS:
            if kw in clean_val:
                return True, 95.0, f"Matches award keyword '{kw}'"
        return False, 40.0, "Does not match award keywords"
