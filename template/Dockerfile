# syntax=docker/dockerfile:1-labs  # Required for advanced features like --parents flag

ARG PYTHON_VERSION=3.13

# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Base Python Environment with UV Package Manager
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS python-base

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager from official image
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# Configure UV for optimal performance and behavior
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install runtime dependencies only (excluding dev dependencies and the project itself)
# This creates a dependency cache layer that rarely changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --locked --no-install-project --no-group dev

# ────────────────────────────────────────────────────────────────────────────────
# Stage 2: Install Project with Version Information
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS python-versioning

WORKDIR /app

# Copy application source code
COPY src/ src/

# Set version for dynamic versioning
ARG VERSION=0.0.0
ENV UV_DYNAMIC_VERSIONING_BYPASS=$VERSION

# Install the project with all extras but still exclude dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --all-extras --locked --no-group dev

# Clean up test directories to reduce image size
RUN find .venv -type d -name 'tests' -exec rm -rf {} +

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Compile Localization Files
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS locales

WORKDIR /app

# Copy localization source files
COPY locales/ locales/

# Compile .po files to .mo files if any locales exist
RUN find locales -mindepth 1 -maxdepth 1 -type d -name '??' 2>/dev/null | grep -q . \
    && uvx --from babel pybabel compile -d locales || echo "No locales to compile"

# ────────────────────────────────────────────────────────────────────────────────
# Stage 5: Install Frontend Dependencies
# ────────────────────────────────────────────────────────────────────────────────
FROM oven/bun:1-alpine AS frontend-deps

WORKDIR /app

# Install frontend dependencies using lockfile
RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=bun.lock,target=bun.lock \
    bun install --frozen-lockfile

# ────────────────────────────────────────────────────────────────────────────────
# Stage 6: Build Frontend Assets
# ────────────────────────────────────────────────────────────────────────────────
FROM frontend-deps AS frontend-build

COPY /templates/frontend/ templates/frontend/

# Build production assets with Bun
RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=config.css,target=config.css \
    --mount=type=bind,source=config.js,target=config.js \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=bun.lock,target=bun.lock \
    bun run build-prod

# ────────────────────────────────────────────────────────────────────────────────
# Stage 7: Final Runtime Image
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG ENVIRONMENT=development

WORKDIR /app

# Copy Python virtual environment with all dependencies and project
COPY --from=python-versioning --chown=app:app /app/.venv/ .venv/

# Copy static assets and markdown content (not full frontend source)
COPY --chown=app:app assets/statics/ assets/statics/
COPY --chown=app:app templates/markdown/ templates/markdown/

# Copy compiled localization files (smaller than source .po files)
COPY --from=locales --chown=app:app --parents /app/locales/*/LC_MESSAGES/messages.mo /

# Copy template files
COPY --chown=app:app templates/frontend templates/frontend/
COPY --chown=app:app templates/email templates/email/

# Copy built frontend assets (CSS and JS bundles)
COPY --from=frontend-build --chown=app:app /app/assets/statics/css/bundle.css assets/statics/css/bundle.css
COPY --from=frontend-build --chown=app:app /app/assets/statics/js/bundle.js assets/statics/js/bundle.js

# Copy application source code
COPY --chown=app:app src/ src/

# Copy version files from the versioning stage
COPY --from=python-versioning --chown=app:app --parents /app/src/core/_version.py /

# Copy configuration file
COPY --chown=app:app .copier-answers.yml ./

# Copy and make startup script executable
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Configure environment for Python application
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    ENVIRONMENT=${ENVIRONMENT} \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
