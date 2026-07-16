from apps.ats.models import ATSBenchmark

class BenchmarkEngine:
    """
    Computes candidate performance comparison against profession-specific benchmarks and percentiles.
    """

    DEFAULT_BENCHMARKS = {
        "Student": {"p25": 48, "p50": 60, "p75": 72, "p90": 85, "avg": 62},
        "Freelancer": {"p25": 52, "p50": 66, "p75": 78, "p90": 88, "avg": 67},
        "Software Engineer": {"p25": 58, "p50": 72, "p75": 84, "p90": 92, "avg": 71},
        "AI Engineer": {"p25": 60, "p50": 74, "p75": 85, "p90": 94, "avg": 73},
        "Data Analyst": {"p25": 55, "p50": 70, "p75": 82, "p90": 91, "avg": 69},
        "UI Designer": {"p25": 54, "p50": 68, "p75": 80, "p90": 90, "avg": 68},
        "Teacher": {"p25": 50, "p50": 65, "p75": 77, "p90": 88, "avg": 65},
        "Doctor": {"p25": 62, "p50": 76, "p75": 86, "p90": 95, "avg": 75},
        "Lawyer": {"p25": 60, "p50": 75, "p75": 85, "p90": 93, "avg": 74},
        "Civil Engineer": {"p25": 54, "p50": 68, "p75": 80, "p90": 90, "avg": 67},
        "Mechanical Engineer": {"p25": 55, "p50": 69, "p75": 81, "p90": 90, "avg": 68},
        "Chemical Engineer": {"p25": 56, "p50": 70, "p75": 82, "p90": 91, "avg": 69},
        "Marketing": {"p25": 52, "p50": 66, "p75": 78, "p90": 89, "avg": 66},
        "HR": {"p25": 50, "p50": 64, "p75": 76, "p90": 87, "avg": 64}
    }

    @staticmethod
    def get_benchmark_comparison(profession: str, overall_score: int) -> dict:
        # Try finding in database
        try:
            bench = ATSBenchmark.objects.get(profession=profession)
            p25 = bench.percentile_25
            p50 = bench.percentile_50
            p75 = bench.percentile_75
            p90 = bench.percentile_90
            avg = bench.average_score
        except ATSBenchmark.DoesNotExist:
            # Prepopulate defaults
            b_data = BenchmarkEngine.DEFAULT_BENCHMARKS.get(profession, BenchmarkEngine.DEFAULT_BENCHMARKS["Software Engineer"])
            p25 = b_data["p25"]
            p50 = b_data["p50"]
            p75 = b_data["p75"]
            p90 = b_data["p90"]
            avg = b_data["avg"]

            # Save default to database silently for future runs
            try:
                ATSBenchmark.objects.create(
                    profession=profession,
                    percentile_25=p25,
                    percentile_50=p50,
                    percentile_75=p75,
                    percentile_90=p90,
                    average_score=avg
                )
            except Exception:
                pass

        # Determine candidate's percentile range
        if overall_score >= p90:
            percentile_str = f"Top 10% (Percentile > 90)"
            standing = "Excellent"
        elif overall_score >= p75:
            percentile_str = f"Top 25% (Percentile 75-90)"
            standing = "Strongly Competitive"
        elif overall_score >= p50:
            percentile_str = f"Top 50% (Percentile 50-75)"
            standing = "Above Average"
        elif overall_score >= p25:
            percentile_str = f"Top 75% (Percentile 25-50)"
            standing = "Below Average"
        else:
            percentile_str = f"Bottom 25% (Percentile < 25)"
            standing = "Needs Immediate Improvement"

        return {
            "profession": profession,
            "percentile_25": p25,
            "percentile_50": p50,
            "percentile_75": p75,
            "percentile_90": p90,
            "average_score": avg,
            "candidate_standing": standing,
            "candidate_percentile_range": percentile_str
        }
