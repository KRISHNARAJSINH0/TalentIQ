import re
from apps.ats.services import COMMON_TYPOS

class GrammarEngine:
    """
    Evaluates grammar, spelling, typos, sentence quality, and readability.
    """

    @staticmethod
    def analyze_grammar(profile, resume) -> dict:
        # Check if called as legacy/backward-compatible mode
        if isinstance(resume, dict):
            return {
                "grammar_score": 85.0,
                "readability_score": 85.0
            }

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
                "category": "Grammar",
                "score": 100.0,
                "strengths": ["No grammar issues found in empty profile."],
                "weaknesses": [],
                "recommendations": [],
                "confidence": 95
            }

        # 1. Typos checking
        found_typos = []
        for typo, correction in COMMON_TYPOS.items():
            if re.search(r'\b' + re.escape(typo) + r'\b', full_text_lower):
                found_typos.append(typo)

        if found_typos:
            score -= len(found_typos) * 10.0
            weaknesses.append(f"Spelling/typo errors found: {', '.join(found_typos[:4])}.")
            recommendations.append("Proofread your resume and fix spelling errors/typos.")
        else:
            strengths.append("No common spelling typos detected.")

        # 2. Capitalization check (first letter of sentences)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        uncapitalized = 0
        for s in sentences:
            # check if first letter is lowercase
            first_char = re.sub(r'[^a-zA-Z]', '', s)
            if first_char and first_char[0].islower():
                uncapitalized += 1

        if uncapitalized > 0:
            score -= min(15.0, uncapitalized * 5.0)
            weaknesses.append(f"Sentence capitalization issues detected ({uncapitalized} instances).")
            recommendations.append("Ensure every sentence starts with a capital letter.")
        else:
            strengths.append("Sentence capitalization is correct.")

        # 3. Passive voice check
        passive_matches = re.findall(r'\b(was|were|been|being|is|are|am|be)\b\s+([a-zA-Z]+ed|done|made|built|run|written|held)\b', full_text_lower)
        if len(passive_matches) > 3:
            score -= 10.0
            weaknesses.append("High usage of passive voice detected.")
            recommendations.append("Rephrase passive sentences to active statements (e.g. 'Reduced load' instead of 'Load was reduced by').")

        score = max(0.0, min(100.0, score))
        confidence = 95

        return {
            "category": "Grammar",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }

    @staticmethod
    def analyze_readability(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        summary_text = profile.summary or ""
        experiences_text = " ".join([getattr(exp, 'description', '') or "" for exp in (profile.experiences.all() if hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all') else [])])
        projects_text = " ".join([getattr(proj, 'description', '') or "" for proj in (profile.projects.all() if hasattr(profile, 'projects') and hasattr(profile.projects, 'all') else [])])
        
        full_text = f"{summary_text} {experiences_text} {projects_text}".strip()

        if not full_text:
            return {
                "category": "Readability",
                "score": 100.0,
                "strengths": ["Empty profile is readable."],
                "weaknesses": [],
                "recommendations": [],
                "confidence": 95
            }

        # 1. Sentence lengths & run-on sentences (> 25 words)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        long_sentences = 0
        for s in sentences:
            if len(s.split()) > 25:
                long_sentences += 1

        if sentences:
            long_sentence_ratio = long_sentences / len(sentences)
            if long_sentence_ratio > 0.2:
                score -= 20.0
                weaknesses.append("Contains several long or run-on sentences (>25 words).")
                recommendations.append("Break down complex sentences into shorter, punchy bullet points (15-20 words).")
            else:
                strengths.append("Sentence lengths are punchy and highly readable.")

        # 2. Pronouns (First person) in Experience
        pronouns = re.findall(r"\b(i|me|my|we|our|us)\b", experiences_text.lower())
        if pronouns:
            score -= min(25.0, len(pronouns) * 5.0)
            weaknesses.append("First-person pronouns detected in your experience description.")
            recommendations.append("Remove personal pronouns (e.g. 'I led', 'my team') to maintain professional distance.")
        else:
            strengths.append("No personal pronouns used in professional work history.")

        # 3. Flesch Kincaid grade level proxy
        # Count words and syllables (rough estimate: count vowels)
        words = re.findall(r'\b[a-zA-Z]+\b', full_text.lower())
        total_words = len(words)
        total_sentences = len(sentences) or 1
        
        def count_syllables(word):
            word = word.lower()
            count = 0
            vowels = "aeiouy"
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count += 1
            return count

        total_syllables = sum(count_syllables(w) for w in words)
        
        # Flesch Reading Ease Formula: 206.835 - 1.015 * (total_words/total_sentences) - 84.6 * (total_syllables/total_words)
        if total_words > 0:
            fre = 206.835 - 1.015 * (total_words / total_sentences) - 84.6 * (total_syllables / total_words)
            if fre < 30:
                score -= 15.0
                weaknesses.append("Text is written at an extremely academic/complex level.")
                recommendations.append("Simplify your language so that it reads easily for HR generalists.")
            elif fre > 90:
                score -= 10.0
                weaknesses.append("Text readability level is very basic.")
                recommendations.append("Use more professional and descriptive terminology.")
            else:
                strengths.append("Professional readability score matches business/industry standards.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Readability",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }


