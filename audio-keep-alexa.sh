#!/usr/bin/env bash
# Keep Alexa as active sink and move new streams to it.
MAC_UNDERSCORE="EC_0D_E4_92_37_5A"
TARGET="bluez_output.${MAC_UNDERSCORE}.1"

while true; do
  DEF=$(pactl info 2>/dev/null | sed -n 's/^Default Sink: //p')
  if pactl list short sinks | awk '{print $2}' | grep -q "^${TARGET}$"; then
    [ "$DEF" != "$TARGET" ] && pactl set-default-sink "$TARGET" 2>/dev/null || true
    for id in $(pactl list short sink-inputs 2>/dev/null | awk '{print $1}'); do
      sink_id=$(pactl list short sink-inputs | awk -v i="$id" '$1==i{print $2}')
      if [ "$sink_id" != "129" ]; then
        pactl move-sink-input "$id" "$TARGET" 2>/dev/null || true
      fi
    done
  fi
  sleep 2
done
