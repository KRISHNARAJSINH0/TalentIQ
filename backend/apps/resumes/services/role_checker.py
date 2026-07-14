import logging
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

ROLE_SKILL_MATRICES: Dict[str, List[str]] = {
    "software": ["Python", "Java", "C++", "JavaScript", "Git", "SQL", "APIs", "Docker", "Cloud"],
    "backend": ["Python", "Java", "Node.js", "SQL", "PostgreSQL", "MongoDB", "APIs", "Docker", "Git"],
    "frontend": ["JavaScript", "React", "HTML", "CSS", "TypeScript", "Git"],
    "fullstack": ["JavaScript", "Python", "React", "Node.js", "SQL", "Git", "Docker"],
    "data analyst": ["SQL", "Python", "Excel", "Power BI", "Tableau", "Statistics"],
    "data scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "PyTorch"],
    "ml engineer": ["Python", "PyTorch", "TensorFlow", "Machine Learning", "Docker", "Git"],
    "designer": ["Figma", "Photoshop", "Illustrator", "UI", "UX", "Wireframing"],
    "ui/ux": ["Figma", "Photoshop", "Wireframing", "User Research", "UI", "UX"],
    "doctor": ["Medical Practice", "Patient Care", "Clinical Research", "Diagnosis"],
    "physician": ["Medical Practice", "Patient Care", "Diagnosis", "Treatment"],
    "lawyer": ["Legal Research", "Contracts", "Litigation", "Compliance"],
    "attorney": ["Legal Research", "Contracts", "Litigation", "Negotiation"],
    "teacher": ["Curriculum Development", "Classroom Management", "Pedagogy", "Assessment"],
    "educator": ["Curriculum Development", "Classroom Management", "Pedagogy"],
    "civil engineer": ["AutoCAD", "Structural Analysis", "Construction Management", "CAD"],
    "mechanical engineer": ["CAD", "SolidWorks", "AutoCAD", "Thermodynamics"],
    "chemical engineer": ["Process Engineering", "Chemical Analysis", "Safety Protocols"],
    "accountant": ["Accounting", "Financial Analysis", "Taxation", "Excel", "Auditing"],
    "hr": ["Recruitment", "Talent Acquisition", "Employee Relations", "HR Policies"],
    "marketing": ["Digital Marketing", "SEO", "Content Strategy", "Social Media", "Analytics"]
}


class RoleChecker:
    """
    Service to validate extracted skills against expected domain skill matrices.
    Provides missing skill suggestions and flags role-to-skill alignment gaps.
    """

    def check_role_consistency(self, payload: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns (issues, suggestions) based on designation vs skills alignment.
        """
        issues: List[Dict[str, Any]] = []
        suggestions: List[Dict[str, Any]] = []

        desig = str(payload.get("designation") or payload.get("current_designation") or payload.get("title") or "").lower()
        skills = payload.get("skills", [])
        if not isinstance(skills, list):
            skills = []

        skills_lower = [str(s).lower() for s in skills if isinstance(s, (str, int))]

        matched_matrix_key = None
        for role_key in ROLE_SKILL_MATRICES:
            if role_key in desig:
                matched_matrix_key = role_key
                break

        if matched_matrix_key:
            expected_skills = ROLE_SKILL_MATRICES[matched_matrix_key]
            missing_skills = [sk for sk in expected_skills if not any(sk.lower() in sl for sl in skills_lower)]

            # If missing more than 60% of expected core skills
            if len(missing_skills) >= len(expected_skills) * 0.6:
                issues.append({
                    "type": "role_skills",
                    "severity": "high",
                    "reason": f"Role '{desig.title()}' profile lacks critical domain skills (e.g. {', '.join(missing_skills[:3])}).",
                    "field": "skills"
                })
            elif len(missing_skills) > 0:
                issues.append({
                    "type": "role_skills",
                    "severity": "medium",
                    "reason": f"Profile missing standard {matched_matrix_key.title()} skills ({', '.join(missing_skills[:3])}).",
                    "field": "skills"
                })

            if missing_skills:
                suggestions.append({
                    "role": matched_matrix_key.title(),
                    "recommended_skills": missing_skills[:5],
                    "reason": f"Adding these recommended skills will increase ATS match score for {matched_matrix_key.title()} roles."
                })

        # Check for ML Engineer / Data Scientist with basic office tools only
        if any(term in desig for term in ["ml engineer", "data scientist", "ai engineer", "backend"]):
            if skills_lower and all(s in ["excel", "word", "powerpoint", "ms office"] for s in skills_lower):
                issues.append({
                    "type": "role_skills",
                    "severity": "critical",
                    "reason": f"Technical role '{desig.title()}' listed only non-technical tools (Excel/Word).",
                    "field": "skills"
                })

        return issues, suggestions
