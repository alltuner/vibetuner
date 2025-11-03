# vibetuner

Blessed Python dependencies for Vibetuner projects.

This package provides a curated set of Python dependencies that form AllTuner's standard stack for web applications:

- **FastAPI** + **MongoDB** (Beanie ODM)
- **OAuth** + **Magic Link** authentication (Authlib)
- **Background task processing** (Redis + Streaq)
- **CLI tools** (Typer)
- **Rich logging** (Loguru)
- And more...

## Installation

```bash
# Using pip
pip install vibetuner

# Using uv
uv add vibetuner

# With development dependencies
uv add vibetuner[dev]
```

## Usage

Simply add `vibetuner` as a dependency in your project. All blessed dependencies will be available.

For the JavaScript/frontend companion package, see [@alltuner/vibetuner](https://www.npmjs.com/package/@alltuner/vibetuner).

## License

MIT
