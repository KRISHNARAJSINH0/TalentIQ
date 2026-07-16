"""
ATS Rule Reporter – Generates structured summaries, recommendations, strengths,
weaknesses, bonuses, and penalties from executed rule results.
"""


class RuleReporter:
    """Formats and summarizes ATS rule execution results."""

    @staticmethod
    def build_report(execution_data: dict) -> dict:
        """
        Builds the final ATS Report JSON structure from execution results.
        """
        results = execution_data["execution_results"]

        strengths = []
        weaknesses = []
        recommendations = []
        penalties = []
        bonuses = []

        # Categorize results
        for r in results:
            if r["status"] == "passed":
                # Add to strengths if high impact or name fits
                if r["points"] > 0 and len(strengths) < 6:
                    strengths.append(f"{r['name']}: {r['explanation']}")
                
                # Add to bonuses if points are positive
                if r["points"] > 0:
                    bonuses.append({
                        "rule_code": r["rule_code"],
                        "name": r["name"],
                        "category": r["category"],
                        "points": r["points"],
                        "explanation": r["explanation"]
                    })
            elif r["status"] == "failed":
                # Add to weaknesses if critical or high severity
                if len(weaknesses) < 6:
                    weaknesses.append(f"{r['name']}: {r['recommendation']}")

                # Map severity to priority field
                priority = "optional"
                if r["severity"] == "critical":
                    priority = "critical"
                elif r["severity"] == "high":
                    priority = "important"

                # Add to recommendations
                recommendations.append({
                    "category": r["category"],
                    "suggestion": r["recommendation"],
                    "priority": priority,
                    "potential_boost": abs(r["points"])
                })

                # Add to penalties if points are negative
                if r["points"] < 0:
                    penalties.append({
                        "rule_code": r["rule_code"],
                        "name": r["name"],
                        "category": r["category"],
                        "penalty_points": r["points"],
                        "recommendation": r["recommendation"]
                    })

        # Fallbacks to ensure non-empty lists for validation/UI matches
        if not strengths:
            strengths.append("Basic resume layout and structure detected.")
        if not weaknesses:
            weaknesses.append("No critical issues found. Maintain regular content updates.")

        # Create standard return payload matching frontend expectations and specifications
        return {
            "overall_score": execution_data["overall_score"],
            "rules_executed": execution_data["rules_executed_count"],
            "passed": execution_data["passed_count"],
            "failed": execution_data["failed_count"],
            "skipped": execution_data["skipped_count"],
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "penalties": penalties,
            "bonuses": bonuses,
            "subscores": execution_data["subscores"],
            "metadata": {
                "profession": execution_data["profession"],
                "processing_time": execution_data["processing_time"],
                "job_specific_results": {
                    "job_match": execution_data.get("job_match_score") or 0,
                    "estimated_ats_job": execution_data.get("job_match_score") or 0,
                } if execution_data.get("job_match_score") is not None else {}
            }
        }
