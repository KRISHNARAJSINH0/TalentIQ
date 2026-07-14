"""
ATS Analysis services – evaluation and scoring for the Master Resume Profile.
All calculations are deterministic and based on the verified Profile database record.
"""

import re
import time
from datetime import datetime
from django.utils import timezone

from apps.profiles.models import Profile, Skill, Education, Experience, Project, Certification, Language


# Industry dictionaries with target keywords and skills
INDUSTRY_DICTS = {
    "Software Engineering": {
        "keywords": ["software development", "architecture", "agile", "scrum", "git", "testing", "algorithms", "data structures", "oop", "software lifecycle", "ci/cd", "debugging", "version control", "refactoring", "sdlc"],
        "skills": ["Java", "Python", "C++", "C#", "Go", "Ruby", "System Design", "Git", "Agile", "Linux", "SQL"]
    },
    "Full Stack": {
        "keywords": ["frontend", "backend", "html", "css", "javascript", "api", "react", "angular", "node.js", "databases", "deployments", "integration", "responsive design", "mvc", "restful api"],
        "skills": ["React", "Node.js", "Express", "MongoDB", "PostgreSQL", "JavaScript", "HTML5", "CSS3", "REST APIs", "Git", "TypeScript"]
    },
    "Backend": {
        "keywords": ["server", "database", "api", "security", "scaling", "performance", "caching", "linux", "microservices", "cloud", "sql", "nosql", "rest", "graphql", "message queue"],
        "skills": ["Python", "Django", "FastAPI", "Node.js", "Go", "PostgreSQL", "Redis", "Docker", "AWS", "Celery", "Kubernetes", "REST API", "SQL"]
    },
    "Frontend": {
        "keywords": ["ui", "ux", "html", "css", "javascript", "responsive", "react", "vue", "svelte", "webpack", "babel", "design", "dom", "flexbox", "grid", "spa"],
        "skills": ["HTML5", "CSS3", "JavaScript", "React", "Vue.js", "Angular", "Sass", "Tailwind CSS", "Responsive Design", "TypeScript", "Figma"]
    },
    "AI/ML": {
        "keywords": ["machine learning", "deep learning", "neural networks", "nlp", "computer vision", "statistics", "modeling", "data", "training", "inference", "supervised", "unsupervised"],
        "skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "Keras", "Pandas", "NumPy", "OpenCV", "Natural Language Processing", "Linear Algebra"]
    },
    "Data Science": {
        "keywords": ["data analysis", "statistics", "data visualization", "sql", "python", "r", "modeling", "pandas", "etl", "tableau", "powerbi", "analytics", "regression", "probability"],
        "skills": ["Python", "R", "SQL", "Pandas", "NumPy", "Tableau", "PowerBI", "Machine Learning", "Data Visualization", "Statistics", "Excel"]
    },
    "Mechanical": {
        "keywords": ["cad", "solidworks", "autocad", "thermodynamics", "fluids", "manufacturing", "materials", "fea", "design", "hvac", "robotics", "mechanics", "stress analysis"],
        "skills": ["SolidWorks", "AutoCAD", "MATLAB", "CAD", "Finite Element Analysis (FEA)", "Manufacturing", "Thermodynamics", "Product Design", "CNC Programming"]
    },
    "Civil": {
        "keywords": ["structural", "autocad", "construction", "surveying", "concrete", "steel", "geotechnical", "infrastructure", "project management", "estimation", "drafting", "permits"],
        "skills": ["AutoCAD", "Civil 3D", "Revit", "SAP2000", "Structural Analysis", "Project Estimation", "Construction Management", "Geotechnical Engineering"]
    },
    "Electrical": {
        "keywords": ["circuit", "power", "embedded", "autocad", "plc", "microcontrollers", "matlab", "hardware", "signal processing", "schematics", "electronics", "multimeter"],
        "skills": ["AutoCAD Electrical", "MATLAB", "PLC Programming", "Circuit Design", "Embedded Systems", "Power Systems", "Microcontrollers", "PCB Design"]
    },
    "Chemical": {
        "keywords": ["process engineering", "reaction", "thermodynamics", "kinetics", "piping", "hse", "plant design", "mass transfer", "fluids", "distillation", "reactors"],
        "skills": ["ASPEN Plus", "MATLAB", "Process Simulation", "Chemical Reactors", "Thermodynamics", "Process Safety", "Piping Design"]
    },
    "HR": {
        "keywords": ["recruitment", "talent", "employee relations", "payroll", "onboarding", "benefits", "hris", "compliance", "training", "performance", "staffing", "mediation"],
        "skills": ["HRIS", "Talent Acquisition", "Employee Onboarding", "Performance Management", "Payroll Administration", "Labor Laws", "Conflict Resolution"]
    },
    "Marketing": {
        "keywords": ["seo", "sem", "campaign", "social media", "content", "analytics", "brand", "copywriting", "marketing strategy", "growth", "advertising", "market research"],
        "skills": ["Google Analytics", "SEO", "SEM", "Content Writing", "Email Marketing", "Social Media Management", "Branding", "Market Research", "Copywriting"]
    },
    "Finance": {
        "keywords": ["financial modeling", "valuation", "budgeting", "forecasting", "excel", "analysis", "portfolio", "corporate finance", "risk", "banking", "equity", "investment"],
        "skills": ["Financial Analysis", "Excel (Advanced)", "Financial Modeling", "Valuation", "Budgeting", "Risk Management", "Corporate Finance", "Portfolio Management"]
    },
    "Accounting": {
        "keywords": ["bookkeeping", "tax", "audit", "ledger", "reconciliation", "quickbooks", "gaap", "invoicing", "compliance", "balance sheet", "journal entries", "ledger"],
        "skills": ["QuickBooks", "Excel", "GAAP", "Tax Preparation", "Auditing", "General Ledger", "Accounts Payable", "Accounts Receivable", "Financial Statements"]
    },
    "Doctor": {
        "keywords": ["medicine", "diagnosis", "patient care", "clinical", "surgery", "treatment", "anatomy", "pharmacology", "ehr", "healthcare", "pediatric", "inpatient", "outpatient"],
        "skills": ["Clinical Diagnosis", "Patient Care", "Surgery", "Emergency Medicine", "Electronic Health Records (EHR)", "Pharmacology", "Medical Research"]
    },
    "Teacher": {
        "keywords": ["lesson planning", "curriculum", "classroom management", "instruction", "grading", "student engagement", "pedagogy", "tutoring", "education", "special ed"],
        "skills": ["Lesson Planning", "Classroom Management", "Curriculum Design", "Special Education", "Educational Technology", "Parent Communication", "Assessment Tools"]
    },
    "Lawyer": {
        "keywords": ["litigation", "legal research", "drafting", "contracts", "advocacy", "corporate law", "counsel", "arbitration", "jurisprudence", "deposition", "pleading"],
        "skills": ["LexisNexis", "Westlaw", "Legal Writing", "Contract Negotiation", "Litigation", "Compliance", "Corporate Law", "Intellectual Property", "Legal Counsel"]
    },
    "Freelancer": {
        "keywords": ["client management", "invoicing", "time management", "proposal", "self-employed", "consulting", "communication", "negotiation", "contracts", "billing"],
        "skills": ["Client Communication", "Project Management", "Proposal Writing", "Time Management", "Freelance Consulting", "Budgeting", "Invoicing"]
    },
    "Student": {
        "keywords": ["internship", "extracurricular", "coursework", "gpa", "projects", "learning", "research", "teamwork", "leadership", "academic", "clubs", "volunteer"],
        "skills": ["Academic Research", "Microsoft Office", "Team Collaboration", "Time Management", "Presentations", "Public Speaking", "Writing"]
    },
    "Designer": {
        "keywords": ["ui/ux", "graphic design", "figma", "adobe", "illustrator", "photoshop", "typography", "branding", "wireframing", "layout", "creative", "portfolio"],
        "skills": ["Figma", "Adobe Photoshop", "Adobe Illustrator", "UI/UX Design", "Typography", "Wireframing", "Branding", "Prototyping", "Sketch"]
    },
    "Journalist": {
        "keywords": ["reporting", "editing", "writing", "interviewing", "research", "media", "storytelling", "publishing", "broadcast", "press", "investigative", "seo writing"],
        "skills": ["News Writing", "Copy Editing", "Investigative Journalism", "Interviewing", "SEO Writing", "Content Management Systems (CMS)", "Social Media Reporting"]
    },
    "Researcher": {
        "keywords": ["analysis", "scientific writing", "hypothesis", "lab", "methodology", "literature review", "spss", "data collection", "statistics", "experiments", "academic", "grants"],
        "skills": ["Data Analysis", "Academic Writing", "Research Methodology", "SPSS", "R", "Literature Review", "Lab Techniques", "Statistical Analysis", "Grant Writing"]
    }
}

