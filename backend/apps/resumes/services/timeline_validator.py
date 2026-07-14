import re
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class TimelineValidator:
    """
    Service to validate employment & education timelines, detecting:
    - Negative experience duration (Start date > End date e.g. 2023-2022)
    - Multiple active current companies (e.g. 2020-present & 2021-present)
    - Experience date overlaps across positions
    - Impossible future graduation dates
    """

    @staticmethod
    def extract_year(value: Any) -> Optional[int]:
        """Parses a 4-digit year or converts 'present'/'current' to current year."""
        if not value:
            return None
        val_str = str(value).strip().lower()
        if val_str in ["present", "current", "ongoing", "now"]:
            return 2026
        match = re.search(r"\b(19|20)\d{2}\b", val_str)
        return int(match.group(0)) if match else None

    def validate_timelines(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload experience and education sections for timeline anomalies.
        Returns a list of error dictionaries.
        """
        errors: List[Dict[str, Any]] = []

        # 1. Experience Timeline Checks
        experience = payload.get("experience", [])
        if isinstance(experience, list):
            current_companies: List[Tuple[int, str]] = []
            parsed_intervals: List[Tuple[int, int, int, str]] = []

            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    comp_name = exp.get("company") or exp.get("employer") or f"Company #{idx+1}"
                    s_raw = exp.get("start_date") or exp.get("start_year")
                    e_raw = exp.get("end_date") or exp.get("end_year")

                    s_year = self.extract_year(s_raw)
                    e_year = self.extract_year(e_raw)
                    is_current = str(e_raw).strip().lower() in ["present", "current", "ongoing", "now"]

                    if is_current:
                        current_companies.append((idx, comp_name))

                    if s_year and e_year:
                        # Negative Duration Error (e.g. 2023-2022)
                        if s_year > e_year and not is_current:
                            errors.append({
                                "type": "timeline_error",
                                "field": f"experience[{idx}]",
                                "value": f"{s_raw} - {e_raw}",
                                "severity": "critical",
                                "confidence": 98,
                                "action": "reject",
                                "reason": f"Negative duration for position at '{comp_name}': start date ({s_year}) is after end date ({e_year})"
                            })
                        else:
                            parsed_intervals.append((s_year, e_year, idx, comp_name))

            # Check Multiple Current Companies
            if len(current_companies) > 1:
                names = ", ".join([c[1] for c in current_companies])
                errors.append({
                    "type": "timeline_error",
                    "field": "experience",
                    "value": names,
                    "severity": "high",
                    "confidence": 85,
                    "action": "review",
                    "reason": f"Multiple active current positions detected at: {names}"
                })

            # Check Overlapping Experience Intervals
            parsed_intervals.sort(key=lambda x: x[0])
            for i in range(len(parsed_intervals) - 1):
                s1, e1, idx1, c1 = parsed_intervals[i]
                s2, e2, idx2, c2 = parsed_intervals[i+1]
                # If second job starts significantly before first job ends (overlap > 1 year)
                if s2 < e1 and (e1 - s2) >= 1:
                    errors.append({
                        "type": "timeline_error",
                        "field": f"experience[{idx2}]",
                        "value": f"{s2} - {e2}",
                        "severity": "medium",
                        "confidence": 80,
                        "action": "review",
                        "reason": f"Employment dates for '{c2}' ({s2}-{e2}) overlap with '{c1}' ({s1}-{e1})"
                    })

        # 2. Education Timeline Checks
        education = payload.get("education", [])
        if isinstance(education, list):
            for idx, edu in enumerate(education):
                if isinstance(edu, dict):
                    inst_name = edu.get("institution") or edu.get("school") or f"Institution #{idx+1}"
                    s_raw = edu.get("start_year") or edu.get("start_date")
                    e_raw = edu.get("end_year") or edu.get("end_date")

                    s_year = self.extract_year(s_raw)
                    e_year = self.extract_year(e_raw)

                    if s_year and e_year and e_year < s_year:
                        errors.append({
                            "type": "timeline_error",
                            "field": f"education[{idx}]",
                            "value": f"{s_raw} - {e_raw}",
                            "severity": "critical",
                            "confidence": 95,
                            "action": "review",
                            "reason": f"Invalid graduation dates for '{inst_name}': end year ({e_year}) is before start year ({s_year})"
                        })

                    if e_year and e_year > 2032:
                        errors.append({
                            "type": "timeline_error",
                            "field": f"education[{idx}].end_year",
                            "value": str(e_raw),
                            "severity": "high",
                            "confidence": 90,
                            "action": "review",
                            "reason": f"Distant future graduation year ({e_year}) detected for '{inst_name}'"
                        })

        return errors
