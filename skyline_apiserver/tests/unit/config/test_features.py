from __future__ import annotations

import pytest

from skyline_apiserver.config.features import validate_kagent_chat

LINK = "https://kagent.example.com/agents/kagent/chat-agent/chat"


@pytest.mark.parametrize(
    "value",
    [
        None,
        {"url": LINK},
        {"url": "/kagent", "namespace": "kagent", "agent": "k8s-agent", "ui_version": "v1"},
        {"url": LINK, "allowed_roles": ["admin", "member"]},
    ],
)
def test_validate_kagent_chat_accepts(value):
    validate_kagent_chat({} if value is None else {"kagent_chat": value})


@pytest.mark.parametrize(
    "value",
    [
        "https://kagent.example.com",
        {},
        {"url": ""},
        {"url": "javascript:alert(1)"},
        {"url": "//evil.example.com"},
        {"url": LINK, "ui_version": "v2"},
        {"url": LINK, "agent": 1},
        {"url": LINK, "allowed_roles": "admin"},
        {"url": LINK, "token": "secret"},
    ],
)
def test_validate_kagent_chat_rejects(value):
    with pytest.raises(ValueError):
        validate_kagent_chat({"kagent_chat": value})
