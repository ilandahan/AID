"""
AID Learning Mode Metrics Calculator

Calculates quality metrics from aggregated feedback data.
Part of the AID Memory System sub-agent.
"""

from typing import Dict, Any, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import json
from pathlib import Path

# Support both relative imports (when used as package) and direct imports (when used standalone)
try:
    from ..feedback.collector import load_pending_feedback, load_feedback_by_date_range
except ImportError:
    from feedback.collector import load_pending_feedback, load_feedback_by_date_range


class MetricsCalculator:
    """Calculate quality metrics from feedback entries."""

    def __init__(self, feedback_entries: List[Dict[str, Any]]):
        """
        Initialize with feedback entries.

        Args:
            feedback_entries: List of feedback entry dictionaries
        """
        self.entries = feedback_entries
        self._cache = {}

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """
        Calculate all available metrics.

        Returns:
            Dictionary containing all metrics
        """
        return {
            "summary": self.get_summary(),
            "decision_acceptance": self.calculate_decision_acceptance_rate(),
            "debate_outcomes": self.calculate_debate_outcomes(),
            "ratings_by_category": self.calculate_ratings_by_category(),
            "feedback_engagement": self.calculate_feedback_engagement(),
            "verbosity_signals": self.calculate_verbosity_signals(),
            "trends": self.calculate_trends()
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get high-level summary statistics."""
        total = len(self.entries)
        if total == 0:
            return {"total_entries": 0, "date_range": None}

        dates = [e['timestamp'][:10] for e in self.entries]
        return {
            "total_entries": total,
            "date_range": {
                "start": min(dates),
                "end": max(dates)
            },
            "unique_sessions": len(set(e.get('session_id', '') for e in self.entries))
        }

    def calculate_decision_acceptance_rate(self) -> Dict[str, Any]:
        """
        Calculate decision acceptance rate.

        acceptance_rate = (decisions_confirmed_without_debate) / (total_decisions)
        """
        decision_entries = [
            e for e in self.entries
            if e.get('decision') and e['decision'].get('topic')
        ]

        if not decision_entries:
            return {"rate": None, "total_decisions": 0}

        total = len(decision_entries)
        debates = sum(
            1 for e in decision_entries
            if e.get('debate', {}).get('occurred', False)
        )
        confirmed_without_debate = total - debates

        rate = confirmed_without_debate / total if total > 0 else 0

        interpretation = self._interpret_acceptance_rate(rate)

        return {
            "rate": round(rate, 3),
            "total_decisions": total,
            "confirmed_without_debate": confirmed_without_debate,
            "debated": debates,
            "interpretation": interpretation
        }

    def _interpret_acceptance_rate(self, rate: float) -> str:
        """Interpret the acceptance rate."""
        if rate >= 0.9:
            return "Excellent - Claude recommendations well-aligned with user"
        elif rate >= 0.7:
            return "Good - Room for improvement in some areas"
        else:
            return "Needs attention - Significant misalignment detected"

    def calculate_debate_outcomes(self) -> Dict[str, Any]:
        """
        Calculate debate outcome statistics.

        debate_win_rate = (debates_where_Claude_position_held) / (total_debates)
        debate_change_rate = (debates_where_Claude_changed) / (total_debates)
        """
        debate_entries = [
            e for e in self.entries
            if e.get('debate', {}).get('occurred', False)
        ]

        if not debate_entries:
            return {
                "total_debates": 0,
                "outcomes": {},
                "win_rate": None,
                "change_rate": None
            }

        total = len(debate_entries)
        outcomes = defaultdict(int)

        for entry in debate_entries:
            outcome = entry.get('debate', {}).get('outcome', 'unknown')
            outcomes[outcome] += 1

        confirmed = outcomes.get('confirmed', 0)
        changed = outcomes.get('changed', 0)
        partial = outcomes.get('partially_changed', 0)

        win_rate = confirmed / total if total > 0 else 0
        change_rate = changed / total if total > 0 else 0

        # Analyze debate topics
        topic_changes = defaultdict(lambda: {"total": 0, "changed": 0})
        for entry in debate_entries:
            topic = entry.get('decision', {}).get('topic_category', 'other')
            topic_changes[topic]["total"] += 1
            if entry.get('debate', {}).get('outcome') in ['changed', 'partially_changed']:
                topic_changes[topic]["changed"] += 1

        topics_by_change_rate = {
            topic: {
                "total": data["total"],
                "change_rate": round(data["changed"] / data["total"], 2) if data["total"] > 0 else 0
            }
            for topic, data in topic_changes.items()
        }

        return {
            "total_debates": total,
            "outcomes": dict(outcomes),
            "win_rate": round(win_rate, 3),
            "change_rate": round(change_rate, 3),
            "partial_change_rate": round(partial / total, 3) if total > 0 else 0,
            "topics_by_change_rate": topics_by_change_rate,
            "interpretation": self._interpret_debate_outcomes(change_rate, topics_by_change_rate)
        }

    def _interpret_debate_outcomes(
        self,
        change_rate: float,
        topics: Dict[str, Dict]
    ) -> str:
        """Interpret debate outcomes."""
        if change_rate > 0.5:
            high_change_topics = [
                t for t, d in topics.items()
                if d['change_rate'] > 0.5 and d['total'] >= 3
            ]
            if high_change_topics:
                return f"High change rate - Review guidance for: {', '.join(high_change_topics)}"
            return "High change rate - User has strong preferences or Claude recommendations need improvement"
        elif change_rate > 0.3:
            return "Moderate change rate - Normal healthy debate pattern"
        else:
            return "Low change rate - Claude positions generally hold after debate"

    def calculate_ratings_by_category(self) -> Dict[str, Any]:
        """
        Calculate average ratings by phase, role, and interaction type.
        """
        rated_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('rating') is not None
        ]

        if not rated_entries:
            return {
                "by_phase": {},
                "by_role": {},
                "by_interaction": {},
                "overall_average": None
            }

        # Group by categories
        by_phase = defaultdict(list)
        by_role = defaultdict(list)
        by_interaction = defaultdict(list)

        for entry in rated_entries:
            rating = entry['feedback']['rating']
            context = entry.get('context', {})

            phase = context.get('phase', 'unknown')
            role = context.get('role', 'unknown')
            interaction = context.get('interaction_type', 'unknown')

            by_phase[phase].append(rating)
            by_role[role].append(rating)
            by_interaction[interaction].append(rating)

        def calc_avg(ratings: List[int]) -> Dict[str, Any]:
            if not ratings:
                return {"average": None, "count": 0}
            return {
                "average": round(sum(ratings) / len(ratings), 2),
                "count": len(ratings),
                "min": min(ratings),
                "max": max(ratings)
            }

        all_ratings = [e['feedback']['rating'] for e in rated_entries]

        return {
            "by_phase": {k: calc_avg(v) for k, v in sorted(by_phase.items())},
            "by_role": {k: calc_avg(v) for k, v in sorted(by_role.items())},
            "by_interaction": {k: calc_avg(v) for k, v in sorted(by_interaction.items())},
            "overall_average": round(sum(all_ratings) / len(all_ratings), 2),
            "weak_spots": self._identify_weak_spots(by_phase, by_role, by_interaction)
        }

    def _identify_weak_spots(
        self,
        by_phase: Dict[str, List[int]],
        by_role: Dict[str, List[int]],
        by_interaction: Dict[str, List[int]]
    ) -> List[Dict[str, Any]]:
        """Identify categories with consistently low ratings."""
        weak_spots = []
        threshold = 3.5  # Below this is considered weak

        for category_name, category_data in [
            ("phase", by_phase),
            ("role", by_role),
            ("interaction", by_interaction)
        ]:
            for key, ratings in category_data.items():
                if len(ratings) >= 3:  # Need enough data
                    avg = sum(ratings) / len(ratings)
                    if avg < threshold:
                        weak_spots.append({
                            "category": category_name,
                            "value": key,
                            "average_rating": round(avg, 2),
                            "sample_size": len(ratings)
                        })

        return sorted(weak_spots, key=lambda x: x['average_rating'])

    def calculate_feedback_engagement(self) -> Dict[str, Any]:
        """
        Calculate feedback engagement metrics.

        feedback_response_rate = (feedback_given) / (feedback_requested)
        skip_rate = (feedback_skipped) / (feedback_requested)
        verbal_rate = (verbal_feedback) / (feedback_given)
        """
        total = len(self.entries)
        if total == 0:
            return {
                "response_rate": None,
                "skip_rate": None,
                "verbal_rate": None
            }

        feedback_given = sum(
            1 for e in self.entries
            if e.get('feedback', {}).get('rating') is not None
            or e.get('feedback', {}).get('verbal')
        )

        skipped = sum(
            1 for e in self.entries
            if e.get('feedback', {}).get('skipped', True)
            and e.get('feedback', {}).get('rating') is None
        )

        verbal = sum(
            1 for e in self.entries
            if e.get('feedback', {}).get('verbal')
        )

        response_rate = feedback_given / total if total > 0 else 0
        skip_rate = skipped / total if total > 0 else 0
        verbal_rate = verbal / feedback_given if feedback_given > 0 else 0

        interpretation = []
        if skip_rate > 0.3:
            interpretation.append("High skip rate - Consider reducing feedback frequency")
        if verbal_rate > 0.5:
            interpretation.append("High verbal rate - Users are engaged, valuable insights available")
        if response_rate > 0.8:
            interpretation.append("Excellent engagement - Users actively providing feedback")

        return {
            "total_opportunities": total,
            "feedback_given": feedback_given,
            "skipped": skipped,
            "verbal_feedback": verbal,
            "response_rate": round(response_rate, 3),
            "skip_rate": round(skip_rate, 3),
            "verbal_rate": round(verbal_rate, 3),
            "interpretation": interpretation
        }

    def calculate_verbosity_signals(self) -> Dict[str, Any]:
        """
        Analyze verbal feedback for verbosity preferences.
        """
        verbose_keywords = [
            "verbose", "long", "faster", "brief", "shorter",
            "too much", "lengthy", "wordy", "concise"
        ]
        detail_keywords = [
            "more detail", "explain", "why", "expand",
            "elaborate", "unclear", "confused", "more info"
        ]

        verbal_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('verbal')
        ]

        verbose_complaints = 0
        detail_requests = 0

        for entry in verbal_entries:
            verbal = entry['feedback']['verbal'].lower()
            for keyword in verbose_keywords:
                if keyword in verbal:
                    verbose_complaints += 1
                    break
            for keyword in detail_keywords:
                if keyword in verbal:
                    detail_requests += 1
                    break

        # Determine preference
        if verbose_complaints > detail_requests * 2:
            preference = "prefers_concise"
        elif detail_requests > verbose_complaints * 2:
            preference = "prefers_detailed"
        else:
            preference = "balanced"

        return {
            "verbose_complaints": verbose_complaints,
            "detail_requests": detail_requests,
            "detected_preference": preference,
            "sample_size": len(verbal_entries)
        }

    def calculate_trends(self) -> Dict[str, Any]:
        """
        Calculate trends over time.
        """
        if len(self.entries) < 5:
            return {"sufficient_data": False}

        # Group by week
        weekly_data = defaultdict(list)
        for entry in self.entries:
            # Get ISO week
            date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
            week_key = f"{date.year}-W{date.isocalendar()[1]:02d}"

            rating = entry.get('feedback', {}).get('rating')
            if rating is not None:
                weekly_data[week_key].append(rating)

        # Calculate weekly averages
        weekly_averages = {
            week: round(sum(ratings) / len(ratings), 2)
            for week, ratings in sorted(weekly_data.items())
            if len(ratings) >= 2
        }

        # Determine trend
        if len(weekly_averages) >= 3:
            weeks = list(weekly_averages.keys())
            recent = [weekly_averages[w] for w in weeks[-3:]]
            older = [weekly_averages[w] for w in weeks[:-3]] if len(weeks) > 3 else [weekly_averages[weeks[0]]]

            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)

            if recent_avg > older_avg + 0.3:
                trend = "improving"
            elif recent_avg < older_avg - 0.3:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "sufficient_data": True,
            "weekly_averages": weekly_averages,
            "trend": trend
        }


def calculate_metrics_from_pending() -> Dict[str, Any]:
    """
    Calculate metrics from all pending feedback.

    Returns:
        Complete metrics dictionary
    """
    entries = load_pending_feedback()
    calculator = MetricsCalculator(entries)
    return calculator.calculate_all_metrics()


def calculate_metrics_for_period(
    days: int = 30,
    include_processed: bool = True
) -> Dict[str, Any]:
    """
    Calculate metrics for a specific time period.

    Args:
        days: Number of days to look back
        include_processed: Whether to include processed feedback

    Returns:
        Complete metrics dictionary
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    entries = load_feedback_by_date_range(
        start_date,
        end_date,
        include_processed=include_processed
    )

    calculator = MetricsCalculator(entries)
    return calculator.calculate_all_metrics()


def generate_metrics_report(metrics: Dict[str, Any]) -> str:
    """
    Generate a human-readable metrics report.

    Args:
        metrics: Metrics dictionary from calculate_all_metrics()

    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 60)
    report.append("AID CONVERSATION QUALITY METRICS REPORT")
    report.append("=" * 60)
    report.append("")

    # Summary
    summary = metrics.get('summary', {})
    report.append("## Summary")
    report.append(f"Total Entries: {summary.get('total_entries', 0)}")
    if summary.get('date_range'):
        report.append(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    report.append(f"Unique Sessions: {summary.get('unique_sessions', 0)}")
    report.append("")

    # Decision Acceptance
    acceptance = metrics.get('decision_acceptance', {})
    report.append("## Decision Acceptance Rate")
    if acceptance.get('rate') is not None:
        report.append(f"Rate: {acceptance['rate'] * 100:.1f}%")
        report.append(f"Total Decisions: {acceptance['total_decisions']}")
        report.append(f"Debated: {acceptance['debated']}")
        report.append(f"Interpretation: {acceptance['interpretation']}")
    else:
        report.append("No decision data available")
    report.append("")

    # Debate Outcomes
    debates = metrics.get('debate_outcomes', {})
    report.append("## Debate Outcomes")
    if debates.get('total_debates', 0) > 0:
        report.append(f"Total Debates: {debates['total_debates']}")
        report.append(f"Win Rate: {debates['win_rate'] * 100:.1f}%")
        report.append(f"Change Rate: {debates['change_rate'] * 100:.1f}%")
        report.append(f"Interpretation: {debates['interpretation']}")
    else:
        report.append("No debate data available")
    report.append("")

    # Ratings
    ratings = metrics.get('ratings_by_category', {})
    report.append("## Ratings by Category")
    report.append(f"Overall Average: {ratings.get('overall_average', 'N/A')}")
    report.append("")

    if ratings.get('by_phase'):
        report.append("### By Phase")
        for phase, data in ratings['by_phase'].items():
            report.append(f"  {phase}: {data['average']} ({data['count']} ratings)")

    if ratings.get('weak_spots'):
        report.append("")
        report.append("### Weak Spots (< 3.5 avg)")
        for spot in ratings['weak_spots']:
            report.append(f"  - {spot['category']}/{spot['value']}: {spot['average_rating']} avg ({spot['sample_size']} samples)")

    report.append("")

    # Engagement
    engagement = metrics.get('feedback_engagement', {})
    report.append("## Feedback Engagement")
    if engagement.get('response_rate') is not None:
        report.append(f"Response Rate: {engagement['response_rate'] * 100:.1f}%")
        report.append(f"Skip Rate: {engagement['skip_rate'] * 100:.1f}%")
        report.append(f"Verbal Rate: {engagement['verbal_rate'] * 100:.1f}%")
        for interp in engagement.get('interpretation', []):
            report.append(f"  - {interp}")
    report.append("")

    # Verbosity
    verbosity = metrics.get('verbosity_signals', {})
    report.append("## Verbosity Preference")
    report.append(f"Detected Preference: {verbosity.get('detected_preference', 'unknown')}")
    report.append(f"Verbose Complaints: {verbosity.get('verbose_complaints', 0)}")
    report.append(f"Detail Requests: {verbosity.get('detail_requests', 0)}")
    report.append("")

    # Trends
    trends = metrics.get('trends', {})
    report.append("## Trends")
    if trends.get('sufficient_data'):
        report.append(f"Trend: {trends.get('trend', 'unknown')}")
    else:
        report.append("Insufficient data for trend analysis")

    report.append("")
    report.append("=" * 60)

    return "\n".join(report)


if __name__ == "__main__":
    # Test with sample data
    print("Testing Metrics Calculator...")

    sample_entries = [
        {
            "id": "1",
            "timestamp": "2024-01-15T10:00:00Z",
            "session_id": "session-1",
            "context": {"phase": "2-tech-spec", "role": "developer", "interaction_type": "decision"},
            "decision": {"topic": "Database selection", "topic_category": "technology", "chosen": "PostgreSQL"},
            "debate": {"occurred": False},
            "feedback": {"rating": 5, "verbal": None, "skipped": False}
        },
        {
            "id": "2",
            "timestamp": "2024-01-15T11:00:00Z",
            "session_id": "session-1",
            "context": {"phase": "2-tech-spec", "role": "developer", "interaction_type": "decision"},
            "decision": {"topic": "Architecture", "topic_category": "architecture", "chosen": "Microservices"},
            "debate": {"occurred": True, "outcome": "changed", "learning": "Team prefers monolith"},
            "feedback": {"rating": 4, "verbal": "Changed after discussion", "skipped": False}
        },
        {
            "id": "3",
            "timestamp": "2024-01-16T09:00:00Z",
            "session_id": "session-2",
            "context": {"phase": "4-development", "role": "developer", "interaction_type": "review"},
            "decision": {"topic": "Code pattern", "topic_category": "other", "chosen": "Repository pattern"},
            "debate": {"occurred": False},
            "feedback": {"rating": 5, "verbal": "Perfect!", "skipped": False}
        }
    ]

    calculator = MetricsCalculator(sample_entries)
    metrics = calculator.calculate_all_metrics()

    print("\nGenerated Report:")
    print(generate_metrics_report(metrics))
