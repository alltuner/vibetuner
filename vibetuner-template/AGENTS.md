# Agent Guide

FastAPI + MongoDB + HTMX web application scaffolded from AllTuner's template.

> **Package name**: `app` below refers to your actual package under `src/`.
> Check `ls src/` if unsure.

## Executive Summary

**For frontend work**: Use the `/frontend-design` skill.

**Key locations**:
Routes: `src/app/frontend/routes/` | Templates: `templates/frontend/` |
Models: `src/app/models/` | App config: `src/app/tune.py` | CSS config: `config.css`

**Stack**: HTMX + Tailwind + DaisyUI. No JavaScript frameworks.

**Never modify**: `vibetuner` package code |
`assets/statics/css/bundle.css` or `js/bundle.js` (auto-generated)

**Framework docs**: https://vibetuner.alltuner.com/llms.txt
**Report issues**: https://github.com/alltuner/vibetuner/issues

---

## Reporting Framework Issues

When you encounter problems with the vibetuner framework, **file an issue
upstream** rather than working around it silently. Any friction in using
the framework is signal, not noise.

File to `alltuner/vibetuner` when you encounter:

1. **Bugs** — crashes, unexpected behavior, incorrect results
2. **Non-ergonomic APIs** — if something requires a workaround or
   boilerplate, that's a framework issue
3. **Missing features** — functionality that should exist in the
   framework but doesn't
4. **Documentation gaps** — missing, unclear, or incorrect docs
5. **Agent rule improvements** — if instructions in this file or
   `.claude/rules/` are misleading, incomplete, or could be better

**Identify yourself**: Always include which coding agent you are
(e.g., "Filed by Claude Code", "Filed by Cursor") at the end of
the issue body so maintainers know the source.

```bash
gh issue create --repo alltuner/vibetuner \
  --title "Brief description" \
  --body "Steps to reproduce, expected vs actual behavior.

Filed by [agent name]."
```

Do NOT silently work around framework issues. Filing the issue is
part of the job.

---

## Project Conventions (`CONVENTIONS.md`)

If `CONVENTIONS.md` exists at the project root, **read it before starting
work**. It contains project-specific rules, patterns, and preferences that
apply on top of this guide. Create it when you need persistent instructions
that aren't covered here.

## Project Learnings (`LEARNINGS.md`)

If `LEARNINGS.md` exists, **read it before starting work**. Add non-obvious
discoveries as short dated bullet points. Remove stale entries.

---

## Python Tooling

**Use `uv` exclusively** (never `python`, `pip`, `poetry`, `conda`):

```bash
uv run python script.py             # Run scripts
uv run vibetuner run dev frontend   # Dev server
uv run ruff format .                # Format code
uv add package-name                 # Add dependency
```

Dev tools included via `vibetuner[dev]`: `babel`, `djlint`, `taplo`,
`rumdl`, `granian[reload]`.

---

## App Configuration (`tune.py`)

Zero-config works out of the box. For custom components, create
`src/app/tune.py`:

```python
from vibetuner import VibetunerApp
from app.frontend.routes import app_router, api_router
from app.models import Post, Comment

app = VibetunerApp(
    models=[Post, Comment],
    routes=[app_router],          # frontend/HTMX (hidden from /docs)
    api_routes=[api_router],      # JSON API (visible in /docs)
    # Also supports: middleware, template_filters, frontend_lifespan,
    # worker_lifespan, oauth_providers, tasks, cli, runtime_config
)
```

---

## PR Titles & Releases

Use **conventional commits** for PR titles: `feat:`, `fix:`, `docs:`,
`chore:`, `refactor:`, `style:`, `test:`, `perf:`, `ci:`, `build:`.
Add `!` for breaking changes (e.g., `feat!:`). PR titles become squash
commit messages. Release Please auto-generates changelogs. Versioning
via git tags + `uv-dynamic-versioning`.

