"""Career selection and current-skill assessment screen."""

import sqlite3

import streamlit as st

from database.db import create_roadmap, get_current_roadmap, get_skills_for_career
from modules.career import list_careers
from modules.skill_assessment import (
    get_assessments,
    get_available_skills,
    save_career_assessment,
)


def render():
    """Let students choose a career and assess skills relevant to that path."""
    st.header("Choose Your Career Path")
    st.write(
        "Pick a target role, then mark only the skills you can already use with "
        "confidence. Your learning path will focus on what remains."
    )
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Select or create a student profile first.")
        return

    try:
        careers = list_careers()
        all_skills = get_available_skills()
        assessments = get_assessments(student_id)
        current_roadmap = get_current_roadmap(student_id)
    except sqlite3.Error:
        st.error("Career and skill data could not be loaded from the database.")
        return

    if not careers:
        st.warning("There are no careers in the database yet.")
        return
    if not all_skills:
        st.warning("There are no skills in the database yet.")
        return

    career_by_id = {career["id"]: career for career in careers}
    saved_career_id = (
        current_roadmap["career_id"] if current_roadmap else None
    )
    if saved_career_id not in career_by_id:
        saved_career_id = st.session_state.get("career_id")
    career_ids = list(career_by_id)
    career_index = (
        career_ids.index(saved_career_id) if saved_career_id in career_by_id else 0
    )
    career_id = st.selectbox(
        "Target career",
        career_ids,
        index=career_index,
        format_func=lambda item_id: career_by_id[item_id]["name"],
        key="career_assessment_career",
    )
    career = career_by_id[career_id]
    st.info(career["description"])

    skill_by_id = {skill["id"]: skill for skill in all_skills}
    skill_by_name = {skill["name"]: skill for skill in all_skills}
    try:
        career_skill_names = [
            row["name"] for row in get_skills_for_career(career_id)
        ]
    except sqlite3.Error:
        st.error("The selected career's skills could not be loaded.")
        return
    previously_known_ids = {item["skill_id"] for item in assessments}
    target_names = set(career_skill_names)
    career_skill_ids = {
        skill["id"]
        for skill in all_skills
        if skill["name"] in target_names
    }
    default_names = [
        skill_by_id[skill_id]["name"]
        for skill_id in previously_known_ids
        if skill_id in skill_by_id and skill_by_id[skill_id]["name"] in target_names
    ]

    st.markdown("#### Skills you already know")
    st.caption(
        "Choose only target-role skills you can demonstrate. Previously assessed "
        "skills outside this career are retained automatically."
    )
    current_skill_names = st.multiselect(
        "Select your confident skills",
        career_skill_names,
        default=default_names,
        key=f"known_skills_{career_id}",
        help="Be honest: this list determines your starting point and completed-skill progress.",
    )
    known_target_count = len(set(current_skill_names) & set(career_skill_names))
    st.caption(
        f"{known_target_count} of {len(career_skill_names)} target skills assessed as known."
    )

    if st.button("Save assessment and build my learning path", type="primary"):
        selected_ids = [
            skill_by_name[name]["id"]
            for name in current_skill_names
            if name in target_names
        ]
        target_ids = list(career_skill_ids)
        try:
            save_career_assessment(student_id, target_ids, selected_ids)
            current = get_current_roadmap(student_id)
            if current is None or current["career_id"] != career_id:
                create_roadmap(student_id, career_id)
            st.session_state.career_id = career_id
            st.session_state.workflow_step = "Skill Gap & Roadmap"
            st.success("Your assessment is saved and your learning path is ready.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))
        except sqlite3.Error:
            st.error("The assessment could not be saved. Check the local database.")
