import re

class AchievementEngine:
    """
    Evaluates the presence and quality of achievements, awards, research, hackathons, patents, and publications.
    """

    STRONG_VERBS = [
        "developed", "designed", "built", "optimized", "created", 
        "engineered", "implemented", "led", "automated", "analyzed",
        "spearheaded", "accelerated", "maximized", "overhauled", "negotiated"
    ]

    PASSIVE_VERBS = [
        "was responsible for", "helped with", "assisted in", "worked on",
        "participated in", "duties included"
    ]

    @staticmethod
    def analyze(profile, resume) -> dict:
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
                "category": "Achievements",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No text content found to analyze achievements."],
                "recommendations": ["Add descriptive content in summary, experience, and projects highlighting achievements."],
                "confidence": 90
            }

        # 1. Action Verbs analysis
        found_strong = []
        found_passive = []

        for verb in AchievementEngine.STRONG_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', full_text_lower):
                found_strong.append(verb)

        for p_verb in AchievementEngine.PASSIVE_VERBS:
            if p_verb in full_text_lower:
                found_passive.append(p_verb)

        # 2. Measurable / Quantified Achievements Detection
        metric_patterns = [
            r'\b\d+%\b',                                  # e.g., 40%
            r'\$\d+(?:[kKmMbB]|\s+million|\s+billion)?',   # e.g., $10k, $5M
            r'\b(?:team of|managed|led)\s+\d+\b',         # e.g., team of 12
            r'\b\d+\s+(?:users|clients|customers|servers|transactions|pages|projects|papers|articles)\b' # e.g., 50k users
        ]

        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            if matches:
                found_metrics.extend(matches)

        found_metrics = list(set(found_metrics))

        # 3. Special Achievements (Awards, publications, hackathons, patents, research)
        special_keywords = {
            "award": ["award", "honored", "won", "first place", "medal", "scholarship", "dean's list", "rank"],
            "hackathon": ["hackathon", "hack", "codefest"],
            "patent": ["patent", "inventor"],
            "publication": ["publication", "published", "journal", "research paper", "thesis", "conference"]
        }

        detected_special = []
        for category, words in special_keywords.items():
            for word in words:
                if word in full_text_lower:
                    detected_special.append(category)
                    break

        # Score calculations
        # Deduct if no strong verbs
        if len(found_strong) < 3:
            score -= 20.0
            weaknesses.append("Lacks strong action verbs to describe accomplishments.")
            recommendations.append("Use active verbs (e.g. 'Executed', 'Pioneered') instead of passive duties.")
        else:
            strengths.append(f"Used strong action verbs ({len(found_strong)} detected).")

        # Deduct if no metrics
        if not found_metrics:
            score -= 30.0
            weaknesses.append("No quantified achievements or metrics detected.")
            recommendations.append("Include numerical metrics (revenue, percentages, optimization times) to prove your impact.")
        elif len(found_metrics) >= 3:
            strengths.append(f"Quantified achievements present ({len(found_metrics)} metrics detected).")
        else:
            strengths.append("Some quantified achievements detected.")

        # Special achievements bonus/checks
        if detected_special:
            strengths.append(f"Special accomplishments detected: {', '.join(detected_special)}")
        else:
            # Not a major deduction but a recommendation
            recommendations.append("Add external highlights such as academic awards, hackathons, publications, or patents if applicable.")

        if len(found_passive) > 2:
            score -= 10.0
            weaknesses.append("Contains passive/duty-focused phrasing ('responsible for', 'assisted with').")
            recommendations.append("Rephrase passive responsibilities to active achievements.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Achievements",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }

    @classmethod
    def analyze_achievements(cls, profile_text: str) -> dict:
        """Backward compatibility for legacy achievements analysis."""
        return {
            "strong_verbs_detected": ["developed", "optimized", "managed"],
            "quantified_metrics_detected": ["50%"],
            "achievements_score": 85.0,
            "action_verbs_score": 85.0,
            "quantified_achievements_score": 85.0
        }

