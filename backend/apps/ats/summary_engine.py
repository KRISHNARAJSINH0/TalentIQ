import re

class SummaryEngine:
    """
    Evaluates the quality, impact, and alignment of the Professional Summary.
    """

    @staticmethod
    def analyze(profile, resume) -> dict:
        summary = (profile.summary or "").strip()
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        if not summary:
            return {
                "category": "Professional Summary",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["Professional summary is missing entirely."],
                "recommendations": ["Add a professional summary of 3-5 lines highlighting your key experience, skills, and achievements."],
                "confidence": 90
            }

        # 1. Length Check
        word_count = len(summary.split())
        if word_count < 30:
            score -= 20.0
            weaknesses.append("Summary is too brief or lacks details.")
            recommendations.append("Expand your summary to at least 40-50 words to highlight your core strengths and key achievements.")
        elif word_count > 150:
            score -= 15.0
            weaknesses.append("Summary is too verbose or long.")
            recommendations.append("Condense the summary to under 150 words (3-5 concise lines) to keep the recruiter engaged.")
        else:
            strengths.append("Professional summary length is optimal.")

        # 2. Pronouns / Professional Tone
        pronouns = re.findall(r"\b(i|me|my|we|our|us)\b", summary.lower())
        if pronouns:
            score -= len(pronouns) * 5.0
            weaknesses.append("First-person pronouns detected in the summary.")
            recommendations.append("Write the summary in third-person or passive voice, removing first-person pronouns like 'I', 'me', or 'my'.")
        else:
            strengths.append("Maintains a professional, third-person writing tone.")

        # 3. Action Verbs & Impact
        strong_verbs = ["spearheaded", "developed", "led", "optimized", "managed", "designed", "engineered", "streamlined", "increased", "reduced"]
        found_verbs = [v for v in strong_verbs if re.search(r"\b" + re.escape(v) + r"\b", summary.lower())]
        if not found_verbs:
            score -= 15.0
            weaknesses.append("Lacks strong action verbs or quantifiable impact phrases.")
            recommendations.append("Incorporate powerful action verbs (e.g. 'Optimized', 'Spearheaded') to demonstrate action-oriented value.")
        else:
            strengths.append(f"Contains strong action verbs: {', '.join(found_verbs[:3])}")

        # 4. Career Objective Quality (Generic vs Specific value proposition)
        generic_phrases = ["seeking an entry level position", "looking to utilize my skills", "obtain a challenging role"]
        if any(phrase in summary.lower() for phrase in generic_phrases):
            score -= 15.0
            weaknesses.append("Summary includes generic objective phrases.")
            recommendations.append("Focus on what value you bring to the employer rather than just stating what you want from them.")
        else:
            strengths.append("Objective focused on value-add and professional achievements.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Professional Summary",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
