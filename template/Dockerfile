# syntax=docker/dockerfile:1-labs  # This is required to be able to use --parents

ARG PYTHON_VERSION=3.13

# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Python Dependencies Cache
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS python-base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Speed up and optimize UV behavior
ENV UV_COMPILE_BYTECODE=1 \
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

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Localizations
# ────────────────────────────────────────────────────────────────────────────────
FROM python-versioning AS locales

WORKDIR /app

COPY locales/ locales/

RUN --mount=type=cache,target=/root/.cache/uv \
    uvx --from babel pybabel compile -d locales | true

# ────────────────────────────────────────────────────────────────────────────────
# Stage 4: Frontend Dependency Builder Base (with PNPM)
# ────────────────────────────────────────────────────────────────────────────────
FROM node:24-alpine AS frontend-deps-base

# Set up PNPM with corepack
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@latest --activate

# ────────────────────────────────────────────────────────────────────────────────
# Stage 5: Frontend Build Stage
# ────────────────────────────────────────────────────────────────────────────────
FROM frontend-deps-base AS frontend-build

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
# Install frontend dependencies
RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile

# Copy frontend source code and build it
COPY frontend/ frontend/
RUN pnpm run build-prod

# ────────────────────────────────────────────────────────────────────────────────
# Stage 6: Final Image
# ────────────────────────────────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim AS runtime

ARG ENVIRONMENT=development

WORKDIR /app

COPY --chown=app:app src/ src/
COPY --chown=app:app frontend/templates/ frontend/templates/

COPY start.sh /start.sh
RUN chmod +x /start.sh

# Copy the .mo files from the locales stage
COPY --from=locales --chown=app:app --parents /app/locales/*/LC_MESSAGES/messages.mo /

# Copy static assets (images, favicons, etc.)
COPY --chown=app:app frontend/statics/ frontend/statics/

# Copy built frontend static assets (JS and CSS bundles)
COPY --from=frontend-build /app/frontend/statics/ frontend/statics/

# Copy Python app with installed virtualenv
COPY --from=python-base --chown=app:app /app/.venv/ .venv/

# Copy the python scripts binaries from the built virtualenv
COPY --from=python-versioning --chown=app:app  /app/.venv/bin/ .venv/bin/

# By specifying the --parents flag, we can copy the _version.py files without
# having to explicityly name the directories, allowing us to reuse this Dockerfile
COPY --from=python-versioning --chown=app:app --parents /app/src/*/_version.py /

# Make sure the virtualenv binaries come first
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH="/app/src"

ENV ENVIRONMENT=${ENVIRONMENT}

EXPOSE 8000

ENTRYPOINT ["/start.sh"]
