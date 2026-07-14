import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ProfileChecker:
    """
    Service to validate project domain relevance, certification alignment, and semantic conflicts.
    - AI/Backend Engineer with non-technical projects (Fashion Catalog, Restaurant Menu)
    - AWS Engineer without AWS certification
    """

    def check_profile_consistency(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload projects and certifications for domain relevance mismatches.
        """
        issues: List[Dict[str, Any]] = []

        desig = str(payload.get("designation") or payload.get("current_designation") or payload.get("title") or "").lower()
        projects = payload.get("projects", [])
        certs = payload.get("certifications", [])

        if not isinstance(projects, list):
            projects = []
        if not isinstance(certs, list):
            certs = []

        proj_titles = [str(p if isinstance(p, str) else p.get("name") or p.get("title") or "").lower() for p in projects]
        cert_titles = [str(c if isinstance(c, str) else c.get("name") or c.get("title") or "").lower() for c in certs]

        # 1. Project Domain Alignment (Backend / AI Engineer with unrelated non-tech projects)
        if any(term in desig for term in ["backend", "ai engineer", "machine learning", "data engineer"]):
            if proj_titles and all(any(unrelated in pt for unrelated in ["fashion", "restaurant", "menu", "cooking", "salon"]) for pt in proj_titles):
                issues.append({
                    "type": "project_relevance",
                    "severity": "medium",
                    "reason": f"Projects ({', '.join(proj_titles[:2])}) show weak technical relevance for '{desig.title()}' role.",
                    "field": "projects"
                })

        # 2. Certification Check (AWS / Cloud Engineer with zero AWS certs)
        if any(term in desig for term in ["aws engineer", "cloud architect", "devops engineer"]):
            if not any("aws" in ct or "amazon" in ct or "cloud" in ct for ct in cert_titles):
                issues.append({
                    "type": "certification",
                    "severity": "low",
                    "reason": f"Role '{desig.title()}' suggests adding relevant cloud certifications (e.g. AWS Certified Solutions Architect).",
                    "field": "certifications"
                })

        return issues
