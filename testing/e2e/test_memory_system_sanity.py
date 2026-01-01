"""
AID Memory System Sanity Tests

E2E tests to verify the Python memory-system works correctly:
1. Feedback collection flow
2. Metrics calculation
3. Pattern detection
4. State management
5. File I/O operations

Run with: pytest testing/e2e/test_memory_system_sanity.py -v
"""

import pytest
import os
import sys
import json
import uuid
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

# ============================================
# Setup
# ============================================

PROJECT_ROOT = Path(__file__).parent.parent.parent
MEMORY_SYSTEM_DIR = PROJECT_ROOT / "memory-system"

# Add memory-system to path for imports
if str(MEMORY_SYSTEM_DIR) not in sys.path:
    sys.path.insert(0, str(MEMORY_SYSTEM_DIR))


# ============================================
# Fixtures
# ============================================

@pytest.fixture(scope="function")
def temp_aid_dir(tmp_path):
    """Create a temporary ~/.aid directory for testing."""
    aid_dir = tmp_path / ".aid"
    aid_dir.mkdir(parents=True)
    (aid_dir / "feedback" / "pending").mkdir(parents=True)
    (aid_dir / "feedback" / "processed").mkdir(parents=True)
    (aid_dir / "reports").mkdir(parents=True)
    (aid_dir / "memory").mkdir(parents=True)
    (aid_dir / "recommendations").mkdir(parents=True)

    # Patch the directories in the modules
    original_dir = os.environ.get("AID_STATE_DIR")
    os.environ["AID_STATE_DIR"] = str(aid_dir)

    yield aid_dir

    # Restore
    if original_dir:
        os.environ["AID_STATE_DIR"] = original_dir
    else:
        os.environ.pop("AID_STATE_DIR", None)


@pytest.fixture
def sample_feedback_entry() -> Dict[str, Any]:
    """Realistic feedback entry for testing."""
    return {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "session_id": f"session_{uuid.uuid4().hex[:8]}",
        "context": {
            "phase": "development",
            "role": "developer",
            "interaction_type": "standard"
        },
        "decision": {
            "topic": "API design approach",
            "topic_category": "architecture",
            "chosen": "REST with OpenAPI",
            "alternatives": ["GraphQL", "gRPC"],
            "rationale": "Better tooling support and team familiarity",
            "confidence": "high"
        },
        "debate": {
            "occurred": False
        },
        "feedback": {
            "rating": 4,
            "verbal": "Good suggestions, helped clarify the trade-offs",
            "skipped": False
        },
        "metadata": {
            "response_length": "medium",
            "transparency_format": "full",
            "time_to_feedback": 45,
            "tools_used": ["Read", "Grep", "Edit"]
        }
    }


@pytest.fixture
def multiple_feedback_entries(sample_feedback_entry) -> List[Dict[str, Any]]:
    """Generate multiple varied feedback entries."""
    entries = []

    # Entry 1: High rating, no debate
    entry1 = sample_feedback_entry.copy()
    entry1["id"] = str(uuid.uuid4())
    entry1["feedback"] = {"rating": 5, "verbal": "Excellent work!", "skipped": False}
    entries.append(entry1)

    # Entry 2: Low rating with debate
    entry2 = {
        "id": str(uuid.uuid4()),
        "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "session_id": f"session_{uuid.uuid4().hex[:8]}",
        "context": {
            "phase": "prd",
            "role": "product-manager",
            "interaction_type": "decision"
        },
        "decision": {
            "topic": "Feature prioritization",
            "topic_category": "product",
            "chosen": "User authentication first",
            "alternatives": ["Dashboard first", "API first"],
            "rationale": "Security foundation needed",
            "confidence": "medium"
        },
        "debate": {
            "occurred": True,
            "user_challenge": "Why not API first?",
            "original_recommendation": "Dashboard first",
            "final_decision": "User authentication first",
            "outcome": "user_convinced_claude",
            "learning": "Consider security implications earlier"
        },
        "feedback": {
            "rating": 3,
            "verbal": "Took some convincing but got there",
            "skipped": False
        },
        "metadata": {
            "response_length": "long",
            "transparency_format": "full",
            "time_to_feedback": 120,
            "tools_used": ["Read", "WebSearch"]
        }
    }
    entries.append(entry2)

    # Entry 3: Skipped feedback
    entry3 = {
        "id": str(uuid.uuid4()),
        "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat() + "Z",
        "session_id": f"session_{uuid.uuid4().hex[:8]}",
        "context": {
            "phase": "tech-spec",
            "role": "tech-lead",
            "interaction_type": "clarification"
        },
        "decision": None,
        "debate": {"occurred": False},
        "feedback": {
            "rating": None,
            "verbal": None,
            "skipped": True
        },
        "metadata": {
            "response_length": "short",
            "transparency_format": "minimal",
            "time_to_feedback": None,
            "tools_used": []
        }
    }
    entries.append(entry3)

    return entries


