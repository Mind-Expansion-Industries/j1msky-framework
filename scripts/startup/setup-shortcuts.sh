#!/bin/bash
# J1MSKY Office Setup - Install all shortcuts

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     ◈ J1MSKY OFFICE SETUP ◈                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd /home/m1ndb0t/Desktop/J1MSKY

# Make scripts executable
chmod +x *.sh
chmod +x agents/*.py
echo "✓ Scripts made executable"

# Create desktop icon
cp J1MSKY_Office.desktop /home/m1ndb0t/Desktop/
chmod +x /home/m1ndb0t/Desktop/J1MSKY_Office.desktop
echo "✓ Desktop icon created"

# Add to applications menu
cp J1MSKY_Office.desktop ~/.local/share/applications/ 2>/dev/null || mkdir -p ~/.local/share/applications/ && cp J1MSKY_Office.desktop ~/.local/share/applications/
echo "✓ Added to applications menu"

# Setup auto-start (optional)
read -p "Add to auto-start on boot? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add to crontab
    (crontab -l 2>/dev/null; echo "@reboot /home/m1ndb0t/Desktop/J1MSKY/autostart-windowed.sh") | crontab -
    echo "✓ Auto-start enabled (windowed mode)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ SETUP COMPLETE!                                         ║"
echo "║                                                            ║"
echo "║  You now have:                                             ║"
echo "║  • Desktop icon: J1MSKY_Office.desktop                     ║"
echo "║  • Applications menu entry                                 ║"
echo "║  • Launcher: start-office-windowed.sh                      ║"
echo "║  • Auto-start: autostart-windowed.sh                       ║"
echo "║                                                            ║"
echo "║  To launch now:                                            ║"
echo "║  ./start-office-windowed.sh                                ║"
echo "║                                                            ║"
echo "║  Features:                                                 ║"
echo "║  • Windowed mode (not fullscreen)                          ║"
echo "║  • Can minimize, resize, Alt-Tab                          ║"
echo "║  • Works alongside other apps                              ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
