import logging

logger = logging.getLogger(__name__)


class CompanyEngine:
    """
    Suggests suitable target companies matching predicted roles.
    """
    @staticmethod
    def get_companies(role: str) -> list:
        role_lower = role.lower()

        # Modern tech keyword matching first
        if "frontend" in role_lower or "react" in role_lower or "web" in role_lower or "javascript" in role_lower:
            return ["Vercel", "Netlify", "Meta", "Airbnb", "Spotify", "Canva", "Figma"]
        elif "ml" in role_lower or "ai" in role_lower or "deep learning" in role_lower or "nlp" in role_lower:
            return ["OpenAI", "Anthropic", "NVIDIA", "Meta AI", "Google DeepMind", "Hugging Face"]
        elif "devops" in role_lower or "cloud" in role_lower or "infrastructure" in role_lower or "sre" in role_lower:
            return ["AWS", "HashiCorp", "Cloudflare", "Microsoft", "Datadog", "Google Cloud"]
        elif "full stack" in role_lower or "fullstack" in role_lower:
            return ["Stripe", "Shopify", "GitHub", "Vercel", "Uber", "Netflix", "Atlassian"]
        elif "backend" in role_lower:
            return ["Google", "Stripe", "Uber", "Netflix", "Atlassian", "OpenAI", "Amazon"]
        elif "data" in role_lower or "analyst" in role_lower or "analytics" in role_lower:
            return ["Snowflake", "Databricks", "Palantir", "Deloitte", "Capital One", "PwC"]
        elif "designer" in role_lower or "ui" in role_lower or "ux" in role_lower:
            return ["Figma", "Adobe", "Canva", "Airbnb", "Spotify", "Apple", "Pentagram"]

        # Dynamic company mapping fallback catalog
        role_company_map = {
            "software engineer": ["Microsoft", "Amazon", "Meta", "Apple", "Salesforce", "GitHub"],
            "civil engineer": ["Bechtel", "AECOM", "Turner Construction", "Jacobs Engineering", "Skanska", "WSP"],
            "doctor": ["Mayo Clinic", "Cleveland Clinic", "HCA Healthcare", "Pfizer", "Novartis", "Teladoc Health"],
            "teacher": ["Coursera", "Pearson Education", "Khan Academy", "Duolingo", "Public School Districts"],
            "lawyer": ["Kirkland & Ellis", "Latham & Watkins", "Baker McKenzie", "Deloitte Legal", "LexisNexis"],
            "researcher": ["Microsoft Research", "MIT Media Lab", "RAND Corporation", "Max Planck Society", "IBM Research"],
            "marketing manager": ["HubSpot", "Salesforce", "Shopify", "VaynerMedia", "TikTok", "Google Ads"],
            "hr specialist": ["Workday", "ADP", "LinkedIn", "Deloitte People Ops", "Accenture HR"],
            "student": ["Google Internship Program", "Microsoft Internships", "Local Seed Startups", "Academic labs"],
            "freelancer": ["Upwork", "Toptal", "Fiverr Pro", "Independent Client Base"]
        }

        # Find best match in mapped roles
        for key, companies in role_company_map.items():
            if key in role_lower or role_lower in key:
                return companies

        # General default
        return ["Google", "Microsoft", "Amazon", "Deloitte", "Accenture"]