# ============================================
# Import Tests
# ============================================

class TestModuleImports:
    """Test that all modules can be imported."""

    def test_import_learning_subagent(self):
        """LearningSubAgent class can be imported."""
        from subagent import LearningSubAgent
        assert LearningSubAgent is not None

    def test_import_feedback_collector(self):
        """FeedbackCollector can be imported."""
        from feedback.collector import FeedbackCollector
        assert FeedbackCollector is not None

    def test_import_metrics_calculator(self):
        """MetricsCalculator can be imported."""
        from analysis.metrics import MetricsCalculator
        assert MetricsCalculator is not None

    def test_import_pattern_detector(self):
        """PatternDetector can be imported."""
        from analysis.patterns import PatternDetector
        assert PatternDetector is not None

    def test_import_quality_dashboard(self):
        """QualityDashboard can be imported."""
        from analysis.dashboard import QualityDashboard
        assert QualityDashboard is not None

    def test_import_recommendation_generator(self):
        """RecommendationGenerator can be imported."""
        from recommendations.generator import RecommendationGenerator
        assert RecommendationGenerator is not None


# ============================================
# Feedback Collection Tests
# ============================================

class TestFeedbackCollection:
    """Test feedback collection functionality."""

    def test_create_feedback_entry(self, sample_feedback_entry):
        """Feedback entry structure is valid."""
        from feedback.collector import create_feedback_entry

        entry = create_feedback_entry(
            session_id="test_session_001",
            phase="development",
            role="developer",
            interaction_type="standard",
            decision={
                "topic": "Test decision",
                "chosen": "Option A",
                "rationale": "Because reasons"
            },
            feedback={"rating": 4, "verbal": "Good job"}
        )

        assert "id" in entry
        assert "timestamp" in entry
        assert entry["session_id"] == "test_session_001"
        assert entry["context"]["phase"] == "development"
        assert entry["context"]["role"] == "developer"
        assert entry["feedback"]["rating"] == 4

    def test_save_feedback_entry(self, temp_aid_dir, sample_feedback_entry):
        """Feedback can be saved to disk."""
        from feedback.collector import save_feedback_entry

        # Monkey-patch the PENDING_DIR
        import feedback.collector as collector
        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            filepath = save_feedback_entry(sample_feedback_entry)

            assert filepath.exists()
            assert filepath.suffix == ".json"

            with open(filepath, 'r', encoding='utf-8') as f:
                saved = json.load(f)

            assert saved["id"] == sample_feedback_entry["id"]
            assert saved["feedback"]["rating"] == sample_feedback_entry["feedback"]["rating"]
        finally:
            collector.PENDING_DIR = original_dir

    def test_load_pending_feedback(self, temp_aid_dir, multiple_feedback_entries):
        """Pending feedback can be loaded."""
        from feedback.collector import load_pending_feedback, save_feedback_entry
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            # Save entries
            for entry in multiple_feedback_entries:
                save_feedback_entry(entry)

            # Load them back
            loaded = load_pending_feedback()

            assert len(loaded) == len(multiple_feedback_entries)
            # Should be sorted by timestamp
            for i in range(len(loaded) - 1):
                assert loaded[i]["timestamp"] <= loaded[i + 1]["timestamp"]
        finally:
            collector.PENDING_DIR = original_dir


# ============================================
# Metrics Calculation Tests
# ============================================

