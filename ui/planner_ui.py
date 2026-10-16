"""Weekly study-time planner screen with modern executive UI, vector analytics, and smart schedule cards."""

import sqlite3
import streamlit as st

from database.db import get_current_roadmap, get_skills_for_career
from modules.planner import plan_study_time
from modules.roadmap import generate_roadmap
from modules.skill_assessment import get_assessments
from ui.navigation import navigate_to


def render():
    """Allocate the student's available hours across the ordered skill gap with sleek, professional UI."""
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please sign in first.")
        return

    try:
        roadmap = get_current_roadmap(student_id)
        if roadmap is None:
            st.info("Select a career and create a learning path first.")
            if st.button("Choose a career"):
                navigate_to("Select Career")
            return
        required = get_skills_for_career(roadmap["career_id"])
        assessments = get_assessments(student_id)
    except sqlite3.Error:
        st.error("The planner could not load your learning path.")
        return

    if not required:
        st.info("This career has no mapped skills to plan yet.")
        return

    assessed_skill_ids = {item["skill_id"] for item in assessments}
    names = [skill["name"] for skill in required]
    current = {
        skill["name"]: int(
            skill["id"] in assessed_skill_ids
        )
        for skill in required
    }
    learning_path = generate_roadmap(
        {name: 1 for name in names}, current, names
    )

    # Executive Banner for Study Planner
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(30, 41, 79, 0.45) 0%, rgba(15, 23, 42, 0.65) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 18px; padding: 22px 26px;
                    margin-bottom: 24px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35);">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 16px;">
                    <div style="width: 52px; height: 52px; border-radius: 14px;
                                background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
                                display: flex; align-items: center; justify-content: center;
                                box-shadow: 0 6px 20px rgba(245, 158, 11, 0.35);">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                    </div>
                    <div>
                        <h2 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.3px;">
                            Study Time Planner
                        </h2>
                        <div style="color: #94a3b8; font-size: 13px; margin-top: 4px;">
                            Intelligent weekly time distribution for <span style="color: #f59e0b; font-weight: 700;">{roadmap['career_name']}</span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; gap: 10px;">
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; font-size: 12px; font-weight: 700;
                                 padding: 6px 14px; border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.3);">
                        {len(learning_path)} Active Milestone{'s' if len(learning_path) != 1 else ''}
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not learning_path:
        st.success("All required skills are marked as known; no study hours need allocating.")
        if st.button("Return to Dashboard", use_container_width=True):
            navigate_to("Dashboard")
        return

    # Interactive Study Hours Input & Metric Summary Cards
    col_input, col_kpi1, col_kpi2 = st.columns([1.4, 1, 1], gap="medium")

    with col_input:
        st.markdown(
            """
            <div style="font-size: 13px; font-weight: 700; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px;">
                Weekly Study Capacity
            </div>
            """,
            unsafe_allow_html=True,
        )
        hours = st.number_input(
            "Available study hours per week",
            min_value=0.0,
            max_value=168.0,
            value=10.0,
            step=0.5,
            label_visibility="collapsed",
        )
        st.caption("Adjust your weekly commitment to recalibrate pace across all remaining skills.")

    hrs_per_skill = round(hours / len(learning_path), 1) if (hours > 0 and learning_path) else 0.0
    daily_pace = round(hours / 7.0, 1) if hours > 0 else 0.0

    with col_kpi1:
        st.markdown(
            f"""
            <div class="metric-card-animated" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Per Skill Pace</div>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
                        <polyline points="2 17 12 22 22 17"></polyline>
                        <polyline points="2 12 12 17 22 12"></polyline>
                    </svg>
                </div>
                <div style="font-size: 26px; color: #38bdf8; font-weight: 800; margin: 4px 0 2px;">{hrs_per_skill} hrs</div>
                <div style="font-size: 11px; color: #64748b;">Average per topic / week</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_kpi2:
        st.markdown(
            f"""
            <div class="metric-card-animated" style="padding: 16px 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 11px; color: #94a3b8; font-weight: 700; text-transform: uppercase;">Daily Effort</div>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                        <path d="M12 14l2 2 4-4"></path>
                    </svg>
                </div>
                <div style="font-size: 26px; color: #34d399; font-weight: 800; margin: 4px 0 2px;">{daily_pace} hrs</div>
                <div style="font-size: 11px; color: #64748b;">Target daily commitment</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    if hours <= 0:
        st.info("Enter a positive number of hours above to generate your customized study schedule.")
    else:
        allocations = plan_study_time(
            hours, [step["skill"] for step in learning_path]
        )

        st.markdown(
            """
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
                <div style="font-size: 16px; font-weight: 700; color: #f8fafc; display: flex; align-items: center; gap: 8px;">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="16" y1="2" x2="16" y2="6"></line>
                        <line x1="8" y1="2" x2="8" y2="6"></line>
                        <line x1="3" y1="10" x2="21" y2="10"></line>
                    </svg>
                    Weekly Schedule Breakdown
                </div>
                <span style="font-size: 12px; color: #94a3b8; font-weight: 500;">
                    Sequential distribution across learning milestones
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # High-End Visual Study Schedule Cards
        schedule_html = ""
        for i, item in enumerate(allocations, 1):
            skill_name = item.get("skill") or item.get("Skill", "Skill")
            allocated_hrs = float(item.get("hours", item.get("Allocated Hours", 0.0)))
            pct_of_total = int((allocated_hrs / hours) * 100) if hours > 0 else 0
            schedule_html += f"""
            <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07);
                        border-radius: 14px; padding: 14px 18px; margin-bottom: 10px; display: flex; align-items: center;
                        justify-content: space-between; gap: 16px; transition: all 0.25s ease;"
                 class="metric-card-animated">
                <div style="display: flex; align-items: center; gap: 14px; flex: 1;">
                    <div style="width: 32px; height: 32px; border-radius: 10px; background: rgba(59, 130, 246, 0.15);
                                border: 1px solid rgba(59, 130, 246, 0.4); display: flex; align-items: center;
                                justify-content: center; font-weight: 800; font-size: 13px; color: #60a5fa;">
                        {i}
                    </div>
                    <div>
                        <div style="font-weight: 700; color: #f8fafc; font-size: 15px;">{skill_name}</div>
                        <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">
                            Priority milestone #{i} in curriculum
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 20px;">
                    <div style="width: 120px; display: none; sm:display: block;">
                        <div style="height: 6px; background: rgba(255,255,255,0.08); border-radius: 4px; overflow: hidden;">
                            <div style="width: {pct_of_total}%; height: 100%; background: linear-gradient(90deg, #0ea5e9, #38bdf8);"></div>
                        </div>
                    </div>
                    <div style="text-align: right; min-width: 90px;">
                        <div style="font-size: 18px; font-weight: 800; color: #f59e0b;">
                            {allocated_hrs:.1f} <span style="font-size: 12px; font-weight: 600; color: #94a3b8;">hrs</span>
                        </div>
                        <div style="font-size: 11px; color: #64748b;">{pct_of_total}% of week</div>
                    </div>
                </div>
            </div>
            """
        st.markdown(schedule_html, unsafe_allow_html=True)
        st.caption("Hours are divided equally across remaining skills, with rounding remainder allotted to final milestones.")

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    if st.button("Continue to Dashboard", type="primary", use_container_width=True):
        navigate_to("Dashboard")
