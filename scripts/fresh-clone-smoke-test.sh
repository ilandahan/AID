#!/usr/bin/env bash
# ─────────────────────────────────────────────────
# fresh-clone-smoke-test.sh — pre-promote gate, run by hand before promoting AID.
#
# WHY: a working copy hides exactly the class of bug a real adopter hits first —
# non-executable scripts (exec bit only exists once committed), personal machine
# paths baked into comments, stale local .aid/.claude state masking what a fresh
# install actually produces. The 2026-09-16 review caught 4 of these only by
# testing the committed tree, not the working copy. This script reproduces that:
# clones HEAD only (committed state, no uncommitted/untracked cruft) into a scratch
# dir, runs install.sh there with an ISOLATED HOME so it can never touch this
# machine's real ~/.claude or ~/.aid, then runs the e2e suite against the clone.
# ─────────────────────────────────────────────────
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

echo "[smoke] cloning committed HEAD (no working-copy cruft) into $WORK/clone"
git clone --quiet --depth 1 "$REPO_ROOT" "$WORK/clone"

export HOME="$WORK/fake-home"
mkdir -p "$HOME"
echo "[smoke] isolated HOME=$HOME (real ~/.claude and ~/.aid are never touched)"

cd "$WORK/clone"

echo "[smoke] running install.sh against the fresh clone..."
if ! bash install.sh; then
  echo "[smoke] FAIL: install.sh exited non-zero on a fresh clone" >&2
  exit 1
fi
echo "[smoke] install.sh OK"

echo "[smoke] running the e2e suite against the fresh clone..."
if ! python -m pytest testing/e2e -q; then
  echo "[smoke] FAIL: e2e suite red on a fresh clone" >&2
  exit 1
fi

echo "[smoke] PASS — fresh clone installs and passes e2e clean"
