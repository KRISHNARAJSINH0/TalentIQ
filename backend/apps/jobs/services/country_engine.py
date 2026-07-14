import logging

logger = logging.getLogger(__name__)


class CountryEngine:
    """
    Suggests suitable countries where candidate skills are in highest demand.
    """
    @staticmethod
    def get_countries(role: str, user_country: str = None) -> list:
        role_lower = role.lower()

        # Base list of countries where this role is in high demand
        countries = []
        if "ai" in role_lower or "ml" in role_lower or "backend" in role_lower or "software" in role_lower or "frontend" in role_lower or "full stack" in role_lower:
            countries = ["USA", "Germany", "India", "Singapore", "Canada", "UK"]
        elif "civil" in role_lower or "structural" in role_lower:
            countries = ["Australia", "Canada", "Germany", "India", "UAE"]
        elif "doctor" in role_lower:
            countries = ["USA", "UK", "Canada", "Australia", "Germany"]
        elif "teacher" in role_lower:
            countries = ["USA", "Canada", "UK", "Australia", "UAE"]
        elif "lawyer" in role_lower:
            countries = ["USA", "UK", "Singapore", "Switzerland"]
        elif "accountant" in role_lower:
            countries = ["USA", "UK", "Singapore", "Australia", "Canada"]
        elif "student" in role_lower or "intern" in role_lower:
            countries = ["USA", "Germany", "Canada", "UK"]
        elif "freelancer" in role_lower or "consultant" in role_lower:
            countries = ["Singapore", "Estonia", "Portugal", "USA", "Germany"]
        else:
            countries = ["USA", "UK", "Canada", "Germany", "Singapore"]

        # Prepend user's actual country if provided
        if user_country:
            uc_clean = user_country.strip()
            # Standardize common representations (e.g. "United States" -> "USA")
            mapping = {
                "united states": "USA",
                "united kingdom": "UK",
                "great britain": "UK",
                "india": "India",
                "germany": "Germany",
                "canada": "Canada",
                "singapore": "Singapore",
                "australia": "Australia"
            }
            uc_mapped = mapping.get(uc_clean.lower(), uc_clean)
            if uc_mapped and uc_mapped not in countries:
                countries.insert(0, uc_mapped)
            elif uc_mapped in countries:
                # Move to the front
                countries.remove(uc_mapped)
                countries.insert(0, uc_mapped)

        return countries
