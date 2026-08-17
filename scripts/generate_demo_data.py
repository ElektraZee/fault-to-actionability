
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

RNG = np.random.default_rng(42)
DEMO_END = pd.Timestamp("2026-08-16 18:00:00")

#fictional equipment
EQUIPMENT = [
    {"equipment": "CELL-A-01", "area": "Assembly"},
    {"equipment": "CELL-A-02", "area": "Assembly"},
    {"equipment": "CONVEYOR-B-01", "area": "Material Handling"},
    {"equipment": "VISION-C-01", "area": "Inspection"},
    {"equipment": "PACK-D-01", "area": "Packaging"},
    {"equipment": "PUMP-E-01", "area": "Utilities"},
    {"equipment": "PRESS-F-01", "area": "Forming"},
    {"equipment": "ROBOT-G-01", "area": "Automation"},
]

#fictional fault codes
FAULTS = [
    {"fault_code": "F101", "fault_description": "Guard circuit open"},
    {"fault_code": "F204", "fault_description": "Part not detected"},
    {"fault_code": "F310", "fault_description": "Cycle-time timeout"},
    {"fault_code": "F415", "fault_description": "Communication interruption"},
    {"fault_code": "F522", "fault_description": "Material-present sensor blocked"},
    {"fault_code": "F630", "fault_description": "Drive overload"},
]

#operation crew
CREWS = ["A", "B", "C", "D"]
SEVERITIES = ["Low", "Medium", "High"]
STATUS_ORDER = [
    "New",
    "Assigned",
    "Contained",
    "Root Cause Confirmed",
    "Countermeasure Implemented",
    "Effectiveness Confirmed",
    "Closed",
]
OWNERS = ["", "A. Rivera", "J. Chen", "M. Patel", "S. Johnson"]

# These combinations occur more frequently so the demo always has repeat faults.
RECURRING_PAIRS = [
    ("CELL-A-01", "F101"),
    ("CELL-A-02", "F310"),
    ("CONVEYOR-B-01", "F204"),
    ("VISION-C-01", "F415"),
]


def build_fault_events(event_count: int = 650) -> pd.DataFrame:
    equipment_to_area = {item["equipment"]: item["area"] for item in EQUIPMENT}
    fault_to_description = {
        item["fault_code"]: item["fault_description"] for item in FAULTS
    }

    rows = []

    for event_id in range(1, event_count + 1):
        if RNG.random() < 0.48:
            equipment, fault_code = RECURRING_PAIRS[
                int(RNG.integers(0, len(RECURRING_PAIRS)))
            ]
        else:
            equipment = EQUIPMENT[int(RNG.integers(0, len(EQUIPMENT)))]["equipment"]
            fault_code = FAULTS[int(RNG.integers(0, len(FAULTS)))]["fault_code"]

        minutes_ago = int(RNG.integers(0, 30 * 24 * 60))
        fault_start = DEMO_END - pd.Timedelta(minutes=minutes_ago)
        fault_duration = int(RNG.integers(1, 19))
        restart_delay = int(RNG.integers(1, 13))
        fault_cleared = fault_start + pd.Timedelta(minutes=fault_duration)
        equipment_restarted = fault_cleared + pd.Timedelta(minutes=restart_delay)

        rows.append(
            {
                "event_id": f"E-{event_id:04d}",
                "equipment": equipment,
                "area": equipment_to_area[equipment],
                "crew": CREWS[int(RNG.integers(0, len(CREWS)))],
                "fault_code": fault_code,
                "fault_description": fault_to_description[fault_code],
                "severity": RNG.choice(SEVERITIES, p=[0.35, 0.45, 0.20]),
                "fault_start": fault_start,
                "fault_cleared": fault_cleared,
                "equipment_restarted": equipment_restarted,
            }
        )

    events = pd.DataFrame(rows).sort_values("fault_start").reset_index(drop=True)
    return events


def build_problem_records(events: pd.DataFrame) -> pd.DataFrame:
    demo_today = events["fault_start"].max().normalize()
    cutoff = demo_today - pd.Timedelta(days=7)

    recent = events[events["fault_start"] >= cutoff]
    grouped = (
        recent.groupby(["equipment", "fault_code", "fault_description"])
        .size()
        .reset_index(name="events_last_7_days")
    )
    grouped = grouped[grouped["events_last_7_days"] >= 3].copy()
    grouped = grouped.sort_values(
        "events_last_7_days", ascending=False
    ).reset_index(drop=True)

    rows = []
    for index, row in grouped.iterrows():
        status = STATUS_ORDER[index % len(STATUS_ORDER)]
        owner = OWNERS[index % len(OWNERS)]

        first_event = recent[
            (recent["equipment"] == row["equipment"])
            & (recent["fault_code"] == row["fault_code"])
        ]["fault_start"].min()

        # Alternate due dates so the dashboard includes both current and overdue work.
        due_date = demo_today + pd.Timedelta(days=(index % 5) - 2)

        containment = (
            "Verified safe condition and restored production using standard recovery."
            if STATUS_ORDER.index(status) >= STATUS_ORDER.index("Contained")
            else ""
        )
        root_cause = (
            "Demo root-cause statement based on synthetic event review."
            if STATUS_ORDER.index(status)
            >= STATUS_ORDER.index("Root Cause Confirmed")
            else ""
        )
        countermeasure = (
            "Demo permanent countermeasure documented for portfolio purposes."
            if STATUS_ORDER.index(status)
            >= STATUS_ORDER.index("Countermeasure Implemented")
            else ""
        )
        effectiveness = (
            "No recurrence observed during the synthetic monitoring window."
            if STATUS_ORDER.index(status)
            >= STATUS_ORDER.index("Effectiveness Confirmed")
            else ""
        )

        rows.append(
            {
                "problem_id": f"P-{index + 1:03d}",
                "equipment": row["equipment"],
                "fault_code": row["fault_code"],
                "title": (
                    f"Recurring {row['fault_code']} on {row['equipment']}: "
                    f"{row['fault_description']}"
                ),
                "events_last_7_days": int(row["events_last_7_days"]),
                "priority": (
                    "High" if row["events_last_7_days"] >= 8 else "Medium"
                ),
                "status": status,
                "owner": owner,
                "opened_date": first_event.normalize(),
                "due_date": due_date,
                "containment": containment,
                "root_cause": root_cause,
                "countermeasure": countermeasure,
                "effectiveness_evidence": effectiveness,
            }
        )

    return pd.DataFrame(rows)


#build events and save output
def main() -> None:
    events = build_fault_events()
    problems = build_problem_records(events)

    events.to_csv(DATA_DIR / "fault_events.csv", index=False)
    problems.to_csv(DATA_DIR / "problem_records.csv", index=False)

    print(f"Created {len(events)} synthetic fault events.")
    print(f"Created {len(problems)} synthetic problem records.")
    print(f"Files saved in: {DATA_DIR}")


if __name__ == "__main__":
    main()
