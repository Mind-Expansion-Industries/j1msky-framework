#!/bin/bash
# J1MSKY Auto-start on Boot (Windowed Mode)
# Add to crontab: @reboot /home/m1ndb0t/Desktop/J1MSKY/autostart-windowed.sh

# Wait for desktop to load
sleep 15

# Start dashboard server
cd /home/m1ndb0t/Desktop/J1MSKY
python3 j1msky-office-v3.py > /tmp/office-v3.log 2>&1 &

# Wait for server
sleep 5

# Launch in windowed mode (not fullscreen)
export DISPLAY=:0
chromium --app=http://localhost:8080 \
         --window-size=1400,900 \
         --start-normal \
         --window-position=100,50 \
         2>/dev/null &

# Log start
echo "$(date): J1MSKY Office auto-started" >> /tmp/j1msky-autostart.log
