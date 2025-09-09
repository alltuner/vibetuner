# Claude Commands for Scaffolding Documentation

This file contains automated commands that Claude Code can use to maintain documentation and generate presentations for the scaffolding project.

## Documentation Maintenance Commands

### Update Scaffolding Overview
```bash
# Command: update-scaffolding-docs
# Description: Updates the main scaffolding overview documentation
# Usage: Automatically scans the codebase and updates SCAFFOLDING_OVERVIEW.md with latest features

claude-command update-scaffolding-docs:
  - Scan copier.yml for new configuration options
  - Check template/ directory for new components
  - Update technology stack descriptions with latest versions
  - Refresh feature descriptions and code examples
  - Update justfile command documentation
  - Validate all links and references
  - Ensure all CLAUDE.md files are documented
  - Update ROI calculations with current metrics
```

### Generate Presentation PDF
```bash
# Command: generate-presentation-pdf
# Description: Converts SCAFFOLDING_OVERVIEW.md to a professional PDF presentation
# Usage: Creates a slide-based PDF suitable for CTO presentations

claude-command generate-presentation-pdf:
  - Parse SCAFFOLDING_OVERVIEW.md structure
  - Extract main sections as slides
  - Create executive summary slide
  - Generate technology stack comparison slides
  - Include code examples and screenshots
  - Create ROI and business case slides  
  - Format with professional styling
  - Output to presentations/scaffolding-overview.pdf
```

### Generate Interactive HTML
```bash
# Command: generate-interactive-html
# Description: Creates a flashy, self-contained HTML presentation with Tailwind styling
# Usage: Generates an interactive web-based presentation for demos

claude-command generate-interactive-html:
  - Convert markdown to HTML with Tailwind CSS
  - Add interactive navigation and animations
  - Include syntax highlighting for code blocks
  - Create responsive design for all devices
  - Add progress indicators and slide transitions
  - Embed images and diagrams inline
  - Include search functionality
  - Generate table of contents with anchor links
  - Output to presentations/scaffolding-overview.html
```

### Sync All Documentation
```bash
# Command: sync-all-docs
# Description: Comprehensive documentation update and validation
# Usage: Updates all documentation files and ensures consistency

claude-command sync-all-docs:
  - Run update-scaffolding-docs
  - Update all CLAUDE.md files in template/
  - Validate documentation links and references
  - Check for outdated command examples
  - Update dependency versions in documentation
  - Ensure consistency across all docs
  - Run spell check and grammar validation
  - Generate change summary report
```

## Content Generation Commands

### Extract Features from Codebase
```bash
# Command: extract-features
# Description: Automatically discovers and documents new scaffolding features
# Usage: Scans codebase to find undocumented features and capabilities

claude-command extract-features:
  - Scan justfile for new commands and document them
  - Check GitHub workflows for new automation
  - Analyze Docker configurations for new features
  - Review template files for new capabilities
  - Document new Claude Code integrations
  - Update feature comparison tables
  - Generate feature matrices and compatibility charts
```

### Update Technology Research
```bash
# Command: update-tech-research
# Description: Refreshes technology stack descriptions with latest information
# Usage: Updates all technology descriptions with current versions and features

claude-command update-tech-research:
  - Research latest FastAPI features and performance metrics
  - Update MongoDB and Beanie ODM capabilities
  - Check HTMX and Tailwind CSS recent updates
  - Validate all external links and references
  - Update version numbers and compatibility info
  - Refresh performance benchmarks and comparisons
  - Update ecosystem and community information
```

### Generate Code Examples
```bash
# Command: generate-code-examples
# Description: Creates and validates code examples throughout documentation
# Usage: Ensures all code examples are current and working

claude-command generate-code-examples:
  - Extract working examples from template files
  - Test all bash command examples
  - Validate Python code snippets
  - Check Docker and compose examples
  - Update configuration file examples
  - Ensure examples match current template structure
  - Add new examples for recent features
```

## Presentation Generation Commands

### Create Executive Summary
```bash
# Command: create-executive-summary
# Description: Generates executive-level summary for CTO presentations
# Usage: Creates concise, business-focused overview

claude-command create-executive-summary:
  - Extract key value propositions
  - Highlight ROI metrics and time savings
  - Include competitive advantage points
  - Create technology risk mitigation summary
  - Generate implementation timeline
  - Add team productivity benefits
  - Format for executive consumption
```