# General lists of common/low-impact/action verbs
COMMON_WEAK_WORDS = ["hardworking", "motivated", "dynamic", "detail-oriented", "team-player", "results-driven", "synergy", "think outside the box", "go-getter", "self-starter", "thought leader"]
STRONG_ACTION_VERBS = ["led", "managed", "designed", "developed", "built", "achieved", "implemented", "increased", "improved", "launched", "coordinated", "generated", "spearheaded", "accelerated", "maximized", "overhauled", "negotiated"]
COMMON_TYPOS = {
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "untill": "until",
    "commited": "committed",
    "goverment": "government",
    "enviroment": "environment",
    "refering": "referring",
    "sucessful": "successful",
    "truely": "truly"
}


class IndustryMatcherService:
    """Matches the profile to all supported industries and returns sorted match percentages."""

    @staticmethod
    def analyze(profile: Profile, profile_text: str) -> dict:
        text_lower = profile_text.lower()
        results = {}

        # Fallback if profile is completely empty
        if not text_lower.strip():
            for ind in INDUSTRY_DICTS:
                results[ind] = 0.0
            return results

        for industry, dicts in INDUSTRY_DICTS.items():
            matches = 0
            keywords = dicts["keywords"]
            for kw in keywords:
                if kw.lower() in text_lower:
                    matches += 1
            
            # Simple match percentage calculation
            percentage = (matches / len(keywords)) * 100.0
            # Boost if the industry name or target skills are matches
            skills_matches = 0
            for skill in dicts["skills"]:
                if skill.lower() in text_lower:
                    skills_matches += 1
            
            if skills_matches > 0:
                percentage += (skills_matches / len(dicts["skills"])) * 15.0
            
            results[industry] = round(min(100.0, percentage), 2)
        
        # Sort industries by match score descending
        sorted_results = dict(sorted(results.items(), key=lambda item: item[1], reverse=True))
        return sorted_results


