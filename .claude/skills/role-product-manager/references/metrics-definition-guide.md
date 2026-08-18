# Metrics Definition Guide

## Types of Metrics

### Input Metrics (Leading)
What you do that drives outcomes
- Features shipped
- Experiments run
- User research sessions
- Marketing campaigns

### Output Metrics (Lagging)
Results of your actions
- Revenue
- User retention
- Customer satisfaction
- Market share

## Metric Definition Framework

### SMART Metrics
```markdown
**Specific**: What exactly are we measuring?
**Measurable**: How do we calculate it?
**Achievable**: Is the target realistic?
**Relevant**: Does it matter for our goals?
**Time-bound**: When do we measure?
```

### Metric Card Template
```markdown
## Metric: [Name]

### Definition
[Precise definition of what this measures]

### Formula
```
[Metric] = [Numerator] / [Denominator] × 100
```

### Data Source
- System: [where data comes from]
- Table/Event: [specific source]
- Refresh: [frequency]

### Baseline
- Current: [value]
- Date: [when measured]

### Target
- Goal: [value]
- Timeframe: [by when]

### Segments
- By: [user type, region, etc.]

### Owner
- Metric owner: [name]
- Data owner: [name]
```

## Common Product Metrics

### Acquisition
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| Sign-ups | New accounts / period | Growth trend |
| CAC | Marketing spend / New customers | < LTV/3 |
| Conversion Rate | Sign-ups / Visitors | 2-5% B2C |
```

### Activation
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| Activation Rate | Users completing key action / Sign-ups | 40-60% |
| Time to Value | Time to first key action | < 5 min |
| Onboarding Completion | Users completing onboarding / Started | 70%+ |
```

### Engagement
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| DAU/MAU | Daily Active / Monthly Active | 20%+ |
| Session Length | Avg time per session | Depends on product |
| Feature Adoption | Users using feature / All users | 30%+ |
| Stickiness | Days active / 30 days | 50%+ |
```

### Retention
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| D1/D7/D30 Retention | Users returning on Day N / Cohort | D1: 40%, D30: 20% |
| Churn Rate | Users lost / Total users | <5% monthly |
| Net Revenue Retention | (Revenue - Churn + Expansion) / Starting | 100%+ |
```

### Revenue
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| MRR | Monthly Recurring Revenue | Growth trend |
| ARPU | Revenue / Users | Growth trend |
| LTV | ARPU × Avg lifetime | > 3x CAC |
| LTV:CAC | Lifetime Value / Acquisition Cost | 3:1+ |
```

### Satisfaction
```markdown
| Metric | Formula | Good Target |
|--------|---------|-------------|
| NPS | Promoters - Detractors | 30+ |
| CSAT | Satisfied / Respondents | 80%+ |
| CES | Ease of use rating | Low effort |
```

## Metric Anti-Patterns

| Anti-Pattern | Problem | Better Approach |
|--------------|---------|-----------------|
| Vanity metrics | Big numbers, no insight | Actionable metrics |
| Too many metrics | Can't focus | 3-5 key metrics |
| No baseline | Can't measure change | Establish baseline first |
| Measuring activity | Not outcomes | Measure results |
| Gaming metrics | Behavior optimization for metric | Balanced scorecard |

## Dashboard Design

### Key Principles
1. **One key metric** - What matters most?
2. **Supporting metrics** - What explains the key metric?
3. **Segments** - Where to dig deeper?
4. **Trends** - Is it getting better?
5. **Targets** - Are we on track?

### Dashboard Template
```markdown
# [Product] Dashboard

## North Star Metric
[Big number with trend arrow]
Target: [X] by [date]

## Health Metrics (3-5)
| Metric | Current | Target | Trend |
|--------|---------|--------|-------|
| [Metric 1] | [value] | [target] | ↑↓→ |
| [Metric 2] | [value] | [target] | ↑↓→ |

## Segments
[Charts by user type, region, etc.]

## Alerts
- ⚠️ [Metric] below threshold
- ✅ [Metric] hit target
```

## Experimentation Metrics

### Experiment Design
```markdown
## Experiment: [Name]

### Hypothesis
If we [change], then [metric] will [improve by X%]
because [reason].

### Primary Metric
[What we're trying to move]

### Secondary Metrics
[Other things we'll watch]

### Guardrail Metrics
[What must NOT get worse]

### Sample Size
[Required users for significance]

### Duration
[How long to run]
```

### Statistical Significance
```markdown
| Confidence | When to Use |
|------------|-------------|
| 90% | Early exploration |
| 95% | Standard (most cases) |
| 99% | High-stakes decisions |
```
