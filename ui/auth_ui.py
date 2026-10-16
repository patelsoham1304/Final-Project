"""Modern, animated, professional Authentication UI screen for student Login and Register."""

import sqlite3
import streamlit as st
from modules.auth import authenticate_user, register_user


def render_auth_screen():
    """Render a stunning, animated hero and eye-pleasing authentication experience."""
    # Top hero section with soft glowing icon & modern typography
    st.markdown(
        """
        <div style="text-align: center; padding: 25px 0 16px 0;">
            <div style="display: inline-flex; align-items: center; justify-content: center;
                        width: 74px; height: 74px; border-radius: 22px;
                        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 50%, #06b6d4 100%);
                        box-shadow: 0 10px 30px rgba(99, 102, 241, 0.35); font-size: 34px; margin-bottom: 16px;"
                 class="floating-avatar">
                🎓
            </div>
            <h1 style="font-size: 2.7rem; font-weight: 800; line-height: 1.15; margin-bottom: 12px; letter-spacing: -0.5px; color: #f8fafc;">
                Welcome to <span class="shimmer-text">PathFinder AI</span>
            </h1>
            <p style="color: #94a3b8; font-size: 1.05rem; max-width: 640px; margin: 0 auto 20px auto; line-height: 1.6;">
                Intelligent education path generator that analyzes your skills, builds dynamic DAG roadmaps, and provides continuous AI mentorship.
            </p>
            <div style="display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; margin-bottom: 24px;">
                <span style="background: rgba(99, 102, 241, 0.12); border: 1px solid rgba(99, 102, 241, 0.25); color: #a5b4fc;
                             padding: 6px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 600;">
                    🗺️ Dynamic Visual Roadmaps
                </span>
                <span style="background: rgba(6, 182, 212, 0.12); border: 1px solid rgba(6, 182, 212, 0.25); color: #67e8f9;
                             padding: 6px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 600;">
                    ⚡ Smart Resume Skill Matcher
                </span>
                <span style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.25); color: #6ee7b7;
                             padding: 6px 14px; border-radius: 999px; font-size: 12.5px; font-weight: 600;">
                    🤖 24/7 AI Learning Tutor
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered glassmorphic column layout
    col_left, col_center, col_right = st.columns([1, 2.3, 1])
    with col_center:
        st.markdown(
            """
            <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(6, 182, 212, 0.05) 100%);
                        border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 16px;
                        padding: 14px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 20px;">🚀</span>
                    <div>
                        <div style="font-weight: 700; color: #f8fafc; font-size: 13.5px;">Student Career Portal</div>
                        <div style="color: #94a3b8; font-size: 11.5px;">Log in or create a free account to begin your journey</div>
                    </div>
                </div>
                <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; font-size: 11px; font-weight: 700;
                             padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3);">
                    ● 100% Free
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Free Account"])

        with tab_login:
            st.markdown(
                """
                <div style="margin: 10px 0 14px 0;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">Welcome back! 👋</div>
                    <div style="font-size: 0.88rem; color: #94a3b8;">Enter your credentials to access your roadmaps and progress.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email address", placeholder="student@example.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                submit_login = st.form_submit_button("🚀 Sign In to Dashboard", type="primary", use_container_width=True)

            if submit_login:
                try:
                    user = authenticate_user(email, password)
                    st.session_state["student_id"] = user["id"]
                    st.session_state["authenticated_user"] = {
                        "id": user["id"],
                        "name": user["name"],
                        "email": user["email"],
                    }
                    st.session_state["workflow_step"] = "Resume Career Path"
                    st.session_state["workflow_navigation"] = "Resume Career Path"
                    st.toast(f"Welcome back, {user['name']}! 🎉", icon="🎓")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))
                except sqlite3.Error as err:
                    st.error(f"Database error during login: {err}")

        with tab_register:
            st.markdown(
                """
                <div style="margin: 10px 0 14px 0;">
                    <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc;">Start Your Path in 30 Seconds 🌟</div>
                    <div style="font-size: 0.88rem; color: #94a3b8;">Create your student profile and get personalized career guidance.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.form("register_form", clear_on_submit=False):
                name = st.text_input("Full Name", placeholder="e.g. Rahul Sharma")
                reg_email = st.text_input("Email address", placeholder="student@example.com")
                reg_password = st.text_input("Password (min. 6 characters)", type="password", placeholder="••••••••")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="••••••••")
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)
                submit_register = st.form_submit_button("✨ Create My Account", type="primary", use_container_width=True)

            if submit_register:
                try:
                    student_id = register_user(name, reg_email, reg_password, confirm_password)
                    st.session_state["student_id"] = student_id
                    st.session_state["authenticated_user"] = {
                        "id": student_id,
                        "name": name.strip(),
                        "email": reg_email.strip().lower(),
                    }
                    st.session_state["workflow_step"] = "Resume Career Path"
                    st.session_state["workflow_navigation"] = "Resume Career Path"
                    st.toast("Account created successfully! Welcome! 🚀", icon="🌟")
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))
                except sqlite3.IntegrityError:
                    st.error("That email is already registered. Please sign in.")
                except sqlite3.Error as err:
                    st.error(f"Database error during registration: {err}")

    # Bottom animated highlights section for students
    st.markdown(
        """
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-top: 36px; padding: 0 10px;">
            <div style="background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
                        border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; transition: transform 0.3s ease;">
                <div style="font-size: 24px; margin-bottom: 8px;">🗺️</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 15px; margin-bottom: 4px;">Interactive Career Maps</div>
                <div style="color: #94a3b8; font-size: 12.5px; line-height: 1.5;">Structured dependency graphs showing exactly what to learn and in what order.</div>
            </div>
            <div style="background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
                        border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; transition: transform 0.3s ease;">
                <div style="font-size: 24px; margin-bottom: 8px;">🧠</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 15px; margin-bottom: 4px;">Smart AI Learning Tutor</div>
                <div style="color: #94a3b8; font-size: 12.5px; line-height: 1.5;">Get immediate explanations, doubt clearances, and real-world project recommendations.</div>
            </div>
            <div style="background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
                        border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 20px; transition: transform 0.3s ease;">
                <div style="font-size: 24px; margin-bottom: 8px;">⏱️</div>
                <div style="font-weight: 700; color: #f8fafc; font-size: 15px; margin-bottom: 4px;">Personalized Study Planner</div>
                <div style="color: #94a3b8; font-size: 12.5px; line-height: 1.5;">Distribute your available weekly hours intelligently across missing skill gaps.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

