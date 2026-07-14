import logging

logger = logging.getLogger(__name__)


class MarketEngine:
    """
    Evaluates market demand and identifies emerging trending skills.
    """
    @staticmethod
    def get_market_data(role: str) -> dict:
        role_lower = role.lower()

        # Default fallback trends
        demand = "High"
        trends = ["Agentic AI", "Kubernetes", "Rust", "Vector Databases", "System Architecture"]

        if "ai" in role_lower or "ml" in role_lower:
            demand = "Very High"
            trends = ["Agentic AI", "LangChain", "LlamaIndex", "MCP (Model Context Protocol)", "Vector DBs", "PyTorch", "GPU Acceleration"]
        elif "backend" in role_lower or "software" in role_lower:
            demand = "High"
            trends = ["FastAPI", "Go / Golang", "Docker", "GraphQL", "Redis Caching", "PostgreSQL Optimization", "Microservices"]
        elif "doctor" in role_lower or "clinical" in role_lower:
            demand = "Very High"
            trends = ["Telehealth Platforms", "AI-assisted Diagnostics", "Electronic Health Records (EHR)", "Preventive Care", "Geriatrics"]
        elif "civil" in role_lower or "structural" in role_lower:
            demand = "Medium"
            trends = ["BIM (Building Information Modeling)", "Green Building & LEED", "Sustainable Materials", "Autodesk Civil 3D", "Structural Dynamics"]
        elif "teacher" in role_lower:
            demand = "Medium"
            trends = ["Digital Pedagogy", "LMS (Canvas/Blackboard)", "Hybrid Teaching Methods", "Interactive Courseware", "Social-Emotional Learning"]
        elif "lawyer" in role_lower:
            demand = "High"
            trends = ["Legal AI & Draft Automation", "GDPR & Privacy Compliance", "Intellectual Property in AI", "Smart Contracts & Blockchain"]
        elif "designer" in role_lower or "ui" in role_lower:
            demand = "High"
            trends = ["Figma Dev Mode", "Design System Engineering", "Framer / Webflow", "Interactive Prototyping", "Motion Design"]
        elif "data" in role_lower or "analyst" in role_lower:
            demand = "High"
            trends = ["Advanced SQL", "dbt (data build tool)", "PowerBI Service", "Python (Pandas/Numpy)", "Data Warehousing (Snowflake)"]
        elif "student" in role_lower or "intern" in role_lower:
            demand = "Medium"
            trends = ["Git & Version Control", "Basic Python/JS", "Problem Solving / LeetCode", "Agile / Scrum Basics"]
        elif "hr" in role_lower or "recruiting" in role_lower:
            demand = "Medium"
            trends = ["People Analytics", "Talent Acquisition SaaS", "Remote Workforce Management", "DEI Strategy"]

        # Market score out of 100 based on demand
        demand_scores = {
            "Low": 40,
            "Medium": 65,
            "High": 85,
            "Very High": 98
        }

        return {
            "demand_level": demand,
            "market_score": demand_scores.get(demand, 80),
            "trending_skills": trends
        }
