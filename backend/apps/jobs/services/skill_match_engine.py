import re
import logging

logger = logging.getLogger(__name__)

# Predefined skill dictionary by category/profession for matching
SKILL_DICTIONARY = {
    "software": ["python", "javascript", "java", "c#", "c++", "rust", "go", "ruby", "php", "typescript", "html", "css", "git", "sql", "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "agile"],
    "data_science": ["python", "r", "sql", "machine learning", "deep learning", "statistics", "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "tableau", "power bi", "hadoop", "spark"],
    "design": ["figma", "sketch", "adobe xd", "photoshop", "illustrator", "ui", "ux", "wireframing", "prototyping", "design system", "typography", "branding"],
    "business": ["project management", "agile", "scrum", "marketing", "seo", "crm", "sales", "finance", "excel", "negotiation", "strategy", "communication", "leadership"],
    "medical": ["clinical", "diagnosis", "surgery", "patient care", "ehr", "pharmacology", "pediatrics", "anatomy", "cardiology", "medical research"],
    "legal": ["contract drafting", "litigation", "corporate law", "compliance", "legal research", "arbitration", "intellectual property", "counseling"],
    "education": ["pedagogy", "curriculum development", "lesson planning", "classroom management", "lms", "e-learning", "special education", "tutoring"]
}

class SkillMatchEngine:
    """
    Evaluates required, preferred, emerging, and missing skills against the JD and profile.
    """
    @staticmethod
    def evaluate_skills(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        candidate_skills = [s.get("skill_name", "").lower() for s in profile_data.get("skills", [])]
        
        # 1. Identify skills mentioned in the JD
        detected_jd_skills = set()
        for cat, skills_list in SKILL_DICTIONARY.items():
            for skill in skills_list:
                # Use word boundaries or simple matching for skills
                if re.search(r'\b' + re.escape(skill) + r'\b', jd_lower):
                    detected_jd_skills.add(skill)

        # Fallback to general words if no dictionary skills found
        if not detected_jd_skills:
            # simple tokenization fallback
            words = re.findall(r'\b[a-zA-Z]{3,15}\b', jd_lower)
            # filter stop words
            stops = {"with", "that", "this", "from", "have", "will", "your", "their"}
            detected_jd_skills = {w for w in words if w not in stops}

        # 2. Categorize into Required, Preferred, and Emerging
        required_skills = []
        preferred_skills = []
        emerging_skills = []
        
        # Emerging skills markers
        emerging_keywords = ["ai", "llm", "mcp", "rust", "kubernetes", "openai", "agentic", "vector", "langchain", "pytorch", "tensorflow"]

        for skill in detected_jd_skills:
            # Check if mentioned with priority adjectives
            pattern_req = rf"(?:must have|required|essential|minimum|experience in|strong command of|proficiency in|expert in)\b.*?{re.escape(skill)}"
            pattern_pref = rf"(?:preferred|plus|nice to have|good to have|desired|highly value|bonus)\b.*?{re.escape(skill)}"
            
            # Simple context matching: search around the skill keyword
            # Get a snippet of text around the skill (e.g. 50 characters before)
            match_idx = jd_lower.find(skill)
            snippet_before = jd_lower[max(0, match_idx - 60):match_idx]
            
            is_req = any(req_w in snippet_before for req_w in ["must", "require", "essential", "minimum", "strong", "proficient", "expert", "need"])
            is_pref = any(pref_w in snippet_before for pref_w in ["prefer", "plus", "nice", "good", "desire", "bonus", "optional"])
            
            if skill in emerging_keywords:
                emerging_skills.append(skill)
            
            # Default fallback: if neither is matched, default to Required if in tech/main category
            if is_pref:
                preferred_skills.append(skill)
            else:
                required_skills.append(skill)

        # Ensure we have some required/preferred for evaluation
        if not required_skills:
            required_skills = list(detected_jd_skills)[:max(1, len(detected_jd_skills) // 2)]
            preferred_skills = list(detected_jd_skills)[len(required_skills):]

        # 3. Match against candidate profile
        matched_required = [s for s in required_skills if any(s in cs or cs in s for cs in candidate_skills)]
        matched_preferred = [s for s in preferred_skills if any(s in cs or cs in s for cs in candidate_skills)]
        
        missing_skills = [s for s in required_skills if s not in matched_required]
        
        # Coverage calculation
        total_req_count = len(required_skills)
        coverage_pct = int((len(matched_required) / max(1, total_req_count)) * 100)
        
        # Skill Importance levels: High, Medium, Low based on mentions
        skill_importance = {}
        for s in detected_jd_skills:
            count = len(re.findall(r'\b' + re.escape(s) + r'\b', jd_lower))
            if count >= 3 or s in required_skills:
                skill_importance[s] = "High"
            elif count == 2 or s in preferred_skills:
                skill_importance[s] = "Medium"
            else:
                skill_importance[s] = "Low"

        # Limit sizes for report clean layout
        return {
            "required_skills": required_skills[:10],
            "preferred_skills": preferred_skills[:10],
            "emerging_skills": emerging_skills[:5],
            "missing_skills": missing_skills[:5],
            "skill_coverage": min(100, max(0, coverage_pct)),
            "skill_importance": skill_importance
        }
