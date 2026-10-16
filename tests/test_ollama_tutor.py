from unittest.mock import Mock, patch

import pytest
import requests

from modules.ollama_tutor import (
    MAX_CHAT_MESSAGE_CHARS,
    OllamaConfig,
    OllamaTutorError,
    build_learning_context,
    load_ollama_config,
    request_tutor_reply,
)


def test_hosted_ollama_config_reads_server_side_secret():
    config = load_ollama_config(
        environ={},
        secrets={
            "ollama": {
                "api_key": "server-secret",
                "model": "gemma4:31b",
            }
        },
    )

    assert config.base_url == "https://ollama.com"
    assert config.chat_url == "https://ollama.com/api/chat"
    assert config.model == "gemma4:31b"
    assert config.api_key == "server-secret"
    assert "server-secret" not in repr(config)


def test_environment_settings_override_streamlit_secrets():
    config = load_ollama_config(
        environ={
            "OLLAMA_API_KEY": "env-secret",
            "OLLAMA_BASE_URL": "https://ollama.example.test/api",
            "OLLAMA_MODEL": "custom-model",
        },
        secrets={
            "ollama": {
                "api_key": "other-secret",
                "model": "other-model",
            }
        },
    )

    assert config.chat_url == "https://ollama.example.test/api/chat"
    assert config.model == "custom-model"
    assert config.api_key == "env-secret"


def test_local_ollama_defaults_without_an_api_key():
    config = load_ollama_config(environ={}, secrets={})

    assert config.base_url == "http://localhost:11434"
    assert config.chat_url == "http://localhost:11434/api/chat"
    assert config.api_key == ""
    assert config.model


def test_api_key_override_defaults_to_hosted_ollama():
    config = load_ollama_config(
        environ={},
        secrets={},
        api_key_override="browser-session-key",
    )

    assert config.base_url == "https://ollama.com"
    assert config.chat_url == "https://ollama.com/api/chat"
    assert config.api_key == "browser-session-key"


def test_api_key_override_rejects_insecure_remote_endpoint():
    with pytest.raises(ValueError, match="Use HTTPS"):
        load_ollama_config(
            environ={"OLLAMA_BASE_URL": "http://ollama.example.test"},
            secrets={},
            api_key_override="browser-session-key",
        )


@pytest.mark.parametrize(
    ("base_url", "message"),
    [
        ("ftp://ollama.example.test", "OLLAMA_BASE_URL"),
        ("https://user:password@ollama.example.test", "OLLAMA_BASE_URL"),
        ("https://ollama.example.test?token=secret", "OLLAMA_BASE_URL"),
        (
            "http://ollama.example.test",
            "Use HTTPS for remote Ollama endpoints",
        ),
    ],
)
def test_rejects_unsafe_or_invalid_service_urls(base_url, message):
    with pytest.raises(ValueError, match=message):
        load_ollama_config(
            environ={
                "OLLAMA_API_KEY": "secret",
                "OLLAMA_BASE_URL": base_url,
            },
            secrets={},
        )


def test_learning_context_includes_selected_role_and_assessed_skills_only():
    context = build_learning_context(
        "Data Analyst",
        [
            {"name": "SQL", "status": "completed", "progress_percent": 100},
            {"name": "Excel", "status": "in_progress", "progress_percent": 40},
        ],
        "Skill Gap & Roadmap",
    )

    assert "Selected career: Data Analyst" in context
    assert "Current app section: Skill Gap & Roadmap" in context
    assert "- SQL: already known" in context
    assert "- Excel: to learn" in context
    assert "%" not in context
    assert "progress" not in context.lower()
    assert "resume" not in context.lower()
    assert "email" not in context.lower()


def test_context_explains_when_no_roadmap_is_selected():
    context = build_learning_context(None, [])

    assert "No career roadmap is selected yet" in context
    assert "choose a career" in context


