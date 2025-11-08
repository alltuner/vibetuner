# CLI Reference

Command-line entry points provided by the `vibetuner` package.

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
- Exits with an error if `.copier-answers.yml` is missing.

## `vibetuner run`

Starts framework services without Docker.

### `dev`

```bash
vibetuner run dev [frontend|worker] [--port PORT] [--host HOST] [--workers COUNT]
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

## Related Commands

Generated projects expose additional helpers in the scaffolded `justfile`,
including `just local-dev`, `just worker-dev`, and `just update-scaffolding`,
which wrap the commands above. Use `just --list` inside a generated project to
see everything available.
