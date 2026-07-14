"""
Recommendation Engine — Generates actionable improvement suggestions.

Produces learning paths, interview readiness scores, certification
recommendations, and salary estimates based on real-world role data.
"""

import logging

logger = logging.getLogger(__name__)

# Real-world salary data by role (USD k/yr)
SALARY_DATA = {
    "software engineer":     {"min": 85, "max": 160, "currency": "$", "suffix": "k/yr"},
    "senior software engineer": {"min": 130, "max": 210, "currency": "$", "suffix": "k/yr"},
    "frontend developer":    {"min": 75, "max": 145, "currency": "$", "suffix": "k/yr"},
    "backend developer":     {"min": 85, "max": 155, "currency": "$", "suffix": "k/yr"},
    "full stack developer":  {"min": 80, "max": 150, "currency": "$", "suffix": "k/yr"},
    "devops engineer":       {"min": 95, "max": 170, "currency": "$", "suffix": "k/yr"},
    "data scientist":        {"min": 95, "max": 175, "currency": "$", "suffix": "k/yr"},
    "data analyst":          {"min": 65, "max": 115, "currency": "$", "suffix": "k/yr"},
    "data engineer":         {"min": 90, "max": 165, "currency": "$", "suffix": "k/yr"},
    "ml engineer":           {"min": 110, "max": 195, "currency": "$", "suffix": "k/yr"},
    "ai engineer":           {"min": 120, "max": 210, "currency": "$", "suffix": "k/yr"},
    "product manager":       {"min": 100, "max": 180, "currency": "$", "suffix": "k/yr"},
    "ux designer":           {"min": 70, "max": 135, "currency": "$", "suffix": "k/yr"},
    "qa engineer":           {"min": 65, "max": 120, "currency": "$", "suffix": "k/yr"},
    "cloud architect":       {"min": 140, "max": 220, "currency": "$", "suffix": "k/yr"},
    "security engineer":     {"min": 100, "max": 180, "currency": "$", "suffix": "k/yr"},
    "mobile developer":      {"min": 80, "max": 155, "currency": "$", "suffix": "k/yr"},
    "site reliability engineer": {"min": 110, "max": 190, "currency": "$", "suffix": "k/yr"},
    "technical lead":        {"min": 130, "max": 200, "currency": "$", "suffix": "k/yr"},
    "engineering manager":   {"min": 150, "max": 240, "currency": "$", "suffix": "k/yr"},
}

# Learning paths by skill category
LEARNING_PATHS = {
    "aws": {"course": "AWS Solutions Architect Associate", "platform": "AWS Training", "hours": 40},
    "docker": {"course": "Docker & Kubernetes: The Practical Guide", "platform": "Udemy", "hours": 24},
    "kubernetes": {"course": "Certified Kubernetes Administrator (CKA)", "platform": "Linux Foundation", "hours": 40},
    "terraform": {"course": "HashiCorp Terraform Associate", "platform": "HashiCorp", "hours": 20},
    "react": {"course": "React – The Complete Guide", "platform": "Udemy/Coursera", "hours": 30},
    "python": {"course": "Python for Everybody", "platform": "Coursera", "hours": 25},
    "java": {"course": "Java Programming Masterclass", "platform": "Udemy", "hours": 40},
    "typescript": {"course": "Understanding TypeScript", "platform": "Udemy", "hours": 15},
    "sql": {"course": "The Complete SQL Bootcamp", "platform": "Udemy", "hours": 12},
    "mongodb": {"course": "MongoDB University - Developer Path", "platform": "MongoDB University", "hours": 20},
    "redis": {"course": "Redis University - Developer Certificate", "platform": "Redis University", "hours": 15},
    "graphql": {"course": "GraphQL by Example", "platform": "Udemy", "hours": 10},
    "tensorflow": {"course": "DeepLearning.AI TensorFlow Developer", "platform": "Coursera", "hours": 35},
    "pytorch": {"course": "Deep Learning with PyTorch", "platform": "Coursera", "hours": 30},
    "spark": {"course": "Apache Spark with Scala", "platform": "Databricks Academy", "hours": 25},
    "kafka": {"course": "Apache Kafka for Beginners", "platform": "Confluent", "hours": 15},
    "system design": {"course": "Grokking System Design", "platform": "Educative", "hours": 30},
    "cicd": {"course": "CI/CD Pipeline with Jenkins & GitHub Actions", "platform": "Udemy", "hours": 12},
    "linux": {"course": "Linux Fundamentals", "platform": "Linux Foundation", "hours": 20},
    "elasticsearch": {"course": "Complete Guide to Elasticsearch", "platform": "Elastic Training", "hours": 18},
    "golang": {"course": "Go: The Complete Developer's Guide", "platform": "Udemy", "hours": 20},
    "rust": {"course": "The Rust Programming Language", "platform": "Rust-lang.org", "hours": 30},
    "flutter": {"course": "Flutter & Dart – The Complete Guide", "platform": "Udemy", "hours": 35},
    "angular": {"course": "Angular – The Complete Guide", "platform": "Udemy", "hours": 30},
    "vue": {"course": "Vue.js 3 – The Complete Guide", "platform": "Udemy", "hours": 25},
    "nextjs": {"course": "Next.js & React – The Complete Guide", "platform": "Udemy", "hours": 20},
}


