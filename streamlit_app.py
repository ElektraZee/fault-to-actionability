#imports, file locations, defining the file path
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

FAULT_FILE = DATA_DIR / "fault_events.csv"
PROBLEM_FILE = DATA_DIR / "problem_records.csv"

#define workflow
STATUS_ORDER = [
    "New",
    "Assigned",
    "Contained",
    "Root Cause Confirmed",
    "Countermeasure Implemented",
    "Effectiveness Confirmed",
    "Closed",
]

NEXT_STATUS = {
    "New": "Assigned",
    "Assigned": "Contained",
    "Contained": "Root Cause Confirmed",
    "Root Cause Confirmed": "Countermeasure Implemented",
    "Countermeasure Implemented": "Effectiveness Confirmed",
    "Effectiveness Confirmed": "Closed",
    "Closed": "Root Cause Confirmed",
}

st.set_page_config(
    page_title="Fault-to-Actionability",
    page_icon="🛠️",
    layout="wide",
)


#Load data and calculations for fault duration, equipment restart delay, and recovery time
@st.cache_data
def load_fault_events() -> pd.DataFrame:
    events = pd.read_csv(
        FAULT_FILE,
        parse_dates=["fault_start", "fault_cleared", "equipment_restarted"],
    )
    events["fault_duration_min"] = (
        events["fault_cleared"] - events["fault_start"]
    ).dt.total_seconds() / 60
    events["restart_delay_min"] = (
        events["equipment_restarted"] - events["fault_cleared"]
    ).dt.total_seconds() / 60
    events["total_recovery_min"] = (
        events["equipment_restarted"] - events["fault_start"]
    ).dt.total_seconds() / 60
    return events


@st.cache_data
def load_problem_records() -> pd.DataFrame:
    return pd.read_csv(
        PROBLEM_FILE,
        parse_dates=["opened_date", "due_date"],
        keep_default_na=False,
    )


def reset_problem_board() -> None:
    st.session_state["problems"] = load_problem_records().copy()


#repeat fault detection
def get_repeat_faults(events: pd.DataFrame, demo_today: pd.Timestamp) -> pd.DataFrame:
    cutoff = demo_today - pd.Timedelta(days=7)
    recent = events[events["fault_start"] >= cutoff]

    repeats = (
        recent.groupby(
            ["equipment", "fault_code", "fault_description"],
            as_index=False,
        )
        .agg(
            event_count=("event_id", "count"),
            median_recovery_min=("total_recovery_min", "median"),
        )
        .sort_values("event_count", ascending=False)
    )

    repeats = repeats[repeats["event_count"] >= 3].copy()
    repeats["fault_pair"] = (
        repeats["equipment"] + " | " + repeats["fault_code"]
    )
    return repeats

#error handling for missing file faults
if not FAULT_FILE.exists() or not PROBLEM_FILE.exists():
    st.error(
        "Demo data files are missing. Open the VS Code terminal and run: "
        "`python scripts/generate_demo_data.py`"
    )
    st.stop()

events = load_fault_events()

#session state rules - no data saved to database
if "problems" not in st.session_state:
    reset_problem_board()

problems = st.session_state["problems"]
demo_today = events["fault_start"].max().normalize()
repeat_faults = get_repeat_faults(events, demo_today)

#App Setup
st.title("Fault-to-Actionability")
st.caption(
    "A synthetic data portfolio prototype that connects manufacturing fault "
    "visibility to ownership, problem solving, countermeasure tracking, and "
    "verified closure."
)

#sidebar setup with reset button and project controls
with st.sidebar:
    st.header("Project controls")
    st.write(
        "All equipment names, fault codes, people, and results in this app are "
        "synthetic."
    )

    st.write(f"**Demo reference date:** {demo_today.date()}")
    if st.button("Reset problem board"):
        reset_problem_board()
        st.success("Problem board reset.")
        st.rerun()

    st.markdown("---")
    st.write("Built By: **Elektra Desmillienne**")
    st.write("Manufacturing Technology and Process Engineering Portfolio")

overview_tab, explorer_tab, board_tab, method_tab = st.tabs(
    ["Overview", "Fault Explorer", "Problem Board", "Method"]
)

