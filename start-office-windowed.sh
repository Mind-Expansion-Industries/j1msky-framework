#!/bin/bash
# J1MSKY Office - Windowed Mode Launcher
# Normal window you can minimize, resize, Alt-Tab

cd /home/m1ndb0t/Desktop/J1MSKY

# Ensure dashboard is running
if ! ss -tlnp | grep -q ":8080"; then
    echo "Starting dashboard server..."
    python3 j1msky-office-v3.py > /tmp/office-v3.log 2>&1 &
    sleep 2
fi

# Launch in normal window (NOT kiosk)
export DISPLAY=:0
chromium --app=http://localhost:8080 \
         --window-size=1400,900 \
         --start-normal \
         --enable-features=WebContentsForceDark \
         2>/dev/null &

echo "J1MSKY Office launched in windowed mode"
echo "You can minimize, resize, or Alt-Tab"
