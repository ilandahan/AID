"""
AID Learning Mode Recommendation Generator

Generates skill update recommendations based on detected patterns.
Part of the AID Memory System sub-agent.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Support both relative imports (when used as package) and direct imports (when used standalone)
try:
    from ..analysis.metrics import MetricsCalculator
    from ..analysis.patterns import PatternDetector
    from ..feedback.collector import load_pending_feedback, load_feedback_by_date_range
except ImportError:
    from analysis.metrics import MetricsCalculator
    from analysis.patterns import PatternDetector
    from feedback.collector import load_pending_feedback, load_feedback_by_date_range

# Configuration
RECOMMENDATIONS_DIR = Path(os.path.expanduser("~/.aid/recommendations"))
QUEUE_FILE = RECOMMENDATIONS_DIR / "queue.json"
APPLIED_FILE = RECOMMENDATIONS_DIR / "applied.json"


def ensure_directories():
    """Create recommendations directories if they don't exist."""
    RECOMMENDATIONS_DIR.mkdir(parents=True, exist_ok=True)


class RecommendationGenerator:
    """Generate skill update recommendations from metrics and patterns."""

    def __init__(
        self,
        metrics: Dict[str, Any],
        patterns: Dict[str, Any],
        feedback_entries: List[Dict[str, Any]]
    ):
        """
        Initialize with analysis results.

        Args:
            metrics: Results from MetricsCalculator
            patterns: Results from PatternDetector
            feedback_entries: Original feedback entries
        """
        self.metrics = metrics
        self.patterns = patterns
        self.entries = feedback_entries

    def generate_all_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate all recommendations from analysis results.

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # From debate patterns
        recommendations.extend(self._recommendations_from_debates())

        # From rating patterns
        recommendations.extend(self._recommendations_from_ratings())

        # From role mismatches
        recommendations.extend(self._recommendations_from_roles())

        # From verbosity signals
        recommendations.extend(self._recommendations_from_verbosity())

        # From phase struggles
        recommendations.extend(self._recommendations_from_phases())

        # Deduplicate and prioritize
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations = self._prioritize_recommendations(recommendations)

        return recommendations

    def _recommendations_from_debates(self) -> List[Dict[str, Any]]:
        """Generate recommendations from debate patterns."""
        recommendations = []
        debate_patterns = self.patterns.get('repeated_debates', {})

        if not debate_patterns.get('patterns_found'):
            return recommendations

        # From category-based debates
        for category, data in debate_patterns.get('by_category', {}).items():
            if data.get('action_needed'):
                recommendations.append(self._create_recommendation(
                    priority="high" if data['change_rate'] > 0.6 else "medium",
                    target_skill=self._category_to_skill(category),
                    section=f"{category.title()} Guidance",
                    current_guidance=f"Current {category} recommendations",
                    proposed_change=self._generate_debate_change(category, data),
                    rationale=f"{data['debate_count']} debates on {category} with {data['change_rate']*100:.0f}% change rate",
                    supporting_data={
                        "debate_count": data['debate_count'],
                        "change_rate": data['change_rate'],
                        "topics": data['topics'][:5],
                        "learnings": data['learnings'][:3]
                    }
                ))

        # From topic clusters
        for cluster in debate_patterns.get('topic_clusters', []):
            if cluster['change_rate'] > 0.5 and cluster['count'] >= 3:
                recommendations.append(self._create_recommendation(
                    priority="medium",
                    target_skill=self._keyword_to_skill(cluster['keyword']),
                    section=f"{cluster['keyword'].title()} Decisions",
                    current_guidance=f"Current guidance for {cluster['keyword']} decisions",
                    proposed_change=f"Review and update guidance for {cluster['keyword']}-related decisions. "
                                   f"Consider adding: 'Check existing project patterns before recommending.'",
                    rationale=f"{cluster['count']} debates on {cluster['keyword']} topics with {cluster['change_rate']*100:.0f}% change rate",
                    supporting_data={
                        "debate_count": cluster['count'],
                        "change_rate": cluster['change_rate'],
                        "topics": cluster['topics']
                    }
                ))

        return recommendations

    def _recommendations_from_ratings(self) -> List[Dict[str, Any]]:
        """Generate recommendations from rating patterns."""
        recommendations = []
        rating_patterns = self.patterns.get('low_rating_patterns', {})

        if not rating_patterns.get('patterns_found'):
            return recommendations

        for category, data in rating_patterns.get('low_rated_categories', {}).items():
            recommendations.append(self._create_recommendation(
                priority="high" if data['average_rating'] < 3.0 else "medium",
                target_skill=self._category_to_skill(category),
                section=f"{category.title()} Quality",
                current_guidance=f"Current {category} guidance",
                proposed_change=f"Improve {category} guidance to address low satisfaction. "
                               f"Focus on clarity and actionability.",
                rationale=f"Average rating of {data['average_rating']} for {category} "
                         f"({data['sample_size']} samples) is below threshold",
                supporting_data={
                    "average_rating": data['average_rating'],
                    "sample_size": data['sample_size'],
                    "min_rating": data['min_rating'],
                    "max_rating": data['max_rating']
                }
            ))

        return recommendations

    def _recommendations_from_roles(self) -> List[Dict[str, Any]]:
        """Generate recommendations from role mismatch patterns."""
        recommendations = []
        role_patterns = self.patterns.get('role_mismatch', {})

        if not role_patterns.get('patterns_found'):
            return recommendations

        for mismatch in role_patterns.get('mismatched_roles', []):
            role = mismatch['role']
            weak_topics = mismatch.get('weak_topics', [])

            if weak_topics:
                change = f"Update guidance for {', '.join(weak_topics)} to be more appropriate for {role} role. "
                if role == 'pm':
                    change += "Focus on business impact over technical details."
                elif role == 'qa':
                    change += "Focus on testability and coverage."
                elif role == 'tech-lead':
                    change += "Include architectural implications."
            else:
                change = f"Review overall guidance tone and content for {role} role."

            recommendations.append(self._create_recommendation(
                priority="high" if mismatch['gap_from_overall'] > 0.7 else "medium",
                target_skill=f"role-{role}",
                section="Role-Specific Guidance",
                current_guidance=f"Current guidance for {role}",
                proposed_change=change,
                rationale=f"{role} role rated {mismatch['average_rating']} vs overall {role_patterns['overall_average']} "
                         f"(gap: {mismatch['gap_from_overall']})",
                supporting_data={
                    "role": role,
                    "average_rating": mismatch['average_rating'],
                    "overall_average": role_patterns['overall_average'],
                    "gap": mismatch['gap_from_overall'],
                    "weak_topics": weak_topics
                }
            ))

        return recommendations

    def _recommendations_from_verbosity(self) -> List[Dict[str, Any]]:
        """Generate recommendations from verbosity signals."""
        recommendations = []
        verbosity = self.patterns.get('verbosity_preference', {})

        if verbosity.get('confidence') not in ['high', 'medium']:
            return recommendations

        preference = verbosity.get('detected_preference')

        if preference == 'prefers_concise':
            recommendations.append(self._create_recommendation(
                priority="medium",
                target_skill="learning-mode",
                section="Transparency Format",
                current_guidance="Use full transparency format by default",
                proposed_change="After 2-3 interactions, switch to abbreviated format unless topic is novel. "
                               "Lead with decision, follow with brief rationale.",
                rationale=f"{verbosity['verbose_signals']} verbose complaints vs {verbosity['detail_signals']} detail requests",
                supporting_data={
                    "verbose_complaints": verbosity['verbose_signals'],
                    "detail_requests": verbosity['detail_signals'],
                    "confidence": verbosity['confidence'],
                    "examples": verbosity.get('examples', {}).get('verbose', [])[:2]
                }
            ))

        elif preference == 'prefers_detailed':
            recommendations.append(self._create_recommendation(
                priority="medium",
                target_skill="learning-mode",
                section="Transparency Format",
                current_guidance="Current transparency approach",
                proposed_change="Always use full transparency format. "
                               "Include detailed rationale and all alternatives considered.",
                rationale=f"{verbosity['detail_requests']} detail requests vs {verbosity['verbose_signals']} verbose complaints",
                supporting_data={
                    "verbose_complaints": verbosity['verbose_signals'],
                    "detail_requests": verbosity['detail_signals'],
                    "confidence": verbosity['confidence'],
                    "examples": verbosity.get('examples', {}).get('detail', [])[:2]
                }
            ))

        return recommendations

    def _recommendations_from_phases(self) -> List[Dict[str, Any]]:
        """Generate recommendations from phase struggle patterns."""
        recommendations = []
        phase_patterns = self.patterns.get('phase_struggles', {})

        if not phase_patterns.get('patterns_found'):
            return recommendations

        for phase_data in phase_patterns.get('struggling_phases', []):
            phase = phase_data['phase']
            phase_name = phase.split('-')[1] if '-' in phase else phase

            weak_topics = phase_data.get('weak_topics', [])

            if weak_topics:
                change = f"Improve guidance for {', '.join(weak_topics)} in this phase."
            elif phase_data.get('high_debate_rate'):
                change = "Clarify default recommendations. High debate rate suggests unclear guidance."
            else:
                change = "Review phase deliverables and expectations."

            recommendations.append(self._create_recommendation(
                priority="high" if phase_data['average_rating'] < 3.0 else "medium",
                target_skill=f"aid-{phase_name}",
                section="Phase Guidance",
                current_guidance=f"Current guidance for {phase_name} phase",
                proposed_change=change,
                rationale=f"Phase {phase_name} averaging {phase_data['average_rating']} rating",
                supporting_data={
                    "phase": phase,
                    "average_rating": phase_data['average_rating'],
                    "weak_topics": weak_topics,
                    "high_debate_rate": phase_data.get('high_debate_rate', False)
                }
            ))

        return recommendations

    def _create_recommendation(
        self,
        priority: str,
        target_skill: str,
        section: str,
        current_guidance: str,
        proposed_change: str,
        rationale: str,
        supporting_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a recommendation dictionary."""
        return {
            "id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "priority": priority,
            "target_skill": target_skill,
            "section": section,
            "current_guidance": current_guidance,
            "proposed_change": proposed_change,
            "rationale": rationale,
            "supporting_data": supporting_data,
            "auto_apply": False,
            "requires_review": True,
            "status": "pending"
        }

    def _category_to_skill(self, category: str) -> str:
        """Map a topic category to a skill name."""
        mapping = {
            "architecture": "system-architect",
            "technology": "aid-tech-spec",
            "testing": "test-driven",
            "security": "code-review",
            "scope": "aid-prd",
            "performance": "aid-development",
            "process": "phase-enforcement"
        }
        return mapping.get(category, "aid-development")

    def _keyword_to_skill(self, keyword: str) -> str:
        """Map a topic keyword to a skill name."""
        mapping = {
            "database": "aid-tech-spec",
            "api": "aid-tech-spec",
            "architecture": "system-architect",
            "testing": "test-driven",
            "auth": "code-review",
            "security": "code-review",
            "cache": "aid-tech-spec",
            "performance": "aid-development",
            "logging": "aid-development",
            "error": "code-review",
            "validation": "code-review",
            "schema": "aid-tech-spec"
        }
        return mapping.get(keyword, "aid-development")

    def _generate_debate_change(
        self,
        category: str,
        data: Dict[str, Any]
    ) -> str:
        """Generate proposed change text from debate data."""
        learnings = data.get('learnings', [])

        if learnings:
            # Incorporate specific learnings
            learning_text = "; ".join(learnings[:2])
            return f"Update {category} guidance based on learned preferences: {learning_text}. " \
                   f"Add: 'Check existing project patterns and team preferences before recommending.'"

        return f"Review {category} guidance. High debate change rate ({data['change_rate']*100:.0f}%) " \
               f"suggests recommendations don't match user expectations. " \
               f"Consider adding more context checks."

    def _deduplicate_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate recommendations for the same skill/section."""
        seen = set()
        unique = []

        for rec in recommendations:
            key = (rec['target_skill'], rec['section'])
            if key not in seen:
                seen.add(key)
                unique.append(rec)

        return unique

    def _prioritize_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Sort recommendations by priority."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(
            recommendations,
            key=lambda x: priority_order.get(x['priority'], 3)
        )


