import logging

logger = logging.getLogger(__name__)


class SalaryEngine:
    """
    Predicts and forecasts salary trends (current, 6m, 12m, 24m) based on role, country, and experience.
    """
    @staticmethod
    def forecast_salary(role: str, country: str, years_experience: int) -> dict:
        role_lower = role.lower()
        country_lower = country.lower()

        # Base salary range determinations by role and country
        # Standardize countries: India, USA, Germany, Canada, UK, Singapore, Australia
        
        # Determine currency & baseline factor multiplier
        if "india" in country_lower:
            currency_symbol = "₹"
            currency_suffix = " LPA"
            # Base ranges in LPA (Lakhs Per Annum)
            base_low, base_high = 6.0, 12.0
            if "senior" in role_lower or "principal" in role_lower:
                base_low, base_high = 18.0, 32.0
            elif "ml" in role_lower or "ai" in role_lower:
                base_low, base_high = 12.0, 24.0
            elif "frontend" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
                base_low, base_high = 8.0, 16.0
            elif "doctor" in role_lower:
                base_low, base_high = 15.0, 25.0
            elif "lawyer" in role_lower:
                base_low, base_high = 10.0, 18.0
            elif "student" in role_lower or "intern" in role_lower:
                base_low, base_high = 2.4, 4.8
            elif "teacher" in role_lower:
                base_low, base_high = 4.0, 8.0
        elif "germany" in country_lower or "europe" in country_lower:
            currency_symbol = "€"
            currency_suffix = "/yr"
            base_low, base_high = 50000, 75000
            if "senior" in role_lower:
                base_low, base_high = 80000, 110000
            elif "ml" in role_lower or "ai" in role_lower:
                base_low, base_high = 70000, 95000
            elif "frontend" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
                base_low, base_high = 55000, 80000
            elif "doctor" in role_lower:
                base_low, base_high = 90000, 150000
            elif "student" in role_lower:
                base_low, base_high = 15000, 25000
        elif "uk" in country_lower or "united kingdom" in country_lower:
            currency_symbol = "£"
            currency_suffix = "/yr"
            base_low, base_high = 45000, 65000
            if "senior" in role_lower:
                base_low, base_high = 75000, 105000
            elif "ml" in role_lower or "ai" in role_lower:
                base_low, base_high = 65000, 90000
            elif "frontend" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
                base_low, base_high = 50000, 75000
            elif "doctor" in role_lower:
                base_low, base_high = 80000, 130000
            elif "student" in role_lower:
                base_low, base_high = 12000, 20000
        elif "singapore" in country_lower:
            currency_symbol = "S$"
            currency_suffix = "/yr"
            base_low, base_high = 60000, 90000
            if "senior" in role_lower:
                base_low, base_high = 100000, 150000
            elif "ml" in role_lower or "ai" in role_lower:
                base_low, base_high = 85000, 120000
            elif "frontend" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
                base_low, base_high = 65000, 95000
            elif "student" in role_lower:
                base_low, base_high = 18000, 30000
        else: # USA / default (USD)
            currency_symbol = "$"
            currency_suffix = "/yr"
            # Base ranges in USD
            base_low, base_high = 80000, 115000
            if "senior" in role_lower or "principal" in role_lower:
                base_low, base_high = 135000, 185000
            elif "ml" in role_lower or "ai" in role_lower:
                base_low, base_high = 110000, 160000
            elif "frontend" in role_lower or "react" in role_lower or "ui" in role_lower or "web" in role_lower:
                base_low, base_high = 90000, 135000
            elif "doctor" in role_lower:
                base_low, base_high = 160000, 260000
            elif "student" in role_lower or "intern" in role_lower:
                base_low, base_high = 25000, 45000
            elif "teacher" in role_lower:
                base_low, base_high = 45000, 65000

        # Adjust for years of experience (approx +5% per year up to +50%)
        exp_multiplier = 1.0 + min(0.50, years_experience * 0.05)
        current_low = int(base_low * exp_multiplier)
        current_high = int(base_high * exp_multiplier)

        # Growth forecasts: 6 months (+3%), 12 months (+7%), 24 months (+15%)
        m6_low = int(current_low * 1.03)
        m6_high = int(current_high * 1.03)

        m12_low = int(current_low * 1.07)
        m12_high = int(current_high * 1.07)

        m24_low = int(current_low * 1.15)
        m24_high = int(current_high * 1.15)

        # Format helpers
        def fmt(val):
            if "LPA" in currency_suffix:
                return f"{currency_symbol}{val:.1f}{currency_suffix}"
            else:
                # Format to $85k style
                k_val = round(val / 1000)
                return f"{currency_symbol}{k_val}k{currency_suffix}"

        return {
            "current": f"{fmt(current_low)} - {fmt(current_high)}",
            "forecast": {
                "months_6": f"{fmt(m6_low)} - {fmt(m6_high)}",
                "months_12": f"{fmt(m12_low)} - {fmt(m12_high)}",
                "months_24": f"{fmt(m24_low)} - {fmt(m24_high)}"
            },
            "values": {
                "current_low": current_low,
                "current_high": current_high,
                "months_6_low": m6_low,
                "months_6_high": m6_high,
                "months_12_low": m12_low,
                "months_12_high": m12_high,
                "months_24_low": m24_low,
                "months_24_high": m24_high,
                "currency_symbol": currency_symbol,
                "currency_suffix": currency_suffix
            }
        }
