# Competitive Analysis Framework

Complete guide for conducting thorough competitive analysis during research phase.

## Analysis Scope

### Types of Competitors

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPETITOR LANDSCAPE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐                                           │
│  │     DIRECT      │  Same problem, similar solution           │
│  │   COMPETITORS   │  Example: Uber vs Lyft                    │
│  └────────┬────────┘                                           │
│           │                                                     │
│  ┌────────▼────────┐                                           │
│  │    INDIRECT     │  Same problem, different solution         │
│  │   COMPETITORS   │  Example: Uber vs Public Transit          │
│  └────────┬────────┘                                           │
│           │                                                     │
│  ┌────────▼────────┐                                           │
│  │   SUBSTITUTE    │  Different problem, competes for          │
│  │    PRODUCTS     │  same budget/time/attention               │
│  └────────┬────────┘  Example: Uber vs Car Ownership           │
│           │                                                     │
│  ┌────────▼────────┐                                           │
│  │     NON-        │  People with the problem who              │
│  │  CONSUMPTION    │  do nothing / use workarounds             │
│  └─────────────────┘  Example: People who don't travel         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Competitor Discovery

### Finding Competitors

**Search Strategies:**
```
1. Google Search
   - "[Problem] software"
   - "[Solution type] tools"
   - "Best [category] apps"
   - "[Competitor name] alternatives"
   - "[Industry] software comparison"

2. Review Sites
   - G2 Crowd
   - Capterra
   - TrustRadius
   - Product Hunt
   - Gartner/Forrester reports

3. Social Listening
   - Reddit: r/[industry]
   - Twitter/X searches
   - LinkedIn discussions
   - Quora questions

4. Customer Research
   - "What else have you tried?"
   - "What alternatives did you consider?"
   - "What do your peers use?"

5. Industry Sources
   - Industry analyst reports
   - Trade publications
   - Conference exhibitor lists
   - Investor portfolios
```

### Competitor Tracking Template

```markdown
## Competitor: [Name]
**Traceability ID**: [PROJECT]-A-COMP-XXX
**Type**: Direct / Indirect / Substitute
**Website**: [URL]
**Founded**: [Year]
**Funding**: [Amount / Stage]
**Estimated Size**: [Employees / Revenue]

### Quick Profile
- **One-liner**: What they do in one sentence
- **Target Market**: Who they serve
- **Core Value Prop**: Why customers choose them
```

---

## Analysis Frameworks

### Feature Comparison Matrix

```markdown
## Feature Comparison: [Category]

| Feature | Us | Competitor A | Competitor B | Competitor C |
|---------|-------|--------------|--------------|--------------|
| **Core Features** |
| Feature 1 | | | | |
| Feature 2 | | | | |
| Feature 3 | | | | |
| **Differentiators** |
| Feature 4 | | | | |
| Feature 5 | | | | |
| **Table Stakes** |
| Feature 6 | | | | |
| Feature 7 | | | | |

Legend: ✓ = Has | ○ = Partial | ✗ = Missing | ★ = Best-in-class
```

### Pricing Analysis

```markdown
## Pricing Comparison

| Tier | Us | Competitor A | Competitor B | Competitor C |
|------|-------|--------------|--------------|--------------|
| Free | | | | |
| Basic | | | | |
| Pro | | | | |
| Enterprise | | | | |

### Pricing Model Notes
| Competitor | Model | Key Constraints | Hidden Costs |
|------------|-------|-----------------|--------------|
| A | Per seat | Min 5 seats | Onboarding fee |
| B | Usage-based | API calls | Overage charges |
| C | Flat rate | Storage limits | Add-ons |
```

### Positioning Map

```markdown
## Positioning Map: [Dimension 1] vs [Dimension 2]

Example dimensions:
- Price vs Features
- Ease of Use vs Power
- SMB vs Enterprise
- Self-serve vs High-touch
- Breadth vs Depth

                     HIGH [Dimension 2]
                           │
                           │    ┌───┐
                           │    │ B │
              ┌───┐        │    └───┘
              │ A │        │
              └───┘        │         ┌───┐
                           │         │ C │
    LOW [Dim 1] ───────────┼─────────────────── HIGH [Dim 1]
                           │         └───┘
                           │
                     ┌───┐ │
                     │ D │ │
                     └───┘ │
                           │
                     LOW [Dimension 2]

### White Space Opportunities
[Areas of the map with no competitors]
```

---

## Deep Dive Analysis

### Per-Competitor Analysis Template

```markdown
# Competitor Deep Dive: [Name]

**Traceability ID Range**: [PROJECT]-A-COMP-XXX to YYY

## Company Overview
- **Founded**:
- **Headquarters**:
- **Employees**:
- **Funding**:
- **Key investors**:

## Product Analysis

### Core Product
- **Main offering**:
- **Technology stack** (if known):
- **Platforms**: Web / Mobile / Desktop / API

### Key Features
| Feature | Description | Strength (1-5) |
|---------|-------------|----------------|
| | | |

### UX/Design
- **First impression**:
- **Onboarding**:
- **Learning curve**:
- **Design quality**:

### Integration Ecosystem
- Native integrations:
- API availability:
- Partner ecosystem:

## Go-to-Market

### Target Customer
- **Primary segment**:
- **Company size**:
- **Industry focus**:
- **User persona**:

### Positioning
- **Tagline**:
- **Key message**:
- **Differentiation claim**:

### Pricing
- **Model**:
- **Entry price**:
- **Enterprise price**:
- **Free tier**: Yes / No

### Distribution
- **Sales model**: Self-serve / Sales-led / PLG / Hybrid
- **Marketing channels**:
- **Content strategy**:

## Strengths & Weaknesses

### Strengths
1.
2.
3.

### Weaknesses
1.
2.
3.

### Opportunities Against Them
1.
2.

### Threats They Pose
1.
2.

## Customer Sentiment

### Review Summary
| Source | Rating | # Reviews | Key Themes |
|--------|--------|-----------|------------|
| G2 | | | |
| Capterra | | | |
| App Store | | | |

### Common Praise
-

### Common Complaints
-

### Notable Quotes
> "[Quote from customer review]"

## Recent Activity

### Product Updates (Last 6 months)
-

### Company News
-

### Hiring Trends
[What roles are they hiring? Indicates focus areas]

## Strategic Assessment

### Their Trajectory
Where are they headed?

### Likely Next Moves
What will they do next?

### Our Counter-Strategy
How should we respond?
```

