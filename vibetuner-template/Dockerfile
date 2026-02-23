# syntax=docker/dockerfile:1-labs  # Required for advanced features like --parents flag

ARG PYTHON_VERSION=3.14

# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Base Python Environment with UV Package Manager
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS python-base

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt-get update && apt-get install -y --no-install-recommends git

# Install UV package manager from official image
COPY --from=ghcr.io/astral-sh/uv:0.10 /uv /uvx /bin/

# Configure UV for optimal performance and behavior
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# ────────────────────────────────────────────────────────────────────────────────
# Stage 2: Install Dependencies Only (cached when deps unchanged)
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS python-deps

# Install runtime dependencies only (excluding dev dependencies and the project itself)
# This creates a dependency cache layer that rarely changes
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-install-project --no-group dev

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Install Project (editable mode for source access)
# ────────────────────────────────────────────────────────────────────────────────
FROM python-deps AS python-app

# Copy application source code
COPY src/ src/

# Install project in editable mode and copy vibetuner templates
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --frozen --no-group dev && \
    cp -r $(.venv/bin/python -c "import vibetuner; print(vibetuner.__path__[0])")/templates/frontend .core-templates

# Clean up test and documentation files from dependencies (failures are non-fatal)
RUN find .venv -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true && \
    find .venv -type f \( -name '*.md' -o -name '*.rst' -o -name '*.txt' \) ! -path '*/METADATA' -delete 2>/dev/null || true

# ────────────────────────────────────────────────────────────────────────────────
# Stage 4: Compile Localization Files (parallel with frontend)
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS locales

WORKDIR /app

# Copy localization source files
COPY locales/ locales/

# Compile .po files to .mo files if any locales exist
RUN find locales -mindepth 1 -maxdepth 1 -type d -name '??' 2>/dev/null | grep -q . \
    && uvx --from babel pybabel compile -d locales || echo "No locales to compile"

# ────────────────────────────────────────────────────────────────────────────────
# Stage 5: Install Frontend Dependencies (parallel with locales)
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

# Copy templates for Tailwind CSS class scanning
COPY templates/frontend/ templates/frontend/
COPY --from=python-app /app/.core-templates/ .core-templates/

# Build production assets with Bun
RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=config.css,target=config.css \
    --mount=type=bind,source=config.js,target=config.js \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=bun.lock,target=bun.lock \
    bun run build-prod

# ────────────────────────────────────────────────────────────────────────────────
# Stage 7: Final Runtime Image (fresh base, no build tools)
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG ENVIRONMENT=dev
ARG VERSION=0.0.0

WORKDIR /app

# Copy Python virtual environment with all dependencies and project installed
COPY --link --from=python-app /app/.venv/ .venv/

# Copy application source code (required for editable install)
COPY --link --from=python-app /app/src/ src/

# Copy static assets and markdown content (not full frontend source)
COPY --link assets/statics/ assets/statics/
COPY --link templates/markdown/ templates/markdown/

# Copy compiled localization files (smaller than source .po files)
COPY --link --from=locales --parents /app/locales/*/LC_MESSAGES/messages.mo /

# Copy template files
COPY --link templates/frontend templates/frontend/
COPY --link templates/email templates/email/

# Copy built frontend assets (CSS and JS bundles)
COPY --link --from=frontend-build /app/assets/statics/css/bundle.css assets/statics/css/bundle.css
COPY --link --from=frontend-build /app/assets/statics/js/bundle.js assets/statics/js/bundle.js

# Copy configuration files (used as project root marker and for package metadata)
COPY --link .copier-answers.yml pyproject.toml ./

# Copy startup script with executable permissions (--chmod eliminates separate RUN layer)
COPY --link --chmod=755 start.sh /start.sh

# Configure environment for Python application
ENV PATH="/app/.venv/bin:$PATH" \
    ENVIRONMENT=${ENVIRONMENT} \
    APP_VERSION=${VERSION} \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
