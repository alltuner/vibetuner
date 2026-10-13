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

### Stale `redis_health_check` cron entry

Projects whose worker once ran streaq 6.0-6.2 may have a leftover `redis_health_check`
cron entry in Redis. streaq 6.3 removed that built-in task but not its stored entry, so
the worker logged `task redis_health_check ... skipped, missing function` at ERROR on
every start. The worker now deletes that one entry on startup (unless your app registers
a task with the same name) and logs an INFO line when it does. No action is needed; you
may see the error one last time if a run was already queued before the upgrade.

## Version-Specific Migration Guides

| Upgrading from | To | Guide |
|----------------|----|-------|
| v11.x | v12 | [Upgrading to v12](upgrading-to-v12.md) — fail-closed `SESSION_KEY`, Jinja autoescaping, auth rate limits |

### Past breaking changes

#### v12 → v13: MongoDB datetimes load as timezone-aware UTC

The framework's MongoDB client now uses `tz_aware=True`. Every `datetime` loaded from MongoDB
(including `TimeStampMixin`'s `db_insert_dt` / `db_update_dt`) is timezone-aware UTC instead of
naive. Before, a value saved as aware UTC came back naive, so equality checks against freshly
built aware values silently failed and `TimeStampMixin.age()` raised `TypeError` on loaded
documents.

What to check in your app:

- Code that compares or subtracts loaded datetimes with naive ones (`datetime.utcnow()`, bare
  `datetime.now()`, `datetime(2026, 1, 1)`) now raises `TypeError`. Use `vibetuner.time.now()` or
  `datetime.now(UTC)` and build literals with `tzinfo=UTC`.
- Equality is the quiet case: `==` / `!=` between aware and naive datetimes never raise, they just
  return `False` / `True`. Code that matched loaded values against naively built ones (for example
  in upsert or sync logic) stops matching without an error. Build the comparison side aware too.
- Code that called `.replace(tzinfo=UTC)` on loaded values, or a `field_validator` that reattached
  UTC to naive values, is now redundant and can be removed.
- No data migration is needed. BSON stores datetimes as UTC; only the decoded Python type changes.
  Naive values your code writes are still stored as UTC and now come back aware.

Full notes: [issue #2159](https://github.com/alltuner/vibetuner/issues/2159).

#### v10 → v11: `WorkerDepends()` / `TaskDepends()` removed

Vibetuner v11 upgraded to streaq v7, which removed the `WorkerDepends()` and
`TaskDepends()` dependency-injection helpers. See the
[Background Tasks — Worker Context](background-tasks.md#worker-context) section for the
migration callout and the replacement `worker.context` pattern.

Full notes: [PR #1996](https://github.com/alltuner/vibetuner/issues/1996) and the
[v11.0.0 changelog entry](https://github.com/alltuner/vibetuner/blob/main/CHANGELOG.md).