class MissingSkillDetector:
    """Detects missing industry-standard skills based on the primary industry."""

    @staticmethod
    def detect(profile: Profile, primary_industry: str, existing_skills: list) -> list:
        if primary_industry not in INDUSTRY_DICTS:
            return []

        target_skills = INDUSTRY_DICTS[primary_industry]["skills"]
        existing_skills_lower = [s.skill_name.strip().lower() for s in existing_skills]

        missing = []
        for skill in target_skills:
            if skill.lower() not in existing_skills_lower:
                missing.append(skill)
        
        return missing


class KeywordAnalysisService:
    """Evaluates keyword usage: strong keywords, weak keywords, action verbs, repeated words."""

    @staticmethod
    def analyze(profile_text: str, primary_industry: str) -> dict:
        text_lower = profile_text.lower()
        
        # 1. Action verbs detection
        action_verbs_found = []
        for verb in STRONG_ACTION_VERBS:
            # Simple word boundary regex match
            if re.search(r'\b' + re.escape(verb) + r'\b', text_lower):
                action_verbs_found.append(verb)
        
        # 2. Weak buzzwords detection
        weak_words_found = []
        for buzz in COMMON_WEAK_WORDS:
            if re.search(r'\b' + re.escape(buzz) + r'\b', text_lower):
                weak_words_found.append(buzz)

        # 3. Strong keywords (industry matches)
        strong_keywords_found = []
        if primary_industry in INDUSTRY_DICTS:
            for kw in INDUSTRY_DICTS[primary_industry]["keywords"]:
                if kw in text_lower:
                    strong_keywords_found.append(kw)

        # 4. Repeated keywords detection (checking frequency of words > 4 characters)
        words = re.findall(r'\b[a-zA-Z]{5,}\b', text_lower)
        frequencies = {}
        for w in words:
            # Skip verbs and common noise
            if w in ["about", "their", "there", "would", "could", "should", "using", "project", "experience"]:
                continue
            frequencies[w] = frequencies.get(w, 0) + 1
        
        repeated_keywords = [w for w, count in frequencies.items() if count >= 4]

        # 5. Missing keywords from target list
        missing_keywords = []
        if primary_industry in INDUSTRY_DICTS:
            for kw in INDUSTRY_DICTS[primary_industry]["keywords"]:
                if kw not in text_lower:
                    missing_keywords.append(kw)

        return {
            "strong_keywords": strong_keywords_found,
            "weak_keywords": weak_words_found,
            "action_verbs": action_verbs_found,
            "repeated_keywords": repeated_keywords,
            "missing_keywords": missing_keywords,
            "low_impact_words": ["just", "really", "very", "basically", "actually", "essentially", "literally", "totally"]
        }


