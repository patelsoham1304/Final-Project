"""Student progress dashboard."""

import sqlite3

import streamlit as st

from database.db import (
    get_current_roadmap,
    get_progress_for_student,
    get_resources_for_skill,
    get_skills_for_career,
    get_student,
)
from modules.progress import calculate_overall_progress, summarize_required_skills
from modules.recommendation import get_next_recommended_skill
from modules.roadmap import generate_roadmap


def render():
    """Show the active student, learning path, progress, and recent activity."""
    st.header("Dashboard")
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Select or create a student profile first.")
        return

    try:
        student = get_student(student_id)
        if student is None:
            st.warning("The selected student profile no longer exists.")
            return
        roadmap = get_current_roadmap(student_id)
        progress = get_progress_for_student(student_id)
        required = (
            get_skills_for_career(roadmap["career_id"]) if roadmap is not None else []
        )
    except sqlite3.Error:
        st.error("The dashboard could not load data from the local database.")
        return

    st.subheader(student["name"])
    if student["email"]:
        st.caption(student["email"])
    if roadmap is None:
        st.info("Choose a target career and assess your current skills to get started.")
        return
    if not required:
        st.warning("This career has no mapped skills yet.")
        return

    progress_by_id = {item["skill_id"]: item for item in progress}
    required_progress = summarize_required_skills(
        [dict(skill) for skill in required],
        [dict(item) for item in progress],
    )
    completed = [
        item["skill"]
        for item in required_progress
        if item["status"] == "completed"
    ]
    incomplete = [
        item["skill"]
        for item in required_progress
        if item["status"] != "completed"
    ]
    overall = calculate_overall_progress(required_progress)
    st.markdown(f"**Target career:** {roadmap['career_name']}")
    st.metric("Overall roadmap progress", f"{overall:.0f}%")
    st.progress(overall / 100)

    names = [skill["name"] for skill in required]
    current = {
        skill["name"]: int(
            skill["id"] in progress_by_id
            and progress_by_id[skill["id"]]["status"] == "completed"
        )
        for skill in required
    }
    learning_path = generate_roadmap({name: 1 for name in names}, current, names)
    recommendation = get_next_recommended_skill(
        [
            {
                "skill": item["skill"],
                "required": item["to_level"],
                "current": item["from_level"],
                "gap": item["to_level"] - item["from_level"],
            }
            for item in learning_path
        ]
    )
    focus = recommendation["skill"] if recommendation else "All skills completed"
    columns = st.columns(3)
    columns[0].metric("Skills completed", f"{len(completed)} / {len(required)}")
    columns[1].metric("Skills remaining", len(incomplete))
    columns[2].metric("Next recommended skill", focus)

    st.subheader("Roadmap preview")
    if learning_path:
        for step in learning_path[:5]:
            st.write(f"{step['step']}. Learn {step['skill']}")
    else:
        st.success("Your roadmap is complete.")

    if recommendation:
        skill_row = next(
            skill for skill in required if skill["name"] == recommendation["skill"]
        )
        st.subheader(f"Recommended resources: {recommendation['skill']}")
        try:
            resources = get_resources_for_skill(skill_row["id"])
        except sqlite3.Error:
            st.error("Recommended resources could not be loaded.")
        else:
            if resources:
                for resource in resources:
                    st.markdown(
                        f"- [{resource['title']}]({resource['url']}) "
                        f"({resource['type']})"
                    )
            else:
                st.info("No resources have been added for this skill.")

    left, right = st.columns(2)
    with left:
        st.subheader("Completed skills")
        st.write(", ".join(completed) if completed else "None yet")
    with right:
        st.subheader("Remaining skills")
        st.write(", ".join(incomplete) if incomplete else "None")

    st.subheader("Recent progress activity")
    if progress:
        recent = [
            {
                "Skill": item["skill_name"],
                "Status": item["status"].replace("_", " ").title(),
                "Progress": f"{item['progress_percent']}%",
                "Last updated": item["updated_at"],
            }
            for item in progress[:10]
        ]
        st.dataframe(recent, hide_index=True, width="stretch")
    else:
        st.info("Progress activity will appear here when you update your roadmap.")
