#!/usr/bin/env bash
set -euo pipefail

echo "== J1MSKY Performance Mode: OFF (Restore) =="

# Restore optional system services
sudo systemctl start ollama 2>/dev/null || true
sudo systemctl start rpi-connect 2>/dev/null || true
sudo systemctl start wayvnc 2>/dev/null || true

# Restore default governor/swap behavior (best-effort)
for g in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
  [ -w "$g" ] && echo ondemand > "$g" || true
done
sudo sysctl -w vm.swappiness=60 >/dev/null 2>&1 || true

# Restore dashboard stack via safe-start
/home/m1ndb0t/Desktop/J1MSKY/scripts/startup/safe-start.sh || true

# Open main views
xdg-open http://127.0.0.1:8080 >/dev/null 2>&1 || true
xdg-open http://127.0.0.1:8093 >/dev/null 2>&1 || true

echo "Restore complete."