class GrammarAnalysisService:
    """Analyses summary and experiences for passive voice, reading ease, spelling, and sentence lengths."""

    @staticmethod
    def analyze(profile: Profile, experiences: list) -> dict:
        text_to_check = profile.summary or ""
        for exp in experiences:
            text_to_check += " " + (exp.description or "")

        text_to_check = text_to_check.strip()
        if not text_to_check:
            return {
                "score": 100.0,
                "passive_voice_count": 0,
                "passive_voice_examples": [],
                "spelling_issues": [],
                "long_sentences_count": 0,
                "summary_quality": "No content to evaluate"
            }

        # 1. Passive voice detection (am/is/are/was/were/been/being + verb in -ed or standard past participle)
        # We can search for helper verbs followed by a word ending in 'ed'
        passive_matches = re.findall(r'\b(was|were|been|being|is|are|am|be)\b\s+([a-zA-Z]+ed|done|made|built|run|written|held)\b', text_to_check.lower())
        passive_examples = [f"{m[0]} {m[1]}" for m in passive_matches]

        # 2. Spelling issues (simple dictionary checklist of common typos)
        spelling_issues = []
        for typo, correction in COMMON_TYPOS.items():
            if re.search(r'\b' + re.escape(typo) + r'\b', text_to_check.lower()):
                spelling_issues.append({"typo": typo, "correction": correction})

        # 3. Sentence quality & length
        # Split by punctuation
        sentences = re.split(r'[.!?]+', text_to_check)
        sentences = [s.strip() for s in sentences if s.strip()]
        long_sentences = 0
        for s in sentences:
            word_count = len(s.split())
            if word_count > 25:
                long_sentences += 1

        # 4. Summary quality
        summary_words = len((profile.summary or "").split())
        if summary_words == 0:
            summary_quality = "Missing summary"
        elif summary_words < 30:
            summary_quality = "Too short (aim for 50-150 words)"
        elif summary_words > 200:
            summary_quality = "Too long (aim for 50-150 words)"
        else:
            summary_quality = "Good length and coverage"

        # 5. Grammar Sub-score calculation
        grammar_score = 100.0
        grammar_score -= len(passive_matches) * 4.0
        grammar_score -= len(spelling_issues) * 6.0
        grammar_score -= long_sentences * 3.0
        if summary_words < 30 or summary_words > 200:
            grammar_score -= 10.0

        return {
            "score": round(max(50.0, grammar_score), 2),
            "passive_voice_count": len(passive_matches),
            "passive_voice_examples": list(set(passive_examples))[:5],
            "spelling_issues": spelling_issues,
            "long_sentences_count": long_sentences,
            "summary_quality": summary_quality
        }


