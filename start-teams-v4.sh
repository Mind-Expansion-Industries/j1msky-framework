#!/bin/bash
# J1MSKY Agent Teams v4.0 Launcher
# Multi-model subagent system with rate limit protection

cd /home/m1ndb0t/Desktop/J1MSKY

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     ◈ J1MSKY AGENT TEAMS v4.0 ◈                              ║"
echo "║                                                                ║"
echo "║     Multi-Model Subagent System                               ║"
echo "║     Rate Limit Protected | Business-Ready                     ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Kill old servers
echo "🧹 Cleaning up..."
pkill -f "j1msky-office\|j1msky-teams\|mission-control" 2>/dev/null
sleep 2

# Start Agent Teams v4.0
echo "🚀 Starting Agent Teams v4.0..."
python3 j1msky-teams-v4.py > /tmp/teams-v4.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"
sleep 3

# Verify it's running
if ss -tlnp | grep -q ":8080"; then
    IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ AGENT TEAMS v4.0 IS LIVE!                                  ║"
    echo "║                                                                ║"
    echo "║  🌐 ACCESS:                                                    ║"
    echo "║     http://localhost:8080                                      ║"
    echo "║     http://${IP}:8080"
    echo "║                                                                ║"
    echo "║  👥 TEAMS (4):                                                 ║"
    echo "║     💻 Code Team - Programming, debugging                      ║"
    echo "║     🎨 Creative Team - Content, design                         ║"
    echo "║     🔍 Research Team - Search, analysis                        ║"
    echo "║     💼 Business Team - Strategy, revenue                       ║"
    echo "║                                                                ║"
    echo "║  🤖 MODELS (3):                                                ║"
    echo "║     • Kimi K2.5 (Fast Coder)                                   ║"
    echo "║     • Claude Sonnet (Creative)                                 ║"
    echo "║     • Claude Opus (Deep Thinker)                               ║"
    echo "║                                                                ║"
    echo "║  ⚡ RATE LIMITS (Real-time tracking):                          ║"
    echo "║     • Kimi: 100/hour                                           ║"
    echo "║     • Anthropic: 50/hour                                       ║"
    echo "║     • Web Search: 100/hour                                     ║"
    echo "║     • Auto-throttling: ACTIVE                                  ║"
    echo "║                                                                ║"
    echo "║  🚀 SPAWN SUBAGENTS:                                           ║"
    echo "║     • Click any model to spawn                                 ║"
    echo "║     • Deploy entire teams                                      ║"
    echo "║     • Track in real-time                                       ║"
    echo "║     • Rate limit protected                                     ║"
    echo "║                                                                ║"
    echo "║  📊 PANELS:                                                    ║"
    echo "║     • Teams - Deploy agent teams                               ║"
    echo "║     • Models - Individual model agents                         ║"
    echo "║     • Spawn - Create custom subagents                          ║"
    echo "║     • Rate Limits - Live tracking                              ║"
    echo "║     • Subagents - Active monitor                               ║"
    echo "║     • Logs - Event stream                                      ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "To spawn: Click Models tab → Click a model → Enter task"
    echo "To stop: kill $SERVER_PID"
    
else
    echo "✗ Failed to start. Check /tmp/teams-v4.log"
    exit 1
fi
