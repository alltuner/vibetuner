# ABOUTME: Ensures jinja {% block %} names referenced in the scaffolded
# ABOUTME: frontend AGENTS.md docs actually exist in skeleton.html.jinja.
# ruff: noqa: S101

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SKELETON = (
    REPO_ROOT
    / "vibetuner-py"
    / "src"
    / "vibetuner"
    / "templates"
    / "frontend"
    / "base"
    / "skeleton.html.jinja"
)
AGENTS_MD = REPO_ROOT / "vibetuner-template" / "templates" / "frontend" / "AGENTS.md"

_BLOCK_RE = re.compile(r"{%-?\s*block\s+([A-Za-z_][A-Za-z0-9_]*)")
_JINJA_FENCE_RE = re.compile(r"```jinja\b[^\n]*\n(.*?)```", re.DOTALL)
_EXTENDS_RE = re.compile(r"{%-?\s*extends\s+['\"]([^'\"]+)['\"]")


def _skeleton_block_names() -> set[str]:
    return set(_BLOCK_RE.findall(SKELETON.read_text()))


def _agents_md_skeleton_block_refs() -> set[str]:
    """Block names used inside jinja fences that extend the skeleton."""
    text = AGENTS_MD.read_text()
    refs: set[str] = set()
    for fence in _JINJA_FENCE_RE.findall(text):
        extends = _EXTENDS_RE.search(fence)
        if extends is None or extends.group(1) != "base/skeleton.html.jinja":
            continue
        refs.update(_BLOCK_RE.findall(fence))
    return refs


def test_agents_md_only_references_real_skeleton_blocks():
    """Jinja silently drops `{% block X %}` content when the parent template has
    no matching block. Doc examples extending the skeleton must use real block
    names so copy-pasting them doesn't fail silently in the browser."""
    skeleton = _skeleton_block_names()
    refs = _agents_md_skeleton_block_refs()
    assert refs, "expected at least one skeleton-extending jinja example in AGENTS.md"
    unknown = refs - skeleton
    assert not unknown, (
        f"AGENTS.md references blocks {sorted(unknown)} that do not exist in "
        f"skeleton.html.jinja. Available blocks: {sorted(skeleton)}."
    )
