"""Resume upload screen with sleek choices for students."""

import streamlit as st

from modules.resume_upload import MAX_RESUME_BYTES
from ui.navigation import navigate_to


def render():
    """Let the student upload a resume or start fresh by choosing their target career."""
    st.markdown(
        """
        <div style="margin-bottom: 22px;">
            <h2 style="font-size: 1.85rem; font-weight: 800; color: #f8fafc; margin-bottom: 6px;">
                🚀 Choose How You'd Like to Begin
            </h2>
            <p style="color: #94a3b8; font-size: 0.95rem; margin: 0; line-height: 1.5;">
                Jumpstart your learning journey either by uploading an existing resume or by exploring our curated career tracks from scratch.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_upload, col_skip = st.columns([1.05, 0.95], gap="large")

    with col_upload:
        st.markdown(
            """
            <div style="background: linear-gradient(145deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
                        border: 1px solid rgba(148, 163, 184, 0.15); border-radius: 18px; padding: 22px;
                        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25); position: relative; overflow: hidden; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">📑</span>
                        <span style="font-weight: 800; font-size: 16px; color: #f8fafc;">Upload Existing Resume</span>
                    </div>
                    <span style="background: rgba(59, 130, 246, 0.18); color: #60a5fa; font-size: 11px; font-weight: 700;
                                 padding: 3px 10px; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.35);">
                        Personalized
                    </span>
                </div>
                <div style="color: #94a3b8; font-size: 13px; line-height: 1.55;">
                    Have an updated resume? Upload your PDF, DOCX, or TXT file to keep it ready for your profile.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded_file = st.file_uploader(
            "Upload your resume",
            type=["pdf", "docx", "txt"],
            help="PDF, DOCX, or UTF-8 TXT; maximum 10 MB.",
            key="career_path_resume_file",
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            if uploaded_file.size > MAX_RESUME_BYTES:
                st.error("Resume files must be 10 MB or smaller.")
            elif uploaded_file.size == 0:
                st.error("The selected resume is empty. Choose a file with content.")
            else:
                st.success(f"✓ {uploaded_file.name} ready for analysis!")
                try:
                    from modules.resume_upload import extract_resume_text, extract_known_skills_from_text
                    from modules.skill_assessment import get_available_skills, save_assessment
                    
                    resume_bytes = uploaded_file.getvalue()
                    resume_text = extract_resume_text(uploaded_file.name, resume_bytes)
                    all_skills = get_available_skills()
                    all_skill_names = [s["name"] for s in all_skills]
                    detected_names = extract_known_skills_from_text(resume_text, all_skill_names)

                    all_careers = [dict(c) for c in __import__("database.db", fromlist=["get_careers"]).get_careers()]
                    career_skills_map = {
                        c["id"]: [s["name"] for s in __import__("database.db", fromlist=["get_skills_for_career"]).get_skills_for_career(c["id"])]
                        for c in all_careers
                    }

                    # Calculate match statistics for all careers
                    career_match_data = []
                    for c in all_careers:
                        c_skills = career_skills_map[c["id"]]
                        matched_in_career = [s for s in c_skills if s in detected_names]
                        pct = int((len(matched_in_career) / len(c_skills)) * 100) if c_skills else 0
                        pending = [s for s in c_skills if s not in detected_names]
                        career_match_data.append({
                            "career": c,
                            "matched_skills": matched_in_career,
                            "pending_skills": pending,
                            "next_skill": pending[0] if pending else None,
                            "pct": pct,
                            "matched_count": len(matched_in_career),
                            "total_count": len(c_skills),
                        })

                    # Sort by match percentage descending
                    career_match_data.sort(key=lambda x: (x["pct"], x["matched_count"]), reverse=True)

                    # Initialize selected career id in session state
                    if "resume_selected_career_id" not in st.session_state or st.session_state["resume_selected_career_id"] not in [c["id"] for c in all_careers]:
                        st.session_state["resume_selected_career_id"] = career_match_data[0]["career"]["id"]

                    active_career_id = st.session_state["resume_selected_career_id"]
                    active_match = next(item for item in career_match_data if item["career"]["id"] == active_career_id)

                    st.session_state["career_id"] = active_career_id
                    st.session_state["resume_detected_skills"] = detected_names
                    st.session_state["uploaded_resume_name"] = uploaded_file.name

                    student_id = st.session_state.get("student_id")
                    if student_id and detected_names:
                        skill_by_name = {s["name"]: s["id"] for s in all_skills}
                        detected_ids = [skill_by_name[name] for name in detected_names if name in skill_by_name]
                        save_assessment(student_id, detected_ids)

                    if detected_names:
                        skills_badges = "".join(
                            f'<span style="background: rgba(16,185,129,0.25); color: #6ee7b7; padding: 4px 10px; border-radius: 8px; font-size: 12px; font-weight:600;">✓ {s}</span>'
                            for s in detected_names
                        )

                        # Display detected skills summary
                        st.markdown(
                            f"""
                            <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(148, 163, 184, 0.2);
                                        border-radius: 14px; padding: 14px; margin: 12px 0 10px 0;">
                                <div style="font-size: 13px; font-weight: 700; color: #38bdf8; margin-bottom: 6px;">
                                    🔍 Skills Detected in Your Resume ({len(detected_names)} found):
                                </div>
                                <div style="display: flex; flex-wrap: wrap; gap: 6px;">
                                    {skills_badges}
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Matching career fields section: Professional interactive track cards
                        st.markdown(
                            """
                            <div style="margin-top: 14px; margin-bottom: 8px;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span style="font-size: 13px; font-weight: 800; color: #f8fafc; text-transform: uppercase; letter-spacing: 0.5px;">
                                        🎯 Pick Your Target Career Path
                                    </span>
                                    <span style="font-size: 11px; color: #94a3b8;">
                                        Tap a track to activate
                                    </span>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        # Filter careers that have at least 1 match or top 3 careers
                        top_careers = [item for item in career_match_data if item["matched_count"] > 0]
                        if not top_careers:
                            top_careers = career_match_data[:3]
                        elif len(top_careers) < 3 and len(career_match_data) >= 3:
                            # include one more career with 0 matches for variety
                            top_careers.append(career_match_data[len(top_careers)])

                        # Render careers in rows of 2 or 3 so each card has plenty of horizontal width
                        num_per_row = 3 if len(top_careers) >= 3 else len(top_careers)
                        for row_start in range(0, len(top_careers), num_per_row):
                            row_careers = top_careers[row_start : row_start + num_per_row]
                            card_cols = st.columns(num_per_row)
                            for idx, item in enumerate(row_careers):
                                c_id = item["career"]["id"]
                                c_name = item["career"]["name"]
                                c_pct = item["pct"]
                                c_cnt = item["matched_count"]
                                c_tot = item["total_count"]
                                is_active = (c_id == active_career_id)

                                with card_cols[idx]:
                                    border_color = "#38bdf8" if is_active else "rgba(148, 163, 184, 0.25)"
                                    bg_grad = (
                                        "linear-gradient(160deg, rgba(14, 165, 233, 0.28), rgba(99, 102, 241, 0.22))"
                                        if is_active
                                        else "linear-gradient(160deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9))"
                                    )
                                    status_badge = (
                                        '<span style="background: #0284c7; color: #ffffff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">CURRENT TARGET</span>'
                                        if is_active
                                        else '<span style="background: rgba(148,163,184,0.15); color: #94a3b8; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 6px;">AVAILABLE</span>'
                                    )

                                    st.markdown(
                                        f"""
                                        <div style="background: {bg_grad}; border: 2px solid {border_color};
                                                    border-radius: 14px; padding: 14px 12px; margin-bottom: 8px;
                                                    box-shadow: {'0 8px 24px rgba(14, 165, 233, 0.28)' if is_active else '0 3px 10px rgba(0,0,0,0.25)'};">
                                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                                                <span style="font-size: 24px;">{'🎯' if is_active else '💼'}</span>
                                                {status_badge}
                                            </div>
                                            <div style="font-size: 15px; font-weight: 800; color: {'#38bdf8' if is_active else '#f8fafc'}; margin-bottom: 8px; line-height: 1.25; min-height: 38px; display: flex; align-items: center;">
                                                {c_name}
                                            </div>
                                            <div style="background: rgba(15, 23, 42, 0.6); border-radius: 10px; padding: 8px 10px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between;">
                                                <div>
                                                    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #94a3b8; font-weight: 700;">Resume Match</div>
                                                    <div style="font-size: 20px; font-weight: 900; color: {'#38bdf8' if c_pct > 0 else '#94a3b8'};">
                                                        {c_pct}%
                                                    </div>
                                                </div>
                                                <div style="text-align: right;">
                                                    <div style="font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; color: #94a3b8; font-weight: 700;">Skills</div>
                                                    <div style="font-size: 13px; font-weight: 700; color: #e2e8f0;">
                                                        {c_cnt} / {c_tot}
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True,
                                    )

                                    btn_label = f"✓ Selected: {c_name}" if is_active else f"Select {c_name}"
                                    if st.button(btn_label, key=f"choose_career_btn_{c_id}", use_container_width=True, type="primary" if is_active else "secondary"):
                                        st.session_state["resume_selected_career_id"] = c_id
                                        st.session_state["career_id"] = c_id
                                        st.rerun()

                        # Show active chosen career details & Next Recommended Skill
                        next_skill = active_match["next_skill"]
                        next_skill_html = ""
                        if next_skill:
                            next_skill_html = f"""
                            <div style="background: rgba(245, 158, 11, 0.12); border-left: 3px solid #f59e0b; padding: 10px 14px; border-radius: 8px; margin-top: 10px;">
                                <div style="display: flex; align-items: center; justify-content: space-between;">
                                    <span style="font-size: 11px; font-weight: 700; color: #fbbf24; text-transform: uppercase; letter-spacing: 0.5px;">
                                        ⚡ Next Recommended Skill to Learn:
                                    </span>
                                    <span style="font-size: 10px; background: rgba(245, 158, 11, 0.2); color: #fde68a; padding: 2px 7px; border-radius: 6px; font-weight:600;">
                                        Milestone 1
                                    </span>
                                </div>
                                <div style="font-size: 14px; font-weight: 700; color: #f8fafc; margin-top: 3px;">
                                    ★ <span style="color: #f59e0b;">{next_skill}</span>
                                </div>
                                <div style="font-size: 12px; color: #94a3b8; margin-top: 3px;">
                                    We marked your existing skills as completed and queued <b>{next_skill}</b> directly as Step 1.
                                </div>
                            </div>
                            """

                        matched_in_chosen = active_match["matched_skills"]
                        chosen_badges = "".join(
                            f'<span style="background: rgba(16,185,129,0.25); color: #6ee7b7; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight:600;">✓ {s}</span>'
                            for s in matched_in_chosen
                        ) if matched_in_chosen else '<span style="color:#94a3b8; font-size:11px;">Starting fresh for this track</span>'

                        st.markdown(
                            f"""
                            <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.25);
                                        border-radius: 12px; padding: 12px 14px; margin: 10px 0 14px 0;">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                    <span style="font-weight: 700; color: #34d399; font-size: 13px;">
                                        💼 Selected Track: <u>{active_match['career']['name']}</u>
                                    </span>
                                    <span style="background: rgba(16, 185, 129, 0.2); color: #a7f3d0; font-size: 11px; padding: 2px 8px; border-radius: 10px;">
                                        {active_match['pct']}% Match ({active_match['matched_count']}/{active_match['total_count']} acquired)
                                    </span>
                                </div>
                                <div style="font-size: 11px; color: #cbd5e1; margin-bottom: 6px;">
                                    <b>Already acquired for this role:</b>
                                    <div style="display: flex; flex-wrap: wrap; gap: 4px; margin-top: 4px;">
                                        {chosen_badges}
                                    </div>
                                </div>
                                {next_skill_html}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            """
                            <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.3);
                                        border-left: 4px solid #ef4444; border-radius: 12px; padding: 14px 16px; margin: 12px 0;">
                                <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; color: #f87171; font-size: 14px;">
                                    ⚠️ In your resume you cannot mention your skills.
                                </div>
                                <div style="font-size: 12px; color: #cbd5e1; margin-top: 5px; line-height: 1.5;">
                                    We couldn't detect recognized technical skills in your uploaded resume. You can select your desired career track below to start learning from scratch, or update your resume and re-upload.
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("Generate My Roadmap Automatically ⚡", type="primary", use_container_width=True):
                            from database.db import create_roadmap
                            from modules.skill_assessment import save_career_assessment
                            skill_by_name = {s["name"]: s["id"] for s in all_skills}
                            career_skill_ids = [skill_by_name[s] for s in career_skills_map[active_career_id] if s in skill_by_name]
                            selected_ids = [skill_by_name[s] for s in active_match["matched_skills"] if s in skill_by_name]
                            if student_id:
                                save_career_assessment(student_id, career_skill_ids, selected_ids)
                                create_roadmap(student_id, active_career_id)
                            navigate_to("Skill Gap & Roadmap")
                    with col_btn2:
                        if st.button("Change Career / Customize Skills ⚙️", use_container_width=True):
                            navigate_to("Select Career")
                except Exception as err:
                    st.warning(f"Could not parse resume text ({err}). You can still continue to career selection.")
                    if st.button("Continue to Select Career 🚀", type="primary", use_container_width=True):
                        navigate_to("Select Career")

    with col_skip:
        st.markdown(
            """
            <div style="background: linear-gradient(145deg, rgba(14, 165, 233, 0.12), rgba(99, 102, 241, 0.12));
                        border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 18px; padding: 22px;
                        box-shadow: 0 10px 30px rgba(14, 165, 233, 0.1); margin-bottom: 12px;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <span style="font-size: 26px;">⚡</span>
                        <span style="font-weight: 800; font-size: 16px; color: #38bdf8;">Start Fresh from Scratch</span>
                    </div>
                    <span style="background: rgba(16, 185, 129, 0.18); color: #34d399; font-size: 11px; font-weight: 700;
                                 padding: 3px 10px; border-radius: 20px; border: 1px solid rgba(16, 185, 129, 0.35);">
                        Instant Access
                    </span>
                </div>
                <div style="color: #cbd5e1; font-size: 13px; line-height: 1.55; margin-bottom: 14px;">
                    No resume needed! Jump straight into assessing your skills and generating a tailored roadmap.
                </div>
                <div style="display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: #94a3b8; margin-bottom: 16px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #38bdf8;">✓</span> Explore 6 in-demand career paths
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #38bdf8;">✓</span> Interactive skill gap analyzer
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="color: #38bdf8;">✓</span> Dynamic roadmap & weekly study planner
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Explore Careers & Build Roadmap ➔", type="primary", use_container_width=True):
            navigate_to("Select Career")


