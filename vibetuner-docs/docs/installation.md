# Installation

## System Requirements

- **Python 3.11 or higher**
- **uv** (Python package manager) - recommended
- **Docker** (optional, for containerized development)

## Installing Vibetuner

### Option 1: No Installation (Recommended)

Use `uvx` to run Vibetuner without installing:

```bash
uvx vibetuner scaffold new my-project
```

This downloads and runs Vibetuner temporarily. No installation, no cleanup needed.

### Option 2: Global Installation

Install Vibetuner globally with uv:

```bash
uv tool install vibetuner
```

Then use it anywhere:

```bash
vibetuner scaffold new my-project
```

### Option 3: Using pip

```bash
pip install vibetuner
vibetuner scaffold new my-project
```

## Installing uv

If you don't have `uv` installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Visit [docs.astral.sh/uv](https://docs.astral.sh/uv/) for more installation options.

## Installing Docker (Optional)

Docker is optional but recommended for consistent development environments.

### macOS

Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

### Linux

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | sh
# Start Docker
sudo systemctl start docker
sudo systemctl enable docker
```

### Windows

Download Docker Desktop from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/)

## Verifying Installation

Test that everything works:

```bash
# Check Python version
python --version  # Should be 3.11 or higher
# Check uv
uv --version
# Check Docker (optional)
docker --version
# Test Vibetuner
uvx vibetuner --help
```

## Creating Your First Project

Once installed, create a new project:

```bash
uvx vibetuner scaffold new my-app
cd my-app
just dev
```

Visit `http://localhost:8000` to see your running application.

## Troubleshooting

### "Command not found: uvx"

Make sure uv is installed and in your PATH:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

### "Python 3.11 not found"

Install Python 3.11 or higher:

```bash
# macOS with Homebrew
brew install python@3.11
# Ubuntu/Debian
sudo apt install python3.11
# Or use uv to manage Python versions
uv python install 3.11
```

### Docker connection errors

Make sure Docker is running:

```bash
docker ps
```

If Docker isn't running, start Docker Desktop or:

```bash
sudo systemctl start docker  # Linux
```

## Next Steps

- [Quick Start](quick-start.md) - Create your first project
- [Development Guide](development-guide.md) - Daily development workflow
