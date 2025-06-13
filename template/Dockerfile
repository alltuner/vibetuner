# syntax=docker/dockerfile:1-labs  # This is required to be able to use --parents

ARG PYTHON_VERSION=3.13

# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Python Dependencies Cache
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS python-base

COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/

# Install tools we will use to clean up things later
RUN apt-get update \
    && apt-get install -y --no-install-recommends binutils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Speed up and optimize UV behavior
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Install only runtime dependencies (no dev, no project) to warm the cache
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --locked --no-install-project --no-group dev --no-group scaffolding

# ────────────────────────────────────────────────────────────────────────────────
# Stage 2: Python Project Installation
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS python-versioning

WORKDIR /app

# Copy full application after resolving lock file
COPY src/ src/

ARG VERSION=0.0.0
ENV UV_DYNAMIC_VERSIONING_BYPASS=$VERSION

# Install project into .venv (still without dev dependencies)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=README.md,target=README.md \
    uv sync --locked --no-group dev --no-group scaffolding

RUN find .venv -type d -name 'tests' -exec rm -rf {} + \
    && find .venv -name "*.so" -exec strip {} + 2>/dev/null || true

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Localizations
# ────────────────────────────────────────────────────────────────────────────────
FROM python-base AS locales

WORKDIR /app

COPY locales/ locales/

RUN find locales -mindepth 1 -maxdepth 1 -type d -name '??' 2>/dev/null | grep -q . \
    && uvx --from babel pybabel compile -d locales || echo "No locales to compile"

# ────────────────────────────────────────────────────────────────────────────────
# Stage 4: Frontend Dependency Builder Base (with PNPM)
# ────────────────────────────────────────────────────────────────────────────────
FROM node:24-alpine AS frontend-deps-base

# Set up PNPM with corepack
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@latest --activate

# ────────────────────────────────────────────────────────────────────────────────
# Stage 5: Frontend Dependencies Only (NEW - SPLIT FROM BUILD)
# ────────────────────────────────────────────────────────────────────────────────
FROM frontend-deps-base AS frontend-deps

WORKDIR /app

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=pnpm-lock.yaml,target=pnpm-lock.yaml \
    pnpm install --frozen-lockfile

# ────────────────────────────────────────────────────────────────────────────────
# Stage 6: Frontend Build (CHANGED - INHERIT DEPS)
# ────────────────────────────────────────────────────────────────────────────────
FROM frontend-deps AS frontend-build

# CHANGE: Dependencies already installed, just copy source and build
COPY frontend/ frontend/
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    --mount=type=bind,source=package.json,target=package.json \
    --mount=type=bind,source=pnpm-lock.yaml,target=pnpm-lock.yaml \
    pnpm run build-prod

# ────────────────────────────────────────────────────────────────────────────────
# Stage 6: Final Image
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG ENVIRONMENT=development

WORKDIR /app

# This is more efficient than copying from two different stages
COPY --from=python-versioning --chown=app:app /app/.venv/ .venv/


# OPTIMIZATION: Only copy built assets, not source frontend files
COPY --from=frontend-build --chown=app:app /app/frontend/statics/css/bundle.css frontend/statics/css/bundle.css
COPY --from=frontend-build --chown=app:app /app/frontend/statics/js/bundle.js frontend/statics/js/bundle.js

# OPTIMIZATION: Copy compiled locales (smaller than source .po files)
COPY --from=locales --chown=app:app --parents /app/locales/*/LC_MESSAGES/messages.mo /

# OPTIMIZATION: Copy version files only (much smaller than copying whole build)
COPY --from=python-versioning --chown=app:app --parents /app/src/*/_version.py /

# Copy only essential static assets and templates (not entire frontend/)
COPY --chown=app:app frontend/statics/ frontend/statics/
COPY --chown=app:app frontend/markdown/ frontend/markdown/
COPY --chown=app:app frontend/templates/ frontend/templates/

# Copy source code (this will be the main invalidation point)
COPY --chown=app:app src/ src/

# Copy minimal config files
COPY --chown=app:app .copier-answers.yml ./


COPY start.sh /start.sh
RUN chmod +x /start.sh

# Make sure the virtualenv binaries come first
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    ENVIRONMENT=${ENVIRONMENT} \
    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
