"""
AID Sub-Agent Registration and QA Gate Hook Tests

WHY THIS TEST:
- PROBLEM 1: Claude Code only registers a sub-agent from `.claude/agents/<name>.md`
  carrying YAML frontmatter. AID shipped only `<name>/AGENT-PROMPT.md` directories, so
  none of the agents were invocable - every `subagent_type="..."` call would fail.
- PROBLEM 2: the QA gate hook printed `{"ok": false}`, which is not a schema Claude Code
  understands, so the gate could never actually block. It was also wired only in
  `settings.local.json` (per-machine, gitignored), meaning a fresh clone had no hook.
- COST OF FAILURE: silent. Agents appear configured, the gate appears enforced, and
  neither runs.
- SUCCESS: every agent folder has a valid registerable definition whose referenced files
  exist, and the hook blocks and allows in the right conditions when actually executed.
"""
import json
import os
import re
import subprocess

import pytest

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
# Components live at the repository root so Claude Code can load this repo as a plugin.
# settings.json stays under .claude/ - it is project configuration, not a component, and
# it is what gets copied into a linked project.
AGENTS_DIR = os.path.join(REPO_ROOT, 'agents')
HOOK = os.path.join(REPO_ROOT, 'hooks', 'validate-qa-gate.py')
SETTINGS = os.path.join(REPO_ROOT, '.claude', 'settings.json')


def _agent_definitions():
    return sorted(f for f in os.listdir(AGENTS_DIR) if f.endswith('.md'))


def _agent_folders():
    return sorted(
        d for d in os.listdir(AGENTS_DIR)
        if os.path.isdir(os.path.join(AGENTS_DIR, d))
    )


