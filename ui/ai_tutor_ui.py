"""Persistent right-side AI tutor connected to the active learning path."""

import sqlite3

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError

from database.db import (
    get_current_roadmap,
    get_skills_for_career,
)
from modules.ollama_tutor import (
    MAX_CHAT_MESSAGE_CHARS,
    OllamaTutorError,
    build_learning_context,
    load_ollama_config,
    request_tutor_reply,
)
from modules.skill_assessment import get_assessments


def _load_secret_settings() -> dict:
    try:
        return dict(st.secrets)
    except StreamlitSecretNotFoundError:
        return {}


def _active_learning_context() -> str:
    student_id = st.session_state.get("student_id")
    if not student_id:
        return build_learning_context(None, [])

    roadmap = get_current_roadmap(student_id)
    if roadmap is None:
        return build_learning_context(None, [])

    skills = get_skills_for_career(roadmap["career_id"])
    assessed_skill_ids = {
        item["skill_id"] for item in get_assessments(student_id)
    }
    skill_context = []
    for skill in skills:
        skill_context.append(
            {
                "name": skill["name"],
                "status": (
                    "completed" if skill["id"] in assessed_skill_ids else "not_started"
                ),
            }
        )
    return build_learning_context(
        roadmap["career_name"],
        skill_context,
        st.session_state.get("workflow_step"),
    )


def render() -> None:
    """Render the same tutor panel alongside every workflow screen."""
    st.markdown(
        """
        <style>
        .st-key-ai_tutor_shell {
            position: sticky;
            top: 4rem;
            max-height: calc(100vh - 5rem);
            overflow-y: auto;
            border: 1px solid #e3e8ef;
            border-radius: .8rem;
            background: #fff;
            padding: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    student_id = st.session_state.get("student_id")
    history_key = f"ai_tutor_messages_{student_id or 'anonymous'}"
    st.session_state.setdefault(history_key, [])
    send_error = None

    with st.container(key="ai_tutor_shell"):
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <div style="width:40px;height:40px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#1d4ed8);
                            display:grid;place-items:center;font-size:20px;box-shadow:0 0 14px rgba(59,130,246,0.35);">
                    🤖
                </div>
                <div>
                    <div style="font-weight:750;font-size:17px;color:#ffffff;line-height:1.2;">AI Pathfinder Tutor</div>
                    <div style="font-size:11px;color:#94a3b8;">Interactive learning guide</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Ask about your selected career, roadmap, skills, or study plan.")
        st.caption("Your resume is not shared. Chat history stays in this browser session.")

        api_key = st.text_input(
            "Ollama API key",
            type="password",
            key="ai_tutor_api_key",
            help=(
                "For hosted Ollama, paste your API key here. It stays in this "
                "browser session and is not saved to the project."
            ),
            placeholder="Paste hosted Ollama API key",
        )

        try:
            config = load_ollama_config(
                secrets=_load_secret_settings(),
                api_key_override=api_key.strip() or None,
            )
        except ValueError as error:
            config = None
            st.error(f"Ollama configuration error: {error}")

        if config:
            if config.api_key:
                st.caption(
                    f"Hosted Ollama · {config.model} · API key configured"
                )
            else:
                st.caption(
                    f"Local Ollama · {config.model} · no API key required"
                )

        for message in st.session_state[history_key]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        with st.form("ai_tutor_form", clear_on_submit=True):
            prompt = st.text_area(
                "Ask the tutor",
                max_chars=MAX_CHAT_MESSAGE_CHARS,
                height=90,
                key=f"ai_tutor_prompt_{student_id or 'anonymous'}",
                placeholder="For example: What should I learn next?",
            )
            submitted = st.form_submit_button("Ask tutor", type="primary")

        if submitted:
            if not config:
                send_error = (
                    "Configure Ollama with OLLAMA_BASE_URL and OLLAMA_MODEL, "
                    "and set OLLAMA_API_KEY for hosted Ollama."
                )
            else:
                try:
                    with st.spinner("Ollama is preparing an answer..."):
                        answer = request_tutor_reply(
                            prompt,
                            _active_learning_context(),
                            st.session_state[history_key],
                            config,
                        )
                    st.session_state[history_key].extend(
                        [
                            {"role": "user", "content": prompt.strip()},
                            {"role": "assistant", "content": answer},
                        ]
                    )
                    st.rerun()
                except ValueError as error:
                    send_error = str(error)
                except OllamaTutorError as error:
                    send_error = str(error)
                except sqlite3.Error:
                    send_error = (
                        "The active learning path could not be loaded. "
                        "Check the local database and try again."
                    )

        if send_error:
            st.error(send_error)
