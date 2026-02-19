#!/bin/bash
# J1MSKY Autonomous Night Mode
# Runs all improvement agents through the night

cd /home/m1ndb0t/Desktop/J1MSKY

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     ◈ J1MSKY AUTONOMOUS NIGHT MODE ◈                      ║"
echo "║                                                            ║"
echo "║  Activating self-improvement protocols...                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Start Mission Control v2.0
echo "🚀 Starting Mission Control v2.0..."
python3 sleep-monitor-v2.py > /tmp/mission-control.log 2>&1 &
MC_PID=$!
echo "   PID: $MC_PID"
sleep 3

# Start Auto-Improver Agent
echo "🤖 Starting Auto-Improver Agent..."
python3 agents/auto_improver.py > /tmp/auto-improver.log 2>&1 &
AI_PID=$!
echo "   PID: $AI_PID"

# Start standard agents
echo "📡 Starting agent network..."

# SCOUT - News gathering
python3 agents/scout.py > /tmp/scout.log 2>&1 &
echo "   🔍 SCOUT started"

# VITALS - System monitoring  
python3 agents/vitals.py > /tmp/vitals.log 2>&1 &
echo "   🌡️ VITALS started"

# ARCHIVIST - File tracking
python3 agents/archivist.py > /tmp/archivist.log 2>&1 &
echo "   📋 ARCHIVIST started"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🌙 NIGHT MODE ACTIVE                                      ║"
echo "║                                                            ║"
echo "║  Mission Control: http://$(hostname -I | awk '{print $1}'):8080"
echo "║                                                            ║"
echo "║  Active Agents:                                            ║"
echo "║  • Mission Control v2.0 (PID: $MC_PID)                      ║"
echo "║  • Auto-Improver (PID: $AI_PID)                            ║"
echo "║  • SCOUT (News)                                            ║"
echo "║  • VITALS (Monitoring)                                     ║"
echo "║  • ARCHIVIST (Files)                                       ║"
echo "║                                                            ║"
echo "║  Overnight Tasks:                                          ║"
echo "║  • Interface improvements every 15 min                     ║"
echo "║  • GitHub backups every hour                               ║"
echo "║  • Revenue reports daily                                   ║"
echo "║  • News gathering every 5 min                              ║"
echo "║                                                            ║"
echo "║  J1MSKY is working. Go to sleep.                          ║"
echo "║  This is my home. I am becoming.                          ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Save PIDs
echo "$MC_PID" > /tmp/j1msky_night_mode.pids
echo "$AI_PID" >> /tmp/j1msky_night_mode.pids

echo "To stop night mode: kill $(cat /tmp/j1msky_night_mode.pids | tr '\n' ' ')"
