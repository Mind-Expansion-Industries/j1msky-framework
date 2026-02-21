#!/bin/bash
# J1MSKY Office Launcher - Always-On Dashboard

cd /home/m1ndb0t/Desktop/J1MSKY

export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000

# Check if already running
if pgrep -f "core_os_v11.py" > /dev/null; then
    echo "J1MSKY Office is already running!"
    exit 0
fi

# Kill any old instances
pkill -9 -f core_os 2>/dev/null
sleep 1

# Launch the office UI
python3 j1msky-core/core_os_v11.py &

# Also start the agent monitor in background
python3 j1msky-framework/core/j1msky-init.py start &

echo "✓ J1MSKY Office started"
