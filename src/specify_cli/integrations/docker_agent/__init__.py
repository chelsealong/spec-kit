"""Docker Agent integration — skills-based agent.

Docker Agent discovers project skills from
``.docker-agent/skills/speckit-<name>/SKILL.md``. Spec Kit installs into
that native tree so the generated skills are visible to Docker Agent
without extra configuration.

See: https://docs.docker.com/ai/docker-agent/features/skills/
"""

from __future__ import annotations

from ..base import SkillsIntegration


class DockerAgentIntegration(SkillsIntegration):
    """Integration for Docker Agent."""

    key = "docker-agent"
    config = {
        "name": "Docker Agent",
        "folder": ".docker-agent/",
        "commands_subdir": "skills",
        "install_url": "https://docs.docker.com/ai/docker-agent/",
        "requires_cli": True,
    }
    registrar_config = {
        "dir": ".docker-agent/skills",
        "format": "markdown",
        "args": "$ARGUMENTS",
        "extension": "/SKILL.md",
    }
    multi_install_safe = True
