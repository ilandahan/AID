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
import os

# Configuration
FEEDBACK_DIR = Path(os.path.expanduser("~/.aid/feedback"))
PENDING_DIR = FEEDBACK_DIR / "pending"
PROCESSED_DIR = FEEDBACK_DIR / "processed"
SCHEMA_PATH = Path(__file__).parent / "schema.json"


def ensure_directories():
    """Create feedback directories if they don't exist."""
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


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
        phase: AID phase (0-discovery, 1-prd, etc.)
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
    Save a feedback entry to the pending directory.

    Args:
        entry: The feedback entry to save

    Returns:
        Path to the saved file
    """
    ensure_directories()

    filename = f"{entry['timestamp'][:10]}_{entry['id'][:8]}.json"
    filepath = PENDING_DIR / filename

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)

    return filepath


def load_pending_feedback() -> List[Dict[str, Any]]:
    """
    Load all pending feedback entries.

    Returns:
        List of feedback entries
    """
    ensure_directories()

    entries = []
    for filepath in PENDING_DIR.glob("*.json"):
        with open(filepath, 'r', encoding='utf-8') as f:
            entries.append(json.load(f))

    return sorted(entries, key=lambda x: x['timestamp'])


def mark_feedback_processed(entry_id: str) -> bool:
    """
    Move a feedback entry from pending to processed.

    Args:
        entry_id: ID of the feedback entry

    Returns:
        True if successful, False if not found
    """
    ensure_directories()

    for filepath in PENDING_DIR.glob("*.json"):
        with open(filepath, 'r', encoding='utf-8') as f:
            entry = json.load(f)

        if entry['id'] == entry_id:
            dest = PROCESSED_DIR / filepath.name
            filepath.rename(dest)
            return True

    return False


def load_feedback_by_session(session_id: str) -> List[Dict[str, Any]]:
    """
    Load all feedback entries for a specific session.

    Args:
        session_id: Session ID to filter by

    Returns:
        List of feedback entries for the session
    """
    entries = []

    for directory in [PENDING_DIR, PROCESSED_DIR]:
        if directory.exists():
            for filepath in directory.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                if entry['session_id'] == session_id:
                    entries.append(entry)

    return sorted(entries, key=lambda x: x['timestamp'])


def load_feedback_by_date_range(
    start_date: str,
    end_date: str,
    include_processed: bool = True
) -> List[Dict[str, Any]]:
    """
    Load feedback entries within a date range.

    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        include_processed: Whether to include processed entries

    Returns:
        List of feedback entries in the date range
    """
    entries = []
    directories = [PENDING_DIR]

    if include_processed:
        directories.append(PROCESSED_DIR)

    for directory in directories:
        if directory.exists():
            for filepath in directory.glob("*.json"):
                with open(filepath, 'r', encoding='utf-8') as f:
                    entry = json.load(f)

                entry_date = entry['timestamp'][:10]
                if start_date <= entry_date <= end_date:
                    entries.append(entry)

    return sorted(entries, key=lambda x: x['timestamp'])


def get_feedback_stats() -> Dict[str, Any]:
    """
    Get basic statistics about collected feedback.

    Returns:
        Dictionary with feedback statistics
    """
    pending = list(PENDING_DIR.glob("*.json")) if PENDING_DIR.exists() else []
    processed = list(PROCESSED_DIR.glob("*.json")) if PROCESSED_DIR.exists() else []

    return {
        "pending_count": len(pending),
        "processed_count": len(processed),
        "total_count": len(pending) + len(processed),
        "pending_dir": str(PENDING_DIR),
        "processed_dir": str(PROCESSED_DIR)
    }


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
    # Test the collector
    print("Testing Feedback Collector...")

    # Create a test entry
    test_entry = create_feedback_entry(
        session_id="test-session-123",
        phase="2-tech-spec",
        role="developer",
        interaction_type="decision",
        decision={
            "topic": "Database selection",
            "topic_category": "technology",
            "chosen": "PostgreSQL",
            "alternatives": ["MongoDB", "MySQL"],
            "rationale": "Team familiarity and ACID compliance",
            "confidence": "high"
        },
        feedback={
            "rating": 5,
            "verbal": "Great recommendation!",
            "skipped": False
        }
    )

    print(f"Created test entry: {test_entry['id']}")

    # Save it
    filepath = save_feedback_entry(test_entry)
    print(f"Saved to: {filepath}")

    # Get stats
    stats = get_feedback_stats()
    print(f"Stats: {stats}")
