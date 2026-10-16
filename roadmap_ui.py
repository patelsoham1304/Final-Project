"""Skill-gap, ordered recommendation, and learning-resource screen."""

import sqlite3

import streamlit as st

from database.db import (
    get_current_roadmap,
    get_progress_for_student,
    get_resources_for_skill,
    get_skills_for_career,
)
from modules.recommendation import get_next_recommended_skill
from modules.roadmap import generate_roadmap


def render():
    """Render known skills, missing skills, and the ordered roadmap."""
    st.header("Skill Gap & Roadmap")
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Select or create a student profile first.")
        return

    try:
        current_roadmap = get_current_roadmap(student_id)
        if current_roadmap is None:
            st.info("Choose a career and complete your skill assessment first.")
            return
        required = get_skills_for_career(current_roadmap["career_id"])
        progress = get_progress_for_student(student_id)
    except sqlite3.Error:
        st.error("The learning path could not be loaded from the database.")
        return

    if not required:
        st.warning("This career has no mapped skills yet.")
        return

    progress_by_id = {item["skill_id"]: item for item in progress}
    known = []
    for item in required:
        saved_progress = progress_by_id.get(item["id"])
        if saved_progress and saved_progress["status"] == "completed":
            known.append(item["name"])
    skill_names = [item["name"] for item in required]
    required_levels = {name: 1 for name in skill_names}
    current_levels = {}
    for item in required:
        saved_progress = progress_by_id.get(item["id"])
        current_levels[item["name"]] = int(
            saved_progress is not None and saved_progress["status"] == "completed"
        )
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
        st.markdown("**Already known skills**")
        st.write(", ".join(known) if known else "No required skills marked complete yet.")
    with missing_column:
        st.markdown("**Missing skills**")
        missing_names = [step["skill"] for step in roadmap]
        st.write(", ".join(missing_names) if missing_names else "No skill gaps.")

    if recommended:
        st.info(f"Recommended next skill: **{recommended['skill']}**")
        future = [step["skill"] for step in roadmap[1:]]
        st.caption(
            "Future skills in dependency order: "
            + (", ".join(future) if future else "none")
        )
    else:
        st.success("You already know every skill required for this career.")

    st.subheader("Your ordered roadmap")
    if not roadmap:
        st.write("Your learning path is complete.")
    else:
        # Career roadmap.sh slug mapping
        career_slug_map = {
            "Frontend Developer": "https://roadmap.sh/frontend",
            "Backend Developer": "https://roadmap.sh/backend",
            "Data Analyst": "https://roadmap.sh/data-analyst",
            "Data Scientist": "https://roadmap.sh/ai-data-scientist",
            "Cybersecurity Analyst": "https://roadmap.sh/cyber-security",
            "UI/UX Designer": "https://roadmap.sh/ux-design",
        }
        career_name = current_roadmap.get("career_name", "")
        roadmap_sh_url = career_slug_map.get(career_name)

        tab1, tab2, tab3 = st.tabs(["🗺️ Visual Tree Roadmap", "⚡ roadmap.sh Live API (Anakin)", "🌐 Interactive Preview"])

        with tab1:
            # Embed the full interactive roadmap diagram test directly in Streamlit
            import os
            html_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "roadmap-test.html")
            if os.path.exists(html_file_path):
                with open(html_file_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=850, scrolling=True)
            else:
                st.info("Interactive roadmap test file loading...")



        with tab2:
            st.markdown("#### ⚡ Live roadmap.sh API Data (via Anakin.io)")
            st.caption("Connected with your Anakin API key (`ask_ee95...c3d7`)")
            slug_key = career_name.lower().replace(" ", "-").replace("analyst", "").strip("-")
            if "cyber" in slug_key:
                slug_key = "cyber-security"
            elif "frontend" in slug_key:
                slug_key = "frontend"
            elif "backend" in slug_key:
                slug_key = "backend"
            elif "data" in slug_key and "scientist" in slug_key:
                slug_key = "ai-data-scientist"
            elif "ux" in slug_key or "ui" in slug_key:
                slug_key = "ux-design"
            else:
                slug_key = "python"

            col_api1, col_api2 = st.columns([3, 1])
            col_api1.write(f"Target Roadmap Slug: `{slug_key}`")
            if col_api2.button("Fetch Live API Data", key="btn_fetch_anakin"):
                from modules.anakin_roadmap import fetch_roadmap_detail
                with st.spinner("Fetching data from Anakin roadmap.sh API..."):
                    api_data = fetch_roadmap_detail(slug_key)
                    if api_data:
                        st.success("API Response Received Successfully!")
                        st.json(api_data)
                    else:
                        st.info("API request submitted. (Note: Anakin Wire API tasks process asynchronously).")

        with tab3:
            if roadmap_sh_url:
                st.info(f"Viewing official interactive roadmap for **{career_name}**:")
                st.link_button(f"Open {career_name} roadmap.sh in new tab ↗", roadmap_sh_url)
                st.components.v1.iframe(roadmap_sh_url, height=750, scrolling=True)
            else:
                st.write("Interactive online roadmap link not available for this role.")




    for step in roadmap:
        with st.expander(f"{step['step']}. Learn {step['skill']}"):
            st.write("Complete this skill before moving to the next ordered skill.")
            try:
                resources = get_resources_for_skill(
                    next(item["id"] for item in required if item["name"] == step["skill"])
                )
            except sqlite3.Error:
                st.error("Resources could not be loaded.")
                continue
            if not resources:
                st.info("No learning resources have been added for this skill yet.")
            for resource in resources:
                free_label = "Free" if resource["is_free"] else "Paid"
                st.markdown(
                    f"- [{resource['title']}]({resource['url']}) "
                    f"({resource['type']}, {free_label})"
                )

    if st.button("Continue to progress tracking"):
        st.session_state.workflow_step = "Update Progress"
        st.rerun()
