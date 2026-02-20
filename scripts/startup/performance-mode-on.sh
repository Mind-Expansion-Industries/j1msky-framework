#!/usr/bin/env bash
set -euo pipefail

echo "== J1MSKY Performance Mode: ON =="

# Stop user dashboard/services (keep OpenClaw gateway)
systemctl --user stop j1msky-agency.service 2>/dev/null || true
systemctl --user stop j1msky-alexa-center.service 2>/dev/null || true
systemctl --user stop j1msky-work-feed.service 2>/dev/null || true

# Keep Alexa bridge optional (light), stop if you want max savings
systemctl --user stop j1msky-alexa-bridge.service 2>/dev/null || true

# Stop optional heavy system services
sudo systemctl stop ollama 2>/dev/null || true
sudo systemctl stop rpi-connect 2>/dev/null || true
sudo systemctl stop wayvnc 2>/dev/null || true

# Kill lingering heavy apps
pkill -f 'chromium|firefox|code-oss|electron|ollama serve|wayvnc' 2>/dev/null || true

sleep 1

echo "-- status --"
uptime
free -h | sed -n '1,3p'
ss -tlnp | grep -E ':8080|:8091|:8092|:8093' || echo 'dashboard ports closed'
pgrep -af 'openclaw-gateway' || echo 'warning: openclaw-gateway not found'
echo "Performance mode enabled."
