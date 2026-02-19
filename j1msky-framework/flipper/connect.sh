#!/bin/bash
# Quick Flipper Test Script

echo "◈ Testing Flipper Connection ◈"
echo ""

# Check if device exists
if [ ! -e /dev/ttyACM0 ]; then
    echo "❌ Flipper not found at /dev/ttyACM0"
    exit 1
fi

echo "✓ Flipper device found"
echo "✓ Permissions OK"
echo ""
echo "Connecting to Flipper CLI..."
echo "(Press Ctrl+A then \ to exit)"
echo ""

# Use screen for interactive session
screen /dev/ttyACM0 115200