class FormattingAnalysisService:
    """Evaluates the structural formatting completeness of the profile."""

    @staticmethod
    def analyze(profile: Profile, user_email: str, user_phone: str, related_data: dict) -> dict:
        checks = {
            "summary_exists": len(profile.summary.strip()) > 15 if profile.summary else False,
            "experience_exists": len(related_data["experiences"]) > 0,
            "education_exists": len(related_data["educations"]) > 0,
            "projects_exist": len(related_data["projects"]) > 0,
            "certificates_exist": len(related_data["certifications"]) > 0 or len(related_data["awards"]) > 0,
            "skills_exist": len(related_data["skills"]) > 0,
            "links_exist": bool(profile.github or profile.linkedin or profile.website or profile.portfolio_url),
            "contact_information_exists": bool(user_email or user_phone or profile.address)
        }

        # Calculate score out of 100 (12.5 points per check)
        points = sum(12.5 for check, val in checks.items() if val)
        
        return {
            "score": round(points, 2),
            "checks": checks
        }


class SuggestionService:
    """Generates prioritized recommendations for profile improvements."""

    @staticmethod
    def get_suggestions(profile: Profile, user_email: str, user_phone: str, related_data: dict, keyword_results: dict, grammar_results: dict, formatting_results: dict) -> list:
        suggestions = []

        # 1. Critical Suggestions (Severe blockers)
        if not formatting_results["checks"]["contact_information_exists"]:
            suggestions.append({
                "priority": "critical",
                "category": "Contact Information",
                "suggestion": "Add direct contact information (phone number or email address) so recruiters can reach you."
            })
        if not formatting_results["checks"]["skills_exist"]:
            suggestions.append({
                "priority": "critical",
                "category": "Skills",
                "suggestion": "Your skills section is empty. List your core technical abilities to pass ATS screening filters."
            })
        if not formatting_results["checks"]["education_exists"]:
            suggestions.append({
                "priority": "critical",
                "category": "Education",
                "suggestion": "No educational records found. Add your university degrees, colleges, or courses."
            })
        if not formatting_results["checks"]["experience_exists"]:
            suggestions.append({
                "priority": "critical",
                "category": "Experience",
                "suggestion": "Add at least one professional work experience record to show your career background."
            })

        # 2. Important Suggestions (Major boosters)
        if not formatting_results["checks"]["summary_exists"]:
            suggestions.append({
                "priority": "important",
                "category": "Summary",
                "suggestion": "Write a strong professional summary explaining your background and key competencies."
            })
        elif grammar_results["summary_quality"] != "Good length and coverage":
            suggestions.append({
                "priority": "important",
                "category": "Summary",
                "suggestion": f"Refine summary length: Currently it is {grammar_results['summary_quality']}. Aim for 50-150 words."
            })
        
        if not formatting_results["checks"]["projects_exist"]:
            suggestions.append({
                "priority": "important",
                "category": "Projects",
                "suggestion": "Include project descriptions to showcase hands-on application of your technical stack."
            })
        else:
            # Check if project has descriptions/urls
            for idx, proj in enumerate(related_data["projects"]):
                if not proj.github_url and not proj.live_url:
                    suggestions.append({
                        "priority": "important",
                        "category": "Projects",
                        "suggestion": f"Add repository or live website links to project '{proj.project_name}' to verify work."
                    })
                    break
        
        if grammar_results["passive_voice_count"] > 3:
            suggestions.append({
                "priority": "important",
                "category": "Grammar",
                "suggestion": f"Reduce passive voice usage ({grammar_results['passive_voice_count']} detected). Use strong action verbs like 'led', 'designed', or 'optimized'."
            })
        
        if len(keyword_results["action_verbs"]) < 3:
            suggestions.append({
                "priority": "important",
                "category": "Keywords",
                "suggestion": "Use stronger action verbs to initiate bullet points in your work experience descriptions."
            })

        if grammar_results["spelling_issues"]:
            suggestions.append({
                "priority": "important",
                "category": "Grammar",
                "suggestion": f"Fix identified typos: {', '.join([issue['typo'] for issue in grammar_results['spelling_issues']])}."
            })

        # 3. Optional Suggestions (Polishing)
        if not profile.linkedin:
            suggestions.append({
                "priority": "optional",
                "category": "Links",
                "suggestion": "Add your LinkedIn profile link to provide professional social proof to hiring managers."
            })
        if not profile.github:
            suggestions.append({
                "priority": "optional",
                "category": "Links",
                "suggestion": "Add your GitHub profile url to showcase code repositories and contributions."
            })
        if not (related_data["certifications"] or related_data["awards"]):
            suggestions.append({
                "priority": "optional",
                "category": "Certifications",
                "suggestion": "Include industry certifications or professional awards to highlight continuous learning."
            })
        
        # Skill-specific suggestions
        tech_skills = [s for s in related_data["skills"] if s.skill_type == Skill.SkillType.TECHNICAL]
        soft_skills = [s for s in related_data["skills"] if s.skill_type == Skill.SkillType.SOFT]
        if not tech_skills and related_data["skills"]:
            suggestions.append({
                "priority": "optional",
                "category": "Skills",
                "suggestion": "Categorize your technical skills explicitly to highlight specialized knowledge."
            })
        if not soft_skills and related_data["skills"]:
            suggestions.append({
                "priority": "optional",
                "category": "Skills",
                "suggestion": "Consider adding relevant soft skills (e.g. leadership, collaboration, mentorship)."
            })

        return suggestions


