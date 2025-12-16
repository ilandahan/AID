"""
AID Feedback Collection Module

Handles collection, storage, and retrieval of user feedback.
"""

from .collector import (
    FeedbackCollector,
    save_feedback,
    load_feedback_by_date_range,
    get_feedback_stats,
    mark_feedback_processed,
    get_pending_feedback
)

__all__ = [
    "FeedbackCollector",
    "save_feedback",
    "load_feedback_by_date_range",
    "get_feedback_stats",
    "mark_feedback_processed",
    "get_pending_feedback"
]
