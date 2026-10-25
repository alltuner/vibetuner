# ABOUTME: Ensures the scaffolded app's container entrypoint scripts never dump the
# ABOUTME: environment (env, printenv, xtrace), which would write secrets to the logs.
# ruff: noqa: S101

import re
import shlex
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
TEMPLATE_DIR = REPO_ROOT / "vibetuner-template"
DOCKERFILE = TEMPLATE_DIR / "Dockerfile"

_COMMAND_SEPARATOR_RE = re.compile(r"&&|\|\||[;|&]")


def _entrypoint_scripts() -> list[Path]:
    """Shell scripts the template Dockerfile copies into the image."""
    scripts: list[Path] = []
    for line in DOCKERFILE.read_text().splitlines():
        tokens = line.split()
        if not tokens or tokens[0].upper() != "COPY":
            continue
        sources = [t for t in tokens[1:-1] if not t.startswith("--")]
        scripts.extend(
            TEMPLATE_DIR / source
            for source in sources
            if source.endswith((".sh", ".sh.j2"))
        )
    return scripts


def _enables_xtrace(words: list[str]) -> bool:
    if words[:3] == ["set", "-o", "xtrace"]:
        return True
    return words[0] == "set" and any(
        re.fullmatch(r"-[a-z]*x[a-z]*", word) for word in words[1:]
    )


def _environment_dumps(script: str) -> list[str]:
    """Lines of `script` that would print environment variables when run."""
    offending: list[str] = []
    for line in script.splitlines():
        if line.startswith("#!"):
            if _enables_xtrace(["set", *line.split()[1:]]):
                offending.append(line)
            continue
        code = line.split("#", 1)[0]
        for command in _COMMAND_SEPARATOR_RE.split(code):
            try:
                words = shlex.split(command)
            except ValueError:
                words = command.split()
            if not words:
                continue
            if words == ["env"] or words[0] == "printenv" or _enables_xtrace(words):
                offending.append(line)
                break
    return offending


def test_dockerfile_copies_start_sh() -> None:
    assert TEMPLATE_DIR / "start.sh" in _entrypoint_scripts()


@pytest.mark.parametrize(
    "script",
    _entrypoint_scripts(),
    ids=lambda path: str(path.relative_to(TEMPLATE_DIR)),
)
def test_entrypoint_does_not_print_environment(script: Path) -> None:
    assert _environment_dumps(script.read_text()) == []


@pytest.mark.parametrize(
    "line",
    [
        "env",
        "  env  ",
        "echo hi && env",
        "printenv",
        "printenv SECRET_KEY",
        "set -x",
        "set -ex",
        "set -o xtrace",
        "#!/bin/sh -x",
    ],
)
def test_detects_environment_dump(line: str) -> None:
    assert _environment_dumps(line) == [line]


@pytest.mark.parametrize(
    "line",
    [
        "set -e",
        "set -eu",
        "env FOO=bar vibetuner run dev",
        "# env",
        'echo "This is the environment:"',
        'exec vibetuner run "$@"',
        "#!/bin/sh",
    ],
)
def test_allows_safe_lines(line: str) -> None:
    assert _environment_dumps(line) == []
