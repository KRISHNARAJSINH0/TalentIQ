"""
Keyword Engine — Extracts, weights, and matches keywords from JD against resume.

Performs TF-based ranking, action verb detection, and keyword-to-section mapping.
"""

import re
import logging
from collections import Counter

logger = logging.getLogger(__name__)

# Common stop words to exclude
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "not", "no", "nor", "so", "if", "then", "than", "too", "very",
    "just", "about", "above", "after", "again", "all", "also", "am",
    "any", "because", "before", "between", "both", "during", "each",
    "few", "further", "get", "got", "he", "her", "here", "him", "his",
    "how", "i", "into", "it", "its", "let", "me", "more", "most", "my",
    "new", "now", "only", "other", "our", "out", "over", "own", "re",
    "s", "same", "she", "some", "such", "t", "that", "their", "them",
    "there", "these", "they", "this", "those", "through", "up", "us",
    "we", "what", "when", "where", "which", "while", "who", "whom",
    "why", "you", "your", "able", "across", "etc", "per", "via",
    "well", "work", "working", "using", "role", "team", "join",
    "company", "looking", "experience", "years", "strong", "ability",
    "including", "within", "ensure", "help", "make", "provide",
}

# Action verbs relevant to JDs
ACTION_VERBS = {
    "design", "develop", "build", "implement", "create", "architect",
    "optimize", "deploy", "manage", "lead", "collaborate", "analyze",
    "maintain", "test", "debug", "review", "mentor", "scale",
    "automate", "integrate", "deliver", "monitor", "troubleshoot",
    "configure", "migrate", "refactor", "document", "research",
    "evaluate", "coordinate", "communicate", "support", "contribute",
}


class KeywordEngine:
    """
    Extract and match keywords from JD text against the user's resume content.
    """

    def analyze(self, jd_content: str, profile_data: dict) -> dict:
        """
        Returns keyword_match percentage and detailed keyword analysis.
        """
        jd_keywords = self._extract_keywords(jd_content)
        resume_text = self._build_resume_text(profile_data)
        resume_lower = resume_text.lower()

        # Match keywords
        matched = []
        unmatched = []
        for kw, count in jd_keywords:
            if kw in resume_lower:
                matched.append({"keyword": kw, "frequency": count})
            else:
                unmatched.append({"keyword": kw, "frequency": count})

        total = len(jd_keywords)
        match_count = len(matched)

        keyword_match = round((match_count / total) * 100) if total > 0 else 80

        # Extract action verbs from JD
        jd_lower = jd_content.lower()
        found_verbs = [v for v in ACTION_VERBS if v in jd_lower]

        return {
            "keyword_match": min(keyword_match, 100),
            "total_keywords": total,
            "matched_count": match_count,
            "matched_keywords": matched[:20],
            "unmatched_keywords": unmatched[:15],
            "action_verbs": sorted(found_verbs),
        }

    def _extract_keywords(self, text: str) -> list:
        """Extract significant keywords via term frequency."""
        # Tokenize
        words = re.findall(r"[a-z][a-z0-9\+\#\.]+", text.lower())

        # Filter stop words and very short tokens
        filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]

        # Count frequencies
        counter = Counter(filtered)

        # Return top keywords sorted by frequency
        return counter.most_common(40)

    def _build_resume_text(self, profile_data: dict) -> str:
        """Build a searchable text blob from the user's profile data."""
        parts = []

        parts.append(profile_data.get("headline", ""))
        parts.append(profile_data.get("summary", ""))

        for skill in profile_data.get("skills", []):
            parts.append(skill.get("skill_name", ""))

        for exp in profile_data.get("experiences", []):
            parts.append(exp.get("designation", ""))
            parts.append(exp.get("company", ""))
            parts.append(exp.get("description", ""))

        for edu in profile_data.get("educations", []):
            parts.append(edu.get("degree", ""))
            parts.append(edu.get("field_of_study", ""))
            parts.append(edu.get("institute", ""))

        for proj in profile_data.get("projects", []):
            parts.append(proj.get("project_name", ""))
            parts.append(proj.get("technologies", ""))
            parts.append(proj.get("description", ""))

        for cert in profile_data.get("certifications", []):
            parts.append(cert.get("name", ""))

        return " ".join(filter(None, parts))
