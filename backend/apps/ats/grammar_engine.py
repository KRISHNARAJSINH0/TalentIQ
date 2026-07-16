import re
from apps.ats.services import COMMON_TYPOS

class GrammarEngine:
    """
    Evaluates readability, sentence lengths, grammar, typos, tone, and conciseness.
    """

    @staticmethod
    def analyze_grammar(profile, related_data: dict) -> dict:
        summary = profile.summary or ""
        experiences_text = " ".join([exp.description or "" for exp in related_data.get("experiences", [])])
        projects_text = " ".join([proj.description or "" for proj in related_data.get("projects", [])])
        
        full_text = f"{summary} {experiences_text} {projects_text}".strip()
        
        if not full_text:
            return {
                "grammar_score": 100.0,
                "readability_score": 100.0,
                "spelling_errors": [],
                "long_sentences_count": 0,
                "passive_voice_count": 0,
                "first_person_pronouns_count": 0
            }

        # 1. Spelling typos checking
        found_typos = []
        for typo, correction in COMMON_TYPOS.items():
            if re.search(r'\b' + re.escape(typo) + r'\b', full_text.lower()):
                found_typos.append({"typo": typo, "correction": correction})

        # Grammar Score: base 100, penalize for typos
        grammar_score = 100.0 - (len(found_typos) * 10.0)
        grammar_score = max(30.0, grammar_score)

        # 2. Readability & professional tone (lack of "I", "my", "me", "we", "our" in professional experience)
        pronouns_pattern = r'\b(i|my|me|we|our|us)\b'
        pronouns_matches = re.findall(pronouns_pattern, experiences_text.lower())
        pronouns_count = len(pronouns_matches)

        # Sentence lengths: count run-on sentences (> 25 words)
        sentences = re.split(r'[.!?]+', full_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        long_sentences = 0
        total_words = 0
        for s in sentences:
            w_count = len(s.split())
            total_words += w_count
            if w_count > 25:
                long_sentences += 1

        # Readability score computation
        readability_score = 100.0
        # Penalize for first-person pronouns in experience
        readability_score -= pronouns_count * 5.0
        # Penalize for run-on sentences
        if len(sentences) > 0:
            long_sentence_ratio = long_sentences / len(sentences)
            readability_score -= long_sentence_ratio * 40.0
        
        # Adjust for summary length
        summary_word_count = len(summary.split())
        if summary_word_count > 0 and (summary_word_count < 30 or summary_word_count > 200):
            readability_score -= 10.0

        readability_score = max(20.0, min(100.0, readability_score))

        # Check passive voice count
        passive_matches = re.findall(r'\b(was|were|been|being|is|are|am|be)\b\s+([a-zA-Z]+ed|done|made|built|run|written|held)\b', full_text.lower())
        passive_count = len(passive_matches)

        return {
            "grammar_score": round(grammar_score, 2),
            "readability_score": round(readability_score, 2),
            "spelling_errors": found_typos,
            "long_sentences_count": long_sentences,
            "passive_voice_count": passive_count,
            "first_person_pronouns_count": pronouns_count
        }
