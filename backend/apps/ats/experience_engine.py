import re
from datetime import datetime

class ExperienceEngine:
    """
    Evaluates the quality, impact, verbs, metrics, and progression of the Experience section.
    """

    @staticmethod
    def analyze(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Get experience objects
        experiences = []
        if hasattr(profile, 'experiences') and profile.experiences:
            if hasattr(profile.experiences, 'all'):
                experiences = list(profile.experiences.all())
            elif isinstance(profile.experiences, list):
                experiences = profile.experiences

        if not experiences:
            return {
                "category": "Experience",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No work experience listed in your profile."],
                "recommendations": ["Add detailed work history including company name, role, duration, and bullet points describing achievements."],
                "confidence": 95
            }

        # 1. Quantified Metrics / Business Impact Check
        # Search for metrics in experience descriptions
        total_descriptions_length = 0
        total_metrics_count = 0
        strong_verbs_count = 0
        
        strong_verbs = ["developed", "optimized", "managed", "designed", "engineered", "implemented", "led", "automated", "analyzed", "spearheaded", "accelerated", "maximized"]
        metric_patterns = [
            r'\b\d+%\b',                                  # e.g., 40%
            r'\$\d+(?:[kKmMbB]|\s+million|\s+billion)?',   # e.g., $10k, $5M
            r'\b(?:team of|managed|led)\s+\d+\b',         # e.g., team of 12
            r'\b\d+\s+(?:users|clients|customers|servers|transactions|pages|projects)\b' # e.g., 50k users
        ]

        companies_seen = set()
        multi_role_companies = set()

        for exp in experiences:
            company = (getattr(exp, 'company_name', '') or getattr(exp, 'company', '') or "").strip()
            role = (getattr(exp, 'job_title', '') or getattr(exp, 'role', '') or "").strip()
            desc = (getattr(exp, 'description', '') or "").strip()
            
            if company:
                if company.lower() in companies_seen:
                    multi_role_companies.add(company.lower())
                companies_seen.add(company.lower())

            total_descriptions_length += len(desc.split())
            
            # Check metrics
            for pattern in metric_patterns:
                total_metrics_count += len(re.findall(pattern, desc, re.IGNORECASE))
                
            # Check action verbs
            for verb in strong_verbs:
                strong_verbs_count += len(re.findall(r'\b' + re.escape(verb) + r'\b', desc.lower()))

        # Average description length per role check
        avg_len = total_descriptions_length / len(experiences)
        if avg_len < 30:
            score -= 20.0
            weaknesses.append("Experience descriptions are too short or lack detail.")
            recommendations.append("Provide 3-5 detailed bullet points for each role explaining your tasks and results.")
        elif avg_len > 250:
            score -= 10.0
            weaknesses.append("Experience descriptions are too verbose.")
            recommendations.append("Make your experience bullet points more concise to improve readability.")
        else:
            strengths.append("Work experience descriptions have appropriate detail.")

        # Metrics check
        if total_metrics_count == 0:
            score -= 25.0
            weaknesses.append("Lacks quantified achievements or metrics (%, $, numerical outcomes).")
            recommendations.append("Quantify your accomplishments (e.g., 'reduced load time by 30%', 'managed $50K budget') to demonstrate real impact.")
        elif total_metrics_count < len(experiences):
            score -= 10.0
            weaknesses.append("Not all job descriptions highlight quantified achievements.")
            recommendations.append("Aim to include at least one quantified result (%, $, scale) for every professional role.")
        else:
            strengths.append("Strong use of quantified business results and metrics.")

        # Action verbs check
        if strong_verbs_count < len(experiences) * 2:
            score -= 15.0
            weaknesses.append("Lacks strong professional action verbs.")
            recommendations.append("Begin description bullets with strong verbs (e.g. 'Optimized', 'Spearheaded', 'Engineered') instead of passive statements.")
        else:
            strengths.append("Good usage of impactful action verbs.")

        # Career progression check (multi-roles at same company represents promotions)
        if multi_role_companies:
            strengths.append("Clear career progression/promotions detected (multiple roles at same company).")
        
        # Duration verification
        insufficient_duration = False
        for exp in experiences:
            # check duration if start/end dates are available
            start_date = getattr(exp, 'start_date', None)
            end_date = getattr(exp, 'end_date', None)
            if start_date:
                # If end_date is None, assume present
                effective_end = end_date or datetime.now().date()
                try:
                    delta = (effective_end - start_date).days
                    if delta < 90:
                        insufficient_duration = True
                except Exception:
                    pass
        
        if insufficient_duration:
            score -= 10.0
            weaknesses.append("Short employment durations (< 3 months) detected without context.")
            recommendations.append("State if short-term roles were contracts, internships, or temporary assignments to avoid being perceived as job-hopping.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Experience",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
