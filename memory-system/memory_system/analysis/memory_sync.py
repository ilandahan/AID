"""
AID Learning Mode Memory Sync

Integrates feedback learnings with Claude Memory system.
Part of the AID Memory System sub-agent.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import os

# Support both relative imports (when used as package) and direct imports (when used standalone)
try:
    from ..feedback.collector import load_feedback_by_date_range, default_names
    from ..feedback import collector
    from .patterns import PatternDetector
    from .. import paths
    from ..redact import redact, redact_obj
except ImportError:
    from feedback.collector import load_feedback_by_date_range, default_names  # type: ignore[no-redef]
    from feedback import collector  # type: ignore[no-redef]
    from analysis.patterns import PatternDetector  # type: ignore[no-redef]
    import paths  # type: ignore[no-redef]
    from redact import redact, redact_obj  # type: ignore[no-redef]


# Configuration. T8-3: from paths.aid_home() on every call ($AID_HOME, else ~/.aid).
def _slots_file() -> Path:
    return paths.memory_dir() / "slots.json"


def _sync_log_file() -> Path:
    return paths.memory_dir() / "sync_log.json"


def _write_json(path: Path, data: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)

# Memory slot allocation (from AID spec: 30 slots total)
SLOT_ALLOCATION = {
    "user_preferences": 5,      # Verbosity, role, phase focus
    "decision_patterns": 8,     # What user typically debates/accepts
    "feedback_trends": 5,       # Rating patterns, engagement
    "skill_adjustments": 7,     # User-specific skill modifications
    "context": 5                # Project state, current task
}


def _norm(content: Any) -> str:
    """T15-26: the form two memory entries are compared in (casefold, collapsed whitespace)."""
    return " ".join(str(content).casefold().split())


def ensure_directories():
    """Create memory directories if they don't exist."""
    paths.memory_dir().mkdir(parents=True, exist_ok=True)


