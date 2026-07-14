import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class TimelineChecker:
    """
    Service to validate date consistency across resume sections:
    - Date range overlaps between experience items
    - Multiple active current positions
    - Pre-graduation senior experience conflicts
    - Education start/end vs work experience timeline conflicts
    """

    @staticmethod
    def extract_year(value: Any) -> Optional[int]:
        if not value:
            return None
        val_str = str(value).strip().lower()
        if val_str in ["present", "current", "ongoing", "now"]:
            return 2026
        match = re.search(r"\b(19|20)\d{2}\b", val_str)
        return int(match.group(0)) if match else None

    def check_timeline_consistency(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyzes payload timeline dates and returns detected consistency issues.
        """
        issues: List[Dict[str, Any]] = []

        experience = payload.get("experience", [])
        if not isinstance(experience, list):
            experience = []

        education = payload.get("education", [])
        if not isinstance(education, list):
            education = []

        # 1. Multiple active current positions
        current_jobs = []
        for exp in experience:
            if isinstance(exp, dict):
                end_val = str(exp.get("end_date") or exp.get("end_year") or "").strip().lower()
                if end_val in ["present", "current", "ongoing", "now"]:
                    current_jobs.append(exp.get("company") or exp.get("employer") or "Position")

        if len(current_jobs) > 1:
            issues.append({
                "type": "timeline",
                "severity": "medium",
                "reason": f"Multiple active current positions detected ({', '.join(current_jobs[:3])}). Verify if candidate holds concurrent roles.",
                "field": "experience"
            })

        # 2. Overlapping Experience Intervals
        parsed_intervals = []
        for idx, exp in enumerate(experience):
            if isinstance(exp, dict):
                s_year = self.extract_year(exp.get("start_date") or exp.get("start_year"))
                e_year = self.extract_year(exp.get("end_date") or exp.get("end_year"))
                if s_year and e_year and s_year <= e_year:
                    parsed_intervals.append((s_year, e_year, exp.get("company") or f"Job #{idx+1}"))

        parsed_intervals.sort(key=lambda x: x[0])
        for i in range(len(parsed_intervals) - 1):
            s1, e1, c1 = parsed_intervals[i]
            s2, e2, c2 = parsed_intervals[i+1]
            if e1 > s2 and e1 < 2026 and e2 < 2026:  # Overlap between past jobs
                issues.append({
                    "type": "timeline",
                    "severity": "medium",
                    "reason": f"Employment timeline overlap between '{c1}' ({s1}-{e1}) and '{c2}' ({s2}-{e2}).",
                    "field": "experience"
                })

        # 3. Education vs Work Experience Pre-graduation Conflict
        grad_year = None
        for edu in education:
            if isinstance(edu, dict):
                ey = self.extract_year(edu.get("end_year") or edu.get("end_date"))
                if ey and (grad_year is None or ey > grad_year):
                    grad_year = ey

        if grad_year:
            for exp in experience:
                if isinstance(exp, dict):
                    s_year = self.extract_year(exp.get("start_date") or exp.get("start_year"))
                    title = str(exp.get("designation") or exp.get("title") or "").lower()
                    if s_year and s_year < grad_year - 4 and any(sr in title for sr in ["senior", "lead", "architect", "head", "director", "vp"]):
                        issues.append({
                            "type": "timeline",
                            "severity": "high",
                            "reason": f"Senior role ('{exp.get('designation')}') starts in {s_year}, significantly prior to degree graduation ({grad_year}).",
                            "field": "experience"
                        })

        return issues
