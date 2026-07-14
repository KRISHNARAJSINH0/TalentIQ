import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SummaryGenerator:
    """
    Generates ATS-optimized professional summaries, bullet-point achievements, and cover letters.
    """

    def generate_summary(self, master_json: Dict[str, Any]) -> str:
        profile = master_json.get("profile", {})
        designation = profile.get("designation", profile.get("role", "Software Professional"))
        skills = master_json.get("skills", [])
        top_skills = ", ".join(skills[:4]) if skills else "modern software engineering practices"

        return (
            f"Results-driven {designation} with expertise in {top_skills}. "
            f"Demonstrated track record of delivering scalable, high-performance web applications, "
            f"optimizing backend systems, and collaborating in fast-paced Agile environments."
        )

    def generate_achievements(self, role: str) -> List[str]:
        return [
            f"Architected high-throughput backend APIs for {role}, reducing latency by 35%.",
            f"Spearheaded automated CI/CD deployment pipelines, accelerating release velocity by 50%.",
            f"Mentored cross-functional engineering teams and enforced rigorous test coverage standards."
        ]

    def generate_cover_letter(self, master_json: Dict[str, Any], company_name: str = "Target Company") -> str:
        profile = master_json.get("profile", {})
        name = profile.get("name", "Applicant")
        designation = profile.get("designation", "Software Engineer")

        return (
            f"Dear Hiring Team at {company_name},\n\n"
            f"I am writing to express my enthusiastic interest in the {designation} position. "
            f"With a proven background in building robust distributed systems and optimizing data pipelines, "
            f"I am confident in my ability to deliver immediate value to your team.\n\n"
            f"Sincerely,\n{name}"
        )
