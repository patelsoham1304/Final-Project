"""Career selection and current-skill assessment screen."""

import sqlite3

import streamlit as st

from database.db import create_roadmap, get_current_roadmap, get_skills_for_career
from ui.navigation import navigate_to
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
        st.warning("Please sign in first.")
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
    resume_skills = set(st.session_state.get("resume_detected_skills", []))
    
    # Pre-select both previously saved skills and any detected skills from uploaded resume
    default_names = [
        name for name in career_skill_names
        if (skill_by_name.get(name) and skill_by_name[name]["id"] in previously_known_ids)
        or name in resume_skills
    ]

    # Initialize state for this career's selected skills if not present
    state_key = f"selected_skills_set_{career_id}"
    if state_key not in st.session_state:
        st.session_state[state_key] = set(default_names)
    elif resume_skills and not (st.session_state[state_key] & resume_skills):
        st.session_state[state_key].update(s for s in resume_skills if s in target_names)

    selected_set = st.session_state[state_key]

    # Clean, modern, eye-friendly layout
    st.markdown(
        """
        <div style="margin-top: 10px; margin-bottom: 8px;">
            <div style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">
                Skills Assessment & Auto-Detection
            </div>
            <div style="font-size: 0.88rem; color: #94a3b8; margin-top: 2px;">
                Skills detected from your resume are marked with green checkmarks. Click any pill to toggle.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Render skills as clean interactive checkboxes/pills in columns
    cols = st.columns(min(len(career_skill_names), 4))
    for idx, skill_name in enumerate(career_skill_names):
        col = cols[idx % len(cols)]
        is_known = skill_name in selected_set
        is_from_resume = skill_name in resume_skills
        with col:
            btn_label = f"✓ {skill_name}" if is_known else f"+ {skill_name}"
            btn_type = "primary" if is_known else "secondary"
            if st.button(
                btn_label,
                key=f"skill_toggle_{career_id}_{idx}",
                type=btn_type,
                use_container_width=True,
                help=f"{'Auto-detected from resume' if is_from_resume else 'Click to toggle mastery status'}",
            ):
                if is_known:
                    selected_set.remove(skill_name)
                else:
                    selected_set.add(skill_name)
                st.session_state[state_key] = selected_set
                st.rerun()

    current_skill_names = [s for s in career_skill_names if s in selected_set]
    known_target_count = len(current_skill_names)
    remaining_in_order = [s for s in career_skill_names if s not in selected_set]

    # Gentle, eye-friendly Summary Card (Soothing Navy / Indigo & Soft Emerald)
    if remaining_in_order:
        next_up = remaining_in_order[0]
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, rgba(79, 70, 229, 0.08) 0%, rgba(6, 182, 212, 0.04) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 16px; padding: 18px 20px; margin: 18px 0;
                        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 11px; text-transform: uppercase; font-weight: 700; color: #818cf8; letter-spacing: 0.5px;">
                        🎯 Remaining Learning Gap ({len(remaining_in_order)} skills to learn)
                    </span>
                    <span style="background: rgba(99, 102, 241, 0.15); color: #a5b4fc; font-size: 11.5px; padding: 3px 10px; border-radius: 12px; font-weight: 600;">
                        {known_target_count}/{len(career_skill_names)} Completed
                    </span>
                </div>
                <div style="font-size: 15px; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                    Next Recommended Milestone: <span style="color: #38bdf8; font-size: 16px;">★ {next_up}</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px;">
                    {''.join([f'<span style="background: rgba(255, 255, 255, 0.04); color: #94a3b8; border: 1px solid rgba(255, 255, 255, 0.08); padding: 4px 10px; border-radius: 8px; font-size: 12px;">{i+1}. {s}</span>' for i, s in enumerate(remaining_in_order)])}
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 10px;">
                    Your personalized roadmap starts from <b>{next_up}</b> automatically!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3);
                        border-radius: 14px; padding: 14px 18px; margin: 16px 0; color: #34d399; font-weight: 600;">
                🎉 All skills mastered for this career path!
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.button("Save Assessment & Build Learning Path 🚀", type="primary", use_container_width=True):
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
            st.success("Your assessment is saved and your learning path is ready.")
            navigate_to("Skill Gap & Roadmap")
        except ValueError as error:
            st.error(str(error))
        except sqlite3.Error:
            st.error("The assessment could not be saved. Check the local database.")
