# User Acceptance Test Cases

Complete the Actual Result and Status columns before publishing.

| Test ID | Requirement | Test | Expected result | Actual result | Status |
|---|---|---|---|---|---|
| TC-001 | BR-001 | Open the app | Synthetic data loads without an error | App opened and data loaded without errors | Passed |
| TC-002 | BR-002 | Compare one event's timestamps with calculated durations | All duration values are correct | F101 Crew A pump E-01 all event calculations were correct | Passed |
| TC-003 | BR-003 | Review the repeat-fault view | Pairs meeting the threshold are displayed | Correct for all shops displayed | Passed |
| TC-004 | BR-004 | Review the dashboard | All 4 headline KPIs are visible | All KPIs (recurring fault pairs, median recovery time, open problems, overdue problems) shown | Passed |
| TC-005 | BR-005 | Filter by one equipment asset | Only matching events remain | Filtered for PRESS-F-01  | Passed |
| TC-006 | BR-006 | Download the filtered CSV | The file downloads and matches the filtered view | Downloaded a filtered CSV containing 33 entries and matched view | Passed |
| TC-007 | BR-007 | Change owner, priority, and due date | New values appear after save | Tested on F415 displayed as expected | Passed |
| TC-008 | BR-008 | Enter problem-solving details  | Entered text appears after save | Modified problem solving entries for F415 | Passed |
| TC-009 | BR-009 | Advance one problem to its next status | The status updates successfully | Advanced F101 to the next status | Passed |
| TC-010 | BR-010 | Try to close without effectiveness evidence | Closure is blocked with an error | Tried to close F522 without effective evidence and was blocked | Passed |
| TC-011 | BR-011 | Select one problem | Matching fault events are displayed | Selected VISION-C-01 F130 matching faults displayed | Passed |
| TC-012 | BR-012 | Review the app and repository | Synthetic-data disclosure is visible | Confirmed synthetic data visibility on repository | Passed |
