# Troubleshooting

## `vibetuner doctor`

`vibetuner doctor` is a built-in diagnostic command that inspects your project and
reports issues before they become runtime surprises. Run it any time something
behaves unexpectedly, after upgrading the framework, or when setting up a project
on a new machine.

```bash
vibetuner doctor
```

No arguments are needed — the command auto-detects the project root by walking up
from the current directory.

### When to run it

- After cloning a project for the first time
- After running `vibetuner scaffold update` or `uv add vibetuner@latest`
- When services (MongoDB, Redis) fail to connect
- When the worker stops processing tasks
- When the app refuses to start in production

### Understanding the output

Each check is printed with a status icon:

| Icon | Meaning |
|------|---------|
| `✓` (green) | Check passed |
| `!` (yellow) | Warning — the app may still work, but review this |
| `✗` (red) | Error — this is likely causing a problem |
| `-` (dim) | Skipped — not applicable to your project |

After all checks, a summary table shows total counts. `doctor` exits with code 1
when any errors are found, making it safe to use in CI or pre-deploy scripts:

```bash
vibetuner doctor || exit 1
```

### What doctor checks

#### Project structure

- **Project root** — confirms you are inside a vibetuner project directory
- **.copier-answers.yml** — required for `vibetuner scaffold update` to work
- **.env file** — warns if missing (copy from `.env.example`)
- **src/ layout** — confirms the package directory exists under `src/`

#### App configuration

- **tune.py** — imports your `src/<app>/tune.py` and reports any import errors or
  `ConfigurationError`. If `tune.py` is absent, zero-config mode is active.

#### Environment

- **Environment mode** — shows `dev`, `prod`, or whatever `ENVIRONMENT` is set to
- **SESSION_KEY** — warns when the key is still the shipped placeholder. Set a real
  key with `vibetuner crypto generate-key` before deploying to production.

#### Service connectivity

TCP reachability checks against the hosts and ports parsed from your env vars.
These are quick socket tests — they confirm the service is reachable, not that
credentials are correct.

- **MongoDB** — from `MONGODB_URL` (default port 27017)
- **Redis** — from `REDIS_URL` (default port 6379); skipped if not configured
- **R2/S3 endpoint** — from `R2_BUCKET_ENDPOINT_URL`; skipped if not configured

#### Models

- **Beanie models** — lists all registered MongoDB models; warns if any cannot be
  imported
- **SQL models** — lists registered SQLModel models; skipped if none are registered

#### Templates

- **Templates directory** — warns if `templates/` is missing
- **Template syntax** — scans all `.html`, `.j2`, `.jinja` files for mismatched
  `{%` / `%}` counts (heuristic check)

#### Dependencies

Reports installed versions of `vibetuner`, `fastapi`, `beanie`, `granian`, and
`pydantic`. Errors if a package is not installed at all.

#### Ports

- **Port 8000** — default frontend port; warns if already in use
- **Port 11111** — default worker monitoring UI port; warns if already in use

---

## Common Issues

### App won't start in production

**Symptom:** `ValueError: SESSION_KEY is still the placeholder value.`

**Fix:** Generate a unique key and set it in `.env`:

```bash
vibetuner crypto generate-key
# Copy the output into .env:
# SESSION_KEY=<generated-key>
```

See [Upgrading to v12 — Fail-Closed SESSION_KEY Guard](upgrading-to-v12.md#fail-closed-session_key-guard)
for background.

### Worker stops processing tasks

**Symptoms:** Tasks enqueue but never execute; `vibetuner worker-health` returns unhealthy.

**Steps:**

1. Run `vibetuner doctor` — check the Redis connectivity and port rows.
2. Is Redis running? `just dev` starts it automatically in Docker.
3. Is the worker process running? Check `docker compose ps` or run `just worker-dev`.
4. Check worker logs for `REDIS_SOCKET_TIMEOUT` errors — the worker may have wedged
   on a dropped TCP connection.

See [Background Tasks — Connection Resilience](background-tasks.md#connection-resilience).

### "Redis not configured" error

Add `REDIS_URL` to your `.env`:

```bash
REDIS_URL=redis://localhost:6379
```

### `ImportError` on `WorkerDepends` or `TaskDepends`

These helpers were removed in Vibetuner v11 (streaq v7). Replace the parameter with
`worker.context`. Full details in
[Background Tasks — Worker Context](background-tasks.md#worker-context).

### tune.py import error

`vibetuner doctor` reports this as an error under "App Configuration". Common causes:

- A missing dependency — run `uv sync`
- A missing env var read at import time — check your `.env`
- A syntax error — check the output for the full traceback

### MongoDB or Redis unreachable

`vibetuner doctor` shows `✗ MongoDB: <host>:<port> unreachable` (or Redis). Possible
causes:

- The service is not running. Start it with `just dev` (Docker) or your local
  service manager.
- The URL in `.env` points to the wrong host or port. Copy the correct value from
  `.env.example`.
- A firewall or VPN is blocking the connection.

### Port already in use

`vibetuner doctor` shows `! Frontend default (8000): Port already in use`. Find and
stop the conflicting process, or change the port with `--port` when starting the server.

---

## See Also

- [Upgrading Your Project](upgrading.md) — general upgrade workflow and migration guides
- [Upgrading to v12](upgrading-to-v12.md) — v11 → v12 breaking changes
- [Background Tasks](background-tasks.md) — worker setup and task patterns
- [CLI Reference](cli-reference.md) — all `vibetuner` subcommands
- [Deployment](deployment.md) — production checklist
