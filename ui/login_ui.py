"""Landing and authentication screen for AI PathFinder."""

import sqlite3
import streamlit as st

from database.db import get_connection
from modules.profile import create_student_profile, list_student_profiles


def render_login(on_login_success):
    """Render the AI PathFinder hero section, login, and registration forms."""
    # Top Hero Branding
    st.markdown(
        """
        <div style="text-align: center; padding: 25px 0 15px 0;">
            <div style="font-size: 50px; line-height: 1; margin-bottom: 12px; filter: drop-shadow(0 0 20px rgba(245, 158, 11, 0.4));">
                🚀
            </div>
            <h1 style="color: #ffffff; font-size: 2.3rem; font-weight: 800; margin-bottom: 8px; letter-spacing: -0.5px;">
                Shape Your Future with <span style="background: linear-gradient(135deg, #f59e0b, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">AI PathFinder</span>
            </h1>
            <p style="color: #94a3b8; font-size: 0.95rem; max-width: 600px; margin: 0 auto 18px auto; line-height: 1.5;">
                Generate customized career roadmaps, discover your skill gaps in real-time, and get 24/7 personalized AI mentorship.
            </p>
            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 25px;">
                <span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: #cbd5e1;">🎯 Smart Career Roadmaps</span>
                <span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: #cbd5e1;">⚡ Interactive Skill Gap Analysis</span>
                <span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: #cbd5e1;">🤖 24/7 AI Learning Tutor</span>
                <span style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); padding: 5px 12px; border-radius: 20px; font-size: 0.75rem; color: #cbd5e1;">📊 Personalized Weekly Study Plans</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Portal Card
    _, center_col, _ = st.columns([0.18, 0.64, 0.18])

    with center_col:
        st.markdown(
            """
            <div style="background: rgba(30, 41, 59, 0.45); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; padding: 14px 20px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 24px;">🎓</span>
                    <div>
                        <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">Student Career Portal</div>
                        <div style="color: #94a3b8; font-size: 0.8rem;">Log in with your email or register to begin your assessment</div>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 600;">● Free Access</span>
                    <span style="background: rgba(6, 182, 212, 0.2); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.4); padding: 3px 8px; border-radius: 6px; font-size: 0.7rem; font-weight: 600;">6 Tech Careers</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔑 Student Log In", "✨ New Student Registration"])

        with tab_login:
            st.markdown(
                """
                <div style="margin-top: 10px; margin-bottom: 12px;">
                    <h3 style="margin: 0; font-size: 1.15rem; color: #f8fafc;">Welcome back! 👋</h3>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">Enter your credentials to continue your learning journey.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("login_form"):
                email = st.text_input("Email address", placeholder="student@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("🚀 Log In to Dashboard", use_container_width=True)

            if submitted:
                clean_email = email.strip()
                if not clean_email:
                    st.error("Please enter your email address.")
                else:
                    try:
                        profiles = list_student_profiles()
                        matched = next((p for p in profiles if (p.get("email") or "").lower() == clean_email.lower()), None)

                        if matched:
                            st.session_state["student_id"] = matched["id"]
                            st.session_state["user_logged_in"] = True
                            st.session_state["user_email"] = matched.get("email")
                            st.session_state["user_name"] = matched.get("name")
                            st.success(f"Welcome back, {matched['name']}!")
                            on_login_success()
                            st.rerun()
                        else:
                            # Auto-create if not found or student doesn't exist yet
                            display_name = clean_email.split("@")[0].replace(".", " ").title()
                            student_id = create_student_profile(display_name, clean_email)
                            st.session_state["student_id"] = student_id
                            st.session_state["user_logged_in"] = True
                            st.session_state["user_email"] = clean_email
                            st.session_state["user_name"] = display_name
                            st.success(f"Welcome {display_name}! Profile created.")
                            on_login_success()
                            st.rerun()
                    except Exception as err:
                        st.error(f"Login failed: {err}")

            # Quick guest access button
            if st.button("Continue as Guest Student 👤", use_container_width=True):
                try:
                    profiles = list_student_profiles()
                    if profiles:
                        st.session_state["student_id"] = profiles[0]["id"]
                        st.session_state["user_name"] = profiles[0]["name"]
                    else:
                        student_id = create_student_profile("Demo Student", "student@example.com")
                        st.session_state["student_id"] = student_id
                        st.session_state["user_name"] = "Demo Student"
                    st.session_state["user_logged_in"] = True
                    on_login_success()
                    st.rerun()
                except Exception as err:
                    st.error(f"Guest login failed: {err}")

        with tab_register:
            st.markdown(
                """
                <div style="margin-top: 10px; margin-bottom: 12px;">
                    <h3 style="margin: 0; font-size: 1.15rem; color: #f8fafc;">Create your profile 🎯</h3>
                    <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 0.85rem;">Register to save your personalized roadmaps and progress.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Alex Johnson")
                reg_email = st.text_input("Email Address", placeholder="alex@example.com")
                reg_password = st.text_input("Create Password", type="password", placeholder="••••••••")
                reg_submit = st.form_submit_button("✨ Register & Start Learning", use_container_width=True)

            if reg_submit:
                if not reg_name.strip():
                    st.error("Please provide your full name.")
                elif not reg_email.strip():
                    st.error("Please provide a valid email.")
                else:
                    try:
                        student_id = create_student_profile(reg_name.strip(), reg_email.strip())
                        st.session_state["student_id"] = student_id
                        st.session_state["user_logged_in"] = True
                        st.session_state["user_name"] = reg_name.strip()
                        st.session_state["user_email"] = reg_email.strip()
                        st.success(f"Account created successfully for {reg_name}!")
                        on_login_success()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("An account with this email already exists. Please log in.")
                    except Exception as err:
                        st.error(f"Registration failed: {err}")
