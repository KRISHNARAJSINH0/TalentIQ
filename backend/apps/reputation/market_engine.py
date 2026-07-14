import re
from datetime import datetime
from apps.profiles.models import Profile, Skill, Experience, Certification


class MarketEngine:
    """
    Sub-system market evaluation service for Resume Reputation:
    Calculates Career, Demand, Growth, and overall Market scores.
    """

    @staticmethod
    def calculate_career_score(profile: Profile) -> float:
        """
        Calculates Career Score (0-100) representing career stature and accomplishments:
        - Experience duration & title senior indicators (50%)
        - Certifications count (25%)
        - Professional awards & achievements (25%)
        """
        certs = profile.certifications.count()
        awards = profile.awards.count()
        experiences = list(profile.experiences.all())

        # 1. Experience Stature
        exp_factor = 50.0
        if not experiences:
            exp_factor = min(40.0, profile.projects.count() * 10.0)
        else:
            total_days = 0
            has_senior_role = False
            for exp in experiences:
                start = exp.start_date
                end = exp.end_date or datetime.today().date() if hasattr(exp, "end_date") else None
                if start and end:
                    total_days += (end - start).days
                
                title = (exp.designation or "").lower()
                if any(x in title for x in ["senior", "lead", "principal", "manager", "head", "director", "chief"]):
                    has_senior_role = True

            years = total_days / 365.25
            exp_factor = min(50.0, 30.0 + (years * 4.0))
            if has_senior_role:
                exp_factor = min(50.0, exp_factor + 10.0)

        # 2. Certifications
        cert_factor = min(25.0, certs * 8.0)

        # 3. Awards
        awards_factor = min(25.0, awards * 12.5)
        if awards_factor == 0.0 and profile.projects.count() >= 2:
            awards_factor = 15.0  # Project bonus fallback

        total_score = exp_factor + cert_factor + awards_factor
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def calculate_demand_score(profile: Profile) -> float:
        """
        Calculates Demand Score (0-100) based on target skills:
        - AI/ML/Deep Learning (Very High: 96-100)
        - Cloud/DevOps (Very High: 92-95)
        - Cyber Security (High: 86-91)
        - Data Analytics & Data Engineering (High: 82-85)
        - Full Stack & Mobile (Medium-High: 78-81)
        - Other sectors (Medium/Standard: 70-77)
        """
        skills = [s.skill_name.lower() for s in profile.skills.all()]
        headline = (profile.headline or "").lower()

        # Check AI demand
        ai_keywords = ["ai", "machine learning", "deep learning", "nlp", "tensorflow", "pytorch", "computer vision", "neural network"]
        if any(ak in headline or any(ak in sk for sk in skills) for ak in ai_keywords):
            return 98.0

        # Check Cloud demand
        cloud_keywords = ["aws", "azure", "gcp", "cloud", "kubernetes", "docker", "devops", "ci/cd"]
        if any(ck in headline or any(ck in sk for sk in skills) for ck in cloud_keywords):
            return 94.0

        # Check Cyber Security demand
        sec_keywords = ["cyber", "security", "pen", "cryptography", "firewall", "information security"]
        if any(sk in headline or any(sk in sk_name for sk_name in skills) for sk in sec_keywords):
            return 90.0

        # Check Data Analytics demand
        data_keywords = ["data science", "data analysis", "tableau", "powerbi", "pandas", "data engineering", "spark", "hadoop"]
        if any(dk in headline or any(dk in sk for sk in skills) for dk in data_keywords):
            return 86.0

        # Check Full Stack / Web Developer demand
        web_keywords = ["full stack", "react", "node", "django", "angular", "vue", "typescript", "flutter", "react native"]
        if any(wk in headline or any(wk in sk for sk in skills) for wk in web_keywords):
            return 82.0

        # Default fallback by headline matches
        if any(ind in headline for ind in ["software", "finance", "engineer", "marketing"]):
            return 78.0
        
        return 72.0

    @staticmethod
    def calculate_growth_score(profile: Profile) -> float:
        """
        Calculates Growth Score (0-100) based on promotions and upward mobility probability.
        """
        experiences = list(profile.experiences.all())
        certs_count = profile.certifications.count()
        
        # Base mobility score
        base_growth = 70.0
        
        # Add points for continuous education / learning milestones
        base_growth += min(15.0, certs_count * 5.0)

        # Experience check
        if len(experiences) >= 2:
            base_growth += 10.0
        elif len(experiences) == 1:
            base_growth += 5.0

        # Check if they have leadership exposure
        leadership_count = 0
        leadership_keywords = ["led", "managed", "spearheaded", "directed"]
        for exp in experiences:
            desc = (exp.description or "").lower()
            if any(lk in desc for lk in leadership_keywords):
                leadership_count += 1
        base_growth += min(10.0, leadership_count * 5.0)

        return round(min(100.0, base_growth), 2)

    @staticmethod
    def calculate_market_score(profile: Profile, demand_score: float, growth_score: float) -> float:
        """
        Aggregates demand, salary potential proxy, remote availability, and growth prospects into a Market Score (0-100).
        """
        # Remote work factor based on headline
        headline = (profile.headline or "").lower()
        remote_factor = 70.0  # baseline
        if any(tech in headline for tech in ["software", "developer", "designer", "writer", "marketing", "data"]):
            remote_factor = 95.0
        elif any(loc in headline for loc in ["engineer", "analyst", "consultant"]):
            remote_factor = 85.0

        # Salary potential proxy based on experience and industry demand
        exp_count = profile.experiences.count()
        salary_factor = min(100.0, 60.0 + (exp_count * 6.0) + (demand_score * 0.2))

        # Final market score aggregation
        market_score = (demand_score * 0.4) + (remote_factor * 0.3) + (salary_factor * 0.3)
        
        # Slight boost if growth potential is high
        if growth_score >= 85:
            market_score = min(100.0, market_score + 3.0)

        return round(market_score, 2)