---

## Competitive Intelligence Sources

### Public Sources
| Source | What You'll Find | How to Access |
|--------|------------------|---------------|
| Crunchbase | Funding, employees, news | crunchbase.com |
| LinkedIn | Employee count, hiring | linkedin.com |
| G2/Capterra | Reviews, ratings, features | g2.com, capterra.com |
| SimilarWeb | Traffic, sources | similarweb.com |
| BuiltWith | Technology stack | builtwith.com |
| Archive.org | Historical website changes | web.archive.org |
| SEC filings | Financial data (public co.) | sec.gov |
| Patent databases | Innovation direction | patents.google.com |
| Job postings | Strategic priorities | Indeed, LinkedIn |
| Press releases | Announcements | Company newsroom |

### Social Listening
| Platform | What to Monitor |
|----------|-----------------|
| Twitter/X | Company account, mentions, hashtags |
| Reddit | Industry subreddits, product mentions |
| LinkedIn | Company page, employee posts |
| YouTube | Product demos, reviews |
| Product Hunt | Launches, community feedback |
| Hacker News | Tech community sentiment |

### Customer Intelligence
| Method | Insight Type |
|--------|--------------|
| Win/Loss interviews | Why customers chose/rejected |
| Support forums | Pain points, feature requests |
| Community channels | User sentiment, workarounds |
| Review mining | Strengths, weaknesses, trends |

---

## Analysis Outputs

### Competitive Summary Template

```markdown
# Competitive Landscape Summary

**Research Period**: [Dates]
**Traceability**: [PROJECT]-A-COMP-001 to XXX

## Market Overview
[2-3 paragraphs on the competitive landscape]

## Competitor Tiers

### Tier 1: Primary Competitors
Direct threats, similar positioning

| Competitor | Strength | Weakness | Threat Level |
|------------|----------|----------|--------------|
| | | | High/Med/Low |

### Tier 2: Secondary Competitors
Indirect competition, different approach

| Competitor | How They Compete | When They Win |
|------------|------------------|---------------|
| | | |

### Tier 3: Emerging Threats
New entrants, potential disruptors

| Competitor | What to Watch | Timeline |
|------------|---------------|----------|
| | | |

## Key Insights

### Market Gaps
1. [PROJECT]-A-COMP-XXX: [Gap description]
2. [PROJECT]-A-COMP-XXX: [Gap description]

### Overserved Needs
[Where competitors over-deliver]

### Underserved Needs
[Where competitors under-deliver]

### Industry Trends
1.
2.
3.

## Positioning Opportunities

### White Space
[Where no competitor plays]

### Differentiation Angles
1.
2.
3.

### Risks to Avoid
1.
2.

## Recommendations

### Must-Have Features
[To be competitive]

### Differentiation Features
[To stand out]

### Positioning Strategy
[How to position against landscape]
```

---

## Competitive Monitoring

### Ongoing Tracking System

```markdown
## Competitor Watch List

| Competitor | Monitor | Frequency | Owner |
|------------|---------|-----------|-------|
| [Name] | Website, pricing, features | Monthly | |
| [Name] | Product updates, blog | Weekly | |
| [Name] | Funding, news | Quarterly | |

### Alert Setup
- Google Alerts: "[Competitor name]", "[Product name]"
- Social monitoring: Brand mentions
- Review site notifications
- Job posting tracking

### Monthly Check-in
- [ ] Review competitor websites for changes
- [ ] Check for new features/products
- [ ] Monitor pricing changes
- [ ] Review recent customer feedback
- [ ] Update competitive matrix
```

---

## Competitive Battlecards

### Quick Reference Card Template

```markdown
## Battlecard: [Competitor Name]

### In 30 Seconds
**They say**: "[Their positioning]"
**Reality**: [What's actually true]
**Our advantage**: [Why we're better]

### When They Come Up

**Situation**: Customer mentions [Competitor]

**Response**:
"[Competitor] is great for [their strength]. Where we differ is
[our differentiation]. For customers who need [our strength],
we're typically a better fit because [reason]."

### Feature Comparison (Key Items)
| Feature | Them | Us | Talking Point |
|---------|------|----|----|
| | | | |

### Objection Handling

**"They're cheaper"**
> [Response]

**"They have [feature] we don't"**
> [Response]

**"They're the market leader"**
> [Response]

### When We Win Against Them
- [Scenario 1]
- [Scenario 2]

### When We Lose Against Them
- [Scenario 1]
- [Scenario 2]

### Proof Points
- Customer: [Name] switched from [Competitor] because [reason]
- Metric: [Comparison data]
```
