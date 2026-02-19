#!/bin/bash
# J1MSKY Terminal Dashboard Launcher v2 - Smooth, Real-Time Tool Monitoring

cd /home/m1ndb0t/Desktop/J1MSKY

echo "◈ Starting J1MSKY Terminal Dashboard v2 ◈"
echo "Showing real-time tool usage and commands"
echo ""

# Check if already running
if pgrep -f "term_dashboard_v2.py" > /dev/null; then
    echo "⚠️  Terminal dashboard already running!"
    echo "Press 'q' to exit first."
    exit 0
fi

# Kill heavy GUI if running
pkill -9 -f core_os_v11.py 2>/dev/null
sleep 1

# Launch the improved terminal dashboard
python3 j1msky-core/term_dashboard_v2.py
