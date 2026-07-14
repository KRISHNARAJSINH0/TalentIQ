import re

# Base Reliability Scores
SOURCE_RELIABILITY = {
    "manual": 100.0,
    "regex": 99.0,
    "spacy": 95.0,
    "gemini": 90.0,
    "recovery_engine": 85.0,
}

# Boost Weights for Entities
ENTITY_BOOSTS = {
    "PERSON": 10.0,
    "ORG": 8.0,
    "DATE": 5.0,
    "EMAIL": 20.0,
    "PHONE": 20.0,
    "LINKEDIN": 20.0,
    "GITHUB": 20.0,
}

# Boost Weights for Matching Sections
SECTION_BOOSTS = {
    "education": 10.0,
    "skills": 10.0,
    "experience": 10.0,
    "projects": 10.0,
    "personal_info": 10.0,
}

# Status Ranges
CONFIDENCE_RANGES = [
    {"min": 95.0, "max": 100.0, "status": "accepted", "label": "Highly Reliable"},
    {"min": 85.0, "max": 95.0, "status": "accepted", "label": "Reliable"},
    {"min": 70.0, "max": 85.0, "status": "review", "label": "Needs Verification"},
    {"min": 50.0, "max": 70.0, "status": "warning", "label": "Suspicious"},
    {"min": 0.0, "max": 50.0, "status": "rejected", "label": "Invalid"},
]


def determine_status(score: float) -> str:
    """
    Returns calibration status based on score boundaries.
    """
    for r in CONFIDENCE_RANGES:
        if r["min"] <= score <= r["max"]:
            return r["status"]
    return "rejected"


def check_name_semantic(value: str) -> tuple[float, str]:
    """
    Checks if a name contains typical job titles / engineering keywords.
    Returns (penalty, reason) if it fails, else (0.0, "").
    """
    if not value:
        return 0.0, ""

    # Common job roles/titles
    title_pattern = re.compile(
        r'\b(engineer|developer|designer|architect|analyst|manager|specialist|consultant|programmer|lead|intern|senior|junior|expert)\b',
        re.IGNORECASE
    )
    if title_pattern.search(value):
        return -30.0, "Name contains a job title/role keyword"
    return 0.0, ""


def check_skill_semantic(value: str) -> tuple[float, str]:
    """
    Checks if a skill contains school/university/degree keywords.
    Returns (penalty, reason) if it fails, else (0.0, "").
    """
    if not value:
        return 0.0, ""

    edu_pattern = re.compile(
        r'\b(university|college|school|bachelor|master|phd|btech|mtech|degree|gpa|cgpa|diploma|academy|institute)\b',
        re.IGNORECASE
    )
    if edu_pattern.search(value):
        return -40.0, "Skill contains education/academic keywords"
    return 0.0, ""


def check_company_semantic(value: str) -> tuple[float, str]:
    """
    Checks if a company name contains educational degrees or keywords.
    Returns (penalty, reason) if it fails, else (0.0, "").
    """
    if not value:
        return 0.0, ""

    degree_pattern = re.compile(
        r'\b(bachelor|master|phd|btech|mtech|msc|bca|mca|degree|gpa|diploma)\b',
        re.IGNORECASE
    )
    if degree_pattern.search(value):
        return -30.0, "Company name contains educational degree keywords"
    return 0.0, ""
