import re

class AchievementEngine:
    """
    Analyzes accomplishments, quantified metrics, and use of strong action verbs.
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
    def analyze_achievements(profile_text: str) -> dict:
        text_lower = profile_text.lower()

        # 1. Action Verbs analysis
        found_strong = []
        found_passive = []

        for verb in AchievementEngine.STRONG_VERBS:
            if re.search(r'\b' + re.escape(verb) + r'\b', text_lower):
                found_strong.append(verb)

        for p_verb in AchievementEngine.PASSIVE_VERBS:
            if p_verb in text_lower:
                found_passive.append(p_verb)

        # Action Verbs Score calculation
        # Base 50, +10 per strong verb up to 100, -10 per passive wording
        action_verbs_score = 50.0 + (len(found_strong) * 10.0) - (len(found_passive) * 12.0)
        action_verbs_score = max(10.0, min(100.0, action_verbs_score))

        # 2. Measurable / Quantified Achievements Detection
        # Match percentages (e.g. 40%, 18%), currency ($10k, $5M), numbers with count qualifiers (serving 50k users, team of 12)
        metric_patterns = [
            r'\b\d+%\b',                                  # e.g., 40%
            r'\$\d+(?:[kKmMbB]|\s+million|\s+billion)?',   # e.g., $10k, $5M, $3 million
            r'\b(?:team of|managed|led)\s+\d+\b',         # e.g., team of 12
            r'\b\d+\s+(?:users|clients|customers|servers|transactions|pages|projects|papers|articles)\b', # e.g., 50k users, 3 research papers
            r'\b(?:reduced|improved|increased|decreased|saved)\s+(?:by\s+)?\d+\b' # e.g., reduced by 20
        ]

        found_metrics = []
        for pattern in metric_patterns:
            matches = re.findall(pattern, profile_text, re.IGNORECASE)
            if matches:
                found_metrics.extend(matches)

        # Remove duplicates
        found_metrics = list(set(found_metrics))

        # Quantified Achievements Score
        # Based on quantity of metrics found
        quantified_score = min(100.0, len(found_metrics) * 20.0)
        # If they have at least 1-2 quantified metrics, set it reasonably high
        if len(found_metrics) >= 3:
            quantified_score = max(quantified_score, 90.0)
        elif len(found_metrics) > 0:
            quantified_score = max(quantified_score, 70.0)
        else:
            quantified_score = 30.0

        # General Achievements Score (looks at bullet counts or explicit achievement-oriented sentences)
        ach_score = 50.0
        # Boost if experience or projects have clear action-result structure
        if len(found_strong) >= 4:
            ach_score += 20.0
        if len(found_metrics) >= 2:
            ach_score += 30.0
        ach_score = min(100.0, ach_score)

        return {
            "action_verbs_score": round(action_verbs_score, 2),
            "quantified_achievements_score": round(quantified_score, 2),
            "achievements_score": round(ach_score, 2),
            "strong_verbs_detected": found_strong,
            "passive_phrases_detected": found_passive,
            "quantified_metrics_detected": found_metrics[:6]
        }
