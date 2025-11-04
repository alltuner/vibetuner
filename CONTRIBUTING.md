# Contributing to Vibetuner

Thanks for your interest in Vibetuner! We appreciate you taking the time to explore this project.

## About Contributions

Vibetuner is currently maintained by All Tuner Labs, S.L. as an internal tool that we've decided to share publicly. While we welcome feedback and are happy to see community interest, please note:

- **We may not accept all pull requests** - The project serves specific internal needs and design goals
- **Response times may vary** - This is one of many projects we maintain
- **Breaking changes may occur** - We prioritize our internal requirements
- **No guarantees on feature requests** - We'll consider them, but can't commit to implementing everything

That said, we do appreciate good contributions and will do our best to review them when time allows.

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

We built Vibetuner to solve our own problems, and we're sharing it in case it helps others. We'll maintain it as our needs evolve, and we'll consider community input when it makes sense. But this remains primarily an internal tool that happens to be open source.

Thanks for understanding!
