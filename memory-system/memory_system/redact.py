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
    # T17-14 (I-20 rule 7): ANY scheme (postgres, mysql, mongodb+srv, redis, amqp, ldap, s3, ...),
    # so credentials in scheme://user:pass@host and scheme://:pass@host are gone. The start is a
    # lookbehind, not \b, so each run of scheme characters is tried once (linear time).
    ("url", re.compile(r"(?i)(?<![a-z0-9+.-])[a-z][a-z0-9+.-]*://[^\s\"'<>]+|\bwww\.[^\s\"'<>]+"), None),
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
    # T17-14 (I-20 rule 6): Authorization: <any scheme word> V (Token, Digest, ApiKey, ...).
    ("token", re.compile(r"(?i)\b(authorization[\"']?\s*[:=]\s*[\"']?[A-Za-z][\w-]{0,30})[ \t]+"
                         r"[^\s\"',;]+"), r"\1 [token]"),
    # T16-26 (I-14): a secret NAME may carry a prefix and a suffix (AWS_SECRET_ACCESS_KEY=,
    # client_secret:, GITHUB_TOKEN=). Applied by _named_secrets (rx None), not by re.sub.
    ("token", None, None),
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

# T16-26 (I-14). The contract's name rule is
#   (?i)(?<![A-Za-z0-9])([A-Za-z0-9_.-]*(?:KEYWORDS)[A-Za-z0-9_.-]*)(\s*[:=]\s*)(["']?)[^\s,;"']+\3
#   -> \1\2\3[token]\3
# As ONE regex it backtracks cubically on a long run of name characters ("_" * 20000 does not
# finish), which would break the _MAX_LEN linear-time bound. _named_secrets gives the same
# matches in linear time: the name is a whole run of name characters (it cannot stop inside one,
# since the next character must be a separator, and the leftmost start of a run always matches
# when a later one does), the keyword is checked on that run, then the value is matched.
_KEYWORD = re.compile(r"(?i)password|passwd|pwd|secret|api[_-]?key|access[_-]?key|private[_-]?key"
                      r"|token|credential")
# T17-14 (I-20 rule 1): an optional closing quote after the name ({"password": "V"},
# 'api_key':'V', "DB_PASSWORD"="V"). It is part of the separator group, so it is kept.
_NAME_SEP = re.compile(r"(?<![A-Za-z0-9_.-])([A-Za-z0-9_.-]+)([\"']?\s*[:=]\s*)")
# T17-14: a quoted value may contain spaces (password="two words"); bounded length keeps it
# linear. An unclosed quote still redacts the run after it. Group 1 = the opening quote.
_VALUE = re.compile(r"\"[^\"\n]{1,256}\"|'[^'\n]{1,256}'|([\"']?)[^\s,;\"']+\1|[\"'][^\s,;\"']+")
# T17-14 (I-20 rule 2): --<name> V / --<name>=V for a secret-ish flag name.
_FLAG = re.compile(r"(?<![\w-])(--[A-Za-z0-9_-]+)(=|[ \t]+(?=[^\s-]))")
# T17-14 (I-20 rule 3): -p<V> attached after a MySQL/MariaDB client, and sshpass -p V. The
# command word is case-insensitive; -p is not (-P is a port). T17 R1-04: the attached value
# may be quoted (-p'V', -p"V words"); its quotes are kept.
_MYSQL_P = re.compile(r"((?i:(?<![\w-])(?:mysqldump|mysqladmin|mysql|mariadb-dump|mariadb)\b)"
                      r"[^\n;|&]{0,300}?(?<![\w-])-p)"
                      r"(?![\"']?\[)(\"[^\"\n]{1,256}\"|'[^'\n]{1,256}'|[\"']?[^\s\"',;]+)")
# T17 R1-04: sshpass -p V, -pV, -p'V' and -p "V" (quoted values, as for mysql above).
_SSHPASS = re.compile(r"((?i:(?<![\w-])sshpass)[ \t]+-p[ \t]*)(?![\"']?\[token\])(\"[^\"\n]{1,256}\""
                      r"|'[^'\n]{1,256}'|[\"']?[^\s\"',;]+)")
# T17-14 (I-20 rule 4): curl -u / --user / --user= user:pass -> user:[token].
_CURL_USER = re.compile(r"((?i:(?<![\w-])curl\b)[^\n;|&]{0,300}?(?<![\w-])(?:-u[ \t]*|--user(?:=|[ \t]+))"
                        r"[\"']?[^\s:\"']+:)(?!\[token\])[^\s\"']+")


def _is_secret_name(name: str) -> bool:
    """I-14 keyword anywhere in the name, or (T17-14, I-20 rule 5) the exact name ``pass``
    (bypass, pass_rate and passes are not secret names)."""
    return bool(_KEYWORD.search(name)) or name.lstrip("-").lower() == "pass"


def _value_out(v) -> str:
    """The redacted value, quotes kept: "V" -> "[token]", 'V' -> '[token]', V -> [token]."""
    return _quoted_token(v.group(0))


def _quoted_token(s: str) -> str:
    q = s[0] if s[0] in "\"'" else ""
    close = q if q and len(s) >= 2 and s.endswith(q) else ""
    return q + "[token]" + close


def _flag_secrets(text: str) -> str:
    out = []
    pos = 0
    at = 0
    while True:
        m = _FLAG.search(text, at)
        if not m:
            break
        v = _VALUE.match(text, m.end()) if _is_secret_name(m.group(1)) else None
        if v is None:
            at = m.end(1)
            continue
        out.append(text[pos:m.end()] + _value_out(v))
        pos = at = v.end()
    out.append(text[pos:])
    return "".join(out)


def _cli_secrets(text: str) -> str:
    """T17-14 (I-20 rules 2-4): CLI-flag secrets, short password flags and curl user:pass."""
    text = _flag_secrets(text)
    # T17 R1-04: an attached quoted value keeps its quotes: -p'V' -> -p'[token]'.
    text = _MYSQL_P.sub(lambda m: m.group(1) + _quoted_token(m.group(2)), text)
    text = _SSHPASS.sub(lambda m: m.group(1) + _quoted_token(m.group(2)), text)
    return _CURL_USER.sub(r"\1[token]", text)
# T16-26: a PEM private-key block, through its END line (or the end of the text).
_PEM = re.compile(r"-----BEGIN ([A-Z0-9 ]*)PRIVATE KEY-----.*?(?:-----END \1PRIVATE KEY-----|\Z)",
                  re.DOTALL)


def _named_secrets(text: str) -> str:
    out = []
    pos = 0         # copied up to here
    at = 0          # search from here
    while True:
        m = _NAME_SEP.search(text, at)
        if not m:
            break
        v = _VALUE.match(text, m.end()) if _is_secret_name(m.group(1)) else None
        if v is None:
            at = m.end(1)
            continue
        out.append(text[pos:m.end()] + _value_out(v))
        pos = at = v.end()
    out.append(text[pos:])
    return "".join(out)


def _url_sub(m) -> str:
    """T16-32: "[url]" plus the sentence punctuation the URL class swallowed
    (``see https://x.example/a.`` -> ``see [url].``), as for paths (T15-28)."""
    return "[url]" + _path_sub(m)[len("[path]"):]


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
    out = _PEM.sub("[private-key]", out)
    for label, rx, repl in _PATTERNS:
        if rx is None:
            out = _cli_secrets(_named_secrets(out))
        elif label == "url" and repl is None:
            out = rx.sub(_url_sub, out)
        elif label == "path" and repl is None:
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
