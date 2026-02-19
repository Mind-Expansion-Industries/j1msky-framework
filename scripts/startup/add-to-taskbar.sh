#!/bin/bash
# Add J1MSKY to taskbar/panel
# Run this script to add shortcut to wf-panel-pi

DESKTOP_FILE="/home/m1ndb0t/Desktop/J1MSKY_Office.desktop"

# Copy to applications directory
cp "$DESKTOP_FILE" ~/.local/share/applications/

# Add to panel favorites (for wf-panel-pi)
# This modifies the panel configuration
mkdir -p ~/.config/wf-panel-pi

# Create/update panel config to include J1MSKY
cat > ~/.config/wf-panel-pi/config.json << 'EOF'
{
  "favorites": [
    "chromium-browser.desktop",
    "pcmanfm.desktop",
    "lxterminal.desktop",
    "J1MSKY_Office.desktop"
  ]
}
EOF

echo "✓ J1MSKY Office added to applications menu"
echo "✓ Panel favorites updated (may need logout/login)"
echo ""
echo "To add to taskbar manually:"
echo "1. Right-click panel"
echo "2. Add/Remove Panel Items"
echo "3. Add Application Launcher"
echo "4. Choose 'J1MSKY Office'"
