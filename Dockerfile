# ────────────────────────────────────────────────────────────────────────────────
# Stage 1: Python Dependencies Cache
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.13-alpine AS python-base

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
    uv sync --locked --no-install-project --no-dev

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
    uv sync --locked --no-dev

# ────────────────────────────────────────────────────────────────────────────────
# Stage 3: Frontend Dependency Builder Base (with PNPM)
# ────────────────────────────────────────────────────────────────────────────────
FROM node:24-alpine AS frontend-deps-base

# Set up PNPM with corepack
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable && corepack prepare pnpm@latest --activate

# ────────────────────────────────────────────────────────────────────────────────
# Stage 4: Frontend Build Stage
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
# Stage 5: Final Image
# ────────────────────────────────────────────────────────────────────────────────
FROM python:3.13-alpine AS runtime

WORKDIR /app

COPY --chown=app:app src/ src/
COPY --chown=app:app frontend/templates/ frontend/templates/

# Copy built frontend static assets
COPY --from=frontend-build /app/frontend/statics/ frontend/statics/

# Copy Python app with installed virtualenv
COPY --from=python-base --chown=app:app /app/.venv/ .venv/
COPY --from=python-versioning --chown=app:app /app/src/alibey/_version.py src/alibey/_version.py

# Make sure the virtualenv binaries come first
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Default command: run FastAPI app
CMD ["fastapi", "run", "src/alibey/frontend"]
