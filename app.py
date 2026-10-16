"""Streamlit entry point for the Personalized Education Path Generator."""

import sqlite3

import streamlit as st

import ui.ai_tutor_ui
import ui.auth_ui
import ui.career_path_ui
import ui.career_ui
import ui.dashboard
import ui.planner_ui
import ui.roadmap_ui
from database.db import get_student
from database.seed import seed_db
from ui.theme import apply_theme


def _sync_navigation_selection():
    """Treat a sidebar selection as the current guided workflow step."""
    st.session_state["workflow_step"] = st.session_state["workflow_navigation"]


def _logout():
    """Clear session authentication state and return to login screen."""
    st.session_state.pop("authenticated_user", None)
    st.session_state.pop("student_id", None)
    st.session_state.pop("workflow_step", None)
    st.session_state.pop("workflow_navigation", None)
    st.rerun()


def main():
    """Initialize local data and render the selected application screen."""
    st.set_page_config(page_title="Education Path Generator", layout="wide")
    try:
        seed_db()
    except Exception as error:
        st.error(
            f"The local database could not be initialized: {error}"
        )
        st.stop()

    apply_theme()

    # Sync latest code changes to C:\Backup\patelsoham1304-automatic-telegram
    try:
        if not st.session_state.get("_backup_synced_all"):
            import sync_all
            sync_all.sync_all()
            st.session_state["_backup_synced_all"] = True
    except Exception:
        pass

    # Authentication Gate: Check if user is logged in
    auth_user = st.session_state.get("authenticated_user")
    student_id = st.session_state.get("student_id")

    # If student_id exists in session from prior direct selection but no auth_user, sync them if possible
    if not auth_user and student_id:
        try:
            student = get_student(student_id)
            if student:
                auth_user = {
                    "id": student["id"],
                    "name": student["name"],
                    "email": student["email"],
                }
                st.session_state["authenticated_user"] = auth_user
        except Exception:
            pass

    if not auth_user:
        # User not logged in, render the login/register screen
        ui.auth_ui.render_auth_screen()
        return

    # Ensure student_id is set to the logged in user
    st.session_state["student_id"] = auth_user["id"]

    steps = [
        "Resume Career Path",
        "Select Career",
        "Skill Gap & Roadmap",
        "Study Planner",
        "Dashboard",
    ]
    current_step = st.session_state.get("workflow_step", steps[0])
    step_index = steps.index(current_step) if current_step in steps else 0
    total_steps = len(steps)
    progress_pct = int(((step_index + 1) / total_steps) * 100)

    # Sidebar Header with Avatar (Visual-only)
    st.sidebar.markdown(
        """
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;">
            <div class="floating-avatar" style="width:42px;height:42px;border-radius:12px;background:linear-gradient(135deg,#4f46e5,#6366f1);
                        display:grid;place-items:center;color:#ffffff;
                        box-shadow:0 0 20px rgba(99,102,241,0.4);">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ffffff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                    <path d="M6 12v5c3 3 9 3 12 0v-5"></path>
                </svg>
            </div>
            <div>
                <div style="font-weight:800;font-size:16.5px;color:#ffffff;line-height:1.2;">PathFinder AI</div>
                <div style="font-size:11px;color:#94a3b8;display:flex;align-items:center;margin-top:2px;">
                    <span class="live-pulse-dot"></span>Interactive Learning
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Logged-in user badge and Logout button
    user_email_display = auth_user.get("email") or "Active Student"
    name_initials = "".join([part[0] for part in auth_user["name"].split()[:2]]).upper()
    st.sidebar.markdown(
        f"""
        <div style="padding: 12px 14px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.07);
                    border-radius: 14px; margin-bottom: 12px; display: flex; align-items: center; gap: 12px;">
            <div style="width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, #4f46e5, #06b6d4);
                        display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: #ffffff;">
                {name_initials}
            </div>
            <div style="overflow: hidden;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 13px; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{auth_user['name']}</div>
                <div style="font-size: 11px; color: #67e8f9; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{user_email_display}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Sign Out", use_container_width=True):
        _logout()

    st.sidebar.caption(
        f"Learning journey · Step {step_index + 1} of {total_steps}"
    )
    if st.session_state.get("workflow_navigation") != current_step:
        st.session_state["workflow_navigation"] = current_step
    selected_step = st.sidebar.radio(
        "Navigation",
        steps,
        index=step_index,
        key="workflow_navigation",
        on_change=_sync_navigation_selection,
    )
    st.session_state.workflow_step = selected_step
    st.sidebar.caption("Student profile active")

    # Circular progress indicator at bottom of sidebar (Visual-only)
    st.sidebar.markdown(
        f"""
        <div style="margin-top:24px;padding:16px;background:linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));border:1px solid rgba(255,255,255,0.06);
                    border-radius:18px;text-align:center;box-shadow:0 8px 24px rgba(0,0,0,0.25);transition:transform 0.3s ease;">
            <div style="position:relative;width:80px;height:80px;margin:0 auto 8px auto;display:grid;place-items:center;">
                <svg width="80" height="80" viewBox="0 0 36 36" style="transform:rotate(-90deg);filter:drop-shadow(0 0 6px rgba(99,102,241,0.35));">
                    <path stroke="rgba(255,255,255,0.06)" stroke-width="3" fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <!-- Cyan Arc -->
                    <path stroke="#06b6d4" stroke-dasharray="60, 100" stroke-width="3.2" stroke-linecap="round" fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                    <!-- Indigo/Violet Active Arc -->
                    <path stroke="#6366f1" stroke-dasharray="{progress_pct * 0.4}, 100" stroke-width="3.8" stroke-linecap="round" fill="none"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div class="floating-avatar" style="position:absolute;width:48px;height:48px;border-radius:50%;background:#0d121f;display:grid;place-items:center;box-shadow:inset 0 0 10px rgba(0,0,0,0.5), 0 0 12px rgba(99,102,241,0.25);">
                    <span style="font-size:20px;">🚀</span>
                </div>
            </div>
            <div style="font-size:13px;font-weight:700;color:#f8fafc;letter-spacing:0.3px;">Step {step_index + 1} of {total_steps}</div>
            <div style="font-size:11px;color:#38bdf8;margin-top:2px;font-weight:600;">{progress_pct}% Completed</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    screens = {
        "Resume Career Path": ui.career_path_ui.render,
        "Select Career": ui.career_ui.render,
        "Skill Gap & Roadmap": ui.roadmap_ui.render,
        "Study Planner": ui.planner_ui.render,
        "Dashboard": ui.dashboard.render,
    }
    content_column, tutor_column = st.columns([0.72, 0.28], gap="large")
    with content_column:
        screens[selected_step]()
    with tutor_column:
        ui.ai_tutor_ui.render()


if __name__ == "__main__":
    main()
