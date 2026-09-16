#!/usr/bin/env bash
# check-harness-immutable.sh — skill-scoped PreToolUse(Write|Edit) for /autoresearch.
# REPO SOURCE OF TRUTH — installed to ~/.claude/skills/autoresearch/bin/ by
# tools/install-guard-hooks.js and drift-checked by tools/check-hooks-installed.js.
# The eval harness is FROZEN during an AR pass: editing criteria YAMLs, agent prompts,
# pipeline config or other skills makes the composite score meaningless and every
# keep/revert decision invalid. rubric_sha256 detects tamper post-hoc; this prevents it.
# Output contract: careful/freeze style — bare {"permissionDecision":...} or nothing.
# Fail-open on any parse failure. (No single quotes inside the python block.)
input=$(cat 2>/dev/null)
printf '%s' "$input" | python -c '
import json, re, sys

try:
    d = json.load(sys.stdin)
    path = (d.get("tool_input") or {}).get("file_path", "") or ""
except Exception:
    raise SystemExit(0)

norm = path.replace("\\", "/")
# The runner MUST write these as part of its own loop (state.json is its mandated
# UNCONDITIONAL final action; results.tsv/snapshots live under autoresearch/) — never deny.
ALLOWED = [
    r"\.aid/pipeline/state\.json$",
    r"\.aid/pipeline/autoresearch/",
    r"\.aid/pipeline/outer-counters\.sidecar$",
]
if any(re.search(p, norm) for p in ALLOWED):
    raise SystemExit(0)
PROTECTED = [
    r"/criteria/[^/]+\.ya?ml$",
    r"/AGENT-PROMPT\.md$",
    r"\.aid/[^ ]*\.json$",
    r"\.mcp\.json$",
    r"/\.claude/skills/",
]
if not any(re.search(p, norm) for p in PROTECTED):
    raise SystemExit(0)

print(json.dumps({
    "permissionDecision": "deny",
    "message": "[autoresearch] Blocked: " + norm + " is part of the FROZEN eval harness "
               "(criteria/prompts/pipeline config/skills). Editing it mid-pass makes the score "
               "meaningless. Edit only the target artifact; harness changes happen outside AR runs.",
}))
' 2>/dev/null
exit 0
