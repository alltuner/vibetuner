# syntax=docker/dockerfile:1-labs  # Required for advanced features like --parents flag

ARG PYTHON_VERSION=3.13

FROM oven/bun:1-alpine AS frontend-base

WORKDIR /app

RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=vibetuner-template/package.json,target=package.json \
    --mount=type=bind,source=vibetuner-template/bun.lock,target=bun.lock \
    bun install --frozen-lockfile

FROM python:${PYTHON_VERSION}-slim AS python-base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install UV package manager from official image
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /uvx /bin/

# Configure UV for optimal performance and behavior
ENV UV_COMPILE_BYTECODE=0 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0 \
    UV_NO_GROUP=dev

COPY copier.yml /template/copier.yml
COPY vibetuner-template /template/vibetuner-template
COPY vibetuner-py /vibetuner-py

RUN --mount=type=cache,target=/root/.cache/uv \
    uvx copier copy --trust --skip-tasks --defaults --data project_slug=vibetuner-test /template .

RUN --mount=type=bind,source=uv-sources.toml,target=/uv-sources.toml \
    cat /uv-sources.toml >> pyproject.toml


RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=vibetuner-py,target=/vibetuner-py \
    uv sync --no-editable

FROM frontend-base AS build-frontend

WORKDIR /app

# Build production assets with Bun
RUN --mount=type=cache,id=bun,target=/root/.bun/install/cache \
    --mount=type=bind,source=vibetuner-template/config.css,target=config.css \
    --mount=type=bind,source=vibetuner-template/config.js,target=config.js \
    --mount=type=bind,source=vibetuner-template/package.json,target=package.json \
    --mount=type=bind,source=vibetuner-template/bun.lock,target=bun.lock \
    bun run build-prod

FROM python-base AS final

WORKDIR /app

# Copy built frontend assets (CSS and JS bundles)
COPY --from=build-frontend /app/assets/statics/css/bundle.css assets/statics/css/bundle.css
COPY --from=build-frontend /app/assets/statics/js/bundle.js assets/statics/js/bundle.js

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]
