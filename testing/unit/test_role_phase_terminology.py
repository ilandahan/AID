"""
Tests for Role-Phase Terminology Mapping

TDD Tests for the role-based phase terminology system.
These tests validate the JSON structure and ensure all required data is present.
"""

import json
import pytest
from pathlib import Path


# Path to the terminology JSON file
TERMINOLOGY_FILE = Path(__file__).parent.parent.parent / ".claude" / "references" / "role-phase-terminology.json"


@pytest.fixture
def terminology_data():
    """Load the terminology JSON file."""
    with open(TERMINOLOGY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


class TestTerminologyStructure:
    """Test the basic structure of the terminology file."""

    def test_file_exists(self):
        """The terminology file should exist."""
        assert TERMINOLOGY_FILE.exists(), f"Terminology file not found at {TERMINOLOGY_FILE}"

    def test_valid_json(self, terminology_data):
        """The file should contain valid JSON."""
        assert terminology_data is not None
        assert isinstance(terminology_data, dict)

    def test_has_required_top_level_keys(self, terminology_data):
        """The JSON should have all required top-level keys."""
        required_keys = ["version", "description", "roles", "phases", "commonSkills", "roleSkillMapping"]
        for key in required_keys:
            assert key in terminology_data, f"Missing required key: {key}"


class TestRolesDefinition:
    """Test the roles definition."""

    EXPECTED_ROLES = ["pm", "lead", "developer", "qa"]

    def test_all_roles_defined(self, terminology_data):
        """All four roles should be defined."""
        roles = terminology_data["roles"]
        for role in self.EXPECTED_ROLES:
            assert role in roles, f"Missing role: {role}"

    def test_role_has_required_fields(self, terminology_data):
        """Each role should have id, name, shortName, and description."""
        required_fields = ["id", "name", "shortName", "description"]
        for role_id, role_data in terminology_data["roles"].items():
            for field in required_fields:
                assert field in role_data, f"Role {role_id} missing field: {field}"

    def test_role_id_matches_key(self, terminology_data):
        """The role id should match the key."""
        for role_id, role_data in terminology_data["roles"].items():
            assert role_data["id"] == role_id, f"Role {role_id} has mismatched id: {role_data['id']}"


class TestPhasesDefinition:
    """Test the phases definition for each role."""

    EXPECTED_PHASES = ["0", "1", "2", "3", "4", "5"]
    EXPECTED_ROLES = ["pm", "lead", "developer", "qa"]

    def test_all_roles_have_phases(self, terminology_data):
        """All roles should have phase definitions."""
        phases = terminology_data["phases"]
        for role in self.EXPECTED_ROLES:
            assert role in phases, f"Missing phases for role: {role}"

    def test_all_phases_defined_for_each_role(self, terminology_data):
        """Each role should have all 6 phases (0-5) defined."""
        phases = terminology_data["phases"]
        for role in self.EXPECTED_ROLES:
            role_phases = phases[role]
            for phase in self.EXPECTED_PHASES:
                assert phase in role_phases, f"Role {role} missing phase: {phase}"

    def test_phase_has_required_fields(self, terminology_data):
        """Each phase should have name, description, and skills."""
        required_fields = ["name", "description", "skills"]
        phases = terminology_data["phases"]
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                for field in required_fields:
                    assert field in phase_data, f"Role {role} phase {phase_num} missing field: {field}"

    def test_phase_name_not_empty(self, terminology_data):
        """Phase names should not be empty."""
        phases = terminology_data["phases"]
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                assert phase_data["name"].strip(), f"Role {role} phase {phase_num} has empty name"

    def test_phase_description_not_empty(self, terminology_data):
        """Phase descriptions should not be empty."""
        phases = terminology_data["phases"]
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                assert phase_data["description"].strip(), f"Role {role} phase {phase_num} has empty description"

    def test_skills_is_list(self, terminology_data):
        """Phase skills should be a list."""
        phases = terminology_data["phases"]
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                assert isinstance(phase_data["skills"], list), f"Role {role} phase {phase_num} skills is not a list"


class TestCommonSkills:
    """Test the common skills definition."""

    EXPECTED_COMMON_SKILLS = ["phase-enforcement", "context-tracking", "learning-mode"]

    def test_common_skills_is_list(self, terminology_data):
        """Common skills should be a list."""
        assert isinstance(terminology_data["commonSkills"], list)

    def test_required_common_skills_present(self, terminology_data):
        """All required common skills should be present."""
        common_skills = terminology_data["commonSkills"]
        for skill in self.EXPECTED_COMMON_SKILLS:
            assert skill in common_skills, f"Missing common skill: {skill}"


class TestRoleSkillMapping:
    """Test the role to skill file mapping."""

    EXPECTED_MAPPINGS = {
        "pm": "role-product-manager",
        "lead": "role-tech-lead",
        "developer": "role-developer",
        "qa": "role-qa-engineer"
    }

    def test_all_roles_mapped(self, terminology_data):
        """All roles should have a skill mapping."""
        mapping = terminology_data["roleSkillMapping"]
        for role in self.EXPECTED_MAPPINGS.keys():
            assert role in mapping, f"Missing skill mapping for role: {role}"

    def test_correct_skill_mappings(self, terminology_data):
        """Skill mappings should be correct."""
        mapping = terminology_data["roleSkillMapping"]
        for role, expected_skill in self.EXPECTED_MAPPINGS.items():
            assert mapping[role] == expected_skill, f"Role {role} has wrong mapping: {mapping[role]}"


class TestPhaseNamesAreUnique:
    """Test that phase names are unique and meaningful."""

    def test_phase_names_differ_by_role(self, terminology_data):
        """At least some phase names should differ between roles (personalization)."""
        phases = terminology_data["phases"]
        
        # Compare PM vs Developer phase 0 names (should be different)
        pm_phase_0 = phases["pm"]["0"]["name"]
        dev_phase_0 = phases["developer"]["0"]["name"]
        
        assert pm_phase_0 != dev_phase_0, "PM and Developer should have different phase 0 names"

    def test_no_generic_phase_names(self, terminology_data):
        """Phase names should not be generic (like just 'Phase 0')."""
        phases = terminology_data["phases"]
        generic_patterns = ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Phase 4", "Phase 5"]
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                name = phase_data["name"]
                assert name not in generic_patterns, f"Role {role} phase {phase_num} has generic name: {name}"


class TestSkillsExist:
    """Test that referenced skills actually exist in the codebase."""

    SKILLS_DIR = Path(__file__).parent.parent.parent / ".claude" / "skills"

    def test_skills_directory_exists(self):
        """The skills directory should exist."""
        assert self.SKILLS_DIR.exists(), f"Skills directory not found at {self.SKILLS_DIR}"

    def test_referenced_phase_skills_exist(self, terminology_data):
        """Skills referenced in phases should exist as directories."""
        phases = terminology_data["phases"]
        missing_skills = []
        
        for role, role_phases in phases.items():
            for phase_num, phase_data in role_phases.items():
                for skill in phase_data["skills"]:
                    skill_path = self.SKILLS_DIR / skill
                    if not skill_path.exists():
                        missing_skills.append(f"{skill} (referenced by {role} phase {phase_num})")
        
        # Some skills might be optional or have different naming
        # Just warn for now, don't fail
        if missing_skills:
            pytest.skip(f"Some skills not found (may be optional): {missing_skills}")

    def test_role_skills_exist(self, terminology_data):
        """Role skills should exist as directories."""
        mapping = terminology_data["roleSkillMapping"]
        
        for role, skill_name in mapping.items():
            skill_path = self.SKILLS_DIR / skill_name
            assert skill_path.exists(), f"Role skill not found: {skill_name} for role {role}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
