import re
import logging

logger = logging.getLogger(__name__)

class ProjectMatchEngine:
    """
    Evaluates projects, tech stacks, live links, github repositories, architecture, and impact.
    """
    @staticmethod
    def evaluate_projects(profile_data: dict, jd_text: str) -> dict:
        jd_lower = jd_text.lower()
        projects = profile_data.get("projects", [])
        
        # 1. Relevant Projects Count & Details
        relevant_projects = []
        tech_matches = 0
        has_github = False
        has_live = False
        architecture_indicators = []
        business_impact_metrics = []
        
        arch_words = ["architecture", "microservices", "scalable", "pipeline", "database design", "api design", "system", "infrastructure"]
        
        for proj in projects:
            p_name = proj.get("project_name", "")
            p_desc = (proj.get("description") or "").lower()
            p_tech = (proj.get("technologies") or "").lower()
            
            # Relevancy: overlap of words
            words = set(re.findall(r'\b\w{3,12}\b', p_desc))
            jd_words = set(re.findall(r'\b\w{3,12}\b', jd_lower))
            overlap = words.intersection(jd_words)
            
            # Check tech overlap
            tech_items = [t.strip().lower() for t in p_tech.split(",") if t.strip()]
            for item in tech_items:
                if item in jd_lower:
                    tech_matches += 1
            
            # Links
            if proj.get("github_url"):
                has_github = True
            if proj.get("live_url"):
                has_live = True
                
            # Architecture checks
            for aw in arch_words:
                if aw in p_desc and aw not in architecture_indicators:
                    architecture_indicators.append(aw)
                    
            # Impact checks (numbers or percent signs)
            metrics = re.findall(r'\b\d+(?:%|\s*percent|\s*k|\s*m|\s*lakhs?|\s*usd|\s*\$)\b', p_desc)
            if metrics:
                business_impact_metrics.extend(metrics)
                
            # Classify project as relevant if overlap is high
            if len(overlap) >= 3 or any(t in jd_lower for t in tech_items):
                relevant_projects.append(p_name)
                
        # Calculate projects match score
        base_score = 40
        if len(projects) > 0:
            base_score += min(30, len(projects) * 10)
        if tech_matches > 0:
            base_score += min(15, tech_matches * 3)
        if has_github:
            base_score += 10
        if has_live:
            base_score += 5
            
        final_score = min(100, base_score)
        
        return {
            "projects_match_score": final_score,
            "relevant_projects": relevant_projects,
            "tech_overlap_count": tech_matches,
            "has_github": has_github,
            "has_live_demo": has_live,
            "architecture_indicators": architecture_indicators,
            "business_impact_metrics": list(set(business_impact_metrics))[:5]
        }
