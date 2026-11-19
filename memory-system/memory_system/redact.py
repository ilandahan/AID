"""
The ONE redactor for the AID learning loop (T8-1, A-07).

WHY: session feedback was stored verbatim. A real ``aid_session.py end`` run kept a client
name, an email address and a project path in ``~/.aid/feedback/pending/``, and
``--sync-memory`` copied free text into memory. Feedback is redacted when it is written AND
when it is read, so files written before this change are covered too.

BEST EFFORT, stated in the docs: emails, URLs, absolute paths, ``file.ext:line``
references, common secret tokens, the project's own names (cwd and root folder names, git
remote owner and repo) and the OS user name are replaced. A person's or a company's name
written as plain words is NOT caught unless it is one of those names.
"""

import getpass
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Iterable, Optional, Set

# Ordered: earlier patterns win, so a URL or an e-mail address is not cut up as a path.
# A path keeps going across a space while the next word still contains a slash
# (C:\Users\Jane Doe\My Projects\x.py). T8 review r1: the space used to end it early.
_CONT = r"(?: [^\s\"'<>|]*[\\/][^\s\"'<>|]*)*"
_MAX_LEN = 100_000      # T8 review r1: bound the regex work on hostile pending files

# (label, pattern, replacement or None for "[label]"). Ordered: earlier patterns win, so a
# URL or an e-mail address is not cut up as a path. Every pattern starts at a word boundary
# or a negative lookbehind, so each word is tried once (linear time).
_PATTERNS = (
    ("url", re.compile(r"(?i)\b(?:https?|ftp|ssh|git|file)://[^\s\"'<>]+|\bwww\.[^\s\"'<>]+"), None),
    # scp-like git remotes: git@github.com:owner/repo.git
    ("url", re.compile(r"(?<![\w.-])[\w.-]+@[\w.-]+\.[A-Za-z]{2,}:[\w./~-]+"), None),
    ("email", re.compile(r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*"
                         r"\.[A-Za-z]{2,}"), None),
    ("token", re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{16,}"
        r"|(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{10,}|glpat-[A-Za-z0-9_-]{16,}|npm_[A-Za-z0-9]{20,}"
        r"|AIza[0-9A-Za-z_-]{30,}|xox[abprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}"
        r"|eyJ[\w-]{8,}\.[\w-]{8,}\.[\w-]{2,})"), None),
    ("token", re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}"), r"\1 [token]"),
    ("token", re.compile(r"(?i)\b(password|passwd|pwd|secret|api[_-]?key|access[_-]?key|token)"
                         r"(\s*[:=]\s*)[^\s,;]+"), r"\1\2[token]"),
    # A quoted path is one unit, spaces and all.
    ("path", re.compile(r"([\"'])(?:[A-Za-z]:[\\/]|\\\\|//|/|~[\w.-]*[\\/]|\$\{?HOME\}?[\\/]"
                        r"|%[A-Za-z]+%[\\/])[^\"'\n]*\1"), r"\1[path]\1"),
    # UNC (both slash styles), drive paths, $HOME / %USERPROFILE% paths, ~ and ~user paths,
    # then POSIX paths with at least two segments. A single segment (/phase-approve,
    # and/or) is not a path.
    ("path", re.compile(r"\\\\[^\s\\]+\\[^\s\"'<>|]*" + _CONT), None),
    ("path", re.compile(r"(?<![:\w/])//[^\s/\"'<>|]+/[^\s\"'<>|]*" + _CONT), None),
    ("path", re.compile(r"(?i)(?<![A-Za-z0-9])[a-z]:[\\/][^\s\"'<>|]*" + _CONT), None),
    ("path", re.compile(r"(?i)(?:\$\{?HOME\}?|%(?:USERPROFILE|HOMEPATH|APPDATA|LOCALAPPDATA)%)"
                        r"[\\/][^\s\"'<>|]*" + _CONT), None),
    ("path", re.compile(r"(?<![\w.~/-])~[\w.-]*[\\/][^\s\"'<>|]*" + _CONT), None),
    ("path", re.compile(r"(?<![\w./-])/[^\s/\"'<>|]+/[^\s\"'<>|]*" + _CONT), None),
    ("file-ref", re.compile(r"(?<![\w./\\-])[\w-]+(?:[./\\][\w-]+)*\.[A-Za-z][A-Za-z0-9]{0,5}"
                            r"(?::\d+(?::\d+)?\b|#L\d+)"), None),
    ("token", re.compile(r"\b[0-9a-fA-F]{32,}\b"), None),
    ("token", re.compile(r"(?<![\w+/=-])(?=[A-Za-z0-9+/_=-]*\d)(?=[A-Za-z0-9+/_=-]*[A-Za-z])"
                         r"[A-Za-z0-9+/_-]{40,}={0,2}"), None),
)

