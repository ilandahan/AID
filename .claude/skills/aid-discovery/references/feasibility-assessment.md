# Feasibility Assessment Guide

## Assessment Dimensions

### 1. Technical Feasibility
| Question | Assessment |
|----------|------------|
| Can we build it? | Yes / Maybe / No |
| Do we have the skills? | Available / Need to hire / Training required |
| Infrastructure ready? | Exists / Needs setup / Major investment |
| Integration complexity? | Simple / Moderate / Complex |

### 2. Operational Feasibility
| Question | Assessment |
|----------|------------|
| Can users adopt it? | Easy / Training needed / Major change |
| Process changes required? | None / Minor / Significant |
| Support capacity? | Ready / Needs scaling / Major gap |
| Compliance requirements? | Met / Achievable / Blocker |

### 3. Economic Feasibility
| Question | Assessment |
|----------|------------|
| ROI positive? | < 6 months / 6-12 months / > 12 months |
| Budget available? | Yes / Partial / No |
| Ongoing costs acceptable? | Yes / Needs review / No |

### 4. Schedule Feasibility
| Question | Assessment |
|----------|------------|
| Can meet deadline? | Comfortable / Tight / Impossible |
| Dependencies manageable? | None / Some / Many blockers |
| Resource availability? | Ready / Partial / Constrained |

## Risk Assessment Matrix

```
           High Impact
                │
   MITIGATE     │    AVOID/
   (Plan B)     │    ESCALATE
                │
────────────────┼────────────────
                │
   ACCEPT       │    MONITOR
   (Low effort) │    (Watch)
                │
           Low Impact

High Likelihood ←────────→ Low Likelihood
```

## Go/No-Go Decision Framework

### Green Light (Proceed)
- [ ] Problem clearly defined and validated
- [ ] Stakeholders identified and available
- [ ] Technical approach feasible
- [ ] Resources available or obtainable
- [ ] Timeline realistic
- [ ] ROI positive

### Yellow Light (Proceed with Conditions)
- [ ] Some risks identified but mitigatable
- [ ] Partial resource availability
- [ ] Dependencies need management
- [ ] Scope may need adjustment

### Red Light (Stop/Pivot)
- [ ] Problem not validated
- [ ] Critical stakeholders unavailable
- [ ] Technical blockers without solutions
- [ ] Resources not available
- [ ] Timeline impossible
- [ ] ROI negative or unclear

## Spike/POC Criteria

### When to Spike
- New technology unknown to team
- Integration with unfamiliar system
- Performance concerns unverified
- Architecture decision unclear

### Spike Structure
```markdown
## Spike: [Question to Answer]

### Hypothesis
We believe [assumption]

### Experiment
We will [approach]

### Success Criteria
We'll know we're right if [measurable outcome]

### Timebox
[X] hours/days maximum

### Findings
[Document results]

### Recommendation
[Go / No-Go / Modified approach]
```

## Output: Feasibility Summary

```markdown
# Feasibility Assessment: [Project Name]

## Summary
| Dimension | Rating | Notes |
|-----------|--------|-------|
| Technical | Green/Yellow/Red | [Brief] |
| Operational | Green/Yellow/Red | [Brief] |
| Economic | Green/Yellow/Red | [Brief] |
| Schedule | Green/Yellow/Red | [Brief] |

## Key Risks
1. [Risk]: [Mitigation]
2. [Risk]: [Mitigation]

## Dependencies
1. [Dependency]: [Status]

## Recommendation
[ ] Proceed
[ ] Proceed with conditions: [list]
[ ] Do not proceed: [reason]
[ ] Need more information: [what]

## Required Spikes
1. [Spike name]: [Question to answer]
```
