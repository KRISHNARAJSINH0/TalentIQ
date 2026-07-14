"""
JD Parser — Extracts structured data from raw job description text.

Uses regex + NLP heuristics to detect:
  - Job title, company, location, employment type, remote status
  - Sections (overview, requirements, responsibilities, qualifications, benefits)
  - Required skills from a 200+ real-world tech skill taxonomy
  - Education requirements, experience years, seniority level
  - Salary range
"""

import re
import logging

logger = logging.getLogger(__name__)


# ─── Real-World Skill Taxonomy (200+ skills) ───────────────────────────────

SKILL_TAXONOMY = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c",
    "go", "golang", "rust", "ruby", "php", "swift", "kotlin", "scala",
    "r", "matlab", "perl", "dart", "lua", "haskell", "elixir", "clojure",
    "objective-c", "shell", "bash", "powershell", "sql", "nosql", "groovy",

    # Web Frontend
    "react", "reactjs", "react.js", "angular", "angularjs", "vue", "vuejs",
    "vue.js", "svelte", "nextjs", "next.js", "nuxt", "nuxtjs", "gatsby",
    "html", "html5", "css", "css3", "sass", "scss", "less", "tailwind",
    "tailwindcss", "bootstrap", "material-ui", "mui", "chakra-ui",
    "styled-components", "webpack", "vite", "parcel", "babel", "eslint",
    "prettier", "jquery", "redux", "mobx", "zustand", "recoil",

    # Web Backend
    "django", "flask", "fastapi", "express", "expressjs", "nestjs",
    "spring", "spring boot", "springboot", "rails", "ruby on rails",
    "laravel", "symfony", "asp.net", ".net", "dotnet", "gin", "fiber",
    "actix", "rocket", "phoenix", "koa", "hapi", "strapi",

    # Databases
    "postgresql", "postgres", "mysql", "mariadb", "mongodb", "sqlite",
    "oracle", "sql server", "mssql", "redis", "memcached", "elasticsearch",
    "dynamodb", "cassandra", "couchdb", "neo4j", "influxdb", "supabase",
    "firebase", "firestore", "cockroachdb", "timescaledb",

    # Cloud & DevOps
    "aws", "amazon web services", "azure", "gcp", "google cloud",
    "docker", "kubernetes", "k8s", "terraform", "ansible", "puppet",
    "chef", "vagrant", "jenkins", "circleci", "github actions",
    "gitlab ci", "travis ci", "argocd", "helm", "istio", "consul",
    "nginx", "apache", "caddy", "traefik", "cloudflare", "vercel",
    "netlify", "heroku", "digitalocean", "linode",

    # Data & ML
    "pandas", "numpy", "scipy", "scikit-learn", "sklearn",
    "tensorflow", "keras", "pytorch", "jax", "xgboost", "lightgbm",
    "catboost", "hugging face", "huggingface", "transformers",
    "opencv", "spacy", "nltk", "gensim", "mlflow", "kubeflow",
    "airflow", "apache airflow", "spark", "apache spark", "pyspark",
    "hadoop", "hive", "kafka", "apache kafka", "flink", "dbt",
    "snowflake", "databricks", "bigquery", "redshift", "looker",
    "tableau", "power bi", "powerbi", "metabase", "grafana",
    "matplotlib", "seaborn", "plotly", "streamlit", "gradio",

    # AI / LLM
    "openai", "gpt", "chatgpt", "langchain", "llamaindex",
    "llm", "rag", "prompt engineering", "fine-tuning",
    "stable diffusion", "midjourney", "dall-e", "whisper",
    "gemini", "claude", "anthropic", "cohere", "pinecone",
    "weaviate", "chromadb", "faiss", "vector database",

    # Mobile
    "react native", "flutter", "swiftui", "jetpack compose",
    "android", "ios", "xamarin", "ionic", "cordova", "expo",

    # Testing
    "jest", "mocha", "chai", "cypress", "playwright", "selenium",
    "puppeteer", "pytest", "unittest", "rspec", "junit", "testng",
    "vitest", "testing library", "enzyme", "supertest", "postman",

    # Tools & Practices
    "git", "github", "gitlab", "bitbucket", "svn",
    "jira", "confluence", "trello", "asana", "notion", "linear",
    "figma", "sketch", "adobe xd", "invision",
    "agile", "scrum", "kanban", "ci/cd", "cicd",
    "tdd", "bdd", "pair programming", "code review",
    "microservices", "monolith", "serverless", "event-driven",
    "rest", "restful", "graphql", "grpc", "websocket", "soap",
    "oauth", "jwt", "saml", "sso",
    "linux", "unix", "windows server", "macos",

    # Security
    "owasp", "penetration testing", "vulnerability assessment",
    "encryption", "ssl", "tls", "ssh", "vpn", "firewall",
    "iam", "rbac", "zero trust", "soc2", "gdpr", "hipaa",
    "cybersecurity", "devsecops", "sast", "dast",

    # Others
    "api", "sdk", "cli", "etl", "data pipeline",
    "data modeling", "data engineering", "data science",
    "machine learning", "deep learning", "nlp",
    "computer vision", "reinforcement learning",
    "system design", "distributed systems",
    "high availability", "scalability", "load balancing",
    "caching", "message queue", "rabbitmq", "celery",
    "websockets", "sse", "blockchain", "web3", "solidity",
}

