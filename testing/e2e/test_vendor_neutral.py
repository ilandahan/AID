"""
AID Vendor-Neutrality Test

WHY THIS TEST:
- PROBLEM: AID is a general-purpose plugin, but its docs, skills and templates
  carried content from one past project that used a specific payment provider,
  plus example credentials using real vendor key prefixes. Readers copied both.
- SUCCESS: no tracked file names that payment provider, and no example
  credential uses a real vendor key prefix. Examples use placeholders such as
  <your-api-key> or EXAMPLE_NOT_A_REAL_KEY instead.

AID_VENDOR_SCAN_ROOT points the scan at another checkout of the same tree
(for example a `git archive HEAD` copy) so the test can be shown to fail on
the pre-scrub content. The file list always comes from this repo's git index.
"""
import os
import re
import subprocess

REPO_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
SCAN_ROOT = os.environ.get('AID_VENDOR_SCAN_ROOT', REPO_ROOT)
THIS_FILE = 'testing/e2e/test_vendor_neutral.py'

VENDOR_WORD = re.compile(r'stripe', re.IGNORECASE)
# Real vendor key prefixes: secret/test keys, webhook secrets, GitHub
# personal access tokens, cloud access-key IDs, chat bot/user tokens.
KEY_SHAPE = re.compile(r'(sk[-_](live|test)|whsec_|ghp_|AKIA[0-9A-Z]|xox[bp]-)')


def _tracked_files():
    out = subprocess.run(
        ['git', 'ls-files', '-z'], cwd=REPO_ROOT,
        capture_output=True, check=True,
    ).stdout.decode('utf-8')
    for rel in out.split('\0'):
        if not rel or rel == THIS_FILE or rel == '.gitleaksignore':
            continue
        if os.path.basename(rel) == 'package-lock.json':
            continue
        yield rel


def _hits(pattern):
    hits = []
    for rel in _tracked_files():
        path = os.path.join(SCAN_ROOT, rel)
        try:
            with open(path, 'rb') as f:
                data = f.read()
        except (FileNotFoundError, IsADirectoryError):
            continue
        if b'\0' in data:  # binary
            continue
        for n, line in enumerate(data.decode('utf-8', 'replace').splitlines(), 1):
            if pattern.search(line):
                hits.append(f'{rel}:{n}: {line.strip()[:120]}')
    return hits


def test_no_project_specific_payment_vendor():
    hits = _hits(VENDOR_WORD)
    assert not hits, 'Vendor name found; use "payment provider" or a placeholder:\n' + '\n'.join(hits)


def test_no_vendor_prefixed_example_keys():
    hits = _hits(KEY_SHAPE)
    assert not hits, 'Vendor-prefixed key shape found; use <your-api-key> or EXAMPLE_NOT_A_REAL_KEY:\n' + '\n'.join(hits)
