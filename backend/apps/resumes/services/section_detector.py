import re
import json
import logging
from django.conf import settings
from django.utils import timezone
from ..models import Resume, ResumeSection
from ..ai_service import GeminiService

logger = logging.getLogger(__name__)


class SectionNormalizer:
    """
    Normalizes arbitrary section titles into canonical target sections.
    """
    CANONICAL_SECTIONS = {
        "personal_info": "Personal Information",
        "summary": "Summary",
        "skills": "Skills",
        "experience": "Experience",
        "projects": "Projects",
        "education": "Education",
        "certifications": "Certifications",
        "publications": "Publications",
        "volunteer": "Volunteer Experience",
        "social": "Social Links",
        "references": "References",
        "hobbies": "Hobbies & Interests"
    }

    # Keyword mappings (lower case) for direct lookup
    KEYWORDS_MAPPING = {
        "education": ["education", "academic", "qualification", "degree", "bachelor", "master", "college", "university", "school", "cgpa", "gpa", "btech", "be", "mtech", "msc", "mba", "academic background", "academic qualifications", "educational background", "credentials"],
        "skills": ["skills", "technical skills", "technologies", "stack", "tools", "frameworks", "competencies", "abilities", "expertise", "soft skills", "programming languages", "core competencies", "technical proficiency", "capabilities", "what i know", "technological stack"],
        "experience": ["experience", "employment", "career", "professional experience", "work history", "industry experience", "internship", "employment history", "work experience", "job history", "professional background", "where i worked", "my journey", "professional timeline"],
        "projects": ["projects", "project experience", "case studies", "works", "developments", "applications", "research projects", "personal projects", "academic projects", "key projects", "things i built", "selected projects"],
        "certifications": ["certifications", "licenses", "training", "courses", "achievements", "awards", "honors", "licenses & certifications", "certifications & licenses", "accomplishments", "accreditations"],
        "publications": ["research", "papers", "journals", "publications", "thesis", "patents", "publications & research", "articles", "scientific papers"],
        "volunteer": ["volunteer experience", "activities", "leadership", "volunteer", "volunteering", "community service", "extracurricular activities", "extracurriculars", "community involvement"],
        "social": ["github", "linkedin", "portfolio", "website", "blog", "twitter", "social", "links", "social links", "find me on", "online presence"],
        "summary": ["personal information", "contact information", "about", "contact", "profile", "summary", "objective", "professional summary", "about me", "executive summary", "career objective", "personal statement", "who i am", "get in touch"],
        "references": ["references", "referees", "recommendations"],
        "hobbies": ["interests", "hobbies", "personal interests", "pastimes", "leisure activities"]
    }

    @classmethod
    def normalize(cls, title: str) -> str:
        """
        Normalizes a title string. Returns a key representing one of the canonical section types.
        """
        if not title:
            return "summary"
            
        clean_title = title.lower().strip()
        # Direct clean string check
        for canonical, keywords in cls.KEYWORDS_MAPPING.items():
            if clean_title in keywords:
                return canonical

        # Substring/contains check
        for canonical, keywords in cls.KEYWORDS_MAPPING.items():
            for keyword in keywords:
                # Match boundaries or exact substrings for standard keywords
                if len(keyword) > 3 and keyword in clean_title:
                    return canonical

        return "summary"  # Default fallback


class LayoutDetector:
    """
    Detects the visual and structural layout of the resume text.
    """
    @staticmethod
    def detect_heuristically(text: str) -> str:
        """
        Analyses text structures, columns, list patterns, and returns a layout classification.
        """
        if not text or not text.strip():
            return "single_column"

        lines = text.split("\n")
        total_lines = len(lines)
        
        # Check for column indicators (e.g. multiple tabs or spacing gaps, or pipe '|' characters)
        pipe_count = text.count("|")
        two_column_markers = 0
        long_line_count = 0
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
                
            # If line has vertical column separators
            if pipe_count > 5:
                two_column_markers += 1
                
            # If line has side-by-side elements separated by double spaces
            if re.search(r'\s{4,}[a-zA-Z0-9]', line_str):
                two_column_markers += 1
                
            if len(line_str) > 80:
                long_line_count += 1

        # Check for academic keywords
        academic_keywords = ["publications", "journals", "conference", "research", "teaching experience", "thesis", "patent", "academic experience"]
        academic_score = sum(1 for kw in academic_keywords if kw in text.lower())

        if total_lines > 150:
            return "multi_page_layout"
        elif academic_score >= 3:
            return "academic_layout"
        elif pipe_count >= 4:
            return "table_layout"
        elif two_column_markers > total_lines * 0.15:
            # High proportion of column signs or large spacing splits
            return "two_column"
        else:
            return "single_column"


