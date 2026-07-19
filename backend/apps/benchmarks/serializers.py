from rest_framework import serializers
from .models import BenchmarkReport, RankingHistory, CareerRanking


class BenchmarkReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = BenchmarkReport
        fields = [
            "id",
            "resume",
            "overall_rank",
            "profession_rank",
            "industry_rank",
            "country_rank",
            "experience_rank",
            "strengths",
            "weaknesses",
            "comparison_metrics",
            "improvement_potential",
            "details_json",
            "created_at",
            "updated_at",
        ]


class RankingHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RankingHistory
        fields = [
            "id",
            "resume",
            "overall_rank",
            "overall_score",
            "recorded_at",
        ]


class CareerRankingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRanking
        fields = [
            "id",
            "resume",
            "profession",
            "experience_level",
            "industry",
            "country",
            "percentile",
        ]