def test_chat_request_uses_bearer_key_and_returns_assistant_content():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "message": {"role": "assistant", "content": "Start with SQL."}
    }
    config = OllamaConfig("https://ollama.com", "gemma4:31b", "server-secret")
    with patch("modules.ollama_tutor.requests.post", return_value=response) as post:
        answer = request_tutor_reply(
            "What should I learn next?",
            "Selected career: Data Analyst",
            [{"role": "user", "content": "Hi"}],
            config,
        )

    assert answer == "Start with SQL."
    assert post.call_args.args[0] == "https://ollama.com/api/chat"
    assert post.call_args.kwargs["headers"]["Authorization"] == "Bearer server-secret"
    body = post.call_args.kwargs["json"]
    assert body["model"] == "gemma4:31b"
    assert body["stream"] is False
    assert body["messages"][0]["role"] == "system"
    assert body["messages"][-1] == {
        "role": "user",
        "content": "What should I learn next?",
    }
    assert post.call_args.kwargs["timeout"] > 0


def test_local_chat_does_not_send_an_authorization_header():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "message": {"role": "assistant", "content": "Practice with a small project."}
    }
    with patch("modules.ollama_tutor.requests.post", return_value=response) as post:
        request_tutor_reply(
            "How do I practice?",
            "No career roadmap is selected yet.",
            [],
            OllamaConfig("http://localhost:11434", "local-model"),
        )

    assert "Authorization" not in post.call_args.kwargs["headers"]


@pytest.mark.parametrize(
    ("status_code", "message"),
    [
        (401, "credentials"),
        (403, "credentials"),
        (404, "configured model or chat endpoint"),
        (500, "HTTP error"),
    ],
)
def test_service_http_errors_are_explained_without_response_secrets(
    status_code, message
):
    response = Mock()
    response.status_code = status_code
    response.raise_for_status.side_effect = (
        requests.HTTPError(response=response) if status_code >= 400 else None
    )
    with patch("modules.ollama_tutor.requests.post", return_value=response):
        with pytest.raises(OllamaTutorError, match=message):
            request_tutor_reply(
                "Help",
                "Context",
                [],
                OllamaConfig(
                    "https://ollama.com",
                    "model",
                    "do-not-include-this-secret",
                ),
            )


def test_network_errors_do_not_expose_request_credentials():
    with patch(
        "modules.ollama_tutor.requests.post",
        side_effect=requests.Timeout("request with hidden token"),
    ):
        with pytest.raises(OllamaTutorError, match="Could not connect") as error:
            request_tutor_reply(
                "Help",
                "Context",
                [],
                OllamaConfig("https://ollama.com", "model", "hidden-token"),
            )

    assert "hidden-token" not in str(error.value)


def test_invalid_json_and_missing_message_are_reported():
    response = Mock()
    response.status_code = 200
    response.json.side_effect = ValueError("invalid")
    with patch("modules.ollama_tutor.requests.post", return_value=response):
        with pytest.raises(OllamaTutorError, match="invalid JSON"):
            request_tutor_reply(
                "Help", "Context", [], OllamaConfig("http://localhost", "model")
            )

    response.json.side_effect = None
    response.json.return_value = {"message": {"content": ""}}
    with patch("modules.ollama_tutor.requests.post", return_value=response):
        with pytest.raises(OllamaTutorError, match="no assistant message"):
            request_tutor_reply(
                "Help", "Context", [], OllamaConfig("http://localhost", "model")
            )


def test_rejects_empty_and_overlong_prompts_without_network_call():
    config = OllamaConfig("http://localhost", "model")
    with patch("modules.ollama_tutor.requests.post") as post:
        with pytest.raises(ValueError, match="Enter a question"):
            request_tutor_reply(" ", "Context", [], config)
        with pytest.raises(ValueError, match=str(MAX_CHAT_MESSAGE_CHARS)):
            request_tutor_reply(
                "x" * (MAX_CHAT_MESSAGE_CHARS + 1), "Context", [], config
            )

    post.assert_not_called()
