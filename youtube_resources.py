"""YouTube learning-channel discovery with a curated, key-free fallback."""

from __future__ import annotations

import os
from typing import Any

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


class YouTubeResourceError(RuntimeError):
    """Raised when the configured YouTube API returns unusable channel data."""


def youtube_api_key() -> str | None:
    """Read the YouTube key from the server environment only."""
    return os.getenv("YOUTUBE_API_KEY", "").strip() or None


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
