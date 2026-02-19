#!/usr/bin/env bash
set -euo pipefail
WS="/home/m1ndb0t/Desktop/J1MSKY"
LOG="$WS/logs/command-audit.log"
mkdir -p "$WS/logs"
TS=$(date -Is)
# tail recent bridge entries as audit summary
RECENT=$(tail -n 20 /tmp/alexa-bridge.log 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g')
{
  echo "[$TS] command-audit snapshot"
  echo "$RECENT"
  echo "---"
} >> "$LOG"

echo "Wrote $LOG"
