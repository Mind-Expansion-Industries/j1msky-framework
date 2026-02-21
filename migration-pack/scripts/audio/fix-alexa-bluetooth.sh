#!/usr/bin/env bash
set -e

MAC="${1:-EC:0D:E4:92:37:5A}"

echo "=== Alexa Bluetooth Output Fix ==="
echo "Target: $MAC"

echo "1) Restarting user audio services..."
systemctl --user restart pipewire pipewire-pulse wireplumber || true
sleep 2

echo "2) Reconnecting Bluetooth device..."
echo -e "disconnect $MAC\nconnect $MAC\ninfo $MAC\nquit" | bluetoothctl || true
sleep 2

echo "3) Available Pulse cards/profiles:"
pactl list cards | sed -n "/Name: bluez_card.${MAC//:/_}/,/Active Profile/p" || true

echo "4) Attempting A2DP sink profiles..."
for P in a2dp-sink a2dp_sink a2dp; do
  pactl set-card-profile "bluez_card.${MAC//:/_}" "$P" 2>/dev/null && echo "set profile: $P" && break || true
done

# Some systems expose only audio-gateway (input path)
if ! pactl list short sinks | grep -q "bluez_output.${MAC//:/_}"; then
  echo "No bluez_output sink detected yet."
fi

echo "5) If bluez sink exists, set as default"
SINK=$(pactl list short sinks | awk '/bluez_output\.'"${MAC//:/_}"'/ {print $2; exit}')
if [ -n "$SINK" ]; then
  pactl set-default-sink "$SINK"
  pactl set-sink-volume "$SINK" 90%
  echo "Default sink => $SINK"
else
  echo "Still no Bluetooth output sink. Likely Echo connected in input/audio-gateway mode."
fi

echo
pactl info | grep "Default Sink" || true
wpctl status | sed -n '/Audio/,/Video/p' | head -80 || true

echo
cat <<EOF
If still failing, do this physical reset sequence:
1) Say: "Alexa, unpair" then "Alexa, pair"
2) Run again: ./fix-alexa-bluetooth.sh $MAC
3) If it still shows only audio-gateway/no bluez_output sink, Echo model/firmware is advertising as input role for this pairing.
   Workaround: use HA Alexa Media Player for cloud media control (no BT sink required).
EOF
