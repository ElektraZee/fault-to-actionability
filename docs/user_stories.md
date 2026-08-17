# User Stories and Acceptance Criteria

## US-001: Detect repeat faults
As a production team leader, I need recurring equipment faults identified so that I can prioritize permanent countermeasures instead of repeatedly restoring the same condition.

**Acceptance criteria**
- Given at least three events with the same equipment and fault code in the seven-day demo window, the pair appears in the repeat-fault view.
- The view shows event count and median recovery time.

## US-002: Assign accountability
As a continuous improvement engineer, I need to assign an owner, priority, and due date so that actions have clear accountability.

**Acceptance criteria**
- The selected problem can be updated with all three values.
- The updated values appear after the app reruns.

## US-003: Track problem-solving progress
As a problem owner, I need to document containment, root cause, countermeasure, and effectiveness evidence so that the problem-solving record is clear.

**Acceptance criteria**
- Each field can be entered and saved for the current session.
- A problem cannot be closed when effectiveness evidence is blank.

## US-004: Monitor overdue work
As an area manager, I need to see overdue open problems so that I can escalate stalled work.

**Acceptance criteria**
- The dashboard counts open problems whose due date is earlier than the demo reference date.

## US-005: Trace problems to events
As a manufacturing systems analyst, I need to view the events linked to a problem so that I can validate the pattern behind the action.

**Acceptance criteria**
- Selecting a problem displays matching equipment/fault-code events.
