#!/bin/bash
# J1MSKY Terminal Dashboard Launcher
# Lightweight TUI for Pi - Easy on resources

cd /home/m1ndb0t/Desktop/J1MSKY

echo "◈ Starting J1MSKY Terminal Dashboard ◈"
echo ""

# Check if already running
if pgrep -f "term_dashboard.py" > /dev/null; then
    echo "⚠️  Terminal dashboard already running!"
    echo "Press 'q' in the dashboard to exit first."
    exit 0
fi

# Kill heavy GUI if running
pkill -9 -f core_os_v11.py 2>/dev/null
sleep 1

# Launch terminal dashboard
python3 j1msky-core/term_dashboard.py
