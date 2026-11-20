# Security Policy

## Supported Versions

Security fixes are applied to the latest release on the `main` branch. Older
versions are not maintained.

| Version | Supported          |
| ------- | ------------------ |
| 3.0.8 (current, `main`) | :white_check_mark: |
| < 3.0.8 | :x: |

The `version` field in `.claude-plugin/plugin.json` identifies the release you
are running; please include it in your report.

## Breather (optional, user-wide)

breather is optional and installs into `~/.claude`, so once installed it is active in **every** project on the machine. In the first session of each day, and again on each prompt until you answer or skip its day-plan question, its instructions tell Claude to fetch **today's calendar events** automatically, before answering and without asking you, through any connector available in the session. It names Google Calendar / Gmail and Microsoft 365 / Outlook as examples: it asks only for today's events, but a Gmail or Outlook connector may also have access to your mail. The events go into the conversation (and so to the model and through that connector), and the meeting start times are saved under `~/.claude/state/breather/`. It also adds hooks and a status line to `~/.claude/settings.json`; see [integrations/breather/README.md](integrations/breather/README.md) for everything it does. To keep this off, do not install breather, or remove it with `/breather-stop` (uninstall).

The vendored installer is pinned: `integrations/breather/PAYLOAD.lock.json` records the upstream commit and the SHA-256 of the installer and of every file it writes, and a test checks them.

## Reporting a Vulnerability

Please do not put vulnerability details in a public GitHub issue.

The reporting channel is GitHub's private vulnerability advisory form for this
repository:
[GitHub Security Advisories](https://github.com/ilandahan/AID/security/advisories/new).

Status: the owner is enabling GitHub private vulnerability reporting for this
repository. Until that is done (pending with the owner), the form may not accept a
report.

If the form does not let you submit a private report, open a minimal public issue
that only asks for a private contact channel. Do not include any details of the
vulnerability in that issue; the maintainer will reply with a private channel.

Repository security settings (Dependabot alerts and Dependabot security updates) are
also pending with the owner; `.github/dependabot.yml` only configures version updates.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce, or a proof of concept
- Affected versions, if known

You can expect an acknowledgement within 7 days. We will investigate, coordinate
a fix, and credit reporters in the release notes unless you prefer to remain
anonymous.