with overview_tab:
    open_problems = problems[problems["status"] != "Closed"].copy()
    overdue_count = int(
        (
            (open_problems["due_date"] < demo_today)
            & (open_problems["due_date"].notna())
        ).sum()
    )

    metric_1, metric_2, metric_3, metric_4 = st.columns(4)
    metric_1.metric("Recurring fault pairs", len(repeat_faults))
    metric_2.metric(
        "Median recovery time",
        f"{events['total_recovery_min'].median():.1f} min",
    )
    metric_3.metric("Open problems", len(open_problems))
    metric_4.metric("Overdue problems", overdue_count)

    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Repeatitive Fault Pareto")
        if repeat_faults.empty:
            st.info("No fault pairs meet the repeat threshold.")
        else:
            figure = px.bar(
                repeat_faults.sort_values("event_count"),
                x="event_count",
                y="fault_pair",
                orientation="h",
                labels={
                    "event_count": "Events in the demo's last 7 days",
                    "fault_pair": "Equipment | fault code",
                },
                hover_data=["fault_description", "median_recovery_min"],
            )
            st.plotly_chart(figure, use_container_width=True)

    with right_column:
        st.subheader("Median recovery time by crew")
        crew_summary = (
            events.groupby("crew", as_index=False)["total_recovery_min"]
            .median()
            .sort_values("total_recovery_min", ascending=False)
        )
        figure = px.bar(
            crew_summary,
            x="crew",
            y="total_recovery_min",
            labels={
                "crew": "Crew",
                "total_recovery_min": "Median recovery time (minutes)",
            },
        )
        st.plotly_chart(figure, use_container_width=True)

    st.subheader("Open-problem summary")
    summary_columns = [
        "problem_id",
        "equipment",
        "fault_code",
        "priority",
        "status",
        "owner",
        "due_date",
    ]
    st.dataframe(
        open_problems[summary_columns].sort_values("due_date"),
        use_container_width=True,
        hide_index=True,
    )

with explorer_tab:
    st.subheader("Explore Fault Events")

    filter_1, filter_2, filter_3 = st.columns(3)

    with filter_1:
        selected_equipment = st.multiselect(
            "Equipment",
            sorted(events["equipment"].unique()),
        )

    with filter_2:
        selected_crews = st.multiselect(
            "Crew",
            sorted(events["crew"].unique()),
        )

    with filter_3:
        selected_fault_codes = st.multiselect(
            "Fault code",
            sorted(events["fault_code"].unique()),
        )

    filtered_events = events.copy()

    if selected_equipment:
        filtered_events = filtered_events[
            filtered_events["equipment"].isin(selected_equipment)
        ]

    if selected_crews:
        filtered_events = filtered_events[
            filtered_events["crew"].isin(selected_crews)
        ]

    if selected_fault_codes:
        filtered_events = filtered_events[
            filtered_events["fault_code"].isin(selected_fault_codes)
        ]

    st.write(f"Showing **{len(filtered_events)}** events.")

    explorer_columns = [
        "event_id",
        "fault_start",
        "equipment",
        "area",
        "crew",
        "fault_code",
        "fault_description",
        "severity",
        "fault_duration_min",
        "restart_delay_min",
        "total_recovery_min",
    ]

    st.dataframe(
        filtered_events[explorer_columns].sort_values(
            "fault_start", ascending=False
        ),
        use_container_width=True,
        hide_index=True,
    )

    csv_data = filtered_events[explorer_columns].to_csv(index=False).encode(
        "utf-8"
    )
    st.download_button(
        "Download filtered events as CSV",
        data=csv_data,
        file_name="filtered_fault_events.csv",
        mime="text/csv",
    )

