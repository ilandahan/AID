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
AGENTS_DIR = os.path.join(REPO_ROOT, '.claude', 'agents')
HOOK = os.path.join(REPO_ROOT, '.claude', 'hooks', 'validate-qa-gate.py')
SETTINGS = os.path.join(REPO_ROOT, '.claude', 'settings.json')

# Files that live in .claude/agents/ but are documentation, not agent definitions.
NON_AGENT_MD = {'AGENT-STANDARD.md'}


def _agent_definitions():
    return sorted(
        f for f in os.listdir(AGENTS_DIR)
        if f.endswith('.md') and f not in NON_AGENT_MD
    )


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

    def test_every_agent_folder_has_a_definition(self):
        folders = _agent_folders()
        defs = {f[:-3] for f in _agent_definitions()}
        missing = [d for d in folders if d not in defs]
        assert not missing, (
            f"agent folders with no registerable .md (Claude Code cannot invoke these): "
            f"{missing}"
        )

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

        # Backtick-quoted repo-relative paths under .claude/, minus glob placeholders.
        referenced = set(re.findall(r'`(\.claude/[^`]+?)`', body))
        missing = []
        for ref in referenced:
            if '<' in ref or '*' in ref:
                continue  # e.g. phase-<N>.md - a family, checked below
            if not os.path.exists(os.path.join(REPO_ROOT, ref)):
                missing.append(ref)
        assert not missing, f"{definition} points at files that do not exist: {missing}"

    def test_phase_review_agent_has_all_phase_prompts(self):
        """The <N> placeholder above hides 6 real files; check them explicitly."""
        for n in range(6):
            p = os.path.join(AGENTS_DIR, 'phase-review-agent', 'phase-prompts',
                             f'phase-{n}.md')
            assert os.path.isfile(p), f"missing phase prompt: phase-{n}.md"


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
