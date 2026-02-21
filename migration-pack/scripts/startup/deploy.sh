#!/bin/bash
# J1MSKY Agency v5.0 - Production Deployment
# One-command setup for business deployment

set -e

AGENCY_NAME="J1MSKY Agency"
VERSION="5.0"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║     ◈ $AGENCY_NAME v$VERSION - Production Deploy ◈          ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check requirements
echo "🔍 Checking requirements..."
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 required"; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ Git required"; exit 1; }
echo "✅ Requirements met"

# Setup directories
echo ""
echo "📁 Setting up directories..."
mkdir -p logs backups config data
echo "✅ Directories created"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -q flask requests schedule 2>/dev/null || echo "⚠️  Some packages may already be installed"
echo "✅ Dependencies ready"

# Check for existing server
echo ""
echo "🧹 Cleaning up old processes..."
pkill -f "j1msky.*\.py" 2>/dev/null || true
sleep 2
echo "✅ Cleanup complete"

# Start server
echo ""
echo "🚀 Starting $AGENCY_NAME v$VERSION..."
nohup python3 j1msky-agency-v5.py > logs/agency.log 2>&1 &
echo "   Server PID: $!"

# Wait for startup
sleep 3

# Verify
echo ""
echo "🔍 Verifying deployment..."
if curl -s http://localhost:8080 >/dev/null; then
    IP=$(hostname -I | awk '{print $1}')
    
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ DEPLOYMENT SUCCESSFUL!                                     ║"
    echo "║                                                                ║"
    echo "║  🌐 ACCESS YOUR AGENCY:                                        ║"
    echo "║                                                                ║"
    echo "║  Local:     http://localhost:8080                              ║"
    echo "║  Network:   http://$IP:8080"
    echo "║  Mobile:    Same URLs on your phone                            ║"
    echo "║                                                                ║"
    echo "║  📱 FEATURES:                                                  ║"
    echo "║  • Mobile-first responsive design                              ║"
    echo "║  • PWA-ready (add to home screen)                              ║"
    echo "║  • 4 Agent Teams ready to deploy                               ║"
    echo "║  • Multi-model support (Kimi, Claude)                          ║"
    echo "║  • Rate limit tracking                                         ║"
    echo "║  • Business dashboard with revenue                             ║"
    echo "║                                                                ║"
    echo "║  💰 REVENUE MODELS:                                            ║"
    echo "║  • Starter: $49/month (2 teams)                                ║"
    echo "║  • Professional: $99/month (4 teams, popular)                  ║"
    echo "║  • Enterprise: $299/month (unlimited)                          ║"
    echo "║  • Pay-per-task: $0.50-$5.00                                   ║"
    echo "║                                                                ║"
    echo "║  📚 DOCUMENTATION:                                             ║"
    echo "║  • AGENCY_MANUAL.md - User guide                               ║"
    echo "║  • API_REFERENCE.md - Developer docs                           ║"
    echo "║  • BUSINESS_SETUP.md - Revenue guide                           ║"
    echo "║                                                                ║"
    echo "║  🚀 NEXT STEPS:                                                ║"
    echo "║  1. Open dashboard in browser                                  ║"
    echo "║  2. Click 'Spawn Agent' to create your first agent             ║"
    echo "║  3. Deploy a team for complex tasks                            ║"
    echo "║  4. Configure Stripe for payments                              ║"
    echo "║  5. Start accepting clients!                                   ║"
    echo "║                                                                ║"
    echo "║  Logs: tail -f logs/agency.log                                 ║"
    echo "║  Stop: pkill -f j1msky-agency-v5.py                            ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Your AI agency is live and ready for business! 🚀"
    
else
    echo "❌ Deployment failed. Check logs/agency.log"
    exit 1
fi
