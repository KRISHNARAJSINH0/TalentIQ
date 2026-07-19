import logging

logger = logging.getLogger(__name__)

class PriorityEngine:
    """
    Categorizes ATS improvement recommendations into Critical, High, Medium, and Low priorities.
    Also calculates their estimated score impact.
    """

    @classmethod
    def prioritize_recommendations(cls, category_scores: list) -> list:
        """
        Analyzes category evaluation scores and formats recommendations with priorities.
        """
        prioritized_list = []

        for breakdown in category_scores:
            cat = breakdown["category"]
            score = breakdown["score"]
            recs = breakdown.get("recommendations", [])
            weight = breakdown.get("weight", 0.05)

            if score >= 85 or not recs:
                continue  # Category is already in a good state

            # Map category to priority
            cat_lower = cat.lower()
            if "contact" in cat_lower or "skill" in cat_lower:
                priority = "critical"
                base_impact = 10
            elif "experience" in cat_lower or "project" in cat_lower or "github" in cat_lower:
                priority = "high"
                base_impact = 8
            elif "summary" in cat_lower or "certification" in cat_lower or "linkedin" in cat_lower or "consistency" in cat_lower:
                priority = "medium"
                base_impact = 5
            else:
                priority = "low"
                base_impact = 3

            # Scale impact based on weight contribution
            impact = round(base_impact * (weight / 0.05))
            impact = max(1, min(15, impact))  # Clamp between 1 and 15 points

            for rec in recs:
                if rec.strip():
                    prioritized_list.append({
                        "category": cat,
                        "recommendation_text": rec,
                        "priority": priority,
                        "score_impact": impact
                    })

        # Sort: critical first, then high, then medium, then low
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        prioritized_list.sort(key=lambda x: priority_order.get(x["priority"], 4))

        return prioritized_list
