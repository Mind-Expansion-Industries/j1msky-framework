#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-$HOME/Desktop/J1MSKY-export-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "$OUT_DIR"

echo "== Export J1MSKY Configs =="
echo "Output: $OUT_DIR"

copy_if(){ [ -f "$1" ] && cp "$1" "$OUT_DIR/"; }
copy_if "$HOME/Desktop/J1MSKY/alexa_commands.json"
copy_if "$HOME/Desktop/J1MSKY/audio_profiles.json"
copy_if "$HOME/Desktop/J1MSKY/homeassistant/packages/j1msky_bridge.yaml"
copy_if "$HOME/Desktop/J1MSKY/homeassistant/sentences/en/j1msky.yaml"
copy_if "$HOME/Desktop/J1MSKY/docs/status/ALEXA_SETUP.md"
copy_if "$HOME/Desktop/J1MSKY/docs/status/AUDIO_OUTPUTS.md"

# Also export lightweight env snapshot
{
  echo "HOST=$(hostname)"
  echo "DATE=$(date -Is)"
  echo "KERNEL=$(uname -a)"
  echo "DEFAULT_SINK=$(pactl info 2>/dev/null | sed -n 's/^Default Sink: //p')"
} > "$OUT_DIR/system_snapshot.env"

# archive
TAR_PATH="${OUT_DIR}.tar.gz"
tar -czf "$TAR_PATH" -C "$(dirname "$OUT_DIR")" "$(basename "$OUT_DIR")"

echo "Export complete: $OUT_DIR"
echo "Archive: $TAR_PATH"
