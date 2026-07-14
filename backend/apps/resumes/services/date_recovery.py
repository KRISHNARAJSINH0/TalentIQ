import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DateRecovery:
    """
    Service to recover and normalize timeline dates:
    - Invert inverted start/end date ranges (e.g. 2024-2022 -> Swap to 2022-2024)
    - Normalize date status terms ('Current', 'Ongoing', 'Now' -> 'Present')
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

    def recover_dates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scans payload experience and education sections for timeline anomalies,
        swaps inverted dates, normalizes status terms, and returns updated recovered payload + recoveries audit records.
        """
        recovered = dict(payload)
        recoveries: List[Dict[str, Any]] = []

        # 1. Experience Date Recovery
        experience = recovered.get("experience", [])
        if isinstance(experience, list):
            new_exp = []
            for idx, exp in enumerate(experience):
                if isinstance(exp, dict):
                    comp_name = exp.get("company") or exp.get("employer") or f"Position #{idx+1}"
                    s_raw = exp.get("start_date") or exp.get("start_year")
                    e_raw = exp.get("end_date") or exp.get("end_year")

                    # Normalize Current/Ongoing -> Present
                    if str(e_raw).strip().lower() in ["current", "ongoing", "now"]:
                        exp["end_date"] = "Present"
                        if "end_year" in exp:
                            exp["end_year"] = "Present"
                        recoveries.append({
                            "type": "normalize",
                            "value": str(e_raw),
                            "from": f"experience[{idx}].end_date",
                            "to": f"experience[{idx}].end_date",
                            "confidence": 99,
                            "status": "recovered",
                            "reason": f"Normalized date status '{e_raw}' -> 'Present'"
                        })

                    s_year = self.extract_year(s_raw)
                    e_year = self.extract_year(e_raw)

                    # Swap Inverted Date Ranges (e.g. 2024-2022 -> 2022-2024)
                    if s_year and e_year and s_year > e_year and str(e_raw).strip().lower() not in ["present", "current", "ongoing", "now"]:
                        exp["start_date"] = str(e_raw)
                        exp["end_date"] = str(s_raw)
                        if "start_year" in exp:
                            exp["start_year"] = e_year
                        if "end_year" in exp:
                            exp["end_year"] = s_year

                        recoveries.append({
                            "type": "swap_dates",
                            "value": f"{s_raw} - {e_raw}",
                            "from": f"experience[{idx}]",
                            "to": f"experience[{idx}]",
                            "confidence": 96,
                            "status": "recovered",
                            "reason": f"Swapped inverted date range for '{comp_name}' ({s_raw}-{e_raw} -> {e_raw}-{s_raw})"
                        })

                    new_exp.append(exp)
                else:
                    new_exp.append(exp)

            recovered["experience"] = new_exp

        # 2. Education Date Recovery
        education = recovered.get("education", [])
        if isinstance(education, list):
            new_edu = []
            for idx, edu in enumerate(education):
                if isinstance(edu, dict):
                    inst_name = edu.get("institution") or edu.get("school") or f"Institution #{idx+1}"
                    s_raw = edu.get("start_year") or edu.get("start_date")
                    e_raw = edu.get("end_year") or edu.get("end_date")

                    s_year = self.extract_year(s_raw)
                    e_year = self.extract_year(e_raw)

                    if s_year and e_year and e_year < s_year:
                        edu["start_year"] = e_year
                        edu["end_year"] = s_year
                        recoveries.append({
                            "type": "swap_dates",
                            "value": f"{s_raw} - {e_raw}",
                            "from": f"education[{idx}]",
                            "to": f"education[{idx}]",
                            "confidence": 95,
                            "status": "recovered",
                            "reason": f"Swapped inverted education graduation years for '{inst_name}' ({s_raw}-{e_raw} -> {e_raw}-{s_raw})"
                        })

                    new_edu.append(edu)
                else:
                    new_edu.append(edu)

            recovered["education"] = new_edu

        return {
            "payload": recovered,
            "recoveries": recoveries
        }
