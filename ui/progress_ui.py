"""Read-only, automatically calculated skill progress screen."""

import sqlite3

import streamlit as st

from database.db import get_current_roadmap, get_progress_for_student, get_skills_for_career
from modules.progress import calculate_overall_progress, summarize_required_skills


def render():
    """Show skill completion derived from the student's current assessment."""
    st.header("Your Learning Progress")
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Select or create a student profile first.")
        return

    try:
        roadmap = get_current_roadmap(student_id)
        if roadmap is None:
            st.info("Select a career and assess your current skills first.")
            return
        skills = get_skills_for_career(roadmap["career_id"])
        saved_progress = get_progress_for_student(student_id)
    except sqlite3.Error:
        st.error("Progress could not be loaded from the database.")
        return

    if not skills:
        st.warning("This career has no mapped skills to track.")
        return

    required_progress = summarize_required_skills(
        [dict(skill) for skill in skills],
        [dict(item) for item in saved_progress],
    )
    completed_count = sum(item["completed"] for item in required_progress)
    overall = calculate_overall_progress(required_progress)

    st.caption(
        f"Progress for your **{roadmap['career_name']}** learning path is calculated "
        "automatically from the skills in your assessment. There are no manual "
        "progress controls on this screen."
    )
    st.metric(
        "Skills completed",
        f"{completed_count} / {len(required_progress)}",
        f"{overall:.0f}% of this career path",
    )
    st.progress(overall / 100)

    st.subheader("Skill checklist")
    for item in required_progress:
        if item["completed"]:
            st.markdown(f"- **[+] {item['skill']}** — Completed")
        else:
            st.markdown(f"- **[-] {item['skill']}** — Still to learn")

    st.info(
        "To update which skills you already know, go to **Select Career** and "
        "save your current-skills assessment. This page recalculates automatically."
    )