class RecommendationEngine:
    """
    Generate actionable recommendations from analysis results.
    """

    def recommend(self, parsed_jd: dict, skill_result: dict, gap_result: dict) -> dict:
        """
        Returns recommendations, interview readiness, and salary estimate.
        """
        missing_skills = skill_result.get("missing", [])

        return {
            "learning_path": self._learning_path(missing_skills),
            "interview_readiness": self._interview_readiness(skill_result, gap_result, parsed_jd),
            "salary_estimate": self._salary_estimate(parsed_jd),
            "strengths": self._identify_strengths(skill_result, gap_result),
            "weaknesses": self._identify_weaknesses(skill_result, gap_result, parsed_jd),
        }

    def _learning_path(self, missing_skills: list) -> list:
        """Build a prioritized learning roadmap."""
        path = []
        for skill in missing_skills[:10]:
            skill_lower = skill.lower()
            info = LEARNING_PATHS.get(skill_lower, {
                "course": f"Learn {skill} – Comprehensive Course",
                "platform": "Online Learning Platform",
                "hours": 20,
            })
            path.append({
                "skill": skill,
                "course": info["course"],
                "platform": info["platform"],
                "estimated_hours": info["hours"],
            })
        return path

    def _interview_readiness(self, skill_result: dict, gap_result: dict, parsed_jd: dict) -> dict:
        """Calculate interview readiness score and identify missing areas."""
        skills_pct = skill_result.get("skills_match", 0)
        exp_pct = gap_result.get("experience_match", 0)
        edu_pct = gap_result.get("education_match", 0)

        # Weighted score
        score = round(skills_pct * 0.45 + exp_pct * 0.35 + edu_pct * 0.20)
        score = max(0, min(100, score))

        # Missing interview areas
        missing_areas = []
        missing_skills = skill_result.get("missing", [])

        # Check for system design
        jd_text = " ".join(parsed_jd.get("responsibilities", [])).lower()
        if any(kw in jd_text for kw in ["system design", "architecture", "scalable", "distributed"]):
            if "system design" in [s.lower() for s in missing_skills]:
                missing_areas.append("System Design")

        # Check for specific tech areas
        for skill in missing_skills[:5]:
            missing_areas.append(skill)

        # Experience gap
        exp_gap = gap_result.get("experience_gap", {})
        if not exp_gap.get("meets_requirement", True):
            missing_areas.append(f"Experience ({exp_gap.get('required_min', 0)}+ years required)")

        return {
            "score": score,
            "missing_areas": missing_areas[:8],
            "ready": score >= 70,
        }

    def _salary_estimate(self, parsed_jd: dict) -> dict:
        """Estimate salary range based on JD role title."""
        title = parsed_jd.get("title", "").lower()

        # Find best matching role
        best_match = None
        for role_key, data in SALARY_DATA.items():
            if role_key in title:
                best_match = data
                break

        if not best_match:
            # Try partial matching
            for role_key, data in SALARY_DATA.items():
                role_words = role_key.split()
                if any(word in title for word in role_words if len(word) > 3):
                    best_match = data
                    break

        if not best_match:
            best_match = SALARY_DATA["software engineer"]

        # Adjust for seniority
        seniority = parsed_jd.get("seniority", "Mid-Level")
        multiplier = {
            "Intern": 0.4, "Junior": 0.7, "Mid-Level": 1.0,
            "Senior": 1.3, "Principal": 1.6,
        }.get(seniority, 1.0)

        return {
            "min": round(best_match["min"] * multiplier),
            "max": round(best_match["max"] * multiplier),
            "currency": best_match["currency"],
            "suffix": best_match["suffix"],
            "seniority_adjustment": seniority,
        }

    def _identify_strengths(self, skill_result: dict, gap_result: dict) -> list:
        """Identify candidate strengths."""
        strengths = []

        matching = skill_result.get("matching", [])
        if len(matching) >= 5:
            strengths.append(f"Strong skill alignment ({len(matching)} matching skills)")
        elif len(matching) >= 3:
            strengths.append(f"Good skill coverage ({len(matching)} matching skills)")

        # Top matching skills
        for skill in matching[:5]:
            strengths.append(skill)

        # Bonus skills
        bonus = skill_result.get("bonus", [])
        if len(bonus) >= 3:
            strengths.append(f"Additional expertise: {', '.join(bonus[:3])}")

        # Experience
        exp_gap = gap_result.get("experience_gap", {})
        if exp_gap.get("meets_requirement", False):
            strengths.append(f"Meets experience requirement ({exp_gap.get('candidate_years', 0)} years)")

        # Education
        edu_gap = gap_result.get("education_gap", {})
        if edu_gap.get("meets_requirement", False) and edu_gap.get("candidate_level"):
            strengths.append(f"Education: {edu_gap['candidate_level']}")

        return strengths[:10]

    def _identify_weaknesses(self, skill_result: dict, gap_result: dict, parsed_jd: dict) -> list:
        """Identify candidate weaknesses."""
        weaknesses = []

        missing = skill_result.get("missing", [])
        if len(missing) >= 5:
            weaknesses.append(f"{len(missing)} required skills not on resume")
        elif len(missing) >= 2:
            weaknesses.append(f"Missing key skills: {', '.join(missing[:4])}")

        # Experience gap
        exp_gap = gap_result.get("experience_gap", {})
        if not exp_gap.get("meets_requirement", True):
            weaknesses.append(
                f"Experience gap: {exp_gap.get('candidate_years', 0)} years "
                f"vs {exp_gap.get('required_min', 0)}+ required"
            )

        # Education gap
        edu_gap = gap_result.get("education_gap", {})
        if not edu_gap.get("meets_requirement", True):
            weaknesses.append(
                f"Education: {edu_gap.get('candidate_level', 'N/A')} "
                f"vs {edu_gap.get('required_level', 'N/A')} required"
            )

        # Certification gaps
        cert_gaps = gap_result.get("certification_gaps", [])
        if cert_gaps:
            weaknesses.append(f"Missing certifications: {', '.join(cert_gaps[:3])}")

        return weaknesses[:8]
