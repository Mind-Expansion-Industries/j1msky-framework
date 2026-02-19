#!/usr/bin/env bash
set -e
PROFILE="${1:-alexa}"
CFG="/home/m1ndb0t/Desktop/J1MSKY/audio_profiles.json"

need(){ command -v "$1" >/dev/null 2>&1 || { echo "missing: $1"; exit 1; }; }
need jq

ensure_cards(){
  pactl set-card-profile alsa_card.platform-fe00b840.mailbox output:analog-stereo 2>/dev/null || true
  pactl set-card-profile alsa_card.platform-fef00700.hdmi output:hdmi-stereo 2>/dev/null || true
  pactl set-card-profile alsa_card.platform-fef05700.hdmi pro-audio 2>/dev/null || true
}

if [ "$PROFILE" = "list" ]; then
  jq -r '.profiles | to_entries[] | "- \(.key): \(.value.label)"' "$CFG"
  echo "Default sink: $(pactl info | sed -n 's/^Default Sink: //p')"
  exit 0
fi

MATCH=$(jq -r --arg p "$PROFILE" '.profiles[$p].sink_match // empty' "$CFG")
VOL=$(jq -r --arg p "$PROFILE" '.profiles[$p].volume // "85%"' "$CFG")
if [ -z "$MATCH" ]; then
  echo "Unknown profile: $PROFILE"
  exit 1
fi

ensure_cards
if [ "$PROFILE" = "alexa" ]; then
  echo -e 'connect EC:0D:E4:92:37:5A\nquit' | bluetoothctl >/dev/null 2>&1 || true
  pactl set-card-profile bluez_card.EC_0D_E4_92_37_5A a2dp-sink 2>/dev/null || true
  sleep 1
fi

SINK=$(pactl list short sinks | awk -v m="$MATCH" '$2 ~ m {print $2; exit}')
if [ -z "$SINK" ]; then
  echo "No sink matched for profile: $PROFILE ($MATCH)"
  pactl list short sinks
  exit 2
fi

pactl set-default-sink "$SINK"
pactl set-sink-volume "$SINK" "$VOL" 2>/dev/null || true

echo "[jimsky] Audio profile set: $PROFILE -> $SINK (vol $VOL)"
echo "Default sink: $(pactl info | sed -n 's/^Default Sink: //p')"
