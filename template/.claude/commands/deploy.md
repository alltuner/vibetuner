---
name: deploy
description: Deploy the latest version to specified environment
argument-hint: <environment>
---

I'll use the deployment-manager agent to deploy the latest version to your specified environment.

**Environment:** $1 (required)

The deployment-manager agent will:

- Check git status and verify clean working directory
- Confirm we're on the main branch or release-ready branch  
- Execute `just deploy-latest $1` to deploy to the specified environment
- Monitor deployment progress and provide status updates
- Verify successful deployment or report any errors clearly

**Usage examples:**

- `/deploy papaya` → deploys to papaya environment
- `/deploy production` → deploys to production environment
- `/deploy staging` → deploys to staging environment

**Safety checks performed:**

- Ensures no uncommitted changes
- Verifies current branch is appropriate for deployment
- Confirms target environment before proceeding

This ensures safe, reliable deployments with full visibility into the process.
