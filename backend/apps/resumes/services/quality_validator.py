import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class QualityValidator:
    """
    Service to validate overall resume completeness, missing required sections,
    low confidence parser extractions, and overall quality metrics.
    """

    def validate_quality_and_missing_fields(
        self,
        payload: Dict[str, Any],
        confidence_map: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scans payload and optional confidence scores for quality issues, missing fields,
        and low confidence extractions.
        Returns dictionary containing errors list and overall quality_score (0-100).
        """
        errors: List[Dict[str, Any]] = []
        quality_score = 100.0

        # 1. Check Missing Sections & Fields
        # Summary
        if not payload.get("summary"):
            quality_score -= 10
            errors.append({
                "type": "missing_field",
                "field": "summary",
                "value": "",
                "severity": "medium",
                "confidence": 95,
                "action": "recover",
                "reason": "Missing Summary section"
            })

        # Skills
        skills = payload.get("skills", [])
        if not skills or (isinstance(skills, list) and len(skills) == 0):
            quality_score -= 25
            errors.append({
                "type": "missing_field",
                "field": "skills",
                "value": "",
                "severity": "critical",
                "confidence": 99,
                "action": "recover",
                "reason": "Missing Skills section"
            })

        # Education
        education = payload.get("education", [])
        if not education or (isinstance(education, list) and len(education) == 0):
            quality_score -= 20
            errors.append({
                "type": "missing_field",
                "field": "education",
                "value": "",
                "severity": "high",
                "confidence": 98,
                "action": "recover",
                "reason": "Missing Education section"
            })

        # Experience
        experience = payload.get("experience", [])
        if not experience or (isinstance(experience, list) and len(experience) == 0):
            quality_score -= 20
            errors.append({
                "type": "missing_field",
                "field": "experience",
                "value": "",
                "severity": "high",
                "confidence": 95,
                "action": "recover",
                "reason": "Missing Work Experience section"
            })

        # Projects
        projects = payload.get("projects", [])
        if not projects or (isinstance(projects, list) and len(projects) == 0):
            quality_score -= 10
            errors.append({
                "type": "missing_field",
                "field": "projects",
                "value": "",
                "severity": "low",
                "confidence": 90,
                "action": "recover",
                "reason": "Missing Projects section"
            })

        # Certifications
        certs = payload.get("certifications", [])
        if not certs or (isinstance(certs, list) and len(certs) == 0):
            quality_score -= 5
            errors.append({
                "type": "missing_field",
                "field": "certifications",
                "value": "",
                "severity": "low",
                "confidence": 85,
                "action": "recover",
                "reason": "Missing Certifications section"
            })

        # 2. Low Confidence Score Evaluation (<70 -> review, <50 -> invalid)
        if confidence_map and isinstance(confidence_map, dict):
            for field, info in confidence_map.items():
                if isinstance(info, dict):
                    conf = info.get("confidence", 100.0)
                    val = info.get("value", "")
                    if conf < 50:
                        quality_score -= 5
                        errors.append({
                            "type": "low_confidence",
                            "field": field,
                            "value": str(val),
                            "severity": "high",
                            "confidence": conf,
                            "action": "reject",
                            "reason": f"Extracted value '{val}' for field '{field}' has critically low parser confidence ({conf}%)"
                        })
                    elif conf < 70:
                        quality_score -= 2
                        errors.append({
                            "type": "low_confidence",
                            "field": field,
                            "value": str(val),
                            "severity": "medium",
                            "confidence": conf,
                            "action": "review",
                            "reason": f"Extracted value '{val}' for field '{field}' has low parser confidence ({conf}%)"
                        })

        quality_score = max(0.0, round(quality_score, 1))
        return {
            "errors": errors,
            "quality_score": quality_score
        }
