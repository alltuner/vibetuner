# Agent Guidance

Looking for instructions tailored to AI coding assistants?

Use [`CLAUDE.md`](./CLAUDE.md). It is the canonical, maintained guide for all
agents (Claude, Cursor, ChatGPT, etc.) that interact with this repository.

## PR Title Conventions for AI Assistants

This project uses **Release Please** for automated changelog generation. When creating PRs, use **conventional commit format** for PR titles:

### Required Format

```text
<type>[optional scope]: <description>
```

### Supported Types

- `feat:` New features (triggers MINOR version)
- `fix:` Bug fixes (triggers PATCH version)
- `docs:` Documentation changes (triggers PATCH version)
- `chore:` Maintenance, dependencies (triggers PATCH version)
- `refactor:` Code refactoring (triggers PATCH version)
- `style:` Formatting, linting (triggers PATCH version)
- `test:` Test changes (triggers PATCH version)
- `perf:` Performance improvements (triggers MINOR version)
- `ci:` CI/CD changes (triggers PATCH version)
- `build:` Build system changes (triggers PATCH version)

### Breaking Changes

Add `!` to indicate breaking changes (triggers MAJOR version):

- `feat!: remove deprecated API`
- `fix!: change database schema`

### Examples

```text
feat: add OAuth authentication support
fix: resolve Docker build failure
docs: update installation guide
chore: bump FastAPI dependency
feat!: remove deprecated authentication system
```

### Why This Matters

- PR titles become commit messages after squash
- Release Please analyzes these to determine version bumps
- Automatic changelog generation from PR titles
- Professional release notes for users

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for detailed guidelines.
