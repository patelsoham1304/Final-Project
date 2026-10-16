"""Weekly study-time planner screen."""

import sqlite3

import streamlit as st

from database.db import get_current_roadmap, get_progress_for_student, get_skills_for_career
from modules.planner import plan_study_time
from modules.roadmap import generate_roadmap


def render():
    """Allocate the student's available hours across the ordered skill gap."""
    st.header("Study Time Planner")
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Select or create a student profile first.")
        return

    try:
        roadmap = get_current_roadmap(student_id)
        if roadmap is None:
            st.info("Select a career and create a learning path first.")
            return
        required = get_skills_for_career(roadmap["career_id"])
        progress = get_progress_for_student(student_id)
    except sqlite3.Error:
        st.error("The planner could not load your learning path.")
        return

    if not required:
        st.info("This career has no mapped skills to plan yet.")
        return
    progress_by_id = {item["skill_id"]: item for item in progress}
    names = [skill["name"] for skill in required]
    current = {
        skill["name"]: int(
            skill["id"] in progress_by_id
            and progress_by_id[skill["id"]]["status"] == "completed"
        )
        for skill in required
    }
    learning_path = generate_roadmap(
        {name: 1 for name in names}, current, names
    )
    if not learning_path:
        st.success("All required skills are complete; no study hours need allocating.")
        return

    hours = st.number_input(
        "Available study hours per week",
        min_value=0.0,
        max_value=168.0,
        value=10.0,
        step=0.5,
    )
    if hours == 0:
        st.info("Enter a positive number of hours to create a weekly plan.")
        return
    allocations = plan_study_time(
        hours, [step["skill"] for step in learning_path]
    )
    st.write(f"Equal split across {len(allocations)} ordered skills:")
    st.dataframe(allocations, hide_index=True, width="stretch")
    st.caption("The hours are divided evenly, and the final step receives any rounding remainder.")