def save_recommendations(recommendations: List[Dict[str, Any]]) -> Path:
    """
    Save recommendations to the queue file.

    Args:
        recommendations: List of recommendations

    Returns:
        Path to the queue file
    """
    ensure_directories()

    # Load existing queue
    existing = []
    if QUEUE_FILE.exists():
        with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
            existing = json.load(f)

    # Merge (avoid duplicates by ID)
    existing_ids = {r['id'] for r in existing}
    for rec in recommendations:
        if rec['id'] not in existing_ids:
            existing.append(rec)

    # Save updated queue
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    return QUEUE_FILE


def load_recommendation_queue() -> List[Dict[str, Any]]:
    """
    Load pending recommendations from the queue.

    Returns:
        List of pending recommendations
    """
    ensure_directories()

    if not QUEUE_FILE.exists():
        return []

    with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def mark_recommendation_applied(rec_id: str) -> bool:
    """
    Mark a recommendation as applied.

    Args:
        rec_id: ID of the recommendation

    Returns:
        True if successful
    """
    ensure_directories()

    # Load queue
    queue = load_recommendation_queue()

    # Find and remove from queue
    rec = None
    for i, r in enumerate(queue):
        if r['id'] == rec_id:
            rec = queue.pop(i)
            rec['status'] = 'applied'
            rec['applied_at'] = datetime.utcnow().isoformat() + "Z"
            break

    if not rec:
        return False

    # Save updated queue
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    # Add to applied
    applied = []
    if APPLIED_FILE.exists():
        with open(APPLIED_FILE, 'r', encoding='utf-8') as f:
            applied = json.load(f)

    applied.append(rec)

    with open(APPLIED_FILE, 'w', encoding='utf-8') as f:
        json.dump(applied, f, indent=2, ensure_ascii=False)

    return True