### Generate Technical Deep Dive
```bash
# Command: generate-technical-deep-dive
# Description: Creates detailed technical documentation for development teams
# Usage: Generates comprehensive technical reference

claude-command generate-technical-deep-dive:
  - Document all architectural decisions
  - Include detailed setup and configuration guides
  - Add troubleshooting and debugging sections
  - Create API reference documentation
  - Include security best practices
  - Add performance tuning guidance
  - Generate testing strategies documentation
```

### Create Comparison Charts
```bash
# Command: create-comparison-charts
# Description: Generates visual comparisons with alternatives
# Usage: Creates charts comparing scaffolding to other solutions

claude-command create-comparison-charts:
  - Create feature comparison matrices
  - Generate performance benchmark charts
  - Build ROI comparison tables
  - Create technology stack comparison
  - Generate learning curve analysis
  - Add maintenance effort comparisons
  - Include ecosystem and community metrics
```

## Validation and Quality Commands

### Validate All Links
```bash
# Command: validate-links
# Description: Checks all external links in documentation
# Usage: Ensures all references are current and accessible

claude-command validate-links:
  - Check all HTTP/HTTPS links
  - Validate GitHub repository references
  - Test documentation links
  - Verify API documentation links
  - Check technology stack official sites
  - Validate internal cross-references
  - Generate broken link report
```

### Check Code Examples
```bash
# Command: check-code-examples
# Description: Validates all code examples in documentation
# Usage: Ensures code examples are syntactically correct and current

claude-command check-code-examples:
  - Parse and validate bash commands
  - Check Python code syntax
  - Validate Docker and compose files
  - Test configuration file examples
  - Check justfile command examples
  - Verify template file snippets
  - Generate validation report
```

### Generate Metrics Report
```bash
# Command: generate-metrics
# Description: Creates performance and usage metrics for documentation
# Usage: Updates documentation with current performance data

claude-command generate-metrics:
  - Measure project setup time
  - Calculate lines of code reduction
  - Measure development velocity improvements
  - Track dependency update frequency
  - Monitor security vulnerability fixes
  - Generate productivity improvement metrics
  - Create cost savings calculations
```

## Automated Workflows

### Daily Documentation Sync
```bash
# Command: daily-sync
# Description: Daily automated documentation maintenance
# Usage: Runs automatically to keep documentation current

claude-command daily-sync:
  - Run validate-links command
  - Check for new template features
  - Update dependency versions
  - Refresh external technology information
  - Generate change notifications
  - Update last-modified timestamps
```

### Weekly Full Update
```bash
# Command: weekly-update
# Description: Comprehensive weekly documentation update
# Usage: Full documentation refresh and validation

claude-command weekly-update:
  - Run sync-all-docs command
  - Generate fresh presentations
  - Update all metrics and benchmarks
  - Refresh technology research
  - Generate new code examples
  - Create updated comparison charts
  - Publish updated documentation
```

### Release Documentation
```bash
# Command: release-docs
# Description: Prepares documentation for scaffolding releases
# Usage: Updates documentation for new scaffolding versions

claude-command release-docs:
  - Update version numbers throughout documentation
  - Document new features and breaking changes
  - Generate migration guides if needed
  - Update compatibility information
  - Create release notes
  - Generate updated presentations
  - Tag documentation version
```

## Usage Instructions

To use these commands with Claude Code:

1. **Single Command:** Ask Claude to run a specific command
   ```
   Please run the update-scaffolding-docs command to refresh the documentation
   ```

2. **Multiple Commands:** Chain commands together
   ```
   Please run sync-all-docs followed by generate-presentation-pdf
   ```

3. **Automated Scheduling:** Set up regular updates
   ```
   Please set up weekly-update to run automatically
   ```

4. **Custom Workflows:** Combine commands for specific needs
   ```
   Please extract-features, then update the overview, then generate both PDF and HTML presentations
   ```

All commands are designed to maintain the documentation automatically while preserving the existing structure and adding new information as the scaffolding evolves.