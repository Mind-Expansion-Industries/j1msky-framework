#!/usr/bin/env bash
set -euo pipefail
WS="/home/m1ndb0t/Desktop/J1MSKY"
OUT="$WS/backups/config-snapshots"
mkdir -p "$OUT"
TS=$(date +%Y%m%d-%H%M%S)
DIR="$OUT/$TS"
mkdir -p "$DIR"
for f in \
  "$WS/alexa_commands.json" \
  "$WS/audio_profiles.json" \
  "$WS/homeassistant/packages/j1msky_bridge.yaml" \
  "$WS/homeassistant/sentences/en/j1msky.yaml"; do
  [ -f "$f" ] && cp "$f" "$DIR/"
done

tar -czf "$OUT/$TS.tar.gz" -C "$OUT" "$TS"
rm -rf "$DIR"
echo "Snapshot: $OUT/$TS.tar.gz"
