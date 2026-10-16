"""Upload-first resume review and professional export screen."""

import hashlib
import sqlite3

import streamlit as st

from database.db import get_careers, get_skills_for_career
from modules.resume_upload import (
    MAX_RESUME_BYTES,
    extract_resume_text,
    review_resume,
)


def render():
    """Upload, review, edit, and download an existing resume."""
    st.header("Resume Review")
    st.write(
        "Upload your current resume to get practical, career-specific feedback "
        "and clear suggestions for improving it."
    )
    st.info(
        "Your file is processed for this session only and is not saved to the "
        "database. The review will not invent experience, skills, or qualifications."
    )

    try:
        careers = get_careers()
    except sqlite3.Error:
        st.error("Career options could not be loaded from the local database.")
        return
    if not careers:
        st.warning("Career options are not available yet.")
        return

    career_by_id = {career["id"]: career for career in careers}
    career_id = st.selectbox(
        "What role are you targeting?",
        list(career_by_id),
        format_func=lambda item_id: career_by_id[item_id]["name"],
        key="resume_review_target_career",
    )
    uploaded_file = st.file_uploader(
        "Upload your existing resume",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX, or UTF-8 TXT; maximum 10 MB. Scanned/image-only PDFs need OCR.",
        key="resume_upload_file",
    )
    if uploaded_file is None:
        st.caption(
            "After uploading, choose **Review my resume** to see feedback and "
            "suggestions tailored to your target career."
        )
        return
    if uploaded_file.size > MAX_RESUME_BYTES:
        st.error("Resume files must be 10 MB or smaller.")
        return

    content = uploaded_file.getvalue()
    upload_key = hashlib.sha256(content).hexdigest()
    result_key = f"{upload_key}:{career_id}"
    if st.button("Review my resume", type="primary", key="analyze_resume_upload"):
        try:
            original_text = extract_resume_text(uploaded_file.name, content)
            career_skills = get_skills_for_career(career_id)
            st.session_state["resume_upload_result"] = {
                "key": result_key,
                "text": original_text,
                "review": review_resume(
                    original_text,
                    [skill["name"] for skill in career_skills],
                ),
            }
        except ValueError as error:
            st.session_state.pop("resume_upload_result", None)
            st.error(str(error))
            return
        except sqlite3.Error:
            st.error("Target-role skills could not be loaded for the review.")
            return

    result = st.session_state.get("resume_upload_result")
    if not result or result["key"] != result_key:
        st.caption("Select **Review my resume** to analyze the uploaded document.")
        return

    resume_review = result["review"]
    st.subheader("Your resume review")
    st.caption(f"Target role: {career_by_id[career_id]['name']}")
    first, second, third = st.columns(3)
    first.metric("Words", resume_review["word_count"])
    second.metric("Sections found", len(resume_review["sections"]))
    third.metric("Action bullets", resume_review["bullet_count"])

    if resume_review["sections"]:
        st.write("**Sections detected:** " + ", ".join(resume_review["sections"]))
    st.markdown("**Recommended improvements**")
    for suggestion in resume_review["suggestions"]:
        st.markdown(f"- {suggestion}")

    if resume_review["matched_target_skills"]:
        st.markdown(
            "**Target-role skills found:** "
            + ", ".join(resume_review["matched_target_skills"])
        )
    missing_skills = resume_review["missing_target_skills"]
    if missing_skills:
        st.markdown("**Target-role skills not mentioned in the resume**")
        st.caption(
            "Only add these if you genuinely have the skill; do not list skills "
            "you have not learned or used."
        )
        st.write(", ".join(missing_skills))