def generate_recommendations_from_feedback(
    days: int = 30,
    include_processed: bool = True
) -> List[Dict[str, Any]]:
    """
    Full pipeline: load feedback, analyze, and generate recommendations.

    Args:
        days: Number of days to analyze
        include_processed: Whether to include processed feedback

    Returns:
        List of generated recommendations
    """
    from datetime import timedelta

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Load feedback
    entries = load_feedback_by_date_range(
        start_date,
        end_date,
        include_processed=include_processed
    )

    if not entries:
        return []

    # Calculate metrics
    metrics_calc = MetricsCalculator(entries)
    metrics = metrics_calc.calculate_all_metrics()

    # Detect patterns
    pattern_detector = PatternDetector(entries)
    patterns = pattern_detector.detect_all_patterns()

    # Generate recommendations
    generator = RecommendationGenerator(metrics, patterns, entries)
    recommendations = generator.generate_all_recommendations()

    # Save to queue
    if recommendations:
        save_recommendations(recommendations)

    return recommendations


def save_recommendation(recommendation: Dict[str, Any]) -> Path:
    """
    Save a single recommendation to the queue file.

    Args:
        recommendation: Single recommendation

    Returns:
        Path to the queue file
    """
    return save_recommendations([recommendation])


def approve_recommendation(rec_id: str) -> bool:
    """
    Approve and apply a recommendation.

    Args:
        rec_id: ID of the recommendation

    Returns:
        True if successful
    """
    return mark_recommendation_applied(rec_id)


