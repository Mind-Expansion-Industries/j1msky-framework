#!/usr/bin/env bash
set -euo pipefail
BASE="/home/m1ndb0t/Desktop/J1MSKY/scripts/startup"
mkdir -p ~/.config/systemd/user
cp "$BASE/j1msky-agency.service" ~/.config/systemd/user/
cp "$BASE/j1msky-alexa-bridge.service" ~/.config/systemd/user/
cp "$BASE/j1msky-alexa-center.service" ~/.config/systemd/user/

systemctl --user daemon-reload
systemctl --user enable --now j1msky-agency.service
systemctl --user enable --now j1msky-alexa-bridge.service
systemctl --user enable --now j1msky-alexa-center.service

echo "Enabled watchdog services:"
systemctl --user --no-pager --type=service | grep -E 'j1msky-(agency|alexa-bridge|alexa-center)' || true
