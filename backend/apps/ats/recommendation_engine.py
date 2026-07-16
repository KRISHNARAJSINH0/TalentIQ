class RecommendationEngine:
    """
    Generates actionable, prioritized improvement recommendations for the resume profile
    to boost their estimated ATS score.
    """

    @staticmethod
    def generate_recommendations(profile, related_data: dict, keyword_results: dict, grammar_results: dict, formatting_results: dict) -> list:
        recommendations = []

        # 1. Contact Information Recommendations
        has_contact = bool(profile.user.email or profile.user.phone or profile.address)
        if not has_contact:
            recommendations.append({
                "category": "Contact Information",
                "suggestion": "Add direct contact information (phone number, email address, or city/state) to the profile header.",
                "priority": "critical",
                "potential_boost": 15
            })

        # 2. LinkedIn, GitHub, Portfolio
        if not profile.linkedin:
            recommendations.append({
                "category": "LinkedIn",
                "suggestion": "Include your LinkedIn profile URL to provide recruiters with professional social proof.",
                "priority": "optional",
                "potential_boost": 5
            })
        if not profile.github:
            # Only recommend if engineering/ML/data
            recommendations.append({
                "category": "GitHub",
                "suggestion": "Add a link to your GitHub profile to showcase your public code repositories and open-source contributions.",
                "priority": "important",
                "potential_boost": 8
            })
        if not (profile.portfolio_url or profile.website):
            recommendations.append({
                "category": "Portfolio",
                "suggestion": "Link a personal portfolio website or Behance/Dribbble profile to demonstrate tangible projects visually.",
                "priority": "optional",
                "potential_boost": 5
            })

        # 3. Skills Recommendations
        skills = related_data.get("skills", [])
        if not skills:
            recommendations.append({
                "category": "Skills",
                "suggestion": "List your core technical and soft skills on the profile to match resume screening keywords.",
                "priority": "critical",
                "potential_boost": 20
            })
        elif len(skills) < 6:
            recommendations.append({
                "category": "Skills",
                "suggestion": "Your skills list is sparse. Add at least 6-10 industry-relevant skills or tools to satisfy keyword queries.",
                "priority": "important",
                "potential_boost": 10
            })

        # Missing skills boost suggestion
        missing_skills = keyword_results.get("missing_skills", [])
        if missing_skills:
            skills_to_suggest = ", ".join(missing_skills[:4])
            recommendations.append({
                "category": "Skill Relevance",
                "suggestion": f"Incorporate missing core skills required for your industry: {skills_to_suggest}.",
                "priority": "important",
                "potential_boost": 8
            })

        # 4. Professional Summary
        summary = profile.summary or ""
        summary_words = len(summary.split())
        if summary_words == 0:
            recommendations.append({
                "category": "Professional Summary",
                "suggestion": "Draft a strong 3-4 sentence professional summary introducing your experience, tech stack, and key strengths.",
                "priority": "important",
                "potential_boost": 10
            })
        elif summary_words < 30 or summary_words > 200:
            recommendations.append({
                "category": "Professional Summary",
                "suggestion": f"Refine summary length: Currently it is {summary_words} words. Aim for a concise range of 50-150 words.",
                "priority": "optional",
                "potential_boost": 4
            })

        # 5. Work Experience & Projects
        experiences = related_data.get("experiences", [])
        if not experiences:
            recommendations.append({
                "category": "Experience",
                "suggestion": "Add professional work experience entries detailing your previous employment history.",
                "priority": "critical",
                "potential_boost": 25
            })
        
        projects = related_data.get("projects", [])
        if not projects:
            recommendations.append({
                "category": "Projects",
                "suggestion": "Include project descriptions to showcase hands-on application of your skills.",
                "priority": "important",
                "potential_boost": 10
            })
        
        # 6. Typos and Spelling errors
        typos = grammar_results.get("spelling_errors", [])
        if typos:
            typo_words = ", ".join([t["typo"] for t in typos])
            recommendations.append({
                "category": "Grammar",
                "suggestion": f"Fix formatting/spelling issues: Correct typos for '{typo_words}' to project high professionalism.",
                "priority": "critical",
                "potential_boost": 12
            })

        # 7. Action verbs & quantified achievements
        passive_count = grammar_results.get("passive_voice_count", 0)
        if passive_count > 3:
            recommendations.append({
                "category": "Action Verbs",
                "suggestion": "Change passive phrasings (e.g. 'was responsible for') to active, impact-oriented verbs like 'led' or 'automated'.",
                "priority": "important",
                "potential_boost": 7
            })

        metrics_count = len(keyword_results.get("found_keywords", []))
        if metrics_count < 4:
            recommendations.append({
                "category": "Keywords",
                "suggestion": "Increase keyword frequency of core concepts and industry tools inside your work description bullets.",
                "priority": "important",
                "potential_boost": 6
            })

        # Certifications
        certs = related_data.get("certifications", [])
        if not certs:
            recommendations.append({
                "category": "Certifications",
                "suggestion": "Include active professional certifications or professional licenses to boost validation credibility.",
                "priority": "optional",
                "potential_boost": 5
            })

        return recommendations
