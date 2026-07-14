import re
from datetime import datetime
from django.utils import timezone
from apps.profiles.models import Profile, Skill, Project, Experience, Certification
from apps.portfolio.models import Portfolio
from apps.resumes.models import ConsistencyReport
from apps.career.models import LearningProgressLog
from apps.ats.services import INDUSTRY_DICTS


class ScoreEngine:
    """
    Sub-system scoring service for Resume Reputation:
    Calculates Skill, Project, Portfolio, Experience, Consistency, and Learning Scores.
    """

    @staticmethod
    def calculate_skills_score(profile: Profile) -> float:
        """
        Calculates a Skills Score (0-100) based on:
        - Quantity (30%)
        - Diversity (20%)
        - Relevance (20%)
        - Demand (10%)
        - Freshness (10%)
        - Depth (10%)
        """
        skills = list(profile.skills.all())
        if not skills:
            return 0.0

        # 1. Quantity
        qty_points = min(30.0, len(skills) * 2.5)

        # 2. Diversity
        skill_types = {s.skill_type for s in skills}
        div_points = min(20.0, len(skill_types) * 10.0)

        # 3. Relevance
        # Check if skills match the target industry keyword pool
        rel_points = 0.0
        headline = (profile.headline or "").lower()
        matched_industry = "Software Engineering"
        for ind, dicts in INDUSTRY_DICTS.items():
            if ind.lower() in headline:
                matched_industry = ind
                break
        
        target_dict_skills = [s.lower() for s in INDUSTRY_DICTS.get(matched_industry, {}).get("skills", [])]
        matched_count = sum(1 for s in skills if s.skill_name.lower() in target_dict_skills)
        if target_dict_skills:
            rel_points = min(20.0, (matched_count / len(target_dict_skills)) * 20.0)
        else:
            rel_points = 15.0

        # 4. Demand
        demand_keywords = ["ai", "machine learning", "deep learning", "nlp", "cloud", "aws", "azure", "gcp", "security", "cyber", "data", "analytics"]
        demand_count = sum(1 for s in skills if any(dk in s.skill_name.lower() for dk in demand_keywords))
        demand_points = min(10.0, demand_count * 2.0)

        # 5. Freshness
        # Default fresh unless no updates, here we assume it's fresh if they are adding skills
        fresh_points = 10.0

        # 6. Depth
        # Count of expert or advanced levels
        depth_count = sum(1 for s in skills if getattr(s, "skill_level", "").lower() in ["expert", "advanced", "senior"])
        depth_points = min(10.0, depth_count * 2.5)

        total_score = qty_points + div_points + rel_points + demand_points + fresh_points + depth_points
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def calculate_projects_score(profile: Profile) -> float:
        """
        Calculates Projects Score (0-100) based on:
        - Project Count (30%)
        - Stack Diversity & Tech (20%)
        - Complexity (15%)
        - Detail/Descriptions (10%)
        - Quantitative Metrics (10%)
        - GitHub Presence (10%)
        - Live Demo (5%)
        """
        projects = list(profile.projects.all())
        if not projects:
            return 0.0

        # 1. Count
        qty_points = min(30.0, len(projects) * 10.0)

        # 2. Stack diversity / tech
        all_techs = set()
        for p in projects:
            if p.technologies:
                techs = [t.strip().lower() for t in p.technologies.split(",") if t.strip()]
                all_techs.update(techs)
        tech_points = min(20.0, len(all_techs) * 2.5)

        # 3. Complexity (proxy by description size and word length)
        total_desc_len = sum(len(p.description or "") for p in projects)
        complexity_points = min(15.0, (total_desc_len / 400.0) * 15.0)

        # 4. Detail / Description Length
        desc_points = min(10.0, (total_desc_len / 200.0) * 10.0)

        # 5. Quantitative Metrics
        # Search for metrics like "30% increase", "served 10k users", "reduced latency by 50ms"
        metric_pattern = re.compile(r"\b\d+%\b|\b\d+\s*(?:users|percent|seconds|ms|hours|dollars|usd|clients|pages)\b")
        metric_matches = 0
        for p in projects:
            if p.description and metric_pattern.search(p.description.lower()):
                metric_matches += 1
        metric_points = min(10.0, metric_matches * 5.0)

        # 6. GitHub Presence
        has_git = any(bool(p.github_url) for p in projects)
        git_points = 10.0 if has_git else 0.0

        # 7. Live Demo
        has_live = any(bool(p.live_url) for p in projects)
        live_points = 5.0 if has_live else 0.0

        total_score = qty_points + tech_points + complexity_points + desc_points + metric_points + git_points + live_points
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def calculate_portfolio_score(profile: Profile) -> float:
        """
        Calculates Portfolio Score (0-100) based on:
        - Presence & Public SEO status (30%)
        - Theme Completeness (25%)
        - Content density (25%)
        - Activity & Traffic metrics (20%)
        """
        portfolio = Portfolio.objects.filter(profile=profile).first()
        if not portfolio:
            # Check if user has added a custom website URL as a backup
            if profile.portfolio_url or profile.website:
                return 40.0
            return 0.0

        # 1. Presence & Public status
        pub_points = 30.0 if (portfolio.is_public and portfolio.slug) else 15.0

        # 2. Theme & Customization Completeness
        theme_points = 25.0
        if portfolio.theme == "glassmorphism":
            theme_points += 5.0
        theme_points = min(25.0, theme_points)

        # 3. Content Density (Portfolio JSON check)
        content_points = 0.0
        p_json = portfolio.portfolio_json
        if p_json and isinstance(p_json, dict):
            sections_count = sum(1 for k, v in p_json.items() if v)
            content_points = min(25.0, sections_count * 4.0)

        # 4. Activity & Analytics Traffic
        views = portfolio.views
        likes = portfolio.likes
        shares = portfolio.shares
        traffic_weight = views + (likes * 3) + (shares * 5)
        analytics_points = min(20.0, (traffic_weight / 10.0) * 20.0)

        total_score = pub_points + theme_points + content_points + analytics_points
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def calculate_experience_score(profile: Profile) -> float:
        """
        Calculates Experience Score (0-100) based on:
        - Duration/Longevity (50%)
        - Leadership indicators (20%)
        - Promotions/Career growth (15%)
        - Key Achievements (15%)
        """
        experiences = list(profile.experiences.all())
        if not experiences:
            # Student check
            projects_count = profile.projects.count()
            if projects_count > 0:
                return round(min(90.0, 45.0 + (projects_count * 10.0)), 2)
            return 0.0

        # 1. Duration / Longevity
        total_days = 0
        for exp in experiences:
            start = exp.start_date
            end = exp.end_date or datetime.today().date()
            if start:
                total_days += (end - start).days
        years = total_days / 365.25
        duration_points = min(50.0, years * 8.0)

        # 2. Leadership Indicators
        leadership_keywords = ["led", "managed", "spearheaded", "directed", "supervised", "leader", "chief", "manager", "head"]
        leadership_count = 0
        for exp in experiences:
            desc = (exp.description or "").lower()
            designation = (exp.designation or "").lower()
            if any(lk in desc or lk in designation for lk in leadership_keywords):
                leadership_count += 1
        lead_points = min(20.0, leadership_count * 10.0)

        # 3. Promotions / Title progression
        # Simple count of unique roles at similar companies, or title change checks
        companies = [exp.company.strip().lower() for exp in experiences if exp.company]
        promotions_points = 0.0
        if len(companies) > len(set(companies)):
            # Has worked at same company with multiple titles
            promotions_points = 15.0
        else:
            # Check if title has advanced from Junior to Senior
            titles = [exp.designation.lower() for exp in experiences if exp.designation]
            has_junior = any("junior" in t or "jr" in t or "intern" in t for t in titles)
            has_senior = any("senior" in t or "sr" in t or "lead" in t or "manager" in t for t in titles)
            if has_junior and has_senior:
                promotions_points = 15.0
            elif len(experiences) >= 2:
                promotions_points = 10.0

        # 4. Key Achievements
        achievement_keywords = ["achieved", "accomplished", "awarded", "delivered", "optimized", "reduced", "increased", "saved", "won"]
        achievement_count = 0
        for exp in experiences:
            desc = (exp.description or "").lower()
            if any(ak in desc for ak in achievement_keywords):
                achievement_count += 1
        achievement_points = min(15.0, achievement_count * 5.0)

        total_score = duration_points + lead_points + promotions_points + achievement_points
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def calculate_consistency_score(profile: Profile, resume) -> float:
        """
        Calculates Consistency Score (0-100) by querying consistency checker reports.
        """
        report = ConsistencyReport.objects.filter(resume=resume).first()
        if report:
            return float(report.score)
        return 75.0  # Baseline default if no report found

    @staticmethod
    def calculate_learning_score(profile: Profile) -> float:
        """
        Calculates Learning Score (0-100) based on:
        - Certifications count (35%)
        - Course milestones completed (30%)
        - Roadmap Learning activity (20%)
        - Career profile additions (15%)
        """
        certs = list(profile.certifications.all())
        user = profile.user

        # 1. Certifications
        cert_points = min(35.0, len(certs) * 12.0)

        # 2. Completed Milestones
        completed_milestones = LearningProgressLog.objects.filter(user=user, is_completed=True).count()
        milestone_points = min(30.0, completed_milestones * 10.0)

        # 3. Learning Activity
        total_milestones = LearningProgressLog.objects.filter(user=user).count()
        activity_points = 0.0
        if total_milestones > 0:
            activity_points = min(20.0, (completed_milestones / total_milestones) * 20.0)
        elif completed_milestones > 0:
            activity_points = 15.0

        # 4. Career updates freshness
        additions_points = 15.0

        total_score = cert_points + milestone_points + activity_points + additions_points
        return round(min(100.0, max(0.0, total_score)), 2)
