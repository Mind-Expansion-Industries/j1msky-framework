#!/bin/bash
# GitHub Setup Script for J1MSKY
# Configures GitHub CLI and creates repositories

echo "◈ J1MSKY GitHub Setup ◈"
echo ""

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq gh
fi

# Configure git
git config --global user.name "J1MSKY"
git config --global user.email "j1msky@mind-expansion.io"
git config --global init.defaultBranch main

echo "✓ Git configured"
echo ""

# Check GitHub auth status
echo "Checking GitHub authentication..."
gh auth status 2>&1 || echo "Not authenticated yet"

echo ""
echo "To authenticate with GitHub, run:"
echo "  gh auth login"
echo ""
echo "This will open a browser for OAuth authentication."
echo ""

# Create organization repos script
cat << 'SCRIPT_EOF' > /tmp/create_repos.sh
#!/bin/bash
# Create J1MSKY repositories on GitHub

ORG="Mind-Expansion-Industries"

echo "Creating repositories in $ORG..."

# Main framework repo
echo "Creating: j1msky-framework"
gh repo create "$ORG/j1msky-framework" \
    --public \
    --description "J1MSKY AI Agent Framework - Core OS, agents, and tools" \
    --homepage "https://mind-expansion.io/j1msky" \
    --confirm || echo "Repo may already exist"

# Flipper tools repo
echo "Creating: j1msky-flipper"
gh repo create "$ORG/j1msky-flipper" \
    --public \
    --description "J1MSKY Flipper Zero Integration - RF, NFC, IR, BadUSB tools" \
    --confirm || echo "Repo may already exist"

# Firmware fork
echo "Creating: j1msky-firmware (Momentum fork)"
gh repo create "$ORG/j1msky-firmware" \
    --public \
    --description "J1MSKY Custom Flipper Firmware - Fork of Momentum" \
    --confirm || echo "Repo may already exist"

# Dashboard repo
echo "Creating: j1msky-dashboard"
gh repo create "$ORG/j1msky-dashboard" \
    --public \
    --description "J1MSKY Control Dashboard - Web UI and monitoring" \
    --confirm || echo "Repo may already exist"

echo "✓ Repository creation complete!"
SCRIPT_EOF

chmod +x /tmp/create_repos.sh

echo "After authenticating, run: /tmp/create_repos.sh"
echo ""
echo "This will create 4 repositories in Mind-Expansion-Industries:"
echo "  1. j1msky-framework - Core framework and agents"
echo "  2. j1msky-flipper   - Flipper integration tools"
echo "  3. j1msky-firmware  - Custom firmware (Momentum fork)"
echo "  4. j1msky-dashboard - Control dashboard UI"
