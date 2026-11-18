"""
AID Learning Mode Feedback Collector

Collects and stores structured feedback from Learning Mode interactions.
Part of the AID Memory System sub-agent.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from functools import lru_cache
import os

from .. import paths
from ..redact import context_names, redact_obj
from .schema import normalize_entry, read_entries

# Configuration. T8-3: every directory comes from paths.aid_home() ($AID_HOME, else ~/.aid),
# read on each call; none is fixed at import time.
SCHEMA_PATH = Path(__file__).parent / "schema.json"


def _pending() -> Path:
    return paths.pending_dir()


def _processed() -> Path:
    return paths.processed_dir()


_CONTEXT: Dict[str, str] = {}


def set_context(cwd: str, root: Optional[str]) -> None:
    """aid_session.py passes the project it resolved (the gates' root), so the names of
    that project are removed whatever the cwd (T8 review r1)."""
    _CONTEXT.update({"cwd": cwd, "root": root or ""})
    default_names.cache_clear()


def _aid_root(start: Path) -> Optional[str]:
    """The nearest ancestor that is an AID project (.aid/state.json or .aid/hooks/config.json),
    never the user-level AID home."""
    home = paths.aid_home().resolve()
    for d in [start] + list(start.parents):
        aid = d / ".aid"
        if aid.resolve() != home and ((aid / "state.json").is_file() or (aid / "hooks" / "config.json").is_file()):
            return str(d)
    return None


@lru_cache(maxsize=None)
def default_names() -> tuple:
    """This process's project names and user name, removed from feedback text (T8-1). The
    project is the one aid_session.py passed, else $CLAUDE_PROJECT_DIR, else the nearest AID
    project above the cwd. Run from an unrelated folder, only the cwd's names are known."""
    cwd = _CONTEXT.get("cwd") or os.getcwd()
    root = _CONTEXT.get("root") or os.environ.get("CLAUDE_PROJECT_DIR") or _aid_root(Path(cwd).resolve())
    return tuple(sorted(context_names(cwd, root)))


def ensure_directories():
    """Create feedback directories if they don't exist."""
    _pending().mkdir(parents=True, exist_ok=True)
    _processed().mkdir(parents=True, exist_ok=True)


def generate_feedback_id() -> str:
    """Generate a unique feedback entry ID."""
    return str(uuid.uuid4())


def create_feedback_entry(
    session_id: str,
    phase: str,
    role: str,
    interaction_type: str,
    decision: Optional[Dict[str, Any]] = None,
    debate: Optional[Dict[str, Any]] = None,
    feedback: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a structured feedback entry.

    Args:
        session_id: ID of the current session
        phase: AID phase (1-prd, 2-tech-spec, etc.)
        role: User's role (developer, pm, qa, tech-lead)
        interaction_type: Type of interaction
        decision: Decision details (topic, chosen, alternatives, rationale)
        debate: Debate details (if occurred)
        feedback: User's explicit feedback (rating, verbal)
        metadata: Additional metadata

    Returns:
        Complete feedback entry dictionary
    """
    entry = {
        "id": generate_feedback_id(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": session_id,
        "context": {
            "phase": phase,
            "role": role,
            "interaction_type": interaction_type
        }
    }

    if decision:
        entry["decision"] = {
            "topic": decision.get("topic"),
            "topic_category": decision.get("topic_category", "other"),
            "chosen": decision.get("chosen"),
            "alternatives": decision.get("alternatives", []),
            "rationale": decision.get("rationale"),
            "confidence": decision.get("confidence", "medium")
        }

    if debate:
        entry["debate"] = {
            "occurred": debate.get("occurred", False),
            "user_challenge": debate.get("user_challenge"),
            "original_recommendation": debate.get("original_recommendation"),
            "final_decision": debate.get("final_decision"),
            "outcome": debate.get("outcome"),
            "learning": debate.get("learning")
        }
    else:
        entry["debate"] = {"occurred": False}

    if feedback:
        entry["feedback"] = {
            "rating": feedback.get("rating"),
            "verbal": feedback.get("verbal"),
            "skipped": feedback.get("skipped", False)
        }
    else:
        entry["feedback"] = {"rating": None, "verbal": None, "skipped": True}

    if metadata:
        entry["metadata"] = {
            "response_length": metadata.get("response_length", "medium"),
            "transparency_format": metadata.get("transparency_format", "full"),
            "time_to_feedback": metadata.get("time_to_feedback"),
            "tools_used": metadata.get("tools_used", [])
        }

    return entry


def save_feedback_entry(entry: Dict[str, Any]) -> Path:
    """
    Save a feedback entry to the pending directory, REDACTED (T8-1: before it is written).

    Args:
        entry: The feedback entry to save

    Returns:
        Path to the saved file
    """
    ensure_directories()
    entry = redact_obj(entry, default_names(), skip_keys=("timestamp", "id", "session_id"))
    filename = f"{entry['timestamp'][:10]}_{entry['id'][:8]}.json"
    filepath = _pending() / filename
    tmp = filepath.with_suffix(".tmp")
    tmp.write_text(json.dumps(entry, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, filepath)
    return filepath


def load_pending_feedback() -> List[Dict[str, Any]]:
    """All pending entries, normalised and redacted (T8-3: the one reader)."""
    return read_entries([_pending()], default_names())


def mark_feedback_processed(entry_id: str) -> bool:
    """
    Move a feedback entry from pending to processed. The id is the normalised one (the
    entry's own id, or its file name for writers that store none).

    Returns:
        True if successful, False if not found
    """
    ensure_directories()
    for filepath in _pending().glob("*.json"):
        try:
            raw = json.loads(filepath.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        e = normalize_entry(raw, filepath)
        if e is not None and e["id"] == entry_id:
            os.replace(filepath, _processed() / filepath.name)
            return True
    return False


def load_feedback_by_session(session_id: str) -> List[Dict[str, Any]]:
    """All entries (pending and processed) of one session."""
    return [e for e in read_entries([_pending(), _processed()], default_names())
            if e["session_id"] == session_id]


def load_feedback_by_date_range(
    start_date: str,
    end_date: str,
    include_processed: bool = True
) -> List[Dict[str, Any]]:
    """
    Load feedback entries within a date range (YYYY-MM-DD, inclusive).
    """
    dirs = [_pending()] + ([_processed()] if include_processed else [])
    return [e for e in read_entries(dirs, default_names())
            if start_date <= e["timestamp"][:10] <= end_date]


def get_feedback_stats() -> Dict[str, Any]:
    """
    Get basic statistics about collected feedback. ``total_entries`` is the key the CLI
    reads (T8-3: it printed 0 because only ``total_count`` existed); both are returned.
    """
    pending = list(_pending().glob("*.json")) if _pending().exists() else []
    processed = list(_processed().glob("*.json")) if _processed().exists() else []
    total = len(pending) + len(processed)
    return {
        "pending_count": len(pending),
        "processed_count": len(processed),
        "total_count": total,
        "total_entries": total,
        "pending_dir": str(_pending()),
        "processed_dir": str(_processed())
    }


def get_pending_feedback() -> List[Dict[str, Any]]:
    """
    Alias for load_pending_feedback for backwards compatibility.

    Returns:
        List of pending feedback entries
    """
    return load_pending_feedback()


def save_feedback(entry: Dict[str, Any]) -> Path:
    """
    Alias for save_feedback_entry for backwards compatibility.

    Args:
        entry: The feedback entry to save

    Returns:
        Path to the saved file
    """
    return save_feedback_entry(entry)


class FeedbackCollector:
    """
    Class-based interface for collecting feedback.

    Provides an object-oriented approach to feedback collection
    with session management and convenience methods.
    """

    def __init__(self, session_id: Optional[str] = None, phase: str = "unknown", role: str = "unknown"):
        """
        Initialize feedback collector.

        Args:
            session_id: Session ID (auto-generated if not provided)
            phase: Current AID phase
            role: User's role
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.phase = phase
        self.role = role
        ensure_directories()

    def collect(
        self,
        interaction_type: str,
        decision: Optional[Dict[str, Any]] = None,
        debate: Optional[Dict[str, Any]] = None,
        feedback: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect and save a feedback entry.

        Args:
            interaction_type: Type of interaction
            decision: Decision details
            debate: Debate details
            feedback: User feedback
            metadata: Additional metadata

        Returns:
            The saved feedback entry
        """
        entry = create_feedback_entry(
            session_id=self.session_id,
            phase=self.phase,
            role=self.role,
            interaction_type=interaction_type,
            decision=decision,
            debate=debate,
            feedback=feedback,
            metadata=metadata
        )
        save_feedback_entry(entry)
        return entry

    def collect_decision(
        self,
        topic: str,
        chosen: str,
        topic_category: str = "other",
        alternatives: Optional[List[str]] = None,
        rationale: str = "",
        confidence: str = "medium",
        rating: Optional[int] = None,
        verbal: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect feedback for a decision.

        Args:
            topic: Decision topic
            chosen: Chosen option
            topic_category: Category of the topic
            alternatives: Alternative options considered
            rationale: Rationale for the decision
            confidence: Confidence level
            rating: User rating (1-5)
            verbal: Verbal feedback

        Returns:
            The saved feedback entry
        """
        return self.collect(
            interaction_type="decision",
            decision={
                "topic": topic,
                "topic_category": topic_category,
                "chosen": chosen,
                "alternatives": alternatives or [],
                "rationale": rationale,
                "confidence": confidence
            },
            feedback={
                "rating": rating,
                "verbal": verbal,
                "skipped": rating is None and verbal is None
            }
        )

    def collect_debate(
        self,
        topic: str,
        user_challenge: str,
        original_recommendation: str,
        final_decision: str,
        outcome: str,
        learning: str,
        rating: Optional[int] = None,
        verbal: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect feedback for a debate.

        Args:
            topic: Debate topic
            user_challenge: User's challenge
            original_recommendation: Original recommendation
            final_decision: Final decision after debate
            outcome: Debate outcome (confirmed/changed/partially_changed)
            learning: Learning from the debate
            rating: User rating (1-5)
            verbal: Verbal feedback

        Returns:
            The saved feedback entry
        """
        return self.collect(
            interaction_type="decision",
            decision={
                "topic": topic,
                "topic_category": "other",
                "chosen": final_decision,
                "alternatives": [original_recommendation] if original_recommendation != final_decision else [],
                "rationale": learning
            },
            debate={
                "occurred": True,
                "user_challenge": user_challenge,
                "original_recommendation": original_recommendation,
                "final_decision": final_decision,
                "outcome": outcome,
                "learning": learning
            },
            feedback={
                "rating": rating,
                "verbal": verbal,
                "skipped": rating is None and verbal is None
            }
        )

    def get_session_feedback(self) -> List[Dict[str, Any]]:
        """
        Get all feedback entries for this session.

        Returns:
            List of feedback entries
        """
        return load_feedback_by_session(self.session_id)

    @staticmethod
    def get_stats() -> Dict[str, Any]:
        """
        Get feedback statistics.

        Returns:
            Dictionary with feedback statistics
        """
        return get_feedback_stats()

    @staticmethod
    def get_pending() -> List[Dict[str, Any]]:
        """
        Get all pending feedback.

        Returns:
            List of pending feedback entries
        """
        return load_pending_feedback()


# Convenience functions for common feedback scenarios

def record_decision_feedback(
    session_id: str,
    phase: str,
    role: str,
    topic: str,
    topic_category: str,
    chosen: str,
    alternatives: List[str],
    rationale: str,
    confidence: str = "medium",
    rating: Optional[int] = None,
    verbal_feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record feedback for a decision interaction.
    """
    entry = create_feedback_entry(
        session_id=session_id,
        phase=phase,
        role=role,
        interaction_type="decision",
        decision={
            "topic": topic,
            "topic_category": topic_category,
            "chosen": chosen,
            "alternatives": alternatives,
            "rationale": rationale,
            "confidence": confidence
        },
        feedback={
            "rating": rating,
            "verbal": verbal_feedback,
            "skipped": rating is None and verbal_feedback is None
        }
    )

    save_feedback_entry(entry)
    return entry


def record_debate_feedback(
    session_id: str,
    phase: str,
    role: str,
    topic: str,
    user_challenge: str,
    original_recommendation: str,
    final_decision: str,
    outcome: str,
    learning: str,
    rating: Optional[int] = None,
    verbal_feedback: Optional[str] = None
) -> Dict[str, Any]:
    """
    Record feedback for a debate interaction.
    """
    entry = create_feedback_entry(
        session_id=session_id,
        phase=phase,
        role=role,
        interaction_type="decision",
        decision={
            "topic": topic,
            "topic_category": "other",
            "chosen": final_decision,
            "alternatives": [original_recommendation] if original_recommendation != final_decision else [],
            "rationale": learning
        },
        debate={
            "occurred": True,
            "user_challenge": user_challenge,
            "original_recommendation": original_recommendation,
            "final_decision": final_decision,
            "outcome": outcome,
            "learning": learning
        },
        feedback={
            "rating": rating,
            "verbal": verbal_feedback,
            "skipped": rating is None and verbal_feedback is None
        }
    )

    save_feedback_entry(entry)
    return entry


def record_phase_gate_feedback(
    session_id: str,
    phase: str,
    role: str,
    rating: int,
    verbal_feedback: Optional[str] = None,
    deliverables: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Record feedback at a phase gate.
    """
    entry = create_feedback_entry(
        session_id=session_id,
        phase=phase,
        role=role,
        interaction_type="phase-gate",
        decision={
            "topic": f"Phase {phase} completion",
            "topic_category": "process",
            "chosen": "Phase approved" if rating >= 3 else "Phase needs revision",
            "alternatives": [],
            "rationale": verbal_feedback or ""
        },
        feedback={
            "rating": rating,
            "verbal": verbal_feedback,
            "skipped": False
        },
        metadata={
            "deliverables": deliverables or []
        }
    )

    save_feedback_entry(entry)
    return entry


if __name__ == "__main__":
    # Demo only: builds an entry and prints it. It never writes to the real ~/.aid (T8-5).
    demo = create_feedback_entry(session_id="demo", phase="2-tech-spec", role="developer",
                                 interaction_type="decision",
                                 feedback={"rating": 5, "verbal": "Great recommendation!"})
    print(json.dumps(demo, indent=2))
