---
paths:
  - Dockerfile*
  - docker-compose*
  - justfile
description: Docker registry, CI/CD recipes, and deployment patterns
---

# Deployment

## Docker Registry

`DOCKER_REGISTRY` controls where images are pushed and pulled.
Configured during scaffolding via the `docker_registry` copier
question (stored in `.copier-answers.yml`). The `DOCKER_REGISTRY`
environment variable overrides the stored value. Defaults to
`localhost:5050` (for use with a local registry proxy).

```bash
# Build and push to the configured registry
just release

# Push to a local registry proxy instead (e.g., Switchyard)
PUSH_REGISTRY=localhost:5050 just release
```

`PUSH_REGISTRY` overrides `DOCKER_REGISTRY` for the push target
only. This is useful when a local registry proxy syncs to the
central registry asynchronously, giving you fast local pushes.

## Deploying

`deploy-latest` pulls and runs the image on a remote host via SSH.
It is decoupled from `release`, so you can push and deploy separately.

```bash
just deploy-latest user@myhost
```

## CI/CD Recipes

- `just build-dev` - Build the dev Docker image
- `just test-build-prod` - Test-build the prod image locally
- `just build-prod` - Build the prod image (requires clean, tagged commit)
- `just release` - Build and push (requires clean, tagged commit)
- `just deploy-latest HOST` - Pull and run on a remote host
