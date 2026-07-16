"""
ATS Rule Registry – Exposes helper functions and custom procedures for evaluation conditions.
"""

from datetime import datetime


def get_years_of_experience(experiences) -> float:
    """Helper to calculate total candidate experience years."""
    total_days = 0
    for exp in experiences:
        start = exp.start_date
        if not start:
            continue
        end = exp.end_date or datetime.today().date()
        total_days += (end - start).days
    return round(total_days / 365.25, 2)


def get_spelling_errors_count(grammar_results) -> int:
    """Helper to get spelling errors count."""
    if not grammar_results:
        return 0
    return len(grammar_results.get("spelling_issues", [])) or grammar_results.get("spelling_errors_count", 0)


def get_passive_voice_count(grammar_results) -> int:
    """Helper to get passive voice count."""
    if not grammar_results:
        return 0
    return grammar_results.get("passive_voice_count", 0)


def get_keyword_density(keyword_results) -> float:
    """Helper to get keyword density percentage."""
    if not keyword_results:
        return 0.0
    return float(keyword_results.get("keyword_density_pct", 0.0))


def has_project_links(projects) -> bool:
    """Helper checking if any projects have urls."""
    return any(bool(p.github_url or p.live_url) for p in projects)


def has_soft_skills(skills) -> bool:
    """Helper checking if soft skills exist."""
    return any(getattr(s, "skill_type", "") == "soft" for s in skills)


def has_tech_skills(skills) -> bool:
    """Helper checking if technical skills exist."""
    return any(getattr(s, "skill_type", "") == "technical" for s in skills)


# A map of all registered helper functions to expose to eval() context
REGISTERED_HELPERS = {
    "get_years_of_experience": get_years_of_experience,
    "get_spelling_errors_count": get_spelling_errors_count,
    "get_passive_voice_count": get_passive_voice_count,
    "get_keyword_density": get_keyword_density,
    "has_project_links": has_project_links,
    "has_soft_skills": has_soft_skills,
    "has_tech_skills": has_tech_skills,
    "len": len,
    "bool": bool,
    "any": any,
    "all": all,
}
