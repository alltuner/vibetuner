---
allowed-tools: BashOutput, mcp__playwright__browser_navigate, mcp__playwright__browser_take_screenshot, mcp__playwright__browser_wait_for
argument-hint: [url]
description: Open app in Playwright browser and wait for authentication
---

I'll open your application in a Playwright browser and wait for you to authenticate.

**URL:** ${1:-<http://localhost:8000}>

First, I'll use the web-app-runner agent to ensure the application is running:

The web-app-runner agent will check if the development environment is running on port 8000 and start it if needed (both `pnpm dev` and `just local-dev` processes). Then I'll:

1. 🌐 Open ${1:-<http://localhost:8000}> in Playwright browser
2. 📸 Take a screenshot so you can see the current state  
3. ⏸️ Wait for you to complete authentication in the browser
4. ✅ Once you're authenticated, I'll be ready for automated testing

**Usage examples:**

- `/auth-test` → Opens localhost:8000
- `/auth-test http://localhost:8080` → Opens custom URL

**What to expect:**

1. Browser window will open with your application
2. You'll see the login/authentication page
3. Complete the authentication process (OAuth, magic link, etc.)
4. Tell me when you're ready to continue testing

This is perfect for testing authenticated flows, protected routes, and user-specific functionality.
