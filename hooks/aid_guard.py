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
    "/.claude/settings.json",
    "/.claude/settings.local.json",
    "/.claude/hooks/",
    "/.claude/plugins/cache/",
    "/.aid/state.json",           # T3-1: the phase the gates read; only aid_session.py writes it
)
# Removing or renaming one of these directories removes protected files with it.
PROTECTED_PARENTS = ("/.aid", "/.claude", "/.aid/hooks", "/.aid/pipeline", "/.claude/hooks",
                     "/.claude/plugins")
# Literal fragments: a Phase 4+ command whose text names one of these is refused
# (catches python -c "open('.claude/settings.json','w')" and similar). Best effort.
PROTECTED_LITERALS = (".aid/hooks", ".aid/integrity", "escalation.json",
                      ".claude/settings.json", ".claude/settings.local.json",
                      ".claude/hooks", ".claude/plugins/cache")

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
                         "memory-sync", "memory-apply")
_INTERPRETERS = ("python", "python3", "py")
ASK_RULES = tuple("Bash({} *aid_session.py {}*)".format(i, s)
                  for s in CONFIRMED_SUBCOMMANDS for i in _INTERPRETERS)
# A3: interpreter, the script path (quoted or bare), the subcommand BARE, then arguments that
# are bare or double-quoted plain text (--note "rating 4 clear scope"), single spaces.
_CANONICAL_CALL = re.compile(
    r"^(?:python|python3|py) (?:\"[^\"\n]+\"|'[^'\n]+'|[^\s\"']+) [A-Za-z0-9._:-]+"
    r"(?: (?:[A-Za-z0-9._:-]+|\"[A-Za-z0-9 ._:-]+\"))*$")


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
    # EVERY occurrence: in `".../AID_SESSION x/../AID_SESSION.PY" jump` the first one is a
    # directory name, and the word after it is not the subcommand (T3 CI, Linux).
    for m in re.finditer("aid_session", cleaned.lower()):
        words = cleaned[m.start():].split()[1:]
        first = next((w for w in words if not w.startswith("-")), "")
        if first.lower() in CONFIRMED_SUBCOMMANDS:
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
    raw = command.strip()
    bare = raw.replace('"', "").replace("'", "")
    if _CANONICAL_CALL.match(raw) and any(
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


def _env_protected():
    """Protected paths that env vars move away from a .claude / .aid folder name, so the
    suffix list misses them: $CLAUDE_CONFIG_DIR/{settings.json, plugins/cache/, hooks/}
    and the layer-B baseline under $AID_HOME/integrity/. Directories end in "/" and
    match by prefix."""
    out = [_key(os.path.realpath(str(integrity_base()))).rstrip("/") + "/"]
    cfg = os.environ.get("CLAUDE_CONFIG_DIR")
    if cfg:
        base = _key(os.path.realpath(cfg)).rstrip("/")
        out += [base + "/settings.json", base + "/plugins/cache/", base + "/hooks/"]
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


def _pre4(command, cwd, root, phase, rules, extra):
    """Before Phase 4, block-mode semantics: None = allowed, else the reason."""
    # First, before the heredoc idiom: Git Bash ends a heredoc at "EOF\r" (measured), so a
    # CR anywhere would let the idiom's body end earlier than this gate thinks.
    if "\r" in command:
        return ("carriage return in the command (Git Bash ends heredocs and words differently "
                "with it); use plain newlines")
    if _is_plugin_session(command):
        return None
    if "aid_session" in command.lower():
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
            if (k != 0 or (len(segs) > 1 and seg.op != "&&") or target in (None, SUSPICIOUS)
                    or any(s.op not in ("&&", "|") for s in segs[:-1])
                    or any(c not in (".", "..") and c[-1:] in (".", " ") for c in parts)
                    or not _same_dir(target, root)):
                return ("cd is allowed only as the first command, only to the project root, "
                        "and only followed by && (cd \"<root>\" && git status)")
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


def lex(command):
    """
    Best-effort split of a command line into Segments for the Phase 4+ check. Raises
    ParseError when the text cannot be parsed. $( ), <( ), >( ) and backtick bodies are
    lexed recursively and returned as extra segments: the shell runs them.
    """
    s = command.replace("\\\r\n", "").replace("\\\n", "")
    segs, subs = [], []
    seg, word, dyn, has_word = Segment(), [], False, False
    seg_start, depth = 0, 0
    pending_heredocs = []      # (delimiter, quoted, strip_tabs)
    pending_redirect = None    # ("w"|"r"|"hd", op)
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


def _cp_mv_targets(name, words, args, vcwd):
    """
    Write targets of cp/mv, honouring -t/-tX/--target-directory[=X], -T, and copy-into-dir.
    Returns (targets, reason_or_None). Best effort (abbreviated long options are not modelled).
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
    if linking and any(is_protected_or_parent(normalize(s.text, vcwd)) for s in sources if not s.dynamic):
        return [], "linking to an AID control file"
    if dest is None:
        return [], None
    dnorm = normalize(dest.text, vcwd) if not dest.dynamic else None
    if recursive and dnorm not in (None, SUSPICIOUS) and is_protected_or_parent(dnorm):
        return [], "recursive copy into a folder holding AID control files"
    targets = [dest]
    into_dir = t_dir is not None or (not no_target_dir and (
        dest.text.endswith(("/", "\\")) or (dnorm not in (None, SUSPICIOUS) and os.path.isdir(dnorm))))
    if into_dir:
        targets += [Word(os.path.join(dest.text, os.path.basename(s.text.rstrip("/\\"))),
                         dest.dynamic or s.dynamic) for s in sources]
    if name == "mv":
        targets += sources                     # moving a file away changes it too
    return targets, None


def _write_word_verdict(w, vcwd, root, phase, rules):
    """AC-31: a target that contains a variable keeps the literal check on its text."""
    if w.dynamic and mentions_protected(w.text):
        return "'{}' names an AID control file (protected in every phase)".format(w.text)
    return write_target_verdict("$dyn" if w.dynamic else w.text, vcwd, root, phase, rules)


def _phase4_exempt(name, words, args):
    """AC-33: reading or staging a control file is not writing it (redirects still checked)."""
    if name in READ_ONLY:
        return True
    if name != "git" or any(w.dynamic for w in words):
        return False
    sub, _rest, _ = _git_split(args, None)
    return sub in GIT_EXEMPT and not any(a.startswith("-") and mentions_protected(a) for a in args)


def _phase4_check(command, cwd, root, phase, rules):
    """BEST EFFORT (see section comment): literal control-file paths in a Bash command."""
    try:
        segments, subs = lex(command)
    except ParseError as e:
        return "cannot parse the command safely ({})".format(e) if mentions_protected(command) else None
    for body in subs:                     # substitution bodies run in subshells; cwd unknown
        reason = _phase4_check(body, None, root, phase, rules)
        if reason:
            return reason

    vcwd, depth, saved = cwd, 0, []
    for seg in segments:
        while depth < seg.depth:
            saved.append(vcwd)
            depth += 1
        while depth > seg.depth:
            vcwd = saved.pop() if saved else vcwd
            depth -= 1

        for w in seg.writes:
            reason = _write_word_verdict(w, vcwd, root, phase, rules)
            if reason:
                return "redirection: " + reason

        words = list(seg.words)
        while words and words[0].text in KEYWORDS_PREFIX and not words[0].dynamic:
            words.pop(0)
        while words and re.match(r"^[A-Za-z_][A-Za-z0-9_]*(\[[^\]]*\])?=", words[0].text):
            words.pop(0)
        if not words or (len(words) == 1 and words[0].text in KEYWORDS_ALONE):
            continue
        t = words[0].text
        name = t.lower() if not words[0].dynamic and "/" not in t and "\\" not in t else None
        if name and IS_WIN:
            name = re.sub(r"\.(exe|cmd|bat)$", "", name)
        args = [w.text for w in words[1:]]

        if _phase4_exempt(name, words, args):
            continue
        if name not in WRITERS:
            for a in args:
                cand = a.split("=", 1)[1] if a.startswith("-") and "=" in a else (None if a.startswith("-") else a)
                # Not a write target: an unreasonable form (`D:`, `test:unit`) is not a control
                # file. Writer operands and redirect targets keep the SUSPICIOUS denial for
                # literal words (stream, drive-relative, UNC); words with ~ or $ are dynamic
                # and get only the mentions_protected check (best effort, N-1).
                n = normalize(cand, vcwd) if cand else None
                if mentions_protected(a) or (n != SUSPICIOUS and is_protected_or_parent(n)):
                    return "'{}' would touch an AID control file".format(seg.raw.strip()[:80])
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
                reason = _write_word_verdict(w, vcwd, root, phase, rules)
                if not reason and name in ("rm", "rmdir", "mv") and is_protected_or_parent(normalize(w.text, vcwd)):
                    reason = "'{}' contains AID control files".format(w.text)
                if reason:
                    return "{}: {}".format(name, reason)
        if name == "cd":
            target = None
            if len(words) == 2 and not words[1].dynamic and words[1].text != "-":
                target = normalize(words[1].text, vcwd) if vcwd is not None or os.path.isabs(words[1].text) else None
            # A cd that would fail (missing dir) leaves the real cwd unchanged: unknown.
            vcwd = target if target not in (None, SUSPICIOUS) and os.path.isdir(target) else None
        elif name in ("pushd", "popd"):
            vcwd = None
    return None


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


def evaluate_powershell(command, cwd, root, phase, rules):
    """
    Return None when a PowerShell command may run, else a reason string.

    Every phase: no aid_session.py call (T7-4, D2). Before code_execute_min_phase: nothing
    runs (T7-3, D1). Otherwise, or with no phase: the best-effort control-file check on a
    copy with backticks removed and backslashes as '/' (T7-5, D3); layers A and B remain the
    real protection, as for Bash at that phase.
    """
    if ps_mentions_session(command):
        return PS_SESSION_REASON
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
    return _phase4_check(norm, cwd, root, phase, rules)


PS_PROTECTED_LITERALS = PROTECTED_LITERALS + (".aid/state.json", ".aid/pipeline/escalation.json")


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
