from typing import Optional
import re
import time
import logging
from django.utils import timezone
from .models import Resume

logger = logging.getLogger(__name__)


class SpacyExtractionService:
    """
    Service to perform NLP-based entity extraction (Person Name, Organizations,
    Locations, Dates, Education Entities, Skills, and Job Titles) using spaCy.
    """
    _nlp = None

    @classmethod
    def get_nlp(cls):
        """Loads and returns the spaCy NLP model, loading it only once."""
        if cls._nlp is None:
            # pyrefly: ignore [import-not-found, missing-import]
            import spacy
            models_to_try = ["en_core_web_lg", "en_core_web_md", "en_core_web_sm"]
            for model in models_to_try:
                try:
                    logger.info(f"Attempting to load spaCy model: {model}")
                    cls._nlp = spacy.load(model)
                    logger.info(f"Successfully loaded spaCy model: {model}")
                    break
                except OSError:
                    logger.warning(f"spaCy model {model} not found/loaded.")
            
            if cls._nlp is None:
                logger.info("Attempting automatic programmatic download of fallback model: en_core_web_sm...")
                try:
                    # pyrefly: ignore [import-not-found, missing-import]
                    import spacy.cli
                    spacy.cli.download("en_core_web_sm")
                    cls._nlp = spacy.load("en_core_web_sm")
                    logger.info("Successfully downloaded and loaded fallback model: en_core_web_sm")
                except Exception as download_err:
                    logger.error(f"Failed to programmatically download fallback model: {str(download_err)}")
                    raise RuntimeError("No spaCy model could be loaded and automatic download failed.")
        return cls._nlp

    def extract_and_save(self, resume: Resume) -> bool:
        """
        Runs spaCy NLP analysis on the resume's extracted_text, updates the
        model fields, and returns True on success, False on failure.
        """
        start_time = time.time()
        resume.spacy_status = Resume.SpacyStatus.PROCESSING
        resume.save(update_fields=["spacy_status"])

        logger.info(f"Starting spaCy NLP analysis for resume: {resume.id}")

        text = resume.extracted_text
        if not text or not text.strip():
            logger.warning(f"No extracted text found for resume: {resume.id}")
            self._handle_failure(resume, "No text content available for analysis.", start_time)
            return False

        try:
            # Check length safety (capping at 500k characters to prevent high memory usage)
            if len(text) > 500000:
                logger.warning(f"Extremely large text content for resume: {resume.id}")
                text = text[:500000]

            extracted_data = self.analyze_text(text)

            duration = time.time() - start_time
            resume.spacy_json = extracted_data
            resume.spacy_status = Resume.SpacyStatus.COMPLETED
            resume.spacy_completed_at = timezone.now()
            resume.spacy_processing_time = round(duration, 4)
            resume.save(
                update_fields=[
                    "spacy_json",
                    "spacy_status",
                    "spacy_completed_at",
                    "spacy_processing_time"
                ]
            )

            logger.info(f"Successfully completed spaCy NLP analysis for resume {resume.id} in {duration:.4f}s")
            return True

        except Exception as e:
            logger.error(f"spaCy NLP extraction failed for resume {resume.id}: {str(e)}", exc_info=True)
            self._handle_failure(resume, f"Extraction failed: {str(e)}", start_time)
            return False

    def analyze_text(self, text: str) -> dict:
        """
        Parses text and extracts all entities, returning a structured dictionary.
        """
        nlp = self.get_nlp()
        doc = nlp(text)

        # 1. Person Name Extraction (Combining Header Line Heuristics & spaCy NER)
        header_name = self._extract_header_name(text)

        person_candidates = []
        name_regex = re.compile(r'^[a-zA-Z\.\s\'-]{3,40}$')
        invalid_name_words = {
            "curriculum", "vitae", "resume", "profile", "summary", "objective",
            "education", "experience", "skills", "projects", "certifications",
            "languages", "hobbies", "contact", "details", "phone", "email",
            "address", "engineering", "basics", "aspirant", "internship",
            "page", "software", "developer", "engineer", "manager", "university",
            "college", "school", "institute"
        }

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                cleaned = ent.text.strip().replace("\n", " ")
                cleaned = " ".join(cleaned.split())
                if cleaned and name_regex.match(cleaned):
                    words = cleaned.split()
                    if 2 <= len(words) <= 4:
                        lower_words = [w.lower() for w in words]
                        if not any(w in invalid_name_words for w in lower_words) and not self._is_blacklisted(cleaned):
                            person_candidates.append(cleaned.title())

        primary_name = header_name or (person_candidates[0] if person_candidates else None)
        if not primary_name:
            raw_persons = [ent.text.strip().replace("\n", " ") for ent in doc.ents if ent.label_ == "PERSON"]
            raw_persons = [" ".join(p.split()) for p in raw_persons if p.strip()]
            for p in raw_persons:
                p_words = [w.lower() for w in p.split()]
                if not any(w in invalid_name_words for w in p_words) and not self._is_blacklisted(p):
                    primary_name = p.title()
                    break

        # 2. Organizations (with enhanced filtering)
        organizations = []
        for ent in doc.ents:
            if ent.label_ == "ORG":
                cleaned = ent.text.strip().replace("\n", " ")
                cleaned = re.sub(r'^[^\w]+', '', cleaned).strip()
                cleaned = " ".join(cleaned.split())
                if cleaned and len(cleaned) > 2 and not self._is_blacklisted(cleaned):
                    # Additional filters to prevent skills/tech from leaking
                    if not self._is_skill_like(cleaned):
                        if not self._is_action_verb(cleaned):
                            if not self._is_noisy_org(cleaned):
                                organizations.append(cleaned)
        organizations = self._clean_duplicates(organizations)

        # 3. Locations
        locations = []
        for ent in doc.ents:
            if ent.label_ in ("GPE", "LOC"):
                cleaned = ent.text.strip().replace("\n", " ")
                cleaned = " ".join(cleaned.split())
                # Normalize capitalization
                cleaned = cleaned.title()
                if cleaned and len(cleaned) > 1 and not self._is_blacklisted(cleaned):
                    if not self._is_skill_like(cleaned):
                        locations.append(cleaned)
        locations = self._clean_duplicates(locations)

        # 4. Dates (with improved filtering)
        dates = []
        phone_pattern = re.compile(r'^\+?\d[\d\s\-]{7,15}$')
        noise_date_words = {
            "weekly", "monthly", "daily", "yearly", "annually", "hourly",
            "today", "tomorrow", "yesterday", "now", "ago", "current",
            "recently", "present", "ongoing", "till date", "to date"
        }
        for ent in doc.ents:
            if ent.label_ == "DATE":
                cleaned = ent.text.strip().replace("\n", " ")
                cleaned = " ".join(cleaned.split())
                if cleaned and len(cleaned) > 2:
                    # Filter out phone numbers
                    if phone_pattern.match(cleaned):
                        continue
                    # Filter out single noise words
                    if cleaned.lower().strip() in noise_date_words:
                        continue
                    # Filter out pure numbers that look like phone/ID numbers
                    digits_only = re.sub(r'[\s\-\+]', '', cleaned)
                    if digits_only.isdigit() and len(digits_only) > 6:
                        continue
                    dates.append(cleaned)
        dates = self._clean_duplicates(dates)

        # 5. Education & Degree detection
        edu_entities = []
        edu_org_keywords = [
            "university", "college", "school", "institute", "academy",
            "polytechnic", "iit", "nit", "bits", "lpu", "vidyalaya",
            "vidyapith", "vishwavidyalaya", "education", "board"
        ]
        degree_patterns = re.compile(
            r'\b(?:b\.?\s?a\.?|b\.?\s?s\.?|b\.?\s?tech\.?|b\.?\s?e\.?|m\.?\s?a\.?|m\.?\s?s\.?|m\.?\s?tech\.?|m\.?\s?b\.?\s?a\.?|ph\.?\s?d\.?|bachelor|master|doctorate|phd|diploma)\b',
            re.IGNORECASE
        )

        # Detect educational organizations
        for org in organizations:
            if any(keyword in org.lower() for keyword in edu_org_keywords):
                edu_entities.append(org)

        # Detect degrees in text (noun chunks or line matches)
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().replace("\n", " ")
            chunk_text = " ".join(chunk_text.split())
            if degree_patterns.search(chunk_text) and len(chunk_text.split()) <= 4:
                edu_entities.append(chunk_text)

        edu_entities = self._clean_duplicates(edu_entities)

        # 6. Job Titles
        job_titles = []
        job_title_keywords = re.compile(
            r'\b(?:software engineer|developer|programmer|data scientist|analyst|manager|consultant|architect|intern|lead|director|administrator|designer|writer|specialist|officer|engineer|coder|trainee|associate|executive|coordinator|supervisor|head|chief|president|founder|co-founder)\b',
            re.IGNORECASE
        )

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().replace("\n", " ")
            chunk_text = " ".join(chunk_text.split())
            if job_title_keywords.search(chunk_text) and len(chunk_text.split()) <= 5:
                # Basic check to avoid general edu degrees matching job titles
                if not degree_patterns.search(chunk_text):
                    job_titles.append(chunk_text)

        job_titles = self._clean_duplicates(job_titles)

        # 7. Skills extraction (NEW — captures tech terms that spaCy misclassifies as ORG)
        skills = self._extract_skills(doc, text)

        return {
            "name": primary_name,
            "organizations": organizations,
            "locations": locations,
            "dates": dates,
            "education_entities": edu_entities,
            "job_titles": job_titles,
            "skills": skills
        }

    def _extract_skills(self, doc, text: str) -> list:
        """
        Extract skills/technologies from spaCy entities and text patterns.
        Captures items that would otherwise be misclassified as organizations.
        """
        skills = []

        # Collect ORG entities that are actually skills/tech
        for ent in doc.ents:
            if ent.label_ == "ORG":
                cleaned = ent.text.strip().replace("\n", " ")
                cleaned = re.sub(r'^[^\w]+', '', cleaned).strip()
                cleaned = " ".join(cleaned.split())
                if cleaned and len(cleaned) > 1:
                    if self._is_skill_like(cleaned) and not self._is_blacklisted(cleaned):
                        skills.append(cleaned)

        # Also look for known tech/skill patterns in noun chunks
        tech_pattern = re.compile(
            r'\b(?:python|java|javascript|typescript|react|angular|vue|django|flask|node\.?js|express|spring|sql|mysql|postgresql|mongodb|redis|docker|kubernetes|aws|azure|gcp|git|linux|html|css|sass|bootstrap|tailwind|figma|photoshop|illustrator|machine learning|deep learning|artificial intelligence|data science|cloud computing|devops|ci/cd|api|rest|graphql|microservices|agile|scrum|jira|jenkins|terraform|ansible|kafka|elasticsearch|tableau|power bi|excel|matlab|r programming|c\+\+|c#|rust|go|kotlin|swift|flutter|react native|next\.?js|nuxt|gatsby|svelte|pytorch|tensorflow|keras|opencv|pandas|numpy|scipy|nltk|spacy|hadoop|spark|airflow|dbt|snowflake|bigquery|databricks)\b',
            re.IGNORECASE
        )

        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.strip().replace("\n", " ")
            chunk_text = " ".join(chunk_text.split())
            if tech_pattern.search(chunk_text) and len(chunk_text.split()) <= 3:
                skills.append(chunk_text)

        skills = self._clean_duplicates(skills)
        return skills

    def _extract_header_name(self, text: str) -> Optional[str]:
        """Extract candidate name from header lines of resume text."""
        invalid_name_words = {
            "curriculum", "vitae", "resume", "profile", "summary", "objective",
            "education", "experience", "skills", "projects", "certifications",
            "languages", "hobbies", "contact", "details", "phone", "email",
            "address", "engineering", "basics", "aspirant", "internship",
            "page", "software", "developer", "engineer", "manager", "portfolio"
        }
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:10]:
            cleaned_line = re.sub(r'^[^\w\s]+', '', line).strip()
            cleaned_line = re.sub(r'\s*\|\s*.*$', '', cleaned_line).strip()
            words = cleaned_line.split()
            if 2 <= len(words) <= 4 and 3 <= len(cleaned_line) <= 40:
                if re.match(r'^[a-zA-Z\.\s\'-]+$', cleaned_line):
                    lower_words = [w.lower().rstrip('.,') for w in words]
                    if not any(w in invalid_name_words for w in lower_words):
                        return cleaned_line.title()
        return None

    def _clean_duplicates(self, items: list) -> list:
        """Remove duplicate strings while maintaining order and capitalization."""
        seen = set()
        cleaned = []
        for item in items:
            if item.lower() not in seen:
                seen.add(item.lower())
                cleaned.append(item)
        return cleaned

    def _is_blacklisted(self, text: str) -> bool:
        """
        Check if the text or any token in the text matches common technologies,
        programming languages, framework names, or human languages that spaCy
        often misclassifies as ORG, GPE, or LOC.
        """
        exclude_words = {
            # Programming languages & Core tech
            "python", "javascript", "js", "typescript", "ts", "html", "css", "java", "c", "c++", "c#", "php", "ruby", "go", "golang", "rust", "scala", "kotlin", "swift", "sql", "pl/sql", "t-sql",
            # Frameworks & Libraries
            "react", "reactjs", "angular", "angularjs", "vue", "vuejs", "django", "flask", "fastapi", "spring", "springboot", "express", "expressjs", "laravel", "rails", "jquery", "bootstrap", "tailwind", "tailwindcss", "sass", "scss", "redux", "nextjs", "nuxt", "gatsby", "svelte", "hibernate", "node", "nodejs", "numpy", "pandas", "pytorch", "tensorflow", "keras", "scikit-learn", "sklearn", "spacy", "nltk", "opencv", "matplotlib", "seaborn",
            # Databases / DevOps / Cloud / Tools
            "postgresql", "postgres", "mysql", "mongodb", "sqlite", "oracle", "redis", "cassandra", "mariadb", "neo4j", "docker", "kubernetes", "k8s", "jenkins", "git", "github", "gitlab", "bitbucket", "jira", "aws", "azure", "gcp", "heroku", "netlify", "vercel", "digitalocean", "linux", "unix", "windows", "macos", "android", "ios", "npm", "yarn", "pip", "maven", "gradle", "postman", "eslint", "prettier", "vite", "webpack", "babel",
            # Human Languages
            "english", "hindi", "spanish", "french", "german", "chinese", "japanese", "russian", "arabic", "portuguese", "italian", "bengali", "telugu", "marathi", "tamil", "urdu", "gujarati", "kannada", "malayalam", "punjabi", "sanskrit",
            # General resume sections/noise
            "skills", "skill", "experience", "education", "project", "projects", "resume", "cv", "portfolio", "details", "contact", "about", "summary", "profile", "links", "hobbies", "interests", "languages", "certificates", "certifications", "achievements", "activities",
            # Education degrees & abbreviations
            "bca", "mca", "mba", "btech", "mtech", "be", "me", "bsc", "msc", "ba", "ma", "phd", "bachelor", "master", "doctorate", "diploma"
        }
        
        # Normalize and split into individual word tokens
        clean_text = text.lower().strip()
        
        # Direct match check
        if clean_text in exclude_words:
            return True
            
        # Check if text consists entirely of non-alphabet characters or starts with a punctuation
        if not re.search(r'[a-zA-Z]', clean_text):
            return True

        # Token match: if any word token is exactly a blacklisted word, or contains "html", "css", "javascript"
        tokens = re.findall(r'\b[a-zA-Z0-9_]+\b', clean_text)
        for token in tokens:
            if token in exclude_words or any(ex in token for ex in ["html", "css", "javascript"]):
                return True
                
        return False

    def _is_skill_like(self, text: str) -> bool:
        """
        Check if text looks like a skill, technology, or technical term
        rather than a real organization name.
        """
        clean = text.lower().strip()

        # Known technology/skill terms that spaCy often classifies as ORG
        skill_terms = {
            # Technologies & Frameworks
            "dbms", "rdbms", "nosql", "iot", "ai", "ml", "dl", "nlp", "cv",
            "api", "rest", "restful", "soap", "graphql", "grpc",
            "oop", "oops", "mvc", "mvvm", "dsa", "os", "cn",
            "tcp", "udp", "http", "https", "ftp", "ssh", "ssl", "tls",
            "json", "xml", "yaml", "csv", "jwt", "oauth",
            "ci", "cd", "ci/cd", "devops", "mlops", "dataops",
            "saas", "paas", "iaas", "serverless", "microservices",
            "agile", "scrum", "kanban", "waterfall",
            "figma", "canva", "photoshop", "illustrator", "xd", "sketch",
            "excel", "word", "powerpoint", "outlook", "sharepoint",
            "tableau", "power bi", "looker", "metabase",
            "selenium", "cypress", "jest", "mocha", "pytest", "unittest",
            "swagger", "openapi", "postman", "insomnia",
            "hadoop", "spark", "hive", "pig", "sqoop", "flume",
            "kafka", "rabbitmq", "celery", "airflow",
            "ansible", "terraform", "puppet", "chef", "vagrant",
            "nginx", "apache", "tomcat", "gunicorn", "uwsgi",
            "elasticsearch", "kibana", "logstash", "grafana", "prometheus",
            "matlab", "simulink", "labview", "autocad", "solidworks",
            "blender", "unity", "unreal", "godot",
            "blockchain", "ethereum", "solidity", "web3",
            "ar", "vr", "xr", "iot",
            # Common compound tech names spaCy misclassifies
            "machine learning", "deep learning", "data science",
            "artificial intelligence", "natural language processing",
            "computer vision", "cloud computing", "big data",
            "data analytics", "data engineering", "web development",
            "mobile development", "full stack", "front end", "back end",
            "frontend", "backend", "fullstack",
            "responsive design", "ui design", "ux design", "ui/ux",
            "version control", "source control",
            "object oriented", "functional programming",
            "test driven", "behavior driven",
            "continuous integration", "continuous deployment",
            "software engineering", "computer engineering",
            "information technology", "computer science",
            "data structures", "algorithms",
            "operating systems", "computer networks",
            "database management", "system design",
        }

        # Direct match
        if clean in skill_terms:
            return True

        # Check if any known skill term is a substring match
        for term in skill_terms:
            if len(term) > 2 and term in clean:
                return True

        # Pattern: ALL CAPS short acronyms (DBMS, IoT, RDBMS, etc.) — likely tech
        if re.match(r'^[A-Z][A-Za-z]{0,2}[A-Z]+$', text.strip()):
            return True
        if re.match(r'^[A-Z]{2,6}$', text.strip()):
            return True

        # Pattern: text that starts/ends with common tech suffixes
        tech_suffixes = (
            ".js", ".py", ".io", ".css", ".ts", ".jsx", ".tsx",
            "sql", "db", "api", "sdk", "cli", "gui", "ide"
        )
        if any(clean.endswith(sfx) for sfx in tech_suffixes):
            return True

        return False

    def _is_action_verb(self, text: str) -> bool:
        """
        Check if text is an action verb commonly found in resume bullet points
        that spaCy sometimes misclassifies as ORG.
        """
        action_verbs = {
            "implemented", "created", "built", "developed", "designed",
            "managed", "led", "improved", "increased", "decreased",
            "established", "launched", "executed", "optimized", "streamlined",
            "automated", "integrated", "configured", "deployed", "maintained",
            "analyzed", "researched", "collaborated", "coordinated", "mentored",
            "trained", "presented", "published", "achieved", "delivered",
            "resolved", "debugged", "tested", "reviewed", "documented",
            "refactored", "migrated", "scaled", "monitored", "secured",
            "architected", "contributed", "spearheaded", "pioneered",
            "facilitated", "negotiated", "acquired", "retained",
            "enhanced", "reduced", "generated", "completed", "conducted",
            "leveraged", "utilized", "adopted", "applied", "assessed",
            "supervised", "oversaw", "directed", "organized", "planned",
            "initiated", "introduced", "proposed", "evaluated", "identified",
            "prepared", "processed", "performed", "participated", "assisted",
            "supported", "provided", "ensured", "handled", "addressed",
            "monitors", "implements", "creates", "builds", "develops",
            "manages", "leads", "improves", "establishes", "launches",
            "introduction", "professional", "success", "aspiration"
        }
        clean = text.lower().strip()
        # Single word action verb
        if clean in action_verbs:
            return True
        # First word of the text is an action verb (e.g. "Implemented a system")
        first_word = clean.split()[0] if clean.split() else ""
        if first_word in action_verbs:
            return True
        return False

    def _is_noisy_org(self, text: str) -> bool:
        """
        Detect noisy/generic text that is not a real organization.
        """
        clean = text.lower().strip()

        # Too short (1-2 chars) or too long (>80 chars)
        if len(clean) < 3 or len(clean) > 80:
            return True

        # Single generic word
        generic_single_words = {
            "team", "group", "department", "division", "unit", "section",
            "chapter", "committee", "board", "council", "panel",
            "internet", "web", "cloud", "server", "network", "system",
            "platform", "application", "service", "solution", "product",
            "industry", "market", "sector", "domain", "field",
            "various", "multiple", "several", "many", "few",
            "responsible", "successfully", "effectively", "efficiently",
            "technical", "professional", "academic", "personal",
            "strong", "excellent", "good", "advanced", "basic",
            "introduction", "success", "aspirant", "phone", "phone-alt",
            "monitors", "leveraged", "overview", "objective",
        }
        if clean in generic_single_words:
            return True

        # Text is just numbers or special chars
        if re.match(r'^[\d\s\-\+\.\,\(\)]+$', clean):
            return True

        # Sentence fragments (too many words for an org name)
        if len(clean.split()) > 6:
            return True

        # Contains bullet chars or special resume formatting
        if any(ch in clean for ch in ['•', '|', '►', '■', '★', '→', '⚡']):
            return True

        # Contains common resume noise patterns
        noise_patterns = [
            r'\b(internship|aspirant|phone|phone-alt)\b',
            r'\b(introduction|professional success)\b',
        ]
        for pat in noise_patterns:
            if re.search(pat, clean):
                return True

        return False

    def _handle_failure(self, resume: Resume, error_message: str, start_time: float):
        """Update model fields on failure."""
        duration = time.time() - start_time
        resume.spacy_status = Resume.SpacyStatus.FAILED
        resume.spacy_processing_time = round(duration, 4)
        resume.spacy_completed_at = timezone.now()
        resume.spacy_json = {"error": error_message}
        resume.save(
            update_fields=[
                "spacy_status",
                "spacy_processing_time",
                "spacy_completed_at",
                "spacy_json"
            ]
        )
