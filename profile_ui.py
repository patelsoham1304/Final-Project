"""Profile selection and creation screen."""

import sqlite3

import streamlit as st

from modules.profile import (
    create_student_profile,
    list_student_profiles,
    update_student_profile,
)


def render():
    """Render the active-profile selector and student profile form."""
    st.header("Student Profile")
    try:
        profiles = list_student_profiles()
    except sqlite3.Error:
        st.error("Student profiles could not be loaded. Check the local database.")
        return

    if profiles:
        active_id = st.session_state.get("student_id")
        selected_profile = next(
            (p for p in profiles if p["id"] == active_id),
            profiles[0],
        )
        st.session_state.student_id = selected_profile["id"]

        # Display active student info directly instead of dropdown list
        st.markdown(
            f"""
            <div style="background: rgba(30, 41, 59, 0.5); border: 1.5px solid rgba(245, 158, 11, 0.4); 
                        border-radius: 12px; padding: 14px 18px; margin-bottom: 18px; display: flex; 
                        align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, #f59e0b, #d97706);
                                display: grid; place-items: center; color: #0b1024; font-weight: 800; font-size: 20px;">
                        {selected_profile['name'][0].upper()}
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #f59e0b; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px;">Active Student Profile</div>
                        <div style="font-size: 18px; font-weight: 800; color: #f8fafc;">{selected_profile['name']}</div>
                        <div style="font-size: 12px; color: #94a3b8;">{selected_profile['email'] if selected_profile['email'] else 'No email attached'}</div>
                    </div>
                </div>
                <div style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.35); padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700;">
                    ● Active
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.session_state.pop("student_id", None)
        st.info("No active student profile found. Please register or create one below.")

    with st.form("profile_form", clear_on_submit=True):
        name = st.text_input("Full name")
        email = st.text_input("Email (optional)")
        submitted = st.form_submit_button("Create student profile")
    if submitted:
        try:
            student_id = create_student_profile(name, email or None)
            st.session_state.student_id = student_id
            st.success("Student profile saved.")
            st.rerun()
        except ValueError as error:
            st.error(str(error))
        except sqlite3.IntegrityError:
            st.error("That email is already used by another student profile.")
        except sqlite3.Error:
            st.error("The profile could not be saved. Check the local database.")

    active_profile = next(
        (
            profile
            for profile in profiles
            if profile["id"] == st.session_state.get("student_id")
        ),
        None,
    )
    if active_profile:
        if st.button("Continue to career and skill assessment"):
            st.session_state.workflow_step = "Select Career"
            st.rerun()

        with st.expander("Edit active student profile"):
            with st.form("edit_profile_form"):
                edited_name = st.text_input(
                    "Full name", value=active_profile["name"]
                )
                edited_email = st.text_input(
                    "Email (optional)", value=active_profile["email"] or ""
                )
                update_submitted = st.form_submit_button("Save profile changes")
            if update_submitted:
                try:
                    update_student_profile(
                        active_profile["id"], edited_name, edited_email or None
                    )
                    st.success("Profile updated.")
                    st.rerun()
                except ValueError as error:
                    st.error(str(error))
                except sqlite3.IntegrityError:
                    st.error("That email is already used by another student profile.")
                except sqlite3.Error:
                    st.error("The profile could not be updated.")
