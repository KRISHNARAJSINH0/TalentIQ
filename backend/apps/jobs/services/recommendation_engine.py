import logging

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Suggests Certifications, Courses, Projects, and Learning Paths based on the candidate's predicted role.
    """
    @staticmethod
    def get_recommendations(role: str) -> dict:
        role_lower = role.lower()

        # Dynamic recommendations catalog
        if "ai" in role_lower or "ml" in role_lower:
            return {
                "certifications": [
                    "AWS Certified Machine Learning – Specialty",
                    "TensorFlow Developer Certificate",
                    "DeepLearning.AI Generative AI Certification"
                ],
                "courses": [
                    "Generative AI with Large Language Models (Coursera)",
                    "Deep Learning Specialization by Andrew Ng",
                    "LangChain & LlamaIndex for AI Assistants"
                ],
                "projects": [
                    "Build a custom RAG chatbot with hybrid search and citation tracking",
                    "Design and implement a multi-agent system using LangGraph or AutoGen"
                ],
                "learning_path": [
                    "1. Master advanced PyTorch and transformer configurations",
                    "2. Dive deep into vector storage, database indexing, and sparse embeddings",
                    "3. Learn model quantization, deployment strategies, and Triton Server"
                ],
                "career_steps": [
                    "Contribute to open-source LLM/agentic tooling (e.g. LangChain, LlamaIndex)",
                    "Present at ML/AI meetups or write tech blogs detailing agent architectures"
                ]
            }
        elif "frontend" in role_lower or "react" in role_lower or "web" in role_lower:
            return {
                "certifications": [
                    "Meta Front-End Developer Professional Certificate",
                    "AWS Certified Developer – Associate",
                    "W3Schools Front-End Web Developer Certification"
                ],
                "courses": [
                    "Advanced React & Next.js: The Complete Guide (Udemy)",
                    "CSS Layout & Design Systems (Frontend Masters)",
                    "TypeScript Masterclass: Next-level Frontend Development"
                ],
                "projects": [
                    "Build a fully responsive micro-frontend dashboard with module federation",
                    "Develop a server-side rendered e-commerce platform with Next.js App Router"
                ],
                "learning_path": [
                    "1. Master ES6+, asynchronous Javascript, and Web Performance optimization",
                    "2. Dive deep into React state management (Zustand/Redux) and React Server Components",
                    "3. Learn modern build tools (Vite, Turbopack) and testing (Jest/Cypress)"
                ],
                "career_steps": [
                    "Contribute to open-source UI libraries or publish reusable React hook packages",
                    "Take ownership of design system token implementations and accessibility (a11y) audits"
                ]
            }
        elif "full stack" in role_lower or "fullstack" in role_lower:
            return {
                "certifications": [
                    "AWS Certified Solutions Architect – Associate",
                    "Full Stack Developer Nanodegree",
                    "MongoDB Certified Developer"
                ],
                "courses": [
                    "Designing Data-Intensive Applications Study Guide",
                    "Node.js, Express, MongoDB & Friends (Udemy)",
                    "Next.js Full Stack Masterclass"
                ],
                "projects": [
                    "Build a real-time collaborative workspace app using WebSockets and Redis",
                    "Implement a secure multi-tenant SaaS dashboard with role-based access control (RBAC)"
                ],
                "learning_path": [
                    "1. Learn database modeling, optimization, and query index optimization",
                    "2. Master client-side and server-side authentication flows (JWT, OAuth2, Sessions)",
                    "3. Implement caching layer with Redis and async background queues with Celery"
                ],
                "career_steps": [
                    "Lead end-to-end features spanning database design to responsive frontend interfaces",
                    "Write comprehensive integration tests covering full application interactions"
                ]
            }
        elif "devops" in role_lower or "sre" in role_lower or "cloud" in role_lower:
            return {
                "certifications": [
                    "AWS Certified Solutions Architect – Professional",
                    "CKA (Certified Kubernetes Administrator)",
                    "HashiCorp Certified: Terraform Associate"
                ],
                "courses": [
                    "Kubernetes Mastery by Mumshad Mannambeth",
                    "Terraform: From Zero to Certified Associate",
                    "DevOps Bootcamp: CI/CD Pipelines with GitHub Actions"
                ],
                "projects": [
                    "Design and launch a highly-available Kubernetes cluster on AWS using IaC",
                    "Build an automated gitops deployment pipeline using ArgoCD and Helm"
                ],
                "learning_path": [
                    "1. Master Infrastructure-as-Code (Terraform) and configuration management (Ansible)",
                    "2. Deepen container orchestration skills (Kubernetes) and networking details",
                    "3. Set up observability stacks with Prometheus, Grafana, and OpenTelemetry"
                ],
                "career_steps": [
                    "Establish centralized log collection and system alert dashboards for production",
                    "Implement auto-scaling rules and disaster recovery failover processes"
                ]
            }
        elif "data" in role_lower or "analyst" in role_lower or "analytics" in role_lower:
            return {
                "certifications": [
                    "Microsoft Certified: Power BI Data Analyst Associate",
                    "Google Advanced Data Analytics Professional Certificate",
                    "dbt Analytics Engineering Certification"
                ],
                "courses": [
                    "Advanced SQL for Analytics and Data Warehousing (Coursera)",
                    "Data Modeling & dbt (Data Build Tool) Bootcamp",
                    "Python for Data Science (Pandas, NumPy, Matplotlib)"
                ],
                "projects": [
                    "Build a real-time sales performance dashboard with dbt pipelines and Power BI",
                    "Create an automated data aggregation pipeline using python and cron orchestrations"
                ],
                "learning_path": [
                    "1. Master advanced SQL features (window functions, CTEs, indexing, query optimization)",
                    "2. Learn dimensional data modeling principles (Star Schema, Snowflake Schema)",
                    "3. Build ETL pipeline templates using Python and modern data orchestrators"
                ],
                "career_steps": [
                    "Present findings and commercial recommendations directly to cross-functional stakeholders",
                    "Standardize data documentation and build catalog repositories for business analyst teams"
                ]
            }
        elif "backend" in role_lower or "software" in role_lower:
            return {
                "certifications": [
                    "AWS Certified Solutions Architect",
                    "CKAD (Certified Kubernetes Application Developer)",
                    "Confluent Certified Developer for Apache Kafka"
                ],
                "courses": [
                    "Distributed Systems & Microservices by Designing Data-Intensive Applications",
                    "Docker & Kubernetes: The Practical Guide (Udemy)",
                    "Advanced System Design for High Scale Solutions"
                ],
                "projects": [
                    "Develop a rate-limiting API gateway with Redis and token bucket algorithm",
                    "Build a distributed transaction system using saga pattern and message brokers"
                ],
                "learning_path": [
                    "1. Deepen understanding of database indexes, replication, and query execution plans",
                    "2. Build containerized systems and establish automated CI/CD deployment pipelines",
                    "3. Implement caching, CDN, and async worker patterns for traffic spikes"
                ],
                "career_steps": [
                    "Mentor junior developers on coding standards, testing patterns, and Git conventions",
                    "Take ownership of critical service performance optimizations and scale audits"
                ]
            }
        elif "civil" in role_lower or "structural" in role_lower:
            return {
                "certifications": [
                    "PMP (Project Management Professional)",
                    "LEED Green Associate / LEED AP",
                    "Autodesk Certified Professional: AutoCAD / Revit"
                ],
                "courses": [
                    "Building Information Modeling (BIM) Lifecycle Management",
                    "Structural Design & Materials Engineering (Coursera)",
                    "Infrastructure Project Management Principles"
                ],
                "projects": [
                    "Develop a complete BIM 3D model for an eco-friendly commercial complex",
                    "Perform structural stress analyses and seismic evaluations on a bridge prototype"
                ],
                "learning_path": [
                    "1. Gain full efficiency with Autodesk Revit and BIM coordination workflow",
                    "2. Complete green building certification training (LEED AP)",
                    "3. Study local building regulations, codes, and construction site management"
                ],
                "career_steps": [
                    "Join construction site audits to gain firsthand experience in field execution",
                    "Engage with the Institution of Civil Engineers or regional associations"
                ]
            }
        elif "doctor" in role_lower:
            return {
                "certifications": [
                    "Board Certification in Family Medicine / Internal Medicine",
                    "Certificate in Travel Medicine (CTM)",
                    "Advanced Cardiac Life Support (ACLS)"
                ],
                "courses": [
                    "Medical Informatics & Telehealth Best Practices",
                    "Clinical Trials & Epidemiology Research Methods",
                    "Health Systems Leadership & Management"
                ],
                "projects": [
                    "Initiate a local public health advisory program on preventive lifestyle habits",
                    "Develop a workflow template for integrating AI diagnostics in community clinics"
                ],
                "learning_path": [
                    "1. Complete internship residency cycles in multi-specialty clinical centers",
                    "2. Undergo specialized training in remote telemedicine operations",
                    "3. Acquire knowledge in data privacy laws regarding Electronic Health Records (EHR)"
                ],
                "career_steps": [
                    "Participate in national clinical advisory circles or medical forums",
                    "Lead digital transformation initiatives inside current hospital clinics"
                ]
            }
        elif "teacher" in role_lower:
            return {
                "certifications": [
                    "National Board Certification for Professional Teaching Standards",
                    "Google Certified Educator (Level 1 & 2)",
                    "CELTA / TEFL Certification"
                ],
                "courses": [
                    "Digital Pedagogy: Teaching with Technology (Coursera)",
                    "Social-Emotional Learning (SEL) Curriculum Design",
                    "Instructional Design Foundations & Models"
                ],
                "projects": [
                    "Create a hybrid LMS-based interactive learning module for high school science",
                    "Design a student assessment tool utilizing automated feedback mechanisms"
                ],
                "learning_path": [
                    "1. Implement student-centric project workflows using interactive classroom tools",
                    "2. Gain expertise in modern EdTech tools (Kahoot, Nearpod, Quizizz)",
                    "3. Study child psychology, inclusive education methods, and classroom dynamics"
                ],
                "career_steps": [
                    "Lead regional curriculum development workshops or EdTech training sessions",
                    "Conduct peer reviews or publish lesson planning blueprints in educational magazines"
                ]
            }
        elif "lawyer" in role_lower:
            return {
                "certifications": [
                    "CIPP/E (Certified Information Privacy Professional/Europe)",
                    "Certified Compliance & Ethics Professional (CCEP)",
                    "Bar Association License"
                ],
                "courses": [
                    "Privacy Law, GDPR & Global Data Compliance (Coursera)",
                    "Smart Contracts & Legal Tech Foundations",
                    "Corporate Law & Mergers & Acquisitions Intensive"
                ],
                "projects": [
                    "Draft a comprehensive compliance policy template for SaaS startups",
                    "Conduct a legal risk analysis on smart contract execution in financial platforms"
                ],
                "learning_path": [
                    "1. Build practical proficiency in Legal AI research tools (e.g. Westlaw Precision)",
                    "2. Specialized studies in privacy laws, compliance regulations, and commercial disputes",
                    "3. Master legal drafting, structured arguments, and client consultation"
                ],
                "career_steps": [
                    "Publish whitepapers detailing regulatory implications in emerging tech",
                    "Join legal aid clinics or volunteer counsel panels for local community issues"
                ]
            }
        elif "designer" in role_lower or "ui" in role_lower:
            return {
                "certifications": [
                    "Google UX Design Professional Certificate",
                    "NN/g UX Certification",
                    "Interaction Design Foundation (IxDF) Certified Designer"
                ],
                "courses": [
                    "Design System Architecture & Tokens",
                    "User Research Methods & Usability Testing (Coursera)",
                    "Webflow / Framer for Designers"
                ],
                "projects": [
                    "Design a comprehensive multi-platform design system in Figma with auto layout",
                    "Redesign a complex dashboard focusing on information architecture and user flows"
                ],
                "learning_path": [
                    "1. Master interactive prototyping, motion design, and developer handoff in Figma",
                    "2. Conduct remote usability tests and write data-backed UX research studies",
                    "3. Learn Framer/Webflow to build and launch fully functional responsive sites"
                ],
                "career_steps": [
                    "Publish detailed case studies on Behance/Dribbble showing your design process",
                    "Conduct design critiques, mentorship, or lead design systems at your company"
                ]
            }
        elif "data" in role_lower or "analyst" in role_lower:
            return {
                "certifications": [
                    "Microsoft Certified: Power BI Data Analyst Associate",
                    "Google Advanced Data Analytics Professional Certificate",
                    "dbt Analytics Engineering Certification"
                ],
                "courses": [
                    "Data Warehousing & Advanced SQL (Coursera)",
                    "Data Modeling & dbt (Data Build Tool) Bootcamp",
                    "Python for Data Analysis (Pandas & NumPy)"
                ],
                "projects": [
                    "Build a real-time sales performance dashboard with dbt pipelines and Power BI",
                    "Analyze public datasets in Python to find trends and build correlation reports"
                ],
                "learning_path": [
                    "1. Master advanced SQL (window functions, CTEs, indexing, query planning)",
                    "2. Learn data modeling principles (star schema, dimensional modeling)",
                    "3. Build automated ETL pipelines using Python and orchestrators (Prefect/Airflow)"
                ],
                "career_steps": [
                    "Present data insights and optimization opportunities directly to stakeholders",
                    "Drive data-driven culture by teaching basic SQL/BI to marketing and ops teams"
                ]
            }

        # General Default
        return {
            "certifications": [
                "Scrum Alliance Certified ScrumMaster (CSM)",
                "Project Management Professional (PMP)"
            ],
            "courses": [
                "Strategic Leadership & Communication Principles",
                "Agile Project Management Bootcamp"
            ],
            "projects": [
                "Establish a team agile board, sprint schedule, and workflow automation",
                "Write a comprehensive product requirements document (PRD) for a new feature"
            ],
            "learning_path": [
                "1. Master strategic project planning, task prioritization, and roadmapping",
                "2. Develop strong technical communication and stakeholder alignment techniques",
                "3. Master modern productivity tools (Jira, Notion, Slack API)"
            ],
            "career_steps": [
                "Take lead on cross-team projects to demonstrate planning and communication skills",
                "Contribute to internal training workshops and document project blueprints"
            ]
        }
