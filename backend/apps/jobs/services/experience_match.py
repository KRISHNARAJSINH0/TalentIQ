import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ExperienceMatchEngine:
    """
    Evaluates experience years, companies, industry relevance, growth, and leadership checks.
    """
    @staticmethod
    def evaluate_experience(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        experiences = profile_data.get("experiences", [])
        
        # 1. Detect target years of experience required from JD
        # e.g., "5+ years", "3-5 years of experience", "minimum 2 years"
        required_years = 2 # default fallback
        match_years = re.search(r'(\d+)\+?\s*years?', jd_lower)
        if match_years:
            required_years = int(match_years.group(1))
            
        # 2. Calculate candidate actual experience years
        candidate_years = 0
        for exp in experiences:
            start_date = exp.get("start_date")
            end_date = exp.get("end_date") or datetime.now().date()
            
            # If dates are strings, convert to date objects
            if isinstance(start_date, str):
                try:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                except ValueError:
                    start_date = None
            if isinstance(end_date, str):
                try:
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                except ValueError:
                    end_date = None
            
            if start_date and end_date:
                delta_days = (end_date - start_date).days
                candidate_years += delta_days / 365.25
            else:
                # Fallback: assume 2 years if entry exists but no dates
                candidate_years += 2.0
                
        candidate_years = round(candidate_years, 1)
        
        # Calculate experience match score
        if candidate_years >= required_years:
            exp_match_score = 100
        else:
            exp_match_score = int((candidate_years / max(1, required_years)) * 100)
        exp_match_score = min(100, max(25, exp_match_score))
        
        # 3. Target companies matching / reputation indicators
        companies_worked = [exp.get("company", "") for exp in experiences]
        recognized_companies = ["google", "microsoft", "amazon", "netflix", "openai", "meta", "adobe", "salesforce", "oracle", "infosys", "tcs", "accenture", "wipro", "ibm", "capgemini"]
        matched_recognized = [c for c in companies_worked if c.lower() in recognized_companies]
        
        # 4. Growth indicator check
        # Look for hierarchical steps in designation history
        seniority_keywords = ["senior", "lead", "principal", "manager", "director", "head", "architect"]
        has_growth = False
        designations = [exp.get("designation", "").lower() for exp in experiences]
        
        # If they transitioned from junior/regular to senior/lead/manager, that's growth
        senior_positions = [d for d in designations if any(k in d for k in seniority_keywords)]
        if len(senior_positions) > 0 and len(designations) > 1:
            has_growth = True
            
        # 5. Leadership indicators
        leadership_indicators = []
        lead_words = ["manage", "lead", "spearhead", "mentor", "direct", "supervise", "coach", "coordinate"]
        
        for exp in experiences:
            desc = (exp.get("description") or "").lower()
            for w in lead_words:
                if w in desc and w not in leadership_indicators:
                    leadership_indicators.append(w)
                    
        return {
            "required_years": required_years,
            "candidate_years": candidate_years,
            "experience_match_score": exp_match_score,
            "companies_worked": companies_worked,
            "matched_recognized_companies": matched_recognized,
            "has_growth": has_growth,
            "leadership_indicators": leadership_indicators,
            "industry_match": 85 if any(term in jd_lower for exp in experiences for term in (exp.get("description") or "").lower().split()[:20]) else 60
        }
