import os
import json
import logging
import time
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

# pyrefly: ignore [missing-import]
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from apps.resumes.models import Resume
from ..models import JobRecommendation, SkillGap

from .role_predictor import RolePredictor
from .job_matcher import JobMatcher
from .industry_engine import IndustryEngine
from .salary_engine import SalaryEngine
from .market_engine import MarketEngine
from .company_engine import CompanyEngine
from .country_engine import CountryEngine
from .skill_gap_engine import SkillGapEngine
from .recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


class JobsGeminiService:
    """
    Handles prompt engineering and communication with Gemini for Job Intelligence tasks.
    """
    _initialized = False
    use_mock = False

    @classmethod
    def initialize_client(cls):
        if not cls._initialized:
            api_key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY is not defined. Falling back to local Mock Job Intelligence engines.")
                cls.use_mock = True
            else:
                try:
                    genai.configure(api_key=api_key)
                    cls.use_mock = False
                except Exception as e:
                    logger.warning(f"Failed to configure Gemini client: {e}. Falling back to Mock.")
                    cls.use_mock = True
            cls._initialized = True

    def generate_intelligence(self, profile_data: dict, retry_count: int = 3, backoff_factor: float = 2.0) -> dict:
        self.initialize_client()

        if self.use_mock:
            return self._run_mock_engines(profile_data)

        # Prepare AI prompt
        prompt = self._build_prompt(profile_data)
        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        
        config = GenerationConfig(
            response_mime_type="application/json",
            temperature=0.1
        )

        for attempt in range(retry_count):
            try:
                response = model.generate_content(prompt, generation_config=config)
                if response and response.text:
                    result = json.loads(response.text)
                    # Validate basic keys
                    if "predicted_role" in result and "recommended_jobs" in result:
                        return result
                raise ValueError("Incomplete or malformed JSON returned from Gemini.")
            except Exception as e:
                logger.warning(f"Gemini Job Intelligence request failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt == retry_count - 1:
                    logger.warning("Exhausted Gemini attempts. Falling back to local Mock engines.")
                    return self._run_mock_engines(profile_data)
                time.sleep(backoff_factor ** attempt)
        
        return self._run_mock_engines(profile_data)

    def _build_prompt(self, profile_data: dict) -> str:
        # Standardize serializer content into string representation for LLM input
        serialized_profile = json.dumps(profile_data, cls=DjangoJSONEncoder)
        
        return f"""
You are a Principal Career Advisor AI.
Analyze the candidate's Master Resume profile data provided below:

{serialized_profile}

Generate a comprehensive Job Intelligence analysis. You MUST output your response as a valid JSON object matching the exact schema below:

{{
  "predicted_role": "Predicted main role category (e.g. Backend Engineer, Doctor, Teacher)",
  "recommended_jobs": [
    {{
      "title": "Specific job title recommendation",
      "score": 90, // integer match percentage (0-100)
      "salary": "Salary range (e.g. ₹18.0 - ₹24.0 LPA, $110k-$145k/yr)",
      "industry": "Industry category",
      "country": "Best fit country (e.g. India, USA, Germany)",
      "remote": true, // boolean remote eligibility
      "missing_skills": ["Skill Name 1", "Skill Name 2"]
    }}
  ],
  "skill_gaps": [
    {{
      "skill": "Required skill that the candidate is missing",
      "importance": "High / Medium / Low"
    }}
  ],
  "market_demand": "Very High / High / Medium / Low",
  "market_score": 88, // integer score 0-100
  "trending_skills": ["Emerging Tech Skill 1", "Emerging Tech Skill 2"],
  "salary_forecast": {{
    "current": "Current expected salary range",
    "months_6": "Predicted salary range in 6 months",
    "months_12": "Predicted salary range in 12 months",
    "months_24": "Predicted salary range in 24 months"
  }},
  "companies": ["Target Company 1", "Target Company 2"],
  "countries": ["Suitability Country 1", "Suitability Country 2"],
  "remote_eligibility": {{
    "eligible": true,
    "score": 85, // integer remote eligibility score
    "factors": ["Reason why they are eligible", "Another remote suitability factor"]
  }},
  "recommendations": {{
    "certifications": ["Recommended Certification 1"],
    "courses": ["Recommended Course 1"],
    "projects": ["Proposed portfolio project idea"],
    "learning_path": ["Step 1 description", "Step 2 description"],
    "career_steps": ["Career advice step 1", "Career advice step 2"]
  }}
}}

Ensure all fields are fully populated and realistic based on the candidate's background. Keep all numbers within logical brackets.
"""

    def _run_mock_engines(self, profile_data: dict) -> dict:
        """
        Runs local rule-based engines to construct a high-fidelity output.
        """
        # 1. Predict Role
        role = RolePredictor.predict_role(profile_data)
        
        # 2. Get Countries
        user_country = profile_data.get("country", "")
        countries = CountryEngine.get_countries(role, user_country)
        primary_country = countries[0] if countries else "USA"

        # 3. Forecast Salaries
        years_exp = 3
        # Try finding actual years of experience from experience count
        experiences = profile_data.get("experiences", [])
        if experiences:
            years_exp = len(experiences) * 2
        salary_data = SalaryEngine.forecast_salary(role, primary_country, years_exp)
        
        # 4. Get Recommended Companies & Industries
        companies = CompanyEngine.get_companies(role)
        industries = IndustryEngine.get_industries(role)
        primary_industry = industries[0] if industries else "Technology"

        # 5. Compute Match Scores for Recommended Jobs
        # Generate 3 relevant job titles based on role
        role_lower = role.lower()
        if "frontend" in role_lower or "react" in role_lower or "web" in role_lower:
            job_titles = [role, f"Senior {role}", "React Developer", "UI Engineer"]
        elif "full stack" in role_lower or "fullstack" in role_lower:
            job_titles = [role, f"Senior {role}", "Full Stack Engineer", "Software Engineer"]
        elif "devops" in role_lower or "sre" in role_lower:
            job_titles = [role, "Cloud Infrastructure Engineer", "Site Reliability Engineer"]
        elif "data scientist" in role_lower or "data science" in role_lower:
            job_titles = [role, f"Senior {role}", "Machine Learning Engineer"]
        elif "engineer" in role_lower:
            job_titles = [f"Senior {role}", role, f"Lead {role}"]
        elif "specialist" in role_lower or "manager" in role_lower:
            job_titles = [role, f"Senior {role}", "Operations Manager"]
        elif "doctor" in role_lower or "practitioner" in role_lower:
            job_titles = [role, "Medical Consultant", "Telehealth Specialist"]
        else:
            job_titles = [role, f"Senior {role}", f"Lead {role}"]

        recommended_jobs = []
        for title in job_titles:
            match_res = JobMatcher.calculate_match(profile_data, title)
            # Find missing skills for this job
            gaps = SkillGapEngine.identify_gaps(profile_data, title)
            missing = [g["skill"] for g in gaps[:3]]
            
            # Local remote logic
            remote_eligible = any(t in role_lower for t in ["ai", "ml", "backend", "software", "designer", "freelancer", "frontend", "full stack", "fullstack", "devops", "data"])

            recommended_jobs.append({
                "title": title,
                "score": match_res["score"],
                "salary": salary_data["current"],
                "industry": primary_industry,
                "country": primary_country,
                "remote": remote_eligible,
                "missing_skills": missing
            })

        # 6. Skill Gaps
        gaps = SkillGapEngine.identify_gaps(profile_data, role)
        
        # 7. Market Demand
        market = MarketEngine.get_market_data(role)

        # 8. Remote Eligibility
        remote_score = 90 if any(t in role_lower for t in ["engineer", "designer", "developer", "programmer", "analyst"]) else 50
        remote_factors = [
            f"Technical skills ({', '.join([s.get('skill_name','') for s in profile_data.get('skills', [])][:3])}) support remote work models.",
            "Independent communication skills indicated in experience entries."
        ] if remote_score >= 70 else ["Physical presence or site visits standard for this profession."]

        # 9. Learning recommendations
        recs = RecommendationEngine.get_recommendations(role)

        return {
            "predicted_role": role,
            "recommended_jobs": recommended_jobs,
            "skill_gaps": gaps,
            "market_demand": market["demand_level"],
            "market_score": market["market_score"],
            "trending_skills": market["trending_skills"],
            "salary_forecast": {
                "current": salary_data["current"],
                "months_6": salary_data["forecast"]["months_6"],
                "months_12": salary_data["forecast"]["months_12"],
                "months_24": salary_data["forecast"]["months_24"]
            },
            "companies": companies,
            "countries": countries,
            "remote_eligibility": {
                "eligible": remote_score >= 70,
                "score": remote_score,
                "factors": remote_factors
            },
            "recommendations": recs
        }


class JobIntelligenceEngine:
    """
    Coordinates profile evaluation and handles model persistence.
    """
    @staticmethod
    def evaluate_profile(resume: Resume, profile_data: dict) -> dict:
        service = JobsGeminiService()
        result = service.generate_intelligence(profile_data)

        # 1. Clear previous recommendation rows for this resume to prevent stale rows
        JobRecommendation.objects.filter(resume=resume).delete()
        SkillGap.objects.filter(resume=resume).delete()

        # 2. Persist Job Recommendations
        for job in result.get("recommended_jobs", []):
            JobRecommendation.objects.create(
                resume=resume,
                title=job.get("title"),
                score=job.get("score", 0),
                salary=job.get("salary", ""),
                industry=job.get("industry", ""),
                country=job.get("country", ""),
                remote=job.get("remote", False),
                missing_skills=job.get("missing_skills", [])
            )

        # 3. Persist Skill Gaps
        for gap in result.get("skill_gaps", []):
            try:
                SkillGap.objects.create(
                    resume=resume,
                    skill=gap.get("skill"),
                    importance=gap.get("importance", "Medium")
                )
            except Exception as e:
                # Catch unique constraints just in case
                logger.warning(f"Could not persist skill gap '{gap.get('skill')}': {e}")

        return result
