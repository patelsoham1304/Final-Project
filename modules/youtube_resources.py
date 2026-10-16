"""YouTube learning-channel discovery with a curated, key-free fallback."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import quote_plus

import requests

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
REQUEST_TIMEOUT_SECONDS = 12
MAX_CHANNELS = 3

_CURATED_CHANNELS = {
    "python": [("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
               ("Corey Schafer", "https://www.youtube.com/@coreyms")],
    "sql": [("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
            ("Alex The Analyst", "https://www.youtube.com/@AlexTheAnalyst")],
    "excel": [("Leila Gharani", "https://www.youtube.com/@LeilaGharani"),
              ("ExcelIsFun", "https://www.youtube.com/@excelisfun")],
    "statistics": [("Khan Academy", "https://www.youtube.com/@khanacademy"),
                   ("StatQuest with Josh Starmer", "https://www.youtube.com/@statquest")],
    "data": [("Alex The Analyst", "https://www.youtube.com/@AlexTheAnalyst"),
             ("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp")],
    "html": [("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
             ("Kevin Powell", "https://www.youtube.com/@KevinPowell")],
    "css": [("Kevin Powell", "https://www.youtube.com/@KevinPowell"),
            ("Web Dev Simplified", "https://www.youtube.com/@WebDevSimplified")],
    "javascript": [("Traversy Media", "https://www.youtube.com/@TraversyMedia"),
                   ("The Net Ninja", "https://www.youtube.com/@NetNinja")],
    "react": [("The Net Ninja", "https://www.youtube.com/@NetNinja"),
              ("Web Dev Simplified", "https://www.youtube.com/@WebDevSimplified")],
    "design": [("Figma", "https://www.youtube.com/@Figma"),
               ("Nielsen Norman Group", "https://www.youtube.com/@NNgroup")],
    "figma": [("Figma", "https://www.youtube.com/@Figma"),
              ("Jesse Showalter", "https://www.youtube.com/@JesseShowalter")],
    "security": [("Professor Messer", "https://www.youtube.com/@professormesser"),
                 ("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp")],
    "network": [("Professor Messer", "https://www.youtube.com/@professormesser"),
                ("PowerCert Animated Videos", "https://www.youtube.com/@PowerCertAnimatedVideos")],
    "linux": [("Learn Linux TV", "https://www.youtube.com/@LearnLinuxTV"),
              ("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp")],
    "git": [("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp"),
            ("The Net Ninja", "https://www.youtube.com/@NetNinja")],
    "machine learning": [("StatQuest with Josh Starmer", "https://www.youtube.com/@statquest"),
                         ("3Blue1Brown", "https://www.youtube.com/@3blue1brown")],
    "default": [("freeCodeCamp.org", "https://www.youtube.com/@freecodecamp")],
}

_CURATED_VIDEOS = {
    "sql": ("SQL Tutorial - Full Database Course for Beginners", "HXV3zeQKqGY"),
    "excel": ("Excel Tutorial for Beginners", "LgXzzu68j7M"),
    "statistics": (
        "Statistics For Data Analytics | Complete Syllabus | Data Science | Statistics Tutorial | Part 1",
        "o7WkGYIPUM8",
    ),
    "python": ("Learn Python - Full Course for Beginners", "rfscVS0vtbw"),
    "pandas": ("Python Pandas Tutorial", "ZyhVh-qRZPA"),
    "data visualization": (
        "Tableau for Data Science and Data Visualization - Crash Course Tutorial",
        "TPMlZxRRaBQ",
    ),
    "data analysis project": ("Build 12 Data Science Apps with Python and Streamlit - Full Course", "JwSS70SZdyM"),
    "html": ("HTML Full Course - Build a Website Tutorial", "pQN-pnXPaVg"),
    "css": ("CSS Tutorial - Zero to Hero (Complete Course)", "1Rs2ND1ryYc"),
    "javascript": (
        "JavaScript Course for Beginners - Your First Step to Web Development",
        "W6NZfCO5SIk",
    ),
    "git": ("Git and GitHub for Beginners - Crash Course", "RGOj5yH7evk"),
    "responsive design": ("Introduction to Responsive Web Design", "srvUrASNj0s"),
    "react": ("React JS Crash Course", "w7ejDZ8SWv8"),
    "frontend project": ("Personal Portfolio Website using HTML, CSS and JavaScript", "oFnIe-RpkE4"),
    "http and rest apis": ("RESTful APIs in 100 Seconds", "-MTSQjw5DrM"),
    "backend development": ("Node.js and Express.js - Full Course", "Oe421EPjeBE"),
    "software testing": ("Python Tutorial: Unit Testing Your Code with unittest", "6tNS--WetLI"),
    "backend project": ("Node.js and Express.js - Full Course", "Oe421EPjeBE"),
    "numpy": ("Python NumPy Tutorial for Beginners", "QUT1VHiLmmI"),
    "machine learning fundamentals": ("A Gentle Introduction to Machine Learning", "Gv9_4yMHFhI"),
    "data science project": ("Build 12 Data Science Apps with Python and Streamlit - Full Course", "JwSS70SZdyM"),
    "design principles": ("UI / UX Design Tutorial - Wireframe, Mockup & Design in Figma", "c9Wg6Cb_YlU"),
    "user research": ("UX Research - Get Started With Qualitative User Research", "bAARmsv1tms"),
    "wireframing": ("UI / UX Design Tutorial - Wireframe, Mockup & Design in Figma", "c9Wg6Cb_YlU"),
    "figma": ("Figma Course - Web Design Tutorial for Beginners", "D56hs0Twfco"),
    "prototyping": ("UI / UX Design Tutorial - Wireframe, Mockup & Design in Figma", "c9Wg6Cb_YlU"),
    "accessibility": (
        "WCAG for Beginners - What Are the Web Content Accessibility Guidelines?",
        "5H1JGdqLrWo",
    ),
    "ux portfolio project": (
        "Writing UX Design Case Study: Step by Step Process for UX/UI Portfolios",
        "bH-tB-qxypI",
    ),
    "networking fundamentals": ("FREE CCNA - What is a Network?", "S7MNX_UD7vY"),
    "linux command line": ("Linux Command Line for Beginners", "sWbUDq4S6Y8"),
    "web security fundamentals": (
        "Web Application Security Fundamentals (must know basics for developers, testers and hackers)",
        "-7OX58nHPb8",
    ),
    "owasp top 10": ("OWASP Top 10 Web Application Security Risks", "wUaeKEl1RCw"),
    "security monitoring": ("SOC Analyst L1 Full Course - Beginner Guide to Cyber Security", "CEKfFnHgQHw"),
    "cybersecurity lab project": (
        "Start Cybersecurity Hands-On with TryHackMe | Beginner Lab Walkthrough",
        "pWLhUqB2PfU",
    ),
}


class YouTubeResourceError(RuntimeError):
    """Raised when the configured YouTube API returns unusable channel data."""


def youtube_api_key() -> str | None:
    """Read the YouTube key from the server environment only."""
    return os.getenv("YOUTUBE_API_KEY", "").strip() or None


def youtube_video_search_url(skill: str) -> str:
    """Build a YouTube video-search link for a roadmap skill."""
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("A skill name is required to create a YouTube search link.")
    query = quote_plus(f"{skill.strip()} tutorial")
    return f"https://www.youtube.com/results?search_query={query}"


def get_recommended_youtube_video(skill: str) -> dict[str, str] | None:
    """Return a curated direct video recommendation for a supported roadmap skill."""
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("A skill name is required to find a recommended YouTube video.")
    normalized = " ".join(skill.split()).casefold()
    recommendation = _CURATED_VIDEOS.get(normalized)
    if recommendation is None:
        return None
    title, video_id = recommendation
    return {
        "title": title,
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def _fallback_channels(skill: str) -> list[dict[str, str]]:
    normalized = skill.casefold()
    channel_list = _CURATED_CHANNELS.get("default", [])
    for keyword, channels in _CURATED_CHANNELS.items():
        if keyword != "default" and keyword in normalized:
            channel_list = channels
            break
    return [
        {"title": title, "url": url, "source": "curated"}
        for title, url in channel_list[:MAX_CHANNELS]
    ]


def find_learning_channels(
    skill: str, api_key: str | None = None
) -> dict[str, Any]:
    """Return YouTube channel links only, using live search or curated channels."""
    if not isinstance(skill, str) or not skill.strip():
        raise ValueError("A skill name is required to find learning channels.")
    key = youtube_api_key() if api_key is None else api_key.strip() or None
    if not key:
        return {"channels": _fallback_channels(skill), "source": "curated"}

    try:
        response = requests.get(
            YOUTUBE_SEARCH_URL,
            params={
                "part": "snippet",
                "type": "channel",
                "maxResults": MAX_CHANNELS,
                "q": f"{skill.strip()} learning tutorial",
                "key": key,
                "fields": "items(id(channelId),snippet(title))",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as error:
        raise YouTubeResourceError(
            "YouTube channel search failed; curated channel suggestions are available."
        ) from error

    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise YouTubeResourceError("YouTube returned an unexpected response shape.")

    channels = []
    for item in payload["items"]:
        if not isinstance(item, dict):
            continue
        channel_info = item.get("id")
        snippet = item.get("snippet")
        if not isinstance(channel_info, dict) or not isinstance(snippet, dict):
            continue
        channel_id = channel_info.get("channelId")
        title = snippet.get("title")
        if (
            isinstance(channel_id, str)
            and channel_id
            and isinstance(title, str)
            and title.strip()
        ):
            channels.append(
                {
                    "title": title.strip(),
                    "url": f"https://www.youtube.com/channel/{channel_id}",
                    "source": "youtube_api",
                }
            )
    if not channels:
        raise YouTubeResourceError(
            "YouTube returned no learning channels; curated channel suggestions are available."
        )
    return {"channels": channels[:MAX_CHANNELS], "source": "youtube_api"}
