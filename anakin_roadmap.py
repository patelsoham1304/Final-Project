"""Client for Anakin.io roadmap.sh live API."""

import os
import time
import requests
import streamlit as st


def get_anakin_api_key() -> str:
    """Retrieve API key from streamlit secrets, env, or fallback."""
    if hasattr(st, "secrets") and "ANAKIN_API_KEY" in st.secrets:
        return st.secrets["ANAKIN_API_KEY"]
    return os.getenv("ANAKIN_API_KEY", "ask_ee95e81adad04f6371210011a4a4e74d6bbcf09d3af57d78b1601e462c54c3d7")


def fetch_roadmap_detail(roadmap_slug: str) -> dict | None:
    """Fetch roadmap topic graph & details from Anakin roadmap.sh wire action."""
    api_key = get_anakin_api_key()
    if not api_key:
        return None

    url = "https://api.anakin.io/v1/wire/task"
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "action_id": "act_roadmap_sh_roadmap_detail",
        "params": {
            "roadmap_slug": roadmap_slug
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        
        # If asynchronous task, poll task id or return result
        task_id = data.get("task_id") or data.get("id")
        if task_id and "result" not in data:
            poll_url = f"https://api.anakin.io/v1/wire/task/{task_id}"
            for _ in range(6):
                time.sleep(1.5)
                poll_resp = requests.get(poll_url, headers=headers, timeout=10)
                if poll_resp.status_code == 200:
                    poll_data = poll_resp.json()
                    if poll_data.get("status") in ("completed", "finished", "success"):
                        return poll_data.get("result", poll_data)
        return data.get("result", data)
    except Exception:
        return None