class MemorySlotManager:
    """Manage Claude Memory slots for AID learnings."""

    def __init__(self):
        """Initialize the slot manager. Reading creates nothing (T8-2: a dry run writes no file)."""
        self.slots = self._load_slots()

    def _load_slots(self) -> Dict[str, Any]:
        """Load current slot allocation."""
        if _slots_file().exists():
            try:
                data = json.loads(_slots_file().read_text(encoding="utf-8"))
            except (OSError, ValueError):
                data = None
            if isinstance(data, dict):
                # T8 review r1: keep only well-formed categories (a list of entry objects).
                return {c: ([e for e in data.get(c) if isinstance(e, dict) and "content" in e]
                            if isinstance(data.get(c), list) else []) for c in SLOT_ALLOCATION}

        # Initialize empty slots
        return {
            "user_preferences": [],
            "decision_patterns": [],
            "feedback_trends": [],
            "skill_adjustments": [],
            "context": []
        }

    def _save_slots(self):
        """Save slot allocation to file."""
        _write_json(_slots_file(), self.slots)

    def get_slot_usage(self) -> Dict[str, Dict[str, int]]:
        """Get current slot usage statistics."""
        usage = {}
        for category, max_slots in SLOT_ALLOCATION.items():
            current = len(self.slots.get(category, []))
            usage[category] = {
                "used": current,
                "max": max_slots,
                "available": max_slots - current
            }
        return usage

    def add_memory(
        self,
        category: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a memory entry to a category.

        Args:
            category: Memory category
            content: Memory content string
            metadata: Optional metadata

        Returns:
            True if added; False for an unknown category or an entry whose normalised
            content is already in that category (T15-26: a sync run twice adds nothing)
        """
        if category not in SLOT_ALLOCATION:
            return False

        max_slots = SLOT_ALLOCATION[category]
        current_entries = self.slots.get(category, [])
        clean = redact(content, default_names())               # T8-1: never raw text
        if self.has_memory(category, clean):
            return False

        # Check if slot available
        if len(current_entries) >= max_slots:
            # Remove oldest entry
            current_entries.pop(0)

        entry = {
            "content": clean,
            "added_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }

        current_entries.append(entry)
        self.slots[category] = current_entries
        self._save_slots()

        return True

    def has_memory(self, category: str, content: Any) -> bool:
        """True when ``category`` already holds an entry with this normalised content."""
        key = _norm(content)
        return any(_norm(e.get("content", "")) == key for e in self.slots.get(category, []))

    def get_memories(self, category: str) -> List[Dict[str, Any]]:
        """Get all memories for a category."""
        return self.slots.get(category, [])

    def clear_category(self, category: str) -> bool:
        """Clear all memories in a category."""
        if category not in self.slots:
            return False

        self.slots[category] = []
        self._save_slots()
        return True

    def format_for_claude_memory(self) -> List[str]:
        """
        Format all memories as strings for Claude Memory integration.

        Returns:
            List of memory strings
        """
        memories = []

        # User preferences
        for entry in self.slots.get("user_preferences", []):
            memories.append(f"[User Preference] {entry['content']}")

        # Decision patterns
        for entry in self.slots.get("decision_patterns", []):
            memories.append(f"[Decision Pattern] {entry['content']}")

        # Feedback trends
        for entry in self.slots.get("feedback_trends", []):
            memories.append(f"[Feedback Trend] {entry['content']}")

        # Skill adjustments
        for entry in self.slots.get("skill_adjustments", []):
            memories.append(f"[Skill Adjustment] {entry['content']}")

        # Context
        for entry in self.slots.get("context", []):
            memories.append(f"[Context] {entry['content']}")

        return memories


class MemorySyncEngine:
    """Sync learnings from feedback analysis to Claude Memory."""

    def __init__(self, days: int = 30):
        """
        Initialize sync engine.

        Args:
            days: Number of days of feedback to analyze
        """
        self.days = days
        self.slot_manager = MemorySlotManager()
        self.entries = self._load_entries()
        self.patterns = None

        if self.entries:
            detector = PatternDetector(self.entries)
            self.patterns = detector.detect_all_patterns()

    def _load_entries(self) -> List[Dict[str, Any]]:
        """Load recent feedback entries."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=self.days)).strftime("%Y-%m-%d")

        return load_feedback_by_date_range(
            start_date,
            end_date,
            include_processed=True
        )

    def should_sync(self) -> bool:
        """
        Determine if memory should be updated based on feedback.

        Returns:
            True if sync is warranted
        """
        if not self.patterns:
            return False

        # Trigger 1: Clear preference pattern (3+ consistent signals)
        verbosity = self.patterns.get('verbosity_preference', {})
        if verbosity.get('confidence') == 'high':
            return True

        # Trigger 2: Debate with significant learning
        debates = self.patterns.get('repeated_debates', {})
        if debates.get('patterns_found'):
            for cat_data in debates.get('by_category', {}).values():
                if cat_data.get('learnings'):
                    return True

        # Trigger 3: Role mismatch detected
        role_mismatch = self.patterns.get('role_mismatch', {})
        if role_mismatch.get('patterns_found'):
            return True

        # Trigger 4: Rating trend shift
        # (Would need historical data to detect)

        return False

    def plan(self) -> List[Dict[str, Any]]:
        """
        T8-2: the memory entries a sync WOULD add, redacted, without writing anything.
        ``aid_session.py memory-preview`` prints this; ``memory-sync`` (which Claude Code asks
        the user to confirm) writes exactly this list.
        """
        if not self.patterns:
            return []
        planned: List[Dict[str, Any]] = []

        def add(category, content, meta):
            clean = redact(content, default_names())
            # T15-26: an entry already in memory, or already planned, is not planned again.
            if self.slot_manager.has_memory(category, clean) or any(
                    p["category"] == category and _norm(p["content"]) == _norm(clean)
                    for p in planned):
                return
            planned.append({"category": category, "content": clean, "metadata": meta})

        verbosity = self.patterns.get('verbosity_preference', {})
        if verbosity.get('confidence') in ['high', 'medium']:
            pref = verbosity.get('detected_preference')
            if pref == 'prefers_concise':
                content = "User prefers abbreviated transparency after initial interactions"
            elif pref == 'prefers_detailed':
                content = "User prefers detailed explanations with full rationale"
            else:
                content = "User prefers balanced communication style"
            add("user_preferences", content,
                {"source": "verbosity_detection", "confidence": verbosity['confidence']})

        debates = self.patterns.get('repeated_debates', {})
        if debates.get('patterns_found'):
            for category, data in debates.get('by_category', {}).items():
                for learning in data.get('learnings', [])[:2]:  # Max 2 per category
                    add("decision_patterns", f"User debates {category} decisions - {learning}",
                        {"source": "debate_analysis", "category": category})

        role_mismatch = self.patterns.get('role_mismatch', {})
        if role_mismatch.get('patterns_found'):
            for mismatch in role_mismatch.get('mismatched_roles', []):
                role = mismatch.get('role', 'unknown')
                weak_topics = mismatch.get('weak_topics', [])
                if weak_topics:
                    content = f"When assisting {role} role, focus on: {', '.join(map(str, weak_topics))}"
                else:
                    content = f"User role {role} needs tailored communication style"
                add("skill_adjustments", content, {"source": "role_mismatch", "role": role})

        phase_struggles = self.patterns.get('phase_struggles', {})
        if phase_struggles.get('patterns_found'):
            for phase_data in phase_struggles.get('struggling_phases', []):
                phase = phase_data.get('phase')
                add("feedback_trends",
                    f"User rates {phase} phase lower ({phase_data.get('average_rating')}) - needs more support",
                    {"source": "phase_analysis", "phase": phase})
        return planned

    def sync_to_memory(self) -> Dict[str, Any]:
        """
        Write the planned entries to the memory slots. Called ONLY through
        ``aid_session.py memory-sync``, which Claude Code asks the user to confirm (T8-2).
        """
        planned = self.plan()
        if not planned:
            return {"synced": False, "memories_added": [],
                    "reason": "Nothing new to sync: every entry is already in memory"
                    if self.patterns else "No patterns available"}
        results = {"synced": True, "timestamp": datetime.utcnow().isoformat() + "Z",
                   "memories_added": []}
        for item in planned:
            if self.slot_manager.add_memory(item["category"], item["content"], item["metadata"]):
                results["memories_added"].append({"category": item["category"],
                                                  "content": item["content"]})
        self._log_sync(results)
        return results

    def _log_sync(self, results: Dict[str, Any]):
        """Log sync results."""
        ensure_directories()

        log = []
        if _sync_log_file().exists():
            try:
                log = json.loads(_sync_log_file().read_text(encoding="utf-8"))
            except (OSError, ValueError):
                log = []
        log.append(results)
        _write_json(_sync_log_file(), log[-100:])     # keep the last 100

    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sync history."""
        if not _sync_log_file().exists():
            return []
        try:
            log = json.loads(_sync_log_file().read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []

        return log[-limit:]


def _mark_processed(entries: List[Dict[str, Any]]) -> List[str]:
    """T16-29 (g8-improve-stat; I-11): after an APPROVED sync, the pending entries it analysed
    move to feedback/processed/. Returns their ids (aid_session.py counts them)."""
    analysed = {e.get("id") for e in entries}
    done = []
    for e in collector.load_pending_feedback():
        if e["id"] in analysed and collector.mark_feedback_processed(e["id"]):
            done.append(e["id"])
    return done


def sync_memory_from_feedback(days: int = 30, approve: bool = False) -> Dict[str, Any]:
    """
    T8-2: without ``approve`` this is a DRY RUN: it returns the planned (redacted) entries
    and writes nothing. ``approve=True`` is passed only by ``aid_session.py memory-sync``,
    the call Claude Code asks the user to confirm.
    """
    engine = MemorySyncEngine(days=days)

    if approve:
        result = engine.sync_to_memory() if engine.should_sync() else {
            "synced": False, "dry_run": False, "planned": [],
            "reason": "No significant patterns to sync"}
        result["processed"] = _mark_processed(engine.entries)
        return result
    if not engine.should_sync():
        return {"synced": False, "dry_run": True, "planned": [],
                "reason": "No significant patterns to sync"}
    if not approve:
        planned = engine.plan()
        if not planned:
            return {"synced": False, "dry_run": True, "planned": [],
                    "reason": "Nothing new to sync: every entry is already in memory"}
        return {"synced": False, "dry_run": True, "planned": planned,
                "reason": "Dry run: nothing written. To write these entries, run /aid-improve "
                          "(it uses aid_session.py memory-sync, which asks you to confirm)."}
    return engine.sync_to_memory()


def get_current_memories() -> Dict[str, Any]:
    """
    Get all current memories formatted for reference.

    Returns:
        Dictionary with memories by category and usage stats
    """
    manager = MemorySlotManager()
    # T20 #3: redacted for display. Slots written before redaction (3.0.7) or edited by
    # hand are never shown raw; the file on disk is unchanged.
    names = default_names()

    return {
        "usage": manager.get_slot_usage(),
        "memories": {
            category: redact_obj(manager.get_memories(category), names,
                                 skip_keys=("added_at",))
            for category in SLOT_ALLOCATION.keys()
        },
        "formatted": [redact(m, names) for m in manager.format_for_claude_memory()]
    }


def add_context_memory(content: str, metadata: Optional[Dict] = None) -> bool:
    """
    Quick function to add a context memory.

    Args:
        content: Memory content
        metadata: Optional metadata

    Returns:
        True if added successfully
    """
    manager = MemorySlotManager()
    return manager.add_memory("context", content, metadata)


if __name__ == "__main__":
    # Read-only demo: it never writes to the real memory (T8-5).
    memories = get_current_memories()
    for category, usage in memories['usage'].items():
        print(f"  {category}: {usage['used']}/{usage['max']} slots")
