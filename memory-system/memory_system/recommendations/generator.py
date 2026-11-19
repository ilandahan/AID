"""
AID Learning Mode Recommendation Generator

Generates skill update recommendations based on detected patterns.
Part of the AID Memory System sub-agent.
"""

import hashlib
import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Support both relative imports (when used as package) and direct imports (when used standalone)
try:
    from ..analysis.metrics import MetricsCalculator
    from ..analysis.patterns import PatternDetector
    from ..feedback.collector import load_pending_feedback, load_feedback_by_date_range, default_names
    from .. import paths
    from ..redact import redact_obj
except ImportError:
    from analysis.metrics import MetricsCalculator
    from analysis.patterns import PatternDetector
    from feedback.collector import load_pending_feedback, load_feedback_by_date_range, default_names
    import paths
    from redact import redact_obj

# T8-2 (D3): an approved proposal may only APPEND to one of these learnings files, inside
# this plugin's own skills/memory-system/references/. Nothing else is ever written.
REFS_ROOT = Path(__file__).resolve().parents[3] / "skills" / "memory-system" / "references"
_TARGET = re.compile(r"^(roles|phases)/([a-z0-9-]+)/cumulative\.md$")
_ROLE_DIRS = {"pm": "product-manager", "product-manager": "product-manager", "qa": "qa-engineer",
              "qa-engineer": "qa-engineer", "lead": "tech-lead", "tech-lead": "tech-lead",
              "developer": "developer", "dev": "developer", "data-scientist": "data-scientist"}
_PHASE_DIRS = ("discovery", "prd", "tech-spec", "breakdown", "development", "qa-ship")


# Configuration. T8-3: from paths.aid_home() on every call ($AID_HOME, else ~/.aid).
def _queue_file() -> Path:
    return paths.recommendations_dir() / "queue.json"


def _applied_file() -> Path:
    return paths.recommendations_dir() / "applied.json"


def _rejected_file() -> Path:
    return paths.recommendations_dir() / "rejected.json"


