#!/bin/bash
# Comprehensive Audio Diagnostic for Bluetooth + Browser

echo "◈ J1MSKY Audio Diagnostic Tool ◈"
echo ""

# Check 1: Bluetooth Connection
echo "1. Bluetooth Device Status:"
echo "   Paired devices:"
bluetoothctl devices 2>/dev/null | grep -E "(Echo|Alexa|Speaker|Headset|Mic)" || echo "   No audio devices found"
echo ""

# Check 2: Audio Sinks (Outputs)
echo "2. Audio Outputs (Sinks):"
pactl list short sinks
echo ""

# Check 3: Audio Sources (Inputs/Mics)
echo "3. Audio Inputs (Sources):"
pactl list short sources
echo ""

# Check 4: Default Audio
echo "4. Default Audio Settings:"
echo "   Default Output:"
pactl info | grep "Default Sink"
echo "   Default Input:"
pactl info | grep "Default Source"
echo ""

# Check 5: Bluetooth Audio Profile
echo "5. Bluetooth Audio Profile:"
pactl list cards | grep -A20 "Name: bluez" | grep -E "(Name:|Profile:|Active Profile:)" || echo "   No Bluetooth audio card found"
echo ""

# Check 6: Browser Audio Permissions
echo "6. Browser Audio Settings:"
echo "   Checking Chromium audio..."
ps aux | grep -E "(chromium|chrome|firefox)" | grep -v grep | head -2
echo ""

# Check 7: Test Audio
echo "7. Testing Audio:"
echo "   Playing test sound to default output..."
timeout 3 speaker-test -t sine -f 1000 2>/dev/null &
sleep 2
pkill speaker-test 2>/dev/null
echo "   ✓ Test complete"
echo ""

# Check 8: Mic Test
echo "8. Microphone Test:"
arecord -l 2>/dev/null | head -5 || echo "   No recording devices found"
echo ""

# Common Fixes Section
echo "═══════════════════════════════════════════════════════════"
echo "COMMON FIXES:"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Fix 1: Set Bluetooth to A2DP (high quality audio)
echo "FIX 1: Set Bluetooth to High Quality Audio (A2DP)"
echo "   Run this command:"
CARD_NAME=$(pactl list cards | grep -B5 "bluez" | grep "Name:" | head -1 | cut -d: -f2 | tr -d ' ')
if [ -n "$CARD_NAME" ]; then
    echo "   pactl set-card-profile $CARD_NAME a2dp-sink"
else
    echo "   (No Bluetooth card detected - connect device first)"
fi
echo ""

# Fix 2: Set default sink
echo "FIX 2: Set Bluetooth as Default Output"
SINK_NAME=$(pactl list short sinks | grep -i "bluez\|echo\|alexa" | awk '{print $2}' | head -1)
if [ -n "$SINK_NAME" ]; then
    echo "   pactl set-default-sink $SINK_NAME"
else
    echo "   (No Bluetooth sink found)"
fi
echo ""

# Fix 3: Restart PulseAudio
echo "FIX 3: Restart Audio System"
echo "   pulseaudio -k && pulseaudio --start"
echo ""

# Fix 4: Browser Fix
echo "FIX 4: Browser Audio Fix"
echo "   For Chromium/Chrome:"
echo "   1. Go to: chrome://settings/content/microphone"
echo "   2. Allow sites to use microphone"
echo "   3. Go to: chrome://settings/content/sound"
echo "   4. Allow sites to play sound"
echo ""

# Fix 5: Volume Check
echo "FIX 5: Check Volumes"
echo "   Current output volume:"
pactl list sinks | grep -A5 "Name:" | grep "Volume:" | head -1
echo "   Set to 100%: pactl set-sink-volume @DEFAULT_SINK@ 100%"
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "QUICK SETUP SCRIPT:"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Create quick fix script
cat > /tmp/fix-audio.sh << 'EOF'
#!/bin/bash
echo "Applying audio fixes..."

# Kill and restart pulseaudio
pulseaudio -k 2>/dev/null
sleep 1
pulseaudio --start
sleep 2

# Find Bluetooth sink
SINK=$(pactl list short sinks | grep bluez | awk '{print $2}' | head -1)
if [ -n "$SINK" ]; then
    pactl set-default-sink $SINK
    pactl set-sink-volume $SINK 100%
    echo "✓ Bluetooth audio set as default"
else
    echo "⚠ No Bluetooth sink found - connect device first"
fi

# Find Bluetooth source (mic)
SOURCE=$(pactl list short sources | grep bluez | awk '{print $2}' | head -1)
if [ -n "$SOURCE" ]; then
    pactl set-default-source $SOURCE
    pactl set-source-volume $SOURCE 100%
    echo "✓ Bluetooth mic set as default"
fi

echo ""
echo "Testing audio..."
speaker-test -t sine -f 1000 -l 1 2>/dev/null
echo "✓ Done!"
EOF

chmod +x /tmp/fix-audio.sh
echo "Created: /tmp/fix-audio.sh"
echo "Run it with: bash /tmp/fix-audio.sh"
echo ""

# Browser-specific instructions
echo "═══════════════════════════════════════════════════════════"
echo "BROWSER-SPECIFIC (Web Audio Issues):"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "If audio doesn't work in browser:"
echo ""
echo "1. Check site permissions:"
echo "   - Click the 🔒 icon in address bar"
echo "   - Ensure 'Sound' and 'Microphone' are allowed"
echo ""
echo "2. Try different browser:"
echo "   - Chromium: sudo apt install chromium-browser"
echo "   - Firefox: sudo apt install firefox-esr"
echo ""
echo "3. Check browser audio output:"
echo "   - chrome://settings/content/sound"
echo "   - Ensure not muted"
echo ""
echo "4. Restart browser completely:"
echo "   - Kill all browser processes"
echo "   - Reopen and test"
echo ""