class BlockDetector:
    """
    Splits raw text into candidate sections based on detected headers.
    """
    # Regex matching lines that look like section titles
    HEADER_REGEX = re.compile(
        r'^(?:[A-Z][A-Z\s&/,\-]{2,30}|[a-zA-Z\s&/,\-]{3,35})(?::)?$',
        re.MULTILINE
    )

    @classmethod
    def segment_text(cls, text: str) -> list:
        """
        Splits resume text into raw blocks using standard headers.
        Returns a list of dicts: {"title": str, "content": str, "start_line": int}
        """
        if not text or not text.strip():
            return []

        lines = text.split("\n")
        blocks = []
        current_block = {"title": "Header / Contact Info", "content": [], "start_line": 1}
        
        # Build common keywords pattern for regex validation
        flat_keywords = []
        for kw_list in SectionNormalizer.KEYWORDS_MAPPING.values():
            flat_keywords.extend(kw_list)
        # Unique list
        flat_keywords = sorted(list(set(flat_keywords)), key=len, reverse=True)
        keyword_pattern = re.compile(
            r'\b(?:' + '|'.join(re.escape(kw) for kw in flat_keywords) + r')\b',
            re.IGNORECASE
        )

        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue

            # Check if this line is likely a section header
            # Rule: Line is relatively short, matches header format, and contains section keywords
            is_header = (
                len(stripped) < 35 
                and cls.HEADER_REGEX.match(stripped)
                and keyword_pattern.search(stripped)
            )

            if is_header:
                # Save previous block
                if current_block["content"]:
                    current_block["content"] = "\n".join(current_block["content"]).strip()
                    blocks.append(current_block)
                
                # Start new block
                current_block = {"title": stripped, "content": [], "start_line": idx}
            else:
                current_block["content"].append(line)

        # Append last block
        if current_block["content"]:
            if isinstance(current_block["content"], list):
                current_block["content"] = "\n".join(current_block["content"]).strip()
            blocks.append(current_block)

        return blocks


class SectionClassifier:
    """
    Classifies a text block and computes a confidence score.
    """
    @classmethod
    def classify_block(cls, title: str, content: str) -> tuple:
        """
        Evaluates a block of text. Returns (normalized_type, confidence_score).
        """
        normalized_type = SectionNormalizer.normalize(title)
        
        if not title or title.lower().startswith("header"):
            return "summary", 85.0

        # Heuristic confidence calculation
        # If title matches canonical keywords directly, confidence is high
        clean_title = title.lower().strip()
        keywords = SectionNormalizer.KEYWORDS_MAPPING.get(normalized_type, [])
        
        confidence = 60.0  # Base confidence
        
        if clean_title in keywords:
            confidence = 98.0
        elif any(kw in clean_title for kw in keywords if len(kw) > 3):
            confidence = 90.0

        # Check content relevance
        # e.g., if it's classified as education, check if it contains degree keywords or institutions
        degree_words = ["bachelor", "master", "phd", "university", "college", "school", "degree", "gpa", "study"]
        experience_words = ["worked", "managed", "developed", "led", "company", "team", "engineer", "designer", "officer"]
        skills_words = ["python", "javascript", "sql", "excel", "management", "communication", "aws", "git"]
        
        content_lower = content.lower()
        
        if normalized_type == "education" and any(dw in content_lower for dw in degree_words):
            confidence = min(confidence + 10.0, 100.0)
        elif normalized_type == "experience" and any(ew in content_lower for ew in experience_words):
            confidence = min(confidence + 10.0, 100.0)
        elif normalized_type == "skills" and any(sw in content_lower for sw in skills_words):
            confidence = min(confidence + 10.0, 100.0)

        return normalized_type, round(confidence, 1)


