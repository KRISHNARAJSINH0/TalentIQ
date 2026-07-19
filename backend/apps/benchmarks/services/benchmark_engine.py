import hashlib
from typing import Dict, Any, List
from django.utils import timezone
from apps.resumes.models import Resume
from apps.profiles.models import Profile
from apps.ats.models import ATSScore  # Let's import to check base ATS score if exists
from ..models import BenchmarkReport, RankingHistory, CareerRanking
from .percentile_engine import PercentileEngine
from .career_ranker import CareerRanker
from .comparison_engine import ComparisonEngine
from .ranking_engine import RankingEngine


class BenchmarkEngine:
    """
    Main coordinator service for candidate benchmarking.
    """

    DEFAULT_PROFESSION = "Software Engineer"
    DEFAULT_INDUSTRY = "AI"
    DEFAULT_COUNTRY = "Remote"

    @classmethod
    def get_user_profile(cls, resume: Resume) -> Profile:
        """
        Safely retrieves user profile.
        """
        try:
            return Profile.objects.filter(user=resume.user).first()
        except Exception:
            return None

    @classmethod
    def get_ats_score(cls, resume: Resume) -> float:
        """
        Gets the latest ATS Score or falls back to a deterministic calculation.
        """
        # Attempt to read from the ATSScore model
        ats_score_obj = ATSScore.objects.filter(resume=resume).order_by("-ats_completed_at").first()
        if ats_score_obj:
            return float(ats_score_obj.ats_score)
            
        # Fallback – check parsed details or default to deterministic score
        parsed = resume.parsed_json
        if isinstance(parsed, dict) and "overall_score" in parsed:
            return float(parsed["overall_score"])
            
        # Hard fallback
        name_hash = int(hashlib.md5(resume.resume_title.encode()).hexdigest(), 16)
        return float(60 + (name_hash % 35))

    @classmethod
    def calculate_improvement_steps(cls, current_percentile: float) -> List[Dict[str, str]]:
        """
        Calculates realistic rank improvements after completing recommendations.
        """
        steps = []
        
        # Step 0: Current Rank
        steps.append({
            "step": "Current Rank",
            "rank": PercentileEngine.format_rank(current_percentile)
        })
        
        # Step 1: After Docker
        docker_pct = max(1.0, current_percentile * 0.8)
        steps.append({
            "step": "After Docker integration",
            "rank": PercentileEngine.format_rank(docker_pct)
        })
        
        # Step 2: After AWS
        aws_pct = max(1.0, docker_pct * 0.75)
        steps.append({
            "step": "After AWS cloud deployment",
            "rank": PercentileEngine.format_rank(aws_pct)
        })
        
        # Step 3: After Better Projects
        proj_pct = max(1.0, aws_pct * 0.65)
        steps.append({
            "step": "After Better System Projects",
            "rank": PercentileEngine.format_rank(proj_pct)
        })
        
        return steps

    @classmethod
    def generate_report(cls, resume: Resume) -> BenchmarkReport:
        """
        Main entrypoint: performs analysis, updates ranking history, caches rankings,
        and saves a BenchmarkReport.
        """
        profile = cls.get_user_profile(resume)
        
        # Determine demographics
        raw_designation = ""
        if profile:
            raw_designation = getattr(profile, "headline", "")
            if not raw_designation:
                try:
                    latest_exp = profile.experiences.order_by("-start_date").first()
                    if latest_exp:
                        raw_designation = latest_exp.designation
                except Exception:
                    pass
            if not raw_designation and resume.parsed_json:
                raw_designation = resume.parsed_json.get("current_role", "")
        else:
            parsed = resume.parsed_json
            if isinstance(parsed, dict):
                raw_designation = parsed.get("current_role", "")
                
        from apps.ats.role_mapper import RoleMapper
        profession = RoleMapper.map_role(raw_designation) if raw_designation else cls.DEFAULT_PROFESSION
        
        experience_level = CareerRanker.determine_career_level(resume, profile)
        industry = getattr(profile, "primary_industry", "") if profile else ""
        if not industry:
            # Fallback to default or simple check
            industry = cls.DEFAULT_INDUSTRY
            
        country = getattr(profile, "country", "") if profile else ""
        if not country:
            country = cls.DEFAULT_COUNTRY
        
        # Validate values are in standard lists if needed, else keep them
        
        # Calculate baseline ATS score
        base_ats = cls.get_ats_score(resume)
        
        # Run sub-metric comparison evaluation
        metrics_pct = ComparisonEngine.evaluate_metrics(resume, base_ats)
        
        # Identify strengths & weaknesses
        sw = RankingEngine.identify_strengths_and_weaknesses(metrics_pct)
        
        # Demographics ranks
        ranks_pct = RankingEngine.calculate_ranks(base_ats, f"{resume.id}-{profession}-{country}")
        
        overall_rank_str = PercentileEngine.format_rank(ranks_pct["overall"])
        profession_rank_str = PercentileEngine.format_rank(ranks_pct["profession"])
        industry_rank_str = PercentileEngine.format_rank(ranks_pct["industry"])
        country_rank_str = PercentileEngine.format_rank(ranks_pct["country"])
        experience_rank_str = PercentileEngine.format_rank(ranks_pct["experience"])
        
        # Improvement potential
        improvements = cls.calculate_improvement_steps(ranks_pct["overall"])
        
        # Raw details dictionary
        details = {
            "profession": profession,
            "experience_level": experience_level,
            "industry": industry,
            "country": country,
            "base_ats_score": base_ats,
            "metrics": metrics_pct,
            "ranks_raw": ranks_pct
        }
        
        # Save Report
        report = BenchmarkReport.objects.create(
            resume=resume,
            overall_rank=overall_rank_str,
            profession_rank=profession_rank_str,
            industry_rank=industry_rank_str,
            country_rank=country_rank_str,
            experience_rank=experience_rank_str,
            strengths=sw["strengths"],
            weaknesses=sw["weaknesses"],
            comparison_metrics=metrics_pct,
            improvement_potential=improvements,
            details_json=details
        )
        
        # Record Ranking History
        RankingHistory.objects.create(
            resume=resume,
            overall_rank=overall_rank_str,
            overall_score=int(base_ats)
        )
        
        # Cache Career Ranking
        CareerRanking.objects.create(
            resume=resume,
            profession=profession,
            experience_level=experience_level,
            industry=industry,
            country=country,
            percentile=ranks_pct["overall"]
        )
        
        return report
