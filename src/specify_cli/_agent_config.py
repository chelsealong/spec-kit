"""Agent configuration constants derived from the integration registry."""
from __future__ import annotations

import os
from typing import Any


def _build_agent_config() -> dict[str, dict[str, Any]]:
    from .integrations import INTEGRATION_REGISTRY
    config: dict[str, dict[str, Any]] = {}
    for key, integration in INTEGRATION_REGISTRY.items():
        if integration.config:
            config[key] = dict(integration.config)
    return config


AGENT_CONFIG: dict[str, dict[str, Any]] = _build_agent_config()

DEFAULT_INIT_INTEGRATION = "copilot"

#: Environment variable that lets users override ``DEFAULT_INIT_INTEGRATION``
#: without passing ``--integration`` on every invocation.
DEFAULT_INIT_INTEGRATION_ENV_VAR = "SPECKIT_DEFAULT_INIT_INTEGRATION"


def get_default_init_integration() -> str:
    """Return the integration to use when none is explicitly selected.

    Honors ``SPECKIT_DEFAULT_INIT_INTEGRATION`` when it names a known
    integration key; otherwise falls back to ``DEFAULT_INIT_INTEGRATION``.
    """
    override = os.environ.get(DEFAULT_INIT_INTEGRATION_ENV_VAR)
    if override and override in AGENT_CONFIG:
        return override
    return DEFAULT_INIT_INTEGRATION

SCRIPT_TYPE_CHOICES: dict[str, str] = {
    "sh": "POSIX Shell (bash/zsh)",
    "ps": "PowerShell",
    "py": "Python",
}
