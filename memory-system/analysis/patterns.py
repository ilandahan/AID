"""
AID Learning Mode Pattern Detection

Identifies patterns in feedback that indicate skill improvement opportunities.
Part of the AID Memory System sub-agent.
"""

from typing import Dict, Any, List, Optional, Tuple
from collections import defaultdict
from datetime import datetime, timedelta
import re
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback.collector import load_pending_feedback, load_feedback_by_date_range


class PatternDetector:
    """Detect patterns in feedback data that indicate improvement opportunities."""

    def __init__(self, feedback_entries: List[Dict[str, Any]]):
        """
        Initialize with feedback entries.

        Args:
            feedback_entries: List of feedback entry dictionaries
        """
        self.entries = feedback_entries

    def detect_all_patterns(self) -> Dict[str, Any]:
        """
        Run all pattern detection algorithms.

        Returns:
            Dictionary containing all detected patterns
        """
        return {
            "repeated_debates": self.detect_repeated_debates(),
            "low_rating_patterns": self.detect_low_rating_patterns(),
            "role_mismatch": self.detect_role_mismatch(),
            "verbosity_preference": self.detect_verbosity_preference(),
            "phase_struggles": self.detect_phase_struggles(),
            "topic_clusters": self.detect_topic_clusters(),
            "feedback_timing": self.detect_feedback_timing_patterns()
        }

    def detect_repeated_debates(self, min_occurrences: int = 3) -> Dict[str, Any]:
        """
        Find topics that repeatedly trigger debates.

        Args:
            min_occurrences: Minimum debates on similar topic to flag

        Returns:
            Pattern detection results
        """
        debate_entries = [
            e for e in self.entries
            if e.get('debate', {}).get('occurred', False)
        ]

        if len(debate_entries) < min_occurrences:
            return {
                "patterns_found": False,
                "reason": "Insufficient debate data"
            }

        # Group debates by topic category
        by_category = defaultdict(list)
        for entry in debate_entries:
            category = entry.get('decision', {}).get('topic_category', 'other')
            topic = entry.get('decision', {}).get('topic', '')
            by_category[category].append({
                "topic": topic,
                "outcome": entry.get('debate', {}).get('outcome'),
                "learning": entry.get('debate', {}).get('learning'),
                "user_challenge": entry.get('debate', {}).get('user_challenge'),
                "timestamp": entry['timestamp']
            })

        # Find categories with repeated debates
        repeated = {}
        for category, debates in by_category.items():
            if len(debates) >= min_occurrences:
                change_count = sum(
                    1 for d in debates
                    if d['outcome'] in ['changed', 'partially_changed']
                )
                repeated[category] = {
                    "debate_count": len(debates),
                    "change_rate": round(change_count / len(debates), 2),
                    "topics": [d['topic'] for d in debates],
                    "learnings": [d['learning'] for d in debates if d['learning']],
                    "action_needed": change_count / len(debates) > 0.5
                }

        # Also cluster by similar topic text
        topic_clusters = self._cluster_similar_topics(debate_entries)

        return {
            "patterns_found": len(repeated) > 0 or len(topic_clusters) > 0,
            "by_category": repeated,
            "topic_clusters": topic_clusters,
            "recommendation": self._generate_debate_recommendation(repeated, topic_clusters)
        }

    def _cluster_similar_topics(
        self,
        entries: List[Dict[str, Any]],
        min_cluster_size: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Cluster debates by similar topic text using simple keyword matching.

        In production, this would use semantic similarity.
        """
        topics = []
        for entry in entries:
            topic = entry.get('decision', {}).get('topic', '')
            if topic:
                topics.append({
                    "topic": topic.lower(),
                    "outcome": entry.get('debate', {}).get('outcome'),
                    "timestamp": entry['timestamp']
                })

        # Simple keyword extraction (production would use NLP)
        keyword_groups = defaultdict(list)
        keywords = [
            'database', 'api', 'architecture', 'testing', 'auth', 'security',
            'cache', 'performance', 'logging', 'error', 'validation', 'schema'
        ]

        for topic_data in topics:
            for keyword in keywords:
                if keyword in topic_data['topic']:
                    keyword_groups[keyword].append(topic_data)
                    break

        # Return clusters with enough members
        clusters = []
        for keyword, items in keyword_groups.items():
            if len(items) >= min_cluster_size:
                change_count = sum(
                    1 for i in items
                    if i['outcome'] in ['changed', 'partially_changed']
                )
                clusters.append({
                    "keyword": keyword,
                    "count": len(items),
                    "change_rate": round(change_count / len(items), 2),
                    "topics": [i['topic'] for i in items]
                })

        return sorted(clusters, key=lambda x: x['count'], reverse=True)

    def _generate_debate_recommendation(
        self,
        by_category: Dict[str, Any],
        clusters: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate recommendation based on debate patterns."""
        high_change_categories = [
            cat for cat, data in by_category.items()
            if data.get('action_needed')
        ]

        high_change_clusters = [
            c['keyword'] for c in clusters
            if c['change_rate'] > 0.5
        ]

        if high_change_categories or high_change_clusters:
            areas = high_change_categories + high_change_clusters
            return f"Review skill guidance for: {', '.join(areas)}. High debate change rates indicate misalignment."

        return None

    def detect_low_rating_patterns(
        self,
        threshold: float = 3.5,
        min_samples: int = 3
    ) -> Dict[str, Any]:
        """
        Find decision types with consistently low ratings.

        Args:
            threshold: Rating threshold for "low"
            min_samples: Minimum samples needed

        Returns:
            Pattern detection results
        """
        rated_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('rating') is not None
        ]

        if len(rated_entries) < min_samples:
            return {
                "patterns_found": False,
                "reason": "Insufficient rated data"
            }

        # Group by topic category
        by_category = defaultdict(list)
        for entry in rated_entries:
            category = entry.get('decision', {}).get('topic_category', 'other')
            by_category[category].append(entry['feedback']['rating'])

        # Find low-rated categories
        low_rated = {}
        for category, ratings in by_category.items():
            if len(ratings) >= min_samples:
                avg = sum(ratings) / len(ratings)
                if avg < threshold:
                    low_rated[category] = {
                        "average_rating": round(avg, 2),
                        "sample_size": len(ratings),
                        "min_rating": min(ratings),
                        "max_rating": max(ratings)
                    }

        return {
            "patterns_found": len(low_rated) > 0,
            "low_rated_categories": low_rated,
            "recommendation": f"Focus improvement on: {', '.join(low_rated.keys())}" if low_rated else None
        }

    def detect_role_mismatch(
        self,
        threshold: float = 3.5,
        min_samples: int = 3
    ) -> Dict[str, Any]:
        """
        Find roles where Claude's guidance doesn't fit well.

        Returns:
            Pattern detection results with role-specific issues
        """
        rated_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('rating') is not None
        ]

        if len(rated_entries) < min_samples:
            return {
                "patterns_found": False,
                "reason": "Insufficient rated data"
            }

        # Group by role
        by_role = defaultdict(list)
        for entry in rated_entries:
            role = entry.get('context', {}).get('role', 'unknown')
            by_role[role].append({
                "rating": entry['feedback']['rating'],
                "verbal": entry.get('feedback', {}).get('verbal'),
                "topic_category": entry.get('decision', {}).get('topic_category'),
                "phase": entry.get('context', {}).get('phase')
            })

        # Calculate averages and find mismatches
        role_stats = {}
        mismatched_roles = []

        overall_ratings = [e['feedback']['rating'] for e in rated_entries]
        overall_avg = sum(overall_ratings) / len(overall_ratings)

        for role, data in by_role.items():
            if len(data) >= min_samples:
                ratings = [d['rating'] for d in data]
                avg = sum(ratings) / len(ratings)
                role_stats[role] = {
                    "average_rating": round(avg, 2),
                    "sample_size": len(ratings),
                    "verbal_feedback_count": sum(1 for d in data if d['verbal']),
                    "below_threshold": avg < threshold,
                    "below_overall": avg < overall_avg - 0.3
                }

                if avg < threshold or avg < overall_avg - 0.5:
                    # Analyze what topics are problematic for this role
                    topic_ratings = defaultdict(list)
                    for d in data:
                        if d['topic_category']:
                            topic_ratings[d['topic_category']].append(d['rating'])

                    weak_topics = [
                        t for t, r in topic_ratings.items()
                        if len(r) >= 2 and sum(r) / len(r) < threshold
                    ]

                    mismatched_roles.append({
                        "role": role,
                        "average_rating": round(avg, 2),
                        "gap_from_overall": round(overall_avg - avg, 2),
                        "weak_topics": weak_topics
                    })

        return {
            "patterns_found": len(mismatched_roles) > 0,
            "role_stats": role_stats,
            "overall_average": round(overall_avg, 2),
            "mismatched_roles": mismatched_roles,
            "recommendation": self._generate_role_recommendation(mismatched_roles)
        }

    def _generate_role_recommendation(
        self,
        mismatched_roles: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate recommendation for role mismatches."""
        if not mismatched_roles:
            return None

        recommendations = []
        for mismatch in mismatched_roles:
            role = mismatch['role']
            weak = mismatch.get('weak_topics', [])
            if weak:
                recommendations.append(
                    f"Update role-{role} guidance for: {', '.join(weak)}"
                )
            else:
                recommendations.append(
                    f"Review role-{role} guidance overall"
                )

        return "; ".join(recommendations)

    def detect_verbosity_preference(self) -> Dict[str, Any]:
        """
        Learn user's verbosity preference from feedback.

        Returns:
            Detected preference and confidence
        """
        verbose_patterns = [
            r'\b(verbose|too long|faster|brief|shorter|lengthy|wordy)\b',
            r'\b(too much|detail|concise|succinct)\b'
        ]
        detail_patterns = [
            r'\b(more detail|explain|why|expand|elaborate)\b',
            r'\b(unclear|confused|more info|don\'t understand)\b'
        ]

        verbal_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('verbal')
        ]

        if len(verbal_entries) < 2:
            return {
                "detected_preference": "unknown",
                "confidence": "low",
                "reason": "Insufficient verbal feedback"
            }

        verbose_signals = 0
        detail_signals = 0
        signal_examples = {"verbose": [], "detail": []}

        for entry in verbal_entries:
            verbal = entry['feedback']['verbal'].lower()

            for pattern in verbose_patterns:
                if re.search(pattern, verbal):
                    verbose_signals += 1
                    signal_examples["verbose"].append(verbal[:100])
                    break

            for pattern in detail_patterns:
                if re.search(pattern, verbal):
                    detail_signals += 1
                    signal_examples["detail"].append(verbal[:100])
                    break

        # Determine preference
        total_signals = verbose_signals + detail_signals

        if total_signals == 0:
            preference = "balanced"
            confidence = "low"
        elif verbose_signals > detail_signals * 2:
            preference = "prefers_concise"
            confidence = "high" if verbose_signals >= 3 else "medium"
        elif detail_signals > verbose_signals * 2:
            preference = "prefers_detailed"
            confidence = "high" if detail_signals >= 3 else "medium"
        else:
            preference = "balanced"
            confidence = "medium"

        return {
            "detected_preference": preference,
            "confidence": confidence,
            "verbose_signals": verbose_signals,
            "detail_signals": detail_signals,
            "sample_size": len(verbal_entries),
            "examples": signal_examples,
            "recommendation": self._generate_verbosity_recommendation(preference, confidence)
        }

    def _generate_verbosity_recommendation(
        self,
        preference: str,
        confidence: str
    ) -> Optional[str]:
        """Generate recommendation for verbosity calibration."""
        if confidence == "low":
            return None

        if preference == "prefers_concise":
            return "Use abbreviated transparency format. Reduce explanation length after initial interactions."
        elif preference == "prefers_detailed":
            return "Use full transparency format. Include detailed rationale and alternatives."

        return None

    def detect_phase_struggles(
        self,
        threshold: float = 3.5,
        min_samples: int = 3
    ) -> Dict[str, Any]:
        """
        Identify phases where users consistently struggle.

        Returns:
            Phase-specific struggle patterns
        """
        rated_entries = [
            e for e in self.entries
            if e.get('feedback', {}).get('rating') is not None
        ]

        if len(rated_entries) < min_samples:
            return {
                "patterns_found": False,
                "reason": "Insufficient data"
            }

        # Group by phase
        by_phase = defaultdict(list)
        for entry in rated_entries:
            phase = entry.get('context', {}).get('phase', 'unknown')
            by_phase[phase].append({
                "rating": entry['feedback']['rating'],
                "topic_category": entry.get('decision', {}).get('topic_category'),
                "had_debate": entry.get('debate', {}).get('occurred', False)
            })

        # Analyze each phase
        phase_analysis = {}
        struggling_phases = []

        for phase, data in by_phase.items():
            if len(data) >= min_samples:
                ratings = [d['rating'] for d in data]
                avg = sum(ratings) / len(ratings)
                debate_rate = sum(1 for d in data if d['had_debate']) / len(data)

                phase_analysis[phase] = {
                    "average_rating": round(avg, 2),
                    "sample_size": len(ratings),
                    "debate_rate": round(debate_rate, 2)
                }

                if avg < threshold:
                    # Find problematic topics in this phase
                    topic_ratings = defaultdict(list)
                    for d in data:
                        if d['topic_category']:
                            topic_ratings[d['topic_category']].append(d['rating'])

                    weak_topics = [
                        t for t, r in topic_ratings.items()
                        if len(r) >= 2 and sum(r) / len(r) < threshold
                    ]

                    struggling_phases.append({
                        "phase": phase,
                        "average_rating": round(avg, 2),
                        "weak_topics": weak_topics,
                        "high_debate_rate": debate_rate > 0.4
                    })

        return {
            "patterns_found": len(struggling_phases) > 0,
            "phase_analysis": phase_analysis,
            "struggling_phases": struggling_phases,
            "recommendation": self._generate_phase_recommendation(struggling_phases)
        }

    def _generate_phase_recommendation(
        self,
        struggling_phases: List[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate recommendations for struggling phases."""
        if not struggling_phases:
            return None

        recommendations = []
        for phase_data in struggling_phases:
            phase = phase_data['phase']
            weak = phase_data.get('weak_topics', [])
            if weak:
                recommendations.append(
                    f"aid-{phase.split('-')[1] if '-' in phase else phase}: improve guidance for {', '.join(weak)}"
                )
            elif phase_data.get('high_debate_rate'):
                recommendations.append(
                    f"aid-{phase.split('-')[1] if '-' in phase else phase}: high debate rate - clarify default recommendations"
                )

        return "; ".join(recommendations) if recommendations else None

    def detect_topic_clusters(self) -> Dict[str, Any]:
        """
        Identify common topic patterns across all feedback.

        Returns:
            Topic clustering analysis
        """
        all_topics = []
        for entry in self.entries:
            topic = entry.get('decision', {}).get('topic')
            category = entry.get('decision', {}).get('topic_category')
            if topic:
                all_topics.append({
                    "topic": topic,
                    "category": category,
                    "rating": entry.get('feedback', {}).get('rating'),
                    "had_debate": entry.get('debate', {}).get('occurred', False)
                })

        if len(all_topics) < 3:
            return {
                "patterns_found": False,
                "reason": "Insufficient topic data"
            }

        # Analyze by category
        category_stats = defaultdict(lambda: {
            "count": 0,
            "ratings": [],
            "debate_count": 0
        })

        for topic in all_topics:
            cat = topic['category'] or 'other'
            category_stats[cat]["count"] += 1
            if topic['rating']:
                category_stats[cat]["ratings"].append(topic['rating'])
            if topic['had_debate']:
                category_stats[cat]["debate_count"] += 1

        # Calculate metrics for each category
        analysis = {}
        for cat, stats in category_stats.items():
            if stats['count'] >= 2:
                avg_rating = (
                    sum(stats['ratings']) / len(stats['ratings'])
                    if stats['ratings'] else None
                )
                analysis[cat] = {
                    "count": stats['count'],
                    "average_rating": round(avg_rating, 2) if avg_rating else None,
                    "debate_rate": round(stats['debate_count'] / stats['count'], 2)
                }

        return {
            "patterns_found": len(analysis) > 0,
            "category_analysis": analysis,
            "most_common": sorted(analysis.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
        }

    def detect_feedback_timing_patterns(self) -> Dict[str, Any]:
        """
        Analyze when users provide vs skip feedback.

        Returns:
            Timing pattern analysis
        """
        entries_with_timing = [
            e for e in self.entries
            if e.get('metadata', {}).get('time_to_feedback') is not None
        ]

        if len(entries_with_timing) < 5:
            return {
                "patterns_found": False,
                "reason": "Insufficient timing data"
            }

        # Analyze timing
        timings = [e['metadata']['time_to_feedback'] for e in entries_with_timing]

        # Group by whether feedback was skipped
        skipped_timings = [
            e['metadata']['time_to_feedback']
            for e in entries_with_timing
            if e.get('feedback', {}).get('skipped', True)
        ]

        provided_timings = [
            e['metadata']['time_to_feedback']
            for e in entries_with_timing
            if not e.get('feedback', {}).get('skipped', True)
        ]

        analysis = {
            "average_time_overall": round(sum(timings) / len(timings), 1),
            "min_time": min(timings),
            "max_time": max(timings)
        }

        if skipped_timings:
            analysis["average_time_skipped"] = round(
                sum(skipped_timings) / len(skipped_timings), 1
            )

        if provided_timings:
            analysis["average_time_provided"] = round(
                sum(provided_timings) / len(provided_timings), 1
            )

        return {
            "patterns_found": True,
            "timing_analysis": analysis,
            "sample_size": len(entries_with_timing)
        }


def detect_patterns_from_pending() -> Dict[str, Any]:
    """
    Run pattern detection on all pending feedback.

    Returns:
        All detected patterns
    """
    entries = load_pending_feedback()
    detector = PatternDetector(entries)
    return detector.detect_all_patterns()


def detect_patterns_for_period(
    days: int = 30,
    include_processed: bool = True
) -> Dict[str, Any]:
    """
    Run pattern detection for a specific time period.

    Args:
        days: Number of days to look back
        include_processed: Whether to include processed feedback

    Returns:
        All detected patterns
    """
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    entries = load_feedback_by_date_range(
        start_date,
        end_date,
        include_processed=include_processed
    )

    detector = PatternDetector(entries)
    return detector.detect_all_patterns()


if __name__ == "__main__":
    # Test with sample data
    print("Testing Pattern Detector...")

    sample_entries = [
        {
            "id": "1", "timestamp": "2024-01-15T10:00:00Z", "session_id": "s1",
            "context": {"phase": "2-tech-spec", "role": "developer", "interaction_type": "decision"},
            "decision": {"topic": "Database selection", "topic_category": "technology"},
            "debate": {"occurred": True, "outcome": "changed", "learning": "Team prefers PostgreSQL"},
            "feedback": {"rating": 4, "verbal": "Good discussion", "skipped": False}
        },
        {
            "id": "2", "timestamp": "2024-01-16T10:00:00Z", "session_id": "s2",
            "context": {"phase": "2-tech-spec", "role": "developer", "interaction_type": "decision"},
            "decision": {"topic": "Database choice for users", "topic_category": "technology"},
            "debate": {"occurred": True, "outcome": "changed", "learning": "ACID needed"},
            "feedback": {"rating": 4, "verbal": "Too verbose, be more concise", "skipped": False}
        },
        {
            "id": "3", "timestamp": "2024-01-17T10:00:00Z", "session_id": "s3",
            "context": {"phase": "4-development", "role": "pm", "interaction_type": "review"},
            "decision": {"topic": "Testing approach", "topic_category": "testing"},
            "debate": {"occurred": False},
            "feedback": {"rating": 2, "verbal": "Too technical for PM", "skipped": False}
        },
        {
            "id": "4", "timestamp": "2024-01-18T10:00:00Z", "session_id": "s4",
            "context": {"phase": "4-development", "role": "pm", "interaction_type": "decision"},
            "decision": {"topic": "Sprint scope", "topic_category": "scope"},
            "debate": {"occurred": False},
            "feedback": {"rating": 3, "verbal": None, "skipped": False}
        }
    ]

    detector = PatternDetector(sample_entries)
    patterns = detector.detect_all_patterns()

    import json
    print("\nDetected Patterns:")
    print(json.dumps(patterns, indent=2, default=str))
