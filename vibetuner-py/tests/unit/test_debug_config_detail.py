# ABOUTME: Tests that the debug config detail page renders set-up guidance for secrets.
# ABOUTME: Regression coverage for #1879 (secret-key dead-end with no how-to block).
# ruff: noqa: S101

from jinja2 import (
    ChainableUndefined,
    ChoiceLoader,
    DictLoader,
    Environment,
    FileSystemLoader,
    select_autoescape,
)
from vibetuner.paths import frontend_templates


def _stub_url_for(name: str, **kwargs):
    class _URL:
        path = f"/{name}"

    return _URL()


def _make_env() -> Environment:
    env = Environment(
        loader=ChoiceLoader(
            [
                DictLoader(
                    {
                        "child.html.jinja": (
                            "{% extends 'debug/config_detail.html.jinja' %}"
                        ),
                    }
                ),
                FileSystemLoader([str(p) for p in frontend_templates]),
            ]
        ),
        autoescape=select_autoescape(["html", "jinja"]),
        undefined=ChainableUndefined,
    )

    class _Hotreload:
        @staticmethod
        def script(url):
            return ""

    env.globals["url_for"] = _stub_url_for
    env.globals["DEBUG"] = True
    env.globals["BODY_CLASS"] = ""
    env.globals["SKIP_HEADER"] = True
    env.globals["SKIP_FOOTER"] = True
    env.globals["project_name"] = "test"
    env.globals["project_description"] = "test"
    env.globals["hotreload"] = _Hotreload()
    return env


def _render_secret_detail(entry: dict) -> str:
    env = _make_env()

    class _StubRequest:
        class state:  # noqa: N801
            language = "en"

        url = "https://test.example.com/debug/config/" + entry["key"]

    return env.get_template("child.html.jinja").render(
        request=_StubRequest(),
        csp_nonce="n",
        umami_website_id=None,
        entry=entry,
        mongodb_available=True,
    )


def _secret_entry(**overrides) -> dict:
    base = {
        "key": "services.anthropic_api_key",
        "value": "",
        "value_type": "str",
        "source": "default",
        "description": "Anthropic API key",
        "category": "services",
        "is_secret": True,
        "env_name": "SERVICES_ANTHROPIC_API_KEY",
    }
    base.update(overrides)
    return base


class TestSecretHowToBlock:
    """The help block must show actionable guidance for first-time admins."""

    def test_renders_env_var_name_for_secret(self):
        out = _render_secret_detail(_secret_entry())
        assert "SERVICES_ANTHROPIC_API_KEY" in out

    def test_renders_cli_command_with_key(self):
        out = _render_secret_detail(_secret_entry())
        assert "uv run vibetuner config set services.anthropic_api_key" in out

    def test_mentions_dot_env_option(self):
        out = _render_secret_detail(_secret_entry())
        # The .env line uses the same uppercase env name format
        assert out.count("SERVICES_ANTHROPIC_API_KEY") >= 2
        assert ".env" in out

    def test_includes_restart_reminder(self):
        out = _render_secret_detail(_secret_entry())
        assert "Restart" in out
        assert "worker" in out
        assert "frontend" in out

    def test_block_absent_for_non_secret_entries(self):
        out = _render_secret_detail(
            _secret_entry(
                key="features.dark_mode",
                value_type="bool",
                value=False,
                category="features",
                is_secret=False,
                env_name="FEATURES_DARK_MODE",
            )
        )
        assert "uv run vibetuner config set" not in out

    def test_env_source_badge_renders(self):
        out = _render_secret_detail(_secret_entry(source="env", value="sk-..."))
        # New source badge must be present so admins can see env wins
        assert ">env<" in out
