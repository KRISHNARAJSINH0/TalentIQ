"""
ATS Predictor — Estimates ATS (Applicant Tracking System) compatibility score.

Analyzes keyword density, section completeness, format compliance,
and generates per-suggestion ATS impact points.
"""

import logging

logger = logging.getLogger(__name__)


class ATSPredictor:
    """
    Predict ATS pass probability and generate improvement suggestions.
    """

    # Weights for ATS sub-scores
    WEIGHTS = {
        "keyword_density": 0.35,
        "skills_coverage": 0.30,
        "section_completeness": 0.20,
        "format_compliance": 0.15,
    }

    def predict(self, profile_data: dict, parsed_jd: dict, skill_result: dict, keyword_result: dict) -> dict:
        """
        Returns ATS score (0–100) and suggestions with per-item impact.
        """
        keyword_score = self._keyword_density_score(keyword_result)
        skills_score = skill_result.get("skills_match", 0)
        section_score = self._section_completeness(profile_data)
        format_score = self._format_compliance(profile_data)

        # Weighted composite
        ats_score = round(
            keyword_score * self.WEIGHTS["keyword_density"]
            + skills_score * self.WEIGHTS["skills_coverage"]
            + section_score * self.WEIGHTS["section_completeness"]
            + format_score * self.WEIGHTS["format_compliance"]
        )
        ats_score = max(0, min(100, ats_score))

        # Generate suggestions
        suggestions = self._generate_suggestions(
            profile_data, parsed_jd, skill_result, keyword_result, ats_score
        )

        # Estimate potential ATS after improvements
        potential_gain = sum(s.get("ats_impact", 0) for s in suggestions)
        estimated_ats = min(100, ats_score + potential_gain)

        return {
            "ats_score": ats_score,
            "estimated_ats": estimated_ats,
            "potential_improvement": potential_gain,
            "breakdown": {
                "keyword_density": keyword_score,
                "skills_coverage": skills_score,
                "section_completeness": section_score,
                "format_compliance": format_score,
            },
            "suggestions": suggestions,
        }

    def _keyword_density_score(self, keyword_result: dict) -> int:
        """Score based on how many JD keywords appear in resume."""
        return keyword_result.get("keyword_match", 70)

    def _section_completeness(self, profile_data: dict) -> int:
        """Score based on how many resume sections are filled."""
        sections = {
            "headline": bool(profile_data.get("headline")),
            "summary": bool(profile_data.get("summary")),
            "skills": len(profile_data.get("skills", [])) > 0,
            "experiences": len(profile_data.get("experiences", [])) > 0,
            "educations": len(profile_data.get("educations", [])) > 0,
            "projects": len(profile_data.get("projects", [])) > 0,
            "certifications": len(profile_data.get("certifications", [])) > 0,
        }
        filled = sum(1 for v in sections.values() if v)
        return round((filled / len(sections)) * 100)

    def _format_compliance(self, profile_data: dict) -> int:
        """Score format quality based on content density."""
        score = 70  # Base score

        # Has summary with good length
        summary = profile_data.get("summary", "")
        if summary and len(summary) > 50:
            score += 10

        # Has multiple skills
        if len(profile_data.get("skills", [])) >= 5:
            score += 10

        # Has experience descriptions
        for exp in profile_data.get("experiences", []):
            if exp.get("description") and len(exp["description"]) > 30:
                score += 5
                break

        return min(100, score)

    def _generate_suggestions(self, profile_data, parsed_jd, skill_result, keyword_result, current_ats):
        """Generate actionable suggestions with ATS impact."""
        suggestions = []
        missing = skill_result.get("missing", [])

        # High-impact missing skills
        high_impact = {
            "docker": 3, "kubernetes": 3, "aws": 4, "azure": 3, "gcp": 3,
            "terraform": 2, "cicd": 2, "python": 4, "java": 4,
            "javascript": 3, "typescript": 3, "react": 3, "django": 3,
            "sql": 3, "postgresql": 2, "mongodb": 2, "redis": 2,
            "git": 2, "linux": 2, "graphql": 2, "nodejs": 2,
            "tensorflow": 3, "pytorch": 3, "spark": 3, "kafka": 2,
        }

        for skill in missing[:8]:
            impact = high_impact.get(skill.lower(), 1)
            suggestions.append({
                "action": f"Add {skill}",
                "detail": f"Add {skill} to your skills section and mention it in relevant project descriptions.",
                "ats_impact": impact,
                "category": "skill",
            })

        # Summary improvement
        summary = profile_data.get("summary", "")
        if not summary or len(summary) < 50:
            suggestions.append({
                "action": "Improve Professional Summary",
                "detail": "Write a compelling 3–4 line professional summary with role-specific keywords.",
                "ats_impact": 2,
                "category": "content",
            })

        # Project descriptions
        projects = profile_data.get("projects", [])
        if len(projects) < 2:
            suggestions.append({
                "action": "Add More Projects",
                "detail": "Include at least 2–3 projects demonstrating relevant skills.",
                "ats_impact": 2,
                "category": "content",
            })

        # Certifications
        jd_skills = parsed_jd.get("skills", [])
        cloud_skills = {"aws", "azure", "gcp", "docker", "kubernetes", "terraform"}
        if cloud_skills & set(s.lower() for s in jd_skills):
            certs = profile_data.get("certifications", [])
            if len(certs) < 1:
                suggestions.append({
                    "action": "Add Cloud Certification",
                    "detail": "Obtain and list a relevant cloud certification (AWS/Azure/GCP).",
                    "ats_impact": 3,
                    "category": "certification",
                })

        return suggestions
