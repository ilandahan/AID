"""
aid_guard -- decision logic for AID's PreToolUse phase gates (v2, round 4).

WHY: three review rounds beat every Bash text-parsing defence of an allow-listed tool
that can write files or run code (cp, sort, sed, find, xargs, git clone, ...): each fix
was answered by a sibling spelling. Round 4 stops modelling flags. Before Phase 4 (block
mode) a Bash command runs only if it is a flat list of literal words (no expansions,
braces, subshells or redirections other than to /dev/null) and every command in it is
on a small table of tools that have NO flag that writes a file or runs a program, plus
exact git / mkdir / cd / version-probe tables. Anything else is denied outright.
Contract: demo/aid-testbed/reports/T1-acceptance.md.

THREAT MODEL: a guardrail for an agent that follows instructions but makes mistakes or
rationalises shortcuts -- not a sandbox.
  - The real protection for the control files is layer A (Claude Code permission deny
    rules, installed by ensure_permissions) plus layer B (check_integrity, every call).
  - From Phase 4 on the agent runs arbitrary code by design. The Phase 4+ Bash check
    (_phase4_check) is BEST EFFORT defence in depth: it catches literal control-file
    paths, and code the agent runs can bypass it. Do not rely on it.

Pure functions only (no stdout, no exit): aid_hooks.py turns the verdicts into hook output.
"""
import fnmatch
import hashlib
import json
import os
import re
import stat
from pathlib import Path

IS_WIN = os.name == "nt"

# The only aid_session.py the Bash gate lets run before Phase 4: this plugin's own copy.
SESSION_SCRIPT = Path(__file__).resolve().parent / "aid_session.py"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# The gates' own control files, matched by SUFFIX of the normalised absolute path so the
# same list covers the project copy and the user-level ~/.claude/settings.json.
# Entries ending in "/" are directories (protects everything under them).
PROTECTED_SUFFIXES = (
    "/.aid/hooks/",
    "/.aid/integrity/",
    "/.aid/pipeline/ESCALATION.json",
    "/.aid/pipeline/cost-ledger.json",   # T21: the $ brake's running total; only gate.mjs writes it
    "/cost-ledger.json",                 # T21b: its home inside a git repo, <git-dir>/aid/<project key>/
    "/.claude/settings.json",
    "/.claude/settings.local.json",
    "/.claude/hooks/",
    "/.claude/plugins/cache/",
    "/.aid/state.json",           # T3-1: the phase the gates read; only aid_session.py writes it
    # T15 I-5: these name the installed plugin roots the gate asks about; an agent that
    # could edit them could register its own folder as an AID plugin root.
    "/.claude/plugins/known_marketplaces.json",
    "/.claude/plugins/installed_plugins.json",
)
# T15 I-4 (D3): QA verdict markers under a project .aid/qa/ (any depth) are control files.
# Matched on the case-folded key inside is_protected (the ONE protected set, INV-1).
_QA_MARKER = re.compile(r"/\.aid/qa/(?:[^/]*/)*(?:[^/]*\.qa-passed|[^/]*-review[^/]*\.json)$")
# Removing or renaming one of these directories removes protected files with it.
PROTECTED_PARENTS = ("/.aid", "/.claude", "/.aid/hooks", "/.aid/pipeline", "/.claude/hooks",
                     "/.claude/plugins")
# Literal fragments: a Phase 4+ command whose text names one of these is refused
# (catches python -c "open('.claude/settings.json','w')" and similar). Best effort.
PROTECTED_LITERALS = (".aid/hooks", ".aid/integrity", "escalation.json",
                      ".claude/settings.json", ".claude/settings.local.json",
                      ".claude/hooks", ".claude/plugins/cache",
                      ".aid/state.json", ".qa-passed",        # T15 I-4 (AC-33 reads stay exempt)
                      "cost-ledger.json")                     # T21 fix 1 (PS_PROTECTED_LITERALS inherits)

# T15-1: .claude/<dir>/ folders Claude Code loads capabilities from (a phase rule, not a
# control file; .claude/hooks/ is ALSO a control file via PROTECTED_SUFFIXES).
CLAUDE_CAPABILITY_DIRS = ("skills", "agents", "commands", "output-styles", "rules", "hooks",
                          "workflows", "routines", "agent-memory")      # T16-6 (I-12)
# T16-6 (I-12): execution-relevant direct children of a project .claude/ (same phase rule).
CLAUDE_EXEC_FILES = ("launch.json", "scheduled_tasks.json", "loop.md", "claude.md", "agents.md")
# T16-4: the pipeline's pass thresholds. The Write tools are asked (aid_hooks); a Bash write
# is refused in every phase (control-file style) by _phase4_check.
PIPELINE_CONFIG = "/.aid/pipeline/config.json"

# When the cwd is unknown, a relative target with one of these names may be a control file.
PROTECTED_BASENAMES = {"settings.json", "settings.local.json", "config.json", "escalation.json",
                       "state.json"}

SUSPICIOUS = "<suspicious>"   # path form we refuse to reason about (8.3 names, ADS, NUL)
SINKS = {"/dev/null", "nul", "/dev/stdout", "/dev/stderr"}

# Claude Code permission rules that protect the control files (layer A). Edit rules cover
# Write/MultiEdit/NotebookEdit and Bash redirections, tee, sed (permissions docs).
DENY_RULES = (
    "Edit(/.aid/hooks/**)",
    "Edit(/.aid/pipeline/ESCALATION.json)",
    "Edit(/.claude/settings.json)",
    "Edit(/.claude/settings.local.json)",
    "Edit(/.claude/hooks/**)",
    # NOT Edit(/.aid/state.json) (T3 A1): Claude Code merges Edit deny paths into the sandbox
    # denyWrite, which would stop aid_session.py itself. Layer C + the ask rules guard it.
)

# T3-4: the aid_session.py subcommands that change the phase are confirmed by the HUMAN.
# Claude Code asks for an explicit ask rule in every mode, bypassPermissions included, and
# denies it where nobody can answer (-p). ONE constant: SessionStart installs these rules
# (layer A) and the Bash gate allows the subcommands only in a spelling they match (T3-4b:
# rule matching is case-sensitive, measured in T3-P1, while Windows runs `PYTHON` too).
# T8 (A1): memory-sync and memory-apply write AID's learning memory and skill learnings
# files; the user confirms those too.
CONFIRMED_SUBCOMMANDS = ("approve", "advance", "jump", "init",    # init incl. --repair (A2)
                         "memory-sync", "memory-apply",
                         "reset", "qa-pass")              # T15 I-1 (D2, D3): 8 x 3 = 24 ask rules
_T3_SUBCOMMANDS = CONFIRMED_SUBCOMMANDS[:6]     # R4-C3: the set HEAD 2db6933's text check knew
_INTERPRETERS = ("python", "python3", "py")
ASK_RULES = tuple("Bash({} *aid_session.py {}*)".format(i, s)
                  for s in CONFIRMED_SUBCOMMANDS for i in _INTERPRETERS)
# A3: interpreter, the script path (quoted or bare), the subcommand BARE, then arguments that
# are bare or double-quoted plain text (--note "rating 4 clear scope"), single spaces.
_CANONICAL_CALL = re.compile(
    r"^(?:python|python3|py) (?:\"[^\"\n]+\"|'[^'\n]+'|[^\s\"']+) [A-Za-z0-9._:-]+"
    r"(?: (?:[A-Za-z0-9._:-]+|\"[A-Za-z0-9 ._:-]+\"))*$")
# T15-3 (R1-C1): characters with which the shell builds a word only at run time.
_UNRESOLVED = re.compile(r"[$`*?\[{]")
_PY_INTERP = re.compile(r"^(?:python[0-9.]*|py)(?:\.exe)?$", re.I)


def _depth0_segments(text):
    """Split at ; & | and newlines outside $( ... ) / ( ... ), so `$(cat f) approve` stays whole."""
    out, cur, depth = [], [], 0
    for ch in text:
        depth = depth + 1 if ch == "(" else max(0, depth - 1) if ch == ")" else depth
        if depth == 0 and ch in ";&|\n":
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def _heredoc_bodies(command, i, pending):
    """R3-C2: read the bodies of the heredocs in `pending` ([(delimiter, strip_tabs)]) from
    index i (just after the newline). Returns (bodies, index after the last body), or None
    when a delimiter line never appears (R4-C1: the caller fails closed on that text)."""
    bodies = []
    for delim, strip in pending:
        lines, found = [], False
        while i < len(command):
            end = command.find("\n", i)
            end = len(command) if end < 0 else end
            line = command[i:end].rstrip("\r")
            i = end + 1
            if (line.lstrip("\t") if strip else line) == delim:
                found = True
                break
            lines.append(line)
        if not found:
            return None
        bodies.append("\n".join(lines))
    return bodies, i


def _arith_cmd(words):
    """T16-5 (E5): the operands of let / declare -i / typeset -i / local -i are arithmetic."""
    ws = [w for w in words if not _ASSIGN.match(w)]
    if not ws:
        return False
    return ws[0] == "let" or (ws[0] in ("declare", "typeset", "local")
                              and any(re.match(r"^[-+][A-Za-z]*i", w) for w in ws[1:]))


def _names_session_text(command):
    """T16-5/T16-7: does the text name aid_session (quotes and backslashes stripped, case-
    folded), use ANSI-C quoting (which can spell it), or hold a glob/brace word that
    _may_name_session accepts?"""
    if "aid_session" in re.sub(r"[\"'`\\\s]", "", command).casefold() or "$'" in command:
        return True
    return any(re.search(r"[*?\[{]", t) and not re.search(r"[$`]", t) and _may_name_session(t)
               for t in re.split(r"[\s\"';&|<>()]+", command) if t)


def _lex(command, _brackets=True):
    """
    R2-C1, R3-C1, R3-C2: the simple commands of `command`, split the way the shell does it,
    as dicts {"words", "sep" (what ended it: ; | || & && newline or ""), "bodies" (the
    heredoc texts it reads)}; None for an unterminated quote (bash runs nothing). Splits at
    ; & | and newlines outside quotes and ( ), at blanks outside quotes, $( ) and backticks
    (so `$(which python)` is one word); quotes and escaping backslashes are removed; a
    `$'...'` word keeps its `$` (it is built at run time). An unquoted `#` that starts a word
    is a comment up to the newline (R3-C1: `# don't` must not read as an open quote). A
    heredoc body is kept apart from the commands.
    R4-C1: a `<<` inside arithmetic (`$(( ))`, `(( ))`) is a shift, not a heredoc; a heredoc
    whose delimiter line never appears returns None, like an unterminated quote, so the
    callers fail closed instead of reading the rest of the text as a heredoc body.
    T16-5 (E5): nor inside `$[ ]`, `${ }`, a `name[ ]=` subscript or the operands of let /
    declare -i; an unbalanced bracket fails closed only when the text names aid_session,
    else the text is lexed as before. T16-11: `$( ... )` inside double quotes is read to its
    matching paren (a heredoc commit message may hold any number of quotes), as lex() does.
    """
    segs, words, cur, has = [], [], [], False
    quote, depth, i, n = None, 0, 0, len(command)
    subs, tick, pending, bodies = [], False, [], []
    arith = []                      # R4-C1: per open paren, is it (inside) arithmetic?
    brk = []                        # T16-5: open $[ / ${ / name[ brackets (their closers)
    while i < n:
        ch = command[i]
        if quote is None and ch == "#" and (i == 0 or command[i - 1] in " \t\n;&|(") and (
                not cur or any(subs) or tick or cur[-1] == "("):
            nl = command.find("\n", i)
            i = n if nl < 0 else nl
            continue
        if (quote is None and ch == "<" and command[i + 1:i + 2] == "<"
                and command[i + 2:i + 3] != "<" and not any(arith) and not brk
                and not _arith_cmd(words)):
            m = re.match(r"<<(-?)[ \t]*((?:[^\s;&|<>()]|\\.)+)", command[i:])
            if m:
                if cur or has:
                    words.append("".join(cur))
                cur, has = [], False
                delim = re.sub(r"[\"'\\]", "", m.group(2))
                words.append("<<" + delim)
                pending.append((delim, bool(m.group(1))))
                i += m.end()
                continue
        if quote is None and ch == "\n" and pending:
            read = _heredoc_bodies(command, i + 1, pending)
            if read is None:
                return None     # R4-C1: no delimiter line: fail closed
            got, after = read
            bodies.extend(got)
            pending = []
            if cur or has:
                words.append("".join(cur))
            cur, has = [], False
            if depth == 0 and words:
                segs.append({"words": words, "sep": "\n", "bodies": bodies})
                words, bodies = [], []
            i = after
            continue
        if quote == "'":
            if ch == "'":
                quote = None
            else:
                cur.append(ch)
        elif quote in ('"', "$'"):
            k = None
            if quote == '"' and ch == "$" and command[i + 1:i + 2] == "(":
                try:
                    k = _matching_paren(command, i + 2)         # T16-11
                except ParseError:
                    k = None                                    # read it as before
            if k is not None:
                cur.append(command[i:k + 1])
                i = k + 1
                continue
            if ch == "\\" and i + 1 < n and (quote == "$'" or command[i + 1] in '"\\$`\n'):
                i += 1
                cur.append(("\\" if quote == "$'" else "") + command[i])  # $'\x5f' stays unresolved
            elif ch == quote[-1]:
                quote = None
            else:
                cur.append(ch)
        elif ch == "\\":
            i += 1
            if i < n and command[i] != "\n":
                cur.append(command[i])
            has = True
        elif ch == "$" and command[i + 1:i + 2] == "'":
            cur.append("$")
            quote, has, i = "$'", True, i + 1
        elif ch in "'\"":
            quote, has = ch, True
        elif ch in " \t" and (any(subs) or tick):
            cur.append(ch)                  # R3-C3: `$(which python)` stays one word
        elif ch == "&" and (command[i - 1:i] == ">" or command[i + 1:i + 2] == ">"):
            cur.append(ch)                  # 2>&1, &> file: a redirection, not a separator
        elif ch in " \t" or (depth == 0 and ch in ";&|\n"):
            if cur or has:
                words.append("".join(cur))
            cur, has = [], False
            if ch not in " \t" and words:
                segs.append({"words": words, "sep": ch, "bodies": bodies})
                words, bodies = [], []
            elif ch in "&|" and not words and segs and segs[-1]["sep"] == ch:
                segs[-1]["sep"] = ch * 2    # && and ||
        else:
            if ch == "(":
                depth += 1
                subs.append(command[i - 1:i] in ("$", "<", ">"))
                # `((` opens arithmetic (`$((`, `((`); every paren inside it stays arithmetic.
                arith.append(any(arith) or command[i + 1:i + 2] == "(")
            elif ch == ")":
                depth = max(0, depth - 1)
                subs = subs[:-1]
                arith = arith[:-1]
            elif ch == "`":
                tick = not tick
            elif _brackets and ch in "[{" and (command[i - 1:i] == "$" or brk or (
                    ch == "[" and not has and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", "".join(cur))
                    and all(_ASSIGN.match(w) for w in words))):
                brk.append("]" if ch == "[" else "}")           # T16-5: $[ ${ name[
            elif brk and ch == brk[-1]:
                brk.pop()
            cur.append(ch)
        i += 1
    if brk and quote is None and not pending:
        # T16-5: an unbalanced bracket: fail closed only when the text names aid_session.
        return None if _names_session_text(command) else _lex(command, _brackets=False)
    if quote in ("'", '"', "$'") or pending:
        return None         # bash refuses an unterminated quote: nothing runs; R4-C1: a
                            # heredoc that never reaches its delimiter line fails closed
    if cur or has:
        words.append("".join(cur))
    if words or bodies:
        segs.append({"words": words, "sep": "", "bodies": bodies})
    return segs


def _shell_segments(command):
    """
    R2-C1: the simple commands of `command` as lists of words (see _lex), or None for an
    unterminated quote. A heredoc fed to a shell (`bash <<EOF`) is read as its commands.
    """
    lexed = _lex(command)
    if lexed is None:
        return None
    out = []
    for s in lexed:
        if s["words"]:
            out.append(s["words"])
        k, _ = _interpreter_at(s["words"], _SHELLS, shc=lambda _p: False) if s["words"] else (None, 0)
        if k is not None and k != "sh-c":
            for body in s["bodies"]:
                out.extend(_shell_segments(body) or [])
    # T16-14: the commands inside $( ... ) and backticks run too (`x="$(python <S> approve)"`).
    # A body the lexer cannot read fails closed only when it names aid_session.
    try:
        subs = lex(command)[1]
    except ParseError:
        subs = [command] if "aid_session" in re.sub(r"[\"'`\\\s]", "", command).casefold() else []
    for body in subs:
        if body == command:
            return None
        got = _shell_segments(body)
        if got is None and "aid_session" in re.sub(r"[\"'`\\\s]", "", body).casefold():
            return None
        out.extend(got or [])
    return out


# R2-C1: words before the command word of a simple command; shells whose -c runs the rest.
_CMD_PREFIXES = {"env", "command", "exec", "nohup", "time", "sudo", "nice", "eval", "do", "then",
                 "else", "if", "while", "until", "!", "{", "&"}
_SHELLS = re.compile(r"^(?:ba|z|da|k)?sh(?:\.exe)?$", re.I)
# R2-C2: interpreters that run code given on the command line or on stdin.
_ANY_INTERP = re.compile(r"^(?:python[0-9.]*|py|node(?:js)?|deno|bun|perl|ruby|php|pwsh|"
                         r"powershell)(?:\.exe)?$", re.I)
_INLINE_FLAGS = ("-", "-c", "-e", "--eval", "-p", "--print", "-r", "-command")
# R3-C1: fail-closed test for text the lexer cannot parse: a python interpreter followed, on
# the same line, by a word the shell builds at run time.
_INTERP_THEN_UNRESOLVED = re.compile(r"(?:^|[\s;&|(`])(?:python[0-9.]*|py)(?:\.exe)?[ \t]+[^\n]*[$`*?\[{]",
                                     re.I)
_SESSION_WORD = re.compile(r"(?:^|[/\\])aid_session(?:\.py)?(?:$|[^a-z0-9_])")


_WRAPPERS = {"timeout", "nice", "ionice", "stdbuf", "winpty", "strace", "ltrace", "taskset",
             "chrt", "unbuffer", "caffeinate"}
_RUNNERS = {"uv", "poetry", "pipenv", "conda", "mamba", "micromamba", "pdm", "hatch", "rye", "pixi"}


def _interpreter_at(words, interp=None, shc=None, dyn=True):
    """R2-C1: (index of the command word if it is, or may be, an interpreter matching
    `interp` (python by default), else None; True when xargs feeds it). The command word
    comes after VAR= prefixes, env, command, sudo, ..., and after `sh -c` (whose payload
    `shc` judges: then ("sh-c", xargs)); a word built at run time may be any interpreter.
    R3-C3: after a wrapper (timeout 60, nice -n 5, winpty, stdbuf -oL, uv/poetry/conda run)
    its options and their values are skipped up to the interpreter.
    T16-7 (E9): with dyn=False a word built at run time counts only when its literal tail
    is an interpreter name (`"$VENV/bin/python"`), not `$DOCKER` or `"$JAVA_HOME/bin/java"`."""
    interp = interp or _PY_INTERP
    shc = shc or _unresolved_session_call
    i, xargs, opts, wrap = 0, False, False, False
    while i < len(words):
        w = words[i].lstrip("({!")
        base = re.split(r"[/\\]", w)[-1]
        bl = re.sub(r"\.exe$", "", base.lower())
        if bl in _WRAPPERS:
            wrap = True
            i += 1
            continue
        if bl in _RUNNERS and i + 1 < len(words) and words[i + 1].lower() in ("run", "exec"):
            wrap = True
            i += 2
            continue
        if wrap and w and not (interp.match(base) or _SHELLS.match(base) or re.search(r"[$`(]", w)):
            i += 1                              # an option or option value of the wrapper
            continue
        if not w or w.lower() in _CMD_PREFIXES or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w) or (
                opts and w.startswith("-")):
            opts = opts or w.lower() in _CMD_PREFIXES
            i += 1
            continue
        if bl == "xargs":
            xargs = opts = True
            i += 1
            continue
        if _SHELLS.match(base) and "-c" in words[i + 1:]:
            j = words.index("-c", i + 1) + 1
            if j < len(words) and shc(words[j]):
                return "sh-c", xargs            # bash -c "python \"<s>\" \$X": its payload
            i, opts, wrap = j, False, False
            continue
        if interp.match(base) or (re.search(r"[$`(]", w) and (
                dyn or interp.match(re.split(r"[$`(){}]", base)[-1]))):
            return i, xargs
        return None, xargs
    return None, xargs


