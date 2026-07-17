import json
import logging
from django.db import transaction
from .models import ProfessionProfile

logger = logging.getLogger(__name__)

DEFAULT_PROFILES = {
    "Software Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications", "Languages"],
        "required_skills": ["Python", "Java", "SQL", "Git", "REST API"],
        "recommended_skills": ["Docker", "Redis", "AWS", "CI/CD", "Kubernetes"],
        "soft_skills": ["Communication", "Problem Solving", "Teamwork"],
        "preferred_certifications": ["AWS Certified Solutions Architect", "Certified ScrumMaster"],
        "expected_projects": ["Web Application", "REST API Development", "Database Schema Design"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [
            {"name": "No GitHub link", "deduction": 5, "condition": "not bool(profile.github)"}
        ],
        "bonuses": [
            {"name": "Has personal portfolio website", "bonus": 5, "condition": "bool(profile.portfolio_url)"}
        ],
        "benchmark_group": "Technology"
    },
    "Backend Developer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Node.js", "Python", "Go", "SQL", "Git"],
        "recommended_skills": ["Redis", "Docker", "FastAPI", "PostgreSQL", "AWS"],
        "soft_skills": ["API Design", "Security Practices", "Collaboration"],
        "preferred_certifications": ["AWS Certified Developer"],
        "expected_projects": ["Microservices Engine", "Database Optimisation"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Frontend Developer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Portfolio"],
        "required_skills": ["JavaScript", "HTML", "CSS", "React", "Git"],
        "recommended_skills": ["TypeScript", "Vue.js", "Tailwind CSS", "Redux", "Vite"],
        "soft_skills": ["UX awareness", "Design systems", "Communication"],
        "preferred_certifications": [],
        "expected_projects": ["Interactive Dashboard", "Web UI Refactoring"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 5,
            "portfolio": 10,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Full Stack Developer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["React", "Node.js", "SQL", "Git", "JavaScript"],
        "recommended_skills": ["Docker", "TypeScript", "FastAPI", "MongoDB", "AWS"],
        "soft_skills": ["End-to-End systems logic", "Agile leadership"],
        "preferred_certifications": [],
        "expected_projects": ["Full-Stack SaaS Platform", "E-Commerce App"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Mobile App Developer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Swift", "Kotlin", "React Native", "Flutter", "Git"],
        "recommended_skills": ["Objective-C", "Android SDK", "CoreData", "Firebase"],
        "soft_skills": ["App performance optimization", "UI styling intuition"],
        "preferred_certifications": [],
        "expected_projects": ["Published Mobile App", "Real-Time Chat App"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "AI Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Python", "TensorFlow", "PyTorch", "NLP", "Scikit-Learn"],
        "recommended_skills": ["Docker", "SQL", "Pandas", "NumPy", "HuggingFace"],
        "soft_skills": ["Analytical thinking", "Research-oriented development"],
        "preferred_certifications": ["Google Cloud Professional Machine Learning Engineer"],
        "expected_projects": ["LLM Fine-tuning", "Computer Vision Pipeline"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Machine Learning Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Python", "PyTorch", "Scikit-Learn", "Git", "Algorithms"],
        "recommended_skills": ["TensorFlow", "Kubeflow", "MLflow", "SQL", "FastAPI"],
        "soft_skills": ["Mathematical rigor", "Hypothesis testing"],
        "preferred_certifications": [],
        "expected_projects": ["Recommendation System", "Anomaly Detector Engine"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 10,
            "github": 10,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Data Scientist": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Publications"],
        "required_skills": ["Python", "R", "SQL", "Statistics", "Machine Learning"],
        "recommended_skills": ["Pandas", "NumPy", "Jupyter", "Tableau", "Spark"],
        "soft_skills": ["Data storytelling", "Business acumen"],
        "preferred_certifications": [],
        "expected_projects": ["Predictive Customer Churn Analysis", "Data Mining Study"],
        "weights": {
            "skills": 30,
            "projects": 20,
            "experience": 20,
            "education": 15,
            "github": 5,
            "portfolio": 5,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Data Analyst": {
        "industry": "Business Intelligence",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["SQL", "Excel", "Power BI", "Statistics"],
        "recommended_skills": ["Python", "Tableau", "Pandas", "NumPy", "Machine Learning"],
        "soft_skills": ["Data cleansing", "Report design", "Detail validation"],
        "preferred_certifications": ["Microsoft Certified: Power BI Data Analyst Associate"],
        "expected_projects": ["Revenue dashboard creation", "Customer segmentation study"],
        "weights": {
            "skills": 70,  # Combined sum of (SQL 20, Python 15, Power BI 20, Excel 15, Statistics 10) = 80 - mapped to skills & experience
            "projects": 15,
            "education": 5,
            "experience": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Business"
    },
    "DevOps Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["CI/CD", "Docker", "Kubernetes", "AWS", "Terraform"],
        "recommended_skills": ["Linux", "Python", "Bash", "Ansible", "Jenkins"],
        "soft_skills": ["Site stability focus", "Automation mind-state"],
        "preferred_certifications": ["Certified Kubernetes Administrator (CKA)"],
        "expected_projects": ["Infrastructure as Code Setup", "Automated deployment pipeline"],
        "weights": {
            "skills": 35,
            "projects": 15,
            "experience": 25,
            "education": 10,
            "github": 5,
            "portfolio": 0,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Cloud Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Certifications", "Projects"],
        "required_skills": ["AWS", "Azure", "Linux", "Terraform", "CloudFormation"],
        "recommended_skills": ["Python", "Docker", "Kubernetes", "IAM Policy Management", "GCP"],
        "soft_skills": ["Cost Optimization", "High Availability architecture"],
        "preferred_certifications": ["AWS Certified Solutions Architect - Professional"],
        "expected_projects": ["Multi-Region Migration", "Serverless Architecture setup"],
        "weights": {
            "skills": 30,
            "experience": 25,
            "education": 10,
            "certifications": 15,
            "projects": 15,
            "github": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "Cybersecurity Engineer": {
        "industry": "Technology",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Firewalls", "Penetration Testing", "Vulnerability Assessment", "SIEM", "Cryptography"],
        "recommended_skills": ["Linux", "Python", "Wireshark", "Metasploit", "Network Security Protocols"],
        "soft_skills": ["Risk mitigation logic", "Ethics & compliance", "Crisis analysis"],
        "preferred_certifications": ["CompTIA Security+", "CISSP", "CEH"],
        "expected_projects": ["Network Intrusion Audit", "Secure Architecture deployment"],
        "weights": {
            "skills": 30,
            "experience": 25,
            "certifications": 20,
            "projects": 15,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Technology"
    },
    "UI Designer": {
        "industry": "Design",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Projects", "Education"],
        "required_skills": ["Figma", "Wireframing", "Prototyping", "User Research"],
        "recommended_skills": ["Illustrator", "Photoshop", "Framer", "HTML", "CSS"],
        "soft_skills": ["Visual hierarchy", "Typography", "Communication"],
        "preferred_certifications": [],
        "expected_projects": ["Website design overhaul", "Design system construction"],
        "weights": {
            "portfolio": 35,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 10
        },
        "penalties": [
            {"name": "No portfolio URL provided", "deduction": 15, "condition": "not bool(profile.portfolio_url)"}
        ],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "UX Designer": {
        "industry": "Design",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Projects", "Education"],
        "required_skills": ["Figma", "Wireframing", "Prototyping", "User Research"],
        "recommended_skills": ["Illustrator", "Photoshop", "Framer", "HTML", "CSS"],
        "soft_skills": ["Empathy mapping", "Information architecture", "Usability testing"],
        "preferred_certifications": [],
        "expected_projects": ["UX Case Study", "User Persona Research"],
        "weights": {
            "portfolio": 35,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Graphic Designer": {
        "industry": "Design",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Photoshop", "Illustrator", "InDesign", "Typography"],
        "recommended_skills": ["Figma", "After Effects", "Branding", "Vector Drawing"],
        "soft_skills": ["Creative thinking", "Client collaboration"],
        "preferred_certifications": [],
        "expected_projects": ["Brand Identity Package", "Print Campaign Design"],
        "weights": {
            "portfolio": 40,
            "projects": 20,
            "skills": 20,
            "experience": 10,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Mechanical Engineer": {
        "industry": "Engineering",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["SolidWorks", "CAD", "AutoCAD", "Thermodynamics", "Materials Science"],
        "recommended_skills": ["MATLAB", "Finite Element Analysis (FEA)", "CNC Programming", "Ansys"],
        "soft_skills": ["Problem solving", "Spatial visualization"],
        "preferred_certifications": ["PE License (Professional Engineer)"],
        "expected_projects": ["Machine component design", "Structural stress analysis study"],
        "weights": {
            "skills": 25,
            "experience": 30,
            "education": 20,
            "projects": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Engineering"
    },
    "Civil Engineer": {
        "industry": "Engineering",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["AutoCAD", "Civil 3D", "Structural Analysis", "Project Estimation"],
        "recommended_skills": ["Revit", "MS Project", "Geotechnical Engineering", "GIS"],
        "soft_skills": ["Site supervision", "Resource allocation"],
        "preferred_certifications": ["EIT Certificate", "PE License"],
        "expected_projects": ["Structural foundation design", "Roadway alignment proposal"],
        "weights": {
            "skills": 25,
            "experience": 30,
            "education": 20,
            "projects": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Engineering"
    },
    "Electrical Engineer": {
        "industry": "Engineering",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["MATLAB", "Circuit Design", "PCB Design", "AutoCAD Electrical"],
        "recommended_skills": ["PLC Programming", "PSpice", "Embedded Systems", "Power Systems"],
        "soft_skills": ["Technical debugging", "Risk safety evaluation"],
        "preferred_certifications": [],
        "expected_projects": ["Power distribution grid audit", "Microcontroller control system"],
        "weights": {
            "skills": 25,
            "experience": 30,
            "education": 20,
            "projects": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Engineering"
    },
    "Chemical Engineer": {
        "industry": "Engineering",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Process Simulation", "Thermodynamics", "Aspen Plus", "MATLAB"],
        "recommended_skills": ["Chemical Safety", "Heat Transfer", "Fluid Dynamics", "Process Controls"],
        "soft_skills": ["Laboratory safety compliance", "Data precision orientation"],
        "preferred_certifications": [],
        "expected_projects": ["Distillation column simulation", "Reactor scale-up configuration study"],
        "weights": {
            "skills": 25,
            "experience": 30,
            "education": 20,
            "projects": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Engineering"
    },
    "Doctor": {
        "industry": "Healthcare",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications", "Publications"],
        "required_skills": ["Clinical Diagnosis", "Patient Care", "Treatment Planning"],
        "recommended_skills": ["Electronic Health Records (EHR)", "Internal Medicine", "Surgery Assistant"],
        "soft_skills": ["Patient empathy", "Stress endurance", "Crisis communications"],
        "preferred_certifications": ["Medical Registration / License to Practice", "ACLS", "BLS"],
        "expected_projects": ["Clinical trials report", "Medical publications"],
        "weights": {
            "experience": 40,
            "education": 25,
            "certifications": 15,
            "projects": 10,
            "achievements": 10
        },
        "penalties": [
            {"name": "No certifications listed (license required)", "deduction": 15, "condition": "certifications_count == 0"}
        ],
        "bonuses": [],
        "benchmark_group": "Healthcare"
    },
    "Nurse": {
        "industry": "Healthcare",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Patient Monitoring", "Medication Administration", "Wound Care", "Vitals Measurement"],
        "recommended_skills": ["EHR Systems", "ICU Support", "First Aid", "Triage"],
        "soft_skills": ["Patient advocacy", "Team shift sync"],
        "preferred_certifications": ["Registered Nurse (RN) License", "BLS", "CPR Certified"],
        "expected_projects": [],
        "weights": {
            "experience": 40,
            "education": 25,
            "certifications": 20,
            "skills": 15
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Healthcare"
    },
    "Pharmacist": {
        "industry": "Healthcare",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Dispensing Medication", "Drug Interactions Analysis", "Inventory Management"],
        "recommended_skills": ["Patient Consultation", "Pharmacy Software", "FDA Compliance"],
        "soft_skills": ["Precision measurements", "Active listening"],
        "preferred_certifications": ["Registered Pharmacist License"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "education": 25,
            "certifications": 20,
            "skills": 20
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Healthcare"
    },
    "Teacher": {
        "industry": "Education",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications", "Achievements"],
        "required_skills": ["Lesson Planning", "Classroom Management", "Curriculum Design"],
        "recommended_skills": ["Educational Technology", "Student Assessment", "Special Education needs"],
        "soft_skills": ["Patience", "Parent communication", "Interactive instruction"],
        "preferred_certifications": ["State Teaching Credential", "TEFL / TESOL"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "education": 25,
            "soft_skills": 20,
            "achievements": 10,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Education"
    },
    "Professor": {
        "industry": "Education",
        "required_sections": ["Contact", "Summary", "Experience", "Education", "Publications"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Academic Research", "Curriculum Design", "Lecture Presentation", "Grant Writing"],
        "recommended_skills": ["Mentorship", "Public Speaking", "Academic Publishing"],
        "soft_skills": ["Scientific communication", "Peer review"],
        "preferred_certifications": [],
        "expected_projects": ["Research Study", "Thesis Supervision"],
        "weights": {
            "experience": 30,
            "education": 30,
            "achievements": 20,
            "skills": 15,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Education"
    },
    "Accountant": {
        "industry": "Finance",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Excel", "QuickBooks", "GAAP", "Tax Preparation", "Auditing"],
        "recommended_skills": ["General Ledger", "Financial Statements", "SAP", "Bank Reconciliation"],
        "soft_skills": ["Numerical precision", "Ethical compliance"],
        "preferred_certifications": ["Certified Public Accountant (CPA) candidate"],
        "expected_projects": ["Audit Report Implementation"],
        "weights": {
            "skills": 30,
            "experience": 30,
            "education": 20,
            "certifications": 10,
            "projects": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Finance"
    },
    "Chartered Accountant": {
        "industry": "Finance",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Tax Audits", "Financial Reporting", "IFRS Compliance", "Corporate Finance"],
        "recommended_skills": ["SAP FICO", "Internal Control Systems", "Direct Taxation", "Strategic Planning"],
        "soft_skills": ["Analytical integrity", "Advisory communication"],
        "preferred_certifications": ["CA Certification / Member of ICAI / ACCA"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "education": 25,
            "certifications": 20,
            "skills": 20
        },
        "penalties": [
            {"name": "No professional CA registration listed", "deduction": 15, "condition": "certifications_count == 0"}
        ],
        "bonuses": [],
        "benchmark_group": "Finance"
    },
    "HR Executive": {
        "industry": "Human Resources",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Talent Acquisition", "Employee Onboarding", "Performance Management", "HRIS"],
        "recommended_skills": ["Labor Law compliance", "Employee Relations", "Payroll Setup", "LinkedIn Recruiter"],
        "soft_skills": ["Conflict resolution", "Interviewing skills", "Confidentiality maintenance"],
        "preferred_certifications": ["SHRM-CP", "PHR"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "skills": 25,
            "education": 20,
            "soft_skills": 15,
            "certifications": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Corporate"
    },
    "Marketing Executive": {
        "industry": "Marketing",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["SEO", "Google Analytics", "Content Writing", "Social Media Marketing"],
        "recommended_skills": ["SEM", "HubSpot", "Copywriting", "A/B Testing", "Email Marketing Campaigns"],
        "soft_skills": ["Data presentation", "Consumer behavior analysis"],
        "preferred_certifications": ["Google Analytics Individual Qualification"],
        "expected_projects": ["Ad Campaign Implementation", "SEO Optimization Study"],
        "weights": {
            "experience": 30,
            "skills": 25,
            "projects": 20,
            "education": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Corporate"
    },
    "Sales Executive": {
        "industry": "Sales",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Lead Generation", "Client Relationship Management", "Negotiation", "Salesforce CRM"],
        "recommended_skills": ["Cold Calling", "B2B Sales pipeline", "Product Demos", "Closing tactics"],
        "soft_skills": ["Persuasive speech", "High energy levels", "Rejection resilience"],
        "preferred_certifications": [],
        "expected_projects": [],
        "weights": {
            "experience": 40,
            "skills": 25,
            "education": 15,
            "soft_skills": 20
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Corporate"
    },
    "Business Analyst": {
        "industry": "Business Intelligence",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Education"],
        "optional_sections": ["Projects"],
        "required_skills": ["SQL", "Data Modeling", "Requirements Gathering", "UML Diagrams"],
        "recommended_skills": ["Jira", "Tableau", "Excel VLOOKUP/Macros", "Python", "Agile methodologies"],
        "soft_skills": ["Stakeholder alignment", "Business cases formulation"],
        "preferred_certifications": ["CBAP Certified"],
        "expected_projects": ["Process Improvement Initiative", "Business Requirements Document"],
        "weights": {
            "experience": 30,
            "skills": 25,
            "projects": 20,
            "education": 15,
            "certifications": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Business"
    },
    "Project Manager": {
        "industry": "Management",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Project Scheduling", "Risk Management", "Budget Control", "Agile & Scrum"],
        "recommended_skills": ["MS Project", "Jira", "Stakeholder Communication", "Resource Allocation"],
        "soft_skills": ["Team coordination", "Decisiveness", "Conflict settlement"],
        "preferred_certifications": ["PMP Certification", "Scrum Product Owner (CSPO)"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "certifications": 25,
            "soft_skills": 20,
            "education": 10,
            "skills": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Corporate"
    },
    "Lawyer": {
        "industry": "Legal",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Legal Writing", "Contract Negotiation", "Litigation Support", "Case Law Research"],
        "recommended_skills": ["LexisNexis", "Westlaw", "Compliance Auditing", "Client Counseling"],
        "soft_skills": ["Logical arguments construction", "Ethical reasoning", "Debating articulation"],
        "preferred_certifications": ["Bar Council Admission / License to Practice Law"],
        "expected_projects": [],
        "weights": {
            "experience": 35,
            "education": 25,
            "skills": 20,
            "soft_skills": 20
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Legal"
    },
    "Architect": {
        "industry": "Architecture",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["AutoCAD", "Revit", "3D Modeling", "SketchUp", "Building Codes"],
        "recommended_skills": ["Photoshop", "BIM workflow", "Site planning", "Structural constraints awareness"],
        "soft_skills": ["Spatial design thinking", "Contractor sync"],
        "preferred_certifications": ["Registered Architect (AIA or equivalent)"],
        "expected_projects": ["Residential blueprints design", "Commercial structural proposal"],
        "weights": {
            "portfolio": 30,
            "experience": 25,
            "skills": 20,
            "projects": 15,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Interior Designer": {
        "industry": "Design",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["SketchUp", "AutoCAD", "Space Planning", "Material Sourcing", "Color Theory"],
        "recommended_skills": ["3ds Max", "V-Ray", "Lighting Layouts", "Client presentations"],
        "soft_skills": ["Visual mood board creation", "Cost estimates formulation"],
        "preferred_certifications": [],
        "expected_projects": ["Office layout planning case", "Residential styling showcase"],
        "weights": {
            "portfolio": 35,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Hotel Manager": {
        "industry": "Hospitality",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Languages"],
        "required_skills": ["Front Office Management", "Guest Services", "Inventory & Vendor Sync", "Budget Management"],
        "recommended_skills": ["PMS Software", "Staff Shift scheduling", "Event Planning"],
        "soft_skills": ["Crisis composure", "Hospitality orientation", "Interpersonal warmth"],
        "preferred_certifications": [],
        "expected_projects": [],
        "weights": {
            "experience": 40,
            "education": 20,
            "soft_skills": 25,
            "skills": 15
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Corporate"
    },
    "Chef": {
        "industry": "Hospitality",
        "required_sections": ["Contact", "Summary", "Experience"],
        "optional_sections": ["Education", "Certifications"],
        "required_skills": ["Menu Planning", "Food Safety (HACCP)", "Kitchen Team Management", "Portion Cost Control"],
        "recommended_skills": ["Pastry Arts", "Inventory software", "Culinary technique diversity"],
        "soft_skills": ["High-pressure stamina", "Sensory taste evaluation"],
        "preferred_certifications": ["ServSafe Certified Manager"],
        "expected_projects": [],
        "weights": {
            "experience": 45,
            "skills": 25,
            "certifications": 15,
            "education": 15
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Journalist": {
        "industry": "Media",
        "required_sections": ["Contact", "Summary", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["News Writing", "Investigative Journalism", "Copy Editing", "Interviews conduction"],
        "recommended_skills": ["SEO optimized blogging", "Photography", "Video recording"],
        "soft_skills": ["Fact verification discipline", "Inquisitiveness", "Networking"],
        "preferred_certifications": [],
        "expected_projects": ["Published Articles portfolio"],
        "weights": {
            "portfolio": 30,
            "experience": 30,
            "skills": 20,
            "education": 10,
            "projects": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Content Writer": {
        "industry": "Media",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Content writing", "SEO principles", "Grammar checker proficiency", "Research skills"],
        "recommended_skills": ["WordPress", "HubSpot", "Social media copy", "Keyword mapping"],
        "soft_skills": ["Varying tone calibration", "Deadline reliability"],
        "preferred_certifications": [],
        "expected_projects": ["Blogging portfolio", "Landing page copy setup"],
        "weights": {
            "portfolio": 30,
            "experience": 25,
            "skills": 25,
            "projects": 10,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Photographer": {
        "industry": "Media",
        "required_sections": ["Contact", "Summary", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Camera Operation", "Adobe Lightroom", "Photoshop", "Lighting configurations"],
        "recommended_skills": ["Studio setup", "Event capturing", "Drone photography"],
        "soft_skills": ["Visual aesthetics orientation", "Client mood direction"],
        "preferred_certifications": [],
        "expected_projects": ["Photo Series Portfolio"],
        "weights": {
            "portfolio": 45,
            "experience": 25,
            "skills": 20,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Video Editor": {
        "industry": "Media",
        "required_sections": ["Contact", "Summary", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Adobe Premiere Pro", "After Effects", "Final Cut Pro", "Color Grading", "Audio Mixing"],
        "recommended_skills": ["DaVinci Resolve", "Subtitling workflow", "Motion Graphics"],
        "soft_skills": ["Timing / pacing intuition", "Narrative continuity matching"],
        "preferred_certifications": [],
        "expected_projects": ["Showreel portfolio", "Promotional ad edits"],
        "weights": {
            "portfolio": 40,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Animator": {
        "industry": "Media",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Maya", "Blender", "Character Animation", "Keyframe timing", "3D Rendering"],
        "recommended_skills": ["After Effects", "Cinema 4D", "Storyboarding", "Texturing"],
        "soft_skills": ["Anatomy motion observation", "Creative collaborative sync"],
        "preferred_certifications": [],
        "expected_projects": ["Animation Demo Reel"],
        "weights": {
            "portfolio": 40,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 5
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Fashion Designer": {
        "industry": "Design",
        "required_sections": ["Contact", "Summary", "Skills", "Experience", "Portfolio"],
        "optional_sections": ["Education"],
        "required_skills": ["Garment sketching", "Pattern making", "Textile sourcing", "Adobe Illustrator"],
        "recommended_skills": ["3D apparel tools", "Sewing techniques", "Trend forecasting"],
        "soft_skills": ["Creative vision", "Color combinations mapping"],
        "preferred_certifications": [],
        "expected_projects": ["Seasonal Collection design Case Study"],
        "weights": {
            "portfolio": 35,
            "projects": 25,
            "skills": 20,
            "experience": 10,
            "education": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "Creative"
    },
    "Police Officer": {
        "industry": "Government",
        "required_sections": ["Contact", "Summary", "Experience", "Education"],
        "optional_sections": ["Certifications"],
        "required_skills": ["Law Enforcement Protocols", "Emergency Response", "Report Writing", "Public Safety"],
        "recommended_skills": ["Physical Training", "First Aid", "Conflict de-escalation", "Evidence Handling"],
        "soft_skills": ["Integrity", "Emotional stability in crisis", "Community relations"],
        "preferred_certifications": ["Police Academy Graduation Certificate"],
        "expected_projects": [],
        "weights": {
            "experience": 50,
            "education": 20,
            "skills": 15,
            "certifications": 15
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "General"
    },
    "Freelancer": {
        "industry": "General Services",
        "required_sections": ["Contact", "Summary", "Portfolio", "Projects"],
        "optional_sections": ["Experience", "Education"],
        "required_skills": ["Client Communication", "Proposal Writing", "Invoicing", "Self-Management"],
        "recommended_skills": ["Time Tracking", "Contract terms outline", "Multi-Project coordination"],
        "soft_skills": ["Proactive outreach", "Negotiation flexibility"],
        "preferred_certifications": [],
        "expected_projects": ["Client case delivery archive"],
        "weights": {
            "portfolio": 30,
            "projects": 25,
            "experience": 20,
            "skills": 15,
            "achievements": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "General"
    },
    "Student": {
        "industry": "Academic",
        "required_sections": ["Contact", "Summary", "Education"],
        "optional_sections": ["Projects", "Skills", "Certifications", "Achievements"],
        "required_skills": ["Academic Research", "Microsoft Office", "Team Collaboration", "Time Management"],
        "recommended_skills": ["Fast learner mindset", "Basic Git usage", "Presentation formulation"],
        "soft_skills": ["Willingness to learn", "Eager adaptability"],
        "preferred_certifications": [],
        "expected_projects": ["Academic Term Paper", "Lab project execution"],
        "weights": {
            "projects": 30,
            "skills": 25,
            "education": 20,
            "certifications": 15,
            "achievements": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "General"
    },
    "Fresher": {
        "industry": "General Services",
        "required_sections": ["Contact", "Summary", "Education", "Skills"],
        "optional_sections": ["Projects", "Certifications"],
        "required_skills": ["Basic Office suite", "Fast learning", "Communication"],
        "recommended_skills": ["Basic technology tools", "Writing accuracy"],
        "soft_skills": ["Enthusiastic support", "Adaptability"],
        "preferred_certifications": [],
        "expected_projects": [],
        "weights": {
            "skills": 30,
            "education": 30,
            "projects": 20,
            "certifications": 10,
            "achievements": 10
        },
        "penalties": [],
        "bonuses": [],
        "benchmark_group": "General"
    }
}

class ProfileLoader:
    """
    Seeds and manages the library of 47 default ProfessionProfiles in the database.
    """

    @staticmethod
    def seed_profiles(overwrite=False) -> int:
        """
        Populates the ProfessionProfile table with the 47 default profiles.
        """
        count = 0
        with transaction.atomic():
            if overwrite:
                logger.info("Overwriting existing profession profiles...")
                ProfessionProfile.objects.all().delete()

            for role_name, data in DEFAULT_PROFILES.items():
                profile, created = ProfessionProfile.objects.get_or_create(
                    role=role_name,
                    defaults={
                        "industry": data["industry"],
                        "required_sections": data.get("required_sections", []),
                        "optional_sections": data.get("optional_sections", []),
                        "required_skills": data.get("required_skills", []),
                        "recommended_skills": data.get("recommended_skills", []),
                        "soft_skills": data.get("soft_skills", []),
                        "preferred_certifications": data.get("preferred_certifications", []),
                        "expected_projects": data.get("expected_projects", []),
                        "weights": data.get("weights", {}),
                        "penalties": data.get("penalties", []),
                        "bonuses": data.get("bonuses", []),
                        "benchmark_group": data.get("benchmark_group", "General"),
                        "enabled": True
                    }
                )
                if created:
                    count += 1
                elif overwrite:
                    # Update fields explicitly if overwrite is requested
                    profile.industry = data["industry"]
                    profile.required_sections = data.get("required_sections", [])
                    profile.optional_sections = data.get("optional_sections", [])
                    profile.required_skills = data.get("required_skills", [])
                    profile.recommended_skills = data.get("recommended_skills", [])
                    profile.soft_skills = data.get("soft_skills", [])
                    profile.preferred_certifications = data.get("preferred_certifications", [])
                    profile.expected_projects = data.get("expected_projects", [])
                    profile.weights = data.get("weights", {})
                    profile.penalties = data.get("penalties", [])
                    profile.bonuses = data.get("bonuses", [])
                    profile.benchmark_group = data.get("benchmark_group", "General")
                    profile.enabled = True
                    profile.save()
                    count += 1

        logger.info(f"Profession profiles seeding completed. Added/Updated {count} profiles.")
        return count