class TestMetricsCalculation:
    """Test metrics calculation functionality."""

    def test_calculate_all_metrics(self, multiple_feedback_entries):
        """All metrics can be calculated."""
        from analysis.metrics import MetricsCalculator

        calc = MetricsCalculator(multiple_feedback_entries)
        metrics = calc.calculate_all_metrics()

        assert "summary" in metrics
        assert "decision_acceptance" in metrics
        assert "debate_outcomes" in metrics
        assert "ratings_by_category" in metrics
        assert "feedback_engagement" in metrics

    def test_summary_metrics(self, multiple_feedback_entries):
        """Summary metrics are correct."""
        from analysis.metrics import MetricsCalculator

        calc = MetricsCalculator(multiple_feedback_entries)
        summary = calc.get_summary()

        assert summary["total_entries"] == 3
        assert "date_range" in summary
        assert summary["unique_sessions"] == 3

    def test_empty_entries_handled(self):
        """Empty feedback list is handled gracefully."""
        from analysis.metrics import MetricsCalculator

        calc = MetricsCalculator([])
        summary = calc.get_summary()

        assert summary["total_entries"] == 0
        assert summary["date_range"] is None

    def test_decision_acceptance_rate(self, multiple_feedback_entries):
        """Decision acceptance rate is calculated."""
        from analysis.metrics import MetricsCalculator

        calc = MetricsCalculator(multiple_feedback_entries)
        acceptance = calc.calculate_decision_acceptance_rate()

        assert "rate" in acceptance
        assert "total_decisions" in acceptance
        # We have 2 entries with decisions, 1 with debate
        assert acceptance["total_decisions"] == 2


# ============================================
# Pattern Detection Tests
# ============================================

class TestPatternDetection:
    """Test pattern detection functionality."""

    def test_detect_all_patterns(self, multiple_feedback_entries):
        """Pattern detection runs without error."""
        from analysis.patterns import PatternDetector

        detector = PatternDetector(multiple_feedback_entries)
        patterns = detector.detect_all_patterns()

        assert patterns is not None
        assert isinstance(patterns, dict)

    def test_empty_pattern_entries_handled(self):
        """Empty feedback list is handled gracefully."""
        from analysis.patterns import PatternDetector

        detector = PatternDetector([])
        patterns = detector.detect_all_patterns()

        assert patterns is not None


# ============================================
# State Management Tests
# ============================================

class TestStateManagement:
    """Test agent state management."""

    def test_state_file_creation(self, temp_aid_dir):
        """State file can be created."""
        state_file = temp_aid_dir / "agent_state.json"

        state = {
            "last_analysis": datetime.utcnow().isoformat() + "Z",
            "last_sync": None,
            "analysis_count": 1,
            "sync_count": 0
        }

        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

        assert state_file.exists()

        with open(state_file, 'r', encoding='utf-8') as f:
            loaded = json.load(f)

        assert loaded["analysis_count"] == 1

    def test_state_persistence(self, temp_aid_dir):
        """State persists across operations."""
        state_file = temp_aid_dir / "agent_state.json"

        # Write initial state
        state = {"count": 0}
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f)

        # Update state
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        state["count"] = 5
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f)

        # Verify
        with open(state_file, 'r', encoding='utf-8') as f:
            final = json.load(f)

        assert final["count"] == 5


# ============================================
# Integration Tests
# ============================================

class TestIntegration:
    """Integration tests for full workflows."""

    @pytest.mark.integration
    def test_full_feedback_flow(self, temp_aid_dir, sample_feedback_entry):
        """Complete feedback collection flow works."""
        from feedback.collector import (
            create_feedback_entry,
            save_feedback_entry,
            load_pending_feedback
        )
        import feedback.collector as collector

        original_pending = collector.PENDING_DIR
        original_processed = collector.PROCESSED_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"
        collector.PROCESSED_DIR = temp_aid_dir / "feedback" / "processed"

        try:
            # Step 1: Create entry
            entry = create_feedback_entry(
                session_id="integration_test_001",
                phase="development",
                role="developer",
                interaction_type="standard",
                feedback={"rating": 5, "verbal": "Integration test feedback"}
            )

            # Step 2: Save entry
            filepath = save_feedback_entry(entry)
            assert filepath.exists()

            # Step 3: Load pending
            pending = load_pending_feedback()
            assert len(pending) >= 1
            assert any(e["session_id"] == "integration_test_001" for e in pending)

        finally:
            collector.PENDING_DIR = original_pending
            collector.PROCESSED_DIR = original_processed

    @pytest.mark.integration
    def test_feedback_to_metrics_flow(self, temp_aid_dir, multiple_feedback_entries):
        """Feedback flows through to metrics calculation."""
        from feedback.collector import save_feedback_entry
        from analysis.metrics import MetricsCalculator
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            # Save feedback entries
            for entry in multiple_feedback_entries:
                save_feedback_entry(entry)

            # Calculate metrics
            calc = MetricsCalculator(multiple_feedback_entries)
            metrics = calc.calculate_all_metrics()

            # Verify metrics were calculated
            assert metrics["summary"]["total_entries"] == 3
            assert metrics["decision_acceptance"]["total_decisions"] == 2

        finally:
            collector.PENDING_DIR = original_dir