_PY_VALUE_OPTS = ("-X", "-W", "-Q", "--check-hash-based-pycs")
_MIN_ARGS = {"jump": 2, "init": 2, "memory-apply": 1, "qa-pass": 1}


def _script_operand(words, k):
    """R3-C3: ("script"|"module", index) of what python (words[k]) runs, skipping its options
    and the values of -X / -W / -Q / --check-hash-based-pycs; ("code", None) for -c, else
    (None, None)."""
    j = k + 1
    while j < len(words):
        x = words[j]
        if x == "--":
            return ("script", j + 1) if j + 1 < len(words) else (None, None)
        if x in _PY_VALUE_OPTS:
            j += 2
            continue
        if re.match(r"^-[A-Za-z0-9.]+$", x):
            for pos, c in enumerate(x[1:], 1):
                if c == "c":
                    return "code", None
                if c == "m":
                    rest = x[pos + 1:]
                    if rest:
                        return "module", j      # -mmod: judged as the whole word
                    return ("module", j + 1) if j + 1 < len(words) else (None, None)
                if c in "XWQ":
                    if pos == len(x) - 1:
                        j += 1                  # its value is the next word
                    break
            j += 1
            continue
        if x.startswith("-"):
            j += 1
            continue
        return "script", j
    return None, None


def _brace_alternatives(word, limit=64):
    """R2-C1: bash brace expansion of {a,b} groups (innermost first, at most `limit`)."""
    m = re.search(r"\{([^{}]*,[^{}]*)\}", word)
    if not m:
        return [word]
    out = []
    for part in m.group(1).split(","):
        out.extend(_brace_alternatives(word[:m.start()] + part + word[m.end():], limit))
        if len(out) >= limit:
            break
    return out[:limit]


def _may_name_session(word):
    """R2-C1/C2: may the shell turn this script operand into an aid_session.py? A variable,
    `$'...'`, `$(...)`, backticks, `<(...)` or a PowerShell `(...)` may be anything; a glob or
    brace word only if one of its expansions has a basename that matches aid_session.py."""
    w = word.lower()
    # R3-C2: a literal last path component that is not aid_session.py cannot be the session
    # script, whatever the folder part expands to (`"$HOME/tools/db.py"`, `$(pwd)/manage.py`).
    # `$S`, `$S.py`, `aid_ses*.py`, an 8.3 name (`AID_SE~1.PY`) and `$(...)` stay in.
    last = w.split("/")[-1]
    ansi_c = w.startswith("$") and "\\" in last         # $'..aid\x5fsession.py': escapes
    last = last if ansi_c else re.split(r"[/\\]", last)[-1]
    if last and not ansi_c and not re.search(r"[$`(){}*?\[\]~]", last) and last.rstrip(". ") != "aid_session.py":
        return False
    if re.search(r"[$`(]", w):
        return True
    if not _UNRESOLVED.search(w):
        return False                        # a literal name: the ordinary checks judge it
    for alt in _brace_alternatives(w):
        if re.search(r"\{[^{}]*\.\.[^{}]*\}", alt):
            return True                     # {a..z} sequence expression
        if fnmatch.fnmatchcase("aid_session.py", re.split(r"[/\\]", alt)[-1]):
            return True
    return False


def _unresolved_session_call(command):
    """
    T15-3 (R1-C1, R2-C1): an aid_session.py call whose script or subcommand the shell fixes
    only at run time: `$(echo approve)`, `${A}pprove`, a backtick, `$X`, `aid_ses*.py`,
    `aid_{session,x}.py`, `$S.py approve`, `$'..aid\\x5fsession.py'`, `python $(cat f) approve`,
    or xargs feeding the arguments. It may run a confirmed subcommand and is never in the
    asked spelling, so it counts as one (deny). Judged only inside a simple command whose
    command word is (or may be) a python interpreter, on its script operand, so `git commit
    -m "[aid] init"`, `grep aid_session hooks/*.py` and `python gen_{a,b}.py init` are not.
    R3-C1: text the shell cannot parse (an unterminated quote) fails closed when it names
    aid_session or puts a run-time-built word after a python interpreter.
    """
    segments = _shell_segments(command)
    if segments is None:
        flat = re.sub(r"[\"'`\\\s]", "", command).lower()
        return "aid_session" in flat or bool(_INTERP_THEN_UNRESOLVED.search(command))
    dyn = _names_session_text(command)          # T16-7 (E9)
    for words in segments:
        interp, xargs = _interpreter_at(words, dyn=dyn)
        if interp == "sh-c":
            return True
        if interp is None:
            continue
        # (a) the script names aid_session and the subcommand is built at run time
        for j in range(interp + 1, len(words)):
            if _SESSION_WORD.search(words[j].lower()):
                nxt = next((x for x in words[j + 1:] if not x.startswith("-")), "")
                if _UNRESOLVED.search(nxt) or (xargs and not re.split(r"[<>]", nxt)[0]):
                    return True
                break
        # (b) the script operand itself is built at run time and may be aid_session.py.
        # R3-C2/C3: aid_session.py has no top-level options, so only the first word after
        # the script is its subcommand: a confirmed word with enough arguments to run, or a
        # word built at run time (`"$C"`), counts; `-k approve`, `--mode init` do not.
        kind, script = _script_operand(words, interp)
        if kind == "module":
            may = bool(re.search(r"[$`(*?\[{]", words[script]))
        else:
            may = kind == "script" and _may_name_session(words[script])
        if may:
            raw = words[script + 1:]
            raw = raw[1:] if raw[:1] == ["--"] else raw
            first = re.split(r"[<>]", re.sub(r"[()`]", "", raw[0]))[0] if raw else ""
            if first and not first.startswith("-"):
                if re.search(r"[$`(*?\[{]", raw[0]):
                    return True                 # the subcommand itself is built at run time
                more = [x for x in raw[1:] if re.split(r"[<>]", x)[0]]
                if first.lower() in CONFIRMED_SUBCOMMANDS and (
                        len(more) >= _MIN_ARGS.get(first.lower(), 0)
                        or any(re.search(r"[$`*?\[{]", x) for x in more)):
                    return True
    return False


def _inline_session_call(command):
    """
    R2-C2: an interpreter given code on its command line or on stdin (-c, -e, `-`, a heredoc,
    a pipe) whose text names aid_session and a confirmed subcommand: subprocess.run([...,
    'aid_session.py', 'init']), runpy with sys.argv, node -e execFileSync(...). That is a
    confirmed call, never in the asked spelling.
    """
    if not _names_confirmed_session(command):
        return False
    segs = _lex(command)
    if segs is None:
        return False                    # _unresolved_session_call fails closed on this text
    # R3-C2: only code the interpreter really receives counts: its own -c/-e word (and the
    # rest of its command), or what reaches its stdin (heredoc, here-string, pipe). An
    # interpreter word inside a commit message, or a `<<` elsewhere, does not.
    for n, seg in enumerate(segs):
        words = seg["words"]
        k, _ = _interpreter_at(words, _ANY_INTERP, shc=_inline_session_call)
        if k == "sh-c":
            return True
        if k is None:
            continue
        rest = words[k + 1:]
        opts = []
        for x in rest:
            if not x.startswith("-") or x == "-":
                break
            opts.append(x.lower())
        nxt = rest[len(opts)] if len(rest) > len(opts) else ""
        if any(o in _INLINE_FLAGS for o in opts):
            payload = rest
        elif nxt in ("", "-") or nxt[:1] == "<":
            payload = list(seg["bodies"]) + [x for x in rest if x.startswith("<<<")]
            m = n - 1
            while m >= 0 and segs[m]["sep"] == "|":
                payload += segs[m]["words"] + segs[m]["bodies"]
                m -= 1
        else:
            continue
        if _names_confirmed_session(" ".join(payload)):
            return True
    # A shell fed a heredoc or a pipe runs that text as commands.
    for n, seg in enumerate(segs):
        k, _ = _interpreter_at(seg["words"], _SHELLS, shc=lambda _p: False)
        if k not in (None, "sh-c") and any(_inline_session_call(b) for b in seg["bodies"]):
            return True
    return False


def _names_confirmed_session(text):
    """R2-C2: does the text (quotes and backslashes ignored) name aid_session and a
    confirmed subcommand as words?"""
    cleaned = text.replace('"', "").replace("'", "").replace("\\", "")
    tokens = set(re.split(r"[^a-z0-9_-]+", cleaned.lower()))
    return "aid_session" in tokens and bool(tokens & set(CONFIRMED_SUBCOMMANDS))


def _session_operand(word):
    """R4-C3: is this interpreter operand the session script (last path component
    aid_session.py, any case, trailing dots/spaces ignored) or module (`hooks.aid_session`)?"""
    last = re.split(r"[/\\]", word.lower())[-1].rstrip(". ")
    return last == "aid_session.py" or last.split(".")[-1] == "aid_session"


def _runner_script(words):
    """T16-13: `uv|pdm|hatch|rye|pixi|poetry|pipenv run [options] x.py ...` runs x.py with
    python: the index of the first .py operand after `<runner> run`, else None."""
    for i, w in enumerate(words[:-1]):
        base = re.sub(r"\.exe$", "", re.split(r"[/\\]", w)[-1].lower())
        if base in _RUNNERS and words[i + 1].lower() in ("run", "exec"):
            return next((j for j in range(i + 2, len(words)) if not words[j].startswith("-")
                         and words[j].lower().rstrip(". ").endswith(".py")), None)
    return None


def _carried_lines(words):
    """R2-04: command lines carried inside one word that a command runs: a git alias
    (`git -c alias.x="!python <S> approve" x`), `script -qc "..."`, `su|runuser -c "..."`,
    `make --eval="x:;..."` / `make -E ...`, `env -S "..."` / `--split-string=...`. Only words
    that name aid_session are returned (newline-joined so each part is its own command)."""
    out = []
    lead = next((re.sub(r"\.exe$", "", re.split(r"[/\\]", x)[-1].lower()) for x in words
                 if x.lower() not in _CMD_PREFIXES - {"env"} and not re.match(r"^[A-Za-z_]\w*=", x)), "")
    for i, w in enumerate(words):
        if "aid_session" not in w.lower():
            continue
        prev = words[i - 1] if i else ""
        line = None
        if lead == "git" and re.match(r"^alias\.[^=]*=!", w, re.I):
            line = w.split("=!", 1)[1]
        elif lead in ("script", "su", "runuser") and (re.match(r"^-[A-Za-z]*c$", prev) or prev == "--command"):
            line = w
        elif lead in ("script", "su", "runuser") and w.startswith("--command="):
            line = w.split("=", 1)[1]
        elif lead == "make" and (w.startswith("--eval=") or prev in ("--eval", "-E")):
            line = w.split("=", 1)[1] if w.startswith("--eval=") else w
            line = re.sub(r"^[^:;\n]*::?;?", "", line, count=1) if ":" in line else line
        elif lead == "env" and (prev in ("-S", "--split-string") or w.startswith(("-S", "--split-string="))):
            line = w if prev in ("-S", "--split-string") else (
                w.split("=", 1)[1] if w.startswith("--split-string=") else w[2:])
        if line:
            out.append(line.replace(";", "\n"))
    return out


