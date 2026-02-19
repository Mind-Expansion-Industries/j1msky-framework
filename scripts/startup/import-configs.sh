#!/usr/bin/env bash
set -euo pipefail

ARCHIVE_OR_DIR="${1:-}"
TARGET="${2:-$HOME/Desktop/J1MSKY}"

if [ -z "$ARCHIVE_OR_DIR" ]; then
  echo "Usage: $0 <export_dir_or_tar.gz> [target_workspace]"
  exit 1
fi

TMP=""
SRC="$ARCHIVE_OR_DIR"
if [ -f "$ARCHIVE_OR_DIR" ] && [[ "$ARCHIVE_OR_DIR" == *.tar.gz ]]; then
  TMP=$(mktemp -d)
  tar -xzf "$ARCHIVE_OR_DIR" -C "$TMP"
  SRC=$(find "$TMP" -mindepth 1 -maxdepth 1 -type d | head -1)
fi

mkdir -p "$TARGET/homeassistant/packages" "$TARGET/homeassistant/sentences/en"

for f in alexa_commands.json audio_profiles.json; do
  [ -f "$SRC/$f" ] && cp "$SRC/$f" "$TARGET/$f"
done
[ -f "$SRC/j1msky_bridge.yaml" ] && cp "$SRC/j1msky_bridge.yaml" "$TARGET/homeassistant/packages/j1msky_bridge.yaml"
[ -f "$SRC/j1msky.yaml" ] && cp "$SRC/j1msky.yaml" "$TARGET/homeassistant/sentences/en/j1msky.yaml"

echo "Import complete into: $TARGET"
[ -n "$TMP" ] && rm -rf "$TMP"
