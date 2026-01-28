# syntax=docker/dockerfile:1-labs  # Required for advanced features like --parents flag
# Test Dockerfile - generates a test project using copier and builds it

ARG PYTHON_VERSION=3.14

# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Frontend dependencies
# ────────────────────────────────────────────────────────────────────────────────
FROM oven/bun:1-alpine AS frontend-deps

WORKDIR /app

RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=vibetuner-template/package.json,target=package.json \
    --mount=type=bind,source=vibetuner-template/bun.lock,target=bun.lock \
    bun install --frozen-lockfile

# ────────────────────────────────────────────────────────────────────────────────
# Stage 2: Build frontend assets
# ────────────────────────────────────────────────────────────────────────────────
FROM frontend-deps AS frontend-build

# Build production assets with Bun
RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=vibetuner-template/config.css,target=config.css \
    --mount=type=bind,source=vibetuner-template/config.js,target=config.js \
    --mount=type=bind,source=vibetuner-template/package.json,target=package.json \
    --mount=type=bind,source=vibetuner-template/bun.lock,target=bun.lock \
    bun run build-prod

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Python base with uv
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS python-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y --no-install-recommends git

# Install UV package manager from official image
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# Configure UV for optimal performance and behavior
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# ────────────────────────────────────────────────────────────────────────────────
# Stage 4: Generate test project with copier
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS python-scaffold

COPY copier.yml /template/copier.yml
COPY vibetuner-template /template/vibetuner-template
COPY vibetuner-py /vibetuner-py

RUN --mount=type=cache,target=/root/.cache/uv \
    uvx copier copy --trust --skip-tasks --defaults --data project_slug=vibetuner-test /template .

# Add local vibetuner source override
RUN --mount=type=bind,source=uv-sources.toml,target=/uv-sources.toml \
    cat /uv-sources.toml >> pyproject.toml

# ────────────────────────────────────────────────────────────────────────────────
# Stage 5: Install Python dependencies and project (non-editable)
# ────────────────────────────────────────────────────────────────────────────────
FROM python-scaffold AS python-app

# Install project non-editable with cleanup
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=vibetuner-py,target=/vibetuner-py \
    uv sync --no-editable --no-group dev && \
    find .venv -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true && \
    find .venv -type f \( -name '*.md' -o -name '*.rst' -o -name '*.txt' \) ! -path '*/METADATA' -delete 2>/dev/null || true

# ────────────────────────────────────────────────────────────────────────────────
# Stage 6: Runtime image (fresh base, no build tools)
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

WORKDIR /app

# Copy Python virtual environment with all dependencies and project installed
COPY --link --from=python-app /app/.venv/ .venv/

# Copy static assets
COPY --link --from=python-app /app/assets/ assets/

# Copy templates
COPY --link --from=python-app /app/templates/ templates/

# Copy built frontend assets (CSS and JS bundles)
COPY --link --from=frontend-build /app/assets/statics/css/bundle.css assets/statics/css/bundle.css
COPY --link --from=frontend-build /app/assets/statics/js/bundle.js assets/statics/js/bundle.js

# Copy configuration file (used as project root marker)
COPY --link --from=python-app /app/.copier-answers.yml ./

# Copy startup script
COPY --link --from=python-app /app/start.sh /start.sh

# Configure environment for Python application
# No PYTHONPATH needed - app is installed in site-packages via non-editable install
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
