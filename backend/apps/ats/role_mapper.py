import logging

logger = logging.getLogger(__name__)

# List of 47 standard supported professions
SUPPORTED_ROLES = [
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "Mobile App Developer",
    "AI Engineer",
    "Machine Learning Engineer",
    "Data Scientist",
    "Data Analyst",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Engineer",
    "UI Designer",
    "UX Designer",
    "Graphic Designer",
    "Mechanical Engineer",
    "Civil Engineer",
    "Electrical Engineer",
    "Chemical Engineer",
    "Doctor",
    "Nurse",
    "Pharmacist",
    "Teacher",
    "Professor",
    "Accountant",
    "Chartered Accountant",
    "HR Executive",
    "Marketing Executive",
    "Sales Executive",
    "Business Analyst",
    "Project Manager",
    "Lawyer",
    "Architect",
    "Interior Designer",
    "Hotel Manager",
    "Chef",
    "Journalist",
    "Content Writer",
    "Photographer",
    "Video Editor",
    "Animator",
    "Fashion Designer",
    "Police Officer",
    "Freelancer",
    "Student",
    "Fresher"
]

class RoleMapper:
    """
    Normalizes arbitrary job titles and profiles to one of the 47 supported roles.
    """

    @classmethod
    def map_role(cls, title: str) -> str:
        if not title:
            return "Software Engineer"

        title_lower = title.strip().lower()

        # Check exact and substring matches
        if "backend" in title_lower:
            return "Backend Developer"
        if "frontend" in title_lower:
            return "Frontend Developer"
        if "full stack" in title_lower or "fullstack" in title_lower:
            return "Full Stack Developer"
        if any(w in title_lower for w in ["mobile", "android", "ios", "flutter", "react native", "swift", "kotlin"]):
            return "Mobile App Developer"
        if "machine learning" in title_lower or "ml" in title_lower or "deep learning" in title_lower:
            return "Machine Learning Engineer"
        if "ai" in title_lower or "artificial intelligence" in title_lower:
            return "AI Engineer"
        if "data scientist" in title_lower:
            return "Data Scientist"
        if "data analyst" in title_lower:
            return "Data Analyst"
        if "devops" in title_lower or "sre" in title_lower or "site reliability" in title_lower:
            return "DevOps Engineer"
        if "cloud" in title_lower or "aws" in title_lower or "azure" in title_lower or "gcp" in title_lower:
            return "Cloud Engineer"
        if any(w in title_lower for w in ["cyber", "security", "infosec", "penetration", "pentest"]):
            return "Cybersecurity Engineer"
        if "ui/ux" in title_lower or "ui ux" in title_lower or "ux designer" in title_lower or "user experience" in title_lower:
            return "UX Designer"
        if "ui designer" in title_lower or "user interface" in title_lower:
            return "UI Designer"
        if "graphic" in title_lower or "illustrator" in title_lower or "creative" in title_lower:
            return "Graphic Designer"
        if "mechanical" in title_lower:
            return "Mechanical Engineer"
        if "civil" in title_lower:
            return "Civil Engineer"
        if "electrical" in title_lower:
            return "Electrical Engineer"
        if "chemical" in title_lower:
            return "Chemical Engineer"
        if any(w in title_lower for w in ["doctor", "physician", "surgeon", "md", "clinical"]):
            return "Doctor"
        if "nurse" in title_lower or "nursing" in title_lower:
            return "Nurse"
        if "pharmacist" in title_lower or "pharmacy" in title_lower:
            return "Pharmacist"
        if "professor" in title_lower or "academic" in title_lower or "lecturer" in title_lower:
            return "Professor"
        if "teacher" in title_lower or "tutor" in title_lower or "educator" in title_lower or "school" in title_lower:
            return "Teacher"
        if "chartered accountant" in title_lower or "ca" == title_lower:
            return "Chartered Accountant"
        if "accountant" in title_lower or "bookkeeper" in title_lower or "accounting" in title_lower:
            return "Accountant"
        if "hr" in title_lower or "human resource" in title_lower or "recruitment" in title_lower or "talent" in title_lower:
            return "HR Executive"
        if "marketing" in title_lower or "seo" in title_lower or "growth marketer" in title_lower:
            return "Marketing Executive"
        if "sales" in title_lower or "business development" in title_lower or "bde" in title_lower:
            return "Sales Executive"
        if "business analyst" in title_lower:
            return "Business Analyst"
        if "project manager" in title_lower or "scrum master" in title_lower or "pm" == title_lower:
            return "Project Manager"
        if "lawyer" in title_lower or "attorney" in title_lower or "legal" in title_lower or "barrister" in title_lower:
            return "Lawyer"
        if "interior designer" in title_lower or "interior design" in title_lower:
            return "Interior Designer"
        if "architect" in title_lower:
            return "Architect"
        if "hotel manager" in title_lower or "hotel management" in title_lower:
            return "Hotel Manager"
        if "chef" in title_lower or "cook" in title_lower:
            return "Chef"
        if "journalist" in title_lower or "reporter" in title_lower:
            return "Journalist"
        if "content writer" in title_lower or "copywriter" in title_lower or "blogger" in title_lower:
            return "Content Writer"
        if "photographer" in title_lower or "photography" in title_lower:
            return "Photographer"
        if "video editor" in title_lower or "video editing" in title_lower:
            return "Video Editor"
        if "animator" in title_lower or "animation" in title_lower:
            return "Animator"
        if "fashion" in title_lower or "apparel designer" in title_lower:
            return "Fashion Designer"
        if "police" in title_lower or "law enforcement" in title_lower or "officer" in title_lower:
            return "Police Officer"
        if "freelancer" in title_lower or "contractor" in title_lower or "independent" in title_lower:
            return "Freelancer"
        if "student" in title_lower or "intern" in title_lower:
            return "Student"
        if "fresher" in title_lower or "entry level" in title_lower or "trainee" in title_lower:
            return "Fresher"

        # Default fallback
        return "Software Engineer"
