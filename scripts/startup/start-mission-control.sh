#!/bin/bash
# J1MSKY Mission Control v2.0 Launcher
# Advanced agent dashboard with job/mission assignment

cd /home/m1ndb0t/Desktop/J1MSKY

echo "◈ Starting J1MSKY Mission Control v2.0 ◈"
echo ""

# Kill old monitor
pkill -f "sleep-monitor.py" 2>/dev/null
sleep 1

# Check if already running
if pgrep -f "sleep-monitor-v2.py" > /dev/null; then
    echo "✓ Mission Control already running!"
    echo ""
    echo "Access: http://$(hostname -I | awk '{print $1}'):8080"
    exit 0
fi

echo "Starting Mission Control on port 8080..."
python3 sleep-monitor-v2.py > /tmp/mission-control.log 2>&1 &
echo "PID: $!"

sleep 3

# Check if started
if pgrep -f "sleep-monitor-v2.py" > /dev/null; then
    IP=$(hostname -I | awk '{print $1}')
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  🚀 MISSION CONTROL v2.0 IS RUNNING                        ║"
    echo "║                                                            ║"
    echo "║  http://${IP}:8080"
    echo "║  http://localhost:8080                                     ║"
    echo "║                                                            ║"
    echo "║  FEATURES:                                                 ║"
    echo "║  • Multi-panel dashboard (Overview, Agents, Missions)     ║"
    echo "║  • Assign agents to missions                               ║"
    echo "║  • Create and queue jobs                                   ║"
    echo "║  • Built-in terminal                                       ║"
    echo "║  • Quick actions (RF scan, news, backup)                  ║"
    echo "║  • Real-time system monitoring                            ║"
    echo "║                                                            ║"
    echo "║  PANELS:                                                   ║"
    echo "║  📊 Overview - Stats, quick actions, recent missions      ║"
    echo "║  👥 Agents - Deploy missions, view agent status           ║"
    echo "║  🎯 Missions - Create and track missions                  ║"
    echo "║  ⚡ Jobs - Queue and execute commands                     ║"
    echo "║  💻 Terminal - Run commands directly                      ║"
    echo "║  🔧 System - Vitals, audio status, system actions         ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
else
    echo "✗ Failed to start. Check /tmp/mission-control.log"
fi
