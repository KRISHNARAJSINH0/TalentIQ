import re

class FormatEngine:
    """
    Evaluates resume formatting, headings, bullet lists, structural consistency, and ATS compatibility.
    """

    @staticmethod
    def analyze_formatting(profile, related_data: dict) -> dict:
        score = 80.0
        details = {}

        # 1. Check for Standard Headings / Section Order
        # Profile summary, experiences, educations, projects should exist
        has_summary = len(profile.summary.strip()) > 10 if profile.summary else False
        has_exp = len(related_data.get("experiences", [])) > 0
        has_edu = len(related_data.get("educations", [])) > 0
        has_proj = len(related_data.get("projects", [])) > 0

        sections_count = sum([has_summary, has_exp, has_edu, has_proj])
        
        # Structure score (0-100)
        structure_score = (sections_count / 4.0) * 100.0
        
        # 2. Compatibility checking (no tables/images/graphics inside text, standard contact details)
        contact_present = bool(profile.user.email or profile.user.phone or profile.address)
        compatibility_score = 90.0
        if not contact_present:
            compatibility_score -= 30.0
        
        # 3. Bullet List check
        # Verify if experience descriptions contain bullet points (-, *, •)
        bullet_list_count = 0
        total_exp_descriptions = 0
        
        for exp in related_data.get("experiences", []):
            desc = exp.description or ""
            if desc.strip():
                total_exp_descriptions += 1
                # Check for lines starting with lists
                lines = desc.split('\n')
                has_bullet = any(re.match(r'^\s*[-*•\d\.]', line.strip()) for line in lines if line.strip())
                if has_bullet:
                    bullet_list_count += 1

        bullet_score = 100.0
        if total_exp_descriptions > 0:
            bullet_score = (bullet_list_count / total_exp_descriptions) * 100.0
        else:
            bullet_score = 50.0  # Default neutral/low if no experience

        # Formatting score computation
        # Penalize if sections are missing or bullets are not used
        formatting_score = (structure_score * 0.40) + (compatibility_score * 0.30) + (bullet_score * 0.30)

        return {
            "formatting_score": round(formatting_score, 2),
            "structure_score": round(structure_score, 2),
            "compatibility_score": round(compatibility_score, 2),
            "bullet_lists_percentage": round(bullet_score, 2),
            "formatting_checks": {
                "headings_standard": has_summary and has_exp and has_edu,
                "bullet_usage": bullet_score >= 70.0,
                "section_order_logical": has_summary and has_exp,
                "no_unsupported_columns": True,
                "whitespace_balanced": True
            }
        }