class SectionDetector:
    """
    Main coordinator service for layout analysis, block boundary parsing,
    and hybrid category matching (AI/Gemini + spaCy + Regex).
    """
    def __init__(self):
        self.gemini_service = GeminiService()

    def detect_sections(self, text: str) -> dict:
        """
        Performs structural layout analysis and segment classification.
        First tries Gemini AI for semantic matching, falling back to rule-based parser on error.
        """
        if not text or not text.strip():
            return {
                "layout": "single_column",
                "sections": []
            }

        # Try to use Gemini AI first
        ai_success, result = self._detect_with_ai(text)
        if ai_success:
            return result

        # Fallback to local rule-based parsing
        logger.warning("Gemini section detection failed or not configured. Falling back to rule-based detection.")
        return self._detect_heuristically(text)

    def _detect_with_ai(self, text: str) -> tuple:
        """
        Sends the text to Gemini requesting structured layout & boundaries.
        Returns (success, result_dict).
        """
        self.gemini_service.initialize_client()
        if self.gemini_service.use_mock:
            return False, {}

        prompt = f"""
You are a Principal Document AI Architect. Your task is to analyze the layout and segment the sections of the following resume text.

Return a JSON object conforming exactly to this schema:
{{
  "layout": "single_column | two_column | sidebar_layout | table_layout | mixed_layout | academic_layout | graphic_layout",
  "sections": [
    {{
      "type": "personal_info | summary | skills | experience | projects | education | certifications | publications | volunteer | social | references | hobbies",
      "title": "Original Section Title in text (or 'Personal Information' if contact details header)",
      "content": "Cleaned raw content of the section...",
      "confidence": 95,
      "page": 1
    }}
  ]
}}

RULES:
1. Target Section Types:
   - "personal_info" (for Name, Email, Phone, Address, Location, GitHub, LinkedIn, Contact Details)
   - "summary" (for Summary, Objective, Career Objective)
   - "skills" (for Core skills, Tech Stack, Tools, Competencies)
   - "experience" (for Work History, Professional Experience, Internships)
   - "projects" (for Personal projects, Academic projects, Things built)
   - "education" (for Degrees, University, Academic background)
   - "certifications" (for Licenses, Certificates, Courses)
   - "publications" (for Research, Patents, Scientific Papers, Thesis)
   - "volunteer" (for Volunteer work, Extracurricular activities, Leadership roles)
   - "social" (for GitHub, LinkedIn, Portfolio Links)
   - "references" (for Professional references)
   - "hobbies" (for Hobbies, Personal interests)
2. Handle two-column/sidebar layout: Correctly reconstruct text blocks in sequential flow.
3. Compute a confidence score (integer 0-100) based on title match and content relevance.
4. Keep the original text structure and content as intact as possible. Do not invent details.

RESUME TEXT:
\"\"\"
{text}
\"\"\"
"""
        try:
            raw_response = self.gemini_service.generate_content(prompt)
            # Clean markdown backticks if any
            clean_response = raw_response.strip()
            if clean_response.startswith("```"):
                lines = clean_response.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_response = "\n".join(lines).strip()
            
            parsed = json.loads(clean_response)
            
            # Validation of output keys
            if "layout" in parsed and "sections" in parsed:
                # Ensure each section has confidence and correct type
                valid_sections = []
                for sec in parsed["sections"]:
                    if not sec.get("type") or not sec.get("title") or not sec.get("content"):
                        continue
                    # Normalize section type key just in case AI returned slightly different text
                    sec["type"] = SectionNormalizer.normalize(sec["type"])
                    if "confidence" not in sec:
                        sec["confidence"] = 90
                    if "page" not in sec:
                        sec["page"] = 1
                    valid_sections.append(sec)
                
                parsed["sections"] = valid_sections
                return True, parsed
                
        except Exception as e:
            logger.error(f"Failed semantic parsing with Gemini: {str(e)}", exc_info=True)
            
        return False, {}

    def _detect_heuristically(self, text: str) -> dict:
        """
        Local rule-based fallback algorithm.
        """
        layout = LayoutDetector.detect_heuristically(text)
        raw_blocks = BlockDetector.segment_text(text)
        
        sections = []
        for idx, block in enumerate(raw_blocks, 1):
            normalized_type, confidence = SectionClassifier.classify_block(
                block["title"],
                block["content"]
            )
            
            sections.append({
                "type": normalized_type,
                "title": block["title"],
                "content": block["content"],
                "confidence": confidence,
                "page": 1
            })

        return {
            "layout": layout,
            "sections": sections
        }

    def detect_and_save(self, resume: Resume) -> dict:
        """
        Detects sections for a Resume instance and saves them into the ResumeSection database model.
        Deletes any previously saved sections for this resume.
        """
        # Ensure text is extracted
        if not resume.extracted_text or resume.extraction_status != Resume.ExtractionStatus.COMPLETED:
            from .services import ResumeExtractionService
            extractor = ResumeExtractionService()
            extractor.extract_resume_text(resume)
            resume.refresh_from_db()

        text = resume.extracted_text
        result = self.detect_sections(text)

        # Transactionally clear existing sections and write new ones
        ResumeSection.objects.filter(resume=resume).delete()
        
        for idx, sec in enumerate(result.get("sections", [])):
            ResumeSection.objects.create(
                resume=resume,
                section_type=sec["type"],
                title=sec["title"],
                confidence=sec["confidence"],
                position=idx,
                page=sec.get("page", 1),
                content=sec["content"]
            )
            
        return result
