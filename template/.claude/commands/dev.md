---
name: dev
description: Start the development environment (frontend assets + backend server)
---

I'll use the web-app-runner agent to start the development environment with both frontend asset bundling and the backend server.

The web-app-runner agent will:

- Check if the application is already running on port 8000
- If port 8000 is in use, assume the app is running and report the status  
- If not running, start both processes in parallel:
  - `bun dev` for frontend asset bundling (CSS/JS auto-rebuild)
  - `just local-dev` for the FastAPI backend server (Python auto-reload)
- Verify the application is accessible at <http://localhost:8000>

This ensures you have a complete development environment ready for testing and development.
