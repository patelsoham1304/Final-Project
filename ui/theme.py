"""Centralized theme and design system styling for the dark navy aesthetic."""

import streamlit as st


def apply_theme():
    """Inject global styling matching the visual target without breaking any widgets."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');

        /* Global Eye-Friendly Deep Slate Canvas */
        .stApp {
            background-color: #090d16;
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(56, 189, 248, 0.06) 0px, transparent 50%),
                radial-gradient(at 50% 100%, rgba(139, 92, 246, 0.05) 0px, transparent 50%);
            background-attachment: fixed;
            color: #f1f5f9;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Sidebar Styling - Soft dark slate */
        section[data-testid="stSidebar"] {
            background-color: #0d121f !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }

        /* Sidebar Navigation Radio Buttons */
        div[data-testid="stRadio"] > div {
            gap: 6px;
        }
        div[data-testid="stRadio"] label {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.04);
            border-radius: 12px;
            padding: 10px 16px !important;
            margin-bottom: 3px;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            cursor: pointer;
            width: 100%;
            font-size: 13.5px;
            font-weight: 500;
            color: #94a3b8;
        }
        div[data-testid="stRadio"] label:hover {
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(99, 102, 241, 0.3);
            color: #f8fafc;
            transform: translateX(3px);
        }
        /* Active Radio Item */
        div[data-testid="stRadio"] label[data-checked="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.16), rgba(139, 92, 246, 0.1)) !important;
            border: 1.5px solid #6366f1 !important;
            box-shadow: 0 4px 20px rgba(99, 102, 241, 0.25);
            color: #ffffff !important;
            font-weight: 700;
            position: relative;
        }
        div[data-testid="stRadio"] label[data-checked="true"]::before {
            content: '';
            position: absolute;
            left: 10px;
            top: 50%;
            transform: translateY(-50%);
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #6366f1;
            box-shadow: 0 0 10px #6366f1;
        }

        /* Buttons Styling - Soothing Indigo & Cyan Gradient */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 13px !important;
            letter-spacing: 0.2px;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
            padding: 8px 10px !important;
            min-height: 2.2rem !important;
            white-space: nowrap !important;
        }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #4f46e5 100%) !important;
            border: 1px solid rgba(56, 189, 248, 0.4) !important;
            color: #ffffff !important;
            box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
        }
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px) scale(1.01) !important;
            box-shadow: 0 6px 20px rgba(2, 132, 199, 0.5) !important;
        }
        .stButton > button[kind="secondary"] {
            background: rgba(30, 41, 59, 0.7) !important;
            border: 1px solid rgba(148, 163, 184, 0.3) !important;
            color: #f1f5f9 !important;
        }
        .stButton > button[kind="secondary"]:hover {
            background: rgba(51, 65, 85, 0.9) !important;
            color: #38bdf8 !important;
            border-color: #38bdf8 !important;
            transform: translateY(-1px) !important;
        }

        /* Input and TextArea Styling - Eye-Resting slate */
        input[type="text"], input[type="password"], textarea, div[data-baseweb="select"] {
            background-color: #111726 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 12px !important;
            color: #f8fafc !important;
            transition: all 0.2s ease !important;
        }
        input:focus, textarea:focus {
            border-color: #6366f1 !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
        }

        /* AI Tutor Container */
        .st-key-ai_tutor_shell {
            background: linear-gradient(180deg, #101628 0%, #0c101d 100%) !important;
            border: 1px solid rgba(99, 102, 241, 0.15) !important;
            border-radius: 20px !important;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45) !important;
            color: #f1f5f9;
            transition: all 0.3s ease !important;
        }
        .st-key-ai_tutor_shell:hover {
            border-color: rgba(99, 102, 241, 0.35) !important;
            box-shadow: 0 14px 40px rgba(99, 102, 241, 0.15) !important;
        }

        /* Info & Alert Banners */
        div[data-testid="stAlert"] {
            background: rgba(16, 22, 38, 0.85) !important;
            border: 1px solid rgba(99, 102, 241, 0.25) !important;
            border-radius: 14px !important;
            color: #f1f5f9 !important;
            backdrop-filter: blur(10px);
        }

        /* Chips Container & Interactive Animations */
        .skill-chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 15px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 600;
            margin: 4px;
            white-space: nowrap;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
            cursor: default;
        }
        .skill-chip:hover {
            transform: translateY(-2px) scale(1.03);
        }
        .skill-chip.known {
            background: rgba(16, 185, 129, 0.1);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: #34d399;
        }
        .skill-chip.missing {
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #818cf8;
        }
        .skill-chip.next {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(217, 119, 6, 0.1));
            border: 1.5px solid #f59e0b;
            color: #fbbf24;
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.25);
            animation: pulse-glow 2.8s infinite ease-in-out;
        }

        /* Pulse glow animation */
        @keyframes pulse-glow {
            0%, 100% {
                box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
            }
            50% {
                box-shadow: 0 0 20px rgba(245, 158, 11, 0.45);
            }
        }

        @keyframes subtleFloat {
            0%, 100% {
                transform: translateY(0px);
            }
            50% {
                transform: translateY(-6px);
            }
        }

        @keyframes livePulse {
            0% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.6);
            }
            70% {
                transform: scale(1);
                box-shadow: 0 0 0 8px rgba(99, 102, 241, 0);
            }
            100% {
                transform: scale(0.95);
                box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
            }
        }

        .floating-avatar {
            animation: subtleFloat 4s ease-in-out infinite;
        }

        .live-pulse-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #6366f1;
            box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.6);
            animation: livePulse 2s infinite;
            margin-right: 6px;
        }

        /* Gradient Text Shimmer - Clean Cyan & Violet */
        .shimmer-text {
            background: linear-gradient(90deg, #38bdf8 0%, #818cf8 30%, #c084fc 70%, #38bdf8 100%);
            background-size: 200% auto;
            color: transparent;
            -webkit-background-clip: text;
            background-clip: text;
            animation: shimmer 6s linear infinite;
        }
        @keyframes shimmer {
            0% { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }

        /* Modern Tabs styling */
        div[data-baseweb="tab-list"] {
            background: #0f1422 !important;
            padding: 5px !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            gap: 6px !important;
        }
        button[data-baseweb="tab"] {
            border-radius: 10px !important;
            padding: 10px 22px !important;
            font-weight: 600 !important;
            transition: all 0.25s ease !important;
            color: #94a3b8 !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2)) !important;
            color: #ffffff !important;
            border: 1px solid rgba(99, 102, 241, 0.4) !important;
            box-shadow: 0 4px 14px rgba(99, 102, 241, 0.2) !important;
        }
        </style>

        """,
        unsafe_allow_html=True,
    )