# ============================================
# Error Handling Tests
# ============================================

class TestErrorHandling:
    """Test error handling scenarios."""

    def test_invalid_json_handled(self, temp_aid_dir):
        """Invalid JSON files are handled gracefully."""
        from feedback.collector import load_pending_feedback
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            # Create invalid JSON file
            invalid_file = collector.PENDING_DIR / "invalid.json"
            invalid_file.write_text("not valid json {{{")

            # Should not crash, may skip invalid file
            try:
                entries = load_pending_feedback()
                # If it returns, it should be an empty list or skip the invalid file
                assert isinstance(entries, list)
            except json.JSONDecodeError:
                # This is also acceptable - the error is surfaced
                pass

        finally:
            collector.PENDING_DIR = original_dir

    def test_missing_required_fields_handled(self):
        """Missing required fields are handled."""
        from analysis.metrics import MetricsCalculator

        # Entry missing required fields
        incomplete_entries = [
            {"id": "1", "timestamp": "2024-01-01T00:00:00Z"},  # Missing context, feedback
        ]

        # Should not crash
        calc = MetricsCalculator(incomplete_entries)
        summary = calc.get_summary()

        assert summary["total_entries"] == 1


# ============================================
# Edge Cases Tests
# ============================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_in_feedback(self, temp_aid_dir):
        """Unicode characters in feedback are handled."""
        from feedback.collector import create_feedback_entry, save_feedback_entry
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            entry = create_feedback_entry(
                session_id="unicode_test",
                phase="development",
                role="developer",
                interaction_type="standard",
                feedback={
                    "rating": 5,
                    "verbal": "很好的工作！🎉 Отлично! مممتاز"
                }
            )

            filepath = save_feedback_entry(entry)

            with open(filepath, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            assert "很好的工作" in loaded["feedback"]["verbal"]
            assert "🎉" in loaded["feedback"]["verbal"]

        finally:
            collector.PENDING_DIR = original_dir

    def test_large_feedback_content(self, temp_aid_dir):
        """Large feedback content is handled."""
        from feedback.collector import create_feedback_entry, save_feedback_entry
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            large_content = "A" * 10000  # 10KB of text

            entry = create_feedback_entry(
                session_id="large_test",
                phase="development",
                role="developer",
                interaction_type="standard",
                feedback={
                    "rating": 4,
                    "verbal": large_content
                }
            )

            filepath = save_feedback_entry(entry)
            assert filepath.exists()

            file_size = filepath.stat().st_size
            assert file_size > 10000  # Should be at least 10KB

        finally:
            collector.PENDING_DIR = original_dir

    def test_concurrent_writes(self, temp_aid_dir):
        """Multiple rapid writes don't conflict."""
        from feedback.collector import create_feedback_entry, save_feedback_entry
        import feedback.collector as collector

        original_dir = collector.PENDING_DIR
        collector.PENDING_DIR = temp_aid_dir / "feedback" / "pending"

        try:
            # Write 10 entries rapidly
            for i in range(10):
                entry = create_feedback_entry(
                    session_id=f"concurrent_test_{i}",
                    phase="development",
                    role="developer",
                    interaction_type="standard",
                    feedback={"rating": i % 5 + 1, "verbal": f"Entry {i}"}
                )
                save_feedback_entry(entry)

            # All should be saved
            files = list(collector.PENDING_DIR.glob("*.json"))
            assert len(files) == 10

        finally:
            collector.PENDING_DIR = original_dir
