from unittest.mock import Mock, patch

import pytest
import requests

from modules.youtube_resources import (
    YouTubeResourceError,
    find_learning_channels,
)


def test_no_key_returns_curated_youtube_channel_links_only():
    result = find_learning_channels("React")

    assert result["source"] == "curated"
    assert result["channels"]
    assert all(
        channel["url"].startswith("https://www.youtube.com/")
        for channel in result["channels"]
    )
    assert all("/watch?" not in channel["url"] for channel in result["channels"])


def test_live_search_requests_channels_and_builds_channel_urls():
    response = Mock()
    response.json.return_value = {
        "items": [
            {
                "id": {"channelId": "UC123"},
                "snippet": {"title": "Example Channel"},
            }
        ]
    }
    with patch(
        "modules.youtube_resources.requests.get", return_value=response
    ) as get:
        result = find_learning_channels("React", api_key="test-key")

    assert get.call_args.kwargs["params"]["type"] == "channel"
    assert result["source"] == "youtube_api"
    assert result["channels"][0]["url"] == "https://www.youtube.com/channel/UC123"
    assert "/watch?" not in result["channels"][0]["url"]


def test_live_search_failure_is_not_silently_shaped_as_success():
    with patch(
        "modules.youtube_resources.requests.get",
        side_effect=requests.RequestException("offline"),
    ):
        with pytest.raises(YouTubeResourceError, match="search failed"):
            find_learning_channels("Python", api_key="test-key")


def test_unexpected_live_response_is_reported():
    response = Mock()
    response.json.return_value = []
    with patch("modules.youtube_resources.requests.get", return_value=response):
        with pytest.raises(YouTubeResourceError, match="response shape"):
            find_learning_channels("Python", api_key="test-key")
