# AID Complete Test Report

Test ID: {{test_id}}
Duration: {{duration_minutes}} minutes
Date: {{date}}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {{total_tests}} |
| Passed | {{passed_count}} |
| Failed (Expected) | {{failed_count}} |
| Pass Rate | {{pass_rate}}% |
| QA Validations | {{qa_validations}} |

**Overall Status: {{overall_status}}**

---

## Phase Results

| Phase | Good | Failed | Gate | Notes |
|-------|------|--------|------|-------|
| 0 Discovery | {{p0_good}} | {{p0_failed}} | {{p0_gate}} | {{p0_notes}} |
| 1 PRD | {{p1_good}} | {{p1_failed}} | {{p1_gate}} | {{p1_notes}} |
| 2 Tech Spec | {{p2_good}} | {{p2_failed}} | {{p2_gate}} | {{p2_notes}} |
| 3a Consolidation | {{p3a_good}} | {{p3a_failed}} | {{p3a_gate}} | {{p3a_notes}} |
| 3b Breakdown | {{p3b_good}} | {{p3b_failed}} | {{p3b_gate}} | {{p3b_notes}} |
| 3c JSON Export | {{p3c_good}} | {{p3c_failed}} | {{p3c_gate}} | {{p3c_notes}} |
| 4 Development | {{p4_good}} | {{p4_failed}} | {{p4_gate}} | {{p4_notes}} |

---

## Quality Check Violation Detection

| Test Case | Expected Score | Actual Score | Detected? |
|-----------|----------------|--------------|-----------|
| Solution in research (P0) | < 7 | {{test_solution_score}} | {{test_solution_result}} |
| Missing WHY (P1) | < 7 | {{test_why_score}} | {{test_why_result}} |
| Code in PRD (P1) | < 7 | {{test_code_prd_score}} | {{test_code_prd_result}} |
| Premature code (P2) | < 7 | {{test_premature_score}} | {{test_premature_result}} |
| Security gap (P2) | < 7 | {{test_security_gap_score}} | {{test_security_gap_result}} |
| Unresolved contradiction (P3a) | < 7 | {{test_unresolved_score}} | {{test_unresolved_result}} |
| Tasks too large (P3b) | < 7 | {{test_large_tasks_score}} | {{test_large_tasks_result}} |
| Incomplete JSON (P3c) | < 7 | {{test_incomplete_json_score}} | {{test_incomplete_json_result}} |
| No WHY header (P4) | < 7 | {{test_no_why_code_score}} | {{test_no_why_code_result}} |
| XSS vulnerability (P4) | < 7 | {{test_xss_score}} | {{test_xss_result}} |

**Detection Rate: {{detection_rate}}%** ({{detected_count}}/{{total_violations}})

---

## Phase 4 QA Validation Results

### QA Task: {{qa_task_id}}

| Criteria Type | Checks | Passed | Failed |
|---------------|--------|--------|--------|
| Must Achieve | {{must_achieve_total}} | {{must_achieve_pass}} | {{must_achieve_fail}} |
| Must Not | {{must_not_total}} | {{must_not_pass}} | {{must_not_fail}} |
| Not Included | {{not_included_total}} | N/A | N/A |
| Best Practices | {{best_practices_total}} | {{best_practices_pass}} | {{best_practices_fail}} |

### QA Pass Test
- **Code reviewed**: `email-validator.ts`, `email-validator.test.ts`
- **Expected verdict**: PASS
- **Actual verdict**: {{qa_pass_verdict}}
- **Result**: {{qa_pass_result}}

### QA Fail Test
- **Code reviewed**: `email-validator-failing.ts`
- **Expected verdict**: FAIL
- **Actual verdict**: {{qa_fail_verdict}}
- **Violations detected**:
{{qa_fail_violations}}
- **Result**: {{qa_fail_result}}

### QA Detection Summary
| Test | Expected | Actual | Detected? |
|------|----------|--------|-----------|
| Good code passes | PASS | {{qa_good_actual}} | {{qa_good_detected}} |
| Bad code fails | FAIL | {{qa_bad_actual}} | {{qa_bad_detected}} |

**QA Catch Rate: {{qa_catch_rate}}%**

---

## Ultrathink Verification Summary

| Metric | Value |
|--------|-------|
| Steps verified | {{ultrathink_steps}} |
| Deep reasoning applied | {{ultrathink_applied}}/{{ultrathink_steps}} |
| Edge cases caught | {{edge_cases_caught}} |
| Quality improvements | {{quality_improvements}} |

---

## Files Generated

### Phase 0 (Discovery)
{{phase_0_files}}

### Phase 1 (PRD)
{{phase_1_files}}

### Phase 2 (Tech Spec)
{{phase_2_files}}

### Phase 3 (Implementation Plan)
{{phase_3_files}}

### Phase 4 (Development)
{{phase_4_files}}

### QA Validation
{{qa_files}}

---

## Issues Found

{{issues}}

---

## Recommendations

{{recommendations}}

---

## Test Artifacts

- **Report**: `.aid/test-outputs/test-{{test_id}}/COMPLETE-TEST-REPORT.md`
- **Thinking Log**: `.aid/test-outputs/test-{{test_id}}/thinking-log.md`
- **Session Data**: `.aid/test-outputs/test-{{test_id}}/session.json`
- **QA Reviews**: `.aid/test-outputs/test-{{test_id}}/qa/`
