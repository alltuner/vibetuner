---
name: readme
description: Create or update a beautiful README.md file with emojis and project info
allowed-tools: Read(*), Write(*), Glob(*)
---

Create or update a comprehensive and visually appealing README.md file for this project. Make it engaging with:

🎯 **Requirements:**

- Use plenty of relevant emojis throughout
- Include project name, description, and key features
- Add usage examples and API documentation
- Add development workflow and contribution guidelines
- Include technology stack and architecture overview
- Make it professional yet fun and engaging
- Use proper markdown formatting with badges, tables, and code blocks
- **ALWAYS run `bun markdownlint --fix README.md` after generating/modifying the README**
- **Fix any linting errors reported by markdownlint to ensure clean, properly formatted markdown**

📋 **Structure to include:**

- Eye-catching header with project name and description
- Project description and key features
- Quick start guide for development
- Configuration guide
- API documentation (if applicable)
- Development workflow
- Technology stack
- Project structure overview
- Contributing guidelines

🎨 **Style guidelines:**

- Use emojis strategically for visual appeal
- Include relevant badges (build status, version, etc.)
- Use tables for structured information
- Add code examples with proper syntax highlighting
- Make navigation easy with table of contents
- Keep it concise but comprehensive

Base the content on the project configuration found in `.copier-answers.yml`, `justfile`, and other project files to ensure accuracy.
