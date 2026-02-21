#!/bin/bash
# J1MSKY Sleep Monitor Launcher
# Starts lightweight web dashboard that runs all night

cd /home/m1ndb0t/Desktop/J1MSKY

echo "◈ Starting J1MSKY Sleep Monitor ◈"
echo ""

# Check if already running
if pgrep -f "sleep-monitor.py" > /dev/null; then
    echo "✓ Sleep monitor already running!"
    echo ""
    echo "Access it at:"
    echo "  http://$(hostname):8080"
    echo "  http://localhost:8080"
    exit 0
fi

# Kill heavy GUIs
pkill -9 -f flipper_gui 2>/dev/null
pkill -9 -f core_os 2>/dev/null

echo "Starting web dashboard on port 8080..."
echo ""

# Start the monitor
python3 sleep-monitor.py > /tmp/sleep-monitor.log 2>&1 &
echo "PID: $!"

sleep 2

# Check if started
if pgrep -f "sleep-monitor.py" > /dev/null; then
    echo ""
    echo "✓ Sleep monitor is running!"
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║  ACCESS THE DASHBOARD:                          ║"
    echo "║                                                  ║"
    echo "║  http://$(hostname -I | awk '{print $1}'):8080"
    echo "║  http://localhost:8080                          ║"
    echo "║                                                  ║"
    echo "║  Auto-refreshes every 5 seconds                 ║"
    echo "║  Works on phone, tablet, any device             ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    echo "The monitor will keep running until you stop it."
    echo "To stop: pkill -f sleep-monitor.py"
else
    echo "✗ Failed to start. Check /tmp/sleep-monitor.log"
fi
