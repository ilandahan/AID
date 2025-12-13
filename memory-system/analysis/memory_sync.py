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
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from feedback.collector import load_feedback_by_date_range
from analysis.patterns import PatternDetector

# Configuration
MEMORY_DIR = Path(os.path.expanduser("~/.aid/memory"))
SLOTS_FILE = MEMORY_DIR / "slots.json"
SYNC_LOG_FILE = MEMORY_DIR / "sync_log.json"

# Memory slot allocation (from AID spec: 30 slots total)
SLOT_ALLOCATION = {
    "user_preferences": 5,      # Verbosity, role, phase focus
    "decision_patterns": 8,     # What user typically debates/accepts
    "feedback_trends": 5,       # Rating patterns, engagement
    "skill_adjustments": 7,     # User-specific skill modifications
    "context": 5                # Project state, current task
}


def ensure_directories():
    """Create memory directories if they don't exist."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)


class MemorySlotManager:
    """Manage Claude Memory slots for AID learnings."""

    def __init__(self):
        """Initialize the slot manager."""
        ensure_directories()
        self.slots = self._load_slots()

    def _load_slots(self) -> Dict[str, Any]:
        """Load current slot allocation."""
        if SLOTS_FILE.exists():
            with open(SLOTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)

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
        with open(SLOTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.slots, f, indent=2, ensure_ascii=False)

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
            True if added successfully
        """
        if category not in SLOT_ALLOCATION:
            return False

        max_slots = SLOT_ALLOCATION[category]
        current_entries = self.slots.get(category, [])

        # Check if slot available
        if len(current_entries) >= max_slots:
            # Remove oldest entry
            current_entries.pop(0)

        entry = {
            "content": content,
            "added_at": datetime.utcnow().isoformat() + "Z",
            "metadata": metadata or {}
        }

        current_entries.append(entry)
        self.slots[category] = current_entries
        self._save_slots()

        return True

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

    def sync_to_memory(self) -> Dict[str, Any]:
        """
        Sync detected patterns to Claude Memory slots.

        Returns:
            Sync results
        """
        if not self.patterns:
            return {"synced": False, "reason": "No patterns available"}

        results = {
            "synced": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "memories_added": []
        }

        # Sync verbosity preference
        verbosity = self.patterns.get('verbosity_preference', {})
        if verbosity.get('confidence') in ['high', 'medium']:
            pref = verbosity['detected_preference']
            if pref == 'prefers_concise':
                content = "User prefers abbreviated transparency after initial interactions"
            elif pref == 'prefers_detailed':
                content = "User prefers detailed explanations with full rationale"
            else:
                content = "User prefers balanced communication style"

            if self.slot_manager.add_memory(
                "user_preferences",
                content,
                {"source": "verbosity_detection", "confidence": verbosity['confidence']}
            ):
                results["memories_added"].append({
                    "category": "user_preferences",
                    "content": content
                })

        # Sync debate learnings
        debates = self.patterns.get('repeated_debates', {})
        if debates.get('patterns_found'):
            for category, data in debates.get('by_category', {}).items():
                for learning in data.get('learnings', [])[:2]:  # Max 2 per category
                    content = f"User debates {category} decisions - {learning}"
                    if self.slot_manager.add_memory(
                        "decision_patterns",
                        content,
                        {"source": "debate_analysis", "category": category}
                    ):
                        results["memories_added"].append({
                            "category": "decision_patterns",
                            "content": content
                        })

        # Sync role-specific learnings
        role_mismatch = self.patterns.get('role_mismatch', {})
        if role_mismatch.get('patterns_found'):
            for mismatch in role_mismatch.get('mismatched_roles', []):
                role = mismatch['role']
                weak_topics = mismatch.get('weak_topics', [])

                if weak_topics:
                    content = f"When assisting {role} role, focus on: {', '.join(weak_topics)}"
                else:
                    content = f"User role {role} needs tailored communication style"

                if self.slot_manager.add_memory(
                    "skill_adjustments",
                    content,
                    {"source": "role_mismatch", "role": role}
                ):
                    results["memories_added"].append({
                        "category": "skill_adjustments",
                        "content": content
                    })

        # Sync rating trends
        phase_struggles = self.patterns.get('phase_struggles', {})
        if phase_struggles.get('patterns_found'):
            for phase_data in phase_struggles.get('struggling_phases', []):
                phase = phase_data['phase']
                content = f"User rates {phase} phase lower ({phase_data['average_rating']}) - needs more support"

                if self.slot_manager.add_memory(
                    "feedback_trends",
                    content,
                    {"source": "phase_analysis", "phase": phase}
                ):
                    results["memories_added"].append({
                        "category": "feedback_trends",
                        "content": content
                    })

        # Log the sync
        self._log_sync(results)

        return results

    def _log_sync(self, results: Dict[str, Any]):
        """Log sync results."""
        ensure_directories()

        log = []
        if SYNC_LOG_FILE.exists():
            with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
                log = json.load(f)

        log.append(results)

        # Keep last 100 entries
        log = log[-100:]

        with open(SYNC_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)

    def get_sync_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent sync history."""
        if not SYNC_LOG_FILE.exists():
            return []

        with open(SYNC_LOG_FILE, 'r', encoding='utf-8') as f:
            log = json.load(f)

        return log[-limit:]


def sync_memory_from_feedback(days: int = 30) -> Dict[str, Any]:
    """
    Convenience function to sync memory from recent feedback.

    Args:
        days: Number of days of feedback to analyze

    Returns:
        Sync results
    """
    engine = MemorySyncEngine(days=days)

    if not engine.should_sync():
        return {"synced": False, "reason": "No significant patterns to sync"}

    return engine.sync_to_memory()


def get_current_memories() -> Dict[str, Any]:
    """
    Get all current memories formatted for reference.

    Returns:
        Dictionary with memories by category and usage stats
    """
    manager = MemorySlotManager()

    return {
        "usage": manager.get_slot_usage(),
        "memories": {
            category: manager.get_memories(category)
            for category in SLOT_ALLOCATION.keys()
        },
        "formatted": manager.format_for_claude_memory()
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
    print("Testing Memory Sync...")
    print("=" * 60)

    # Show current state
    memories = get_current_memories()
    print("\nCurrent Memory Usage:")
    for category, usage in memories['usage'].items():
        print(f"  {category}: {usage['used']}/{usage['max']} slots")

    print("\nFormatted Memories:")
    for mem in memories['formatted']:
        print(f"  - {mem}")

    # Test adding a memory
    print("\nAdding test memory...")
    success = add_context_memory(
        "Working on authentication feature",
        {"project": "test-project"}
    )
    print(f"Add result: {success}")

    # Show updated state
    memories = get_current_memories()
    print("\nUpdated Memory Usage:")
    for category, usage in memories['usage'].items():
        print(f"  {category}: {usage['used']}/{usage['max']} slots")

    print("\n" + "=" * 60)
    print("Memory sync test complete.")
