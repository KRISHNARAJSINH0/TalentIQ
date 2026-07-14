import logging

logger = logging.getLogger(__name__)


class SkillGapEngine:
    """
    Computes gaps between candidate's current verified skills and the target role's in-demand skills.
    """
    @staticmethod
    def identify_gaps(profile_data: dict, predicted_role: str) -> list:
        role_lower = predicted_role.lower()
        current_skills = [s.get("skill_name", "").lower() for s in profile_data.get("skills", [])]

        # Standard requirements per role
        role_requirements = {
            "backend engineer": [
                {"skill": "Redis", "importance": "High"},
                {"skill": "AWS", "importance": "High"},
                {"skill": "Kubernetes", "importance": "Medium"},
                {"skill": "Terraform", "importance": "Medium"},
                {"skill": "CI/CD", "importance": "High"},
                {"skill": "System Design", "importance": "High"}
            ],
            "frontend developer": [
                {"skill": "React", "importance": "High"},
                {"skill": "TypeScript", "importance": "High"},
                {"skill": "Next.js", "importance": "Medium"},
                {"skill": "TailwindCSS", "importance": "Medium"},
                {"skill": "Git", "importance": "High"},
                {"skill": "Figma", "importance": "Low"}
            ],
            "frontend engineer": [
                {"skill": "React", "importance": "High"},
                {"skill": "TypeScript", "importance": "High"},
                {"skill": "Next.js", "importance": "Medium"},
                {"skill": "TailwindCSS", "importance": "Medium"},
                {"skill": "Git", "importance": "High"},
                {"skill": "Figma", "importance": "Low"}
            ],
            "full stack developer": [
                {"skill": "React", "importance": "High"},
                {"skill": "Node.js", "importance": "High"},
                {"skill": "Docker", "importance": "Medium"},
                {"skill": "PostgreSQL", "importance": "High"},
                {"skill": "System Design", "importance": "Medium"},
                {"skill": "Git", "importance": "High"}
            ],
            "full stack engineer": [
                {"skill": "React", "importance": "High"},
                {"skill": "Node.js", "importance": "High"},
                {"skill": "Docker", "importance": "Medium"},
                {"skill": "PostgreSQL", "importance": "High"},
                {"skill": "System Design", "importance": "Medium"},
                {"skill": "Git", "importance": "High"}
            ],
            "devops engineer": [
                {"skill": "Docker", "importance": "High"},
                {"skill": "Kubernetes", "importance": "High"},
                {"skill": "Terraform", "importance": "High"},
                {"skill": "CI/CD", "importance": "High"},
                {"skill": "AWS", "importance": "High"},
                {"skill": "Prometheus", "importance": "Medium"}
            ],
            "data scientist": [
                {"skill": "Python", "importance": "High"},
                {"skill": "SQL", "importance": "High"},
                {"skill": "Machine Learning", "importance": "High"},
                {"skill": "Deep Learning", "importance": "Medium"},
                {"skill": "Pandas", "importance": "High"},
                {"skill": "Tableau", "importance": "Medium"}
            ],
            "software engineer": [
                {"skill": "Docker", "importance": "High"},
                {"skill": "AWS / Cloud", "importance": "High"},
                {"skill": "CI/CD Pipelines", "importance": "Medium"},
                {"skill": "System Architecture", "importance": "High"},
                {"skill": "Testing / PyTest", "importance": "Medium"}
            ],
            "ml engineer": [
                {"skill": "LangChain", "importance": "High"},
                {"skill": "Agentic AI", "importance": "High"},
                {"skill": "Vector DBs (Pinecone/Milvus)", "importance": "High"},
                {"skill": "Kubernetes", "importance": "Medium"},
                {"skill": "Model Quantization", "importance": "Medium"}
            ],
            "ai engineer": [
                {"skill": "LangChain / LlamaIndex", "importance": "High"},
                {"skill": "Agentic AI Frameworks", "importance": "High"},
                {"skill": "Vector Databases", "importance": "High"},
                {"skill": "MCP (Model Context Protocol)", "importance": "Medium"},
                {"skill": "LLM Fine-tuning", "importance": "Medium"}
            ],
            "civil engineer": [
                {"skill": "BIM (Building Information Modeling)", "importance": "High"},
                {"skill": "LEED Certification", "importance": "Medium"},
                {"skill": "Project Management (PMP)", "importance": "High"},
                {"skill": "SAP2000", "importance": "Medium"}
            ],
            "doctor": [
                {"skill": "Telemedicine Protocols", "importance": "High"},
                {"skill": "Digital Health Integration", "importance": "Medium"},
                {"skill": "Medical Leadership", "importance": "Medium"},
                {"skill": "Advanced Clinical Trials", "importance": "Low"}
            ],
            "teacher": [
                {"skill": "LMS Administration (Canvas)", "importance": "High"},
                {"skill": "Digital Pedagogy", "importance": "High"},
                {"skill": "EdTech Tool Integration", "importance": "High"},
                {"skill": "Interactive Courseware Design", "importance": "Medium"}
            ],
            "lawyer": [
                {"skill": "Legal AI Tools", "importance": "High"},
                {"skill": "Compliance Risk Management", "importance": "High"},
                {"skill": "Privacy Law (GDPR/CCPA)", "importance": "High"},
                {"skill": "Blockchain Legalities", "importance": "Low"}
            ],
            "ui ux designer": [
                {"skill": "Webflow / Framer", "importance": "High"},
                {"skill": "User Research Methods", "importance": "High"},
                {"skill": "Design System Architecture", "importance": "High"},
                {"skill": "Motion Design", "importance": "Medium"}
            ],
            "designer": [
                {"skill": "Webflow", "importance": "High"},
                {"skill": "Framer", "importance": "High"},
                {"skill": "User Research Methods", "importance": "Medium"},
                {"skill": "Motion Design", "importance": "Medium"}
            ],
            "data analyst": [
                {"skill": "Advanced SQL & CTEs", "importance": "High"},
                {"skill": "dbt (Data Build Tool)", "importance": "High"},
                {"skill": "Python for Automation", "importance": "Medium"},
                {"skill": "Big Data (Spark/Hadoop)", "importance": "Low"}
            ],
            "researcher": [
                {"skill": "Machine Learning Basics", "importance": "High"},
                {"skill": "Grant Writing", "importance": "Medium"},
                {"skill": "Python Data Science Stack", "importance": "Medium"},
                {"skill": "Big Data Analytics", "importance": "Low"}
            ],
            "marketing manager": [
                {"skill": "SQL for Analytics", "importance": "Medium"},
                {"skill": "Python (Marketing Automation)", "importance": "Low"},
                {"skill": "Conversion Rate Optimization (CRO)", "importance": "High"},
                {"skill": "A/B Testing", "importance": "High"}
            ],
            "hr specialist": [
                {"skill": "People Analytics", "importance": "High"},
                {"skill": "HR Data Visualization (Tableau)", "importance": "Medium"},
                {"skill": "Strategic Workforce Planning", "importance": "High"},
                {"skill": "Compensation Benchmarking", "importance": "Medium"}
            ]
        }

        # Select suitable list
        requirements = []
        for key, reqs in role_requirements.items():
            if key in role_lower or role_lower in key:
                requirements = reqs
                break

        if not requirements:
            # General generic list
            requirements = [
                {"skill": "Cloud Infrastructure (AWS/GCP)", "importance": "High"},
                {"skill": "Agile Methodologies (Scrum)", "importance": "Medium"},
                {"skill": "System Architecture", "importance": "High"},
                {"skill": "CI/CD & DevOps Basics", "importance": "Medium"}
            ]

        # Identify missing skills
        gaps = []
        for req in requirements:
            req_skill = req["skill"]
            if not any(req_skill.lower() in cs for cs in current_skills):
                gaps.append(req)

        return gaps
