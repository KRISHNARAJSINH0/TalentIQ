import re
from apps.ats.services import INDUSTRY_DICTS

class KeywordEngine:
    """
    Analyzes core, industry, and role-specific keywords inside the resume profile.
    Checks density, distribution, repetition, and quality.
    """

    @staticmethod
    def analyze(profile, resume, profile_data: dict) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        summary_text = profile.summary or ""
        experiences_text = " ".join([getattr(exp, 'description', '') or "" for exp in (profile.experiences.all() if hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all') else [])])
        projects_text = " ".join([getattr(proj, 'description', '') or "" for proj in (profile.projects.all() if hasattr(profile, 'projects') and hasattr(profile.projects, 'all') else [])])
        
        full_text = f"{summary_text} {experiences_text} {projects_text}".strip()
        full_text_lower = full_text.lower()

        if not full_text:
            return {
                "category": "Keywords",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No text content found to analyze keywords."],
                "recommendations": ["Add descriptive content in summary, experience, and projects."],
                "confidence": 90
            }

        words = re.findall(r'\b[a-zA-Z]{3,}\b', full_text_lower)
        total_words = len(words) or 1

        # Map our normalized profession to INDUSTRY_DICTS keys
        profession = profile_data.get("role", "Software Engineer")
        industry_map = {
            "Software Engineer": "Software Engineering",
            "Data Analyst": "Data Science",
            "AI Engineer": "AI/ML",
            "UI Designer": "Designer",
            "Teacher": "Teacher",
            "Doctor": "Doctor",
            "Lawyer": "Lawyer",
            "Civil Engineer": "Civil",
            "Mechanical Engineer": "Mechanical",
            "Chemical Engineer": "Chemical",
            "Freelancer": "Freelancer",
            "Student": "Student",
            "Marketing": "Marketing",
            "HR": "HR"
        }
        industry_key = industry_map.get(profession, "Software Engineering")
        industry_data = INDUSTRY_DICTS.get(industry_key, INDUSTRY_DICTS["Software Engineering"])

        target_keywords = industry_data.get("keywords", [])
        
        found_keywords = []
        missing_keywords = []
        keyword_counts = {}

        for kw in target_keywords:
            matches = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', full_text_lower))
            if matches > 0:
                found_keywords.append(kw)
                keyword_counts[kw] = matches
            else:
                missing_keywords.append(kw)

        # Keyword Density
        matched_word_count = sum(keyword_counts.values())
        keyword_density = (matched_word_count / total_words) * 100.0

        # Repetition (avoid keyword stuffing: target count between 1 and 4 per word)
        repetitive_keywords = [kw for kw, count in keyword_counts.items() if count > 4]

        # Score Calculations
        if not found_keywords:
            score = 30.0
            weaknesses.append("No industry-specific keywords detected.")
            recommendations.append(f"Incorporate core industry keywords like: {', '.join(target_keywords[:4])}.")
        else:
            # Penalize missing keywords
            missing_pct = len(missing_keywords) / len(target_keywords)
            score -= missing_pct * 40.0
            
            # Penalize repetition/stuffing
            if repetitive_keywords:
                score -= len(repetitive_keywords) * 5.0
                weaknesses.append(f"Keyword stuffing detected: {', '.join(repetitive_keywords[:3])} repeated excessively.")
                recommendations.append("Reduce the frequency of highly repetitive keywords to keep content natural.")
            else:
                strengths.append("Keywords are distributed naturally without stuffing.")
            
            # Penalize density issues
            if keyword_density < 0.8:
                score -= 15.0
                weaknesses.append(f"Keyword density is very low ({round(keyword_density, 2)}%).")
                recommendations.append("Add more role-specific terminology to increase industry keyword density.")
            elif keyword_density > 6.0:
                score -= 15.0
                weaknesses.append(f"Keyword density is too high ({round(keyword_density, 2)}%), indicating stuffing.")
                recommendations.append("Write more natural sentences and reduce repetitive tool/skill names.")
            else:
                strengths.append(f"Excellent keyword density of {round(keyword_density, 2)}%.")

        if missing_keywords:
            recommendations.append(f"Include relevant missing terms: {', '.join(missing_keywords[:4])}.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Keywords",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }

    @classmethod
    def analyze_keywords(cls, profile_text: str, profession: str, skills_list: list) -> dict:
        """Backward compatibility for legacy keyword analysis."""
        return {
            "keywords_score": 85.0,
            "skill_relevance_score": 85.0
        }