# Folder and repo names too generic to remove from feedback text.
_STOP = {
    "app", "apps", "code", "demo", "dev", "docs", "home", "main", "master", "project",
    "projects", "repo", "repos", "src", "source", "test", "tests", "testing", "tmp", "temp",
    "user", "users", "work", "workspace", "desktop", "documents", "downloads", "phase",
    "feature", "features", "build", "local", "files", "data", "scratch", "sandbox", "clean",
    "the", "and", "for", "with",
}


def _usable(name: str, min_len: int = 4) -> bool:
    n = name.strip().lower()
    return len(n) >= min_len and n not in _STOP and not n.isdigit()


def _git_remote_names(root: Path) -> Set[str]:
    """Owner and repo of every git remote of ``root`` (https, ssh and scp forms)."""
    try:
        out = subprocess.run(["git", "-C", str(root), "config", "--get-regexp", r"^remote\..*\.url$"],
                             capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return set()
    names = set()
    for line in out.splitlines():
        url = line.split(None, 1)[-1].strip()
        parts = [p for p in re.split(r"[/:]", url) if p]
        if len(parts) >= 2:
            names.add(re.sub(r"\.git$", "", parts[-1]))
            names.add(parts[-2])
    return names


def context_names(cwd: Optional[str] = None, root: Optional[str] = None) -> Set[str]:
    """The project's own names (cwd and root basenames, git remote owner/repo) and the OS
    user name: words that identify this project or person in otherwise generic text."""
    names: Set[str] = set()
    for d in (cwd, root):
        if d:
            names.add(Path(d).name)
    for d in {root, cwd} - {None}:
        names |= _git_remote_names(Path(d))
    return {n for n in names if _usable(n)} | user_names()


def user_names() -> Set[str]:
    """The OS user name(s): replaced with [user], not [project]."""
    users = set()
    try:
        users.add(getpass.getuser())
    except Exception:
        pass
    users |= {os.environ.get("USERNAME", ""), os.environ.get("USER", ""), Path.home().name}
    return {u for u in users if _usable(u, 3)}


def _name_patterns(names: Iterable[str]):
    users = {u.lower() for u in user_names()}
    for n in sorted(set(names), key=len, reverse=True):
        label = "[user]" if n.lower() in users else "[project]"
        parts = [p for p in re.split(r"[-_. ]+", n) if p]
        if not parts or not _usable("".join(parts), 3 if label == "[user]" else 4):
            continue
        # secret-proj also as Secret_Proj, SECRET.PROJ, "secret proj" and secretproj
        body = r"[-_. ]?".join(re.escape(p) for p in parts)
        yield label, re.compile(r"(?i)(?<![A-Za-z0-9])" + body + r"(?![A-Za-z0-9])")


_TRAIL = ".,;:!?"
_CLOSE = {")": "(", "]": "[", "}": "{"}


def _path_sub(m) -> str:
    """T15-28: "[path]" plus the sentence punctuation the path class swallowed
    (``notes.txt,`` -> ``[path],``). A closing bracket is kept with the path only when the
    path itself opened it."""
    s = m.group(0)
    end = len(s)
    while end > 1:
        ch = s[end - 1]
        if ch in _TRAIL or (ch in _CLOSE and s[:end].count(_CLOSE[ch]) < s[:end].count(ch)):
            end -= 1
            continue
        break
    return "[path]" + s[end:]


def redact(text: Any, names: Optional[Iterable[str]] = None) -> Any:
    """Replace each sensitive part of ``text`` with a typed placeholder ([email], [path],
    [url], [token], [file-ref], [project], [user]). Non-strings are returned unchanged.
    Idempotent. Text longer than _MAX_LEN is cut there first."""
    if not isinstance(text, str) or not text:
        return text
    out = text if len(text) <= _MAX_LEN else text[:_MAX_LEN] + " [truncated]"
    for label, rx, repl in _PATTERNS:
        if label == "path" and repl is None:
            out = rx.sub(_path_sub, out)
        else:
            out = rx.sub(repl or "[{}]".format(label), out)
    for label, rx in _name_patterns(names or ()):
        out = rx.sub(label, out)
    return out


def redact_obj(obj: Any, names: Optional[Iterable[str]] = None, skip_keys=("timestamp",)) -> Any:
    """``redact`` applied to every string inside dicts and lists (keys are kept)."""
    names = list(names or ())
    if isinstance(obj, dict):
        return {k: (v if k in skip_keys else redact_obj(v, names, skip_keys)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_obj(v, names, skip_keys) for v in obj]
    return redact(obj, names)