def _read_list(path: Path) -> List[Dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def _write_list(path: Path, data: List[Dict[str, Any]]):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def ensure_directories():
    """Create recommendations directories if they don't exist."""
    paths.recommendations_dir().mkdir(parents=True, exist_ok=True)


def target_for(target_skill: str) -> Optional[str]:
    """The learnings file a recommendation may be applied to, or None (a skill-wide
    recommendation is shown to the user but cannot be applied by the tool)."""
    t = str(target_skill or "")
    if t.startswith("role-") and t[5:] in _ROLE_DIRS:
        return "roles/{}/cumulative.md".format(_ROLE_DIRS[t[5:]])
    if t.startswith("aid-") and t[4:] in _PHASE_DIRS:
        return "phases/{}/cumulative.md".format(t[4:])
    return None


def resolve_target(rel: Any, refs_root: Optional[Path] = None) -> Optional[Path]:
    """The real file for an allowed relative target, or None. Allowed: exactly
    ``roles|phases/<name>/cumulative.md`` that exists under the references root, after
    resolving symlinks (no ``..``, no absolute path, no other file)."""
    root = (refs_root or REFS_ROOT).resolve()
    if not isinstance(rel, str):
        return None
    rel = rel.replace("\\", "/")
    prefix = "skills/memory-system/references/"
    if rel.startswith(prefix):
        rel = rel[len(prefix):]
    if not _TARGET.match(rel):
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.is_file() else None


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
                rationale=f"{verbosity.get('detail_signals', 0)} detail requests vs {verbosity.get('verbose_signals', 0)} verbose complaints",
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
        """Create a recommendation dictionary: redacted (T8-1), with an id derived from its
        content so the same recommendation is queued once however often it is generated."""
        rec = redact_obj({
            "priority": priority,
            "target_skill": target_skill,
            "target_file": target_for(target_skill),
            "section": section,
            "current_guidance": current_guidance,
            "proposed_change": proposed_change,
            "rationale": rationale,
            "supporting_data": supporting_data,
        }, default_names())
        rec["id"] = _content_id(rec)
        rec.update({"generated_at": datetime.utcnow().isoformat() + "Z", "auto_apply": False,
                    "requires_review": True, "status": "pending"})
        return rec

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
    Add recommendations to the queue, once each (by id), redacted (T8-4). An id that was
    already applied or rejected is not queued again.
    """
    queue = _read_list(_queue_file())
    known = queue + _read_list(_applied_file()) + _read_list(_rejected_file())
    # T15-30: an entry stored under its pre-T15 id still counts as seen under its new id.
    seen = {r.get("id") for r in known} | {_content_id(r) for r in known if _id_matches_content(r)}
    for rec in recommendations:
        if isinstance(rec, dict) and rec.get("id") and rec["id"] not in seen:
            queue.append(redact_obj(rec, default_names(), skip_keys=("id", "generated_at")))
            seen.add(rec["id"])
    _write_list(_queue_file(), queue)
    return _queue_file()


def load_recommendation_queue() -> List[Dict[str, Any]]:
    """Pending recommendations. Reading creates nothing."""
    return _read_list(_queue_file())


def _find(queue: List[Dict[str, Any]], rec_id: str) -> Optional[int]:
    """Index of the one queued recommendation whose id is ``rec_id`` or starts with it (8+
    characters, as the report prints). None when missing or ambiguous."""
    rec_id = str(rec_id or "")
    if len(rec_id) < 8:
        return None
    hits = [i for i, r in enumerate(queue) if str(r.get("id", "")).startswith(rec_id)]
    return hits[0] if len(hits) == 1 else None


def apply_recommendation(rec_id: str, refs_root: Optional[Path] = None) -> Dict[str, Any]:
    """
    T8-2 (D3): append ONE queued recommendation to its learnings file and move it to
    applied.json. Called only through ``aid_session.py memory-apply``, which Claude Code
    asks the user to confirm. Refuses (``ok`` False, nothing changed) an unknown id or a
    recommendation without an allowed target.
    """
    queue = load_recommendation_queue()
    i = _find(queue, rec_id)
    if i is None:
        return {"ok": False, "reason": "no single queued recommendation has id {!r}".format(rec_id)}
    rec = queue[i]
    path = resolve_target(rec.get("target_file"), refs_root)
    if path is None:
        return {"ok": False, "reason": "recommendation {} has no allowed target (only "
                "skills/memory-system/references/roles|phases/<name>/cumulative.md); apply it "
                "by hand if you want it".format(rec.get("id"))}
    if not _id_matches_content(rec):
        return {"ok": False, "reason": "recommendation {!r} does not match its content (the queue "
                "was edited); run memory-preview and confirm the id it shows".format(rec.get("id"))}
    clean = redact_obj(rec, default_names(), skip_keys=("id", "generated_at"))
    block = "\n## Applied learning ({}, recommendation {})\n\n- {}\n  - Why: {}\n".format(
        datetime.utcnow().strftime("%Y-%m-%d"), clean["id"], _one_line(clean.get("proposed_change")),
        _one_line(clean.get("rationale")))
    with open(path, "a", encoding="utf-8", newline="") as f:
        f.write(block)
    queue.pop(i)
    clean.update({"status": "applied", "applied_at": datetime.utcnow().isoformat() + "Z"})
    _write_list(_queue_file(), queue)
    _write_list(_applied_file(), _read_list(_applied_file()) + [clean])
    return {"ok": True, "id": clean.get("id"), "target": str(rec.get("target_file"))}


def _content_key(rec: Dict[str, Any]) -> bytes:
    return "|".join(str(rec.get(k)) for k in
                    ("target_skill", "target_file", "section", "proposed_change",
                     "rationale")).encode("utf-8")


def _content_id(rec: Dict[str, Any]) -> str:
    """The id a recommendation's CONTENT gives it. memory-apply checks it, so the id the user
    confirms in Claude Code's prompt fixes exactly what is appended: the target file and
    both texts that are written (T8 review r1 and r2). T15-30: sha256, 32 hex chars."""
    return hashlib.sha256(_content_key(rec)).hexdigest()[:32]


def _legacy_content_id(rec: Dict[str, Any]) -> str:
    """The pre-T15 id (SHA-1, 16 hex chars). Only READ, so entries queued before T15 can
    still be applied or rejected; new ids are never made this way."""
    return hashlib.sha1(_content_key(rec), usedforsecurity=False).hexdigest()[:16]


def _id_matches_content(rec: Dict[str, Any]) -> bool:
    rec_id = rec.get("id")
    return rec_id == _content_id(rec) or rec_id == _legacy_content_id(rec)


def _one_line(value: Any) -> str:
    """Plain text on one line: no newlines and no leading Markdown heading, quote or list
    marks, so an applied proposal cannot add headings or structure to a learnings file."""
    text = " ".join(str(value if value is not None else "").split())
    return re.sub(r"^[#>*+\s-]+", "", text)[:1000]


def mark_recommendation_applied(rec_id: str) -> bool:
    """Kept for callers of the old API: applies the recommendation (see apply_recommendation)."""
    return apply_recommendation(rec_id)["ok"]


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
    """Approve = apply (see apply_recommendation)."""
    return apply_recommendation(rec_id)["ok"]


def reject_recommendation(rec_id: str, reason: str = "") -> bool:
    """Move a queued recommendation to rejected.json without applying it."""
    queue = load_recommendation_queue()
    i = _find(queue, rec_id)
    if i is None:
        return False
    rec = queue.pop(i)
    rec.update({"status": "rejected", "rejected_at": datetime.utcnow().isoformat() + "Z"})
    _write_list(_queue_file(), queue)
    _write_list(_rejected_file(), _read_list(_rejected_file()) + [rec])
    return True


def queue_proposals(data: Any) -> Dict[str, Any]:
    """
    T8-2 (D3): queue the memory-analysis agent's proposals (its JSON output, or the list in
    its ``suggestions``). Each proposal is redacted; one whose target is not an allowed
    learnings file is skipped. Nothing is applied here.

    I-8 (T15-29): ``skipped_targets`` lists targets that are not an allowed learnings file;
    ``skipped_empty`` lists allowed targets whose proposal has no content.
    """
    items = data.get("suggestions", []) if isinstance(data, dict) else data
    queued, skipped, empty = [], [], []
    for s in items if isinstance(items, list) else []:
        if not isinstance(s, dict):
            continue
        target = s.get("target") if isinstance(s.get("target"), dict) else {}
        rel = target.get("file") or s.get("target_file")
        text = s.get("content") or s.get("proposed_change")
        if resolve_target(rel) is None:
            skipped.append(str(rel))
            continue
        if not isinstance(text, str) or not text.strip():
            empty.append(str(rel))
            continue
        rel = str(rel).replace("\\", "/").replace("skills/memory-system/references/", "")
        rec = redact_obj({"priority": s.get("priority", "medium"), "target_skill": "memory-system",
                          "target_file": rel, "section": target.get("section", "Learnings"),
                          "current_guidance": "", "proposed_change": text,
                          "rationale": s.get("rationale", ""), "supporting_data": {}}, default_names())
        rec["id"] = _content_id(rec)
        rec.update({"generated_at": datetime.utcnow().isoformat() + "Z", "auto_apply": False,
                    "requires_review": True, "status": "pending", "source": "memory-analysis-agent"})
        queued.append(rec)
    save_recommendations(queued)
    return {"queued": [r["id"] for r in queued], "skipped_targets": skipped,
            "skipped_empty": empty}


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