# Synonym map for fuzzy matching
SKILL_SYNONYMS = {
    "js": "javascript",
    "ts": "typescript",
    "py": "python",
    "node": "nodejs",
    "node.js": "nodejs",
    "react.js": "react",
    "reactjs": "react",
    "vue.js": "vue",
    "vuejs": "vue",
    "angular.js": "angular",
    "angularjs": "angular",
    "next.js": "nextjs",
    "nuxt.js": "nuxtjs",
    "express.js": "expressjs",
    "nest.js": "nestjs",
    "spring boot": "springboot",
    "ruby on rails": "rails",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "k8s": "kubernetes",
    "postgres": "postgresql",
    "mongo": "mongodb",
    "sql server": "mssql",
    "scikit-learn": "sklearn",
    "apache spark": "spark",
    "apache kafka": "kafka",
    "apache airflow": "airflow",
    "power bi": "powerbi",
    "hugging face": "huggingface",
    "ci/cd": "cicd",
    "golang": "go",
    ".net": "dotnet",
    "asp.net": "dotnet",
}

# Section heading patterns
SECTION_PATTERNS = {
    "overview": r"(?i)(about\s+(?:the\s+)?(?:role|position|job|opportunity)|overview|summary|description|introduction)",
    "requirements": r"(?i)(requirements?|what\s+(?:you|we)\s+(?:need|require|expect)|must\s+have|mandatory)",
    "responsibilities": r"(?i)(responsibilities|what\s+you['']?ll?\s+do|duties|key\s+(?:responsibilities|duties)|your\s+role)",
    "qualifications": r"(?i)(qualifications?|who\s+you\s+are|ideal\s+candidate|about\s+you)",
    "preferred": r"(?i)(preferred|nice\s+to\s+have|bonus|good\s+to\s+have|plus|desirable|advantageous)",
    "benefits": r"(?i)(benefits?|perks|what\s+we\s+offer|compensation|why\s+join)",
    "company": r"(?i)(about\s+(?:us|the\s+company|our\s+company)|who\s+we\s+are|company\s+(?:overview|description))",
}

# Seniority patterns
SENIORITY_PATTERNS = [
    (r"(?i)\b(principal|staff|distinguished|fellow)\b", "Principal"),
    (r"(?i)\b(senior|sr\.?|lead)\b", "Senior"),
    (r"(?i)\b(mid[- ]?level|intermediate)\b", "Mid-Level"),
    (r"(?i)\b(junior|jr\.?|entry[- ]?level|associate|graduate)\b", "Junior"),
    (r"(?i)\b(intern|internship|trainee|apprentice)\b", "Intern"),
]

