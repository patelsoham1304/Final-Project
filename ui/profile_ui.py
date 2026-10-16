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
        previous_id = st.session_state.get("student_id")
        selected_index = next(
            (i for i, profile in enumerate(profiles) if profile["id"] == previous_id),
            0,
        )
        profile_by_id = {profile["id"]: profile for profile in profiles}
        selected_id = st.selectbox(
            "Active student profile",
            list(profile_by_id),
            index=selected_index,
            format_func=lambda profile_id: profile_by_id[profile_id]["name"],
            key="active_profile_selector",
        )
        selected_profile = profile_by_id[selected_id]
        st.session_state.student_id = selected_profile["id"]
        st.caption(
            f"Working as {selected_profile['name']}"
            + (f" ({selected_profile['email']})" if selected_profile["email"] else "")
        )
    else:
        st.session_state.pop("student_id", None)
        st.info("Create a student profile to begin.")

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
