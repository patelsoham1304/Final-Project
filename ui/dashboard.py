"""Shared student career and skill-assessment dashboard."""

import sqlite3
import streamlit as st

from database.db import (
    get_current_roadmap,
    get_resources_for_skill,
    get_skills_for_career,
    get_student,
)
from modules.progress import calculate_overall_progress, summarize_required_skills
from modules.recommendation import get_next_recommended_skill
from modules.roadmap import generate_roadmap
from modules.skill_assessment import get_assessments
from ui.navigation import navigate_to


def render():
    """Show the active student, career assessment, and learning suggestions with sleek professional UI."""
    student_id = st.session_state.get("student_id")
    if not student_id:
        st.warning("Please sign in first.")
        return

    try:
        student = get_student(student_id)
        if student is None:
            st.warning("The selected student profile no longer exists.")
            return
        roadmap = get_current_roadmap(student_id)
        assessments = get_assessments(student_id)
        required = (
            get_skills_for_career(roadmap["career_id"]) if roadmap is not None else []
        )
    except sqlite3.Error:
        st.error("The dashboard could not load data from the local database.")
        return

    # Student Name Initials for Avatar
    name_parts = student["name"].strip().split()
    initials = (name_parts[0][0] + (name_parts[-1][0] if len(name_parts) > 1 else "")).upper()
    email_text = student["email"] or "No email provided"

    # Executive Profile Header Card (Clean, SVG-based, Professional)
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, rgba(30, 41, 79, 0.5) 0%, rgba(15, 23, 42, 0.7) 100%);
                    border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 18px; padding: 22px 26px;
                    margin-bottom: 24px; box-shadow: 0 12px 32px rgba(0, 0, 0, 0.35); position: relative; overflow: hidden;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
                <div style="display: flex; align-items: center; gap: 18px;">
                    <div style="width: 58px; height: 58px; border-radius: 16px;
                                background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
                                border: 2px solid rgba(255, 255, 255, 0.2); display: flex; align-items: center;
                                justify-content: center; font-weight: 800; font-size: 22px; color: #ffffff;
                                box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4);">
                        {initials}
                    </div>
                    <div>
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <h2 style="margin: 0; font-size: 1.6rem; font-weight: 800; color: #f8fafc; letter-spacing: -0.3px;">
                                {student['name']}
                            </h2>
                            <span style="display: inline-flex; align-items: center; gap: 5px; background: rgba(16, 185, 129, 0.15);
                                         color: #34d399; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 20px;
                                         border: 1px solid rgba(16, 185, 129, 0.35);">
                                <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981;"></span> Verified Learner
                            </span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 16px; margin-top: 6px; color: #94a3b8; font-size: 13px;">
                            <span style="display: flex; align-items: center; gap: 6px;">
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38bdf8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                                    <polyline points="22,6 12,13 2,6"></polyline>
                                </svg>
                                {email_text}
                            </span>
                        </div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="text-align: right; border-right: 1px solid rgba(255, 255, 255, 0.1); padding-right: 14px;">
                        <div style="font-size: 11px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Active Path</div>
                        <div style="font-size: 14px; font-weight: 700; color: #f59e0b;">
                            {roadmap['career_name'] if roadmap else 'Not Selected'}
                        </div>
                    </div>
                    <div style="padding-left: 4px;">
                        <span style="font-size: 12px; background: rgba(255, 255, 255, 0.06); padding: 6px 12px; border-radius: 8px;
                                     border: 1px solid rgba(255, 255, 255, 0.1); color: #cbd5e1; font-weight: 600;">
                            Account Active
                        </span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Gamification & Learning Streak Widget
    from modules.gamification import get_student_gamification_data
    game_data = get_student_gamification_data(student_id)

    streak_days = game_data["streak"]
    user_xp = game_data["xp"]
    user_level = game_data["level"]
    lvl_pct = game_data["level_progress"]
    badges = game_data["badges"]

    badge_chips = "".join(
        f'<div style="display:flex;align-items:center;gap:8px;padding:6px 12px;border-radius:10px;'
        f'background:{"rgba(14,165,233,0.18)" if b["unlocked"] else "rgba(148,163,184,0.06)"};'
        f'border:1px solid {"#38bdf8" if b["unlocked"] else "rgba(148,163,184,0.2)"};'
        f'opacity:{"1" if b["unlocked"] else "0.45"};">'
        f'<span style="font-size:18px;">{b["icon"]}</span>'
        f'<div><div style="font-size:12px;font-weight:700;color:{"#ffffff" if b["unlocked"] else "#94a3b8"};">{b["name"]}</div>'
        f'<div style="font-size:10px;color:{"#7dd3fc" if b["unlocked"] else "#64748b"};">{b["desc"]}</div></div></div>'
        for b in badges
    )

    st.markdown(
        f'<div style="background:linear-gradient(135deg, rgba(14,165,233,0.12), rgba(99,102,241,0.12));'
        f'border:1px solid rgba(56,189,248,0.25);border-radius:16px;padding:16px 20px;margin-bottom:20px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px;">'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="font-size:26px;background:rgba(239,68,68,0.15);padding:6px 10px;border-radius:12px;border:1px solid rgba(239,68,68,0.3);">🔥</div>'
        f'<div><div style="font-size:11px;color:#f87171;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;">Learning Streak</div>'
        f'<div style="font-size:20px;font-weight:900;color:#ffffff;">{streak_days} Day{"s" if streak_days != 1 else ""} Active</div></div></div>'
        f'<div style="display:flex;align-items:center;gap:16px;">'
        f'<div><div style="font-size:11px;color:#38bdf8;font-weight:800;text-transform:uppercase;letter-spacing:0.5px;text-align:right;">Student Rank</div>'
        f'<div style="font-size:18px;font-weight:900;color:#f8fafc;text-align:right;">Level {user_level} ({user_xp} XP)</div></div>'
        f'<div style="width:42px;height:42px;border-radius:50%;background:linear-gradient(135deg,#0284c7,#6366f1);'
        f'display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:800;color:#ffffff;box-shadow:0 0 15px rgba(2,132,199,0.5);">🏆</div></div></div>'
        f'<div style="background:rgba(0,0,0,0.3);height:8px;border-radius:4px;overflow:hidden;margin-bottom:12px;">'
        f'<div style="background:linear-gradient(90deg,#0284c7,#38bdf8);height:100%;width:{lvl_pct}%;"></div></div>'
        f'<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-top:8px;">{badge_chips}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if roadmap is None:
        st.info("Choose a target career and assess your current skills to get started.")
        if st.button("Choose a career"):
            navigate_to("Select Career")
        return
    if not required:
        st.warning("This career has no mapped skills yet.")
        return

    assessed_by_id = {item["skill_id"]: item for item in assessments}
    required_progress = summarize_required_skills(
        [dict(skill) for skill in required],
        [dict(item) for item in assessments],
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

    # 3-Column Sleek Metric Cards with Crisp Vector Graphics (No Emojis)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card-animated">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:12px;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Skill Coverage</div>
                    <div style="width:30px;height:30px;border-radius:8px;background:rgba(52,211,153,0.15);display:flex;align-items:center;justify-content:center;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <circle cx="12" cy="12" r="6"></circle>
                            <circle cx="12" cy="12" r="2"></circle>
                        </svg>
                    </div>
                </div>
                <div style="font-size:30px;color:#34d399;font-weight:800;margin:6px 0 2px;letter-spacing:-0.5px;">{overall:.0f}%</div>
                <div style="font-size:12px;color:#64748b;">Overall career readiness</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card-animated">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:12px;color:#94a3b8;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Remaining Milestones</div>
                    <div style="width:30px;height:30px;border-radius:8px;background:rgba(96,165,250,0.15);display:flex;align-items:center;justify-content:center;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
                        </svg>
                    </div>
                </div>
                <div style="font-size:30px;color:#60a5fa;font-weight:800;margin:6px 0 2px;letter-spacing:-0.5px;">{len(incomplete)}</div>
                <div style="font-size:12px;color:#64748b;">Skills pending mastery</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    names = [skill["name"] for skill in required]
    current = {
        skill["name"]: int(
            skill["id"] in assessed_by_id
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
    focus = (
        recommendation["skill"]
        if recommendation
        else "All skills mastered"
    )

    with c3:
        st.markdown(
            f"""
            <div class="metric-card-animated" style="border-color:rgba(245,158,11,0.4);background:linear-gradient(135deg,rgba(245,158,11,0.08),rgba(217,119,6,0.02));">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-size:12px;color:#f59e0b;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">Priority Focus</div>
                    <div style="width:30px;height:30px;border-radius:8px;background:rgba(245,158,11,0.2);display:flex;align-items:center;justify-content:center;">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                    </div>
                </div>
                <div style="font-size:24px;color:#ffffff;font-weight:800;margin:6px 0 2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{focus}</div>
                <div style="font-size:12px;color:#fcd34d;">Recommended next step</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.progress(overall / 100)

    # Known vs Remaining Interactive Chip Lists with Vector Icons
    left, right = st.columns(2)
    with left:
        st.markdown(
            """
            <div style="font-size:15px;font-weight:700;color:#f8fafc;margin-bottom:8px;display:flex;align-items:center;gap:8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Mastered Skills
            </div>
            """,
            unsafe_allow_html=True,
        )
        if completed:
            known_chips = "".join(
                f'<span class="skill-chip known"><span style="color:#10b981;font-weight:700;">✓</span> {name}</span>'
                for name in completed
            )
            st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{known_chips}</div>', unsafe_allow_html=True)
        else:
            st.caption("No mastered skills registered yet")
    with right:
        st.markdown(
            """
            <div style="font-size:15px;font-weight:700;color:#f8fafc;margin-bottom:8px;display:flex;align-items:center;gap:8px;">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                </svg>
                Target Learning Queue
            </div>
            """,
            unsafe_allow_html=True,
        )
        if incomplete:
            rem_chips = "".join(
                f'<span class="skill-chip missing"><span style="color:#60a5fa;font-weight:700;">•</span> {name}</span>'
                for name in incomplete
            )
            st.markdown(f'<div style="display:flex;flex-wrap:wrap;">{rem_chips}</div>', unsafe_allow_html=True)
        else:
            st.caption("All curriculum skills completed")

    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:16px;font-weight:700;color:#f8fafc;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="8" y1="6" x2="21" y2="6"></line>
                <line x1="8" y1="12" x2="21" y2="12"></line>
                <line x1="8" y1="18" x2="21" y2="18"></line>
                <line x1="3" y1="6" x2="3.01" y2="6"></line>
                <line x1="3" y1="12" x2="3.01" y2="12"></line>
                <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
            Roadmap Sequence Preview
        </div>
        """,
        unsafe_allow_html=True,
    )
    if learning_path:
        preview_items = "".join(
            f"""
            <div style="display:flex;align-items:center;gap:14px;padding:12px 16px;background:rgba(255,255,255,0.03);
                        border:1px solid rgba(255,255,255,0.07);border-radius:12px;margin-bottom:8px;transition:all 0.2s ease;">
                <div style="width:28px;height:28px;border-radius:8px;background:rgba(59,130,246,0.15);border:1px solid #3b82f6;
                            display:grid;place-items:center;font-size:12px;font-weight:800;color:#60a5fa;">
                    {step['step']}
                </div>
                <div style="font-weight:600;color:#f1f5f9;font-size:14px;">Master {step['skill']}</div>
                <div style="margin-left:auto;font-size:12px;color:#94a3b8;font-weight:500;">Step {step['step']} of {len(learning_path)}</div>
            </div>
            """
            for step in learning_path[:5]
        )
        st.markdown(preview_items, unsafe_allow_html=True)
    else:
        st.success("Your roadmap is complete.")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:16px;font-weight:700;color:#f8fafc;margin-bottom:10px;">
            Assessment Records
        </div>
        """,
        unsafe_allow_html=True,
    )
    required_by_id = {skill["id"]: skill["name"] for skill in required}
    relevant_assessments = [
        item for item in assessments if item["skill_id"] in required_by_id
    ]
    if relevant_assessments:
        recent = [
            {
                "Skill": required_by_id[item["skill_id"]],
                "Status": "Mastered",
                "Assessed Date": item["updated_at"],
            }
            for item in relevant_assessments[:10]
        ]
        st.dataframe(recent, hide_index=True, width="stretch")
    else:
        st.info("Your career skill assessment will appear here after selecting a career.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    roadmap_button, planner_button = st.columns(2)
    with roadmap_button:
        if st.button("View Full Learning Roadmap", use_container_width=True):
            navigate_to("Skill Gap & Roadmap")
    with planner_button:
        if st.button("Open Weekly Study Planner", use_container_width=True):
            navigate_to("Study Planner")
