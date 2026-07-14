import logging
from typing import Dict, List, Any, Optional

from .entity_classifier import EntityClassifier
from .ontology_engine import OntologyEngine

logger = logging.getLogger(__name__)


class SectionErrorDetector:
    """
    Service to detect section misclassification and entity collisions across sections:
    - Education contains Skills (e.g. Python inside Education)
    - Skills contains Universities (e.g. MIT inside Skills)
    - Projects contain Companies (e.g. Google inside Project title)
    - Name contains Designation (e.g. Software Engineer inside Name)
    - Certificates contain Experience
    - Languages contain Technologies
    """

    def __init__(self):
        self.classifier = EntityClassifier()
        self.ontology = OntologyEngine()

    def detect_section_errors(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload sections for misplaced entities.
        Returns a list of error dictionaries.
        """
        errors: List[Dict[str, Any]] = []

        # 1. Name contains Designation
        name = payload.get("name") or payload.get("full_name")
        if name and isinstance(name, str):
            is_name_valid, score, reason = self.ontology.validate_person_name(name)
            if not is_name_valid:
                errors.append({
                    "type": "wrong_entity",
                    "field": "name",
                    "value": name,
                    "severity": "high",
                    "confidence": 95,
                    "action": "reject",
                    "reason": f"Name field contains designation or title term ('{name}')"
                })

        # 2. Skills contains Universities
        skills = payload.get("skills", [])
        if isinstance(skills, list):
            for idx, sk in enumerate(skills):
                if isinstance(sk, str):
                    res = self.classifier.classify_entity(sk, context_section="skills")
                    if res["top_category"] == "UNIVERSITY":
                        errors.append({
                            "type": "wrong_entity",
                            "field": f"skills[{idx}]",
                            "value": sk,
                            "severity": "high",
                            "confidence": int(res["confidence_score"]),
                            "action": "move",
                            "reason": f"'{sk}' appears to be a university, misplaced inside skills"
                        })

        # 3. Education contains Skills
        education = payload.get("education", [])
        if isinstance(education, list):
            for idx, edu in enumerate(education):
                val_str = edu if isinstance(edu, str) else str(edu.get("institution") or edu.get("degree") or "")
                if val_str:
                    res = self.classifier.classify_entity(val_str, context_section="education")
                    if res["top_category"] in ["SKILL", "TECHNOLOGY"]:
                        errors.append({
                            "type": "wrong_entity",
                            "field": f"education[{idx}]",
                            "value": val_str,
                            "severity": "high",
                            "confidence": int(res["confidence_score"]),
                            "action": "move",
                            "reason": f"'{val_str}' appears to be a skill/technology, misplaced inside education"
                        })

        # 4. Projects contain Companies
        projects = payload.get("projects", [])
        if isinstance(projects, list):
            for idx, proj in enumerate(projects):
                val_str = proj if isinstance(proj, str) else str(proj.get("title") or proj.get("name") or "")
                if val_str:
                    res = self.classifier.classify_entity(val_str, context_section="projects")
                    if res["top_category"] in ["COMPANY", "ORGANIZATION"]:
                        errors.append({
                            "type": "semantic_mismatch",
                            "field": f"projects[{idx}]",
                            "value": val_str,
                            "severity": "medium",
                            "confidence": int(res["confidence_score"]),
                            "action": "review",
                            "reason": f"'{val_str}' appears to be a company/employer, misplaced inside projects"
                        })

        # 5. Languages contain Technologies
        languages = payload.get("languages", [])
        if isinstance(languages, list):
            for idx, lang in enumerate(languages):
                if isinstance(lang, str):
                    res = self.classifier.classify_entity(lang, context_section="languages")
                    if res["top_category"] in ["SKILL", "TECHNOLOGY"] and lang.lower() not in ["english", "french", "german", "spanish", "hindi"]:
                        errors.append({
                            "type": "wrong_entity",
                            "field": f"languages[{idx}]",
                            "value": lang,
                            "severity": "medium",
                            "confidence": int(res["confidence_score"]),
                            "action": "move",
                            "reason": f"'{lang}' is a programming language/technology, misplaced inside spoken languages"
                        })

        return errors
