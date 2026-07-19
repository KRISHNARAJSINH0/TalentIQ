import re

class FormatEngine:
    """
    Evaluates layout, sections order, bullet points, formatting consistency, and parser compatibility.
    """

    @staticmethod
    def analyze(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # 1. Section presence and ordering checklist
        has_summary = len(profile.summary.strip()) > 10 if profile.summary else False
        has_exp = (profile.experiences.count() > 0) if hasattr(profile, 'experiences') and hasattr(profile.experiences, 'count') else False
        has_edu = (profile.educations.count() > 0) if hasattr(profile, 'educations') and hasattr(profile.educations, 'count') else False
        has_proj = (profile.projects.count() > 0) if hasattr(profile, 'projects') and hasattr(profile.projects, 'count') else False

        sections_present = sum([has_summary, has_exp, has_edu, has_proj])

        if sections_present < 4:
            score -= (4 - sections_present) * 15.0
            missing_secs = []
            if not has_summary: missing_secs.append("Summary")
            if not has_exp: missing_secs.append("Experience")
            if not has_edu: missing_secs.append("Education")
            if not has_proj: missing_secs.append("Projects")
            weaknesses.append(f"Missing core resume sections: {', '.join(missing_secs)}.")
            recommendations.append("Ensure your resume contains all standard sections: Summary, Experience, Education, and Projects.")
        else:
            strengths.append("All standard professional sections are present.")

        # 2. Bullet list checks
        experiences = list(profile.experiences.all()) if (hasattr(profile, 'experiences') and hasattr(profile.experiences, 'all')) else []
        total_exp_descriptions = 0
        bullet_list_count = 0

        for exp in experiences:
            desc = (getattr(exp, 'description', '') or "").strip()
            if desc:
                total_exp_descriptions += 1
                lines = desc.split('\n')
                # Check for bullet indicator lines
                has_bullet = any(re.match(r'^\s*[-*•\d\.]', line.strip()) for line in lines if line.strip())
                if has_bullet:
                    bullet_list_count += 1

        if total_exp_descriptions > 0:
            bullet_pct = (bullet_list_count / total_exp_descriptions) * 100.0
            if bullet_pct < 60.0:
                score -= 20.0
                weaknesses.append("Work experience details are not formatted in bullet lists.")
                recommendations.append("Convert long paragraphs in work history into clean, readable bullet points.")
            else:
                strengths.append("Consistent use of bullet points for descriptions.")
        else:
            # Neutral if no experiences
            pass

        # 3. Text layout consistency (whitespace, paragraphs, tables/images compatibility)
        # Check if the raw parsed resume content contains hints of tables or multi-column grids
        # (e.g. multiple tabs or spacing indicators)
        resume_text = getattr(resume, 'regex_completed_at', None) # just a check
        raw_text = getattr(resume, 'regex_json', {})
        if isinstance(raw_text, dict):
            raw_text = str(raw_text)
        elif not isinstance(raw_text, str):
            raw_text = ""

        # Check for column/table symbols or layout issues
        if "|" in raw_text or "  \t" in raw_text:
            score -= 10.0
            weaknesses.append("Complex multi-column or table formatting detected in parsing.")
            recommendations.append("Use a single-column layout without tables or text boxes to ensure ATS parsers read it linearly.")
        else:
            strengths.append("Simple, linear single-column layout style detected.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Formatting",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }

    @classmethod
    def analyze_formatting(cls, profile, related_data) -> dict:
        """Backward compatibility for legacy formatting analysis."""
        return {
            "structure_score": 85.0,
            "compatibility_score": 85.0,
            "formatting_score": 85.0
        }

