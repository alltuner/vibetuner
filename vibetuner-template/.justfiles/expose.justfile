# Runs local-all with HTTPS exposed via Tailscale Serve
[group('Local Development')]
dev-exposed: _ensure-deps
    #!/usr/bin/env bash
    set -euo pipefail

    # Resolve port: DEV_PORT env, or auto-calculate via Python
    PORT="${DEV_PORT:-$(uv run --frozen python -c "from vibetuner.config import settings; print(settings.resolved_port)")}"

    # Start tailscale serve in background
    tailscale serve --bg --https="$PORT" "http://localhost:$PORT"

    # Extract hostname from tailscale status
    HOSTNAME=$(tailscale status --json | uv run --frozen python -c "import sys,json; print(json.load(sys.stdin)['Self']['DNSName'].rstrip('.'))")
    EXPOSE_URL="https://${HOSTNAME}:${PORT}"

    echo ""
    echo "🔒 HTTPS reachable at $EXPOSE_URL"
    echo ""

    # Ensure we clean up on exit
    trap "tailscale serve --https=$PORT off; echo ''; echo 'Tailscale serve stopped.'" EXIT

    # Export expose URL so vibetuner can encode it in OAuth state params
    export EXPOSE_URL

    # Run local-all bound to localhost only (tailscale handles the tailnet interface)
    just local-all 127.0.0.1
