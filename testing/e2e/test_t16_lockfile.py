"""
T16 orchestrator (reports/T16-acceptance.md, T16-42 lockfile echo, T16-49 cucumber moderates):
package-lock.json agrees with package.json and plugin.json, and the root dependency tree is
cucumber 13.3+ without the glob/minimatch versions npm audit flagged.

WHY THIS TEST:
- PROBLEM: the lockfile still said version 1.0.0 and an old license while package.json and
  plugin.json said 3.0.8, and @cucumber/cucumber 12.9.0 pulled glob 13 -> minimatch 10, three
  moderate advisories (GHSA-3g3m-2fjr-6pw4, GHSA-g3hv-75wg-m249) on every `npm ci`.
- COST OF FAILURE: `npm audit` stays red for every user, a release reads three different
  versions, and a node outside cucumber's engines gets a lockfile it cannot run.
- SUCCESS: one version and license everywhere, cucumber >= 13.3.0 locked, no lockfile entry
  in the vulnerable glob/minimatch ranges, and package.json engines admit only node majors
  that cucumber 13 itself supports.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def ver(s):
    return tuple(int(x) for x in re.match(r"(\d+)\.(\d+)\.(\d+)", s).groups())


def admitted_majors(rng, top=40):
    """Node majors a simple npm engines range admits (forms used here: N, ^N.m.p, >=N[.m.p])."""
    out = set()
    for clause in rng.split("||"):
        c = clause.strip()
        m = re.fullmatch(r">=\s*(\d+)(?:\.\d+(?:\.\d+)?)?", c)
        if m:
            out.update(range(int(m.group(1)), top))
            continue
        m = re.fullmatch(r"\^?(\d+)(?:\.\d+(?:\.\d+)?)?", c)
        assert m, "unparsed engines clause: " + c
        out.add(int(m.group(1)))
    return out


PKG = load("package.json")
LOCK = load("package-lock.json")
ROOT = LOCK["packages"][""]


def test_t16_42_lockfile_echoes_package_and_plugin_version():
    plugin = load(".claude-plugin/plugin.json")
    assert PKG["version"] == plugin["version"]
    assert LOCK["version"] == PKG["version"], LOCK["version"]
    assert ROOT["version"] == PKG["version"], ROOT["version"]


def test_t16_42_lockfile_echoes_package_license():
    assert ROOT.get("license") == PKG["license"], ROOT.get("license")


def test_t16_49_cucumber_13_3_in_manifest_and_lockfile():
    assert PKG["dependencies"]["@cucumber/cucumber"] == "^13.3.0"
    assert ROOT["dependencies"]["@cucumber/cucumber"] == "^13.3.0"
    locked = LOCK["packages"]["node_modules/@cucumber/cucumber"]["version"]
    assert ver(locked) >= (13, 3, 0), locked


def test_t16_49_no_audited_glob_or_minimatch_in_lockfile():
    # npm audit at 5f8f199: glob 9.0.0 - 14.0.1, minimatch 7.0.0 - 11.0.0 (moderate).
    bad = []
    for key, meta in LOCK["packages"].items():
        name = key.rsplit("node_modules/", 1)[-1]
        if name == "glob" and (9, 0, 0) <= ver(meta["version"]) <= (14, 0, 1):
            bad.append((key, meta["version"]))
        if name == "minimatch" and (7, 0, 0) <= ver(meta["version"]) <= (11, 0, 0):
            bad.append((key, meta["version"]))
    assert not bad, bad


def test_t16_49_root_engines_fit_cucumber_engines():
    assert ROOT["engines"] == PKG["engines"]
    cuke = LOCK["packages"]["node_modules/@cucumber/cucumber"]["engines"]["node"]
    root = admitted_majors(PKG["engines"]["node"])
    extra = sorted(root - admitted_majors(cuke))
    assert not extra, "package.json engines admit node {} that {} refuses".format(extra, cuke)
    assert 20 not in root and 22 in root and 24 in root


def test_t16_49_lockfile_root_matches_manifest():
    # guard: the lockfile was regenerated from this exact manifest, not hand-edited
    for field in ("dependencies", "devDependencies", "optionalDependencies"):
        assert ROOT.get(field) == PKG.get(field), field
    assert ROOT["name"] == PKG["name"] == LOCK["name"]


def test_t16_49_every_locked_package_is_registry_pinned():
    # guard: npm ci verifies each tarball against a sha512 from the public registry
    loose = [k for k, m in LOCK["packages"].items()
             if k and not m.get("link")
             and not (str(m.get("resolved", "")).startswith("https://registry.npmjs.org/")
                      and str(m.get("integrity", "")).startswith("sha512-"))]
    assert not loose, loose
