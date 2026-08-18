"""
AID Recommendations Module

Generates and manages skill update recommendations based on feedback analysis.
"""

from .generator import (
    RecommendationGenerator,
    save_recommendation,
    load_recommendation_queue,
    approve_recommendation,
    reject_recommendation,
    format_recommendations_report
)

__all__ = [
    "RecommendationGenerator",
    "save_recommendation",
    "load_recommendation_queue",
    "approve_recommendation",
    "reject_recommendation",
    "format_recommendations_report"
]
