#!/bin/bash
# Audio Test & Echo/Alexa Setup Script

echo "◈ J1MSKY Audio Test & Echo Setup ◈"
echo ""

# Test 1: Check audio devices
echo "1. Checking audio devices..."
echo "   Speakers/Headphones:"
pactl list sinks | grep -E "Name:|Description:" | head -6
echo ""
echo "   Microphones:"
pactl list sources | grep -E "Name:|Description:" | head -6
echo ""

# Test 2: Play test sound
echo "2. Playing test sound..."
echo "   You should hear a beep in 3 seconds..."
sleep 1
paplay /usr/share/sounds/alsa/Front_Center.wav 2>&1 || speaker-test -t sine -f 1000 -l 1 2>&1 &
sleep 3
pkill speaker-test 2>/dev/null
echo "   ✓ Test sound played"
echo ""

# Test 3: Bluetooth/Echo check
echo "3. Checking Echo/Alexa connection..."
echo "   Paired Bluetooth devices:"
bluetoothctl devices | grep -i echo || echo "   No Echo found in paired devices"
echo ""

# Test 4: Set Echo as audio output if connected
echo "4. Attempting to connect Echo as audio output..."
# Find Echo device
ECHO_MAC=$(bluetoothctl devices | grep -i echo | awk '{print $2}')
if [ -n "$ECHO_MAC" ]; then
    echo "   Found Echo at: $ECHO_MAC"
    echo "   Connecting..."
    bluetoothctl connect $ECHO_MAC 2>&1
    sleep 2
    
    # Check if it shows as audio sink
    if pactl list sinks | grep -q "$ECHO_MAC"; then
        echo "   ✓ Echo connected as audio output!"
        
        # Set as default
        SINK_NAME=$(pactl list sinks | grep -B2 "$ECHO_MAC" | grep "Name:" | head -1 | cut -d: -f2 | tr -d ' ')
        if [ -n "$SINK_NAME" ]; then
            pactl set-default-sink $SINK_NAME 2>&1
            echo "   ✓ Echo set as default audio output"
        fi
    else
        echo "   ⚠️  Echo paired but not showing as audio device"
        echo "   You may need to: 'Alexa, pair Bluetooth'"
    fi
else
    echo "   No Echo device found"
    echo "   To pair: Put Echo in pairing mode, then run:"
    echo "   bluetoothctl scan on"
    echo "   bluetoothctl pair [MAC_ADDRESS]"
fi

echo ""
echo "5. Audio routing test..."
echo "   Current default output:"
pactl info | grep "Default Sink" || echo "   No default sink set"

echo ""
echo "◈ Audio Setup Complete ◈"
echo ""
echo "Troubleshooting tips:"
echo "  • Make sure Echo is in pairing mode: 'Alexa, pair Bluetooth'"
echo "  • Check Pi Bluetooth: bluetoothctl"
echo "  • Test with: paplay /usr/share/sounds/alsa/Front_Center.wav"
echo "  • Set default: pactl set-default-sink [SINK_NAME]"
