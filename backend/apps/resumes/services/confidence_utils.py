import re

class AgreementCalculator:
    """
    Computes agreement level between different extraction engines (Regex, spaCy, Gemini).
    """

    @classmethod
    def calculate_agreement(cls, field_name: str, value: str, regex_data: dict, spacy_data: dict, gemini_data: dict) -> tuple[float, list[str]]:
        """
        Compares values across sources.
        Returns (boost_or_override, list_of_matching_sources).
        """
        if not value:
            return 0.0, []

        regex_data = regex_data or {}
        spacy_data = spacy_data or {}
        gemini_data = gemini_data or {}

        val_clean = str(value).strip().lower()
        matching_sources = []

        # Find which sources contain the value
        # 1. Regex
        regex_val = regex_data.get(field_name)
        if regex_val:
            if isinstance(regex_val, list):
                if any(str(item).strip().lower() == val_clean for item in regex_val):
                    matching_sources.append("regex")
            elif str(regex_val).strip().lower() == val_clean:
                matching_sources.append("regex")

        # 2. spaCy
        spacy_val = spacy_data.get(field_name)
        if spacy_val:
            if isinstance(spacy_val, list):
                if any(str(item).strip().lower() == val_clean for item in spacy_val):
                    matching_sources.append("spacy")
            elif str(spacy_val).strip().lower() == val_clean:
                matching_sources.append("spacy")

        # 3. Gemini
        gemini_val = gemini_data.get(field_name)
        if gemini_val:
            if isinstance(gemini_val, list):
                if any(str(item).strip().lower() == val_clean for item in gemini_val):
                    matching_sources.append("gemini")
            elif str(gemini_val).strip().lower() == val_clean:
                matching_sources.append("gemini")

        # Fallback keyword checks if exact checks didn't trigger
        # For instance, if checking name and it was extracted by spaCy and Gemini
        if field_name == "name":
            # spaCy and Gemini check
            if spacy_data.get("name") and gemini_data.get("name"):
                s_name = str(spacy_data["name"]).strip().lower()
                g_name = str(gemini_data["name"]).strip().lower()
                if s_name == g_name or s_name in g_name or g_name in s_name:
                    if "spacy" not in matching_sources: matching_sources.append("spacy")
                    if "gemini" not in matching_sources: matching_sources.append("gemini")

        # De-duplicate matching sources list
        matching_sources = list(set(matching_sources))

        # Agreement calculations
        if len(matching_sources) >= 3:
            # Full agreement override (Regex + spaCy + Gemini)
            return 100.0, matching_sources
        elif len(matching_sources) == 2:
            # Partial agreement boost
            return 5.0, matching_sources

        return 0.0, matching_sources


class ContextAnalyzer:
    """
    Analyzes spatial and contextual position of entities in the resume.
    """

    @classmethod
    def is_in_header(cls, value: str, raw_text: str) -> bool:
        """
        Determines if the value occurs within the top 15% lines of the raw text.
        """
        if not value or not raw_text:
            return False

        lines = raw_text.split("\n")
        total_lines = len(lines)
        if total_lines == 0:
            return False

        # Header limit
        header_limit = max(1, int(total_lines * 0.15))
        header_text = "\n".join(lines[:header_limit]).lower()
        
        return str(value).strip().lower() in header_text

    @classmethod
    def is_in_section(cls, value: str, section_type: str, sections_qs) -> bool:
        """
        Determines if the value is contained inside a specific detected ResumeSection.
        """
        if not value or not section_type or not sections_qs:
            return False

        val_clean = str(value).strip().lower()
        
        # Look for section matches
        matching_sections = sections_qs.filter(section_type=section_type)
        for sec in matching_sections:
            if val_clean in sec.content.lower():
                return True
        return False