def reject_recommendation(rec_id: str) -> bool:
    """
    Reject a recommendation (remove from queue without applying).

    Args:
        rec_id: ID of the recommendation

    Returns:
        True if successful
    """
    ensure_directories()

    # Load queue
    queue = load_recommendation_queue()

    # Find and remove from queue
    for i, r in enumerate(queue):
        if r['id'] == rec_id:
            queue.pop(i)
            break
    else:
        return False

    # Save updated queue
    with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)

    return True


def format_recommendations_report(recommendations: List[Dict[str, Any]]) -> str:
    """
    Format recommendations as a human-readable report.

    Args:
        recommendations: List of recommendations

    Returns:
        Formatted report string
    """
    if not recommendations:
        return "No recommendations generated."

    lines = []
    lines.append("=" * 60)
    lines.append("SKILL UPDATE RECOMMENDATIONS")
    lines.append("=" * 60)
    lines.append("")

    # Group by priority
    by_priority = {"high": [], "medium": [], "low": []}
    for rec in recommendations:
        by_priority[rec['priority']].append(rec)

    for priority in ["high", "medium", "low"]:
        if by_priority[priority]:
            lines.append(f"## {priority.upper()} Priority")
            lines.append("")

            for rec in by_priority[priority]:
                lines.append(f"### {rec['target_skill']} - {rec['section']}")
                lines.append(f"ID: {rec['id'][:8]}")
                lines.append(f"")
                lines.append(f"**Current:** {rec['current_guidance']}")
                lines.append(f"")
                lines.append(f"**Proposed:** {rec['proposed_change']}")
                lines.append(f"")
                lines.append(f"**Rationale:** {rec['rationale']}")
                lines.append(f"")

                data = rec['supporting_data']
                if data:
                    lines.append("**Supporting Data:**")
                    for key, value in data.items():
                        if isinstance(value, list):
                            lines.append(f"  - {key}: {', '.join(str(v) for v in value[:3])}")
                        else:
                            lines.append(f"  - {key}: {value}")
                    lines.append("")

                lines.append("-" * 40)
                lines.append("")

    lines.append("=" * 60)
    lines.append(f"Total Recommendations: {len(recommendations)}")
    lines.append(f"  High: {len(by_priority['high'])}")
    lines.append(f"  Medium: {len(by_priority['medium'])}")
    lines.append(f"  Low: {len(by_priority['low'])}")

    return "\n".join(lines)


