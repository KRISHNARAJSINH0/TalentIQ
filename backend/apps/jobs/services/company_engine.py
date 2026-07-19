import logging
import re

logger = logging.getLogger(__name__)

# Core expectations mapping per company
COMPANY_EXPECTATIONS = {
    "google": {
        "expectations": ["Algorithms", "System Design", "Leadership"],
        "keywords": ["algorithm", "data structure", "complexity", "system design", "scalability", "lead", "manage", "spearhead"]
    },
    "amazon": {
        "expectations": ["Leadership Principles", "Cloud", "Ownership"],
        "keywords": ["leadership", "cloud", "aws", "ownership", "customer obsession", "deliver results", "bias for action"]
    },
    "netflix": {
        "expectations": ["Distributed Systems", "Microservices", "Freedom and Responsibility"],
        "keywords": ["distributed", "microservices", "concurrency", "resiliency", "autonomy", "scale", "stream"]
    },
    "openai": {
        "expectations": ["Python", "LLMs", "AI", "Research"],
        "keywords": ["python", "llm", "large language model", "ai", "artificial intelligence", "research", "machine learning", "pytorch"]
    },
    "microsoft": {
        "expectations": ["Software Engineering", "Cloud", "Enterprise Systems"],
        "keywords": ["c#", ".net", "azure", "cloud", "enterprise", "windows", "architecture"]
    },
    "meta": {
        "expectations": ["Product Engineering", "React", "Scale"],
        "keywords": ["react", "frontend", "scale", "product", "mobile", "hack", "fast"]
    }
}

class CompanyEngine:
    """
    Coordinates target company prediction and evaluates candidate alignment with company expectations.
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

        return ["Google", "Microsoft", "Amazon", "Deloitte", "Accenture"]

    @staticmethod
    def evaluate_company_fit(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        
        # 1. Identify which company is mentioned in the JD or fallback to predicted match
        target_company = "General"
        recognized_companies = ["google", "microsoft", "amazon", "netflix", "openai", "meta", "adobe", "salesforce", "oracle", "infosys", "tcs", "accenture", "wipro", "ibm", "capgemini"]
        
        for c in recognized_companies:
            if re.search(r'\b' + re.escape(c) + r'\b', jd_lower):
                target_company = c.capitalize()
                break
                
        # If no recognized company detected in JD text, guess based on profile role focus
        if target_company == "General":
            # Check profile designation names or default to "Google" for SWE
            designations = [exp.get("designation", "").lower() for exp in profile_data.get("experiences", [])]
            if any("engineer" in d or "developer" in d for d in designations):
                target_company = "Google" # Default target for developers
            else:
                target_company = "Accenture" # Default target for consulting
                
        # 2. Check expectations alignment
        co_key = target_company.lower()
        expectations_list = []
        fit_score = 75 # default baseline
        matched_indicators = []
        missing_indicators = []
        
        # Pull text from profile summary, skills, projects, and experiences
        candidate_text = (profile_data.get("summary") or "").lower()
        candidate_text += " " + " ".join([s.get("skill_name", "").lower() for s in profile_data.get("skills", [])])
        candidate_text += " " + " ".join([(exp.get("description") or "").lower() for exp in profile_data.get("experiences", [])])
        candidate_text += " " + " ".join([(p.get("description") or "").lower() for p in profile_data.get("projects", [])])
        
        if co_key in COMPANY_EXPECTATIONS:
            meta = COMPANY_EXPECTATIONS[co_key]
            expectations_list = meta["expectations"]
            keywords = meta["keywords"]
            
            # Check how many indicators are found in candidate profile text
            matches = 0
            for kw in keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', candidate_text):
                    matches += 1
                    matched_indicators.append(kw.capitalize())
                else:
                    missing_indicators.append(kw.capitalize())
                    
            # Compute fit score
            pct = int((matches / max(1, len(keywords))) * 100)
            fit_score = min(100, max(45, pct))
        else:
            # Generic company expectations
            expectations_list = ["Professional Experience", "Collaboration", "Communication"]
            matched_indicators = ["Collaboration", "Professionalism"]
            missing_indicators = []
            
        return {
            "target_company": target_company,
            "expectations": expectations_list,
            "fit_score": fit_score,
            "matched_indicators": matched_indicators[:4],
            "missing_indicators": missing_indicators[:4]
        }
