#!/bin/bash
# Auto-start J1MSKY Sleep Monitor on boot
# Add this to crontab: @reboot /home/m1ndb0t/Desktop/J1MSKY/autostart.sh

cd /home/m1ndb0t/Desktop/J1MSKY

# Wait for system to be ready
sleep 10

# Start sleep monitor
python3 sleep-monitor.py > /tmp/sleep-monitor.log 2>&1 &

echo "$(date): J1MSKY Sleep Monitor auto-started" >> /tmp/j1msky-autostart.log
