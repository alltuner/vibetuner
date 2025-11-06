# Contributing to Vibetuner

Thanks for your interest in Vibetuner! We appreciate you taking the time to explore this project.

## About This Project

Vibetuner was born to meet the needs of [All Tuner Labs](https://alltuner.com) when spawning new projects. It embodies our core beliefs:

- **Simplicity**: Minimal boilerplate, clear conventions
- **Speed of Iteration**: Fast development cycles, hot reload, minimal friction
- **Modern Technology Stack**: Latest stable versions, async-first architecture
- **Good Integration with Coding Assistants**: Well-documented, predictable patterns

## About Contributions

While we welcome feedback and are happy to see community interest, please note:

- **We may not accept all pull requests** - The project serves specific internal needs and design goals
- **Response times may vary** - This is one of many projects we maintain
- **Breaking changes may occur** - We prioritize our internal requirements
- **No guarantees on feature requests** - We'll consider them, but can't commit to implementing everything

That said, we do appreciate good contributions that align with our core beliefs (simplicity,
speed, modern stack, assistant-friendly) and will do our best to review them when time allows.

## Ways to Contribute

### Reporting Issues

If you encounter bugs or have suggestions:

1. **Check existing issues** first to avoid duplicates
2. **Provide clear reproduction steps** - We can't fix what we can't reproduce
3. **Include relevant details**: OS, Python/Node versions, error messages, etc.
4. **Be patient** - We'll respond when we can

### Pull Requests

If you'd like to submit code:

1. **Discuss first** for significant changes - Open an issue before investing time
2. **Follow existing patterns** - Match the code style and architecture
3. **Keep it focused** - Small, targeted PRs are easier to review
4. **Test your changes** - Make sure everything still works
5. **No expectations** - We may decline PRs that don't align with our goals

### Documentation

Documentation improvements are always welcome and generally easier to accept than code changes.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/alltuner/vibetuner
cd vibetuner

# Set up Python package
cd vibetuner-py
uv sync

# Set up JavaScript package
cd ../vibetuner-js
bun install

# Test the scaffold command
uv run --directory ../vibetuner-py vibetuner scaffold new /tmp/test-project
```

## Code Style

- **Python**: Follow existing style, use Ruff for formatting
- **JavaScript**: Follow existing style
- **Templates**: Use djlint for Jinja2 templates
- **Commits**: Clear, concise messages describing the "why"

## PR Title Format (Important!)

This project uses **Release Please** for automated changelog generation. Since we squash PRs,
the **PR title becomes the commit message** that determines version bumps and changelog entries.

### Required Format

```text
<type>[optional scope]: <description>
```

### Supported Types and Version Impact

| Type | Description | Version Impact |
|------|-------------|----------------|
| `feat` | New features | **MINOR** |
| `fix` | Bug fixes | **PATCH** |
| `docs` | Documentation changes | **PATCH** |
| `chore` | Maintenance, dependencies | **PATCH** |
| `refactor` | Code refactoring | **PATCH** |
| `style` | Formatting, linting | **PATCH** |
| `test` | Test changes | **PATCH** |
| `perf` | Performance improvements | **MINOR** |
| `ci` | CI/CD changes | **PATCH** |
| `build` | Build system changes | **PATCH** |

### Breaking Changes

Add `!` to indicate breaking changes (triggers **MAJOR** version):

- `feat!: remove deprecated API`
- `fix!: change database schema`

### Examples

#### ✅ Good PR Titles

```text
feat: add OAuth authentication support
fix: resolve Docker build failure
docs: update installation guide
chore: bump FastAPI dependency
feat(auth): add Google OAuth provider
feat!: remove deprecated authentication system
```

#### ❌ Bad PR Titles (Release Please can't categorize)

```text
Add OAuth
Fix Docker
Update docs
Authentication changes
OAuth implementation
```

### Why This Matters

1. **Automatic Version Detection**: Release Please analyzes PR titles to determine if release
   should be MAJOR/MINOR/PATCH
2. **Changelog Generation**: PR titles become professional changelog entries
3. **Clean History**: Squashed commits follow conventional commit format
4. **Team Communication**: Clear, standardized communication about changes

### Quick Reference

```bash
# New Features → MINOR release
feat: add new feature
feat(scope): specific feature

# Bug Fixes → PATCH release  
fix: resolve issue
fix(scope): specific fix

# Breaking Changes → MAJOR release
feat!: breaking change
BREAKING CHANGE: description

# Documentation → PATCH release
docs: update documentation

# Maintenance → PATCH release
chore: update dependencies
refactor: improve code structure
```

### Development Workflow

During development, your local commit messages can be quick and informal:

```bash
git commit -m "wip"
git commit -m "fix typo"
git commit -m "more work"
```

The **PR title** is what matters for the final release. When creating a PR:

```bash
gh pr create --title "feat: add OAuth authentication support" --body "Detailed description..."
```

### Validation

We have automated PR title validation that will:

- ✅ Allow properly formatted titles
- ❌ Block titles that don't follow conventional commit format
- 💡 Provide helpful error messages to fix issues

## Testing

Before submitting:

```bash
# Format Python code
cd vibetuner-py
ruff format .

# Check for issues
ruff check .

# Test scaffold command
uv run vibetuner scaffold new /tmp/test-project --defaults
cd /tmp/test-project
just dev  # Should start without errors
```

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Open an issue for questions or clarifications. We'll do our best to respond when we can.

## Final Note

We built Vibetuner to solve our own problems, and we're sharing it in case it helps others.
We'll maintain it as our needs evolve, and we'll consider community input when it makes sense.
But this remains primarily an internal tool that happens to be open source.

Thanks for understanding!
