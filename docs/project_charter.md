# Fault-to-Actionability Project Charter

## Business problem
Manufacturing operations can have visibility to equipment faults without a consistent process for converting repeat events into owned, verifiable problem closures.

## Hypothesis
A structured workflow that connects fault-event data to repeat-fault detection, ownership, containment, root-cause analysis, countermeasure tracking, and effectiveness confirmation may improve actionability on the production floor.

## Target users
- Production team leaders
- Maintenance team members
- Continuous improvement engineers
- Manufacturing engineers
- Manufacturing systems analysts
- Production Managers

## Within scope
- Synthetic equipment-fault events
- Repeat fault identification
- Fault recovery analysis
- Problem ownership and due dates
- Root cause and countermeasure documentation
- Problem Solving effectiveness confirmation
- KPI reporting

## Out of scope
- Real plant data
- Connection to a real PLC, SCADA, MES, or ERP
- Automated equipment control
- Production deployment

## Core metrics
1. Recurring fault pairs
2. Median total recovery time
3. Restart delay
4. Open-problem count
5. Overdue-problem count
6. Problem status

## Definition of done
- The app runs locally in Streamlit.
- The app loads at least 500 synthetic fault events.
- The app shows repeat faults, recovery time, open problems, and overdue problems.
- A user can update a problem record during the current session.
- The app prevents closure without effectiveness evidence.
- Requirements, user stories, UAT tests, architecture, and data notice are documented.
- The code is pushed to GitHub and deployed to Streamlit Community Cloud.
