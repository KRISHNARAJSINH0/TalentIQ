"""
ATS Rule Validator – Verifies rule conditions compile to valid python expressions
and ensures rule points and properties are correctly configured.
"""

import ast
from django.core.exceptions import ValidationError


class RuleValidator:
    """Validator for ATS Rules and conditions."""

    @staticmethod
    def validate_condition(condition_str: str) -> bool:
        """
        Parses a python expression string to verify if it is syntactically valid.
        Raises ValidationError if invalid.
        """
        if not condition_str or not condition_str.strip():
            raise ValidationError("Condition expression cannot be empty.")
            
        try:
            # Parse the expression
            parsed = ast.parse(condition_str.strip(), mode="eval")
            return True
        except SyntaxError as e:
            raise ValidationError(f"Syntax error in rule condition expression: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Invalid condition expression: {str(e)}")

    @classmethod
    def validate_rule(cls, rule_data: dict) -> bool:
        """
        Validates all fields in a rule dictionary.
        """
        name = rule_data.get("name")
        rule_code = rule_data.get("rule_code")
        condition = rule_data.get("condition")
        points = rule_data.get("points")
        severity = rule_data.get("severity")

        if not name or not name.strip():
            raise ValidationError("Rule name is required.")
        if not rule_code or not rule_code.strip():
            raise ValidationError("Rule code is required.")
        if points is None:
            raise ValidationError("Points / Score impact is required.")
            
        try:
            int(points)
        except (ValueError, TypeError):
            raise ValidationError("Points must be an integer.")

        if severity not in ["critical", "high", "medium", "low"]:
            raise ValidationError("Severity must be one of: critical, high, medium, low.")

        cls.validate_condition(condition)
        return True
