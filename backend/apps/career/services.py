import os
import json
import logging
import time
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

# pyrefly: ignore [missing-import]
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)


class CareerGeminiService:
    """
    Wrapper around Gemini API. Includes prompts, validation, caching mock fallbacks,
    and automatic retries for Career Assistant endpoints.
    """
    _initialized = False
    use_mock = False

    @classmethod
    def initialize_client(cls):
        if not cls._initialized:
            api_key = getattr(settings, "GEMINI_API_KEY", None) or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY is not defined. Falling back to local Mock Career AI Service.")
                cls.use_mock = True
            else:
                try:
                    genai.configure(api_key=api_key)
                    cls.use_mock = False
                except Exception as e:
                    logger.warning(f"Failed to configure Gemini client: {e}. Falling back to Mock.")
                    cls.use_mock = True
            cls._initialized = True

    def generate_content(self, prompt: str, is_json: bool = True, retry_count: int = 3, backoff_factor: float = 2.0) -> str:
        self.initialize_client()
        
        if self.use_mock:
            return self._mock_fallback(prompt)

        model_name = getattr(settings, "GEMINI_MODEL", "gemini-1.5-flash")
        model = genai.GenerativeModel(model_name)
        
        config = GenerationConfig(
            response_mime_type="application/json" if is_json else "text/plain",
            temperature=0.2
        )

        for attempt in range(retry_count):
            try:
                response = model.generate_content(prompt, generation_config=config)
                if response and response.text:
                    return response.text
                raise ValueError("Empty response text from Gemini.")
            except Exception as e:
                logger.warning(f"Gemini API request failed (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt == retry_count - 1:
                    logger.warning("Exhausted Gemini attempts. Using mock fallback.")
                    return self._mock_fallback(prompt)
                time.sleep(backoff_factor ** attempt)
        
        return self._mock_fallback(prompt)

    def _mock_fallback(self, prompt: str) -> str:
        """
        Detects if this is a cover letter request or a career analysis request,
        and generates highly detailed, structured mock responses.
        """
        # If it's a cover letter request
        if "Cover Letter" in prompt or "cover-letter" in prompt:
            company = "Target Company"
            position = "Senior Professional"
            tone = "Professional"
            
            # Simple regex parser to extract parameters from mock prompt
            for line in prompt.splitlines():
                if "Company:" in line:
                    company = line.split("Company:")[1].strip()
                elif "Position:" in line:
                    position = line.split("Position:")[1].strip()
                elif "Tone:" in line:
                    tone = line.split("Tone:")[1].strip()

            mock_letter = f"""Dear Hiring Team,

I am writing to express my strong interest in the {position} position at {company}. Based on my background as described in my master profile, I am confident that my experience and skills align perfectly with the goals of your team.

Throughout my career, I have focused on solving complex challenges, delivering scalable results, and collaborating with cross-functional teams. I am particularly excited about {company}'s current trajectory and believe my expertise will allow me to hit the ground running.

Thank you for considering my application. I look forward to the opportunity to discuss how my profile and background can contribute to your continued success.

Sincerely,
[Your Name]"""
            
            return json.dumps({
                "cover_letter": mock_letter
            })

        # Default fallback: Career Analysis
        # Parse years of experience and current role from prompt if possible
        headline = "Software Professional"
        skills = ["Python", "SQL", "Git"]
        if "master_resume_json" in prompt:
            try:
                # Find start of JSON
                start_idx = prompt.find("{")
                end_idx = prompt.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    data = json.loads(prompt[start_idx:end_idx+1])
                    headline = data.get("headline") or data.get("current_designation") or headline
                    skills = [s.get("skill_name") for s in data.get("skills", [])][:6] or skills
            except Exception:
                pass

        mock_analysis = {
            "scores": {
                "career_readiness": 85,
                "growth_score": 80,
                "learning_score": 75,
                "industry_alignment": 90,
                "skill_strength": 82,
                "market_demand": 88
            },
            "career_details": {
                "current_role": headline,
                "career_stage": "Mid-Level Professional",
                "years_experience": "3-5 Years",
                "industry": "Technology / Software Development",
                "strengths": [
                    "Strong grasp of core technical principles",
                    "Adept at system design and requirements mapping",
                    "Active communicator and collaborator"
                ],
                "weaknesses": [
                    "Limited exposure to complex cloud architecture scaling",
                    "Needs more experience in mentoring junior engineers",
                    "Could benefit from broader DevOps knowledge"
                ],
                "career_direction": "Transition towards Senior Engineering and Technical Architecture roles.",
                "growth_opportunities": "Acquire advanced cloud certifications and lead cross-team architecture projects."
            },
            "skill_gap": {
                "current_skills": skills,
                "missing_skills": ["Docker", "Redis", "AWS Cloud Practitioner", "GraphQL", "CI/CD Pipelines", "Celery", "Kubernetes", "Microservices Design"]
            },
            "roadmap": {
                "milestones": [
                    {
                        "milestone_title": "Milestone 1: Containerization & Caching (Months 1-3)",
                        "sequence": 1,
                        "description": "Learn to containerize deployments and implement performance caching systems.",
                        "items": [
                            {"name": "Docker Basics", "category": "Technology", "resource": "Docker Official Docs & Tutorials"},
                            {"name": "Redis caching layers", "category": "Technology", "resource": "Redis University courses"},
                            {"name": "Read: 'Designing Data-Intensive Applications' by Martin Kleppmann", "category": "Book", "resource": "Bookstore / Libraries"}
                        ]
                    },
                    {
                        "milestone_title": "Milestone 2: Cloud Architecting & CI/CD (Months 4-6)",
                        "sequence": 2,
                        "description": "Deploy to cloud infrastructure and build automated integration pipelines.",
                        "items": [
                            {"name": "AWS Certified Cloud Practitioner", "category": "Certification", "resource": "AWS Academy & Cloud Academy"},
                            {"name": "GitHub Actions / GitLab CI", "category": "Technology", "resource": "Official CI/CD tutorials"}
                        ]
                    },
                    {
                        "milestone_title": "Milestone 3: Microservices & Advanced Orchestration (Months 7-12)",
                        "sequence": 3,
                        "description": "Transition application clusters into production-grade orchestration topologies.",
                        "items": [
                            {"name": "Kubernetes Administration", "category": "Technology", "resource": "CNCF K8s certification path"},
                            {"name": "Celery asynchronous queueing", "category": "Technology", "resource": "Celery Project docs"}
                        ]
                    }
                ],
                "estimated_duration": "12 Months"
            },
            "suggestions": {
                "roles": ["Senior Backend Developer", "Systems Architect", "DevOps Engineer"],
                "industries": ["Fintech", "SaaS Enterprise Platforms", "AI Infrastructure Providers"],
                "career_transitions": "From Mid-level Engineer to Tech Lead or Systems Architect.",
                "emerging_technologies": ["Distributed Vector Databases", "LLM Fine-tuning Orchestration", "Serverless Edge Runtimes"],
                "trending_skills": ["Cloud Security", "Prompt Engineering", "TypeScript Development"]
            }
        }
        return json.dumps(mock_analysis, indent=2)


class CareerAnalysisService:
    """
    Main orchestrator for profile analysis, skill gaps, roadmaps, and career scoring.
    """
    @staticmethod
    def analyze_profile(profile_data: dict, ats_results: dict = None) -> dict:
        gemini = CareerGeminiService()
        
        prompt = f"""
You are a Senior AI Career Coach and Resume Expert. Analyze the following verified master resume profile JSON and ATS results (if provided) to output a complete, highly comprehensive career planning analysis in JSON format.

VERIFIED RESUME PROFILE JSON:
{json.dumps(profile_data, cls=DjangoJSONEncoder, indent=2)}

ATS RESULTS:
{json.dumps(ats_results or {}, cls=DjangoJSONEncoder, indent=2)}

OUTPUT RULES:
- Output ONLY the raw JSON string. Do NOT wrap it in markdown code blocks.
- Fill all fields realistically based on candidate skills.

JSON SCHEMA TO RETURN:
{{
  "scores": {{
    "career_readiness": 0-100 score,
    "growth_score": 0-100 score,
    "learning_score": 0-100 score,
    "industry_alignment": 0-100 score,
    "skill_strength": 0-100 score,
    "market_demand": 0-100 score
  }},
  "career_details": {{
    "current_role": "string",
    "career_stage": "string",
    "years_experience": "string",
    "industry": "string",
    "strengths": ["string"],
    "weaknesses": ["string"],
    "career_direction": "string",
    "growth_opportunities": "string"
  }},
  "skill_gap": {{
    "current_skills": ["string"],
    "missing_skills": ["string"]
  }},
  "roadmap": {{
    "milestones": [
      {{
        "milestone_title": "string",
        "sequence": 1,
        "description": "string",
        "items": [
          {{
            "name": "string",
            "category": "Technology | Certification | Course | Book | Tutorial | Community",
            "resource": "string"
          }}
        ]
      }}
    ],
    "estimated_duration": "string"
  }},
  "suggestions": {{
    "roles": ["string"],
    "industries": ["string"],
    "career_transitions": "string",
    "emerging_technologies": ["string"],
    "trending_skills": ["string"]
  }}
}}
"""
        response_text = gemini.generate_content(prompt)
        try:
            return json.loads(response_text)
        except Exception as e:
            logger.error(f"Failed to parse Career Analysis JSON: {e}")
            # parse mock fallback
            return json.loads(gemini._mock_fallback(prompt))


class CoverLetterGeneratorService:
    """
    Service responsible for creating tailor-made Cover Letters based on target descriptions.
    """
    @staticmethod
    def generate(profile_data: dict, company: str, position: str, description: str, tone: str, letter_type: str) -> str:
        gemini = CareerGeminiService()
        
        prompt = f"""
You are a Senior Career Coach and Expert Writer. Write a beautiful, tailor-made Cover Letter using the candidate's verified profile data and job application parameters.

CANDIDATE PROFILE DATA:
{json.dumps(profile_data, cls=DjangoJSONEncoder, indent=2)}

JOB DETAILS:
Company: {company}
Position: {position}
Job Description: {description}
Tone: {tone}
Cover Letter Type: {letter_type}

OUTPUT RULES:
- Output a JSON with a single key "cover_letter" containing the cover letter text.
- Do not add markdown backticks.

SCHEMA:
{{
  "cover_letter": "The full text of the cover letter with proper spacing and paragraph breaks."
}}
"""
        response_text = gemini.generate_content(prompt)
        try:
            parsed = json.loads(response_text)
            return parsed.get("cover_letter", "")
        except Exception as e:
            logger.error(f"Failed to parse Cover Letter JSON: {e}")
            fallback = json.loads(gemini._mock_fallback(prompt))
            return fallback.get("cover_letter", "")
