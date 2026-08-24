"""Tests for DockerAgentIntegration."""

from urllib.parse import urlparse

import pytest

from specify_cli.integrations import get_integration

from .test_integration_base_skills import SkillsIntegrationTests


class TestDockerAgentIntegration(SkillsIntegrationTests):
    KEY = "docker-agent"
    FOLDER = ".docker-agent/"
    COMMANDS_SUBDIR = "skills"
    REGISTRAR_DIR = ".docker-agent/skills"

    def test_options_include_skills_flag(self):
        """Not applicable — Docker Agent only supports the skills layout."""
        pytest.skip(
            "Docker Agent is always skills-based and does not expose a --skills option"
        )

    def test_options_do_not_include_skills_flag(self):
        """Docker Agent is always skills-based; no --skills option is exposed."""
        i = get_integration(self.KEY)
        assert i is not None
        opts = i.options()
        skills_opts = [o for o in opts if o.name == "--skills"]
        assert len(skills_opts) == 0, (
            "Docker Agent is always skills-based and should not expose a --skills option"
        )

    def test_requires_cli_is_true(self):
        """Docker Agent is a CLI tool; requires_cli must be True."""
        i = get_integration(self.KEY)
        assert i is not None
        assert i.config["requires_cli"] is True
        assert i.config["name"] == "Docker Agent"

    def test_multi_install_safe_is_true(self):
        """Docker Agent uses an isolated .docker-agent/ root — safe to install
        alongside other integrations."""
        i = get_integration(self.KEY)
        assert i.multi_install_safe is True

    def test_is_slash_skills_agent(self):
        """Docker Agent invokes skills with a slash command (per its docs:
        ``/{skill-name}``), so is_slash_skills_agent must report True in both
        the enabled and disabled cases — it is always-slash, not conditional
        (mirrors droid/grok/trae/zed/devin)."""
        from specify_cli._invocation_style import is_slash_skills_agent

        assert is_slash_skills_agent("docker-agent", True) is True
        assert is_slash_skills_agent("docker-agent", False) is True

    def test_install_url_points_to_docker(self):
        i = get_integration(self.KEY)
        url = i.config.get("install_url")
        assert url is not None
        host = (urlparse(url).hostname or "").lower()
        assert host == "docs.docker.com" or host.endswith(".docker.com"), (
            f"install_url must point at the Docker domain, got: {url}"
        )


class TestDockerAgentInitFlow:
    """--integration docker-agent creates expected files."""

    def test_integration_docker_agent_creates_skills(self, tmp_path):
        """--integration docker-agent should create skills under
        .docker-agent/skills."""
        from typer.testing import CliRunner

        from specify_cli import app

        runner = CliRunner()
        target = tmp_path / "test-proj"
        result = runner.invoke(
            app,
            [
                "init",
                str(target),
                "--integration",
                "docker-agent",
                "--ignore-agent-tools",
                "--script",
                "sh",
            ],
            catch_exceptions=False,
        )

        assert result.exit_code == 0, (
            f"init --integration docker-agent failed: {result.output}"
        )
        assert (
            target / ".docker-agent" / "skills" / "speckit-plan" / "SKILL.md"
        ).exists()
        assert (
            target / ".docker-agent" / "skills" / "speckit-specify" / "SKILL.md"
        ).exists()


class TestDockerAgentCommandInvocation:
    """Skills agents use the hyphenated ``/speckit-<name>`` slash form."""

    def test_build_command_invocation_uses_hyphenated_skill_name(self):
        i = get_integration("docker-agent")
        assert i.build_command_invocation("speckit.plan", "feature-x") == (
            "/speckit-plan feature-x"
        )
        assert i.build_command_invocation("plan") == "/speckit-plan"