# Education patterns
EDUCATION_PATTERNS = [
    (r"(?i)\b(ph\.?d|doctorate|doctoral)\b", "PhD"),
    (r"(?i)\b(master'?s?|m\.?s\.?|m\.?sc|m\.?tech|mba|m\.?eng)\b", "Master's"),
    (r"(?i)\b(bachelor'?s?|b\.?s\.?|b\.?sc|b\.?tech|b\.?eng|b\.?a\.?|undergraduate)\b", "Bachelor's"),
    (r"(?i)\b(diploma|associate'?s?)\b", "Diploma"),
]

# Employment type
EMPLOYMENT_PATTERNS = {
    "full-time": r"(?i)\b(full[- ]?time)\b",
    "part-time": r"(?i)\b(part[- ]?time)\b",
    "contract": r"(?i)\b(contract|freelance|consulting)\b",
    "internship": r"(?i)\b(internship|intern)\b",
}

# Industry classification keywords
INDUSTRY_KEYWORDS = {
    "Technology": ["software", "saas", "platform", "tech", "technology", "it", "digital"],
    "AI / Machine Learning": ["ai", "artificial intelligence", "machine learning", "ml", "deep learning", "nlp", "llm", "data science"],
    "FinTech": ["fintech", "finance", "banking", "payment", "trading", "crypto", "blockchain"],
    "Healthcare": ["health", "healthcare", "medical", "pharma", "biotech", "clinical"],
    "E-Commerce": ["ecommerce", "e-commerce", "retail", "marketplace", "shopping"],
    "Cybersecurity": ["security", "cybersecurity", "infosec", "threat", "vulnerability"],
    "Cloud / Infrastructure": ["cloud", "infrastructure", "devops", "sre", "platform engineering"],
    "Gaming": ["game", "gaming", "esports", "unity", "unreal"],
    "Analytics": ["analytics", "data analytics", "business intelligence", "bi", "reporting"],
    "EdTech": ["education", "edtech", "learning", "lms", "e-learning"],
    "SaaS": ["saas", "subscription", "b2b", "enterprise software"],
}


