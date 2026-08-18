# Visual QA Grading Criteria Reference

Source: Adapted from Anthropic's "Harness Design for Long-Running Apps" (March 2026)
by Prithvi Rajasekaran's frontend evaluator criteria.

---

## The Four Criteria

### Design Quality (30% weight)
> Does the work form a coherent whole with unified mood and identity?

**What to look for:**
- Consistent color palette (not more than 3-4 primary colors)
- Visual hierarchy — headings stand out, CTAs are prominent
- Unified mood — dark and professional, or light and friendly, but not mixed
- Intentional whitespace — breathing room, not cramped
- Component consistency — all cards look like siblings, all buttons are family

**Red flags:**
- Mixed design languages (Material buttons + Bootstrap cards)
- Random colors with no palette logic
- No clear visual hierarchy — everything screams for attention equally

### Originality (15% weight)
> Evidence of custom decisions vs generic AI patterns?

**What to look for:**
- Custom color choices (not default blue/gray)
- Unique layout decisions (not standard sidebar + content)
- Branded feel — could you identify this app vs another?
- Micro-interactions or transitions that feel intentional
- Typography choices beyond system defaults

**Red flags:**
- Pure Tailwind defaults (indigo-500, gray-100 everywhere)
- Cookie-cutter layout seen in every AI-generated app
- "It works but looks like every other dashboard"

### Craft (25% weight)
> Typography, spacing, color harmony, alignment, pixel precision?

**What to look for:**
- Consistent spacing (8px grid or similar system)
- Typography scale (clear hierarchy: h1 > h2 > h3 > body)
- Proper line height (1.5 for body text)
- Color contrast (WCAG AA minimum: 4.5:1 for normal text)
- Alignment — everything on a grid, nothing floating randomly
- Border radius consistency (same radius on all similar elements)
- Responsive adaptation (not just hiding things on mobile)

**Tools to verify:**
- Lighthouse audit → accessibility score (includes contrast)
- resize_page → check responsive behavior
- take_snapshot → verify a11y tree for missing labels

### Functionality (30% weight)
> Can users understand what to do and complete tasks?

**What to test:**
- Every visible button: does clicking it do something?
- Every form: does filling and submitting work?
- Navigation: do links go where expected?
- States: loading states, empty states, error states
- Modals/dialogs: do they open AND close?
- Dropdowns: do they expand and select?

**Red flags:**
- Click on button → nothing happens (most common CRITICAL issue)
- Form submits but no success/error feedback
- Navigation leads to blank or 404 pages
- Scrolling doesn't work or page overflows viewport

---

## Anti-Patterns in Visual QA

| Anti-Pattern | Why It's Dangerous |
|---|---|
| Scoring from code only | Code can render differently than expected |
| Not testing mobile | 50%+ of users are mobile |
| Skipping interactive testing | "It looks good" ≠ "it works" |
| Inflating scores for working functionality | Working is the baseline, not a bonus |
| Ignoring accessibility | Legal risk + excludes users |