def _runs_session(command, powershell=False):
    """
    R4-C3: does the command really run aid_session.py with a confirmed subcommand (or one
    built at run time)? The narrow check behind the gate's every-folder decision (D1/D2):
    only the script operand of a python interpreter whose last path component is
    aid_session.py, or a script operand built at run time in an interpreter's script position
    (_unresolved_session_call, Bash), or code given to an interpreter (_inline_session_call),
    counts. Prose, commit messages, echo/printf/grep text and heredoc bodies that only NAME
    aid_session do not (HEAD 2db6933 allowed them outside AID). Inside an AID project
    evaluate_bash keeps the wider T3 text check (_confirmed_intent).
    PowerShell: backtick escapes and `+` joins are removed first and `\` reads as `/` (T18); a bare variable script
    operand (`$env:SCRIPT`) is not judged (R4-C3); built paths are _ps_built_session_call's.
    """
    text = command
    if powershell:
        # T18 (gate run 4): `\` is a path separator in PowerShell, not an escape; lexed as bash,
        # `.\aid_session.py` read as `.aid_session.py` and the call went unjudged (silent allow).
        text = re.sub(r"[`]", "", command).replace("\\", "/")
    elif _unresolved_session_call(command) or _inline_session_call(command):
        return True
    segments = _shell_segments(text)
    if segments is None:
        # Unparsable (unterminated quote or heredoc): fail closed when it names the script.
        return "aid_session" in re.sub(r"[\"'`\\\s+]", "", command).lower()
    for words in segments:
        lead = next((x for x in words if x.lower() not in _CMD_PREFIXES - {"eval"}
                     and not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", x)), "")
        if lead.lower() == "eval":                 # eval 'python "<S>" approve': its text runs
            rest = words[words.index(lead) + 1:]   # R2-01: a direct call there gets its twin
            if rest and _runs_session(direct_exec_twin(" ".join(rest), powershell), powershell):
                return True
            continue
        # T18 (narrow audit 1): a direct call in the carried line gets its python twin (I-17).
        if not powershell and any(_runs_session(direct_exec_twin(p)) for p in _carried_lines(words)):
            return True                          # R2-04: git alias, script -c, su -c, ...
        # R1-03 (T17 fix cycle 1): a direct call in the -c payload (`sh -c "\"<S>\" approve"`)
        # is judged like its python twin (I-17).
        k, _ = _interpreter_at(words, shc=lambda p: _runs_session(direct_exec_twin(p, powershell), powershell))
        if k == "sh-c":
            return True
        r = _runner_script(words)
        if k is None and r is not None:
            k, kind, j = r - 1, "script", r      # T16-13: `uv run "<S>" approve`
        elif k is None:
            # R2-04: `coverage run [-m] X`, `pipx run X`: X (or a later operand) is what runs.
            # Only as the command word (after env/command/VAR= prefixes), not `echo coverage ...`.
            c = next((i for i, x in enumerate(words) if x.lower() not in _CMD_PREFIXES
                      and not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", x)), None)
            if c is None or c + 1 >= len(words) or not re.match(
                    r"^(?:coverage|pipx)(?:\.exe)?$", re.split(r"[/\\]", words[c])[-1], re.I):
                continue
            k, kind, j = c, "module", c + 1
        else:
            kind, j = _script_operand(words, k)
        if kind not in ("script", "module") or j is None:
            continue

        def clean(x):
            return re.sub(r"[()+\s\"']", "", x) if powershell else x
        op = clean(words[j])
        named = _session_operand(op)
        if powershell and not named and re.search(r"[*?\[]", op):
            named = fnmatch.fnmatchcase("aid_session.py", re.split(r"[/\\]", op.lower())[-1])
        if not named:
            # R2-04: a script-runner module (`-m runpy|pdb|cProfile|trace|coverage ...`), any
            # module or script, coverage/pipx: a LATER operand that is the session script runs
            # it (or is handed to it): `python -m runpy "<S>" approve`, `python x.py "<S>" approve`.
            j = next((m for m in range(j + 1, len(words)) if _session_operand(clean(words[m]))), None)
            if j is None:
                continue
        nxt = next((x for x in words[j + 1:] if not x.startswith("-")), "")
        first = re.split(r"[;&|<>()]", nxt)[0]
        if first.lower() in CONFIRMED_SUBCOMMANDS or (nxt and re.search(r"[$`(]", nxt)):
            return True
    return False


def _confirmed_intent(command):
    """T3 A3: does the command run aid_session.py with a confirmed subcommand? Judged on the
    first non-option word after the script, ignoring quotes and backslashes, so `"approve"`,
    `ap""prove` and `ap\\prove` (which bash all runs as approve) count."""
    # Judge the text bash will actually run: quotes and backslashes removed BEFORE looking
    # for the script, so `aid_sess""ion.py` cannot hide the call (T3 review r2 BLOCKER).
    cleaned = command.replace('"', "").replace("'", "").replace("\\", "")
    i = cleaned.lower().find("aid_session")
    if (i >= 0 or "aid_session" in cleaned.replace("\n", "").lower()) and (
            "$'" in command or "\\\n" in command):
        # Bash-only quoting ($'\x61pprove', a backslash-newline split) can spell any
        # subcommand; never canonical, so treating it as a confirmed call denies it.
        return True
    if _unresolved_session_call(command) or _inline_session_call(command):
        return True
    if _runs_session(command):
        return True
    # T3 text check (5f8f199), EVERY occurrence: in `".../AID_SESSION x/../AID_SESSION.PY"
    # jump` the first one is a directory name, and the word after it is not the subcommand.
    # It keeps the T15 A1 residual forms (pythonw, chronic/setsid/flock python, case, eval of
    # a variable, ...) denied inside AID. T16 B1: as at 5f8f199, prose, commit messages and
    # echo/grep text that NAME aid_session and a confirmed word are denied too (an accepted
    # false denial in the safe direction; T16-14 reverted, R4-03).
    if "aid_session" in cleaned.lower():
        for m in re.finditer("aid_session", cleaned.lower()):
            words = cleaned[m.start():].split()[1:]
            first = next((w for w in words if not w.startswith("-")), "")
            # T15-3: `approve; echo x`, `approve>log`, `approve&&x`: the shell ends the word.
            first = re.split(r"[;&|<>()]", first)[0]
            if first.lower() in _T3_SUBCOMMANDS:
                return True
    # And on the same words AC-23 accepts: whatever the gate would run as this plugin's
    # script, its subcommand decides.
    if _is_plugin_session(command):
        w = tokenize_strict(command)[0].words
        first = next((x.text for x in w[2:] if not x.text.startswith("-")), "")
        return first.lower() in CONFIRMED_SUBCOMMANDS
    return False


def confirmed_form_verdict(command):
    """
    T3-4b: None unless the command runs a confirmed aid_session.py subcommand in a form that
    Claude Code would NOT ask the user about. Allowed: the canonical shape AND a case-
    sensitive ASK_RULES match (quote characters ignored, as Claude Code's match did in T3-P1).
    """
    if not _confirmed_intent(command):
        return None
    return _form_reason(command)


def _form_reason(command):
    """T3-4b: None when a confirmed call is in the asked (canonical) spelling, else the
    deny reason. The caller has already decided that the command is a confirmed call."""
    raw = command.strip()
    bare = raw.replace('"', "").replace("'", "")
    if _CANONICAL_CALL.match(raw) and not _unresolved_session_call(command) and any(
            fnmatch.fnmatchcase(bare, r[len("Bash("):-1]) for r in ASK_RULES):
        return None
    return ("this aid_session.py call changes the AID phase or AID's learning memory, so the "
            "user must confirm it, and "
            "Claude Code only asks in the exact form: lower-case python, python3 or py, single "
            "spaces, the subcommand bare (not quoted), e.g. python \"{}\" approve. Quoted "
            "values (--note \"...\") may contain only letters, digits, spaces and . _ : - . "
            "Run it in that form; do not make the change any other way"
            ).format(str(SESSION_SCRIPT).replace("\\", "/"))


def _key(path):
    """Comparison form: forward slashes; case-folded on Windows."""
    p = path.replace("\\", "/")
    return p.casefold() if IS_WIN else p


def normalize(path, cwd, literal=False, strip=True):
    """
    Resolve a path the way the OS will, or return SUSPICIOUS / None.

    None  = not decidable statically (shell word with $, glob, ~user, backticks).
    SUSPICIOUS = a form used to dodge string checks (NUL, 8.3 short names, NTFS streams).
    literal=True for Write-tool paths: no shell expansion happens, so $ ? * are plain text.
    strip=False keeps trailing dots/spaces (the raw form): Win32 drops them, but writers
    using \\\\?\\ paths (Node) create them literally. write_target_verdict checks both.
    """
    if path is None:
        return None
    if "\x00" in path:
        return SUSPICIOUS
    if _key(path) in SINKS:
        return _key(path)
    p = path.replace("\\", "/")
    for prefix in ("//?/", "//./"):
        if p.startswith(prefix):
            p = p[len(prefix):]
            # \\?\Volume{GUID}\..., \\?\UNC\host\..., \\.\device: only the drive form is
            # reasoned about; anything else would be joined onto cwd and miss the checks.
            if not re.match(r"^[A-Za-z]:(/|$)", p):
                return SUSPICIOUS
            break
    if IS_WIN and p.startswith("//"):
        return SUSPICIOUS                                     # UNC \\host\share (incl. \\host\c$)
    if not literal and (re.search(r"[$`*?\[]", p) or p.startswith("~") and not re.match(r"^~(/|$)", p)):
        return None
    if IS_WIN:
        m = re.match(r"^/([a-zA-Z])(/|$)(.*)$", p)          # MSYS /c/x -> c:/x
        if m:
            p = "{}:/{}".format(m.group(1), m.group(3))
        if re.match(r"^[A-Za-z]:(?!/)", p):
            return SUSPICIOUS                                 # drive-relative C: / C:x: Git Bash reads C:/ or a literal name, Win32 joins cwd
    # Bash expands ~user too; Claude Code's Write tool expands only "~", "~/" and "~\"
    # (backslashes are already "/"), so a literal "~Iland/x" is a dir named "~Iland" (F1).
    if not literal or re.match(r"^~(/|$)", p):
        p = os.path.expanduser(p)
    if IS_WIN:
        drive, rest = os.path.splitdrive(p)
        if ":" in rest:
            return SUSPICIOUS                                 # alternate data stream
        parts = rest.replace("\\", "/").split("/")
        if any(re.search(r"~\d", part) for part in parts):
            return SUSPICIOUS                                 # 8.3 short name
        # Windows drops trailing dots/spaces from each component.
        if strip:
            p = drive + "/".join(part.rstrip(" .") if part not in (".", "..") else part for part in parts)
    if not os.path.isabs(p):
        if cwd is None:
            return None
        p = os.path.join(cwd, p)
    if IS_WIN and not strip:
        # Plain realpath folds "docs." onto an existing "docs" (Win32 rules); with the \\?\
        # prefix it keeps the component as Node creates it (measured, scratchpad t1a).
        p = os.path.realpath("\\\\?\\" + os.path.normpath(p))
        if p.startswith("\\\\?\\UNC\\"):
            p = "\\\\" + p[8:]                                # \\?\UNC\host\x keys as //host/x, like the root
        return _key(p[4:] if p.startswith("\\\\?\\") else p)
    return _key(os.path.realpath(p))


_PROJECT = None         # the gated project's root (aid_hooks.set_project_root sets it)
_LIVE_PROTECTED = ("hooks", ".claude-plugin", "agents", "skills/reflection/criteria")


def set_project(root):
    """T17-9: the project root the gates judge, so the live plugin root can be told apart."""
    global _PROJECT
    _PROJECT = str(root) if root else None


def _live_protected():
    """T17-9 (U-09): from a project outside the live plugin root (link-project route), the
    live root's hooks, manifest, agents and reflection criteria are protected like the cache
    copies (T15-5). The live root's own repo, as the project, is unchanged."""
    if not _PROJECT:
        return []
    live = _key(os.path.realpath(str(LIVE_ROOT))).rstrip("/")
    proj = _key(os.path.realpath(str(_PROJECT))).rstrip("/")
    if (live + "/").startswith(proj + "/"):
        return []
    return [live + "/" + d + "/" for d in _LIVE_PROTECTED]


def _live_root_only(norm):
    """T17-9: protected only as a live-root file (not by any other rule)."""
    if norm in (None, SUSPICIOUS) or norm in SINKS:
        return False
    k = _pkey(norm.rstrip("/")) + "/"
    if not any(k.startswith(_pkey(e)) for e in _live_protected()):
        return False
    global _PROJECT
    saved, _PROJECT = _PROJECT, None
    try:
        return not is_protected(norm)
    finally:
        _PROJECT = saved


def _live_parent(norm, lp):
    """R1-01 (T17 fix cycle 1): the live root itself, or a folder in it that holds a protected
    one (skills/, skills/reflection/): removing, moving or extracting into it reaches the
    live-root files, as a cache copy's own folder does (T15-5). `lp` is _live_protected()."""
    if not lp or norm in (None, SUSPICIOUS) or norm in SINKS:
        return False
    k = _pkey(norm.rstrip("/"))
    root = _pkey(lp[0])[:-len("/" + _LIVE_PROTECTED[0] + "/")]
    return (k + "/").startswith(root + "/") and any(_pkey(e).startswith(k + "/") for e in lp)


def _mentions_live(text, lp):
    """R1-01: the text names a live-root protected folder inside a word (`of=<R>/hooks/x`,
    `-o<R>/hooks/x`, code given to an interpreter): the live-root twin of mentions_protected,
    which catches the cache copies by their `.claude/plugins/cache` text."""
    t = text.replace("\\", "/").casefold() + "/"
    return any(_pkey(e) in t for e in lp)


# R1-01: interpreters whose script word may be a live-root file (running it is not writing it).
_LIVE_RUNNERS = re.compile(r"^(?:pythonw?[0-9.]*|pyw?|node(?:js)?|deno|bun|(?:ba|z|da|k)?sh)(?:\.exe)?$",
                           re.I)


def _live_run_word(words):
    """R1-01: the script word the interpreter of this simple command runs (after the VAR=,
    env/exec/nohup/..., wrapper and runner prefixes), else None."""
    texts = [w.text for w in words]
    k, _ = _interpreter_at(texts, _LIVE_RUNNERS, shc=lambda _p: False, dyn=False)
    if not isinstance(k, int):
        # Behind a launcher the walk does not know (chronic, setsid, flock F, ...): the first
        # interpreter word, so the T15 A1 residual rows keep their verdicts (T16-14).
        k = next((i for i, w in enumerate(words) if not w.dynamic
                  and _LIVE_RUNNERS.match(re.split(r"[/\\]", w.text)[-1])), None)
        if k is None:
            return None
    if _PY_INTERP.match(re.split(r"[/\\]", texts[k])[-1]):
        kind, j = _script_operand(texts, k)
        return texts[j] if kind == "script" else None
    j = k + 1
    while j < len(texts) and texts[j].startswith("-"):
        j += 1
    return texts[j] if j < len(texts) else None


# T17-9: operands a Phase 4+ command edits in place (writers proper are judged as writes).
_IN_PLACE_CMDS = {"install", "ln", "truncate", "dd", "rsync", "chmod", "chown", "shred", "unlink"}


def _edits_in_place(name, args):
    return name in _IN_PLACE_CMDS or (name in ("sed", "perl", "ruby") and any(
        re.match(r"^-[A-Za-z]*i", a) or a.startswith("--in-place") for a in args))


def _env_protected():
    """Protected paths that env vars move away from a .claude / .aid folder name, so the
    suffix list misses them: $CLAUDE_CONFIG_DIR/{settings.json, plugins/cache/, hooks/}
    and the layer-B baseline under $AID_HOME/integrity/. Directories end in "/" and
    match by prefix."""
    out = [_key(os.path.realpath(str(integrity_base()))).rstrip("/") + "/"]
    # T17-8 (U-08): the recommendation queue that memory-apply turns into skill edits.
    for h in (os.environ.get("AID_HOME") or str(Path.home() / ".aid"), str(Path.home() / ".aid")):
        out.append(_key(os.path.realpath(os.path.join(h, "recommendations"))).rstrip("/") + "/")
    out += _live_protected()
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        base = _key(os.path.realpath(cfg)).rstrip("/")
        out += [base + "/settings.json", base + "/plugins/cache/", base + "/hooks/",
                base + "/plugins/known_marketplaces.json",          # T15 I-5
                base + "/plugins/installed_plugins.json"]
    return out


def _pkey(path):
    """Protected-set comparison form: case-folded on EVERY OS (F3). macOS (APFS/HFS+) is
    case-insensitive by default, so `.CLAUDE/SETTINGS.JSON` reaches the real control file
    there; _key folds only on Windows. Over-matching a distinct-case name on a
    case-sensitive Linux disk is a deliberate false denial on a control-file name."""
    return _key(path).casefold()


def _user_state_files():
    """T3 A5: the user-level session file(s), $AID_HOME/state.json and ~/.aid/state.json.
    They share the /.aid/state.json suffix with the project file but are not control files."""
    homes = [os.environ.get("AID_HOME") or str(Path.home() / ".aid"), str(Path.home() / ".aid")]
    return {_pkey(os.path.realpath(os.path.join(h, "state.json"))) for h in homes}


def is_protected(norm):
    if norm in (None, SUSPICIOUS) or norm in SINKS:
        return norm == SUSPICIOUS
    k = _pkey(norm.rstrip("/"))
    if k in _user_state_files():
        return False
    if _QA_MARKER.search(k):
        return True
    for s in PROTECTED_SUFFIXES:
        sk = _pkey(s)
        if sk.endswith("/"):
            if (k + "/").find(sk) >= 0:
                return True
        elif k.endswith(sk):
            return True
    return any((k + "/").startswith(e) if e.endswith("/") else k == e
               for e in map(_pkey, _env_protected()))


def is_protected_or_parent(norm):
    if is_protected(norm):
        return True
    if norm in (None, SUSPICIOUS):
        return norm == SUSPICIOUS
    k = _pkey(norm.rstrip("/"))
    return any(k.endswith(_pkey(p)) for p in PROTECTED_PARENTS)


def mentions_protected(text):
    t = text.replace("\\", "/").casefold()
    return any(lit in t for lit in PROTECTED_LITERALS)


def is_project_state(norm):
    """T16-1/2 (E2): a project .aid/state.json in ANY folder (not the user-level file, A5)."""
    if norm in (None, SUSPICIOUS) or norm in SINKS:
        return False
    k = _pkey(norm.rstrip("/"))
    return k.endswith("/.aid/state.json") and k not in _user_state_files()


def is_pipeline_config(norm):
    """T16-4: a project .aid/pipeline/config.json."""
    return norm not in (None, SUSPICIOUS) and _pkey(norm.rstrip("/")).endswith(PIPELINE_CONFIG)


# R1-06 (T16 fix cycle 1): control files a glob write target may expand to.
_CONTROL_GLOB_TARGETS = (".aid/state.json", ".aid/pipeline/config.json", ".aid/pipeline/escalation.json",
                         ".aid/hooks/config.json", ".claude/settings.json", ".claude/settings.local.json",
                         ".aid/pipeline/cost-ledger.json")     # T21


_HOME_PREFIX = re.compile(r"^(?:~|\$HOME|\$\{HOME\})(?=[/\\]|$)")


def _expand_home(text):
    """R2-03: bash expands a leading `~`, `$HOME` or `${HOME}` to the user's home."""
    return _HOME_PREFIX.sub(lambda _m: os.path.expanduser("~").replace("\\", "/"), text, count=1)


def _home_word(w):
    """R2-03: a word whose only expansion is a leading ~ / $HOME, with that expanded."""
    if not w.dynamic or not _HOME_PREFIX.match(w.text):
        return w
    t = _expand_home(w.text)
    return Word(t, bool(re.search(r"[$`*?\[{~]", t[len(os.path.expanduser("~")):])))


def _brace_words(w, home=True):
    """R2-01: bash brace expansion is static text: an unquoted `{a,b}` word with no $ or
    backtick is every one of its alternatives (`.aid/state.{json,x}`, `.aid/{state,x}.json`).
    A quoted brace is not expanded; the lexer does not keep that, so it counts too (a false
    denial only on a quoted brace-and-comma name of a control file). home: a leading ~ /
    $HOME is expanded first (_home_word)."""
    w = _home_word(w) if home else w
    if not (w.dynamic and "{" in w.text and "," in w.text) or re.search(r"[$`]", w.text):
        return [w]
    alts = _brace_alternatives(w.text)
    return [Word(a, bool(re.search(r"[*?\[{~]", a))) for a in alts] if len(alts) > 1 else [w]


def _user_homes():
    """R2-03: the folders whose .aid/state.json is the user-level file (T3 A5), as parts."""
    return {tuple(p for p in k.split("/")[:-2] if p) for k in _user_state_files()}


def _glob_names_control(text, vcwd, targets=_CONTROL_GLOB_TARGETS, hidden=False):
    """R1-06: may this glob write target (`.aid/stat?.json`, `.aid/st*e.json`,
    `.aid/pipeline/conf?g.json`) expand to one of `targets`? Judged on the trailing path
    components, case-folded, brace alternatives expanded; vcwd (when known) is prefixed to a
    relative target, so `cd .aid && echo x > stat?.json` counts.
    R2-03: a leading ~ / $HOME is the user's home, and the user-level ~/.aid/state.json stays
    exempt (T3 A5). Bash globs do not match a dot name (`*` is not `.aid`) unless the pattern
    component starts with a dot; PowerShell wildcards do (hidden=True)."""
    t = _expand_home(text).replace("\\", "/").casefold()
    if not re.search(r"[*?\[]", t) or re.search(r"[$`]", t):
        return False
    if vcwd and vcwd != SUSPICIOUS and not (t.startswith("/") or re.match(r"^[a-z]:/", t)):
        t = _key(vcwd).casefold().rstrip("/") + "/" + t
    homes = _user_homes()
    for alt in _brace_alternatives(t):
        parts = [p.rstrip(". ") or p for p in alt.split("/") if p not in ("", ".")]
        for ctl in targets:
            c = ctl.split("/")
            if len(parts) >= len(c) and all(
                    fnmatch.fnmatchcase(x, p) and (hidden or not x.startswith(".") or p.startswith("."))
                    for p, x in zip(parts[-len(c):], c)):
                if ctl == ".aid/state.json" and tuple(parts[:-2]) in homes:
                    continue                    # the user-level session file (T3 A5)
                return True
    return False


def _record_assignments(assigns, variables):
    """R1-06: `f=.aid/state.json; echo x > $f`: remember plain `name=value` shell assignments
    (a segment of assignments only) so a later bare `$name` target is judged on its value."""
    for a in assigns:
        name, _, value = a.text.partition("=")
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            variables[name] = Word(value, a.dynamic)


def _assigned_word(w, variables):
    """R1-06: the remembered value of a bare `$name` / `${name}` word, else the word."""
    m = re.match(r"^\$(?:\{([A-Za-z_][A-Za-z0-9_]*)\}|([A-Za-z_][A-Za-z0-9_]*))$", w.text)
    if w.dynamic and m and (m.group(1) or m.group(2)) in variables:
        return variables[m.group(1) or m.group(2)]
    return w


def state_file_reason(path):
    """T16-1/2: the reason given for a write to a project .aid/state.json."""
    return ("'{}' is the AID project state file (an AID control file, protected in every "
            "folder). Only aid_session.py writes it; to create it "
            "run /aid-init, which asks the user to confirm python \"{}/hooks/aid_session.py\" "
            "init <role> <phase>").format(path, str(LIVE_ROOT).replace("\\", "/"))


def write_tool_state_target(path, cwd):
    """T16-1: does a Write-tool path (no shell expansion) name a project .aid/state.json?
    Both the Win32 (stripped) and the raw trailing-dot form are judged (AC-35)."""
    if not isinstance(path, str) or not path:
        return False
    norms = [normalize(path, cwd, literal=True, strip=s) for s in (True, False)]
    if SUSPICIOUS in norms:
        # R1-04: an NTFS stream spelling (`.aid/state.json::$DATA` is the file itself,
        # `.aid/STATE.json:alt` creates it) is SUSPICIOUS, which is_project_state does not
        # judge. Drop each component's `:stream[:$type]` and trailing dots/spaces.
        p = re.sub(r"^[A-Za-z]:", "", path.replace("\\", "/")).casefold()
        parts = [re.sub(r":.*$", "", c).rstrip(". ") for c in p.split("/")]
        if len(parts) >= 2 and parts[-2:] == [".aid", "state.json"]:
            return True
    return any(is_project_state(n) for n in norms)


_PS_WRITERS = re.compile(r"(?:^|[\s;|&(])(?:set-content|add-content|out-file|new-item|copy-item|"
                         r"move-item|rename-item|tee-object|sc|ac|ni|cpi|mi|rni|ren|copy|cp|move|mv|"
                         r"tee)(?=$|[\s;|&)])|>|::(?:write|append)all", re.I)
# R2-03 / R2-05: PowerShell commands whose first operand is a SOURCE (only the destination is
# written), and the ones that delete their operands.
_PS_COPY_CMDS = {"copy-item", "cpi", "copy", "cp", "move-item", "mi", "move", "mv", "rename-item",
                 "rni", "ren"}
_PS_REMOVE_CMDS = {"remove-item", "ri", "rm", "del", "erase", "rd", "rmdir", "clear-content", "clc"}


def _ps_glob_targets(low, remove=False):
    """R2-03: the words of a PowerShell command (quotes and backticks removed, case-folded,
    '/' separators) that it may write: redirect targets; the destination of Copy-Item /
    Move-Item / Rename-Item (-Destination / -NewName or the second positional), never its
    source; every operand of another writer (_PS_WRITERS) and, with remove=True (R2-05),
    of Remove-Item / ri / rm / del / erase / rd / rmdir / Clear-Content."""
    out = []
    for seg in re.split(r"[;|&\n]+", low):
        toks = [t for t in re.split(r"[\s,()]+", seg) if t]
        for i, t in enumerate(toks):
            m = re.match(r"^\d?>>?(.*)$", t)
            if m:
                out.append(m.group(1) or (toks[i + 1] if i + 1 < len(toks) else ""))
        if not toks:
            continue
        cmd, args = toks[0], toks[1:]
        if cmd in _PS_COPY_CMDS:
            pos, dest, k = [], None, 0
            while k < len(args):
                a = args[k]
                if a.startswith("-"):
                    pname, _, val = a.partition(":")
                    takes = pname.startswith(("-de", "-ne", "-pa", "-li"))
                    if takes and not val:
                        val, k = (args[k + 1] if k + 1 < len(args) else ""), k + 1
                    if pname.startswith(("-de", "-ne")):
                        dest = val
                elif not re.match(r"^\d?>", a):
                    pos.append(a)
                k += 1
            dest = dest if dest is not None else (pos[1] if len(pos) > 1 else None)
            if dest:
                out.append(dest)
        elif (remove and cmd in _PS_REMOVE_CMDS) or _PS_WRITERS.search(seg):
            out += [a.partition(":")[2] if a.startswith("-") else a for a in args]
    return [t for t in out if t]


_SH_C_OPT = re.compile(r"^-[A-Za-z]*c[A-Za-z]*$")
# R3-06: text that names a `.aid` path component (quotes and backslashes removed first).
_NAMES_AID = re.compile(r"(?:^|[^A-Za-z0-9_.-])\.aid(?![A-Za-z0-9_-])", re.I)


def _shell_c_bodies(words):
    """R3-03 (T16 fix cycle 3): the static text a `bash|sh|dash|zsh|ksh -c '<text>'` in this
    segment runs, also behind nohup/env/timeout/... prefixes: a shell word, its options
    (-e, -o pipefail, --login), then a -c cluster (-c, -ec, -lc) gives the next word."""
    out = []
    for i, w in enumerate(words):
        if w.dynamic or not _SHELLS.match(re.split(r"[/\\]", w.text)[-1]):
            continue
        k = i + 1
        while k < len(words) and words[k].text.startswith(("-", "+")):
            a = words[k].text
            if _SH_C_OPT.match(a):
                # R4-04(1): `bash -c -- '<text>'`: the body follows the `--`.
                j = k + 2 if k + 1 < len(words) and words[k + 1].text == "--" else k + 1
                if j < len(words):
                    out.append(words[j].text)
                break
            # R4-04(1): options that take an argument (--rcfile F, --init-file F, -o/-O opt)
            # are skipped with it; `--` is skipped too (fail closed: a later -c still counts).
            k += 2 if a in ("-o", "+o", "-O", "+O", "--rcfile", "--init-file") else 1
    return out


def _env_chdir(words):
    """R3-03: the folder (a Word) that `env -C DIR` / `env -CDIR` / `env --chdir[=]DIR` runs
    its command in, else None."""
    for i, w in enumerate(words):
        if w.dynamic or re.sub(r"\.exe$", "", re.split(r"[/\\]", w.text)[-1].lower()) != "env":
            continue
        k = i + 1
        while k < len(words):
            a = words[k].text
            if a in ("-C", "--chdir"):
                return words[k + 1] if k + 1 < len(words) else None
            if a.startswith("--chdir="):
                return Word(a.split("=", 1)[1], words[k].dynamic)
            if re.match(r"^-[A-Za-z]*C.+", a) and not a.startswith("--"):
                return Word(a[a.index("C") + 1:], words[k].dynamic)
            if a in ("-u", "--unset", "-S", "--split-string"):
                k += 2
            elif a.startswith("-") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", a):
                k += 1
            else:
                break
        return None
    return None


def _strip_streams(text):
    """R3-03: `state.json:x` / `.aid/state.json::$DATA` names the file itself (NTFS stream):
    each component without its `:stream[:$type]` (a leading drive `C:` kept)."""
    m = re.match(r"^([A-Za-z]:)(.*)$", text)
    drive, rest = (m.group(1), m.group(2)) if m else ("", text)
    return drive + "/".join(c.split(":", 1)[0] for c in rest.replace("\\", "/").split("/"))


def state_write_reason(command, cwd, powershell=False, _aid_named=False, _nested=False, in_aid=True):
    """
    T16-2 (E2): a Bash / PowerShell command that writes a project .aid/state.json, in EVERY
    folder: a redirect or writer target (tee, cp, mv, ln, touch, install, dd of=, sed -i)
    that resolves to it, or (the T15-10 literal rule) a non-read-only command whose text
    names .aid/state.json. Reads (cat, jq, Get-Content) stay allowed. None if not.
    R3-03: a static `bash -c '<text>'` body is judged in the folder it runs in, `env -C DIR`
    runs its command in DIR, `git [-C D] mv SRC DIR/` writes DIR/<basename SRC>, and an NTFS
    `:stream` suffix names the file itself.
    T16 B1 (E2 bounded): outside AID projects (in_aid False) a Bash write is judged in the
    hook's cwd only, on the text it names (the literal name, its quote/brace/glob spellings,
    a variable or substitution holding it). A write reached through a cwd change (cd,
    pushd, popd, env -C, git -C), a shell -c body run elsewhere, or interpreter code is an
    accepted, documented residual (like A1). Inside AID every form is judged.
    """
    # R1-02: quote removal and backslashes cannot hide the name from this prefilter.
    # R1-06: a glob target (`.aid/stat?.json`) is judged below. R2-01: so is a brace word
    # (`.aid/state.{json,x}`, `.aid/state.js{on,}`) that splits the name.
    if ("state.json" not in re.sub(r"[\"'\\`]", "", command).casefold()
            and not re.search(r"[*?\[]", command) and not re.search(r"\{[^{}]*,", command)):
        return None
    if powershell:
        # R1-03: a writer whose text names both the .aid folder and state.json (after
        # backticks and quotes are removed): `./.aid/./state.json`, `cd .aid; sc state.json`,
        # `Move-Item state.json .aid`, `".aid\st`ate.json"`. Or a glob that may match it
        # (R2-03: only a write target: the destination of Copy-Item/Move-Item, not its source).
        low = re.sub(r"[`\"']", "", command).replace("\\", "/").casefold()
        if _PS_WRITERS.search(low) and (
                (re.search(r"(?:^|[^a-z0-9_.-])\.aid(?:$|[^a-z0-9_-])", low) and "state.json" in low)
                or any(_glob_names_control(t, None, (".aid/state.json",), hidden=True)
                       for t in _ps_glob_targets(low))):
            return state_file_reason(".aid/state.json")
        return None
    try:
        segments, subs = lex(command)
    except ParseError:
        return state_file_reason(".aid/state.json") if ".aid/state.json" in \
            command.replace("\\", "/").casefold() else None
    # R3-06: does this command (or the one whose `bash -c` body this is) name a .aid folder?
    aid_named = _aid_named or bool(_NAMES_AID.search(re.sub(r"[\"'\\`]", "", command)))
    for body in subs:
        # R2-02: a substitution runs in the same folder (a subshell of this one).
        reason = state_write_reason(body, cwd, _aid_named=aid_named, in_aid=in_aid)
        if reason:
            return reason

    variables = {}
    # R2-02: True once a cd / pushd / popd went somewhere this check cannot resolve: a bare
    # `state.json` target may then be the project state file. R3-06: only for a directory
    # stack move (`cd -`, `popd`, `pushd +1`, which can return to a .aid folder of an earlier
    # call), or when this command names a .aid folder (`cd "$D/.aid"`); `cd "$TMPDIR"` alone
    # does not (a state.json there is an ordinary application file, as at 5f8f199).
    unknown = [in_aid and cwd is None and (not _nested or aid_named)]       # T16 B1

    def hit(w, vcwd, target=True):
        return any(hit_one(a, vcwd, target) for a in _brace_words(_assigned_word(w, variables)))

    def hit_one(w, vcwd, target):
        if ".aid/state.json" in w.text.replace("\\", "/").casefold():
            n = None if w.dynamic else normalize(w.text, vcwd)
            return n in (None, SUSPICIOUS) or not _pkey(n) in _user_state_files()
        if w.dynamic:       # R1-06: only a write target's glob, not `python x.py .aid/*.json`
            return target and _glob_names_control(w.text, vcwd, (".aid/state.json",))
        if target and unknown[0] and not re.match(r"^(?:/|[A-Za-z]:)", w.text.replace("\\", "/")) and [
                c.split(":", 1)[0].rstrip(". ").casefold() for c in re.split(r"[/\\]", w.text)
                if c not in ("", ".")] == ["state.json"]:
            return True
        n = normalize(w.text, vcwd)
        if n == SUSPICIOUS:                 # R3-03: `state.json:x` is the state file's stream
            n = normalize(_strip_streams(w.text), vcwd)
        return is_project_state(n)

    # R1-06: a redirect target built by a substitution that names the state file.
    sub_names = any(".aid/state.json" in b.replace("\\", "/").casefold() for b in subs)
    vcwd = cwd
    for seg in segments:
        for w in seg.writes:
            if hit(w, vcwd) or (sub_names and w.dynamic and re.search(r"[$`]", w.text)):
                return state_file_reason(w.text)
        words = list(seg.words)
        while words and words[0].text in KEYWORDS_PREFIX and not words[0].dynamic:
            words.pop(0)
        assigns = []
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?=", words[0].text):
            assigns.append(words.pop(0))
        if not words:
            _record_assignments(assigns, variables)
            continue
        t = words[0].text
        name = t.lower() if not words[0].dynamic and "/" not in t and "\\" not in t else None
        if name and IS_WIN:
            name = re.sub(r"\.(exe|cmd|bat)$", "", name)
        if name in ("builtin", "command") and len(words) > 1 and not words[1].dynamic and \
                words[1].text.lower() in ("cd", "pushd", "popd"):
            words = words[1:]                       # R2-02: `builtin cd`, `command cd`
            name = words[0].text.lower()
        args = [w.text for w in words[1:]]
        if name in ("cd", "pushd", "popd") and not in_aid:
            continue                        # T16 B1: no cwd tracking outside AID (residual)
        if name in ("cd", "pushd", "popd"):
            # `mkdir -p .aid && cd .aid`: the folder may exist only once the line runs.
            # R2-02: options -P -L -e -@ (pushd -n) and `--` are skipped; pushd is a cd.
            rest = list(words[1:])
            while rest and not rest[0].dynamic and re.match(r"^-[PLe@n]+$", rest[0].text):
                rest.pop(0)
            if rest and rest[0].text == "--" and not rest[0].dynamic:
                rest.pop(0)
            stack = name == "popd" or len(rest) > 1 or (name == "pushd" and not rest) or (
                rest and re.match(r"^[-+]", rest[0].text))
            if stack:
                n = None
            else:
                dest = _home_word(_assigned_word(rest[0], variables)) if rest else \
                    Word(os.path.expanduser("~"), False)
                n = None if dest.dynamic else normalize(dest.text, vcwd)
            vcwd = n if n not in (None, SUSPICIOUS) else None
            unknown[0] = vcwd is None and bool(stack or aid_named)     # R3-06
            continue
        # R3-03: `env -C DIR cmd` runs cmd in DIR; `bash -c '<text>'` runs <text> in that folder.
        scwd, s_unknown = vcwd, unknown[0]
        ecd = _env_chdir(words)
        if ecd is not None and in_aid:      # T16 B1: env -C outside AID is a residual
            ed = _home_word(_assigned_word(ecd, variables))
            n = None if ed.dynamic else normalize(ed.text, vcwd)
            scwd = n if n not in (None, SUSPICIOUS) else None
            s_unknown = scwd is None and aid_named
        for body in _shell_c_bodies(words):
            reason = state_write_reason(body, scwd, _aid_named=aid_named or s_unknown, _nested=True,
                                        in_aid=in_aid)
            if reason:
                return reason
        if name == "git":
            # R3-03: `git [-C D] mv SRC... DEST/` writes DEST/<basename SRC> (like mv).
            sub, rest, gcwd = _git_split(args, scwd)
            if sub == "mv" and isinstance(rest, list) and gcwd is not None:
                pseudo = [Word("mv", False)] + [Word(a, bool(re.search(r"[$`*?\[{~]", a))) for a in rest
                                                 if a != "--"]
                for w in _cp_mv_targets("mv", pseudo, [a for a in rest if a != "--"], gcwd, dest_only=True)[0]:
                    if hit(w, gcwd):
                        return state_file_reason(w.text)
        saved_unknown, unknown[0] = unknown[0], s_unknown
        try:
            reason = _state_segment_reason(name, words, args, scwd, hit)
        finally:
            unknown[0] = saved_unknown
        if reason:
            return reason
    return None


def _state_segment_reason(name, words, args, vcwd, hit):
    """state_write_reason for one simple command run in vcwd (R3-03: split out so an
    `env -C DIR` command is judged in DIR)."""
    if _phase4_exempt(name, words, args):
        return None
    # R2-03: only a write destination is judged on its resolved path (and its glob or
    # braces): redirects, the cp/mv/ln/install target, tee/touch/sed -i files, dd of=.
    # A cp/mv/ln/install source is read or moved away, never written. Any other operand
    # keeps the T15-10 literal rule (text naming .aid/state.json) only.
    if name in ("cp", "mv", "ln", "install"):
        targets, others = _cp_mv_targets(name, words, args, vcwd, dest_only=True)[0], []
    else:
        in_place = name == "sed" and any(
            a.startswith("--in-place") or re.match(r"^-[A-Za-z]*i", a) and not a.startswith("--")
            for a in args)
        targets = [w for w in words[1:] if not w.text.startswith("-")] if (
            name in ("tee", "touch") or in_place) else []
        targets += [Word(a.split("=", 1)[1], w.dynamic) for w, a in zip(words[1:], args)
                    if name == "dd" and a.startswith("of=")]
        others = list(words[1:]) + [Word(a.split("=", 1)[1], w.dynamic) for w, a in zip(words[1:], args)
                                    if a.startswith("--") and "=" in a]
    for w in targets:
        if hit(w, vcwd):
            return state_file_reason(w.text)
    if name == "git":
        # R4-02: `git [-C D] log|diff|show --output[=]<f>` writes <f> (in D).
        gcwd = _git_split(args, vcwd)[2]
        for k, a in enumerate(args):
            out = Word(a.split("=", 1)[1], words[k + 1].dynamic) if a.startswith("--output=") else (
                words[k + 2] if a == "--output" and k + 2 < len(words) else None)
            if out is not None and hit(out, gcwd):
                return state_file_reason(out.text)
    for w in others:
        if hit(w, vcwd, False):
            return state_file_reason(w.text)
    return None


def is_plans_file(norm):
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    plans = _key(os.path.realpath(os.path.join(config_dir, "plans"))).rstrip("/") + "/"
    return bool(norm) and norm not in (None, SUSPICIOUS) and norm.startswith(plans)


def write_target_verdict(path, cwd, root, phase, rules, literal=False):
    """
    May the agent write `path`? Returns None if yes, else the reason.

    One rule set for the Write tool, mkdir targets before Phase 4, and Phase 4+ Bash write
    targets:
      - protected control files: never (every phase)
      - Phase >= code_write_min_phase: anything else is allowed
      - before that: only under allowed_write_prefixes, never inside .git, never outside
        the project (except Claude Code's own plan files), never an undecidable path.
    AC-35: a trailing dot/space component is judged in both its stripped (Win32) and raw
    (Node, \\\\?\\) form; either one refused means refused.
    """
    return (_target_verdict(path, cwd, root, phase, rules, literal, True)
            or _target_verdict(path, cwd, root, phase, rules, literal, False))


def _hard_linked(norm):
    """An existing regular file with more than one name. ponytail: denies every multi-link
    file instead of samefile-matching the protected set; tolerable for a Write target."""
    try:
        st = os.stat(norm)
    except (OSError, ValueError):
        return False
    return stat.S_ISREG(st.st_mode) and st.st_nlink > 1


def _target_verdict(path, cwd, root, phase, rules, literal, strip):
    norm = normalize(path, cwd, literal, strip)
    if norm == SUSPICIOUS:
        return "refusing an obfuscated path form ({!r})".format(path)
    if norm in SINKS and not literal:
        # Shell redirect targets only. A literal name (Write tool, mkdir) is a real file:
        # Git Bash `mkdir nul` and Node `writeFileSync('nul')` create one (measured).
        return None
    if norm is not None and is_protected(norm):
        return "'{}' is an AID control file (protected in every phase)".format(path)
    if norm is not None and norm not in SINKS and _hard_linked(norm):
        # realpath does not reveal hard links: another name may be a control file.
        return ("'{}' has other hard links, and AID cannot tell whether one of them is a "
                "control file; refused in every phase").format(path)
    if norm is None and (mentions_protected(path) or (
            cwd is None and not os.path.isabs(path)
            and os.path.basename(path.replace("\\", "/")).casefold() in PROTECTED_BASENAMES)):
        return "'{}' may be an AID control file (cannot resolve it; protected in every phase)".format(path)
    if phase is None or phase >= rules.get("code_write_min_phase", 4):
        return None
    if norm is None:
        return "cannot tell where '{}' points (variable, glob or ~); not allowed before Phase {}".format(
            path, rules.get("code_write_min_phase", 4))
    if is_plans_file(norm):
        return None
    root_k = _key(os.path.realpath(str(root))).rstrip("/") + "/"
    if not (norm + "/").startswith(root_k):
        return "'{}' is outside the project".format(path)
    rel = norm[len(root_k):]
    # .git, .GIT, ".git." and ".git " all name the same directory on Windows.
    if any(part.casefold().rstrip(" .") == ".git" for part in rel.split("/")):
        return "'{}' is inside .git (hooks and config there run code)".format(path)
    # T15-1 (R-01): Claude Code loads skills, agents, commands, output styles, rules and
    # hooks from .claude/<dir>/; a file there runs with the agent's tools, so before the
    # execute phase it is not a plain doc even though .claude/ is an allowed prefix.
    parts = [part.casefold().rstrip(" .") for part in rel.split("/")]
    if any(a == ".claude" and b in CLAUDE_CAPABILITY_DIRS for a, b in zip(parts, parts[1:])):
        return ("'{}' is in a Claude Code capability folder (.claude/{}/): what it holds is "
                "loaded as skills, agents, commands or rules, so it waits for Phase {} like "
                "source (.claude/plans/ and other .claude/ files stay writable)").format(
            path, "|".join(CLAUDE_CAPABILITY_DIRS), rules.get("code_write_min_phase", 4))
    if len(parts) >= 2 and parts[-2] == ".claude" and parts[-1] in CLAUDE_EXEC_FILES:
        return ("'{}' is a file Claude Code loads or runs (.claude/{}): it waits for Phase {} "
                "like source").format(path, "|".join(CLAUDE_EXEC_FILES), rules.get("code_write_min_phase", 4))
    for prefix in rules.get("allowed_write_prefixes", []):
        if (rel + "/").startswith(_key(prefix)):
            return None
    return "'{}' is source, not docs/specs/tests (allowed: {})".format(
        path, ", ".join(rules.get("allowed_write_prefixes", [])))


# ---------------------------------------------------------------------------
# Before Phase 4: strict tokenizer (AC-1..AC-6, AC-15)
# ---------------------------------------------------------------------------

class Denied(Exception):
    """The command uses syntax the pre-Phase-4 gate does not accept."""


class SWord(object):
    __slots__ = ("text", "quoted", "glob")

    def __init__(self, text, quoted, glob):
        self.text, self.quoted, self.glob = text, quoted, glob


class SSeg(object):
    __slots__ = ("words", "redirect", "op")

    def __init__(self, words, redirect, op=None):
        # op: the separator that ended this segment (";", "|", "||", "&&"), None at the end
        self.words, self.redirect, self.op = words, redirect, op


DQ_DOLLAR = ("'$' and backticks expand even inside double quotes; put literal text in "
             "single quotes (e.g. grep 'foo$' docs/a.md)")


def _devnull_end(cmd, j):
    """cmd[j:] must be optional blanks + '/dev/null' + a word boundary; return the end index."""
    while j < len(cmd) and cmd[j] in " \t":
        j += 1
    if cmd.startswith("/dev/null", j):
        k = j + len("/dev/null")
        if k >= len(cmd) or cmd[k] in " \t\n;|&":
            return k
    raise Denied("redirection is allowed only to /dev/null (or 2>&1) before Phase 4; "
                 "use the Write tool to create files")


def tokenize_strict(cmd):
    """
    Split a command into simple commands joined by | && || ; or newline, implementing
    bash's quoting rules exactly and raising Denied on anything ambiguous or dynamic:
      - single quotes: literal up to the next ' (a backslash inside is literal);
      - double quotes: \\ is one backslash; \\ before " $ ` or newline is denied;
        any other backslash is literal; $ and ` are denied;
      - unquoted: backslash, $, `, { } ( ), <, a lone &, |& are denied; > only as
        2>&1, >/dev/null, 2>/dev/null, &>/dev/null;
      - an unterminated quote is denied (carriage returns are refused by _pre4 first).
    """
    segs, words, redirect = [], [], False
    buf, has, quoted, glob = [], False, False, False
    i, n = 0, len(cmd)

    def end_word():
        nonlocal buf, has, quoted, glob
        if has:
            words.append(SWord("".join(buf), quoted, glob))
        buf, has, quoted, glob = [], False, False, False

    def end_seg(op=None):
        nonlocal words, redirect
        end_word()
        if words:
            segs.append(SSeg(words, redirect, op))
        words, redirect = [], False

    while i < n:
        c = cmd[i]
        if c == "'":
            j = cmd.find("'", i + 1)
            if j < 0:
                raise Denied("unterminated single quote")
            buf.append(cmd[i + 1:j])
            has = quoted = True
            i = j + 1
            continue
        if c == '"':
            j = i + 1
            while True:
                if j >= n:
                    raise Denied("unterminated double quote")
                d = cmd[j]
                if d == '"':
                    break
                if d in "$`":
                    raise Denied(DQ_DOLLAR)
                if d == "\\":
                    nxt = cmd[j + 1:j + 2]
                    if nxt == "\\":
                        buf.append("\\")
                        j += 2
                        continue
                    if nxt in ('"', "$", "`", "\n"):
                        raise Denied("a backslash before \" $ ` or a newline inside double "
                                     "quotes is ambiguous; use single quotes")
                buf.append(d)
                j += 1
            has = quoted = True
            i = j + 1
            continue
        if c in "$`":
            raise Denied("expansions and substitutions ($, `) cannot be checked before "
                         "Phase 4; write literal values (single quotes keep $ literal)")
        if c == "\\":
            raise Denied("unquoted backslash; quote the word instead (\"C:\\dir\\file\" is fine)")
        if c in "{}":
            raise Denied("unquoted braces (brace expansion / grouping) are not allowed before "
                         "Phase 4; quote them or list the paths")
        if c in "()":
            raise Denied("subshells, groups and arithmetic are not allowed before Phase 4")
        if c == "#" and not has:
            while i < n and cmd[i] != "\n":
                i += 1
            continue
        if c in " \t":
            end_word()
            i += 1
            continue
        if c in "\n;":
            end_seg(";")
            i += 1
            continue
        if c == "|":
            if cmd[i + 1:i + 2] == "&":
                raise Denied("|& is not allowed before Phase 4")
            end_seg("||" if cmd[i + 1:i + 2] == "|" else "|")
            i += 2 if cmd[i + 1:i + 2] == "|" else 1
            continue
        if c == "&":
            if cmd[i + 1:i + 2] == "&":
                end_seg("&&")
                i += 2
                continue
            if cmd[i + 1:i + 2] == ">" and not has:
                i = _devnull_end(cmd, i + 2)
                redirect = True
                continue
            raise Denied("background jobs (&) are not allowed before Phase 4")
        if c == "<":
            raise Denied("input redirection, heredocs and process substitution are not allowed "
                         "before Phase 4; pass the file name as an argument")
        if c == ">":
            fd = "".join(buf) if has and not quoted and "".join(buf).isdigit() else None
            if fd is not None:
                buf, has, quoted, glob = [], False, False, False
            else:
                end_word()
                fd = ""
            nxt = cmd[i + 1:i + 2]
            if nxt == "&":
                k = i + 3
                if fd == "2" and cmd[i + 2:i + 3] == "1" and (k >= n or cmd[k] in " \t\n;|&"):
                    i = k
                    redirect = True
                    continue
                raise Denied("only 2>&1 is allowed as a descriptor redirection before Phase 4")
            if fd not in ("", "2") or nxt in (">", "|"):
                raise Denied("redirection is allowed only to /dev/null (or 2>&1) before Phase 4; "
                             "use the Write tool to create files")
            i = _devnull_end(cmd, i + 1)
            redirect = True
            continue
        if c in "*?[":
            glob = True
        buf.append(c)
        has = True
        i += 1
    end_seg()
    return segs


# ---------------------------------------------------------------------------
# Before Phase 4: command tables (AC-7..AC-13, AC-20..AC-24)
# ---------------------------------------------------------------------------

# Every entry is here because it has NO flag that writes a file or runs a program, under
# any spelling (no -o/--output, no --exec, no --compress-program, no script argument).
# Do not add a tool that has such a flag; add a narrow table like GIT_OPTIONS instead.
READ_ONLY = frozenset({
    "ls", "dir", "cat", "head", "tail", "wc", "grep", "egrep", "fgrep", "cut", "tr", "jq",
    "diff", "cmp", "comm", "nl", "column", "stat", "du", "df", "basename", "dirname",
    "realpath", "pwd", "echo", "true", "false", "which", "where", "type", "sha256sum",
    "sha1sum", "md5sum", "uname", "whoami",
})

# `<tool> --version` and nothing else (AC-10).
VERSION_TOOLS = frozenset({"node", "npm", "npx", "pnpm", "yarn", "bun", "deno", "python",
                           "python3", "py", "pip", "pip3", "git", "gh", "claude", "tsc"})

# git before Phase 4: subcommand -> (exact options, regex for attached values). Every token
# starting with '-' must match one of them; '--' ends options. Nothing here writes outside
# .git (index, objects, refs) or runs a program the agent chose.
_FMT = r"--(format|pretty)=.*"
GIT_OPTIONS = {
    "status": ({"-s", "--short", "-b", "--branch", "--porcelain", "--long", "-v", "--verbose",
                "--ignored", "--show-stash", "-u", "-uno", "-unormal", "-uall"},
               r"--porcelain=v[12]|--untracked-files=(no|normal|all)"),
    "log": ({"--oneline", "--stat", "--shortstat", "--numstat", "--name-only", "--name-status",
             "-p", "--patch", "--graph", "--decorate", "--all", "--reverse", "--no-merges",
             "--merges", "--first-parent", "--abbrev-commit", "--follow", "-n", "--pretty",
             "--no-color"},
            r"-\d+|-n\d+|--max-count=\d+|--(since|until|after|before|author|grep|date)=.*|" + _FMT),
    "diff": ({"--stat", "--shortstat", "--numstat", "--name-only", "--name-status", "--cached",
              "--staged", "--no-color", "-w", "--word-diff", "--check", "--quiet",
              "--exit-code", "--minimal", "--no-ext-diff", "--no-textconv"},
             r"-U\d+|--unified=\d+"),
    "show": ({"--stat", "--shortstat", "--name-only", "--name-status", "--oneline", "-s",
              "--no-patch", "--quiet", "--abbrev-commit", "--no-color", "--pretty"}, _FMT),
    "rev-parse": ({"--abbrev-ref", "--short", "--show-toplevel", "--git-dir",
                   "--is-inside-work-tree", "--verify", "--symbolic-full-name", "-q", "--quiet"},
                  r"--short=\d+"),
    "ls-files": ({"-c", "--cached", "-m", "--modified", "-o", "--others", "-d", "--deleted",
                  "--exclude-standard", "-s", "--stage", "--error-unmatch"}, None),
    "blame": ({"-w", "-s", "-e", "-l", "--porcelain", "-L"}, r"-L\d+(,\d+)?"),
    "branch": ({"-a", "--all", "-r", "--remotes", "-v", "-vv", "--list", "--show-current",
                "--merged", "--no-merged", "--contains"}, None),
    "add": ({"-A", "--all", "-u", "--update", "-n", "--dry-run", "-v", "--verbose"}, None),
    "commit": ({"-m", "-a", "--all", "-q", "--quiet", "-v", "--amend", "--no-edit", "-s",
                "--signoff", "--allow-empty"}, None),
}


def _same_dir(a, b):
    return a is not None and _key(os.path.realpath(a)).rstrip("/") == _key(os.path.realpath(str(b))).rstrip("/")


def _git_pre4(toks, cwd, root):
    if toks[:1] == ["--no-pager"]:
        toks = toks[1:]
    if not toks or toks[0] not in GIT_OPTIONS:
        return "git {} is not allowed before Phase 4 (allowed: {})".format(
            toks[0] if toks else "", ", ".join(sorted(GIT_OPTIONS)))
    if not _same_dir(cwd, root):
        return "git runs only in the project root before Phase 4 (a repository elsewhere " \
               "can carry its own hooks and config)"
    exact, pattern = GIT_OPTIONS[toks[0]]
    for t in toks[1:]:
        if t == "--":
            break
        if t.startswith("-") and t not in exact and not (pattern and re.fullmatch(pattern, t)):
            return "git {} option {} is not on AID's pre-Phase-4 list".format(toks[0], t)
    return None


def _cmd_name(word):
    t = word.text.lower()
    return re.sub(r"\.exe$", "", t) if IS_WIN else t


_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\[.*\])?\+?=")
_SESSION_ARG = re.compile(r"^[A-Za-z0-9 ._:-]+$")


def _is_plugin_session(command):
    """AC-23: exactly `python|python3|py "<absolute path of this plugin's aid_session.py>" args`."""
    try:
        segs = tokenize_strict(command)
    except Denied:
        return False
    if len(segs) != 1 or segs[0].redirect or len(segs[0].words) < 2:
        return False
    w = segs[0].words
    if w[0].quoted or _cmd_name(w[0]) not in ("python", "python3", "py"):
        return False
    script = w[1].text
    if not (os.path.isabs(script.replace("\\", "/")) or re.match(r"^[A-Za-z]:[/\\]", script)):
        return False
    if normalize(script, None, literal=True) != _key(os.path.realpath(str(SESSION_SCRIPT))):
        return False
    return all(_SESSION_ARG.match(x.text) for x in w[2:])


# AC-22: `git commit [options] -m "$(cat <<'DELIM'` ... first exact DELIM line ... `)"`.
_COMMIT_IDIOM = re.compile(r"(git commit(?: [^\n]*?)?) -m \"\$\(cat <<(['\"])([A-Za-z_][A-Za-z0-9_]*)\2\n")


def _commit_idiom(command, cwd, root, phase, rules, extra):
    """None = not this idiom; "" = allowed; other str = denied reason."""
    m = _COMMIT_IDIOM.match(command)
    if not m:
        return None
    # tokenize_strict drops a '# ...' comment, but bash then comments out the heredoc
    # opener too, so every "body" line would run as a command. No '#' in the head at all.
    if "#" in m.group(1):
        return "'#' is not allowed in the commit-idiom head (bash would comment out the heredoc)"
    try:
        head = tokenize_strict(m.group(1))
    except Denied as e:
        return str(e)
    if len(head) != 1 or [w.text for w in head[0].words[:2]] != ["git", "commit"] or head[0].redirect:
        return "the commit-message heredoc is allowed only on a plain 'git commit'"
    reason = _pre4(m.group(1), cwd, root, phase, rules, extra)
    if reason:
        return reason
    lines = command[m.end():].split("\n")
    delim = m.group(3)
    if delim not in lines:
        return "heredoc body has no closing {} line".format(delim)
    # Inside $( ) bash 5.2 also ends the body at a line that starts with the delimiter and
    # holds a ')' ("EOF)", "EOF )", "EOFx)", measured: touch ran). Refuse any body line
    # that names the delimiter and has a ')' -- a superset, so no exact bash model needed.
    if any(delim in ln and ")" in ln for ln in lines[:lines.index(delim)]):
        return "a heredoc body line may not contain both {} and ')'".format(delim)
    after = lines[lines.index(delim) + 1:]          # the FIRST exact delimiter line ends it
    if after and after[-1] == "":
        after = after[:-1]
    if len(after) != 1 or not after[0].startswith(')"'):
        return "only ')\"' may follow the heredoc delimiter"
    tail = after[0][2:]
    if tail == "":
        return ""
    if not tail.startswith(" && "):
        return "only ')\"' or ')\" && <command>' may follow the heredoc delimiter"
    return _pre4(tail[4:], cwd, root, phase, rules, extra) or ""


def _may_run_named_file(command):
    """T16-12: may an interpreter (or a shell, or a word built at run time) run something in
    this command? Read-only text that only names aid_session.py (grep, git log, ls) is not."""
    segs = _shell_segments(command)
    if segs is None:
        return True
    return any(_interpreter_at(w, _ANY_INTERP, shc=lambda _p: True)[0] is not None
               or _interpreter_at(w, _SHELLS, shc=lambda _p: True)[0] is not None for w in segs)


def _pre4(command, cwd, root, phase, rules, extra):
    """Before Phase 4, block-mode semantics: None = allowed, else the reason."""
    # First, before the heredoc idiom: Git Bash ends a heredoc at "EOF\r" (measured), so a
    # CR anywhere would let the idiom's body end earlier than this gate thinks.
    if "\r" in command:
        return ("carriage return in the command (Git Bash ends heredocs and words differently "
                "with it); use plain newlines")
    if _is_plugin_session(command):
        return None
    if "aid_session" in command.lower() and _may_run_named_file(command):
        # T3 review: a near-miss used to get the generic "'python' is not on the read-only
        # list", which sent the agent back to the very command it was running.
        return ("this aid_session.py call is not in the one allowed form: a single command, "
                "lower-case python, python3 or py, this plugin's script as an absolute path "
                "({}), and plain arguments. Free text (--note and similar) may only contain "
                "letters, digits, spaces and . _ : - ; leave a flag out when its text is empty"
                ).format(str(SESSION_SCRIPT).replace("\\", "/"))
    idiom = _commit_idiom(command, cwd, root, phase, rules, extra)
    if idiom is not None:
        return idiom or None
    try:
        segs = tokenize_strict(command)
    except Denied as e:
        return str(e)
    min_phase = rules.get("code_execute_min_phase", 4)
    vcwd = cwd
    for k, seg in enumerate(segs):
        w0 = seg.words[0]
        args = [w.text for w in seg.words[1:]]
        if _ASSIGN.match(w0.text):
            return "variable assignments are not allowed before Phase {}".format(min_phase)
        if w0.quoted or w0.glob or "/" in w0.text or "\\" in w0.text:
            return "the command name must be a plain word (no path, quotes or glob)"
        name = _cmd_name(w0)
        # human-owned extra_allowed_commands: the whole command must equal the entry
        # ("npm ci" does not allow "npm ci --prefix docs"); an entry ending in " *" opts
        # into any trailing arguments.
        if any(e and e[0] == name and (args == e[1:] or e[-1] == "*" and args[:len(e) - 2] == e[1:-1])
               for e in extra):
            continue
        if name == "cd":
            # Judge cd by what bash does, not by what normalize() makes of it: (1) Windows
            # strips trailing dots/spaces from a path component but Git Bash does not, so
            # `cd "<root>."` FAILS in bash; refuse such components. (2) A failed cd must
            # stop the whole line: cd must be followed by && and the rest may only use && and
            # | (`cd X && a ; b` and `cd X && a || b` run b after a failed cd).
            target = normalize(args[0], vcwd, literal=True) if len(args) == 1 and not seg.words[1].glob else None
            parts = re.split(r"[/\\]", args[0]) if len(args) == 1 else []
            # (A trailing ; or newline after the last command is harmless and ignored.)
            # T16-9: each refusal names its own cause.
            usage = " (allowed: cd \"<root>\" && git status)"
            if k != 0:
                return "cd is allowed only as the first command" + usage
            if any(c not in (".", "..") and c[-1:] in (".", " ") for c in parts):
                return ("cd target '{}' has a path component ending in a dot or space: Git Bash "
                        "keeps it, so that cd fails".format(args[0] if args else "") + usage)
            if target in (None, SUSPICIOUS) or not _same_dir(target, root):
                return ("cd is allowed only to the project root ({}), not '{}'".format(
                    str(root).replace("\\", "/"), " ".join(args)) + usage)
            bad = next((s.op for s in ([seg] if len(segs) > 1 and seg.op != "&&" else [])
                        + [s for s in segs[:-1] if s.op not in ("&&", "|")]), None)
            if bad:
                return ("{} after `cd <root> && ...`: a failed cd would not stop the rest; "
                        "join the commands with && (or |) only".format(
                            "`;` (or a newline)" if bad == ";" else "`{}`".format(bad)) + usage)
            vcwd = str(root)
            continue
        if name in VERSION_TOOLS and args == ["--version"]:
            # Root only, like git: some tools read per-directory config that can run code
            # (yarn 1 runs the `yarn-path` file named in a .yarnrc in its cwd), and before
            # Phase 4 the agent can write such files only below the root (docs/ ...).
            if not _same_dir(vcwd, root):
                return "'{} --version' runs only in the project root before Phase {}".format(name, min_phase)
            continue
        if name in READ_ONLY:
            continue
        if name == "git":
            reason = _git_pre4(args, vcwd, root)
            if reason:
                return reason
            continue
        if name == "mkdir":
            targets = [a for a in args if a not in ("-p", "-v")]
            if not targets:
                return "mkdir needs a directory"
            for t in targets:
                if t.startswith("-"):
                    return "mkdir option {} is not allowed before Phase {} (only -p, -v)".format(t, min_phase)
                if re.search(r"[*?\[]", t) or t.startswith("~"):
                    return "mkdir targets must be literal paths"
                reason = write_target_verdict(t, vcwd, root, phase, rules, literal=True)
                if reason:
                    return "mkdir: " + reason
            continue
        return "'{}' is not on AID's read-only list before Phase {}".format(name, min_phase)
    return None


# ---------------------------------------------------------------------------
# Phase 4+ (and no-phase): BEST-EFFORT control-file check
#
# The agent runs arbitrary code from Phase 4 on; this check only catches literal
# control-file paths and is bypassable by any code the agent runs. The real protection is
# layer A (permission deny rules) plus layer B (check_integrity on every call).
# ---------------------------------------------------------------------------

class Word(object):
    __slots__ = ("text", "dynamic")

    def __init__(self, text, dynamic):
        self.text = text
        self.dynamic = dynamic        # contains expansion, glob, escape: value unknown statically

    def __repr__(self):
        return "Word({!r}{})".format(self.text, ", dyn" if self.dynamic else "")


class Segment(object):
    __slots__ = ("words", "writes", "raw", "depth", "term")

    def __init__(self, depth=0):
        self.words, self.writes, self.raw, self.depth, self.term = [], [], "", depth, ""


class ParseError(Exception):
    pass


_REDIR = re.compile(r"(\d*|&)(>>|>\||>&|&>>|&>|<<<|<<-|<<|<&|<>|>|<)")


def _matching_paren(s, i):
    """
    s[i] is just after '$(' / '<(' / '>('; return index of the matching ')'.
    Heredoc bodies inside are skipped (an apostrophe in a commit message is not a quote).
    """
    depth, quote, heredocs = 1, None, []
    while i < len(s):
        c = s[i]
        if c == "\n" and heredocs and not quote:
            i += 1
            for delim, strip_tabs in heredocs:
                while True:
                    if i >= len(s):
                        raise ParseError("unterminated heredoc " + delim)
                    eol = s.find("\n", i)
                    line = s[i:eol if eol >= 0 else len(s)].rstrip("\r")
                    i = eol + 1 if eol >= 0 else len(s)
                    if (line.lstrip("\t") if strip_tabs else line) == delim:
                        break
            heredocs = []
            continue
        if not quote and s.startswith("<<", i) and not s.startswith("<<<", i):
            dm = re.match(r"<<(-?)\s*\\?(['\"]?)([^\s'\";&|<>()\\]+)\2", s[i:])
            if dm:
                heredocs.append((dm.group(3), dm.group(1) == "-"))
                i += dm.end()
                continue
        if quote:
            if c == "\\" and quote == '"':
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c == "\\":
            i += 2
            continue
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ParseError("unbalanced $( )")


def _substitutions(text, subs):
    """Collect $( ) and backtick bodies from text where they expand (heredoc body, dquotes)."""
    i = 0
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text.startswith("$(", i):
            j = _matching_paren(text, i + 2)
            subs.append(text[i + 2:j])
            i = j + 1
            continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j < 0:
                raise ParseError("unbalanced backtick")
            subs.append(text[i + 1:j])
            i = j + 1
            continue
        i += 1


def lex(command, _brackets=True):
    """
    Best-effort split of a command line into Segments for the Phase 4+ check. Raises
    ParseError when the text cannot be parsed. $( ), <( ), >( ) and backtick bodies are
    lexed recursively and returned as extra segments: the shell runs them.
    T16-5 (E5): no redirection or heredoc inside `$[ ]`, `${ }` or a `name[ ]=` subscript,
    and no heredoc in the operands of let / declare -i (an unbalanced bracket: lexed as before).
    """
    s = command.replace("\\\r\n", "").replace("\\\n", "")
    segs, subs = [], []
    seg, word, dyn, has_word = Segment(), [], False, False
    seg_start, depth = 0, 0
    pending_heredocs = []      # (delimiter, quoted, strip_tabs)
    pending_redirect = None    # ("w"|"r"|"hd", op)
    brk = []                   # T16-5: open $[ / ${ / name[ brackets (their closers)
    i, n = 0, len(s)

    def end_word():
        nonlocal word, dyn, has_word, pending_redirect
        if not has_word:
            return
        text = "".join(word)
        w = Word(text, dyn and text not in ("[", "[[", "]", "]]", "{", "}"))
        if pending_redirect is not None:
            if pending_redirect[0] == "w":
                seg.writes.append(w)
            pending_redirect = None
        else:
            seg.words.append(w)
        word, dyn, has_word = [], False, False

    def end_segment(pos, term=""):
        nonlocal seg, seg_start
        end_word()
        seg.raw = s[seg_start:pos]
        seg.term = term
        if seg.words or seg.writes:
            segs.append(seg)
        seg = Segment(depth)
        seg_start = pos + 1

    while i < n:
        c = s[i]
        if c == "'":
            j = s.find("'", i + 1)
            if j < 0:
                raise ParseError("unbalanced single quote")
            word.append(s[i + 1:j])
            has_word = True
            i = j + 1
            continue
        if c == '"':
            j, buf = i + 1, []
            while j < n and s[j] != '"':
                if s[j] == "\\" and j + 1 < n:
                    buf.append(s[j + 1])
                    j += 2
                    continue
                if s.startswith("$(", j):
                    k = _matching_paren(s, j + 2)
                    subs.append(s[j + 2:k])
                    buf.append("$")
                    dyn = True
                    j = k + 1
                    continue
                if s[j] == "`":
                    k = s.find("`", j + 1)
                    if k < 0:
                        raise ParseError("unbalanced backtick")
                    subs.append(s[j + 1:k])
                    dyn = True
                    j = k + 1
                    continue
                if s[j] == "$":
                    dyn = True
                buf.append(s[j])
                j += 1
            if j >= n:
                raise ParseError("unbalanced double quote")
            word.append("".join(buf))
            has_word = True
            i = j + 1
            continue
        if c == "\\" and i + 1 < n:
            word.append(s[i + 1])
            dyn = True if s[i + 1] not in " \t" else dyn
            has_word = True
            i += 2
            continue
        if c == "$" and s[i + 1:i + 3] == "((":
            k = _matching_paren(s, i + 2)
            _substitutions(s[i + 3:k - 1], subs)
            word.append("0")
            dyn = has_word = True
            i = k + 1
            continue
        if c == "(" and s[i + 1:i + 2] == "(" and not has_word and (
                not seg.words or [w.text for w in seg.words] == ["for"]):
            k = _matching_paren(s, i + 1)
            _substitutions(s[i + 2:k - 1], subs)
            seg.words.append(Word("((", False))
            i = k + 1
            continue
        if c == "$" and s[i + 1:i + 2] == "(" or c in "<>" and s[i + 1:i + 2] == "(" and not has_word:
            k = _matching_paren(s, i + 2)
            subs.append(s[i + 2:k])
            word.append("$")
            dyn = has_word = True
            i = k + 1
            continue
        if c == "`":
            k = s.find("`", i + 1)
            if k < 0:
                raise ParseError("unbalanced backtick")
            subs.append(s[i + 1:k])
            word.append("$")
            dyn = has_word = True
            i = k + 1
            continue
        if c == "$" and s[i + 1:i + 2] == "'":
            j = i + 2
            while j < n and s[j] != "'":
                j += 2 if s[j] == "\\" else 1
            if j >= n:
                raise ParseError("unbalanced $'...'")
            word.append(s[i + 2:j])
            dyn = has_word = True
            i = j + 1
            continue
        if c == "#" and not has_word:
            while i < n and s[i] not in "\r\n":
                i += 1
            continue
        if _brackets and c in "[{" and (s[i - 1:i] == "$" or brk or (
                c == "[" and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", "".join(word))
                and all(_ASSIGN.match(w.text) for w in seg.words))):
            brk.append("]" if c == "[" else "}")
        elif brk and c == brk[-1]:
            brk.pop()
        if brk and c in "<>":
            word.append(c)                  # T16-5: a shift or comparison, not a redirection
            has_word = True
            i += 1
            continue
        if (c == "<" and s[i + 1:i + 2] == "<" and s[i + 2:i + 3] != "<"
                and _arith_cmd([w.text for w in seg.words])):
            word.append("<<")               # T16-5: let / declare -i operands: a shift
            has_word = True
            i += 2
            continue
        m = _REDIR.match(s, i) if (c in "<>&" or c.isdigit()) else None
        if m and (m.group(1) == "" or not has_word or "".join(word).isdigit()) and (c != "&" or s[i:i + 2] in ("&>",)):
            if has_word and "".join(word).isdigit():
                word, dyn, has_word = [], False, False
            else:
                end_word()
            op = m.group(2)
            i = m.end()
            if op in (">&", "<&"):
                fd = re.match(r"\s*(\d+|-)", s[i:])
                if fd:
                    i += fd.end()
                    continue
                pending_redirect = ("w" if op == ">&" else "r", op)
            elif op in ("<<", "<<-"):
                dm = re.match(r"\s*(\\?)(['\"]?)([^\s'\";&|<>()\\]+)\2", s[i:])
                if not dm:
                    raise ParseError("heredoc without delimiter")
                pending_heredocs.append((dm.group(3), bool(dm.group(1) or dm.group(2)), op == "<<-"))
                i += dm.end()
            elif op == "<<<":
                pending_redirect = ("hd", op)
            elif op in ("<", "<&"):
                pending_redirect = ("r", op)
            else:
                pending_redirect = ("w", op)
            continue
        if c in "\r\n":
            end_segment(i)
            i += 1
            for delim, quoted, strip_tabs in pending_heredocs:
                body = []
                while True:
                    if i >= n:
                        raise ParseError("unterminated heredoc " + delim)
                    eol = s.find("\n", i)
                    line = s[i:eol if eol >= 0 else n].rstrip("\r")
                    i = eol + 1 if eol >= 0 else n
                    if (line.lstrip("\t") if strip_tabs else line) == delim:
                        break
                    body.append(line)
                if not quoted:
                    _substitutions("\n".join(body), subs)
            pending_heredocs = []
            seg_start = i
            continue
        if c in ";&|()":
            end_segment(i, c)
            if c in "()":                     # subshell: cd inside it does not leak out
                depth += 1 if c == "(" else -1
                seg.depth = depth
            i += 1
            continue
        if c in " \t":
            end_word()
            i += 1
            continue
        if c in "*?[{~$":
            dyn = True
        word.append(c)
        has_word = True
        i += 1

    if brk:
        return lex(command, _brackets=False)     # T16-5: unbalanced: lexed as before
    if pending_heredocs:
        raise ParseError("heredoc body missing")
    end_segment(n)
    if pending_redirect is not None and pending_redirect[0] == "w":
        raise ParseError("redirection without target")
    return segs, subs


KEYWORDS_PREFIX = {"if", "then", "else", "elif", "do", "while", "until", "!", "{", "time"}
KEYWORDS_ALONE = {"fi", "done", "}", "esac", "else", "then", "do", "(("}

GIT_WRITE_SUBS = {"checkout", "restore", "reset", "stash", "mv", "rm", "clean", "apply", "am",
                  "worktree", "clone", "switch", "merge", "pull", "rebase", "cherry-pick", "revert"}
# AC-33: git subcommands that only read (or stage) and may name a control file in Phase 4+.
GIT_EXEMPT = {"status", "log", "diff", "show", "blame", "ls-files", "rev-parse", "add"}
WRITERS = {"mkdir", "touch", "rm", "rmdir", "cp", "mv", "tee"}


def _short_flags(args):
    """Letters of single-dash flag clusters (-rT -> {'r','T'})."""
    out = set()
    for a in args:
        if re.match(r"^-[A-Za-z]+$", a):
            out.update(a[1:])
    return out


def _git_split(args, cwd):
    """(subcommand, rest, effective cwd after -C) or (None, reason, None) for a bad global option."""
    i, gcwd = 0, cwd
    while i < len(args):
        a = args[i]
        if a in ("--no-pager", "-P", "--no-optional-locks", "--paginate", "-p", "--literal-pathspecs"):
            i += 1
        elif a == "-C" and i + 1 < len(args):
            n = normalize(args[i + 1], gcwd) if gcwd is not None else None
            gcwd = n if n not in (None, SUSPICIOUS) else None
            i += 2
        elif a.startswith("-"):
            return None, "git global option {}".format(a), None
        else:
            break
    if i >= len(args):
        return "", [], gcwd
    return args[i], args[i + 1:], gcwd


def _git_pathspecs(sub, rest, gcwd):
    """Paths a git write-subcommand will create or change."""
    if sub in ("worktree",) and rest[:1] == ["add"]:
        ops = [a for a in rest[1:] if not a.startswith("-")]
        return ops[:1]
    if "--" in rest:
        return rest[rest.index("--") + 1:]
    if sub in ("restore", "rm", "mv"):
        out, skip = [], False
        for a in rest:
            if skip:
                skip = False
                continue
            if a in ("-s", "--source"):
                skip = True
                continue
            if not a.startswith("-"):
                out.append(a)
        return out
    if sub == "checkout" and gcwd is not None:
        return [a for a in rest if not a.startswith("-") and os.path.exists(os.path.join(gcwd, a))]
    return []


def _cp_mv_targets(name, words, args, vcwd, dest_only=False):
    """
    Write targets of cp/mv, honouring -t/-tX/--target-directory[=X], -T, and copy-into-dir.
    Returns (targets, reason_or_None). Best effort (abbreviated long options are not modelled).
    dest_only (R2-03, the every-folder state.json rule; also ln/install): the destination
    only, with no link/recursive verdict and no mv sources.
    """
    flags = _short_flags(args)
    t_dir, skip, operands = None, False, []
    for w in words[1:]:
        a = w.text
        if skip:
            t_dir, skip = w, False
            continue
        if a in ("-t", "--target-directory"):
            skip = True
        elif a.startswith("--target-directory="):
            t_dir = Word(a.split("=", 1)[1], w.dynamic)
        elif re.match(r"^-[A-Za-z]*t.+", a) and not a.startswith("--"):
            t_dir = Word(a[a.index("t") + 1:], w.dynamic)
        elif not a.startswith("-") or a == "-":
            operands.append(w)
    no_target_dir = "T" in flags or "--no-target-directory" in args
    linking = bool({"l", "s"} & flags) or any(a in ("--link", "--symbolic-link") for a in args)
    recursive = bool({"r", "R", "a"} & flags) or any(a in ("--recursive", "--archive") for a in args)
    if t_dir is not None:
        dest, sources = t_dir, operands
    else:
        dest, sources = (operands[-1] if operands else None), operands[:-1]
    if not dest_only and linking and any(is_protected_or_parent(normalize(s.text, vcwd))
                                         for s in sources if not s.dynamic):
        return [], "linking to an AID control file"
    if dest is None:
        return [], None
    dnorm = normalize(dest.text, vcwd) if not dest.dynamic else None
    if not dest_only and recursive and dnorm not in (None, SUSPICIOUS) and is_protected_or_parent(dnorm):
        return [], "recursive copy into a folder holding AID control files"
    targets = [dest]
    into_dir = t_dir is not None or (not no_target_dir and (
        dest.text.endswith(("/", "\\")) or (dnorm not in (None, SUSPICIOUS) and os.path.isdir(dnorm))))
    if into_dir:
        targets += [Word(os.path.join(dest.text, os.path.basename(s.text.rstrip("/\\"))),
                         dest.dynamic or s.dynamic) for s in sources]
    if name == "mv" and not dest_only:
        targets += sources                     # moving a file away changes it too
    return targets, None


def _short_in_control_dir(text):
    """T21 audit: an 8.3 short name (`~N`) inside .aid/ or .claude/ may alias a control file
    (`.aid/pipeline/COST-L~1.JSO`). Revisions and versions (`HEAD~1`, `@~20`) never match."""
    return bool(re.search(r"~\d", text)) and bool(
        re.search(r"(?:^|[/\\])\.(?:aid|claude)(?:[/\\]|$)", text, re.I))


def _write_word_verdict(w, vcwd, root, phase, rules):
    """AC-31: a target that contains a variable keeps the literal check on its text."""
    if _short_in_control_dir(w.text):
        # T21 fix 1: the lexer makes a `~` word dynamic, so normalize's 8.3 check never saw
        # `> .aid/pipeline/COST-L~1.JSO`; refused in every phase, as the Write tool does.
        return "refusing an obfuscated path form ({!r})".format(w.text)
    if w.dynamic and mentions_protected(w.text):
        return "'{}' names an AID control file (protected in every phase)".format(w.text)
    if w.dynamic and _glob_names_control(w.text, vcwd):
        return "'{}' may expand to an AID control file (protected in every phase)".format(w.text)
    return (write_target_verdict("$dyn" if w.dynamic else w.text, vcwd, root, phase, rules)
            or _pipeline_config_reason(w, vcwd))


def _brace_verdict(w, vcwd, root, phase, rules):
    """R2-01: _write_word_verdict on each brace alternative (and a leading ~ / $HOME
    expanded) of a write target: `touch .aid/{hooks,x}/config.json` writes both."""
    alts = _brace_words(w)
    if len(alts) == 1 and alts[0] is w:
        return _write_word_verdict(w, vcwd, root, phase, rules)
    return next((r for r in (_write_word_verdict(a, vcwd, root, phase, rules) for a in alts) if r), None)


def _pipeline_config_reason(w, vcwd):
    """T16-4: a Bash write to .aid/pipeline/config.json (the pipeline's pass thresholds)."""
    if (PIPELINE_CONFIG[1:] in w.text.replace("\\", "/").casefold()
            or (not w.dynamic and is_pipeline_config(normalize(w.text, vcwd)))):
        return ("'{}' holds the pipeline's pass thresholds; only the user changes it (the "
                "Write and Edit tools ask the user)").format(w.text)
    return None


def _phase4_exempt(name, words, args):
    """AC-33: reading or staging a control file is not writing it (redirects still checked)."""
    if name in READ_ONLY:
        return True
    if name != "git" or any(w.dynamic for w in words):
        return False
    sub, _rest, _ = _git_split(args, None)
    # R4-02: `--output[=]<f>` (log/diff/show/...) writes <f>: never an exempt read; it is
    # judged as a write to <f> (_phase4_check's git --output rule, and state_write_reason).
    if any(a == "--output" or a.startswith("--output=") for a in args):
        return False
    return sub in GIT_EXEMPT and not any(a.startswith("-") and mentions_protected(a) for a in args)


def _phase4_check(command, cwd, root, phase, rules):
    """BEST EFFORT (see section comment): literal control-file paths in a Bash command."""
    try:
        segments, subs = lex(command)
    except ParseError as e:
        # R2-02 (T17 fix cycle 2): also a text naming a live-root protected folder (a shell -c
        # body with an apostrophe path, `sh -c "cp a <R>/hooks/x"`), as for the cache copies.
        return "cannot parse the command safely ({})".format(e) if (
            mentions_protected(command) or _mentions_live(command, _live_protected())) else None
    for body in subs:                     # substitution bodies run in subshells; cwd unknown
        reason = _phase4_check(body, None, root, phase, rules)
        if reason:
            return reason

    # R1-06: `echo x > $(echo .aid/state.json)`: a write target built by a substitution whose
    # text names a control file (the lexer keeps only `$` for that target).
    sub_names = any(mentions_protected(b) or PIPELINE_CONFIG[1:] in b.replace("\\", "/").casefold()
                    for b in subs)
    # R3-01 (T16 fix cycle 3): True after a cd / pushd into an AID control folder (.aid,
    # .claude, .aid/hooks, ...). A literal such cd is itself denied (T16 B1); for one this
    # check cannot resolve (`cd "$P/.aid"`), any later command that is not a read (READ_ONLY,
    # an exempt git read) or another cd is refused: a shell
    # or interpreter there (`cd .aid && bash -c 'echo x > state.json'`) writes control files
    # by bare names this check cannot see.
    vcwd, depth, saved, variables, in_ctl = cwd, 0, [], {}, False
    for seg in segments:
        while depth < seg.depth:
            saved.append((vcwd, in_ctl))
            depth += 1
        while depth > seg.depth:
            vcwd, in_ctl = saved.pop() if saved else (vcwd, in_ctl)
            depth -= 1

        for w in seg.writes:
            reason = _brace_verdict(_assigned_word(w, variables), vcwd, root, phase, rules)
            if not reason and sub_names and w.dynamic and re.search(r"[$`]", w.text):
                reason = "'{}' is built by a command that names an AID control file".format(w.text)
            if reason:
                return "redirection: " + reason

        if in_ctl and re.search(r"\$\(|`|[<>]\(", seg.raw):
            # R3-01: a substitution there runs with this check's cwd unknown.
            return "'{}' runs a command substitution in an AID control folder".format(seg.raw.strip()[:80])
        words = list(seg.words)
        while words and words[0].text in KEYWORDS_PREFIX and not words[0].dynamic:
            words.pop(0)
        assigns = []
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?=", words[0].text):
            assigns.append(words.pop(0))
        if not words:
            _record_assignments(assigns, variables)     # R1-06: `f=<path>; echo x > $f`
        if not words or (len(words) == 1 and words[0].text in KEYWORDS_ALONE):
            continue
        t = words[0].text
        name = t.lower() if not words[0].dynamic and "/" not in t and "\\" not in t else None
        if name and IS_WIN:
            name = re.sub(r"\.(exe|cmd|bat)$", "", name)
        args = [w.text for w in words[1:]]

        if name not in ("cd", "pushd", "popd"):
            # R3-03: a static `bash -c '<text>'` body runs in this folder; `env -C DIR cmd`
            # in DIR (a control folder: refused, like a cd there followed by a command).
            for body in _shell_c_bodies(words):
                reason = _phase4_check(body, vcwd, root, phase, rules)
                if reason:
                    return reason
            ecd = _env_chdir(words)
            if ecd is not None and _ctl_dir_word(ecd, vcwd):
                return "'{}' runs a command in an AID control folder".format(seg.raw.strip()[:80])
            if in_ctl and not _phase4_exempt(name, words, args):
                return ("'{}' runs in an AID control folder (after a cd into it): only reads (ls, "
                        "cat, grep, git status/log/diff) may follow such a cd").format(seg.raw.strip()[:80])
        if _phase4_exempt(name, words, args):
            continue
        lp = _live_protected()
        if name not in WRITERS:
            # R1-01 (T17 fix cycle 1): from a linked project, a live-root operand is allowed only
            # as the script an interpreter runs, or a cd / pushd folder; any other command that
            # names it (curl -o, dd of=, tar -C, unzip -d, Remove-Item, Set-Content, ...) is
            # refused, as for the cache copies. A shell -c body is judged on its own (R3-03).
            run_word = _live_run_word(words) if lp else None
            sh_bodies = set(_shell_c_bodies(words)) if lp else set()
            # R2-01: each alternative of an unquoted {a,b} operand (`sed -i ... .aid/{hooks,x}/..`).
            for a in [x.text for w in words[1:] for x in _brace_words(w, home=False)]:
                cand = a.split("=", 1)[1] if a.startswith("-") and "=" in a else (None if a.startswith("-") else a)
                # Not a write target: an unreasonable form (`D:`, `test:unit`) is not a control
                # file. Writer operands and redirect targets keep the SUSPICIOUS denial for
                # literal words (stream, drive-relative, UNC); words with ~ or $ are dynamic
                # and get only the mentions_protected check (best effort, N-1).
                n = normalize(cand, vcwd) if cand else None
                live_ok = bool(lp) and (a == run_word or name in ("cd", "pushd")) and not _edits_in_place(
                    name, args) and (_live_root_only(n) or _live_parent(n, lp))
                # T16 B1: T16-10 reverted; `cd .aid` / `cd ~/.aid` stay denied, as at 5f8f199.
                if mentions_protected(a) or _short_in_control_dir(a) or (
                        n != SUSPICIOUS and is_protected_or_parent(n) and not live_ok) or (
                        lp and not live_ok and a not in sh_bodies and (
                            _mentions_live(a, lp) or _live_parent(n, lp))):
                    # T17-9: running or reading a live-root file is not writing it.
                    return "'{}' would touch an AID control file".format(seg.raw.strip()[:80])
                if name != "cd" and _pipeline_config_reason(Word(a, True), vcwd):
                    return "'{}' would touch {}".format(seg.raw.strip()[:80], PIPELINE_CONFIG[1:])
        if name == "git":
            sub, rest, gcwd = _git_split(args, vcwd)
            rest = rest if isinstance(rest, list) else []
            for k, a in enumerate(rest):         # --output=<file> writes from any subcommand
                if a.startswith("--output"):
                    out = a.split("=", 1)[1] if "=" in a else (rest[k + 1] if k + 1 < len(rest) else "")
                    reason = write_target_verdict(out, gcwd, root, phase, rules)
                    if reason:
                        return "git --output: " + reason
            if sub and sub in GIT_WRITE_SUBS:
                for pth in _git_pathspecs(sub, rest, gcwd):
                    reason = write_target_verdict(pth, gcwd, root, phase, rules)
                    if reason:
                        return "git {}: {}".format(sub, reason)
        if name in WRITERS:
            if name in ("cp", "mv"):
                operands, reason = _cp_mv_targets(name, words, args, vcwd)
                if reason:
                    return "{}: {}".format(name, reason)
            else:
                operands = [w for w in words[1:] if not w.text.startswith("-")]
            for w in operands:
                w = _assigned_word(w, variables)
                reason = _brace_verdict(w, vcwd, root, phase, rules)
                if not reason and sub_names and w.dynamic and re.search(r"[$`]", w.text):
                    reason = "'{}' is built by a command that names an AID control file".format(w.text)
                if not reason and name in ("rm", "rmdir", "mv") and any(
                        is_protected_or_parent(normalize(a.text, vcwd)) for a in _brace_words(w)):
                    reason = "'{}' contains AID control files".format(w.text)
                if not reason and lp and name in ("rm", "rmdir", "mv", "cp") and any(
                        _live_parent(normalize(a.text, vcwd), lp) for a in _brace_words(w)):
                    # R1-01: `rm -rf "<R>"`, `mv "<R>/skills" x`, `cp -r hooks "<R>"`.
                    reason = "'{}' contains AID control files (the live AID plugin root)".format(w.text)
                if reason:
                    return "{}: {}".format(name, reason)
        # R3-02 (T17): skip cd/pushd options (-L -P -e -@ -n) and `--` before the target, so
        # `cd -- "<R>"`, `cd -P "<R>"` and `pushd -- "<R>"` move vcwd like the plain forms.
        cd_rest = _cd_operands(words) if name in ("cd", "pushd") else None
        if name == "cd" or (name == "pushd" and len(cd_rest) == 1 and not cd_rest[0].dynamic
                            and not re.match(r"^[-+]", cd_rest[0].text)):
            # R2-02 (T17 fix cycle 2): `pushd DIR` moves to DIR like `cd DIR`, so the later
            # segments' relative words resolve there (`pushd "<R>" && rm -rf agents`).
            target = None
            if len(cd_rest) == 1 and not cd_rest[0].dynamic and cd_rest[0].text != "-":
                t = cd_rest[0].text
                target = normalize(t, vcwd) if vcwd is not None or os.path.isabs(t) else None
            ops = [w for w in words[1:] if not (w.text.startswith("-") and not w.dynamic)]
            if ops:
                in_ctl = _ctl_dir_word(ops[-1], vcwd)               # R3-01
            elif not args:
                in_ctl = False                                       # `cd` alone: home
            # A cd that would fail (missing dir) leaves the real cwd unchanged: unknown.
            vcwd = target if target not in (None, SUSPICIOUS) and os.path.isdir(target) else None
        elif name in ("pushd", "popd"):
            ops = [w for w in words[1:] if not re.match(r"^[-+]", w.text) or w.dynamic]
            if name == "pushd" and ops:
                in_ctl = _ctl_dir_word(ops[-1], vcwd)               # R3-01
            vcwd = None
    return None


def _cd_operands(words):
    """R3-02 (T17): the operands of a cd/pushd segment after its leading options
    (-L, -P, -e, -@, -n, combined like -LP) and an optional `--` end-of-options marker."""
    rest = list(words[1:])
    while rest and not rest[0].dynamic:
        t = rest[0].text
        if t == "--":
            rest = rest[1:]
            break
        if re.fullmatch(r"-[LPe@n]+", t):
            rest = rest[1:]
            continue
        break
    return rest


def _ctl_dir_word(w, vcwd):
    """R3-01: is the cd / pushd / env -C folder word an AID control folder or one holding
    control files (.aid, .claude, .aid/hooks, ...)? A word this check cannot resolve counts
    when its text ends in such a component (`"$HOME/.aid"`, `$P/.claude/`)."""
    w = _home_word(w)
    n = None if w.dynamic else normalize(w.text, vcwd)
    if n not in (None, SUSPICIOUS):
        return is_protected_or_parent(n)
    # Unresolved, or a drive-relative / stream form (`cd D:`): judged on its text.
    t = re.sub(r"[\"'\\]", "/", _strip_streams(w.text) if n == SUSPICIOUS else w.text).rstrip("/. ")
    return bool(re.search(r"(?:^|/)\.(?:aid|claude)(?:/(?:hooks|pipeline|plugins|integrity))?$", t, re.I))


def evaluate_bash(command, cwd, root, phase, rules, extra_allowed=()):
    """
    Return None when the command may run, else a reason string.

    Before code_execute_min_phase: the strict grammar + command tables (_pre4).
    Otherwise (Phase 4+, or no phase): the best-effort control-file check (_phase4_check).
    In every phase first: a phase-changing aid_session.py call must be in the spelling the
    ask rules match, or the user would not be asked (T3-4b).
    """
    reason = confirmed_form_verdict(command)
    if reason:
        return reason
    if _is_plugin_session(command):
        # T3 A3: the plugin's own script in the exact AC-23 shape runs in every phase. From
        # Phase 4 its path (~/.claude/plugins/cache/...) would otherwise read as a control file.
        return None
    if phase is not None and phase < rules.get("code_execute_min_phase", 4):
        return _pre4(command, cwd, root, phase, rules, [list(e) for e in extra_allowed])
    return _phase4_check(command, cwd, root, phase, rules)


# ---------------------------------------------------------------------------
# PowerShell tool (T7). Claude Code sends it to the same hook as Bash (matcher
# Bash|PowerShell, command in tool_input.command). The read-only list above is bash
# grammar; PowerShell parses \ ` $() & differently, so it is never applied here.
# ---------------------------------------------------------------------------

PS_SESSION_REASON = (
    "aid_session.py cannot run from the PowerShell tool: Claude Code's confirmation (ask) "
    "rules cover the Bash tool only, so the user would not be asked. Run it with the Bash "
    "tool in the form the command file gives, or let the user type it with a leading !")


def ps_mentions_session(command):
    """T7-4: aid_session named anywhere, after removing PowerShell quoting and joins."""
    return "aid_session" in re.sub(r"[\"'`+\s]", "", command).casefold()


_PS_LISTING = r"(?:get-childitem|gci|ls|dir|resolve-path|rvpa|get-item|gi)"
# R3-C4: a value taken from a listing of an aid_s* wildcard: the script path built at run time.
_PS_SESSION_GLOB = re.compile(_PS_LISTING + r"\b[^;|\n]*aid_s[^\s'\"/\\;|)]*[*?\[]", re.I)
_PS_HOOKS_LISTING = re.compile(r"(?:=|\()\s*" + _PS_LISTING + r"\b[^;|\n)]*[\\/]hooks(?:[\\/'\"\s)]|$)", re.I)


def _ps_built_session_call(command):
    """
    R3-C4 (best effort, D3): a PowerShell command that may run aid_session.py through a script
    path built at run time: a value taken from Get-ChildItem/Resolve-Path on an aid_s*
    wildcard, or on a hooks/ folder together with python and a confirmed word; or a python
    reached through `& (Get-Command python)` or Start-Process ... -ArgumentList, read as the
    plain call it makes and judged like Bash (T15-3).
    """
    if _PS_SESSION_GLOB.search(command):
        return True
    low = command.casefold()
    if _PS_HOOKS_LISTING.search(command) and re.search(r"\bpy(?:thon[0-9.]*)?(?:\.exe)?\b", low) and (
            set(re.split(r"[^a-z0-9-]+", re.sub(r"[\"'`+]", "", low))) & set(CONFIRMED_SUBCOMMANDS)):
        return True
    plain = re.sub(r"\(\s*(?:get-command|gcm)\s+(?:-name\s+)?['\"]?([^\s'\")]+)['\"]?\s*\)", r"\1",
                   command, flags=re.I)
    plain = re.sub(r"\b(?:start-process|saps|start)\b((?:\s+-(?!argumentlist\b|args\b)\w+)*)\s+"
                   r"(?:-filepath\s+)?(\S+)((?:\s+-(?!argumentlist\b|args\b)\w+)*)\s+"
                   r"-(?:argumentlist|args)\s+([^;|\n]+)",
                   lambda m: m.group(2) + " " + " ".join(
                       a.strip() for a in re.split(r",(?![^(]*\))", m.group(4))),
                   plain, flags=re.I)
    return plain != command and _unresolved_session_call(plain)


def evaluate_powershell(command, cwd, root, phase, rules):
    """
    Return None when a PowerShell command may run, else a reason string.

    Every phase: no aid_session.py call (T7-4, D2). Before code_execute_min_phase: nothing
    runs (T7-3, D1). Otherwise, or with no phase: the best-effort control-file check on a
    copy with backticks removed and backslashes as '/' (T7-5, D3); layers A and B remain the
    real protection, as for Bash at that phase.
    """
    # R4-C3: the Bash run-time-built check misread PowerShell (`(Join-Path $PWD 'manage.py')`,
    # `$env:SCRIPT`) as a built session script; _runs_session judges PowerShell operands.
    if (ps_mentions_session(command) or _runs_session(command, powershell=True)
            or _ps_built_session_call(command)):
        return PS_SESSION_REASON        # R2-C3: also (Get-ChildItem ..aid_s*.py).FullName qa-pass
    min_phase = rules.get("code_execute_min_phase", 4)
    if phase is not None and phase < min_phase:
        return ("PowerShell commands cannot run before Phase {}: AID's read-only command list "
                "is defined for the Bash tool only".format(min_phase))
    norm = command.replace("`", "").replace("\\", "/")
    # T7 review r1: the bash lexer misreads PowerShell (an escaped `" left a quote open and
    # hid the rest; -Path:x, [IO.File]::WriteAllText('x') and x:stream were not seen as
    # paths). So any PowerShell command whose text names a control file is refused, even a
    # read (the Read tool or Bash can read it). Best effort, D3.
    low = norm.casefold()
    hit = next((lit for lit in PS_PROTECTED_LITERALS if lit in low), None)
    if hit:
        return "this PowerShell command names an AID control file ({})".format(hit)
    # R2-02 (T17 fix cycle 2): a .NET static call that changes files (`[IO.File]::WriteAllText`,
    # `[IO.Directory]::Delete`, ...) naming a live-root protected folder from a linked project,
    # as the cache copies' literal check above refuses it. Reads (Read*, Exists, Get*,
    # Enumerate*) stay as they were.
    lp = _live_protected()
    if lp and _PS_IO_CHANGE.search(norm) and any(re.search(
            re.escape(_pkey(e).rstrip("/")) + r"(?:[/\"'\s,)]|$)", low) for e in lp):
        return "this PowerShell command changes a file of the live AID plugin root (an AID control file)"
    # R2-05: a wildcard a writer or Remove-Item/ri/del/... may expand to a control file
    # (`Remove-Item .aid\pipeline\ESC*.json`, `del .aid\*`); PowerShell wildcards match dot names.
    glob = next((t for t in _ps_glob_targets(re.sub(r"[\"']", "", low), remove=True)
                 if _glob_names_control(t, cwd, hidden=True)), None)
    if glob:
        return "'{}' may expand to an AID control file (protected in every phase)".format(glob)
    return _phase4_check(norm, cwd, root, phase, rules)


PS_PROTECTED_LITERALS = PROTECTED_LITERALS + (".aid/state.json", ".aid/pipeline/escalation.json")
# R2-02: a System.IO static call other than a read (the type may be written with System. or
# without, any case, spaces before ::).
_PS_IO_CHANGE = re.compile(r"\[\s*(?:system\s*\.\s*)?io\s*\.\s*\w+\s*\]\s*::\s*(?!(?:read|exists|get|enumerate|combine|join|has|is)\w*\b)\w"
                           # R3-02 (T17): writer constructors, `New-Object IO.StreamWriter("<R>/hooks/x")`
                           r"|new-object\s+(?:-typename\s+)?(?:system\s*\.\s*)?io\s*\.\s*(?:streamwriter|filestream|binarywriter|fileinfo)\b",
                           re.I)


# ---------------------------------------------------------------------------
# T15 (D1, D2): the gate itself asks the user, in EVERY folder, before any phase rule
# ---------------------------------------------------------------------------

LIVE_ROOT = Path(__file__).resolve().parent.parent      # the plugin root this hook runs from


def _plugin_root_ok(d):
    """I-5: a regular hooks/aid_session.py and .claude-plugin/plugin.json named "aid"."""
    try:
        if not stat.S_ISREG(os.stat(os.path.join(d, "hooks", "aid_session.py")).st_mode):
            return False
        data = read_settings(os.path.join(d, ".claude-plugin", "plugin.json"))[0]
        return isinstance(data, dict) and data.get("name") == "aid"
    except (OSError, ValueError):
        return False


def _json_or_none(path):
    try:
        return read_settings(path)[0]
    except (OSError, ValueError):
        return None


def installed_plugin_roots(project_root=None):
    """
    T15 I-5: the normalised AID plugin roots, the live root first, then for each config dir
    ($CLAUDE_CONFIG_DIR, ~/.claude; deduplicated) every plugins/cache/*/aid/*/, every
    directory-marketplace installLocation and every installed_plugins.json aid@* installPath.
    A candidate counts only if _plugin_root_ok and (except the live root) it is not inside
    the current project, where the agent can write.
    """
    cfgs, seen = [], set()
    for c in (os.environ.get("CLAUDE_CONFIG_DIR"), str(Path.home() / ".claude")):
        if c and _key(os.path.realpath(c)) not in seen:
            seen.add(_key(os.path.realpath(c)))
            cfgs.append(Path(c))
    cands = []
    for cfg in cfgs:
        plugins = cfg / "plugins"
        try:
            markets = sorted((plugins / "cache").iterdir())
        except OSError:
            markets = []
        for m in markets:
            try:
                cands += [str(v) for v in sorted((m / "aid").iterdir())]
            except OSError:
                pass
        known = _json_or_none(plugins / "known_marketplaces.json")
        for e in (known.values() if isinstance(known, dict) else ()):
            if (isinstance(e, dict) and isinstance(e.get("source"), dict)
                    and e["source"].get("source") == "directory"
                    and isinstance(e.get("installLocation"), str)):
                cands.append(e["installLocation"])
        inst = _json_or_none(plugins / "installed_plugins.json")
        plugs = inst.get("plugins") if isinstance(inst, dict) else None
        for name, entries in (plugs.items() if isinstance(plugs, dict) else ()):
            if not str(name).startswith("aid@"):
                continue
            for e in (entries if isinstance(entries, list) else [entries]):
                if isinstance(e, dict) and isinstance(e.get("installPath"), str):
                    cands.append(e["installPath"])
    proj = (_key(os.path.realpath(str(project_root))).rstrip("/") + "/") if project_root else None
    out = [_key(os.path.realpath(str(LIVE_ROOT))).rstrip("/")]
    for c in cands:
        if "\x00" in c or not os.path.isabs(c):
            continue
        k = _key(os.path.realpath(c)).rstrip("/")
        if k in out or (proj and (k + "/").startswith(proj)) or not _plugin_root_ok(k):
            continue
        out.append(k)
    return out


def _session_call_root(command, roots):
    """The root whose hooks/aid_session.py the command runs in the AC-23 shape, else None."""
    try:
        segs = tokenize_strict(command)
    except Denied:
        return None
    if len(segs) != 1 or segs[0].redirect or len(segs[0].words) < 2:
        return None
    w = segs[0].words
    if w[0].quoted or _cmd_name(w[0]) not in _INTERPRETERS:
        return None
    script = w[1].text
    if not (os.path.isabs(script.replace("\\", "/")) or re.match(r"^[A-Za-z]:[/\\]", script)):
        return None
    if not all(_SESSION_ARG.match(x.text) for x in w[2:]):
        return None
    n = normalize(script, None, literal=True)
    return next((r for r in roots
                 if n == _key(os.path.realpath(os.path.join(r, "hooks", "aid_session.py")))), None)


def _session_subcommand(command):
    try:
        w = tokenize_strict(command)[0].words
    except (Denied, IndexError):
        return "?"
    return next((x.text for x in w[2:] if not x.text.startswith("-")), "?")


# T15-6 (D2): plugin scripts that change the machine outside the project. Exact shapes only.
PLUGIN_SCRIPTS = (
    ("node", ("integrations", "breather", "install.mjs"),
     "the breather installer writes hooks into ~/.claude/settings.json and reads your calendar"),
    ("bash", ("scripts", "init-project.sh"), "init-project.sh creates a new project folder"),
)
_SCRIPT_CALL = re.compile(r"^(node|bash) (\"[^\"\n$`]*[^\"\n$`\\]\"|'[^'\n]+'|[^\s\"'$`;&|<>(){}]+)"
                          r"((?: [A-Za-z0-9._=:-]+)*)$")


def plugin_script_ask(command, project_root=None):
    """T15-6: the ask reason when the command is exactly `node|bash "<IR>/<script>" [args]`."""
    m = _SCRIPT_CALL.match(command)
    if not m:
        return None
    path = m.group(2)
    path = path[1:-1] if path[:1] in "\"'" else path
    if not (os.path.isabs(path.replace("\\", "/")) or re.match(r"^[A-Za-z]:[/\\]", path)):
        return None
    n = normalize(path, None, literal=True)
    for interp, rel, what in PLUGIN_SCRIPTS:
        if interp == m.group(1) and any(
                n == _key(os.path.realpath(os.path.join(r, *rel)))
                for r in installed_plugin_roots(project_root)):
            return ("AID asks before this plugin script runs: {}. The user must confirm it "
                    "({}).".format(what, "/".join(rel)))
    return None


# T16-3 (E4, I-13): resolving a pipeline escalation is the user's decision.
_GATE_REL = ("skills", "pipeline-orchestrator", "gate.mjs")
_RESOLVE_CALL = re.compile(r"^node (\"[^\"\n$`]*[^\"\n$`\\]\"|'[^'\n]+'|[^\s\"'$`;&|<>(){}]+)"
                           r" --resolve (\"[^\"$`\\\r\n]{1,500}\"|'[^'\r\n]{1,500}'|[A-Za-z0-9._=:-]+)$")
RESOLVE_ASK_REASON = ("AID asks before a pipeline escalation is resolved: gate.mjs --resolve clears "
                      ".aid/pipeline/ESCALATION.json, a decision only the user makes. The user must "
                      "confirm it.")


def resolve_user_line():
    """I-13: the line the user runs (the agent shows it and never runs it)."""
    return '! node "{}/{}" --resolve "<what was decided>"'.format(
        str(LIVE_ROOT).replace("\\", "/"), "/".join(_GATE_REL))


def resolve_ask(command, project_root=None):
    """T16-3: the I-13 exact form `node "<IR>/skills/pipeline-orchestrator/gate.mjs" --resolve <A>`."""
    m = _RESOLVE_CALL.match(command)
    if not m:
        return None
    path = m.group(1)
    path = path[1:-1] if path[:1] in "\"'" else path
    if not (os.path.isabs(path.replace("\\", "/")) or re.match(r"^[A-Za-z]:[/\\]", path)):
        return None
    n = normalize(path, None, literal=True)
    if any(n == _key(os.path.realpath(os.path.join(r, *_GATE_REL)))
           for r in installed_plugin_roots(project_root)):
        return RESOLVE_ASK_REASON
    return None


# R1-05: runtimes and package-runner wrappers that run a .mjs script, and the subcommand
# words between such a wrapper and the script.
_RESOLVE_INTERP = re.compile(r"^(?:python[0-9.]*|py|node(?:js)?|deno|bunx?|tsx|ts-node(?:-esm)?|"
                             r"npx|pnpx|pnpm|yarn|npm|esno|vite-node|perl|ruby|php|pwsh|powershell)"
                             r"(?:\.exe|\.cmd)?$", re.I)
_RESOLVE_SUBWORDS = {"dlx", "exec", "x", "run", "node", "nodejs", "tsx", "ts-node", "bun", "deno"}


def resolve_denied(command, powershell=False):
    """T16-3 (I-13): inside AID, any other command that runs an interpreter and names gate.mjs
    and resolve, or runs a script operand built at run time followed by --resolve."""
    text = command.replace("`", "") if powershell else command
    # R1-05: judged with quotes, backslashes and backticks removed (`--res\olve`,
    # `--reso""lve`, `"gate.m"js`), as the shell runs it.
    low = re.sub(r"[\"'\\`]", "", text).casefold()
    names = "gate.mjs" in low and "resolve" in low
    segs = _shell_segments(text)
    if segs is None:
        return names
    for words in segs:
        lead = next((x for x in words if x.lower() not in _CMD_PREFIXES - {"eval"}
                     and not re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", x)), "")
        if lead.lower() == "eval":      # R2-01: eval "\"<P>\" --resolve ok": its text runs
            rest = words[words.index(lead) + 1:]
            if rest and resolve_denied(direct_exec_twin(" ".join(rest), powershell), powershell):
                return True
            continue
        k, _ = _interpreter_at(words, _RESOLVE_INTERP,       # R1-03: direct calls in the payload
                               shc=lambda p: resolve_denied(direct_exec_twin(p, powershell), powershell))
        if k == "sh-c":
            return True
        if k is None:
            continue
        if names:
            return True
        rest = [re.sub(r"[\"'\\`]", "", w) for w in words[k + 1:]]
        ops = [w for w in rest if not w.startswith("-")]
        while ops and ops[0].lower() in _RESOLVE_SUBWORDS:
            ops.pop(0)                          # npx node <P>, pnpm dlx <P>, yarn node <P>
        # A script operand built at run time, or a glob (`g?te.mjs`, `g*.mjs`), with --resolve.
        if "resolve" in low and any(re.search(r"[*?\[{]", w) and any(
                fnmatch.fnmatchcase("gate.mjs", re.split(r"[/\\]", a.lower())[-1])
                for a in _brace_alternatives(w)) for w in ops):
            return True
        if ops and re.search(r"[$`(*?\[{]", ops[0]) and "--resolve" in rest:
            return True
    return False


# T17 I-17 (F1): a command word whose last path component is aid_session.py or gate.mjs runs
# that script directly (shebang, file association). It is judged as if python / node stood
# right before that word, so every spelling gets the interpreter call's verdict. Exact name
# only (the _session_operand normaliser: any case, trailing dots/spaces ignored).
_DIRECT_SCRIPTS = (
    ("python", re.compile(r"^aid_session\.py[. ]*$", re.I), _PY_INTERP, _session_operand),
    ("node", re.compile(r"^gate\.mjs[. ]*$", re.I), re.compile(r"^node(?:\.exe)?$", re.I),
     lambda w: re.split(r"[/\\]", w.lower())[-1].rstrip(". ") == "gate.mjs"),
)
_DIRECT_NAME = re.compile(r"aid_session\.py|gate\.mjs", re.I)


def _word_start(command, idx, powershell):
    """Index where the shell word holding command[idx] starts (quotes and escapes tracked)."""
    return _word_starts(command, [idx], powershell)[0]


def _word_starts(command, idxs, powershell):
    """R2-04 (T17 fix cycle 2): _word_start for every index of the ascending `idxs`, in one
    forward scan of `command` (linear, not one scan from 0 per index)."""
    out, start, quote, i = [], 0, None, 0
    esc = "`" if powershell else "\\"
    for idx in idxs:
        while i < idx:
            ch = command[i]
            if quote:
                if ch == quote:
                    quote = None
                elif ch == esc and quote == '"':
                    i += 1
            elif ch in "'\"":
                quote = ch
            elif ch == esc:
                i += 1
            elif ch in " \t\r\n;&|()" or (ch == "`" and not powershell):
                start = i + 1
            i += 1
        out.append(start)
    return out


def _direct_calls(command, powershell, interp, is_script):
    """How many simple commands run `<interp> <script> ...` (interp the command word)."""
    text = command.replace("`", "").replace("\\", "/") if powershell else command
    segs = _shell_segments(text) or []
    n = 0
    for words in segs:
        k, _ = _interpreter_at(words, interp, shc=lambda _p: False, dyn=False)
        if isinstance(k, int) and k + 1 < len(words) and is_script(words[k + 1]):
            n += 1
    return n


def direct_exec_twin(command, powershell=False):
    """T17 I-17: the command with `python ` / `node ` inserted before every command word that
    is aid_session.py / gate.mjs (after the VAR=, env/exec/nohup/..., wrapper and runner
    prefixes _interpreter_at walks). The gates judge this twin, so verdict(C) == verdict(P)."""
    if not isinstance(command, str) or not _DIRECT_NAME.search(command):
        return command
    if powershell:
        # R2-01 (T17 fix cycle 2): `& ("<P>") --resolve ok` runs the same as `& "<P>" ...`.
        command = _PS_CALL_GROUP.sub(r"& \1", command)
    if "<<" in command:                 # a heredoc body spans the separators: judged whole
        return _twin_subs(_twin_part(command, powershell), powershell)
    out, last = [], 0
    for a, b in _twin_chunks(command, powershell):
        out.append(command[last:a])
        out.append(_twin_part(command[a:b], powershell))
        last = b
    out.append(command[last:])
    return _twin_subs("".join(out), powershell)


_PS_CALL_GROUP = re.compile(r"&\s*\(\s*(\"[^\"`$]*\"|'[^']*'|[^\s()\"'`$;|&]+)\s*\)")


def _twin_subs(command, powershell):
    """R2-01 (T17 fix cycle 2): the twin inside every command-substitution body, whatever
    its quoting: `x="$("<S>" qa-pass T-1)"`, `echo "$(...)"`, `` `...` ``. The top-level pass
    sees a double-quoted word as one word, so each $( ) / backtick body (outside single
    quotes) is twinned on its own, recursively. Unbalanced text is left as it is."""
    if not _DIRECT_NAME.search(command):
        return command
    return _map_subs(command, powershell, lambda body: direct_exec_twin(body, powershell))


def _map_subs(command, powershell, fn):
    """`command` with each outermost $( ) / backtick body (outside single quotes) as fn(body)."""
    out, i, last, quote, n = [], 0, 0, None, len(command)
    esc = "`" if powershell else "\\"
    while i < n:
        ch = command[i]
        if quote == "'":
            if ch == "'":
                quote = None
        elif ch == esc:
            i += 2
            continue
        elif ch == "'" and quote is None:
            quote = "'"
        elif ch == '"':
            quote = None if quote == '"' else '"'
        elif command.startswith("$(", i):
            try:
                j = _matching_paren(command, i + 2)
            except ParseError:
                break
            out.append(command[last:i + 2])
            out.append(fn(command[i + 2:j]))
            last, i = j, j + 1
            continue
        elif ch == "`" and not powershell:
            j = command.find("`", i + 1)
            if j < 0:
                break
            out.append(command[last:i + 1])
            out.append(fn(command[i + 1:j]))
            last, i = j, j + 1
            continue
        i += 1
    out.append(command[last:])
    return "".join(out)


def _twin_chunks(command, powershell):
    """R1-05 (T17 fix cycle 1): (start, end) spans of the parts of `command` split at the
    top-level ; & | and newlines (quotes, escapes, backticks and parentheses tracked), so each
    candidate twin is re-judged on its own part, not on the whole command (linear time)."""
    spans, start, quote, depth, i, n = [], 0, None, 0, 0, len(command)
    esc = "`" if powershell else "\\"
    while i < n:
        ch = command[i]
        if quote:
            if ch == quote:
                quote = None
            elif ch == esc and quote == '"':
                i += 1
        elif ch in "'\"" or (ch == "`" and not powershell):
            quote = ch
        elif ch == esc:
            i += 1
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0 and ch == "&" and (
                (i > 0 and command[i - 1] in "<>") or (i + 1 < n and command[i + 1] == ">")):
            # R3-01 (T17): the & of a redirect (2>&1, >&2, <&3, &>file) is not a separator;
            # splitting there left an unlexable part and the direct call got no twin.
            pass
        elif depth == 0 and ch in ";&|\n":
            spans.append((start, i))
            start = i + 1
        i += 1
    spans.append((start, n))
    return spans


def _twin_part(text, powershell):
    """T17 I-17 on one part: insert the interpreter before each direct script command word.
    R1-05: a part whose simple commands have no such command word is skipped after one lex,
    and the search stops once every such command word has its interpreter."""
    if not _DIRECT_NAME.search(text):
        return text
    for interp_word, name, interp, is_script in _DIRECT_SCRIPTS:
        # R2-04: substitution bodies are twinned on their own (_twin_subs), so only this
        # part's own simple commands count here; text the lexer cannot read gets no twin
        # (no candidate could add a call), so it is not tried word by word.
        plain = _map_subs(text, powershell, lambda _b: "")
        plain = plain.replace("`", "").replace("\\", "/") if powershell else plain
        segs = _shell_segments(plain)
        want = 0 if segs is None else sum(
            1 for w in segs if isinstance(_interpreter_at(w, name, shc=lambda _p: False, dyn=False)[0], int))
        if want == 0:
            continue
        have = _direct_calls(text, powershell, interp, is_script)
        done, shift = 0, 0
        ms = [m for m in _DIRECT_NAME.finditer(text) if name.match(m.group(0))]
        # R2-04 (T17 fix cycle 2): every word start in one scan of this text (an insertion is
        # at an earlier word start, so a later one only moves by `shift`), and each word tried
        # once: names inside one quoted VAR= / env value are one word, not one lex each.
        starts, tried = _word_starts(text, [m.start() for m in ms], powershell), set()
        # In order: the command word comes before its arguments, so the search ends early.
        for m, s0 in zip(ms, starts):
            if want is not None and done >= want:
                break
            if s0 in tried:
                continue
            tried.add(s0)
            s = s0 + shift
            cand = text[:s] + interp_word + " " + text[s:]
            got = _direct_calls(cand, powershell, interp, is_script)
            if got > have:
                text, have, done, shift = cand, got, done + 1, shift + len(interp_word) + 1
    return text


def session_ask_verdict(command, project_root=None, powershell=False):
    """
    T15 (D1, D2): decided before any phase rule, in every folder. Returns (kind, reason):
      ("ask", r)     the gate asks the user: a confirmed subcommand (I-1) in the asked spelling
                     to an installed plugin root, any subcommand of a non-live installed root
                     (Bash), or a T15-6 plugin script (Bash);
      ("foreign", r) a confirmed subcommand in the asked spelling to an aid_session.py that is
                     not an installed root (the caller asks outside AID, applies the existing
                     rules inside it, and asks where those would allow);
      ("deny", r)    a confirmed subcommand in any other spelling (T3-4b);
      (None, None)   not a human-confirmed call: the phase rules decide.
    """
    if powershell:
        # T15-6 (D2, A2; docs review NEW-1): the exact plugin-root breather installer /
        # init-project.sh call is asked from the PowerShell tool too, as from Bash. Only the
        # exact form: no $, backtick, ;, |, redirect or ( ) can follow the quoted path.
        why = plugin_script_ask(command, project_root) or resolve_ask(command, project_root)
        if why:
            return "ask", why
        # T15-4: only the exact canonical call is asked; any other PowerShell spelling that
        # names aid_session and a confirmed subcommand (quotes, backticks, + joins) is denied.
        # R2-C3: also a script operand built at run time ((Get-ChildItem ..aid_s*.py).FullName,
        # $p) followed by a confirmed word, and a subcommand built at run time ($([char]105+
        # 'nit'), $env:X) after aid_session: the same as Bash (T15-3), denied in every folder.
        # R4-C3: judged only on python script operands (_runs_session), never on prose or a
        # commit message that names aid_session; inside AID evaluate_powershell keeps T7-4.
        if _ps_built_session_call(command):
            return "deny", PS_SESSION_REASON        # R3-C4: gci aid_s*.py, & (gcm python), Start-Process
        if not _runs_session(command, powershell=True):
            return None, None
        bad = "`" in command or _form_reason(command)
        if not bad:
            return _confirmed_call_verdict(command, project_root)
        return "deny", _form_reason(command) or PS_SESSION_REASON
    why = plugin_script_ask(command, project_root) or resolve_ask(command, project_root)
    if why:
        return "ask", why
    if ("aid_session" not in re.sub(r"[\"'`\\\s]", "", command).casefold()
            and not _unresolved_session_call(command)):     # T15-3 (R1-C1): aid_ses*.py, $S.py
        return None, None
    # R4-C3: the every-folder decision judges only a real call (_runs_session): an
    # interpreter's aid_session.py operand or a run-time-built one, not text naming it.
    if not _runs_session(command):
        roots = installed_plugin_roots(project_root)
        r = _session_call_root(command, roots)
        if r and r != roots[0]:
            return "ask", ("aid_session.py {} runs from another installed copy of the AID plugin "
                           "({}); the user must confirm it".format(_session_subcommand(command), r))
        return None, None
    bad = _form_reason(command)
    if bad:
        return "deny", bad
    return _confirmed_call_verdict(command, project_root)


def _confirmed_call_verdict(command, project_root):
    """A confirmed subcommand in the canonical (asked) spelling: ask or foreign."""
    sub = _session_subcommand(command)
    if _session_call_root(command, installed_plugin_roots(project_root)):
        return "ask", ("aid_session.py {} changes the AID phase, AID's runtime data or its learning "
                       "memory, so the user must confirm it (AID's gate asks in every folder)"
                       .format(sub))
    return "foreign", ("aid_session.py {} is a human-confirmed subcommand, run here from a script "
                       "that is not an installed AID plugin's (this plugin's is {}); the user "
                       "must confirm it".format(sub, str(SESSION_SCRIPT).replace("\\", "/")))


# ---------------------------------------------------------------------------
# Layer A: permission deny rules; Layer B: integrity baseline
# ---------------------------------------------------------------------------

_SETTINGS_BOMS = ((b"\xff\xfe", "utf-16-le"), (b"\xfe\xff", "utf-16-be"), (b"\xef\xbb\xbf", "utf-8"))


def read_settings(path):
    """
    AC-44: the ONE reader for Claude Code settings files (layer A, layer B, AC-40). UTF-8
    with or without a BOM, and UTF-16 LE/BE with a BOM. Returns (data, bom, codec) so a
    writer can keep the file's encoding. Raises FileNotFoundError / OSError, and ValueError
    when the bytes cannot be decoded or parsed.
    """
    raw = Path(path).read_bytes()
    bom, codec = next(((b, c) for b, c in _SETTINGS_BOMS if raw.startswith(b)), (b"", "utf-8"))
    return json.loads(raw[len(bom):].decode(codec)), bom, codec


def ensure_permissions(root):
    """
    Add AID's deny rules to <root>/.claude/settings.json (additive; never removes rules).
    Returns (added_count, error_or_None). A malformed settings file is left untouched; a
    BOM / UTF-16 file is rewritten in its own encoding (AC-44).
    """
    path = Path(root) / ".claude" / "settings.json"
    bom, codec = b"", "utf-8"
    try:
        data, bom, codec = read_settings(path) if path.exists() else ({}, bom, codec)
    except (ValueError, OSError) as e:
        return 0, "cannot read {}: {}".format(path, e)
    if not isinstance(data, dict):
        return 0, "{} is not a JSON object".format(path)
    perms = data.setdefault("permissions", {})
    if not isinstance(perms, dict):
        return 0, "permissions in {} is not an object".format(path)
    added = 0
    for key, rules in (("deny", DENY_RULES), ("ask", ASK_RULES)):     # T3-4: ask rules too
        have = perms.setdefault(key, [])
        if not isinstance(have, list):
            return 0, "permissions.{} in {} is not a list".format(key, path)
        missing = [r for r in rules if r not in have]
        have.extend(missing)
        added += len(missing)
    if not added:
        return 0, None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bom + (json.dumps(data, indent=2) + "\n").encode(codec))
    return added, None


def deny_rules_present(root):
    """Layer A intact: every deny rule AND every T3-4 ask rule is still in project settings."""
    try:
        perms = read_settings(Path(root) / ".claude" / "settings.json")[0].get("permissions", {})
        return (all(r in perms.get("deny", []) for r in DENY_RULES)
                and all(r in perms.get("ask", []) for r in ASK_RULES))
    except (ValueError, OSError, AttributeError):
        return False


def hooks_disabled(root):
    """
    "<file> sets <key>" when project settings switch Claude Code hooks or the AID plugin
    off, else None. LIMIT: once Claude Code has applied such a setting no AID hook runs at
    all, so this can only catch the window before Claude Code reloads its settings.
    AC-44: UTF-8 (BOM or not) and UTF-16 with a BOM are read; a file that exists but
    cannot be decoded or parsed is reported as possibly disabling hooks.
    """
    for name in ("settings.local.json", "settings.json"):
        try:
            data = read_settings(Path(root) / ".claude" / name)[0]
        except FileNotFoundError:
            continue
        except OSError:
            return ".claude/{} cannot be read (possibly disables hooks)".format(name)
        except ValueError:      # UnicodeDecodeError and JSONDecodeError are ValueErrors
            return ".claude/{} cannot be decoded or parsed (possibly disables hooks)".format(name)
        if not isinstance(data, dict):
            continue
        v = data.get("disableAllHooks")
        if v is True or str(v).strip().lower() == "true":
            return ".claude/{} sets disableAllHooks".format(name)
        plugins = data.get("enabledPlugins")
        if isinstance(plugins, dict) and any(
                str(k).split("@")[0].lower() == "aid" and v is False for k, v in plugins.items()):
            return ".claude/{} sets enabledPlugins aid to false".format(name)
    return None


def _sha(path):
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return "absent"


def integrity_base():
    return Path(os.environ.get("AID_HOME") or (Path.home() / ".aid")) / "integrity"


def integrity_dir(root):
    digest = hashlib.sha256(_key(os.path.realpath(str(root))).encode("utf-8")).hexdigest()[:16]
    return integrity_base() / digest


def snapshot(root, levels):
    return {"config_sha": _sha(Path(root) / ".aid" / "hooks" / "config.json"),
            "deny_rules": deny_rules_present(root),
            "levels": levels}


_SESSION_ID = re.compile(r"[A-Za-z0-9_.-]{1,128}")


def _seen_file(root):
    # Kept in the PROJECT, apart from the integrity dir, so deleting that dir does not also
    # erase the record that SessionStart took a baseline for the session.
    return Path(root) / ".aid" / "audit" / "integrity-sessions.json"


def _seen_sessions(root):
    try:
        data = json.loads(_seen_file(root).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_baseline(root, session_id, levels, session_start=False):
    if not session_id or not _SESSION_ID.fullmatch(session_id):
        return
    d = integrity_dir(root)
    d.mkdir(parents=True, exist_ok=True)
    snap = snapshot(root, levels)
    if session_start:
        snap["session_start"] = True    # AC-43: only a SessionStart baseline may latch the root
    (d / (session_id + ".json")).write_text(json.dumps(snap), encoding="utf-8")
    if session_start:
        seen = _seen_sessions(root)
        seen.pop(session_id, None)
        seen[session_id] = levels
        seen = dict(list(seen.items())[-20:])   # ponytail: last 20 sessions is plenty
        try:
            _seen_file(root).parent.mkdir(parents=True, exist_ok=True)
            _seen_file(root).write_text(json.dumps(seen), encoding="utf-8")
        except OSError:
            pass


def started_at(root, session_id):
    """AC-43: True when SessionStart (not layer B's first-use trust) wrote this session's
    baseline for root. The baseline lives under AID_HOME, so it survives .aid going away."""
    try:
        base = json.loads((integrity_dir(root) / (session_id + ".json")).read_text(encoding="utf-8"))
        return isinstance(base, dict) and base.get("session_start") is True
    except (OSError, ValueError):
        return False


LATCH_RELEASE_SOURCES = ("startup", "resume", "clear")


def release_latch(root, session_id):
    """
    AC-43 amendment (a): a SessionStart the user caused (LATCH_RELEASE_SOURCES; never
    "compact", which Claude Code fires mid-session on its own) ends the latch for a root
    whose .aid is gone. --resume/--continue keep the session id, so without this a project
    the user de-initialised between sittings was denied for the rest of the conversation.
    The baseline is kept minus its session_start flag (no new store; layer B still has it
    if .aid comes back). Returns True when a latch was released.
    """
    f = integrity_dir(root) / (session_id + ".json")
    try:
        base = json.loads(f.read_text(encoding="utf-8"))
        if isinstance(base, dict) and base.pop("session_start", None) is True:
            f.write_text(json.dumps(base), encoding="utf-8")
            return True
    except (OSError, ValueError):
        pass
    return False


_RANK = {"log": 0, "warn": 1, "block": 2}


def weakened_since_last_session(root, levels):
    """
    AC-42 (after the fact): compare this SessionStart's levels and deny rules with the
    previous session's record for this project, store the new record, and return the list
    of weakenings (empty when nothing got weaker).
    """
    d = integrity_dir(root)
    f = d / "@last-session.json"          # '@' cannot appear in a session id
    try:
        last = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        last = None
    now = snapshot(root, levels)
    try:
        d.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(now), encoding="utf-8")
    except OSError:
        pass
    out = []
    if isinstance(last, dict):
        for gate, before in sorted((last.get("levels") or {}).items()):
            after = levels.get(gate)
            if before in _RANK and after in _RANK and _RANK[after] < _RANK[before]:
                out.append("{} went from {} to {}".format(gate, before, after))
        if last.get("deny_rules") and not now["deny_rules"]:
            out.append("AID's permission deny rules are no longer in .claude/settings.json")
    return out


def check_integrity(root, session_id, levels, markers_missing=False):
    """
    Layer B, every gate call. Returns (violation_reason_or_None, baseline_levels).
    Order: hooks/plugin being disabled (AC-40), then the gate config and deny rules vs this
    session's baseline. A missing baseline is created (first-use trust) ONLY for a session
    SessionStart never recorded; for a recorded one it is a violation, judged at the levels
    SessionStart recorded (so "set config to log + delete the integrity dir" is refused).
    LIMIT (same honesty rule as AC-32): Phase 4+ code can still forge a matching baseline
    and the record; this closes only the cheap deletion route.
    markers_missing (AC-43): the root was latched from this session's baseline because its
    .aid markers are gone; that is a violation at the baseline's levels (N-15: code that
    also deletes the baseline is out of scope).
    """
    if markers_missing:
        try:
            lv = json.loads((integrity_dir(root) / (session_id + ".json")).read_text(encoding="utf-8"))["levels"]
        except (OSError, ValueError, TypeError, KeyError):
            lv = {}
        lv = lv if isinstance(lv, dict) else {}
        return ("AID's markers (.aid/state.json, .aid/hooks/config.json) disappeared mid-session "
                "from {}; restore the .aid folder to continue. If the user removed AID on "
                "purpose, resuming or restarting Claude Code ends this check".format(root),
                {g: lv[g] if lv.get(g) in _RANK else "block" for g in levels})
    base = None
    valid = bool(session_id) and _SESSION_ID.fullmatch(session_id) is not None
    if valid:
        f = integrity_dir(root) / (session_id + ".json")
        try:
            base = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            seen = _seen_sessions(root).get(session_id)
            if seen is not None:
                lv = seen if isinstance(seen, dict) else {}
                return ("AID's integrity baseline for this session disappeared (it was recorded "
                        "at session start); restart Claude Code to take a fresh one",
                        {g: lv.get(g, "block") for g in levels})
            write_baseline(root, session_id, levels)
    base_levels = base.get("levels", levels) if isinstance(base, dict) else levels
    off = hooks_disabled(root)
    if off:
        # LIMIT: this only works until Claude Code reloads its settings; after that no AID
        # hook runs at all, so it cannot be guaranteed (layer A is what prevents the write).
        return ("Claude Code hooks or the AID plugin are being disabled ({}). AID refuses tool "
                "calls while this is set; this only takes effect if Claude Code has not "
                "reloaded settings yet. Remove the setting to continue.".format(off), base_levels)
    if not isinstance(base, dict):
        return None, levels
    now = snapshot(root, levels)
    if now["config_sha"] != base.get("config_sha"):
        return ("AID gate config (.aid/hooks/config.json) changed during this session; "
                "restart Claude Code to accept the change", base_levels)
    if base.get("deny_rules") and not now["deny_rules"]:
        return ("AID permission deny rules were removed from .claude/settings.json during this "
                "session; restore them or restart Claude Code", base_levels)
    return None, base_levels
