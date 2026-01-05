"""
AID Memory System - Learning Mode Sub-Agent

A feedback analysis system that learns from user interactions
to improve Claude's assistance quality over time.

Main Components:
- feedback/: Feedback collection and storage
- analysis/: Metrics, patterns, and dashboards
- recommendations/: Skill update recommendations

Usage:
    from memory_system import LearningSubAgent

    agent = LearningSubAgent()
    report = agent.analyze_quality()
"""

from .subagent import LearningSubAgent

__version__ = "1.0.0"
__all__ = ["LearningSubAgent"]
