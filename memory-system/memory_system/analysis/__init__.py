"""
AID Analysis Module

Provides metrics calculation, pattern detection, dashboards, and memory sync.
"""

from .metrics import MetricsCalculator, generate_metrics_report
from .patterns import PatternDetector
from .dashboard import QualityDashboard, generate_dashboard, save_dashboard
from .memory_sync import (
    MemorySyncEngine,
    MemorySlotManager,
    sync_memory_from_feedback,
    get_current_memories,
    add_context_memory
)

__all__ = [
    # Metrics
    "MetricsCalculator",
    "generate_metrics_report",
    # Patterns
    "PatternDetector",
    # Dashboard
    "QualityDashboard",
    "generate_dashboard",
    "save_dashboard",
    # Memory Sync
    "MemorySyncEngine",
    "MemorySlotManager",
    "sync_memory_from_feedback",
    "get_current_memories",
    "add_context_memory"
]