> **Stale CI on release PRs:** the scaffolded `release.yml` regenerates
> `uv.lock` after Release Please bumps `pyproject.toml`, then pushes the
> fix back to the PR branch with the default `GITHUB_TOKEN`. GitHub's
> anti-loop protection swallows that push, so no fresh CI runs on the
> lock-update commit — the PR's checks reflect the *pre*-regeneration
> state. Harmless if your merge gates aren't lockfile-sensitive.
> If you gate merge on `uv sync --frozen` (or any check that reads
> `uv.lock`), swap `GITHUB_TOKEN` for a [GitHub App token](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation)
> via [`actions/create-github-app-token`](https://github.com/actions/create-github-app-token)
> in the checkout + push steps so the regenerated commit triggers CI normally.

---

## Updating Scaffolding

Update dependencies and scaffolding in one step:

```bash
just deps-scaffolding-pr     # In a fresh worktree, then open a PR
just deps-scaffolding        # On the current feature branch, no PR
```

Both apply the latest scaffolding first (so Copier bumps `package.json`
/ `pyproject.toml`), then run `bun update` / `uv lock --upgrade` against
the bumped manifests. `deps-scaffolding` requires a clean working tree
and refuses to run on the default branch.

---

## Quick Start

```bash
just install-deps            # Once after cloning
just local-all               # Dev server + assets (recommended)
just local-all-with-worker   # With background worker (requires Redis)
just dev                     # Docker development
```

Key commands: `just format` (all code), `just lint` (all code),
`just format-py` (Python only), `just i18n` (translations).

`just dev` builds an all-in-one dev container (Python + bun + watchers)
and brings up mongo/redis alongside. Edits to `src/`, `templates/`, or
asset sources sync into the container via `docker compose up --watch`;
granian reloads on Python edits and the in-container bun watchers rebuild
`bundle.css`/`bundle.js` on template / asset edits — no host-side bun is
needed. The mapped host port is deterministic per project directory (in
the 14000–17999 band), so two scaffolded projects can run side-by-side.

> **Tailwind v4 watcher quirk:** if you edit `config.css`, restart
> `just dev` / `just local-all` — Tailwind v4 doesn't watch its own
> input file. Edits to templates and other `@source`-listed
> directories rebuild correctly without restart. Tracked upstream at
> [tailwindlabs/tailwindcss#14726](https://github.com/tailwindlabs/tailwindcss/issues/14726).

---

## Architecture

```text
src/app/              # Your code
  tune.py             # App config (optional)
  frontend/routes/    # HTTP handlers
  models/             # Beanie documents
  services/           # Business logic
  tasks/              # Background jobs
  cli/                # CLI commands
templates/frontend/   # Jinja templates
assets/statics/css/config.css  # Tailwind config (edit this, not bundle.css)
```

**Core (`vibetuner` package)**: Auth, OAuth, email, blob storage, base
templates, MongoDB setup. File issues, don't modify.
**App (`src/app/`)**: Your code. Edit freely.

---

## Development Patterns

### Routes

```python
from fastapi import APIRouter, Request, Depends
from vibetuner import render_template
from vibetuner.frontend.deps import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def dashboard(request: Request, user=Depends(get_current_user)):
    return render_template("dashboard.html.jinja", request, {"user": user})
```

Register routes in `__init__.py` via `APIRouter.include_router()`, then
list in `tune.py`.

### Models

```python
from beanie import Document, Link
from vibetuner.models import UserModel
from vibetuner.models.mixins import TimeStampMixin

class Post(Document, TimeStampMixin):
    title: str
    content: str
    author: Link[UserModel]
    class Settings:
        name = "posts"
        indexes = ["author", "db_insert_dt"]
```

Export from `__init__.py`, list in `tune.py` `models=[]`.

For detailed patterns (soft delete, encrypted fields, CRUD factory,
SSE, HTMX helpers, caching, background tasks, deployment, testing,
configuration, localization), see
https://vibetuner.alltuner.com/llms.txt

---

## Code Style

**Python**: Type hints always, async/await for DB ops,
**run `ruff format .` after changes**, 88 char lines.

**Frontend**: HTMX for dynamics, Tailwind classes, DaisyUI components,
extend `base/skeleton.html.jinja`.

**Tailwind 4**: Use utility classes and arbitrary values
(`text-[13px]`, `bg-[#1DB954]`). Define tokens in `config.css`
`@theme {}`. No inline styles.

---

## Important Rules

1. Never modify `vibetuner` package
2. All your code goes in `src/app/`
3. Always run `ruff format .` after Python changes
4. Use `uv` exclusively for Python
5. Override, don't modify core templates
6. Never inspect `bundle.css`/`bundle.js` — edit `config.css`/`config.js`
7. Configure in `tune.py` — don't rely on auto-discovery
