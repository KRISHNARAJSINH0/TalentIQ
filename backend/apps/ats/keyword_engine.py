import re
from apps.ats.services import INDUSTRY_DICTS

class KeywordEngine:
    """
    Analyzes core, industry, and role-specific keywords inside the resume profile.
    Checks density, distribution, repetition, and quality.
    """

    @staticmethod
    def analyze_keywords(profile_text: str, profession: str, skills_list: list) -> dict:
        text_lower = profile_text.lower()
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)
        total_words = len(words) or 1

        # Map our normalized profession to INDUSTRY_DICTS keys
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
        target_skills = industry_data.get("skills", [])

        # Core/Industry/Role Keywords Found
        found_keywords = []
        missing_keywords = []
        keyword_counts = {}

        for kw in target_keywords:
            matches = len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', text_lower))
            if matches > 0:
                found_keywords.append(kw)
                keyword_counts[kw] = matches
            else:
                missing_keywords.append(kw)

        # Keyword Density
        matched_word_count = sum(keyword_counts.values())
        keyword_density = (matched_word_count / total_words) * 100.0

        # Distribution Check (Summary vs Experience vs Skills)
        # Higher score if keyword matches are distributed
        # Repetition (avoid keyword stuffing: target count between 1 and 4 per word)
        repetitive_keywords = [kw for kw, count in keyword_counts.items() if count > 4]

        # Keyword Quality Score (0-100)
        # Penalize if no keywords found, or stuffing, reward decent density (1-4%)
        keyword_quality = 100.0
        if not found_keywords:
            keyword_quality = 30.0
        else:
            # Penalize missing keywords
            missing_pct = len(missing_keywords) / len(target_keywords)
            keyword_quality -= missing_pct * 40.0
            
            # Penalize repetition/stuffing
            if repetitive_keywords:
                keyword_quality -= len(repetitive_keywords) * 5.0
            
            # Penalize excessive or too low density
            if keyword_density < 0.5:
                keyword_quality -= 15.0
            elif keyword_density > 6.0:
                keyword_quality -= 10.0 # Keyword stuffing penalty

        # Skill relevance score
        skills_lower = [s.lower() for s in skills_list]
        relevant_skills_found = [s for s in target_skills if s.lower() in skills_lower]
        missing_skills = [s for s in target_skills if s.lower() not in skills_lower]
        
        skill_relevance_score = 100.0
        if target_skills:
            relevance_ratio = len(relevant_skills_found) / len(target_skills)
            skill_relevance_score = relevance_ratio * 100.0

        return {
            "keywords_score": round(max(0.0, min(100.0, keyword_quality)), 2),
            "skill_relevance_score": round(max(0.0, min(100.0, skill_relevance_score)), 2),
            "total_keywords_count": matched_word_count,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords[:8],
            "keyword_density_pct": round(keyword_density, 2),
            "repetitive_keywords": repetitive_keywords,
            "relevant_skills_found": relevant_skills_found,
            "missing_skills": missing_skills[:8],
            "keyword_distribution": {
                "summary": len(re.findall(r'\b(summary|profile|about)\b', text_lower)),
                "experience": len(re.findall(r'\b(experience|history|employment|work)\b', text_lower)),
                "skills": len(re.findall(r'\b(skills|technologies|tools|expertise)\b', text_lower))
            }
        }
