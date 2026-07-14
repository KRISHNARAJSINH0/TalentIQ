import logging

logger = logging.getLogger(__name__)


class IndustryEngine:
    """
    Identifies candidate target industries based on predicted roles.
    """
    @staticmethod
    def get_industries(predicted_role: str) -> list:
        role_lower = predicted_role.lower()

        # Dynamic mapping mapping predicted role to growth industries
        role_industry_map = {
            "backend engineer": ["FinTech", "Cloud Infrastructure", "SaaS", "Artificial Intelligence"],
            "software engineer": ["Technology", "SaaS", "E-commerce", "Internet Services"],
            "ml engineer": ["Artificial Intelligence", "Deep Tech", "Scientific Research", "Robotics"],
            "ai engineer": ["Generative AI", "AI Agents", "Deep Learning", "SaaS Automation"],
            "civil engineer": ["Construction", "Real Estate Development", "Infrastructure Planning", "Civil Engineering"],
            "doctor": ["Healthcare Services", "Clinical Research", "Telehealth & Digital Health", "Biotechnology"],
            "teacher": ["K-12 Education", "EdTech & E-Learning", "Higher Education", "Educational Publishing"],
            "lawyer": ["Legal Services", "Corporate Compliance", "IP & Patents", "LegalTech Solutions"],
            "ui ux designer": ["Product Design", "Creative Agency", "Tech Products", "E-commerce & Retail"],
            "designer": ["Design Studio", "Creative Strategy", "Branding & Media", "Advertising"],
            "data analyst": ["Business Intelligence", "Market Analytics", "Banking & Finance", "Healthcare Analytics"],
            "researcher": ["R&D Labs", "Academia", "Policy Think Tanks", "Scientific Consulting"],
            "marketing manager": ["AdTech", "SaaS Marketing", "E-commerce Growth", "Digital Media Agency"],
            "hr specialist": ["Enterprise Software", "Recruitment Platforms", "Professional Services", "HR Consulting"],
            "student": ["Academic Institutions", "Tech Internships", "E-Learning Platforms"],
            "freelancer": ["Gig Economy", "Professional Consulting", "Creative Contracting"]
        }

        # Find best match
        for key, industries in role_industry_map.items():
            if key in role_lower or role_lower in key:
                return industries

        # General default
        return ["Technology", "SaaS", "Consulting", "Information Services"]
