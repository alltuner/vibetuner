# Upgrading Your Project

This page covers the general workflow for keeping a Vibetuner project current. For
version-specific breaking changes, see the migration guides listed at the bottom.

## Versioning Policy

Vibetuner follows [semantic versioning](https://semver.org/). Version bumps are driven
by the conventional-commit type of each merged PR, processed automatically by
[Release Please](https://github.com/googleapis/release-please):

| Change type | Example PR title | Version bump |
|-------------|------------------|--------------|
| Breaking change | `feat!: remove deprecated API` | **MAJOR** |
| New feature | `feat: add OAuth support` | MINOR |
| Performance | `perf: speed up SSE fan-out` | MINOR |
| Bug fix, docs, chore | `fix: resolve Redis timeout` | PATCH |

**MAJOR version upgrades always include a migration guide.** MINOR and PATCH upgrades
are safe to apply without code changes in the common case.

The full history is in the
[CHANGELOG](https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md). Breaking
changes are flagged with a `⚠ BREAKING CHANGES` header and include migration instructions.

## Updating the Scaffold Template

Your project was generated from the Vibetuner Copier template. As the template evolves
(new justfile targets, updated compose files, tooling improvements), pull the latest
template changes into your project:

```bash
vibetuner scaffold update
```

This runs Copier's update against the latest template revision. For each file that has
changed since your last update, Copier shows the diff and asks you to accept or skip it.
Review changes carefully for any files you have customised (e.g. `compose.prod.yml`,
`.env.example`, `justfile`).

### Common options

| Flag | Default | Description |
|------|---------|-------------|
| `--skip-answered` | on | Re-uses your original answers — no prompts for settings you already configured |
| `--no-skip-answered` | — | Re-prompts for every question — use when you need to change project settings |
| `--branch BRANCH` | `main` | Pull from a specific template branch instead of the latest `main` |

### After running scaffold update

1. Review the diff: `git diff`
2. Resolve any merge conflicts in customised files
3. Sync dependencies: `uv sync`
4. Restart: `just dev`
5. Run `vibetuner doctor` to confirm everything is healthy (see [Troubleshooting](troubleshooting.md))

## Upgrading the Framework Package

`vibetuner scaffold update` updates the **template scaffold** (project files, justfile,
compose, tooling). It does **not** bump the `vibetuner` Python package version. To
upgrade the framework itself:

```bash
uv add "vibetuner>=NEW_VERSION"
```

Or to always track the latest release:

```bash
uv add vibetuner@latest
```

For **MAJOR version upgrades**, read the relevant migration guide before running the
version bump. After upgrading, run `vibetuner doctor` to catch configuration issues
early.

## Version-Specific Migration Guides

| Upgrading from | To | Guide |
|----------------|----|-------|
| v11.x | v12 | [Upgrading to v12](upgrading-to-v12.md) — fail-closed `SESSION_KEY`, Jinja autoescaping, auth rate limits |

### Past breaking changes

#### v10 → v11: `WorkerDepends()` / `TaskDepends()` removed

Vibetuner v11 upgraded to streaq v7, which removed the `WorkerDepends()` and
`TaskDepends()` dependency-injection helpers. See the
[Background Tasks — Worker Context](background-tasks.md#worker-context) section for the
migration callout and the replacement `worker.context` pattern.

Full notes: [PR #1996](https://github.com/alltuner/vibetuner/issues/1996) and the
[v11.0.0 changelog entry](https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md).
