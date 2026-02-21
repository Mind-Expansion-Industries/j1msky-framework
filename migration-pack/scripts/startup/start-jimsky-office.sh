#!/usr/bin/env bash
set -euo pipefail
WS="/home/m1ndb0t/Desktop/J1MSKY"

# Prefer watchdog-managed services to avoid duplicate processes/port conflicts
if systemctl --user list-unit-files | grep -q 'j1msky-agency.service'; then
  systemctl --user restart j1msky-agency.service || true
  systemctl --user restart j1msky-alexa-bridge.service || true
  systemctl --user restart j1msky-alexa-center.service || true
  systemctl --user restart j1msky-work-feed.service || true
else
  nohup python3 "$WS/dashboards/j1msky-agency-v5.py" >/tmp/j1msky-agency.log 2>&1 &
  nohup python3 "$WS/scripts/alexa/alexa_bridge.py" >/tmp/alexa-bridge.log 2>&1 &
  nohup python3 "$WS/scripts/alexa/ALEXA_COMMAND_CENTER.py" >/tmp/alexa-cmd-center.log 2>&1 &
  nohup python3 "$WS/dashboards/work-feed.py" >/tmp/jimsky-work-feed.log 2>&1 &
fi

sleep 1

# Open office dashboard and work feed
xdg-open http://127.0.0.1:8080 >/dev/null 2>&1 || true
xdg-open http://127.0.0.1:8093 >/dev/null 2>&1 || true

echo "jimsky Office started"
