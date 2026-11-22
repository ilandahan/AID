"""
The ONE reader of feedback files (T8-3).

WHY: three writers produced three shapes, and the readers indexed raw keys of only one of
them. The live writer (``aid_session.py end``) stored a top-level ``rating``; every reader
looked for ``feedback.rating``, so /aid-end ratings were never counted, and the hand-written
shape (no ``timestamp``) crashed every command. Every reader now goes through
``normalize_entry``, which also redacts (T8-1: old unredacted files are covered).

Canonical shape (the collector's):
    {id, timestamp, session_id, source,
     context: {phase, role, interaction_type},
     feedback: {rating, verbal, skipped},
     debate: {occurred, ...}, decision?: {...}, metadata?: {...}}
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..redact import redact_obj


def _rating(value: Any) -> Optional[int]:
    try:
        r = int(value)
    except (TypeError, ValueError):
        return None
    return r if 1 <= r <= 5 else None


def _text(*parts: Any) -> Optional[str]:
    kept = [str(p).strip() for p in parts if isinstance(p, str) and p.strip()]
    return " ".join(kept) or None


def _file_time(path: Optional[Path]) -> str:
    try:
        ts = path.stat().st_mtime if path else None
    except OSError:
        ts = None
    dt = datetime.fromtimestamp(ts, timezone.utc) if ts else datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_entry(raw: Any, path: Optional[Path] = None,
                    names: Optional[Iterable[str]] = None) -> Optional[Dict[str, Any]]:
    """Map shape A (aid_session end/approve), C (collector) or D (hand-written) to the
    canonical shape, redacted. Returns None for something that is not a feedback object."""
    if not isinstance(raw, dict):
        return None
    stem = path.stem if path else None
    ts = raw.get("timestamp") if isinstance(raw.get("timestamp"), str) else _file_time(path)
    ctx = raw.get("context") if isinstance(raw.get("context"), dict) else {}

    if isinstance(raw.get("feedback"), dict):                      # C: the collector
        fb = raw["feedback"]
        entry = dict(raw)
        entry["feedback"] = {"rating": _rating(fb.get("rating")), "verbal": fb.get("verbal"),
                             "skipped": bool(fb.get("skipped", fb.get("rating") is None))}
        source = raw.get("source", "collector")
    elif "metrics" in raw or "qualitative" in raw:                 # D: hand-written
        m = raw.get("metrics") if isinstance(raw.get("metrics"), dict) else {}
        q = raw.get("qualitative") if isinstance(raw.get("qualitative"), dict) else {}
        verbal = _text(q.get("what_worked") and "Worked well: " + q["what_worked"],
                       q.get("what_didnt") and "To improve: " + q["what_didnt"], q.get("user_note"))
        entry = {"feedback": {"rating": _rating(m.get("rating")), "verbal": verbal,
                              "skipped": _rating(m.get("rating")) is None and not verbal},
                 "metadata": {"revisions": m.get("revisions")}}
        source = raw.get("source", "hand-written")
    else:                                                          # A: aid_session.py
        verbal = _text(raw.get("worked_well") and "Worked well: " + raw["worked_well"],
                       raw.get("to_improve") and "To improve: " + raw["to_improve"],
                       raw.get("note"))
        entry = {"feedback": {"rating": _rating(raw.get("rating")), "verbal": verbal,
                              "skipped": _rating(raw.get("rating")) is None and not verbal}}
        meta = {k: raw[k] for k in ("duration_minutes", "subagent_review") if k in raw}
        if meta:
            entry["metadata"] = meta
        source = raw.get("source", "aid-end")
        # T17-18 (L3c-2d): the phase (0-5) first, so it maps to a real phase skill; the
        # role-specific display name ("Technical Design") only when there is no phase.
        phase_raw = raw.get("phase")
        ctx = {"phase": phase_raw if phase_raw not in (None, "") and not isinstance(phase_raw, bool)
               else raw.get("phase_display"), "role": raw.get("role")}

    entry["id"] = str(raw.get("id") or stem or ts)
    entry["timestamp"] = ts
    entry["session_id"] = str(raw.get("session_id") or entry["id"])
    entry["source"] = source
    phase = ctx.get("phase", raw.get("phase"))
    entry["context"] = {
        "phase": str(phase) if phase not in (None, "") else "unknown",
        "role": str(ctx.get("role") or raw.get("role") or "unknown"),
        "interaction_type": str(ctx.get("interaction_type") or
                                ("phase-gate" if source == "phase-approve" else "session")),
    }
    if not isinstance(entry.get("debate"), dict):
        entry["debate"] = {"occurred": False}
    # T8 review r1: readers call .lower() and similar on these; a list or number in a
    # hand-edited file crashed every command.
    entry["feedback"]["verbal"] = _str_or_none(entry["feedback"].get("verbal"))
    for key, fields in (("debate", ("user_challenge", "original_recommendation", "final_decision",
                                    "outcome", "learning")),
                        ("decision", ("topic", "topic_category", "chosen", "rationale", "confidence"))):
        if key in entry and not isinstance(entry[key], dict):
            entry.pop(key) if key == "decision" else entry.update(debate={"occurred": False})
        for f in fields:
            if isinstance(entry.get(key), dict) and f in entry[key]:
                entry[key][f] = _str_or_none(entry[key][f])
    if isinstance(entry.get("decision"), dict):
        alts = entry["decision"].get("alternatives")
        entry["decision"]["alternatives"] = [str(a) for a in alts] if isinstance(alts, list) else []
    return redact_obj(entry, names, skip_keys=("timestamp", "id", "session_id"))


def _str_or_none(v: Any) -> Optional[str]:
    if v is None or isinstance(v, str):
        return v
    if isinstance(v, list):
        return " ".join(str(x) for x in v)
    return str(v)


def read_entries(directories: Iterable[Path], names: Optional[Iterable[str]] = None) -> List[Dict[str, Any]]:
    """Every readable feedback file in ``directories``, normalised and sorted by time.
    Unreadable or non-object files are skipped, never fatal."""
    entries = []
    for d in directories:
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.json")):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            e = normalize_entry(raw, path, names)
            if e is not None:
                entries.append(e)
    return sorted(entries, key=lambda x: x["timestamp"])
