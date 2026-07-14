"""
Gap Analyzer — Identifies experience, education, certification,
and skill gaps between the candidate's profile and the JD requirements.
"""

import logging
from datetime import date

logger = logging.getLogger(__name__)


class GapAnalyzer:
    """
    Analyze gaps across multiple dimensions.
    """

    def analyze(self, profile_data: dict, parsed_jd: dict, skill_result: dict) -> dict:
        """
        Args:
            profile_data: serialized profile dict (experiences, educations, skills, certifications, projects)
            parsed_jd:    output from JDParser.parse()
            skill_result: output from SkillMatcher.match()

        Returns structured gap report.
        """
        gaps = {
            "skill_gaps": self._skill_gaps(skill_result),
            "experience_gap": self._experience_gap(profile_data, parsed_jd),
            "education_gap": self._education_gap(profile_data, parsed_jd),
            "certification_gaps": self._certification_gaps(profile_data, parsed_jd),
            "experience_match": 0,
            "education_match": 0,
        }

        gaps["experience_match"] = gaps["experience_gap"].get("match_pct", 80)
        gaps["education_match"] = gaps["education_gap"].get("match_pct", 80)

        return gaps

    # ── Skill Gaps ──────────────────────────────────────────────────
    def _skill_gaps(self, skill_result: dict) -> list:
        """Prioritize missing skills by importance."""
        missing = skill_result.get("missing", [])
        gaps = []

        # High-demand skills get High priority
        high_priority_keywords = {
            "python", "java", "javascript", "react", "django", "aws", "docker",
            "kubernetes", "sql", "postgresql", "mongodb", "git", "linux",
            "typescript", "nodejs", "spring", "springboot", "flask", "fastapi",
            "tensorflow", "pytorch", "spark", "kafka", "redis", "elasticsearch",
            "terraform", "cicd", "go", "rust", "angular", "vue",
        }

        for skill in missing:
            importance = "High" if skill.lower() in high_priority_keywords else "Medium"
            gaps.append({"skill": skill, "importance": importance})

        return gaps

    # ── Experience Gap ──────────────────────────────────────────────
    def _experience_gap(self, profile_data: dict, parsed_jd: dict) -> dict:
        """Compare candidate's years of experience vs JD requirement."""
        # Calculate candidate experience
        experiences = profile_data.get("experiences", [])
        total_months = 0

        for exp in experiences:
            start = exp.get("start_date")
            end = exp.get("end_date")
            if start:
                try:
                    if isinstance(start, str):
                        start = date.fromisoformat(start)
                    if end:
                        if isinstance(end, str):
                            end = date.fromisoformat(end)
                    else:
                        end = date.today()
                    months = (end.year - start.year) * 12 + (end.month - start.month)
                    total_months += max(months, 0)
                except (ValueError, TypeError):
                    continue

        candidate_years = round(total_months / 12, 1)

        # JD requirement
        exp_req = parsed_jd.get("experience_years", {})
        req_min = exp_req.get("min", 0)
        req_max = exp_req.get("max", 0)

        # Calculate match
        if req_min == 0:
            match_pct = 90
        elif candidate_years >= req_min:
            match_pct = min(100, 80 + int((candidate_years / max(req_max, req_min)) * 20))
        else:
            match_pct = max(30, int((candidate_years / req_min) * 80))

        return {
            "candidate_years": candidate_years,
            "required_min": req_min,
            "required_max": req_max,
            "meets_requirement": candidate_years >= req_min,
            "match_pct": min(match_pct, 100),
        }

    # ── Education Gap ───────────────────────────────────────────────
    def _education_gap(self, profile_data: dict, parsed_jd: dict) -> dict:
        """Compare education levels."""
        DEGREE_RANK = {
            "": 0, "Diploma": 1, "Bachelor's": 2, "Master's": 3, "PhD": 4,
        }

        # Candidate's highest education
        educations = profile_data.get("educations", [])
        candidate_level = ""
        candidate_field = ""
        for edu in educations:
            degree = edu.get("degree", "")
            for level_name in ["PhD", "Master's", "Bachelor's", "Diploma"]:
                if level_name.lower() in degree.lower() or (
                    level_name == "Bachelor's" and any(
                        t in degree.lower() for t in ["b.tech", "b.sc", "b.s.", "bachelor", "b.eng", "b.a."]
                    )
                ) or (
                    level_name == "Master's" and any(
                        t in degree.lower() for t in ["m.tech", "m.sc", "m.s.", "master", "mba", "m.eng"]
                    )
                ):
                    if DEGREE_RANK.get(level_name, 0) > DEGREE_RANK.get(candidate_level, 0):
                        candidate_level = level_name
                        candidate_field = edu.get("field_of_study", "")
                    break

        # JD requirement
        jd_edu = parsed_jd.get("education", {})
        required_level = jd_edu.get("level", "")

        cand_rank = DEGREE_RANK.get(candidate_level, 0)
        req_rank = DEGREE_RANK.get(required_level, 0)

        if req_rank == 0:
            match_pct = 95  # No specific requirement
        elif cand_rank >= req_rank:
            match_pct = 100
        elif cand_rank == req_rank - 1:
            match_pct = 75
        else:
            match_pct = 50

        return {
            "candidate_level": candidate_level,
            "candidate_field": candidate_field,
            "required_level": required_level,
            "required_field": jd_edu.get("field", ""),
            "meets_requirement": cand_rank >= req_rank,
            "match_pct": match_pct,
        }

    # ── Certification Gaps ──────────────────────────────────────────
    def _certification_gaps(self, profile_data: dict, parsed_jd: dict) -> list:
        """Identify certification-related gaps from JD requirements."""
        jd_text_lower = " ".join(parsed_jd.get("requirements", [])).lower()

        cert_keywords = {
            "AWS Certified": ["aws certified", "aws certification"],
            "Azure Certified": ["azure certified", "az-", "microsoft certified"],
            "GCP Certified": ["google cloud certified", "gcp certified"],
            "PMP": ["pmp", "project management professional"],
            "Scrum Master": ["csm", "scrum master", "psm"],
            "Kubernetes (CKA/CKAD)": ["cka", "ckad", "kubernetes certified"],
            "Terraform Associate": ["terraform certified", "terraform associate"],
            "CompTIA Security+": ["comptia", "security+"],
            "CISSP": ["cissp"],
        }

        # Candidate's certifications
        candidate_certs = set()
        for cert in profile_data.get("certifications", []):
            candidate_certs.add(cert.get("name", "").lower())

        missing_certs = []
        for cert_name, keywords in cert_keywords.items():
            for kw in keywords:
                if kw in jd_text_lower:
                    # Check if candidate has it
                    has_it = any(kw in c for c in candidate_certs)
                    if not has_it:
                        missing_certs.append(cert_name)
                    break

        return missing_certs
