#!/usr/bin/env bash
set -euo pipefail

# Lightweight guard: keeps resource usage in check without heavy polling
# Safe to run periodically (e.g., every 20-30 min)

LOG_DIR="/home/m1ndb0t/Desktop/J1MSKY/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/low-resource-guard.log"

now(){ date '+%Y-%m-%d %H:%M:%S'; }

# 1) Rotate overly large temp logs (soft cap 5MB)
for f in /tmp/j1msky-agency.log /tmp/alexa-bridge.log /tmp/alexa-cmd-center.log /tmp/model-lab.log; do
  if [ -f "$f" ]; then
    size=$(stat -c%s "$f" 2>/dev/null || echo 0)
    if [ "$size" -gt 5242880 ]; then
      cp "$f" "$f.bak" 2>/dev/null || true
      : > "$f"
      echo "[$(now)] rotated $f" >> "$LOG"
    fi
  fi
done

# 2) Ensure only canonical services remain (avoid duplicate UI servers)
# Keep watchdog-managed services only; kill old duplicate python dashboards if present.
pkill -f "python3 .*model-lab-ui.py" 2>/dev/null || true
pkill -f "python3 .*sleep-monitor" 2>/dev/null || true
pkill -f "python3 .*mission-control" 2>/dev/null || true

# 3) Audio sanity: if Alexa sink exists, keep default sink on it (cheap one-liner)
ALEXA_SINK="bluez_output.EC_0D_E4_92_37_5A.1"
if pactl list short sinks | awk '{print $2}' | grep -q "^${ALEXA_SINK}$"; then
  current=$(pactl info | sed -n 's/^Default Sink: //p')
  if [ "$current" != "$ALEXA_SINK" ]; then
    pactl set-default-sink "$ALEXA_SINK" 2>/dev/null || true
    echo "[$(now)] default sink restored to Alexa" >> "$LOG"
  fi
fi

# 4) Write compact snapshot
temp=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)
temp_c=$(awk -v t="$temp" 'BEGIN{printf "%.1f", t/1000}')
mem=$(free -m | awk '/Mem:/ {printf "%.1f", ($3/$2)*100}')

printf '[%s] ok temp=%sC mem=%s%%\n' "$(now)" "$temp_c" "$mem" >> "$LOG"
