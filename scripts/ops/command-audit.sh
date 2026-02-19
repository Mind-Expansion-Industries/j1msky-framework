#!/usr/bin/env bash
set -euo pipefail
WS="/home/m1ndb0t/Desktop/J1MSKY"
LOG="$WS/logs/command-audit.log"
mkdir -p "$WS/logs"
TS=$(date -Is)
# tail recent bridge entries as audit summary (squash noisy Python tracebacks)
RECENT=$(tail -n 60 /tmp/alexa-bridge.log 2>/dev/null \
  | sed 's/\x1b\[[0-9;]*m//g' \
  | awk '
      BEGIN { in_tb=0 }
      /^Traceback \(most recent call last\):/ { in_tb=1; print "[traceback detected]"; next }
      in_tb && /^OSError:/ { print; in_tb=0; next }
      in_tb { next }
      { print }
    ')

# keep log healthy: soft-rotate when file gets large
MAX_BYTES=$((200 * 1024))
if [ -f "$LOG" ] && [ "$(wc -c < "$LOG")" -gt "$MAX_BYTES" ]; then
  tail -n 1200 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
fi

{
  echo "[$TS] command-audit snapshot"
  echo "$RECENT"
  echo "---"
} >> "$LOG"

echo "Wrote $LOG"
