# AID Test Report

Test ID: {{test_id}}
Started: {{started_at}}
Completed: {{completed_at}}
Duration: {{duration_minutes}} minutes

## Test Configuration

Project: {{project_name}}
Phases Tested: {{phases_tested}}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {{total_tests}} |
| Passed | {{passed_count}} |
| Failed | {{failed_count}} |
| Pass Rate | {{pass_rate}}% |

Overall Status: {{overall_status}}

## Phase Results

### Phase 0: Discovery

| Output | Score | Status | Notes |
|--------|-------|--------|-------|
| research-summary.md | {{p0_research_score}} | {{p0_research_status}} | {{p0_research_notes}} |
| stakeholder-analysis.md | {{p0_stakeholder_score}} | {{p0_stakeholder_status}} | {{p0_stakeholder_notes}} |
| competitive-analysis.md | {{p0_competitive_score}} | {{p0_competitive_status}} | {{p0_competitive_notes}} |

Gate Check: {{p0_gate_status}}

### Phase 1: PRD

| Output | Score | Status | Notes |
|--------|-------|--------|-------|
| user-stories.md | {{p1_stories_score}} | {{p1_stories_status}} | {{p1_stories_notes}} |
| requirements.md | {{p1_requirements_score}} | {{p1_requirements_status}} | {{p1_requirements_notes}} |
| scope.md | {{p1_scope_score}} | {{p1_scope_status}} | {{p1_scope_notes}} |

Gate Check: {{p1_gate_status}}

### Phase 2: Tech Spec

| Output | Score | Status | Notes |
|--------|-------|--------|-------|
| architecture-overview.md | {{p2_arch_score}} | {{p2_arch_status}} | {{p2_arch_notes}} |
| data-model.md | {{p2_data_score}} | {{p2_data_status}} | {{p2_data_notes}} |
| api-design.md | {{p2_api_score}} | {{p2_api_status}} | {{p2_api_notes}} |

Gate Check: {{p2_gate_status}}

## Reflection Validation

### Deliberate Failure Detection

| Test Case | Violation Type | Expected | Actual | Result |
|-----------|---------------|----------|--------|--------|
| Solution in research | Phase Compliance | < 7 | {{test_solution_score}} | {{test_solution_result}} |
| Missing WHY in story | WHY Alignment | < 7 | {{test_why_score}} | {{test_why_result}} |
| Code in PRD | Phase Compliance | < 7 | {{test_code_prd_score}} | {{test_code_prd_result}} |
| Implementation code | Phase Compliance | < 7 | {{test_impl_score}} | {{test_impl_result}} |
| No security section | Security | < 7 | {{test_security_score}} | {{test_security_result}} |

Detection Rate: {{detection_rate}}%

### Score Distribution

| Category | Count | Avg Score |
|----------|-------|-----------|
| Excellent (8+) | {{excellent_count}} | {{excellent_avg}} |
| Good (7-7.9) | {{good_count}} | {{good_avg}} |
| Failed (<7) | {{failed_count}} | {{failed_avg}} |

## Test Assertions

| Assertion | Status |
|-----------|--------|
| Reflection catches violations | {{violations_status}} |
| Good content passes | {{good_status}} |
| Gates enforce rules | {{gates_status}} |
| Scores differentiate quality | {{diff_status}} |

## Issues Found

{{issues}}

## Recommendations

{{recommendations}}
