"""Shared navigation for the guided learning workflow."""

import streamlit as st


def navigate_to(step: str) -> None:
    """Set the next screen; the app syncs the sidebar widget before rendering."""
    st.session_state["workflow_step"] = step
    st.rerun()