class JDParser:
    """
    Parse raw job description text into structured data.
    """

    def parse(self, content: str) -> dict:
        """
        Main entry point. Returns a dict with all extracted fields.
        """
        if not content or not content.strip():
            return {"error": "Empty job description content"}

        content_clean = content.strip()
        content_lower = content_clean.lower()

        result = {
            "title": self._extract_title(content_clean),
            "company": self._extract_company(content_clean),
            "location": self._extract_location(content_clean),
            "employment_type": self._detect_employment_type(content_lower),
            "remote_status": self._detect_remote(content_lower),
            "seniority": self._detect_seniority(content_clean),
            "experience_years": self._extract_experience_years(content_clean),
            "education": self._extract_education(content_clean),
            "salary_range": self._extract_salary(content_clean),
            "industry": self._detect_industry(content_lower),
            "skills": self._extract_skills(content_lower),
            "sections": self._detect_sections(content_clean),
            "requirements": self._extract_requirements(content_clean),
            "responsibilities": self._extract_responsibilities(content_clean),
        }

        logger.info(
            "JDParser extracted %d skills, seniority=%s, exp=%s",
            len(result["skills"]),
            result["seniority"],
            result["experience_years"],
        )
        return result

    # ── Title ───────────────────────────────────────────────────────
    def _extract_title(self, text: str) -> str:
        """Extract job title from the first few lines."""
        lines = text.strip().split("\n")
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue
            # Skip lines that look like company names or headers
            if re.match(r"(?i)^(about|we are|our|the company|join)", line):
                continue
            # Likely title if short and contains role keywords
            if len(line) < 120 and re.search(
                r"(?i)(engineer|developer|analyst|designer|manager|architect|scientist|consultant|specialist|lead|director|coordinator|administrator|officer|executive)",
                line,
            ):
                # Clean artifacts
                title = re.sub(r"[\*\#\-\_\=]+", "", line).strip()
                return title
        # Fallback: first non-empty line
        for line in lines[:3]:
            line = line.strip()
            if line and len(line) < 120:
                return re.sub(r"[\*\#\-\_\=]+", "", line).strip()
        return ""

    # ── Company ─────────────────────────────────────────────────────
    def _extract_company(self, text: str) -> str:
        patterns = [
            r"(?i)(?:company|employer|organization)\s*[:–—-]\s*(.+?)(?:\n|$)",
            r"(?i)(?:at|@)\s+([A-Z][A-Za-z0-9\s&\.]+?)(?:\s*[-–—]|\n|$)",
            r"(?i)about\s+([A-Z][A-Za-z0-9\s&\.]{2,40})(?:\n|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                company = match.group(1).strip()
                if len(company) < 60:
                    return company
        return ""

    # ── Location ────────────────────────────────────────────────────
    def _extract_location(self, text: str) -> str:
        patterns = [
            r"(?i)location\s*[:–—-]\s*(.+?)(?:\n|$)",
            r"(?i)(?:based\s+in|located\s+in|office\s+in)\s+(.+?)(?:\n|\.|$)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                loc = match.group(1).strip()
                if len(loc) < 80:
                    return loc
        return ""

    # ── Employment type ─────────────────────────────────────────────
    def _detect_employment_type(self, text_lower: str) -> str:
        for etype, pattern in EMPLOYMENT_PATTERNS.items():
            if re.search(pattern, text_lower):
                return etype
        return "full-time"

    # ── Remote ──────────────────────────────────────────────────────
    def _detect_remote(self, text_lower: str) -> str:
        if re.search(r"(?i)\b(fully\s+remote|100%\s+remote|remote\s+(?:only|first|friendly|position|role|work))\b", text_lower):
            return "remote"
        if re.search(r"(?i)\b(hybrid|flex|flexible\s+(?:work|location))\b", text_lower):
            return "hybrid"
        if re.search(r"(?i)\b(on[- ]?site|in[- ]?office|office[- ]?based)\b", text_lower):
            return "on-site"
        if "remote" in text_lower:
            return "remote"
        return "on-site"

    # ── Seniority ───────────────────────────────────────────────────
    def _detect_seniority(self, text: str) -> str:
        # Check first 500 chars (title area)
        header = text[:500]
        for pattern, level in SENIORITY_PATTERNS:
            if re.search(pattern, header):
                return level
        return "Mid-Level"

    # ── Experience years ────────────────────────────────────────────
    def _extract_experience_years(self, text: str) -> dict:
        patterns = [
            r"(\d+)\+?\s*(?:to|-|–)\s*(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?",
            r"(\d+)\+\s*(?:years?|yrs?)\s*(?:of)?\s*(?:experience|exp)?",
            r"(?:at\s+least|minimum|min)\s*(\d+)\s*(?:years?|yrs?)",
            r"(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*(?:relevant|professional|hands-on|industry)?\s*(?:experience|exp)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[1]:
                    return {"min": int(groups[0]), "max": int(groups[1])}
                return {"min": int(groups[0]), "max": int(groups[0]) + 2}
        return {"min": 0, "max": 0}

    # ── Education ───────────────────────────────────────────────────
    def _extract_education(self, text: str) -> dict:
        for pattern, level in EDUCATION_PATTERNS:
            if re.search(pattern, text):
                # Try to find field of study
                field_match = re.search(
                    r"(?i)(?:in|of)\s+(computer\s+science|engineering|information\s+technology|mathematics|statistics|physics|data\s+science|business|finance|economics|arts|design|communications|marketing|psychology|biology|chemistry|nursing|medicine)",
                    text,
                )
                return {
                    "level": level,
                    "field": field_match.group(1).title() if field_match else "",
                }
        return {"level": "", "field": ""}

    # ── Salary ──────────────────────────────────────────────────────
    def _extract_salary(self, text: str) -> dict:
        patterns = [
            r"[\$₹€£]\s*(\d[\d,]*)\s*(?:k|K)?\s*(?:to|-|–)\s*[\$₹€£]?\s*(\d[\d,]*)\s*(?:k|K)?",
            r"(\d[\d,]*)\s*(?:to|-|–)\s*(\d[\d,]*)\s*(?:LPA|CTC|per\s+annum|\/yr|\/year)",
            r"(?:salary|compensation|ctc|package)\s*[:–—-]\s*[\$₹€£]?\s*(\d[\d,]*)\s*(?:k|K)?\s*(?:to|-|–)\s*[\$₹€£]?\s*(\d[\d,]*)\s*(?:k|K)?",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {"min": match.group(1), "max": match.group(2)}
        return {}

    # ── Industry ────────────────────────────────────────────────────
    def _detect_industry(self, text_lower: str) -> str:
        scores = {}
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[industry] = score
        if scores:
            return max(scores, key=scores.get)
        return "Technology"

    # ── Skills ──────────────────────────────────────────────────────
    def _extract_skills(self, text_lower: str) -> list:
        """Extract all recognized skills from the JD text."""
        found = set()
        for skill in SKILL_TAXONOMY:
            # Word-boundary match to avoid partial hits
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text_lower):
                # Normalize via synonym map
                normalized = SKILL_SYNONYMS.get(skill, skill)
                found.add(normalized)
        return sorted(found)

    # ── Sections ────────────────────────────────────────────────────
    def _detect_sections(self, text: str) -> dict:
        """Detect section boundaries in the JD."""
        sections = {}
        lines = text.split("\n")
        current_section = "overview"
        current_lines = []

        for line in lines:
            stripped = line.strip()
            matched = False
            for section_name, pattern in SECTION_PATTERNS.items():
                if re.match(pattern, stripped):
                    # Save previous section
                    if current_lines:
                        sections[current_section] = "\n".join(current_lines).strip()
                    current_section = section_name
                    current_lines = []
                    matched = True
                    break
            if not matched:
                current_lines.append(line)

        # Save last section
        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections

    # ── Requirements ────────────────────────────────────────────────
    def _extract_requirements(self, text: str) -> list:
        """Extract bullet-point requirements."""
        requirements = []
        in_requirements = False
        for line in text.split("\n"):
            stripped = line.strip()
            if re.match(SECTION_PATTERNS["requirements"], stripped):
                in_requirements = True
                continue
            if in_requirements:
                if re.match(r"(?i)^(responsibilities|qualifications|benefits|about)", stripped):
                    break
                # Capture bullet items
                cleaned = re.sub(r"^[\s•·\-\*\►\▸\➤\➜\→]+", "", stripped).strip()
                if cleaned and len(cleaned) > 10:
                    requirements.append(cleaned)
        return requirements[:15]

    # ── Responsibilities ────────────────────────────────────────────
    def _extract_responsibilities(self, text: str) -> list:
        """Extract bullet-point responsibilities."""
        responsibilities = []
        in_responsibilities = False
        for line in text.split("\n"):
            stripped = line.strip()
            if re.match(SECTION_PATTERNS["responsibilities"], stripped):
                in_responsibilities = True
                continue
            if in_responsibilities:
                if re.match(r"(?i)^(requirements|qualifications|benefits|about)", stripped):
                    break
                cleaned = re.sub(r"^[\s•·\-\*\►\▸\➤\➜\→]+", "", stripped).strip()
                if cleaned and len(cleaned) > 10:
                    responsibilities.append(cleaned)
        return responsibilities[:15]
