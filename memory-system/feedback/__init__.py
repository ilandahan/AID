"""
AID Feedback Collection Module

Handles collection, storage, and retrieval of user feedback.
"""

from .collector import (
    FeedbackCollector,
    save_feedback,
    save_feedback_entry,
    load_feedback_by_date_range,
    load_pending_feedback,
    get_feedback_stats,
    mark_feedback_processed,
    get_pending_feedback
)

__all__ = [
    "FeedbackCollector",
    "save_feedback",
    "save_feedback_entry",
    "load_feedback_by_date_range",
    "load_pending_feedback",
    "get_feedback_stats",
    "mark_feedback_processed",
    "get_pending_feedback"
]