if __name__ == "__main__":
    print("Testing Recommendation Generator...")

    # Create sample data
    sample_metrics = {
        "decision_acceptance": {"rate": 0.65, "total_decisions": 20, "debated": 7},
        "debate_outcomes": {"change_rate": 0.57},
        "ratings_by_category": {"overall_average": 3.8}
    }

    sample_patterns = {
        "repeated_debates": {
            "patterns_found": True,
            "by_category": {
                "technology": {
                    "action_needed": True,
                    "debate_count": 5,
                    "change_rate": 0.6,
                    "topics": ["Database", "Cache", "API"],
                    "learnings": ["Team prefers PostgreSQL", "Redis for session"]
                }
            },
            "topic_clusters": []
        },
        "role_mismatch": {
            "patterns_found": True,
            "overall_average": 4.0,
            "mismatched_roles": [
                {
                    "role": "pm",
                    "average_rating": 3.2,
                    "gap_from_overall": 0.8,
                    "weak_topics": ["testing", "architecture"]
                }
            ]
        },
        "verbosity_preference": {
            "detected_preference": "prefers_concise",
            "confidence": "high",
            "verbose_signals": 5,
            "detail_signals": 1
        },
        "low_rating_patterns": {"patterns_found": False},
        "phase_struggles": {"patterns_found": False}
    }

    generator = RecommendationGenerator(sample_metrics, sample_patterns, [])
    recommendations = generator.generate_all_recommendations()

    print("\nGenerated Recommendations:")
    print(format_recommendations_report(recommendations))
