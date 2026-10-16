"""Resume-first career matching and learning-plan screen."""

import hashlib

import streamlit as st

from database.seed import CAREER_CATALOG
from modules.career_path import (
    AIAnalysisError,
    CareerPathError,
    analyze_resume,
    build_learning_roadmap,
    openai_api_key,
)
from modules.resume_upload import MAX_RESUME_BYTES, extract_resume_text
from modules.youtube_resources import (
    YouTubeResourceError,
    find_learning_channels,
    youtube_api_key,
)


def _career_profiles():
    return [
        {"name": name, "description": details["description"], "skills": details["skills"]}
        for name, details in CAREER_CATALOG.items()
    ]


def _render_channels(skill: str, button_key: str):
    result_key = f"career_path_channels:{skill}"
    if st.button("Find YouTube learning channels", key=button_key):
        try:
            st.session_state[result_key] = find_learning_channels(
                skill, api_key=youtube_api_key()
            )
        except YouTubeResourceError as error:
            st.warning(f"{error} Showing curated channels instead.")
            st.session_state[result_key] = find_learning_channels(skill, api_key="")

    result = st.session_state.get(result_key)
    if not result:
        return
    if result["source"] == "curated":
        st.caption("Curated YouTube channels (not a live search).")
    for channel in result["channels"]:
        st.link_button(channel["title"], channel["url"])


def render():
    """Analyze an uploaded resume and produce a role-specific learning path."""
    st.header("Resume-to-Career Path")
    st.write(
        "Start with your existing resume. The app identifies resume evidence, "
        "compares it with supported career profiles, and builds an ordered plan."
    )
    st.info(
        "Your uploaded file is processed in this browser session and is not saved "
        "to the app database. Role matches are limited to the six career profiles "
        "currently supported by this project."
    )

    uploaded_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX, or UTF-8 TXT; maximum 10 MB. Scanned PDFs need OCR.",
        key="career_path_resume_file",
    )
    left, right = st.columns(2)
    target_role = left.text_input(
        "Optional role you are interested in",
        placeholder="For example, Frontend Developer",
        key="career_path_target_role",
    )
    weekly_hours = right.number_input(
        "Study hours per week",
        min_value=1,
        max_value=80,
        value=8,
        step=1,
        key="career_path_weekly_hours",
    )

    api_key = openai_api_key()
    use_ai = False
    if api_key:
        use_ai = st.checkbox(
            "I consent to sending redacted resume text to OpenAI for analysis and "
            "learning-hour estimates.",
            value=False,
            key="career_path_ai_consent",
            help=(
                "Email addresses, phone numbers, and URLs are removed first. "
                "Other personal details can remain in the resume. OpenAI API "
                "retention is governed by your account's data-control settings."
            ),
        )
    else:
        st.caption(
            "AI is not configured; resume matching and learning-time estimates "
            "will use transparent local rules. No resume text leaves this app."
        )

    if uploaded_file is None:
        st.caption("Upload a resume to see evidence-backed role matches.")
        return
    if uploaded_file.size > MAX_RESUME_BYTES:
        st.error("Resume files must be 10 MB or smaller.")
        return

    content = uploaded_file.getvalue()
    upload_fingerprint = hashlib.sha256(content).hexdigest()
    if st.button("Analyze resume and find career matches", type="primary"):
        try:
            resume_text = extract_resume_text(uploaded_file.name, content)
            analysis = analyze_resume(
                resume_text,
                _career_profiles(),
                target_role=target_role,
                api_key=api_key,
                use_ai=use_ai,
            )
        except AIAnalysisError as error:
            st.error(f"AI analysis failed: {error}")
            st.warning("Retry with AI consent turned off to use local matching.")
            st.session_state.pop("career_path_analysis", None)
            return
        except (CareerPathError, ValueError) as error:
            st.error(str(error))
            st.session_state.pop("career_path_analysis", None)
            return
        st.session_state["career_path_analysis"] = {
            "upload_fingerprint": upload_fingerprint,
            "analysis": analysis,
        }

    saved = st.session_state.get("career_path_analysis")
    if not saved or saved["upload_fingerprint"] != upload_fingerprint:
        st.caption("Select **Analyze resume and find career matches** to continue.")
        return
    analysis = saved["analysis"]

    st.subheader("Resume evidence")
    st.caption(
        "Analysis mode: "
        + ("OpenAI with your consent" if analysis["analysis_mode"] == "openai" else "local rules")
    )
    if analysis["experience_years"] is not None:
        st.metric("Experience explicitly stated", f"{analysis['experience_years']:g} years")
    else:
        st.caption("No explicit years-of-experience value was identified.")
    if analysis["skills"]:
        for skill in analysis["skills"]:
            st.markdown(
                f"- **{skill['name']}** — evidence level {skill['level']}/5 "
                f"({skill['confidence']} confidence): “{skill['evidence']}”"
            )
    else:
        st.caption(
            "No supported skills were found in the resume text. Check that the "
            "document contains selectable text and uses recognizable skill names."
        )

    st.subheader("Best matches among supported career profiles")
    st.caption(
        "Fit score combines resume evidence level with the role's listed skills; "
        "a skill mention alone is not counted as working proficiency."
    )
    for match in analysis["role_matches"]:
        st.markdown(f"**{match['name']} · {match['fit_percent']}% skill coverage**")
        st.progress(match["fit_percent"] / 100)
        st.caption(
            f"Found in resume: {', '.join(match['matched_skills']) or 'none'}"
            f" · At working level: {len(match['demonstrated_skills'])}"
            f" · Skills to build: {len(match['missing_skills'])}"
        )

    match_by_name = {match["name"]: match for match in analysis["role_matches"]}
    selected_role = st.selectbox(
        "Choose a role for your personalized roadmap",
        list(match_by_name),
        key="career_path_selected_role",
    )
    selected_match = match_by_name[selected_role]
    try:
        roadmap = build_learning_roadmap(
            selected_match,
            analysis["skills"],
            weekly_hours,
            experience_years=analysis["experience_years"],
            api_key=api_key if use_ai else None,
        )
    except AIAnalysisError as error:
        st.warning(f"AI duration estimate failed: {error} Using curated estimates.")
        roadmap = build_learning_roadmap(
            selected_match,
            analysis["skills"],
            weekly_hours,
            experience_years=analysis["experience_years"],
        )
    except CareerPathError as error:
        st.error(str(error))
        return

    st.subheader(f"Learning roadmap: {selected_role}")
    if roadmap["steps"]:
        low, high = roadmap["duration_range_weeks"]
        first, second, third = st.columns(3)
        first.metric("Estimated learning time", f"{roadmap['total_learning_hours']} hours")
        second.metric("At your pace", f"{roadmap['estimated_weeks']} weeks")
        third.metric("Planning range", f"{low}–{high} weeks")
        st.caption(
            f"Estimate source: {roadmap['duration_source']}. Actual time varies "
            "with practice, prior knowledge, and study consistency."
        )
        for step in roadmap["steps"]:
            with st.container(border=True):
                st.markdown(
                    f"**Step {step['step']}: {step['skill']}** · "
                    f"Evidence level {step['current_level']}/5 → working target "
                    f"{step['target_level']}/5"
                )
                st.caption(
                    f"About {step['estimated_hours']} learning hours · "
                    f"weeks {step['start_week']}–{step['end_week']} at "
                    f"{weekly_hours} study hours/week."
                )
                _render_channels(step["skill"], f"youtube_channel_{step['step']}")
    else:
        st.success("Your resume already shows the working target for every listed skill.")
        st.caption("The target is practical entry-level competence, not expert mastery.")
