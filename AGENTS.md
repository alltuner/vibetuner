# Agent Guidance

Looking for instructions tailored to AI coding assistants?

Use [`CLAUDE.md`](./CLAUDE.md). It is the canonical, maintained guide for all
agents (Claude, Cursor, ChatGPT, etc.) that interact with this repository.

## PR Title Conventions for AI Assistants

This project uses **Release Please** for automated changelog generation.
When creating PRs, use **conventional commit format** for PR titles:

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
- Every merged PR creates/updates a Release Please PR
- Release happens when the Release Please PR is merged
- Automatic changelog generation from PR titles
- Professional release notes for users

### Release Workflow

1. Merge any PR → Release Please creates/updates a release PR
2. Review the release PR (version bump + changelog)
3. Merge the release PR when ready to release
4. Release Please publishes the release and triggers package publishing

See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for detailed guidelines.

## Testing Scaffold Changes from a Branch

When working on scaffold-related changes (template updates, CLI improvements), you can test
the scaffolding CLI directly from a branch without publishing to PyPI:

```bash
# Test scaffold command from a specific branch
uvx git+https://github.com/alltuner/vibetuner@BRANCH_NAME#subdirectory=vibetuner-py scaffold new --help

# Create a test project using the branch
uvx git+https://github.com/alltuner/vibetuner@BRANCH_NAME#subdirectory=vibetuner-py scaffold new /tmp/test-project
```

The scaffold command also accepts a `-b` parameter to specify the branch dynamically:

```bash
# Specify branch with -b parameter (when available)
uvx git+https://github.com/alltuner/vibetuner#subdirectory=vibetuner-py scaffold new -b BRANCH_NAME /tmp/test-project
```

**When to use this:**

- Testing scaffold changes before merging a PR
- Verifying bug fixes in template or CLI
- Allowing others to test your changes before review
- CI/CD integration testing

**Note:** The repository includes a `tmp/` directory at the root with its contents
automatically ignored by git. Use this directory for testing scaffold commands if you have
difficulty accessing external directories like `/tmp`:

```bash
# Test scaffolding in the repo's tmp directory
uvx git+https://github.com/alltuner/vibetuner@BRANCH_NAME#subdirectory=vibetuner-py scaffold new ./tmp/test-project
```

See `vibetuner-docs/docs/development.md` for complete development workflows.
