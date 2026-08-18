# Bad Evaluation Example (Anti-Patterns)

Same context as good example - shows what NOT to do.

## Problems

| Issue | Bad | Good |
|-------|-----|------|
| Inflated scores | Security 8/10 | Security 6/10 |
| Vague notes | "Secure enough" | "SECRET_KEY hardcoded - security risk" |
| Missing issues | vulnerabilities: [] | Lists specific vulnerabilities |
| Unhelpful guidance | "Maybe improve later" | "Move SECRET_KEY to env var using os.getenv()" |
| Empty do_not_change | [] | Lists patterns to preserve |

## Red Flags

**Scoring**: All 9-10, no scores below 7, perfect 10 on any criterion
**Notes**: Single-word ("Good", "Fine"), "N/A" for would_improve
**Guidance**: Empty required_changes when score < 7, vague suggestions

## Right Mindset

- "What could go wrong with this code?"
- "What would a security auditor find?"
- "What's missing that should be there?"

NOT: "This is probably fine" or "I don't want to be too harsh"
