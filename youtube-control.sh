#!/usr/bin/env bash
set -e
CMD="${1:-toggle}"
export DISPLAY=${DISPLAY:-:0}

# Prefer playerctl if browser exposes MPRIS
if command -v playerctl >/dev/null 2>&1; then
  case "$CMD" in
    play) playerctl play 2>/dev/null || true ;;
    pause) playerctl pause 2>/dev/null || true ;;
    next) playerctl next 2>/dev/null || true ;;
    prev) playerctl previous 2>/dev/null || true ;;
    toggle) playerctl play-pause 2>/dev/null || true ;;
  esac
fi

# Fallback to media keys via xdotool
if command -v xdotool >/dev/null 2>&1; then
  case "$CMD" in
    play|pause|toggle) xdotool key XF86AudioPlay ;;
    next) xdotool key XF86AudioNext ;;
    prev) xdotool key XF86AudioPrev ;;
  esac
fi

echo "[jimsky] youtube/media command sent: $CMD"
