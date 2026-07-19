import re

class ContactEngine:
    """
    Evaluates quality of Contact Information including validity and professionalism.
    """

    @staticmethod
    def analyze(profile, resume) -> dict:
        score = 100.0
        strengths = []
        weaknesses = []
        recommendations = []

        # Extract values
        email = (profile.user.email or "").strip()
        phone = (profile.user.phone or "").strip()
        name = f"{profile.user.first_name or ''} {profile.user.last_name or ''}".strip()
        
        # Look for social/professional URLs
        linkedin = ""
        github = ""
        portfolio = ""
        
        # Check profile links
        links = profile.links if hasattr(profile, 'links') and profile.links else []
        # Support either direct string or serialized list
        if isinstance(links, str):
            links = [links]
        
        for link in links:
            link_lower = link.lower()
            if "linkedin.com" in link_lower:
                linkedin = link
            elif "github.com" in link_lower:
                github = link
            elif any(x in link_lower for x in ["portfolio", "personal", "site", "web"]):
                portfolio = link

        # Also fallback to resume content if fields are empty
        resume_text = (resume.regex_json or {}).get("Contact", "")
        if isinstance(resume_text, dict):
            resume_text = str(resume_text)
        elif not isinstance(resume_text, str):
            resume_text = ""

        # Validity Checks
        # Name check
        if not name or len(name) < 3:
            score -= 20.0
            weaknesses.append("Full name is missing or too short on your profile.")
            recommendations.append("Ensure your full legal name is prominently displayed at the top of your resume.")
        else:
            strengths.append("Full name is clearly presented.")

        # Email check
        if not email:
            score -= 20.0
            weaknesses.append("Email address is missing.")
            recommendations.append("Provide a valid email address for recruiters to reach you.")
        else:
            # Check validity
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                score -= 15.0
                weaknesses.append("Email format appears invalid.")
                recommendations.append("Ensure your email uses standard format (e.g. name@domain.com).")
            else:
                # Professionalism check
                unprofessional_words = ["crazy", "sexy", "cool", "gamer", "stud", "wild", "party"]
                if any(w in email.lower() for w in unprofessional_words):
                    score -= 15.0
                    weaknesses.append("Email address uses unprofessional keywords.")
                    recommendations.append("Use a professional email address containing your name (e.g. john.doe@email.com).")
                
                standard_domains = ["gmail.com", "outlook.com", "yahoo.com", "icloud.com", "protonmail.com", "hotmail.com"]
                email_domain = email.split("@")[-1].lower() if "@" in email else ""
                if email_domain not in standard_domains and not email_domain.endswith((".edu", ".org")):
                    # Minor note but not a major penalty
                    strengths.append(f"Email uses custom domain: {email_domain}")
                else:
                    strengths.append("Professional email address provided.")

        # Phone check
        if not phone:
            score -= 15.0
            weaknesses.append("Phone number is missing.")
            recommendations.append("Add a valid phone number with country/area code.")
        else:
            # Valid format check (e.g. +1234567890 or standard formats)
            clean_phone = re.sub(r"[\s\-\(\)\+]", "", phone)
            if len(clean_phone) < 7 or not clean_phone.isdigit():
                score -= 10.0
                weaknesses.append("Phone number format is invalid.")
                recommendations.append("Format your phone number correctly (e.g., +1 (555) 019-2834).")
            else:
                strengths.append("Valid phone number format detected.")

        # Location check
        location = getattr(profile, 'address', '') or ""
        if not location or len(location.strip()) < 5:
            score -= 10.0
            weaknesses.append("Physical location (City, State/Country) is missing or incomplete.")
            recommendations.append("Include your location (City, State or Country) to help recruiters identify relocation/commute requirements.")
        else:
            strengths.append("Physical location details are complete.")

        # Social links check
        if not linkedin:
            score -= 10.0
            weaknesses.append("LinkedIn profile link is missing.")
            recommendations.append("Include a link to your LinkedIn profile to showcase your professional network.")
        else:
            if not linkedin.startswith(("http://", "https://")):
                score -= 5.0
                weaknesses.append("LinkedIn link is malformed (missing https://).")
                recommendations.append("Ensure your LinkedIn URL is fully qualified starting with https://.")
            else:
                strengths.append("LinkedIn profile link is present and correctly formatted.")

        if not github:
            score -= 5.0  # Minor penalty for general, we will assess it more specifically in GitHub engine
        else:
            strengths.append("GitHub profile link is present.")

        score = max(0.0, min(100.0, score))
        confidence = 95 if (email and phone) else 80

        return {
            "category": "Contact Information",
            "score": round(score, 2),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "confidence": confidence
        }
