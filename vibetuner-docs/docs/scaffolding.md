# Scaffolding Reference

Guidance for generating and updating projects with the Vibetuner Copier template.

## Overview

`vibetuner scaffold` wraps [Copier](https://copier.readthedocs.io/) to generate a
fully configured project from the files in `vibetuner-template/`. Answers to the
prompts below are stored in `.copier-answers.yml` inside the generated project,
so subsequent updates can reuse them.

## Template Prompts

- `company_name` – default `Acme Corp`. Displayed in generated metadata, email
templates, and documentation.
- `author_name` – default `Developer`. Used for attribution in project metadata.
- `author_email` – default `dev@example.com`. Included in scaffolded docs and config.
- `project_name` – default `_folder_name`. Human-friendly name used throughout
the README and docs.
- `project_slug` – default `_folder_name`. Must match `^[a-z][a-z0-9\-]*[a-z0-9]$`
(used for Python package name, Docker image, compose project name).
- `project_description` – default `A project that does something useful.`

Populates package metadata.

- `fqdn` – default empty. When set, enables production deployment extras (Caddy,

Watchtower, etc.).

- `python_version` – default `3.13`. Controls `.python-version`, Docker images,
and `uv` settings.
- `supported_languages` – default `[]`. JSON/YAML list of language codes (for
example `["es", "fr"]`), adds translation skeletons.
- `enable_job_queue` – default `false`. When enabled, includes Redis/Streaq
worker setup and related Docker services.
- `redis_url` – default `redis://localhost:6379/`. Used when background jobs are
enabled.
- `mongodb_url` – default `mongodb://user:password@localhost:27017/`. Seed
connection string written to `.env.local`.
- `enable_watchtower` – default `false`. Only prompted when `fqdn` is set; adds

Watchtower service to production Docker Compose.

### Supplying Values Non-Interactively

- `--defaults` answers all prompts with defaults.
- `--data key=value` overrides individual answers (repeat the flag for multiple
overrides).
- `--template` lets you point at a different Copier template source (local path,
git URL, or `github:user/repo`).

## Post-Generation Tasks

After `vibetuner scaffold new`, Copier executes the commands listed in `copier.yml`:

- `just git-init {{ project_slug }}` – initializes a git repository and tags `v0.0.1`.
- `uv sync` – installs Python dependencies defined by the scaffold.
- `mise trust` – trusts the generated `.mise.toml` (optional tooling setup). *
- `uv run pre-commit install` – installs the repository’s pre-commit hooks.
> \* See the mise documentation for details; no additional action is required if you skip mise.

## Updating Existing Projects

There are two supported update flows:

1. **`vibetuner scaffold update`** (works everywhere)
- Reads `.copier-answers.yml` and reapplies the latest template files.
- Respects previous answers by default; pass `--no-skip-answered` to revisit prompts.
- Runs the same post-generation tasks after updating files.
2. **`just update-scaffolding`** (inside generated projects)
- Shells out to `copier update -A --trust`, then re-syncs dependencies (`bun install`, `uv sync --all-extras`).

- Useful when you already have the project checked out with the scaffolded `justfile`.

Both commands update tracked files. Always commit or stash local changes before
running them, review the results, and resolve any merge prompts Copier surfaces.

## Recommended Workflow

1. Commit your working tree.
2. Run either `vibetuner scaffold update` or `just update-scaffolding`.
3. Re-run tests (`just test-build-prod`, `just dev`) to confirm nothing broke.
4. Commit the changes produced by the update.

Refer back to this document whenever you need to adjust template answers,
automate non-interactive scaffolding, or keep existing projects in sync with the
latest Vibetuner release.