with board_tab:
    st.subheader("Problem Action Board")
    st.write(
        "Updates are stored only for your current browser session. They reset "
        "when you press the reset button or when the hosted app restarts."
    )

    if problems.empty:
        st.info("No problem records are available.")
    else:
        problem_options = {
            row["problem_id"]: (
                f"{row['problem_id']} | {row['equipment']} | "
                f"{row['fault_code']} | {row['status']}"
            )
            for _, row in problems.iterrows()
        }

        selected_problem_id = st.selectbox(
            "Select a problem",
            options=list(problem_options.keys()),
            format_func=lambda problem_id: problem_options[problem_id],
        )

        selected_index = problems.index[
            problems["problem_id"] == selected_problem_id
        ][0]
        selected_problem = problems.loc[selected_index]

        detail_1, detail_2, detail_3, detail_4 = st.columns(4)
        detail_1.metric("Status", selected_problem["status"])
        detail_2.metric("Priority", selected_problem["priority"])
        detail_3.metric(
            "Owner",
            selected_problem["owner"] or "Unassigned",
        )
        detail_4.metric(
            "Events in last 7 days",
            int(selected_problem["events_last_7_days"]),
        )

        st.write(f"**Problem:** {selected_problem['title']}")

        current_status = selected_problem["status"]
        next_status = NEXT_STATUS[current_status]
        status_options = [current_status]
        if next_status not in status_options:
            status_options.append(next_status)

        with st.form("problem_update_form"):
            form_1, form_2, form_3 = st.columns(3)

            with form_1:
                owner = st.text_input(
                    "Owner",
                    value=selected_problem["owner"],
                )

            with form_2:
                priorities = ["Low", "Medium", "High", "Critical"]
                priority = st.selectbox(
                    "Priority",
                    priorities,
                    index=priorities.index(selected_problem["priority"]),
                )

            with form_3:
                due_date = st.date_input(
                    "Due date",
                    value=selected_problem["due_date"].date(),
                )

            proposed_status = st.selectbox(
                "Status",
                status_options,
                index=0,
                help=(
                    "This starter version allows the current status or the "
                    "next approved workflow status."
                ),
            )

            containment = st.text_area(
                "Immediate containment",
                value=selected_problem["containment"],
            )
            root_cause = st.text_area(
                "Confirmed root cause",
                value=selected_problem["root_cause"],
            )
            countermeasure = st.text_area(
                "Permanent countermeasure",
                value=selected_problem["countermeasure"],
            )
            effectiveness = st.text_area(
                "Effectiveness evidence",
                value=selected_problem["effectiveness_evidence"],
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            if proposed_status == "Closed" and not effectiveness.strip():
                st.error(
                    "A problem cannot be closed without effectiveness evidence."
                )
            else:
                problems.loc[selected_index, "owner"] = owner.strip()
                problems.loc[selected_index, "priority"] = priority
                problems.loc[selected_index, "due_date"] = pd.Timestamp(
                    due_date
                )
                problems.loc[selected_index, "status"] = proposed_status
                problems.loc[selected_index, "containment"] = containment.strip()
                problems.loc[selected_index, "root_cause"] = root_cause.strip()
                problems.loc[
                    selected_index, "countermeasure"
                ] = countermeasure.strip()
                problems.loc[
                    selected_index, "effectiveness_evidence"
                ] = effectiveness.strip()

                st.session_state["problems"] = problems
                st.success("Problem record updated for this browser session.")
                st.rerun()

        st.subheader("Linked fault events")
        linked_events = events[
            (events["equipment"] == selected_problem["equipment"])
            & (events["fault_code"] == selected_problem["fault_code"])
        ].copy()

        linked_columns = [
            "event_id",
            "fault_start",
            "crew",
            "severity",
            "fault_duration_min",
            "restart_delay_min",
            "total_recovery_min",
        ]

        st.dataframe(
            linked_events[linked_columns].sort_values(
                "fault_start", ascending=False
            ),
            use_container_width=True,
            hide_index=True,
        )

with method_tab:
    st.subheader("Project hypothesis")
    st.info(
        "Manufacturing operations may have sufficient fault visibility but "
        "still struggle to convert repeated events into owned, verified, "
        "permanent countermeasures."
    )

    st.subheader("Current-state pattern")
    st.write(
        "Fault occurs → team restores production → fault remains in history → "
        "same fault repeats → team restores production again."
    )

    st.subheader("Future-state pattern")
    st.write(
        "Fault occurs → repeat pattern is detected → problem is assigned → "
        "containment and root cause are documented → countermeasure is "
        "implemented → effectiveness is checked → problem is closed."
    )

    st.subheader("Metric definitions")
    st.markdown(
        """
- **Fault duration:** fault-cleared time - fault-start time.
- **Restart delay:** equipment restarted time - fault cleared time.
- **Total recovery time:** equipment restarted time - fault start time.
- **Repeat fault:** the same equipment/fault-code pair occurring at least
  3 times within the demo's 7day window.
- **Overdue problem:** an open problem with a due date earlier than the demo
  reference date.
        """
    )

    st.subheader("Limitations")
    st.markdown(
        """
- All data and results are synthetic.
- This is a prototype, not a production MES or specific Company System.
- Problem Board edits are session based and are not permanently stored.
- The application supports human led problem solving; it does not diagnose root
  cause automatically.
        """
    )
