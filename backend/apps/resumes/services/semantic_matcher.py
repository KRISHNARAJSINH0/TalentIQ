import math
import re
import logging
from collections import Counter
from typing import Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class SemanticMatcher:
    """
    Computes semantic similarity, vector cosine similarity, string distance,
    and N-gram overlap between extracted resume entities and target category ontologies.
    """

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        """Tokenizes text into normalized lowercase alphanumeric tokens."""
        if not text:
            return []
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9\+#\.]+\b", text) if len(w) > 1]

    @staticmethod
    def _text_to_vector(text: str) -> Counter:
        """Converts string into word count frequency vector."""
        tokens = SemanticMatcher._tokenize(text)
        return Counter(tokens)

    @classmethod
    def cosine_similarity(cls, text1: str, text2: str) -> float:
        """
        Calculates Cosine Similarity (0.0 to 1.0) between two text strings using token frequency vectors.
        """
        vec1 = cls._text_to_vector(text1)
        vec2 = cls._text_to_vector(text2)

        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        return float(numerator) / denominator

    @classmethod
    def token_overlap_score(cls, text: str, target_list: List[str]) -> float:
        """
        Calculates token overlap score (0.0 to 100.0) against a list of target phrases.
        """
        if not text or not target_list:
            return 0.0

        text_tokens = set(cls._tokenize(text))
        if not text_tokens:
            return 0.0

        max_overlap = 0.0
        for target in target_list:
            target_tokens = set(cls._tokenize(target))
            if not target_tokens:
                continue

            overlap = len(text_tokens & target_tokens)
            score = (overlap / float(len(text_tokens | target_tokens))) * 100.0
            if score > max_overlap:
                max_overlap = score

        return min(100.0, max_overlap)

    @classmethod
    def lev_distance(cls, s1: str, s2: str) -> int:
        """Computes Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return cls.lev_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]

    @classmethod
    def string_similarity(cls, s1: str, s2: str) -> float:
        """Calculates normalized string similarity ratio (0.0 to 100.0)."""
        if not s1 or not s2:
            return 0.0
        s1_clean, s2_clean = s1.strip().lower(), s2.strip().lower()
        if s1_clean == s2_clean:
            return 100.0

        distance = cls.lev_distance(s1_clean, s2_clean)
        max_len = max(len(s1_clean), len(s2_clean))
        if max_len == 0:
            return 100.0
        return (1.0 - (distance / float(max_len))) * 100.0

    @classmethod
    def match_against_category(cls, value: str, entities: List[str], keywords: List[str]) -> float:
        """
        Computes combined semantic match score (0.0 to 100.0) of a value against category vocabulary.
        """
        if not value:
            return 0.0

        val_clean = value.strip().lower()

        # 1. Exact match boost
        if any(val_clean == e.lower() for e in entities):
            return 100.0

        # 2. Substring / Keyword match
        for kw in keywords:
            if kw.lower() in val_clean:
                return 95.0

        # 3. Token overlap similarity
        overlap_score = cls.token_overlap_score(value, entities)
        if overlap_score > 70.0:
            return overlap_score

        # 4. Best string similarity
        best_sim = 0.0
        for ent in entities[:100]: # Check top candidates
            sim = cls.string_similarity(val_clean, ent)
            if sim > best_sim:
                best_sim = sim

        return best_sim
