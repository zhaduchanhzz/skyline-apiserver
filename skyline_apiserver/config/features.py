"""Validate deployment UI settings without registering individual feature names."""

KAGENT_CHAT_KEYS = {"url", "namespace", "agent", "ui_version", "allowed_roles"}
KAGENT_CHAT_UI_VERSIONS = {"v0", "v1"}


def validate_features(config):
    """The console owns flag names, defaults, and parent relationships."""
    values = config.get("features")
    if values is None:
        return
    if not isinstance(values, dict):
        raise ValueError("features must be a mapping of panel names to booleans or null")
    for name, value in values.items():
        if not isinstance(name, str):
            raise ValueError("features keys must be strings")
        if value is not None and type(value) is not bool:
            raise ValueError(f"features.{name} must be a boolean or null")


def validate_kagent_chat(config):
    """Check the shape of the optional kagent_chat block.

    The console validates the URL and names again before using them, so this
    only rejects values that are clearly wrong at startup.
    """
    values = config.get("kagent_chat")
    if values is None:
        return
    if not isinstance(values, dict):
        raise ValueError("kagent_chat must be a mapping")
    unknown = set(values) - KAGENT_CHAT_KEYS
    if unknown:
        names = ", ".join(sorted(map(str, unknown)))
        raise ValueError(f"kagent_chat has unknown keys: {names}")
    url = values.get("url")
    if not isinstance(url, str) or not url.strip():
        raise ValueError("kagent_chat.url must be a non-empty string")
    url = url.strip()
    is_path = url.startswith("/") and not url.startswith("//")
    if not (is_path or url.lower().startswith(("http://", "https://"))):
        raise ValueError('kagent_chat.url must be an http(s) URL or a path starting with "/"')
    for key in ("namespace", "agent"):
        value = values.get(key)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"kagent_chat.{key} must be a string")
    ui_version = values.get("ui_version")
    if ui_version is not None and ui_version not in KAGENT_CHAT_UI_VERSIONS:
        raise ValueError('kagent_chat.ui_version must be "v0" or "v1"')
    roles = values.get("allowed_roles")
    if roles is not None and (
        not isinstance(roles, list) or not all(isinstance(role, str) for role in roles)
    ):
        raise ValueError("kagent_chat.allowed_roles must be a list of strings")
