"""Skill-gap, ordered recommendation, and learning-resource screen."""

import sqlite3

import streamlit as st

from database.db import (
    get_current_roadmap,
    get_resources_for_skill,
    get_skills_for_career,
)
from modules.recommendation import get_next_recommended_skill
from modules.roadmap import generate_roadmap
from modules.skill_assessment import get_assessments
from modules.youtube_resources import get_recommended_youtube_video
from ui.navigation import navigate_to
from ui.roadmap_diagram import (
    build_roadmap_diagram_data,
    render_roadmap_diagram,
)



def render():
    """Render known skills, missing skills, and the ordered roadmap."""
    st.header("Skill Gap & Roadmap")
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please sign in first.")
        return

    try:
        current_roadmap = get_current_roadmap(student_id)
        if current_roadmap is None:
            st.info("Choose a career and complete your skill assessment first.")
            if st.button("Choose a career"):
                navigate_to("Select Career")
            return
        required = get_skills_for_career(current_roadmap["career_id"])
        assessments = get_assessments(student_id)
    except sqlite3.Error:
        st.error("The learning path could not be loaded from the database.")
        return

    if not required:
        st.warning("This career has no mapped skills yet.")
        return

    assessed_by_id = {item["skill_id"]: item for item in assessments}
    resources_by_skill_id = {}
    try:
        for skill in required:
            resources_by_skill_id[skill["id"]] = get_resources_for_skill(skill["id"])
    except sqlite3.Error:
        st.error("Learning resources could not be loaded for the roadmap.")
        return

    known = []
    for item in required:
        if item["id"] in assessed_by_id:
            known.append(item["name"])
    skill_names = [item["name"] for item in required]
    required_levels = {name: 1 for name in skill_names}
    current_levels = {}
    for item in required:
        current_levels[item["name"]] = int(item["id"] in assessed_by_id)
    roadmap = generate_roadmap(required_levels, current_levels, skill_names)
    recommended = get_next_recommended_skill(
        [
            {
                "skill": step["skill"],
                "required": step["to_level"],
                "current": step["from_level"],
                "gap": step["to_level"] - step["from_level"],
            }
            for step in roadmap
        ]
    )

    st.subheader(f"Target career: {current_roadmap['career_name']}")



    known_column, missing_column = st.columns(2)
    with known_column:
        st.markdown("**Already Known Skills**")
        if known:
            known_chips = "".join(
                f'<span class="skill-chip known"><span style="color:#10b981;">✓</span> {name}</span>'
                for name in known
            )
            st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{known_chips}</div>', unsafe_allow_html=True)
        else:
            st.write("None")
    with missing_column:
        st.markdown("**Missing Skills**")
        missing_names = [step["skill"] for step in roadmap]
        if missing_names:
            rec_name = recommended["skill"] if recommended else None
            missing_chips = "".join(
                f'<span class="skill-chip next"><span style="color:#f59e0b;">★</span> {name}</span>'
                if name == rec_name
                else f'<span class="skill-chip missing"><span style="color:#60a5fa;">○</span> {name}</span>'
                for name in missing_names
            )
            st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{missing_chips}</div>', unsafe_allow_html=True)
        else:
            st.write("None")

    if recommended:
        st.markdown(
            f"""
            <div class="next-step-card" style="background:linear-gradient(135deg, rgba(245,158,11,0.14), rgba(217,119,6,0.06));
                        border:1px solid #f59e0b;border-radius:14px;padding:16px 20px;margin:16px 0;
                        box-shadow:0 0 20px rgba(245,158,11,0.18);display:flex;align-items:center;justify-content:space-between;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#f59e0b,#d97706);
                                display:grid;place-items:center;color:#0b1024;font-size:18px;font-weight:800;
                                box-shadow:0 0 14px rgba(245,158,11,0.4);">
                        ★
                    </div>
                    <div>
                        <div style="font-size:11px;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:0.05em;">Recommended Next Step</div>
                        <div style="font-size:17px;color:#ffffff;font-weight:700;">{recommended['skill']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        future = [step["skill"] for step in roadmap[1:]]
        st.caption(
            "Future skills in dependency order: "
            + (", ".join(future) if future else "none")
        )
    else:
        st.success("You marked every skill required for this career as already known.")

    st.subheader("Visual Learning Path")
    st.caption(
        "The complete career path is shown in prerequisite order. Green checks "
        "mark skills you selected as already known; purple markers show skills "
        "to learn. Select a skill for details, or search, pan, and zoom."
    )
    try:
        diagram_data = build_roadmap_diagram_data(
            current_roadmap["career_name"],
            required,
            assessed_by_id,
            resources_by_skill_id,
        )
        render_roadmap_diagram(diagram_data)
    except (TypeError, ValueError) as error:
        st.error(f"The visual roadmap could not be created: {error}")
        return

    st.subheader("Complete career roadmap")
    for index, skill in enumerate(required, start=1):
        already_known = skill["id"] in assessed_by_id
        title = (
            f"{index}. Already know: {skill['name']}"
            if already_known
            else f"{index}. Learn {skill['name']}"
        )
        with st.expander(title):
            if already_known:
                st.write("You selected this skill as one you already know.")
            else:
                st.write("Learn this skill in the displayed prerequisite order.")
            if not already_known:
                video = get_recommended_youtube_video(skill["name"])
                if video:
                    st.write(f"**Recommended video:** {video['title']}")
                    st.video(video["url"])
                    st.link_button("Watch this video on YouTube", video["url"])
                else:
                    st.info("A direct video recommendation is not available for this skill yet.")
