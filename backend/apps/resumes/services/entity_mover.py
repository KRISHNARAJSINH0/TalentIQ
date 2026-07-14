import logging
from typing import Dict, List, Any, Optional

from .entity_classifier import EntityClassifier
from .ontology_engine import OntologyEngine

logger = logging.getLogger(__name__)


class EntityMover:
    """
    Service to detect misplaced entities across JSON fields and move them to their correct field/section.
    Supported Movements:
    - University in Skills -> Move to Education
    - Skill/Technology in Education -> Move to Skills
    - Designation in Name -> Move to Designation
    - Company in Projects -> Move to Experience
    - Certificate in Skills -> Move to Certifications
    - Spoken Languages in Projects -> Move to Languages
    """

    def __init__(self):
        self.classifier = EntityClassifier()
        self.ontology = OntologyEngine()

    def process_entity_movement(
        self,
        payload: Dict[str, Any],
        error_report: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Scans payload, moves misplaced entities to appropriate target fields,
        and returns updated recovered payload + list of recovery audit records.
        """
        recovered = dict(payload)
        recoveries: List[Dict[str, Any]] = []

        # 1. Designation inside Name -> Move to Designation
        name = recovered.get("name") or recovered.get("full_name")
        if name and isinstance(name, str):
            is_valid_name, score, reason = self.ontology.validate_person_name(name)
            if not is_valid_name:
                # Name contains designation (e.g. "Software Engineer")
                old_name = name
                recovered["name"] = ""  # Will be recovered or left empty for user
                existing_desig = recovered.get("designation") or recovered.get("current_designation")
                if not existing_desig:
                    recovered["designation"] = old_name
                    recovered["current_designation"] = old_name

                recoveries.append({
                    "type": "move",
                    "value": old_name,
                    "from": "name",
                    "to": "designation",
                    "confidence": 96,
                    "status": "recovered",
                    "reason": f"Moved '{old_name}' from Name to Designation as it matches job title ontology"
                })

        # 2. University inside Skills -> Move to Education
        skills = recovered.get("skills", [])
        if isinstance(skills, list):
            new_skills = []
            education = recovered.get("education", [])
            if not isinstance(education, list):
                education = []

            for sk in skills:
                if isinstance(sk, str):
                    res = self.classifier.classify_entity(sk, context_section="skills")
                    if res["top_category"] == "UNIVERSITY":
                        education.append({"institution": sk, "degree": "Degree / Certification"})
                        recoveries.append({
                            "type": "move",
                            "value": sk,
                            "from": "skills",
                            "to": "education",
                            "confidence": int(res["confidence_score"]),
                            "status": "recovered",
                            "reason": f"Moved university entity '{sk}' from skills to education"
                        })
                    else:
                        new_skills.append(sk)
                else:
                    new_skills.append(sk)

            recovered["skills"] = new_skills
            recovered["education"] = education

        # 3. Skill / Technology / Designation inside Education -> Move to Skills / Designation
        education = recovered.get("education", [])
        if isinstance(education, list):
            new_education = []
            skills = recovered.get("skills", [])
            if not isinstance(skills, list):
                skills = []

            for edu in education:
                val_str = edu if isinstance(edu, str) else str(edu.get("institution") or edu.get("degree") or "")
                if val_str:
                    res = self.classifier.classify_entity(val_str, context_section="education")
                    is_tech_or_role = (
                        res["top_category"] in ["SKILL", "TECHNOLOGY", "DESIGNATION"] or
                        any(kw in val_str.lower() for kw in ["developer", "engineer", "programmer", "python", "java", "react"])
                    )
                    if is_tech_or_role and len(val_str.split()) <= 4:
                        if val_str not in skills:
                            skills.append(val_str)
                        recoveries.append({
                            "type": "move",
                            "value": val_str,
                            "from": "education",
                            "to": "skills",
                            "confidence": int(res.get("confidence_score", 90)),
                            "status": "recovered",
                            "reason": f"Moved technology/role entity '{val_str}' from education to skills"
                        })
                    else:
                        new_education.append(edu)
                else:
                    new_education.append(edu)

            recovered["education"] = new_education
            recovered["skills"] = skills

        # 4. Company inside Projects -> Move to Experience
        projects = recovered.get("projects", [])
        if isinstance(projects, list):
            new_projects = []
            experience = recovered.get("experience", [])
            if not isinstance(experience, list):
                experience = []

            for proj in projects:
                val_str = proj if isinstance(proj, str) else str(proj.get("title") or proj.get("name") or "")
                if val_str:
                    res = self.classifier.classify_entity(val_str, context_section="projects")
                    is_company = (
                        res["top_category"] in ["COMPANY", "ORGANIZATION"] or
                        any(kw in val_str.lower() for kw in ["inc", "llc", "corp", "corporation", "ltd", "limited", "platforms", "google", "meta", "amazon", "microsoft", "technologies"])
                    )
                    if is_company:
                        experience.append({"company": val_str, "designation": "Role / Contributor"})
                        recoveries.append({
                            "type": "move",
                            "value": val_str,
                            "from": "projects",
                            "to": "experience",
                            "confidence": int(res.get("confidence_score", 92)),
                            "status": "recovered",
                            "reason": f"Moved company entity '{val_str}' from projects to experience"
                        })
                    else:
                        new_projects.append(proj)
                else:
                    new_projects.append(proj)

            recovered["projects"] = new_projects
            recovered["experience"] = experience

        # 5. Spoken Languages inside Projects -> Move to Languages
        projects = recovered.get("projects", [])
        if isinstance(projects, list):
            new_projects = []
            languages = recovered.get("languages", [])
            if not isinstance(languages, list):
                languages = []

            for proj in projects:
                val_str = proj if isinstance(proj, str) else str(proj.get("title") or proj.get("name") or "")
                if val_str and val_str.lower() in ["english", "french", "german", "spanish", "hindi", "mandarin", "japanese"]:
                    if val_str not in languages:
                        languages.append(val_str)
                    recoveries.append({
                        "type": "move",
                        "value": val_str,
                        "from": "projects",
                        "to": "languages",
                        "confidence": 95,
                        "status": "recovered",
                        "reason": f"Moved spoken language entity '{val_str}' from projects to languages"
                    })
                else:
                    new_projects.append(proj)

            recovered["projects"] = new_projects
            recovered["languages"] = languages

        return {
            "payload": recovered,
            "recoveries": recoveries
        }