class ResumeStrengthAnalyzer:
    """Evaluates strengths and weaknesses based on analysis results."""

    @staticmethod
    def get_strengths_and_weaknesses(profile: Profile, related_data: dict, keyword_results: dict, grammar_results: dict, formatting_results: dict) -> tuple:
        strengths = []
        weaknesses = []

        # 1. Strengths
        if len(related_data["skills"]) >= 8:
            strengths.append("Diverse list of key professional skills.")
        if formatting_results["checks"]["links_exist"]:
            strengths.append("Good online presence with portfolio/repository links.")
        if len(keyword_results["action_verbs"]) >= 5:
            strengths.append("Excellent utilization of action-oriented verbs.")
        if grammar_results["passive_voice_count"] <= 1:
            strengths.append("Active voice is consistently used across descriptions.")
        if len(related_data["projects"]) >= 2:
            strengths.append("Solid project portfolio demonstrating practical achievements.")
        if formatting_results["checks"]["contact_information_exists"]:
            strengths.append("Clearly structured and complete contact section.")

        # Default strength if none
        if not strengths:
            strengths.append("Basic resume outline is set up.")

        # 2. Weaknesses
        if not formatting_results["checks"]["summary_exists"]:
            weaknesses.append("Missing introductory professional profile summary.")
        if len(keyword_results["strong_keywords"]) < 4:
            weaknesses.append("Low keyword density matching target industry roles.")
        if grammar_results["spelling_issues"]:
            weaknesses.append("Spelling and typo warnings detected in descriptions.")
        if grammar_results["long_sentences_count"] > 3:
            weaknesses.append("Several run-on/long sentences affecting readability.")
        if len(related_data["skills"]) < 4:
            weaknesses.append("Sparse skills section; needs additional tools and tech listed.")

        # Default weakness if none
        if not weaknesses:
            weaknesses.append("No major structural weaknesses detected.")

        return strengths, weaknesses


