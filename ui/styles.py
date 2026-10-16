"""Shared visual styling for the Streamlit application."""

import streamlit as st


def apply_app_styles() -> None:
    """Apply a consistent, responsive visual system to all workflow screens."""
    st.markdown(
        """
        <style>
        :root {
            --epg-ink: #243247;
            --epg-muted: #687487;
            --epg-blue: #4568a8;
            --epg-blue-dark: #355486;
            --epg-border: #e3e8ef;
            --epg-surface: #ffffff;
        }
        .stApp {
            background: #f7f8fa;
            color: var(--epg-ink);
        }
        [data-testid="stHeader"] {
            background: rgba(247, 248, 250, .94);
        }
        [data-testid="stSidebar"] {
            background: #f1f3f6;
            border-right: 1px solid var(--epg-border);
        }
        [data-testid="stSidebar"] > div:first-child {
            padding-top: 1.35rem;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label {
            border-radius: .65rem;
            padding: .28rem .42rem;
            transition: background-color .18s ease, color .18s ease;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
            background: #e9edf3;
        }
        [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background: #e4eaf4;
            color: var(--epg-blue-dark);
            font-weight: 650;
        }
        .block-container {
            max-width: 1180px;
            padding-top: 2rem;
            padding-bottom: 3rem;
            animation: epg-enter .38s ease-out both;
        }
        h1, h2, h3 {
            color: var(--epg-ink);
            letter-spacing: -.025em;
        }
        h1 {
            font-weight: 750;
        }
        h1::after {
            content: "";
            display: block;
            width: 2.8rem;
            height: 3px;
            margin-top: .55rem;
            border-radius: 999px;
            background: var(--epg-blue);
            opacity: .82;
        }
        [data-testid="stCaptionContainer"] {
            color: var(--epg-muted);
        }
        [data-testid="stAlert"] {
            border-radius: .75rem;
            border-left-width: 3px;
        }
        [data-testid="stExpander"] {
            background: var(--epg-surface);
            border: 1px solid var(--epg-border);
            border-radius: .8rem;
        }
        [data-testid="stMetric"] {
            background: var(--epg-surface);
            border: 1px solid var(--epg-border);
            border-radius: .8rem;
            padding: 1rem 1.1rem;
            box-shadow: 0 2px 10px rgba(36, 50, 71, .035);
            transition: border-color .18s ease, transform .18s ease;
        }
        [data-testid="stMetric"]:hover {
            border-color: #c3d0e2;
            transform: translateY(-2px);
        }
        [data-testid="stMetricLabel"] {
            color: var(--epg-muted);
        }
        div.stButton > button,
        div.stFormSubmitButton > button,
        div.stDownloadButton > button {
            border-radius: .58rem;
            min-height: 2.7rem;
            font-weight: 650;
            transition: transform .16s ease, box-shadow .16s ease,
                        background-color .16s ease, border-color .16s ease;
        }
        div.stButton > button[kind="primary"],
        div.stFormSubmitButton > button[kind="primary"] {
            background: var(--epg-blue);
            border-color: var(--epg-blue);
        }
        div.stButton > button:hover,
        div.stFormSubmitButton > button:hover,
        div.stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(69, 104, 168, .14);
        }
        div.stButton > button[kind="primary"]:hover,
        div.stFormSubmitButton > button[kind="primary"]:hover {
            background: var(--epg-blue-dark);
            border-color: var(--epg-blue-dark);
        }
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stMultiSelect"] > div > div {
            border-radius: .6rem;
        }
        [data-testid="stProgress"] > div > div {
            background-color: var(--epg-blue);
            transition: width .45s ease;
        }
        a {
            color: var(--epg-blue-dark);
            text-decoration-color: #bdc9da;
            text-underline-offset: .15em;
        }
        a:hover {
            color: var(--epg-blue);
            text-decoration-color: currentColor;
        }
        @keyframes epg-enter {
            from {
                opacity: 0;
                transform: translateY(7px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: .01ms !important;
                animation-iteration-count: 1 !important;
                scroll-behavior: auto !important;
                transition-duration: .01ms !important;
            }
        }
        @media (max-width: 720px) {
            .block-container {
                padding: 1.15rem 1rem 2rem;
            }
            h1 {
                font-size: 1.8rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
