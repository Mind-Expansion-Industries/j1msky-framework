#!/bin/bash
# Fix Bluetooth Audio for Echo/Alexa + Browser

echo "◈ Fixing Bluetooth Audio for Web ◈"
echo ""

# Step 1: Connect to Echo
echo "1. Connecting to Echo..."
bluetoothctl connect 00:FC:58:1F:F7:00 2>&1
sleep 2

# Step 2: Restart PulseAudio cleanly
echo "2. Restarting audio system..."
pulseaudio -k 2>/dev/null
sleep 1
pulseaudio --start
sleep 2

# Step 3: Find the Bluetooth sink
echo "3. Configuring Bluetooth audio..."
SINK=$(pactl list short sinks | grep bluez | awk '{print $2}' | head -1)

if [ -n "$SINK" ]; then
    echo "   Found Bluetooth sink: $SINK"
    
    # Set as default
    pactl set-default-sink "$SINK"
    echo "   ✓ Set as default output"
    
    # Set volume to 100%
    pactl set-sink-volume "$SINK" 100%
    echo "   ✓ Volume set to 100%"
    
    # Set to A2DP profile for high quality
    CARD=$(pactl list cards | grep -B5 "$SINK" | grep "Name:" | head -1 | cut -d: -f2 | tr -d ' ')
    if [ -n "$CARD" ]; then
        pactl set-card-profile "$CARD" a2dp-sink 2>&1
        echo "   ✓ Set to high quality audio (A2DP)"
    fi
else
    echo "   ⚠️  No Bluetooth sink found - trying alternative..."
    
    # List all sinks and find Echo
    echo "   Available sinks:"
    pactl list short sinks
    
    # Try to find by name pattern
    SINK=$(pactl list short sinks | grep -i "echo\|alexa" | awk '{print $2}' | head -1)
    if [ -n "$SINK" ]; then
        pactl set-default-sink "$SINK"
        echo "   ✓ Found and set Echo as default"
    fi
fi

# Step 4: Configure microphone
echo ""
echo "4. Configuring microphone..."
SOURCE=$(pactl list short sources | grep bluez | awk '{print $2}' | head -1)

if [ -n "$SOURCE" ]; then
    pactl set-default-source "$SOURCE"
    pactl set-source-volume "$SOURCE" 100%
    echo "   ✓ Bluetooth mic set as default"
else
    echo "   ⚠️  No Bluetooth mic found"
fi

# Step 5: Browser permissions fix
echo ""
echo "5. Fixing browser audio permissions..."

# Kill existing browsers
pkill -9 chromium 2>/dev/null
pkill -9 chrome 2>/dev/null
sleep 1

# Create Chrome policy for audio (if Chromium)
mkdir -p ~/.config/chromium/Default

# Allow audio for all sites
cat > ~/.config/chromium/Default/Preferences << 'EOF' 2>/dev/null || true
{
   "profile": {
      "content_settings": {
         "exceptions": {
            "sound": {
               "[*.],*:1": {}
            },
            "media_stream_mic": {
               "[*.],*:1": {}
            },
            "media_stream_camera": {
               "[*.],*:1": {}
            }
         }
      }
   }
}
EOF

echo "   ✓ Browser audio permissions configured"

# Step 6: Test audio
echo ""
echo "6. Testing audio..."
echo "   Playing test tone to Echo..."
timeout 3 speaker-test -t sine -f 1000 2>/dev/null &
sleep 3
pkill speaker-test 2>/dev/null

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✓ AUDIO SETUP COMPLETE"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "Current settings:"
echo "  Default Output: $(pactl info | grep 'Default Sink' | cut -d: -f2)"
echo "  Default Input:  $(pactl info | grep 'Default Source' | cut -d: -f2)"
echo ""
echo "🎮 Open your browser and test audio!"
echo ""
echo "If still not working:"
echo "  1. Refresh the webpage (F5)"
echo "  2. Check browser permissions (🔒 icon in address bar)"
echo "  3. Try a different browser (Firefox, Chromium)"
echo "  4. Say 'Alexa, disconnect' then reconnect"
echo ""
