# CLI Reference

Command-line entry points provided by the `vibetuner` package.

!!! note "Package name convention"
    In all examples, `app` refers to your project's Python package (the directory under `src/`).
    The actual name depends on your project slug (e.g., `src/myproject/` for a project named
    "myproject").

## `vibetuner scaffold`

### `new`

```bash
vibetuner scaffold new DESTINATION [options]
```

Creates a project from the local Vibetuner Copier template.

#### Options

- `--template`, `-t` – Use a different template source (local path, git URL,
`github:user/repo`, etc.).
- `--defaults`, `-d` – Accept default answers for every prompt (non-interactive).
- `--data key=value` – Override individual template variables. Repeat for
multiple overrides.
- `--branch`, `-b` – Use specific branch/tag from the vibetuner template repository.
- `DESTINATION` must not already exist.

#### Examples

```bash
# Interactive run
vibetuner scaffold new my-project
# Non-interactive defaults
vibetuner scaffold new my-project --defaults
# Override selected values in non-interactive mode
vibetuner scaffold new my-project \
--defaults \
--data project_name="My Project" \
--data python_version="3.12"

# Test from a specific branch
vibetuner scaffold new my-project --branch fix/scaffold-command
```

See the [Scaffolding Reference](scaffolding.md) for a complete description of
template prompts and post-generation tasks.

### `update`

```bash
vibetuner scaffold update [PATH] [options]
```

Brings an existing project up to date with the current template.

- `PATH` defaults to the current directory.
- `--skip-answered / --no-skip-answered` controls whether previously answered
prompts are re-asked (defaults to skipping).
- `--branch`, `-b` – Use specific branch/tag from the vibetuner template repository.
- Exits with an error if `.copier-answers.yml` is missing.

### `adopt`

```bash
vibetuner scaffold adopt [PATH] [options]
```

Adopts vibetuner scaffolding for an existing project that already has vibetuner as a dependency.

- `PATH` defaults to the current directory.
- Requires `pyproject.toml` with vibetuner in dependencies.
- Fails if `.copier-answers.yml` already exists (use `update` instead).

#### Options

- `--defaults`, `-d` – Accept default answers for every prompt (non-interactive).
- `--data key=value` – Override individual template variables.
- `--branch`, `-b` – Use specific branch/tag from the vibetuner template repository.

## `vibetuner run`

Starts framework services without Docker.

### `dev`

```bash
vibetuner run dev [frontend|worker] [--port PORT] [--host HOST] [--workers COUNT] [--auto-port]
```

- `--auto-port` – Use deterministic port based on project path (8001-8999). Mutually exclusive
  with `--port`.

```bash
# Example with auto-port (uses deterministic port 8001-8999)
vibetuner run dev --auto-port
```

- Sets `DEBUG=1` and enables hot reload.
- `service` defaults to `frontend`.
- Frontend watches `src/app/` and `templates/` for changes.
- Worker runs the Streaq worker with reload enabled (ignores `--workers` > 1).

### `prod`

```bash
vibetuner run prod [frontend|worker] [--port PORT] [--host HOST] [--workers COUNT]
```

- Sets `ENVIRONMENT=production`.
- Disables hot reload and honors `--workers` for both frontend and worker services.
- Useful for containerless deployments or reproducing production settings locally.

## `vibetuner db`

Database management commands for SQL databases (SQLModel/SQLAlchemy).

### `create-schema`

```bash
vibetuner db create-schema
```

Creates all database tables defined in SQLModel metadata. This command:

1. Imports models from `app.models` to ensure they're registered
2. Creates tables in the database specified by `DATABASE_URL`
3. Skips if tables already exist (safe to run multiple times)

**Prerequisites:**

- `DATABASE_URL` environment variable must be set
- Models must be defined using SQLModel with `table=True`

**Example:**

```bash
# Set database URL
export DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb

# Create tables
vibetuner db create-schema
```

**Note:** This command is only for SQL databases. MongoDB collections are created
automatically when documents are inserted.

## `vibetuner version`

Show version information.

```bash
vibetuner version [--app]
```

### Options

- `--app`, `-a` – Show app settings version even if not in a project directory.

## Related Commands

Generated projects expose additional helpers in the scaffolded `justfile`:

### Development

- `just local-all` – Runs server + assets in parallel with auto-port (recommended for local dev)
- `just local-all-with-worker` – Same as above but includes background worker (requires Redis)
- `just local-dev` – Runs server only (use with `bun dev` in separate terminal)
- `just worker-dev` – Runs background worker only
- `just update-scaffolding` – Updates project to latest template

Use `just --list` inside a generated project to see all available commands.
