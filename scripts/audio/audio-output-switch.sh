#!/usr/bin/env bash
set -e

# J1MSKY Audio Output Switcher
# Usage:
#   ./audio-output-switch.sh list
#   ./audio-output-switch.sh alexa
#   ./audio-output-switch.sh jack
#   ./audio-output-switch.sh hdmi1
#   ./audio-output-switch.sh hdmi2

cmd="${1:-list}"

ensure_profiles() {
  # Keep analog + HDMI1 ready
  pactl set-card-profile alsa_card.platform-fe00b840.mailbox output:analog-stereo 2>/dev/null || true
  pactl set-card-profile alsa_card.platform-fef00700.hdmi output:hdmi-stereo 2>/dev/null || true
  # HDMI2 on Pi often only exposes pro-audio
  pactl set-card-profile alsa_card.platform-fef05700.hdmi pro-audio 2>/dev/null || true
}

pick_sink() {
  local pattern="$1"
  pactl list short sinks | awk -v p="$pattern" '$2 ~ p {print $2; exit}'
}

set_default() {
  local sink="$1"
  if [[ -z "$sink" ]]; then
    echo "No matching sink found."
    return 1
  fi
  pactl set-default-sink "$sink"
  pactl set-sink-volume "$sink" 90% 2>/dev/null || true
  echo "Default sink => $sink"
}

list_all() {
  echo "=== Available sinks ==="
  pactl list short sinks
  echo
  echo "Default sink:"
  pactl info | grep 'Default Sink' || true
}

ensure_profiles

case "$cmd" in
  list)
    list_all
    ;;
  alexa)
    # Try known Echo sink pattern
    s=$(pick_sink "^bluez_output\\.EC_0D_E4_92_37_5A")
    if [[ -z "$s" ]]; then
      echo "Alexa sink not found. Attempting reconnect/profile..."
      echo -e "connect EC:0D:E4:92:37:5A\nquit" | bluetoothctl >/dev/null 2>&1 || true
      pactl set-card-profile bluez_card.EC_0D_E4_92_37_5A a2dp-sink 2>/dev/null || true
      sleep 1
      s=$(pick_sink "^bluez_output\\.EC_0D_E4_92_37_5A")
    fi
    set_default "$s"
    ;;
  jack)
    s=$(pick_sink "^alsa_output\\.platform-fe00b840\\.mailbox\\.stereo-fallback$")
    set_default "$s"
    ;;
  hdmi1)
    s=$(pick_sink "^alsa_output\\.platform-fef00700\\.hdmi\\.hdmi-stereo$")
    set_default "$s"
    ;;
  hdmi2)
    # pro-audio sink name varies; match by card 2 path pattern
    s=$(pactl list short sinks | awk '$2 ~ /platform-fef05700\.hdmi/ {print $2; exit}')
    # fallback to any sink with vc4hdmi1 naming
    [[ -z "$s" ]] && s=$(pactl list short sinks | awk '$2 ~ /vc4hdmi1|card2|hdmi.*2/ {print $2; exit}')
    set_default "$s"
    ;;
  *)
    echo "Unknown command: $cmd"
    echo "Use: list | alexa | jack | hdmi1 | hdmi2"
    exit 1
    ;;
esac

echo
list_all
