#!/bin/bash
# J1MSKY Office Status Monitor
# Check if office is running, restart if needed

cd /home/m1ndb0t/Desktop/J1MSKY

export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000

# Check if running
if pgrep -f "core_os_v11.py" > /dev/null; then
    echo "✅ J1MSKY Office is running"
    pgrep -f "core_os_v11.py"
else
    echo "⚠️  J1MSKY Office not running. Starting..."
    python3 j1msky-core/core_os_v11.py > /tmp/office.log 2>&1 &
    sleep 2
    echo "✅ Started with PID: $!"
fi
