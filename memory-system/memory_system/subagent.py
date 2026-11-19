"""
AID Learning Mode Sub-Agent

Main orchestrator for conversation quality analysis.
Coordinates feedback collection, metrics calculation, pattern detection,
recommendation generation, and Claude Memory integration.

Usage:
    # As a module
    from memory_system.subagent import LearningSubAgent
    agent = LearningSubAgent()
    report = agent.analyze_quality()

    # As CLI
    python -m memory_system.subagent --analyze
    python -m memory_system.subagent --dashboard
    python -m memory_system.subagent --sync-memory
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import argparse
import sys

# Support both relative imports (when used as package) and direct imports (when used standalone)
try:
    from .feedback.collector import (
        FeedbackCollector,
        load_feedback_by_date_range,
        get_feedback_stats,
        mark_feedback_processed
    )
    from .analysis.metrics import MetricsCalculator, generate_metrics_report
    from .analysis.patterns import PatternDetector
    from .analysis.dashboard import QualityDashboard, generate_dashboard, save_dashboard
    from .analysis.memory_sync import (
        MemorySyncEngine,
        MemorySlotManager,
        sync_memory_from_feedback,
        get_current_memories,
        add_context_memory
    )
    from .recommendations.generator import (
        RecommendationGenerator,
        load_recommendation_queue,
        save_recommendations,
        format_recommendations_report,
        approve_recommendation,
        reject_recommendation
    )
    from . import paths
except ImportError:
    from feedback.collector import (
        FeedbackCollector,
        load_feedback_by_date_range,
        get_feedback_stats,
        mark_feedback_processed
    )
    from analysis.metrics import MetricsCalculator, generate_metrics_report
    from analysis.patterns import PatternDetector
    from analysis.dashboard import QualityDashboard, generate_dashboard, save_dashboard
    from analysis.memory_sync import (
        MemorySyncEngine,
        MemorySlotManager,
        sync_memory_from_feedback,
        get_current_memories,
        add_context_memory
    )
    from recommendations.generator import (
        RecommendationGenerator,
        load_recommendation_queue,
        save_recommendations,
        format_recommendations_report,
        approve_recommendation,
        reject_recommendation
    )
    import paths


# Configuration. T8-3: $AID_HOME, else ~/.aid, read on every call.
def _state_file() -> Path:
    return paths.aid_home() / "agent_state.json"


def ensure_directories():
    """Create necessary directories."""
    paths.aid_home().mkdir(parents=True, exist_ok=True)


class LearningSubAgent:
    """
    AID Learning Mode Sub-Agent

    Orchestrates all feedback analysis and learning operations.
    """

    def __init__(self, days: int = 30):
        """
        Initialize the sub-agent.

        Args:
            days: Default number of days to analyze
        """
        ensure_directories()
        self.days = days
        self.state = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        """Load agent state."""
        if _state_file().exists():
            try:
                return json.loads(_state_file().read_text(encoding="utf-8"))
            except (OSError, ValueError):
                pass

        return {
            "last_analysis": None,
            "last_sync": None,
            "last_recommendations": None,
            "analysis_count": 0,
            "sync_count": 0
        }

    def _save_state(self):
        """Save agent state."""
        _state_file().write_text(json.dumps(self.state, indent=2, ensure_ascii=False), encoding="utf-8")

    # =========================================================================
    # Session End Operations
    # =========================================================================

    def collect_session_feedback(
        self,
        session_id: str,
        role: str,
        phase: str,
        rating: int,
        interaction_type: str = "standard",
        decision_topic: Optional[str] = None,
        decision_outcome: Optional[str] = None,
        debate_details: Optional[Dict[str, Any]] = None,
        user_comment: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect feedback at session end.

        This is called when a session ends to capture the user's feedback.

        Args:
            session_id: Unique session identifier
            role: User role (developer, pm, qa, tech-lead)
            phase: AID phase (discovery, prd, tech-spec, etc.)
            rating: 1-5 rating
            interaction_type: standard, decision, debate, clarification
            decision_topic: Topic of decision (if applicable)
            decision_outcome: accepted, modified, rejected
            debate_details: Details of any debates
            user_comment: Free-form user comment
            context: Additional context

        Returns:
            Saved feedback entry
        """
        # T8-3: FeedbackCollector has no collect_feedback (AttributeError); use collect().
        collector = FeedbackCollector(session_id=session_id, phase=phase, role=role)
        decision = ({"topic": decision_topic, "chosen": decision_outcome}
                    if decision_topic or decision_outcome else None)
        return collector.collect(
            interaction_type=interaction_type,
            decision=decision,
            debate=debate_details,
            feedback={"rating": rating, "verbal": user_comment,
                      "skipped": rating is None and not user_comment},
            metadata=context
        )

    # =========================================================================
    # Daily Operations (Lazy Analysis)
    # =========================================================================

    def daily_analysis(self) -> Dict[str, Any]:
        """
        Run daily analysis of feedback.

        Calculates metrics and detects patterns from recent feedback.
        Called lazily (on demand or scheduled).

        Returns:
            Analysis results
        """
        # Load recent feedback
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        entries = load_feedback_by_date_range(
            start_date, end_date,
            include_processed=True
        )

        if not entries:
            return {
                "status": "no_data",
                "message": "No feedback entries available for analysis"
            }

        # Calculate metrics
        metrics_calc = MetricsCalculator(entries)
        metrics = metrics_calc.calculate_all_metrics()

        # Detect patterns
        pattern_detector = PatternDetector(entries)
        patterns = pattern_detector.detect_all_patterns()

        # Update state
        self.state["last_analysis"] = datetime.utcnow().isoformat() + "Z"
        self.state["analysis_count"] += 1
        self._save_state()

        return {
            "status": "success",
            "analyzed_at": self.state["last_analysis"],
            "entries_analyzed": len(entries),
            "metrics": metrics,
            "patterns": patterns
        }

    # =========================================================================
    # Weekly Operations (Recommendations)
    # =========================================================================

    def weekly_recommendations(self) -> Dict[str, Any]:
        """
        Generate weekly skill update recommendations.

        Analyzes accumulated feedback and generates actionable
        recommendations for skill improvements.

        Returns:
            Recommendation generation results
        """
        # Load feedback
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        entries = load_feedback_by_date_range(
            start_date, end_date,
            include_processed=True
        )

        if not entries:
            return {
                "status": "no_data",
                "message": "No feedback entries available for recommendations"
            }

        # Calculate metrics and patterns
        metrics_calc = MetricsCalculator(entries)
        metrics = metrics_calc.calculate_all_metrics()

        pattern_detector = PatternDetector(entries)
        patterns = pattern_detector.detect_all_patterns()

        # Generate recommendations
        rec_generator = RecommendationGenerator(metrics, patterns, entries)
        recommendations = rec_generator.generate_all_recommendations()
        # T8-4: generated recommendations are queued (they were never saved, so --pending
        # was always empty). Queuing applies nothing.
        save_recommendations(recommendations)

        # Update state
        self.state["last_recommendations"] = datetime.utcnow().isoformat() + "Z"
        self._save_state()

        return {
            "status": "success",
            "generated_at": self.state["last_recommendations"],
            "recommendations_count": len(recommendations),
            "recommendations": recommendations,
            "pending_queue": load_recommendation_queue()
        }

    # =========================================================================
    # On-Demand Operations
    # =========================================================================

    def analyze_quality(self, days: Optional[int] = None) -> Dict[str, Any]:
        """
        Full quality analysis (on-demand command).

        This is the main entry point for the /aid:analyze-quality command.
        Provides comprehensive analysis with all metrics, patterns,
        recommendations, and action items.

        Args:
            days: Number of days to analyze (default: self.days)

        Returns:
            Complete quality analysis report
        """
        analysis_days = days or self.days

        dashboard = QualityDashboard(days=analysis_days)
        report = dashboard.generate_full_report()

        # Add agent state info
        report["agent_state"] = {
            "last_analysis": self.state.get("last_analysis"),
            "last_sync": self.state.get("last_sync"),
            "analysis_count": self.state.get("analysis_count", 0)
        }

        # Update state
        self.state["last_analysis"] = datetime.utcnow().isoformat() + "Z"
        self.state["analysis_count"] += 1
        self._save_state()

        return report

    def generate_report(
        self,
        days: Optional[int] = None,
        format: str = "markdown"
    ) -> str:
        """
        Generate a formatted quality report.

        Args:
            days: Number of days to analyze
            format: 'markdown' or 'json'

        Returns:
            Formatted report string
        """
        analysis_days = days or self.days

        if format == "json":
            report = self.analyze_quality(days=analysis_days)
            return json.dumps(report, indent=2, ensure_ascii=False)

        dashboard = QualityDashboard(days=analysis_days)
        return dashboard.generate_markdown_report()

    def save_report(
        self,
        days: Optional[int] = None,
        format: str = "markdown"
    ) -> Path:
        """
        Save a quality report to file.

        Args:
            days: Number of days to analyze
            format: 'markdown' or 'json'

        Returns:
            Path to saved report
        """
        return save_dashboard(days=days or self.days, format=format)

    # =========================================================================
    # Memory Operations
    # =========================================================================

    def sync_to_memory(self, days: Optional[int] = None, approve: bool = False) -> Dict[str, Any]:
        """
        Plan (default, writes nothing) or write the learnings for AID's LOCAL memory
        ($AID_HOME/memory). ``approve=True`` is passed only by ``aid_session.py memory-sync``,
        which Claude Code asks the user to confirm (T8-2).
        """
        analysis_days = days or self.days

        result = sync_memory_from_feedback(days=analysis_days, approve=approve)

        if result.get("synced"):
            self.state["last_sync"] = datetime.utcnow().isoformat() + "Z"
            self.state["sync_count"] = self.state.get("sync_count", 0) + 1
            self._save_state()

        return result

    def get_memories(self) -> Dict[str, Any]:
        """
        Get current Claude Memory entries.

        Returns:
            Current memory state with usage statistics
        """
        return get_current_memories()

    def add_context(self, content: str, metadata: Optional[Dict] = None) -> bool:
        """
        Add a context memory entry.

        Args:
            content: Memory content
            metadata: Optional metadata

        Returns:
            True if added successfully
        """
        return add_context_memory(content, metadata)

    # =========================================================================
    # Recommendation Management
    # =========================================================================

    def get_pending_recommendations(self) -> List[Dict[str, Any]]:
        """Get pending recommendations awaiting approval."""
        return load_recommendation_queue()

    def approve_skill_update(self, recommendation_id: str) -> bool:
        """
        Approve a skill update recommendation.

        Args:
            recommendation_id: ID of recommendation to approve

        Returns:
            True if approved successfully
        """
        return approve_recommendation(recommendation_id)

    def reject_skill_update(self, recommendation_id: str, reason: str = "") -> bool:
        """
        Reject a skill update recommendation.

        Args:
            recommendation_id: ID of recommendation to reject
            reason: Rejection reason

        Returns:
            True if rejected successfully
        """
        return reject_recommendation(recommendation_id, reason)

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """
        Get overall feedback statistics.

        Returns:
            Feedback statistics
        """
        return get_feedback_stats()

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get sub-agent status.

        Returns:
            Agent state and status information
        """
        stats = self.get_stats()
        memories = self.get_memories()
        pending = self.get_pending_recommendations()

        return {
            "agent_state": self.state,
            "feedback_stats": stats,
            "memory_usage": memories.get("usage", {}),
            "pending_recommendations": len(pending),
            "status": "active"
        }


# =============================================================================
# CLI Interface
# =============================================================================

def _days(value: str) -> int:
    """--days within 1-3650 (a huge value overflowed the date arithmetic)."""
    d = int(value)
    if not 1 <= d <= 3650:
        raise argparse.ArgumentTypeError("--days must be 1-3650")
    return d


def print_sync_result(result: Dict[str, Any]):
    """Shared by the CLI preview and aid_session.py memory-preview / memory-sync."""
    if result.get("synced"):
        print("Memories added: {}".format(len(result.get("memories_added", []))))
        for mem in result.get("memories_added", []):
            print("  - [{}] {}".format(mem["category"], mem["content"]))
        return
    planned = result.get("planned") or []
    if planned:
        print("Would add {} entr{}:".format(len(planned), "y" if len(planned) == 1 else "ies"))
        for mem in planned:
            print("  - [{}] {}".format(mem["category"], mem["content"]))
    print(result.get("reason", "Nothing to sync"))


def _json_mode(args, agent: "LearningSubAgent") -> bool:
    """Print the requested operation's result as one JSON document. False when no
    operation was requested (the caller prints the help)."""
    if args.analyze or args.dashboard:
        result = agent.analyze_quality(days=args.days)
        if args.save:
            result = dict(result, saved_to=str(agent.save_report(days=args.days, format="json")))
    elif args.sync_memory:
        result = agent.sync_to_memory(days=args.days)          # dry run, writes nothing
    elif args.recommendations:
        result = agent.weekly_recommendations()
    elif args.pending:
        result = {"pending": agent.get_pending_recommendations()}
    elif args.status:
        result = agent.get_agent_status()
    elif args.stats:
        result = agent.get_stats()
    elif args.memories:
        result = agent.get_memories()
    else:
        return False
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    return True


def main():
    """CLI entry point for the sub-agent."""
    for stream in (sys.stdout, sys.stderr):      # Windows consoles: emoji in reports
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(
        description="AID Learning Mode Sub-Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m memory_system.subagent --analyze
  python -m memory_system.subagent --dashboard --days 14
  python -m memory_system.subagent --sync-memory
  python -m memory_system.subagent --status
  python -m memory_system.subagent --recommendations
        """
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run full quality analysis"
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Generate quality dashboard"
    )
    parser.add_argument(
        "--sync-memory",
        action="store_true",
        help="Preview the entries a memory sync would add to AID's local memory "
             "($AID_HOME/memory). Writes nothing; the write is aid_session.py memory-sync, "
             "which asks the user to confirm"
    )
    parser.add_argument(
        "--recommendations",
        action="store_true",
        help="Generate skill update recommendations"
    )
    parser.add_argument(
        "--pending",
        action="store_true",
        help="Show pending recommendations"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show sub-agent status"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show feedback statistics"
    )
    parser.add_argument(
        "--memories",
        action="store_true",
        help="Show AID's local memory entries ($AID_HOME/memory)"
    )
    parser.add_argument(
        "--days",
        type=_days,
        default=30,
        help="Number of days to analyze (default: 30)"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to file"
    )

    args = parser.parse_args()

    # Initialize agent
    agent = LearningSubAgent(days=args.days)

    # T15-27 (L3-2g): --format json prints ONE JSON document for every operation (no
    # banner), so a caller can json.loads the whole output. The text output is unchanged.
    if args.format == "json" and _json_mode(args, agent):
        return

    # Execute requested operation
    if args.analyze:
        print("Running quality analysis...")
        print("=" * 60)
        result = agent.analyze_quality(days=args.days)

        if args.format == "json":
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            # Print summary
            if result.get("has_data"):
                summary = result.get("summary", {})
                health = summary.get("health", {})

                print(f"\nHealth Score: {health.get('score', 'N/A')}/100")
                print(f"Status: {health.get('status', 'unknown')}")
                print(f"\nKey Metrics:")

                metrics = summary.get("key_metrics", {})
                if metrics.get("overall_rating"):
                    print(f"  - Rating: {metrics['overall_rating']}/5")
                if metrics.get("acceptance_rate") is not None:
                    print(f"  - Acceptance: {metrics['acceptance_rate']*100:.0f}%")
                if metrics.get("debate_rate") is not None:
                    print(f"  - Debate Rate: {metrics['debate_rate']*100:.0f}%")

                # Action items
                items = result.get("action_items", [])
                if items:
                    print(f"\nAction Items ({len(items)}):")
                    for item in items[:5]:
                        print(f"  [{item['priority'].upper()}] {item['action']}")
            else:
                print(result.get("message", "No data available"))

        if args.save:
            path = agent.save_report(days=args.days, format=args.format)
            print(f"\nReport saved to: {path}")

    elif args.dashboard:
        print("Generating quality dashboard...")
        print("=" * 60)

        if args.save:
            path = agent.save_report(days=args.days, format=args.format)
            print(f"Dashboard saved to: {path}")
        else:
            report = agent.generate_report(days=args.days, format=args.format)
            print(report)

    elif args.sync_memory:
        print("Memory sync preview (dry run, nothing is written)")
        print("=" * 60)
        print_sync_result(agent.sync_to_memory(days=args.days))

    elif args.recommendations:
        print("Generating skill update recommendations...")
        print("=" * 60)
        result = agent.weekly_recommendations()

        if result.get("status") == "success":
            recs = result.get("recommendations", [])
            print(f"\nGenerated {len(recs)} recommendations")

            for rec in recs[:5]:
                print(f"\n[{str(rec.get('priority', '?')).upper()}] {rec.get('target_skill', '?')}")
                print(f"  Section: {rec.get('section', '?')}")
                print(f"  {str(rec.get('rationale', ''))[:80]}...")
        else:
            print(result.get("message", "No recommendations generated"))

    elif args.pending:
        print("Pending Recommendations")
        print("=" * 60)
        pending = agent.get_pending_recommendations()

        if pending:
            for rec in pending:
                print(f"\n[{str(rec.get('priority', '?')).upper()}] {str(rec.get('id', ''))[:16]}")
                print(f"  Skill: {rec.get('target_skill', '?')}")
                print(f"  Learnings file: {rec.get('target_file') or '(none; cannot be applied)'}")
                print(f"  Section: {rec.get('section', '?')}")
                print(f"  Proposed: {str(rec.get('proposed_change', ''))[:200]}")
        else:
            print("No pending recommendations")

    elif args.status:
        print("Sub-Agent Status")
        print("=" * 60)
        status = agent.get_agent_status()

        state = status.get("agent_state", {})
        print(f"\nLast Analysis: {state.get('last_analysis', 'Never')}")
        print(f"Last Sync: {state.get('last_sync', 'Never')}")
        print(f"Analysis Count: {state.get('analysis_count', 0)}")
        print(f"Sync Count: {state.get('sync_count', 0)}")

        print(f"\nPending Recommendations: {status.get('pending_recommendations', 0)}")

        stats = status.get("feedback_stats", {})
        print(f"\nFeedback Entries: {stats.get('total_entries', 0)}")
        print(f"Pending Processing: {stats.get('pending_count', 0)}")

        usage = status.get("memory_usage", {})
        if usage:
            print("\nMemory Usage:")
            for cat, data in usage.items():
                print(f"  {cat}: {data.get('used', 0)}/{data.get('max', 0)}")

    elif args.stats:
        print("Feedback Statistics")
        print("=" * 60)
        stats = agent.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))

    elif args.memories:
        print("AID memory entries (local, $AID_HOME/memory)")
        print("=" * 60)
        memories = agent.get_memories()

        usage = memories.get("usage", {})
        print("\nSlot Usage:")
        for cat, data in usage.items():
            print(f"  {cat}: {data.get('used', 0)}/{data.get('max', 0)} slots")

        formatted = memories.get("formatted", [])
        if formatted:
            print("\nMemories:")
            for mem in formatted:
                print(f"  - {mem}")
        else:
            print("\nNo memories stored yet")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