def _frontmatter(path):
    """Return the YAML frontmatter block, or None if absent."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    return m.group(1) if m else None


class TestAgentsAreRegisterable:
    """Without these, `subagent_type="<name>"` cannot resolve."""

    def test_agents_dir_contains_only_definitions(self):
        """
        WHY: Claude Code registers EVERY .md under agents/ as an agent - recursively.
        Verified with `claude plugin validate`, which reported
        agents/aid-test-agent/examples/failed-test.md as an agent. Shipping asset folders
        here exposed ~71 agents, most of them prompt fragments and calibration examples.

        Mandatory assets are inlined into the definition; examples live in agent-assets/,
        which nothing scans.
        """
        folders = _agent_folders()
        assert not folders, (
            f"agents/ must be flat - every .md inside these folders would register as a "
            f"junk agent: {folders}"
        )
        stray = [f for f in os.listdir(AGENTS_DIR) if not f.endswith('.md')]
        assert not stray, f"non-definition files in agents/: {stray}"

    def test_no_nested_markdown_anywhere_under_agents(self):
        """Belt and braces: the recursion is what bites, so check recursively."""
        nested = []
        for root, _dirs, files in os.walk(AGENTS_DIR):
            if os.path.abspath(root) == os.path.abspath(AGENTS_DIR):
                continue
            nested += [os.path.relpath(os.path.join(root, f), REPO_ROOT)
                       for f in files if f.endswith('.md')]
        assert not nested, f"nested .md files would register as agents: {nested}"

    @pytest.mark.parametrize('definition', _agent_definitions())
    def test_definition_has_valid_frontmatter(self, definition):
        fm = _frontmatter(os.path.join(AGENTS_DIR, definition))
        assert fm is not None, (
            f"{definition} has no YAML frontmatter, so Claude Code will not register it"
        )

        name = re.search(r'^name:\s*(\S+)', fm, re.M)
        assert name, f"{definition} frontmatter has no 'name'"
        assert name.group(1) == definition[:-3], (
            f"{definition}: frontmatter name '{name.group(1)}' must match the filename"
        )

        desc = re.search(r'^description:\s*(.+)', fm, re.M)
        assert desc and len(desc.group(1).strip()) >= 20, (
            f"{definition}: 'description' drives delegation and must be substantive"
        )

    @pytest.mark.parametrize('definition', _agent_definitions())
    def test_referenced_files_exist(self, definition):
        """A definition that points at a missing prompt fails only at runtime."""
        path = os.path.join(AGENTS_DIR, definition)
        with open(path, encoding='utf-8') as f:
            body = f.read()

        # Backtick-quoted repo-relative paths at any component root, minus placeholders.
        referenced = set(re.findall(
            r'`((?:agents|agent-assets|skills|commands|rules|references|hooks)/[^`]+?)`',
            body))
        missing = []
        for ref in referenced:
            if '<' in ref or '*' in ref or '{' in ref:
                continue  # a family or a template variable, not a literal path
            if not os.path.exists(os.path.join(REPO_ROOT, ref)):
                missing.append(ref)
        assert not missing, f"{definition} points at files that do not exist: {missing}"

    def test_phase_review_agent_carries_all_six_phase_prompts(self):
        """
        These were 6 separate files under phase-prompts/. They are now inlined, because a
        plugin agent's cwd is the user's project - an external asset path resolves against
        their code, not the plugin. Inlined means present, so assert the content, not a path.
        """
        body = open(os.path.join(AGENTS_DIR, 'phase-review-agent.md'),
                    encoding='utf-8').read()
        for n in range(6):
            assert f'phase-prompts/phase-{n}.md' in body, (
                f'phase-review-agent.md lost the phase-{n} prompt section'
            )


class TestQAGateHookIsWired:
    def test_settings_registers_the_stop_hook(self):
        with open(SETTINGS, encoding='utf-8') as f:
            settings = json.load(f)

        hooks = settings.get('hooks', {}).get('Stop')
        assert hooks, (
            "settings.json has no Stop hook - the QA gate never fires on a fresh clone"
        )
        commands = [
            h.get('command', '')
            for group in hooks for h in group.get('hooks', [])
        ]
        assert any('validate-qa-gate.py' in c for c in commands), (
            f"no Stop hook invokes validate-qa-gate.py; found: {commands}"
        )

    def test_hook_script_exists(self):
        assert os.path.isfile(HOOK), "validate-qa-gate.py is referenced but missing"


class TestQAGateHookBehavior:
    """Execute the real hook with real Stop-hook payloads."""

    @staticmethod
    def _project(tmp_path, phase=4, task='TASK-1', criteria=True, passed=False):
        """Inject a project fixture. Never reads the real .aid state."""
        aid = tmp_path / '.aid' / 'qa'
        aid.mkdir(parents=True)
        (tmp_path / '.aid' / 'state.json').write_text(
            json.dumps({'current_phase': phase}))
        (tmp_path / '.aid' / 'context.json').write_text(
            json.dumps({'current_task': {'id': task}}))
        if criteria:
            (aid / f'{task}.yaml').write_text('criteria:\n  - it works\n')
        if passed:
            (aid / f'{task}-review.json').write_text(json.dumps({'verdict': 'PASS'}))
        return tmp_path

    @staticmethod
    def _run(project, payload):
        return subprocess.run(
            ['python', HOOK], input=json.dumps(payload),
            capture_output=True, text=True, timeout=60, cwd=str(project),
        )

    def test_blocks_when_qa_not_passed(self, tmp_path):
        project = self._project(tmp_path)

        result = self._run(project, {})

        assert result.returncode == 0, f"hook errored: {result.stderr}"
        payload = json.loads(result.stdout)
        assert payload.get('decision') == 'block', (
            f"expected a block decision, got: {result.stdout!r}"
        )
        # The reason is Claude's instruction for what to do next, so it must name the
        # agent that can actually be invoked.
        assert 'qa-validator-agent' in payload.get('reason', ''), (
            "block reason must point at the registerable qa-validator-agent"
        )

    def test_allows_when_qa_passed(self, tmp_path):
        project = self._project(tmp_path, passed=True)

        result = self._run(project, {})

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            f"QA passed but the hook still emitted a decision: {result.stdout!r}"
        )

    def test_allows_outside_development_phase(self, tmp_path):
        project = self._project(tmp_path, phase=1)

        result = self._run(project, {})

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            f"gate fired outside Phase 4: {result.stdout!r}"
        )

    def test_allows_when_no_qa_criteria_defined(self, tmp_path):
        project = self._project(tmp_path, criteria=False)

        result = self._run(project, {})

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            f"gate fired for a task with no criteria file: {result.stdout!r}"
        )

    def test_does_not_block_loop(self, tmp_path):
        """stop_hook_active means we already blocked once; blocking again loops."""
        project = self._project(tmp_path)

        result = self._run(project, {'stop_hook_active': True})

        assert result.returncode == 0
        assert result.stdout.strip() == '', (
            "hook blocked while stop_hook_active was set - this loops forever: "
            f"{result.stdout!r}"
        )
