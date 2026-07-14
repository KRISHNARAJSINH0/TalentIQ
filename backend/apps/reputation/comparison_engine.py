from typing import List, Dict, Any


class ComparisonEngine:
    """
    Sub-system comparison service for Resume Reputation:
    Provides benchmark comparison data across different segments and professions.
    """

    BENCHMARKS = [
        {"name": "Students", "score": 58},
        {"name": "Freshers", "score": 65},
        {"name": "Civil Engineers", "score": 70},
        {"name": "Teachers", "score": 72},
        {"name": "Designers", "score": 75},
        {"name": "Researchers", "score": 77},
        {"name": "Software Engineers", "score": 80},
        {"name": "Doctors", "score": 82},
        {"name": "ML Engineers", "score": 86},
        {"name": "Industry Average", "score": 72},
        {"name": "Top 10%", "score": 85},
        {"name": "Top 5%", "score": 90},
        {"name": "Top 1%", "score": 95}
    ]

    @classmethod
    def get_benchmarks(cls, candidate_score: float) -> List[Dict[str, Any]]:
        """
        Returns list of comparison benchmarks, including the candidate's own position.
        """
        results = []
        for b in cls.BENCHMARKS:
            results.append({
                "category": b["name"],
                "score": b["score"],
                "type": "benchmark"
            })
        
        # Insert the candidate's own score
        results.append({
            "category": "You",
            "score": round(candidate_score, 1),
            "type": "candidate"
        })
        
        # Sort benchmarks by score ascending so it displays nicely in charts
        results = sorted(results, key=lambda x: x["score"])
        return results
