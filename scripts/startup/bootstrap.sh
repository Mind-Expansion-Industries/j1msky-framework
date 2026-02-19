#!/usr/bin/env bash
set -euo pipefail

# J1MSKY Homebase Bootstrap
# Usage:
#   ./scripts/startup/bootstrap.sh [workspace_path]

WORKSPACE="${1:-$HOME/Desktop/J1MSKY}"
REPO_URL="https://github.com/Mind-Expansion-Industries/j1msky-framework.git"

echo "== J1MSKY Homebase Bootstrap =="
echo "Workspace: $WORKSPACE"

if [ ! -d "$WORKSPACE/.git" ]; then
  mkdir -p "$(dirname "$WORKSPACE")"
  git clone "$REPO_URL" "$WORKSPACE"
else
  echo "Repo already exists, pulling latest..."
  git -C "$WORKSPACE" pull --ff-only || true
fi

cd "$WORKSPACE"

# Ensure executable bits for scripts
find scripts -type f -name "*.sh" -exec chmod +x {} + || true
find . -maxdepth 1 -type f -name "*.sh" -exec chmod +x {} + || true

# Python deps (best-effort; don't fail whole bootstrap)
if command -v python3 >/dev/null 2>&1; then
  python3 -m pip install --user --break-system-packages -r scripts/../requirements.txt 2>/dev/null || true
fi

# Create required dirs
mkdir -p logs backups memory config homeassistant/packages homeassistant/sentences/en

# Start core local services (best effort)
nohup python3 dashboards/j1msky-agency-v5.py >/tmp/j1msky-agency.log 2>&1 &
nohup python3 scripts/alexa/alexa_bridge.py >/tmp/alexa-bridge.log 2>&1 &
nohup python3 scripts/alexa/ALEXA_COMMAND_CENTER.py >/tmp/alexa-cmd-center.log 2>&1 &

sleep 2

echo
echo "Bootstrap complete."
echo "Agency UI:      http://127.0.0.1:8080"
echo "Model Lab:      http://127.0.0.1:8090 (if started)"
echo "Alexa Bridge:   http://127.0.0.1:8091/health"
echo "Alexa Cmd UI:   http://127.0.0.1:8092"
echo
echo "Next: run ./scripts/startup/verify.sh"
