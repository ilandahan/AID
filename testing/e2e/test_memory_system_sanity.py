"""
Memory System Sanity Tests
Validates that the AID memory system references and structure are intact.
"""
import os
import pytest

SKILLS_DIR = os.path.join('.claude', 'skills')
MEMORY_DIR = os.path.join(SKILLS_DIR, 'memory-system')
REFS_DIR = os.path.join(MEMORY_DIR, 'references')


class TestMemorySystemStructure:
    """Verify memory system directory structure."""

    def test_memory_system_skill_exists(self):
        assert os.path.isfile(os.path.join(MEMORY_DIR, 'SKILL.md'))

    @pytest.mark.parametrize("role", [
        "product-manager", "developer", "qa-engineer", "tech-lead", "data-scientist"
    ])
    def test_role_reference_exists(self, role):
        skill_path = os.path.join(REFS_DIR, 'roles', role, 'SKILL.md')
        cumulative_path = os.path.join(REFS_DIR, 'roles', role, 'cumulative.md')
        assert os.path.isfile(skill_path), f"Missing {skill_path}"
        assert os.path.isfile(cumulative_path), f"Missing {cumulative_path}"

    @pytest.mark.parametrize("phase", [
        "discovery", "prd", "tech-spec", "breakdown", "development", "qa-ship"
    ])
    def test_phase_reference_exists(self, phase):
        skill_path = os.path.join(REFS_DIR, 'phases', phase, 'SKILL.md')
        cumulative_path = os.path.join(REFS_DIR, 'phases', phase, 'cumulative.md')
        assert os.path.isfile(skill_path), f"Missing {skill_path}"
        assert os.path.isfile(cumulative_path), f"Missing {cumulative_path}"


class TestLearningMode:
    """Verify learning mode skill exists."""

    def test_learning_mode_skill_exists(self):
        assert os.path.isfile(os.path.join(SKILLS_DIR, 'learning-mode', 'SKILL.md'))
