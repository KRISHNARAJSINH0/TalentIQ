import re

class ProjectsEngine:
    """
    Evaluates the quality, complexity, repositories, and impact of Projects.
    """

    @staticmethod
    def analyze(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Get projects
        projects = []
        if hasattr(profile, 'projects') and profile.projects:
            if hasattr(profile.projects, 'all'):
                projects = list(profile.projects.all())
            elif isinstance(profile.projects, list):
                projects = profile.projects

        if not projects:
            return {
                "category": "Projects",
                "score": 0.0,
                "strengths": [],
                "weaknesses": ["No personal or professional projects listed."],
                "recommendations": ["Add 2-3 significant projects with descriptions of tools used and live repository links."],
                "confidence": 90
            }

        # 1. Project Count Check
        if len(projects) < 2:
            score -= 15.0
            weaknesses.append("Too few projects listed.")
            recommendations.append("List at least 2-3 detailed projects to showcase hands-on experience.")
        else:
            strengths.append(f"Good variety of projects ({len(projects)}) listed.")

        # 2. Technology Stack & Detail Checks
        has_github_links = False
        has_live_links = False
        has_tech_stack = False
        total_project_words = 0
        architecture_terms = ["api", "database", "server", "frontend", "backend", "microservices", "cloud", "ui", "ux", "rest", "graphql"]
        found_arch = False

        for proj in projects:
            title = (getattr(proj, 'title', '') or getattr(proj, 'project_title', '') or "").strip()
            desc = (getattr(proj, 'description', '') or "").strip()
            url = (getattr(proj, 'project_url', '') or getattr(proj, 'url', '') or "").strip()
            repo = (getattr(proj, 'github_url', '') or getattr(proj, 'repository', '') or "").strip()

            total_project_words += len(desc.split())

            if "github.com" in repo.lower() or "github.com" in url.lower():
                has_github_links = True
            if url and "github.com" not in url.lower():
                has_live_links = True
            
            # Check tech stack list
            technologies = getattr(proj, 'technologies', [])
            if technologies:
                has_tech_stack = True
            elif re.search(r'\b(using|built with|developed using|tech stack|technologies)\b', desc.lower()):
                has_tech_stack = True

            # Architecture terms check
            if any(term in desc.lower() for term in architecture_terms):
                found_arch = True

        # Average words per project
        avg_project_len = total_project_words / len(projects)
        if avg_project_len < 20:
            score -= 20.0
            weaknesses.append("Project descriptions are extremely brief.")
            recommendations.append("Expand project descriptions with details about architecture, your contributions, and tech stacks.")
        elif avg_project_len >= 50:
            strengths.append("Project descriptions have rich context and implementation detail.")

        # Tech stack validation
        if not has_tech_stack:
            score -= 15.0
            weaknesses.append("Missing explicit technology stacks in project descriptions.")
            recommendations.append("Explicitly state the languages, frameworks, and databases used for each project.")
        else:
            strengths.append("Projects explicitly outline the technology stacks used.")

        # Repo links validation
        if not has_github_links:
            score -= 15.0
            weaknesses.append("Projects lack links to source code repositories (e.g. GitHub).")
            recommendations.append("Add links to your public GitHub repositories so recruiters can verify your coding standards.")
        else:
            strengths.append("Includes repository links for code verification.")

        # Live demo links validation
        if not has_live_links:
            score -= 5.0
            weaknesses.append("Projects lack links to live demonstrations or hosted websites.")
            recommendations.append("Provide live URLs or demo links (e.g. Vercel, Netlify, AWS) to make projects interactive.")
        else:
            strengths.append("Includes live deployment links.")

        # Architecture and design check
        if not found_arch:
            score -= 10.0
            weaknesses.append("Lacks architectural explanations in project details.")
            recommendations.append("Use standard engineering terms (e.g. API, database, server, frontend) to explain your project designs.")
        else:
            strengths.append("Details include clear architectural descriptions.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Projects",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