class ATSScoringService:
    """The central scoring engine that runs all sub-services and builds the final score."""

    @staticmethod
    def run_analysis(profile: Profile, resume_id: str = None) -> dict:
        start_time = time.time()

        # 1. Fetch related profile records
        skills = list(profile.skills.all())
        educations = list(profile.educations.all())
        experiences = list(profile.experiences.all())
        projects = list(profile.projects.all())
        certifications = list(profile.certifications.all())
        languages = list(profile.languages.all())
        awards = list(profile.awards.all())
        volunteer = list(profile.volunteer_work.all())
        hobbies = list(profile.hobbies.all())
        publications = list(profile.publications.all())
        references = list(profile.references.all())

        related_data = {
            "skills": skills,
            "educations": educations,
            "experiences": experiences,
            "projects": projects,
            "certifications": certifications,
            "languages": languages,
            "awards": awards,
            "volunteer": volunteer,
            "hobbies": hobbies,
            "publications": publications,
            "references": references
        }

        # Combine all profile text for keyword analysis
        profile_text_parts = [
            profile.summary or "",
            profile.address or "",
            ", ".join([s.skill_name for s in skills]),
            " ".join([exp.designation + " " + exp.company + " " + (exp.description or "") for exp in experiences]),
            " ".join([proj.project_name + " " + (proj.description or "") + " " + proj.technologies for proj in projects])
        ]
        profile_text = " ".join(profile_text_parts)

        # 2. Run Industry Matcher
        industry_matches = IndustryMatcherService.analyze(profile, profile_text)
        primary_industry = list(industry_matches.keys())[0] if industry_matches else "Software Engineering"
        industry_score = industry_matches.get(primary_industry, 50.0)

        # 3. Detect Missing Skills
        missing_skills = MissingSkillDetector.detect(profile, primary_industry, skills)

        # 4. Keyword Analysis
        keyword_analysis = KeywordAnalysisService.analyze(profile_text, primary_industry)
        
        # Calculate Keyword Score: based on strong keyword match count and action verb usage
        target_keyword_count = len(INDUSTRY_DICTS.get(primary_industry, {}).get("keywords", [1]))
        strong_keyword_ratio = len(keyword_analysis["strong_keywords"]) / target_keyword_count
        keyword_score = round(min(100.0, 40.0 + (strong_keyword_ratio * 45.0) + (len(keyword_analysis["action_verbs"]) * 2.5)), 2)

        # 5. Grammar Analysis
        grammar_analysis = GrammarAnalysisService.analyze(profile, experiences)
        grammar_score = grammar_analysis["score"]

        # 6. Formatting Analysis
        formatting_analysis = FormattingAnalysisService.analyze(profile, profile.user.email, profile.user.phone, related_data)
        formatting_score = formatting_analysis["score"]

        # 7. Skills Score calculation
        skills_score = 0.0
        if len(skills) >= 10:
            skills_score = 100.0
        elif len(skills) >= 6:
            skills_score = 85.0
        elif len(skills) >= 1:
            skills_score = 65.0
        
        # Bonus for categorizing skills
        has_tech = any(s.skill_type == Skill.SkillType.TECHNICAL for s in skills)
        has_soft = any(s.skill_type == Skill.SkillType.SOFT for s in skills)
        if has_tech and has_soft:
            skills_score = min(100.0, skills_score + 10.0)

        # 8. Education Score calculation
        education_score = 0.0
        if educations:
            education_score = 70.0
            # Give points for completeness of degree details
            complete_details = True
            for edu in educations:
                if not edu.degree or not edu.institute or not edu.start_date:
                    complete_details = False
            if complete_details:
                education_score += 30.0
        
        # 9. Experience Score calculation
        experience_score = 0.0
        if experiences:
            experience_score = 70.0
            # Estimate years of experience
            total_days = 0
            for exp in experiences:
                start = exp.start_date
                end = exp.end_date or datetime.today().date()
                total_days += (end - start).days
            
            years = total_days / 365.25
            if years >= 5.0:
                experience_score += 30.0
            elif years >= 2.0:
                experience_score += 20.0
            else:
                experience_score += 10.0
        elif primary_industry in ["Student", "Freelancer"]:
            # Students/Freelancers can score based on project quantity
            experience_score = min(90.0, 50.0 + (len(projects) * 10.0))

        # 10. Projects Score calculation
        projects_score = 0.0
        if projects:
            projects_score = 70.0
            has_links = any(proj.github_url or proj.live_url for proj in projects)
            if has_links:
                projects_score += 30.0
        elif primary_industry in ["HR", "Accounting", "Doctor", "Teacher"]:
            # Some roles might not emphasize code/technical projects
            projects_score = 80.0

        # 11. Completeness & Profile Completion %
        # Simple count of filled attributes on Profile/User + related records count
        completion_points = 0
        if profile.summary: completion_points += 10
        if profile.user.first_name and profile.user.last_name: completion_points += 10
        if profile.user.email: completion_points += 10
        if profile.user.phone: completion_points += 10
        if profile.address: completion_points += 10
        if profile.linkedin or profile.github: completion_points += 10
        if skills: completion_points += 10
        if educations: completion_points += 10
        if experiences: completion_points += 10
        if projects or certifications or languages: completion_points += 10
        completion_score = float(completion_points)

        # 12. Overall Score (Weighted combination)
        overall_score = round(
            (keyword_score * 0.20) +
            (skills_score * 0.20) +
            (experience_score * 0.20) +
            (education_score * 0.10) +
            (projects_score * 0.10) +
            (formatting_score * 0.10) +
            (grammar_score * 0.10),
            2
        )

        # 13. Strengths and Weaknesses
        strengths, weaknesses = ResumeStrengthAnalyzer.get_strengths_and_weaknesses(
            profile, related_data, keyword_analysis, grammar_analysis, formatting_analysis
        )

        # 14. Suggestions Generation
        suggestions = SuggestionService.get_suggestions(
            profile, profile.user.email, profile.user.phone, related_data, keyword_analysis, grammar_analysis, formatting_analysis
        )

        processing_time = round(time.time() - start_time, 4)

        # Return standard JSON payload
        return {
            "overall_score": overall_score,
            "keyword_score": keyword_score,
            "skills_score": skills_score,
            "experience_score": experience_score,
            "education_score": education_score,
            "grammar_score": grammar_score,
            "formatting_score": formatting_score,
            "completion_score": completion_score,
            "industry_score": round(industry_score, 2),
            "missing_skills": missing_skills,
            "suggestions": suggestions,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "metadata": {
                "primary_industry": primary_industry,
                "industry_matches": industry_matches,
                "keyword_details": {
                    "strong_keywords": keyword_analysis["strong_keywords"],
                    "weak_keywords": keyword_analysis["weak_keywords"],
                    "action_verbs": keyword_analysis["action_verbs"],
                    "repeated_keywords": keyword_analysis["repeated_keywords"]
                },
                "grammar_details": {
                    "passive_voice_count": grammar_analysis["passive_voice_count"],
                    "passive_voice_examples": grammar_analysis["passive_voice_examples"],
                    "spelling_issues": grammar_analysis["spelling_issues"],
                    "long_sentences_count": grammar_analysis["long_sentences_count"]
                },
                "processing_time": processing_time
            }
        }
