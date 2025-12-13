"""
AID Learning Mode Quality Dashboard

Generates comprehensive quality reports from feedback analysis.
Part of the AID Memory System sub-agent.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import os
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback.collector import load_feedback_by_date_range, get_feedback_stats
from analysis.metrics import MetricsCalculator, generate_metrics_report
from analysis.patterns import PatternDetector
from recommendations.generator import (
    RecommendationGenerator,
    load_recommendation_queue,
    format_recommendations_report
)

# Configuration
REPORTS_DIR = Path(os.path.expanduser("~/.aid/reports"))


def ensure_directories():
    """Create reports directories if they don't exist."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class QualityDashboard:
    """Generate comprehensive quality dashboards from feedback data."""

    def __init__(self, days: int = 30, include_processed: bool = True):
        """
        Initialize dashboard with time range.

        Args:
            days: Number of days to analyze
            include_processed: Whether to include processed feedback
        """
        self.days = days
        self.include_processed = include_processed
        self.entries = self._load_entries()

        # Initialize analyzers
        self.metrics = None
        self.patterns = None
        self.recommendations = None

        if self.entries:
            metrics_calc = MetricsCalculator(self.entries)
            self.metrics = metrics_calc.calculate_all_metrics()

            pattern_detector = PatternDetector(self.entries)
            self.patterns = pattern_detector.detect_all_patterns()

            rec_generator = RecommendationGenerator(
                self.metrics, self.patterns, self.entries
            )
            self.recommendations = rec_generator.generate_all_recommendations()

    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load feedback entries for the time range."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        return load_feedback_by_date_range(
            start_date,
            end_date,
            include_processed=self.include_processed
        )

    def generate_full_report(self) -> Dict[str, Any]:
        """
        Generate a complete quality report.

        Returns:
            Dictionary containing all dashboard data
        """
        if not self.entries:
            return {
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "period_days": self.days,
                "has_data": False,
                "message": "No feedback data available for the specified period"
            }

        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "period_days": self.days,
            "has_data": True,
            "summary": self._generate_summary(),
            "metrics": self.metrics,
            "patterns": self.patterns,
            "recommendations": self.recommendations,
            "pending_recommendations": load_recommendation_queue(),
            "action_items": self._generate_action_items()
        }

    def _generate_summary(self) -> Dict[str, Any]:
        """Generate executive summary."""
        if not self.metrics:
            return {}

        summary = self.metrics.get('summary', {})
        acceptance = self.metrics.get('decision_acceptance', {})
        ratings = self.metrics.get('ratings_by_category', {})
        engagement = self.metrics.get('feedback_engagement', {})
        debates = self.metrics.get('debate_outcomes', {})

        # Determine overall health
        health_score = self._calculate_health_score()

        return {
            "period": {
                "start": summary.get('date_range', {}).get('start'),
                "end": summary.get('date_range', {}).get('end'),
                "days": self.days
            },
            "totals": {
                "feedback_entries": summary.get('total_entries', 0),
                "unique_sessions": summary.get('unique_sessions', 0)
            },
            "key_metrics": {
                "overall_rating": ratings.get('overall_average'),
                "acceptance_rate": acceptance.get('rate'),
                "debate_rate": round(1 - (acceptance.get('rate') or 0), 3),
                "debate_change_rate": debates.get('change_rate'),
                "feedback_response_rate": engagement.get('response_rate')
            },
            "health": health_score
        }

    def _calculate_health_score(self) -> Dict[str, Any]:
        """Calculate overall conversation quality health score."""
        scores = []
        details = []

        # Rating score (0-100)
        avg_rating = self.metrics.get('ratings_by_category', {}).get('overall_average')
        if avg_rating:
            rating_score = (avg_rating / 5) * 100
            scores.append(rating_score)
            details.append(f"Rating: {avg_rating}/5 ({rating_score:.0f}%)")

        # Acceptance rate score
        acceptance_rate = self.metrics.get('decision_acceptance', {}).get('rate')
        if acceptance_rate is not None:
            acceptance_score = acceptance_rate * 100
            scores.append(acceptance_score)
            details.append(f"Acceptance: {acceptance_rate*100:.0f}%")

        # Low debate change rate is good
        change_rate = self.metrics.get('debate_outcomes', {}).get('change_rate')
        if change_rate is not None:
            # Lower is better, invert
            change_score = (1 - change_rate) * 100
            scores.append(change_score)
            details.append(f"Position stability: {change_score:.0f}%")

        # Engagement score
        response_rate = self.metrics.get('feedback_engagement', {}).get('response_rate')
        if response_rate is not None:
            engagement_score = response_rate * 100
            scores.append(engagement_score)
            details.append(f"Engagement: {response_rate*100:.0f}%")

        if not scores:
            return {"score": None, "status": "insufficient_data"}

        overall_score = sum(scores) / len(scores)

        if overall_score >= 80:
            status = "excellent"
        elif overall_score >= 65:
            status = "good"
        elif overall_score >= 50:
            status = "needs_attention"
        else:
            status = "critical"

        return {
            "score": round(overall_score, 1),
            "status": status,
            "details": details
        }

    def _generate_action_items(self) -> List[Dict[str, Any]]:
        """Generate prioritized action items."""
        items = []

        # From recommendations
        if self.recommendations:
            high_priority = [
                r for r in self.recommendations
                if r['priority'] == 'high'
            ]

            for rec in high_priority[:3]:
                items.append({
                    "type": "recommendation",
                    "priority": "high",
                    "action": f"Update {rec['target_skill']}: {rec['section']}",
                    "reason": rec['rationale'],
                    "source": f"recommendation:{rec['id'][:8]}"
                })

        # From patterns
        if self.patterns:
            # Role mismatches
            mismatches = self.patterns.get('role_mismatch', {}).get('mismatched_roles', [])
            for mismatch in mismatches[:2]:
                items.append({
                    "type": "pattern",
                    "priority": "high" if mismatch['gap_from_overall'] > 0.7 else "medium",
                    "action": f"Review role-{mismatch['role']} guidance",
                    "reason": f"Rating gap of {mismatch['gap_from_overall']} from overall",
                    "source": "pattern:role_mismatch"
                })

            # Verbosity calibration
            verbosity = self.patterns.get('verbosity_preference', {})
            if verbosity.get('confidence') == 'high':
                pref = verbosity['detected_preference']
                if pref != 'balanced':
                    items.append({
                        "type": "calibration",
                        "priority": "medium",
                        "action": f"Calibrate to {pref.replace('_', ' ')} communication style",
                        "reason": f"{verbosity['verbose_signals']} verbose vs {verbosity['detail_signals']} detail signals",
                        "source": "pattern:verbosity"
                    })

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(items, key=lambda x: priority_order.get(x['priority'], 3))

    def generate_markdown_report(self) -> str:
        """
        Generate a markdown-formatted quality report.

        Returns:
            Markdown report string
        """
        report = self.generate_full_report()

        if not report.get('has_data'):
            return f"# AID Quality Report\n\n{report.get('message', 'No data available')}"

        lines = []
        lines.append("# AID Conversation Quality Report")
        lines.append(f"**Generated:** {report['generated_at']}")
        lines.append(f"**Period:** Last {report['period_days']} days")
        lines.append("")

        # Summary section
        summary = report.get('summary', {})
        health = summary.get('health', {})

        lines.append("## Executive Summary")
        lines.append("")

        if health.get('score'):
            status_emoji = {
                "excellent": "🟢",
                "good": "🟡",
                "needs_attention": "🟠",
                "critical": "🔴"
            }.get(health['status'], "⚪")

            lines.append(f"### Health Score: {status_emoji} {health['score']}/100 ({health['status'].replace('_', ' ').title()})")
            lines.append("")

        key_metrics = summary.get('key_metrics', {})
        if key_metrics:
            lines.append("### Key Metrics")
            lines.append("")
            lines.append("| Metric | Value |")
            lines.append("|--------|-------|")

            if key_metrics.get('overall_rating'):
                lines.append(f"| Average Rating | {key_metrics['overall_rating']}/5 |")
            if key_metrics.get('acceptance_rate') is not None:
                lines.append(f"| Decision Acceptance | {key_metrics['acceptance_rate']*100:.0f}% |")
            if key_metrics.get('debate_rate') is not None:
                lines.append(f"| Debate Rate | {key_metrics['debate_rate']*100:.0f}% |")
            if key_metrics.get('debate_change_rate') is not None:
                lines.append(f"| Debate Change Rate | {key_metrics['debate_change_rate']*100:.0f}% |")
            if key_metrics.get('feedback_response_rate') is not None:
                lines.append(f"| Feedback Response | {key_metrics['feedback_response_rate']*100:.0f}% |")

            lines.append("")

        totals = summary.get('totals', {})
        if totals:
            lines.append(f"**Total Feedback Entries:** {totals.get('feedback_entries', 0)}")
            lines.append(f"**Unique Sessions:** {totals.get('unique_sessions', 0)}")
            lines.append("")

        # Ratings by category
        ratings = report.get('metrics', {}).get('ratings_by_category', {})
        if ratings.get('by_phase'):
            lines.append("## Ratings by Phase")
            lines.append("")
            lines.append("| Phase | Average | Count |")
            lines.append("|-------|---------|-------|")
            for phase, data in ratings['by_phase'].items():
                lines.append(f"| {phase} | {data['average']} | {data['count']} |")
            lines.append("")

        if ratings.get('by_role'):
            lines.append("## Ratings by Role")
            lines.append("")
            lines.append("| Role | Average | Count |")
            lines.append("|------|---------|-------|")
            for role, data in ratings['by_role'].items():
                lines.append(f"| {role} | {data['average']} | {data['count']} |")
            lines.append("")

        # Weak spots
        weak_spots = ratings.get('weak_spots', [])
        if weak_spots:
            lines.append("## Areas Needing Attention")
            lines.append("")
            for spot in weak_spots:
                lines.append(f"- **{spot['category']}/{spot['value']}**: {spot['average_rating']} avg ({spot['sample_size']} samples)")
            lines.append("")

        # Debate analysis
        debates = report.get('metrics', {}).get('debate_outcomes', {})
        if debates.get('total_debates', 0) > 0:
            lines.append("## Debate Analysis")
            lines.append("")
            lines.append(f"**Total Debates:** {debates['total_debates']}")
            lines.append(f"**Claude Position Held:** {debates['win_rate']*100:.0f}%")
            lines.append(f"**Position Changed:** {debates['change_rate']*100:.0f}%")
            lines.append("")

            topics_by_change = debates.get('topics_by_change_rate', {})
            if topics_by_change:
                lines.append("### Debates by Topic Category")
                lines.append("")
                lines.append("| Category | Debates | Change Rate |")
                lines.append("|----------|---------|-------------|")
                for topic, data in sorted(topics_by_change.items(), key=lambda x: x[1]['change_rate'], reverse=True):
                    lines.append(f"| {topic} | {data['total']} | {data['change_rate']*100:.0f}% |")
                lines.append("")

        # Action items
        action_items = report.get('action_items', [])
        if action_items:
            lines.append("## Action Items")
            lines.append("")
            for i, item in enumerate(action_items, 1):
                priority_emoji = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(item['priority'], "⚪")
                lines.append(f"{i}. {priority_emoji} **{item['action']}**")
                lines.append(f"   - Reason: {item['reason']}")
                lines.append("")

        # Pending recommendations
        pending = report.get('pending_recommendations', [])
        if pending:
            lines.append("## Pending Skill Update Recommendations")
            lines.append("")
            for rec in pending[:5]:
                lines.append(f"- **[{rec['priority'].upper()}]** {rec['target_skill']}: {rec['section']}")
            if len(pending) > 5:
                lines.append(f"- ... and {len(pending) - 5} more")
            lines.append("")

        # Verbosity preference
        verbosity = report.get('patterns', {}).get('verbosity_preference', {})
        if verbosity.get('confidence') in ['high', 'medium']:
            lines.append("## User Preferences Learned")
            lines.append("")
            lines.append(f"- **Communication Style:** {verbosity['detected_preference'].replace('_', ' ').title()} (confidence: {verbosity['confidence']})")
            lines.append("")

        # Trends
        trends = report.get('metrics', {}).get('trends', {})
        if trends.get('sufficient_data'):
            lines.append("## Trends")
            lines.append("")
            lines.append(f"**Overall Trend:** {trends['trend'].title()}")
            lines.append("")

        lines.append("---")
        lines.append(f"*Report generated by AID Learning Mode Sub-Agent*")

        return "\n".join(lines)

    def save_report(self, format: str = "markdown") -> Path:
        """
        Save the report to a file.

        Args:
            format: 'markdown' or 'json'

        Returns:
            Path to saved file
        """
        ensure_directories()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if format == "json":
            filepath = REPORTS_DIR / f"quality-report_{timestamp}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.generate_full_report(), f, indent=2, ensure_ascii=False)
        else:
            filepath = REPORTS_DIR / f"quality-report_{timestamp}.md"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.generate_markdown_report())

        return filepath


def generate_dashboard(days: int = 30) -> str:
    """
    Quick function to generate a dashboard report.

    Args:
        days: Number of days to analyze

    Returns:
        Markdown report string
    """
    dashboard = QualityDashboard(days=days)
    return dashboard.generate_markdown_report()


def save_dashboard(days: int = 30, format: str = "markdown") -> Path:
    """
    Generate and save a dashboard report.

    Args:
        days: Number of days to analyze
        format: 'markdown' or 'json'

    Returns:
        Path to saved report
    """
    dashboard = QualityDashboard(days=days)
    return dashboard.save_report(format=format)


if __name__ == "__main__":
    print("Testing Quality Dashboard...")
    print("=" * 60)

    # Create dashboard (will show "no data" message if no feedback exists)
    dashboard = QualityDashboard(days=30)

    print("\nMarkdown Report:")
    print("-" * 40)
    print(dashboard.generate_markdown_report())

    print("\n" + "=" * 60)
    print("Dashboard generation complete.")
