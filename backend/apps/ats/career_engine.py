import re

class CareerEngine:
    """
    Evaluates Career Progression (vertical growth, promotions) and Leadership indicators.
    """

    @staticmethod
    def analyze_career_progression(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        experiences = list(profile.experiences.all()) if (hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all')) else []

        if not experiences:
            return {
                "category": "Career Progression",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No experience history to evaluate career progression."],
                "recommendations": ["Add professional roles to your timeline to showcase career progression."],
                "confidence": 95
            }

        # 1. Job Hopping / Longevity Check
        short_tenure_count = 0
        total_tenure_days = 0
        companies = set()

        for exp in experiences:
            company = (getattr(exp, 'company_name', '') or getattr(exp, 'company', '') or "").strip()
            if company:
                companies.add(company.lower())

            start_date = getattr(exp, 'start_date', None)
            end_date = getattr(exp, 'end_date', None)

            if start_date and end_date:
                days = (end_date - start_date).days
                total_tenure_days += days
                if days < 365:  # less than 1 year
                    short_tenure_count += 1

        # Longevity score calculations
        if len(experiences) > 1:
            short_ratio = short_tenure_count / len(experiences)
            if short_ratio > 0.5:
                score -= 20.0
                weaknesses.append("High ratio of short-term employments (<1 year) detected.")
                recommendations.append("Explain short-term roles (e.g. contracting, consulting) or group them together to avoid job-hopping concerns.")
            else:
                strengths.append("Demonstrates solid job tenure across roles.")
        
        # 2. Vertical growth (check if title keywords advance from junior to senior/lead)
        junior_keywords = ["junior", "jr", "associate", "intern", "trainee", "entry"]
        senior_keywords = ["senior", "sr", "lead", "principal", "head", "manager", "director", "vp"]
        
        has_junior = False
        has_senior = False

        for exp in experiences:
            role_title = (getattr(exp, 'job_title', '') or getattr(exp, 'role', '') or "").lower()
            if any(jk in role_title for jk in junior_keywords):
                has_junior = True
            if any(sk in role_title for sk in senior_keywords):
                has_senior = True

        if has_junior and has_senior:
            score += 10.0  # Promotion / vertical growth bonus
            strengths.append("Clear vertical growth from junior to senior titles detected.")
        elif len(companies) < len(experiences):
            # Same company listed multiple times (promotion/lateral movement)
            score += 10.0
            strengths.append("Lateral or vertical movement within the same organization detected.")
        else:
            strengths.append("Timelines represent standard, steady growth.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Career Progression",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }

    @staticmethod
    def analyze_leadership(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        summary_text = profile.summary or ""
        experiences_text = " ".join([getattr(exp, 'description', '') or "" for exp in (profile.experiences.all() if hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all') else [])])
        projects_text = " ".join([getattr(proj, 'description', '') or "" for proj in (profile.projects.all() if hasattr(profile, 'projects') and hasattr(profile.projects, 'all') else [])])
        
        full_text = f"{summary_text} {experiences_text} {projects_text}".strip().lower()

        if not full_text:
            return {
                "category": "Leadership",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No text to evaluate leadership indicators."],
                "recommendations": ["Highlight leadership and ownership experience in your work descriptions."],
                "confidence": 95
            }

        # 1. Leadership keywords check
        leadership_terms = ["led", "managed", "spearheaded", "hired", "trained", "mentored", "lead", "manager", "director", "head of", "supervised", "coordinate", "oversaw"]
        detected_terms = [t for t in leadership_terms if re.search(r'\b' + re.escape(t) + r'\b', full_text)]

        if not detected_terms:
            score -= 30.0
            weaknesses.append("Lacks leadership or project ownership indicators.")
            recommendations.append("Incorporate terms like 'Led', 'Mentored', or 'Spearheaded' to demonstrate ownership and initiative.")
        else:
            strengths.append(f"Strong ownership and leadership indicators detected: {', '.join(detected_terms[:3])}.")

        # 2. Team sizes, budgets, and leadership scope
        scope_indicators = ["team of", "budget of", "cross-functional", "stakeholder", "initiative"]
        detected_scope = [si for si in scope_indicators if si in full_text]
        
        if detected_scope:
            strengths.append("Highlights the scale and scope of leadership (e.g. team size, budgets).")
        else:
            score -= 10.0
            weaknesses.append("Missing context on leadership scope (e.g., team sizes managed, stakeholders influenced).")
            recommendations.append("Specify leadership scope such as number of people managed or project budgets handled.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Leadership",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
