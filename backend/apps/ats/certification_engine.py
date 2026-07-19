import re

class CertificationEngine:
    """
    Evaluates quality, credibility, and relevance of professional certifications.
    """

    @staticmethod
    def analyze(profile, resume, profile_data: dict) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Extract certifications from profile
        certifications = []
        if hasattr(profile, 'certifications') and profile.certifications:
            if hasattr(profile.certifications, 'all'):
                certifications = list(profile.certifications.all())
            elif isinstance(profile.certifications, list):
                certifications = profile.certifications

        # Fallback to resume parsing if empty
        if not certifications:
            # Check if there are certifications in profile JSON or related
            # If completely empty, we can return a baseline but recommend certifications
            # depending on the profession. Some professions require certifications (e.g. Cybersecurity, Project Management)
            req_certs = profile_data.get("preferred_certifications", [])
            if req_certs:
                score -= 30.0
                weaknesses.append("No professional certifications listed.")
                recommendations.append(f"Highly recommended to obtain certifications for this role: {', '.join(req_certs[:2])}")
            else:
                score = 80.0 # Neutral baseline
                strengths.append("No certifications listed, which is acceptable for this role.")
            
            return {
                "category": "Certifications",
                "score": round(score, 2),
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": recommendations,
                "confidence": 90
            }

        # 1. Quantity Check
        if len(certifications) >= 3:
            strengths.append("Multiple professional certifications listed.")
        
        # 2. Provider Quality / Prestige
        prestige_providers = ["aws", "amazon", "google", "microsoft", "azure", "cisco", "pmi", "project management institute", "scrum.org", "scrum alliance", "oracle", "salesforce", "red hat"]
        has_prestige = False
        matched_preferred = []
        preferred_certs_list = [c.lower() for c in profile_data.get("preferred_certifications", [])]

        for cert in certifications:
            name = (getattr(cert, 'name', '') or getattr(cert, 'certification_name', '') or "").strip()
            authority = (getattr(cert, 'authority', '') or getattr(cert, 'issuing_organization', '') or "").strip()
            
            combined_text = f"{name} {authority}".lower()
            if any(provider in combined_text for provider in prestige_providers):
                has_prestige = True
            
            # Check preferred certifications from profile
            for pc in preferred_certs_list:
                if pc in combined_text:
                    matched_preferred.append(pc)

        if has_prestige:
            strengths.append("Contains highly recognized industry certifications (e.g. AWS, Microsoft, Cisco, Google).")
        else:
            score -= 10.0
            weaknesses.append("Certifications list is missing major recognized industry providers.")
            recommendations.append("Prioritize credentials from official authorities like AWS, Google Cloud, PMI, or Cisco.")

        # Preferred cert match
        if preferred_certs_list:
            if matched_preferred:
                strengths.append(f"Aligned with preferred role certifications: {', '.join(matched_preferred)}")
            else:
                score -= 15.0
                weaknesses.append("Lacks preferred certifications defined for this role.")
                recommendations.append(f"Consider pursuing: {', '.join(profile_data.get('preferred_certifications', [])[:2])}.")

        # Check for expiration/validity
        has_dates = False
        for cert in certifications:
            issue_date = getattr(cert, 'issue_date', None)
            if issue_date:
                has_dates = True

        if not has_dates:
            score -= 5.0
            weaknesses.append("Missing issuance/expiration dates on some certifications.")
            recommendations.append("Specify issuance dates or credential IDs for validation.")

        score = max(0.0, min(100.0, score))
        confidence = 90

        return {
            "category": "Certifications",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
