import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
URL_REGEX = r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$"


class ContactValidator:
    """
    Service to validate contact information, detecting:
    - Missing email, missing phone, missing linkedin
    - Invalid email formats
    - Malformed phone numbers
    - Invalid GitHub usernames or portfolio URLs
    """

    def validate_contact(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scans payload for missing contact information and invalid formats.
        Returns a list of error dictionaries.
        """
        errors: List[Dict[str, Any]] = []

        # 1. Email Checks
        email = payload.get("email")
        if not email or not str(email).strip():
            errors.append({
                "type": "missing_contact",
                "field": "email",
                "value": "",
                "severity": "critical",
                "confidence": 99,
                "action": "recover",
                "reason": "Missing email address"
            })
        elif isinstance(email, str):
            email_str = email.strip()
            if not re.match(EMAIL_REGEX, email_str):
                errors.append({
                    "type": "formatting_issue",
                    "field": "email",
                    "value": email_str,
                    "severity": "high",
                    "confidence": 95,
                    "action": "recover",
                    "reason": f"Malformed email address '{email_str}'"
                })

        # 2. Phone Checks
        phone = payload.get("phone")
        if not phone or not str(phone).strip():
            errors.append({
                "type": "missing_contact",
                "field": "phone",
                "value": "",
                "severity": "high",
                "confidence": 95,
                "action": "recover",
                "reason": "Missing phone number"
            })
        else:
            phone_str = str(phone).strip()
            digits = re.sub(r"\D", "", phone_str)
            if len(digits) < 7 or len(digits) > 15:
                errors.append({
                    "type": "formatting_issue",
                    "field": "phone",
                    "value": phone_str,
                    "severity": "medium",
                    "confidence": 90,
                    "action": "review",
                    "reason": f"Invalid phone number '{phone_str}' (digit count: {len(digits)})"
                })

        # 3. LinkedIn Checks
        linkedin = payload.get("linkedin")
        if not linkedin or not str(linkedin).strip():
            errors.append({
                "type": "missing_contact",
                "field": "linkedin",
                "value": "",
                "severity": "medium",
                "confidence": 85,
                "action": "review",
                "reason": "Missing LinkedIn profile URL"
            })

        # 4. GitHub Checks
        github = payload.get("github")
        if github and str(github).strip():
            gh_str = str(github).strip()
            if not ("github.com" in gh_str.lower() or re.match(r"^[a-zA-Z0-9-]+$", gh_str)):
                errors.append({
                    "type": "formatting_issue",
                    "field": "github",
                    "value": gh_str,
                    "severity": "medium",
                    "confidence": 85,
                    "action": "review",
                    "reason": f"Invalid GitHub profile or username '{gh_str}'"
                })

        # 5. Portfolio URL Checks
        portfolio = payload.get("portfolio") or payload.get("website")
        if portfolio and str(portfolio).strip():
            port_str = str(portfolio).strip()
            if not re.match(URL_REGEX, port_str, re.IGNORECASE):
                errors.append({
                    "type": "formatting_issue",
                    "field": "portfolio",
                    "value": port_str,
                    "severity": "low",
                    "confidence": 80,
                    "action": "review",
                    "reason": f"Invalid website/portfolio URL format '{port_str}'"
                })

        return errors
