#!/bin/bash
# J1MSKY Flipper Launcher
# Easy access to all Flipper tools

cd /home/m1ndb0t/Desktop/J1MSKY/j1msky-framework/flipper

echo "◈ J1MSKY FLIPPER TOOLS ◈"
echo ""
echo "Select tool:"
echo "1. GUI Control Panel (Full dashboard with 6 tabs)"
echo "2. Basic Automation (Easy scripts)"
echo "3. Bluetooth/BLE Control"
echo "4. Command Line (Direct serial)"
echo "5. Simple Bridge (Minimal)"
echo ""
read -p "Choice (1-5): " choice

case $choice in
    1)
        echo "Launching GUI Control Panel..."
        python3 flipper_gui.py
        ;;
    2)
        echo "Launching Basic Automation..."
        cd /home/m1ndb0t/Desktop/J1MSKY
        python3 basic_automation.py
        ;;
    3)
        echo "Launching Bluetooth Control..."
        python3 ble_control.py
        ;;
    4)
        echo "Launching Command Line..."
        python3 flipper_cli.py
        ;;
    5)
        echo "Launching Simple Bridge..."
        python3 simple_bridge.py
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
