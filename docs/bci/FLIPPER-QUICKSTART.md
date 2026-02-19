# 🎮 J1MSKY Flipper Control - Quick Access Guide

## 📍 All Tools Location
```
/home/m1ndb0t/Desktop/J1MSKY/
├── flipper-launcher.sh          # <-- EASY LAUNCHER (run this!)
├── basic_automation.py          # Simple automation scripts
└── j1msky-framework/flipper/
    ├── flipper_gui.py           # Full GUI dashboard (6 tabs)
    ├── ble_control.py           # Bluetooth/BLE control
    ├── automations.py           # Advanced automations
    ├── flipper_cli.py           # Command line interface
    └── simple_bridge.py         # Minimal serial bridge
```

## 🚀 Quick Start

### Option 1: Easy Launcher (Recommended)
```bash
cd ~/Desktop/J1MSKY
./flipper-launcher.sh
```
Then select:
- **1** = GUI Control Panel (what you see now!)
- **2** = Basic Automation
- **3** = Bluetooth Control
- **4** = Command Line
- **5** = Simple Bridge

### Option 2: Direct Launch

**GUI Dashboard (6 tabs):**
```bash
cd ~/Desktop/J1MSKY/j1msky-framework/flipper
python3 flipper_gui.py
```

**Basic Automation:**
```bash
cd ~/Desktop/J1MSKY
python3 basic_automation.py
```

**Bluetooth/BLE:**
```bash
cd ~/Desktop/J1MSKY/j1msky-framework/flipper
python3 ble_control.py
```

## 🎛️ GUI Dashboard Features

### 6 Tabs Available:

| Tab | Function | What You Can Do |
|-----|----------|-----------------|
| **📡 SubGHz** | RF Control | Scan garage doors (300-915 MHz), capture signals, transmit |
| **📱 NFC** | NFC Tags | Read cards, emulate tags, security audit |
| **📺 IR Remote** | Infrared | Control TVs/ACs, brute force remotes |
| **🔌 GPIO** | Pin Control | Read/write GPIO pins, control relays |
| **💻 BadUSB** | USB Automation | Run keyboard scripts, penetration testing |
| **🗄️ Database** | Signal Storage | Save captured signals, export/import JSON |

### How to Use GUI:
1. Click **CONNECT** button (green)
2. Wait for "CONNECTED" status
3. Click any tab to access features
4. Use frequency buttons or custom input
5. View results in console at bottom

## 📡 Basic Automation (5 Options)

```bash
python3 basic_automation.py
```

1. **RF Signal Scanner** - Find all radio signals
2. **Garage Door Test** - Check if vulnerable
3. **NFC Tag Reader** - Read nearby cards
4. **TV Remote Clone** - Capture IR remote
5. **Continuous Monitor** - 24/7 signal watch

## 🔵 Bluetooth/BLE Control

```bash
python3 ble_control.py
```

- **BLE Scan** - Find Bluetooth devices
- **BLE Spam** - Send advertisement packets
- **Kitchen Sink** - Aggressive mode (30 sec)

## 🔧 What You Can Do

### Security Testing:
- Scan neighborhood for garage remotes
- Test your own garage door vulnerability
- Audit NFC access cards
- Find unknown RF signals

### Home Automation:
- Clone TV remotes
- Control AC units
- Automate lights (via GPIO)
- Smart home integration

### Penetration Testing:
- BadUSB automation
- RF replay attacks
- NFC cloning
- IR remote takeover

## 🌐 GitHub Repos

- **Framework:** https://github.com/Mind-Expansion-Industries/j1msky-framework
- **Firmware:** https://github.com/Mind-Expansion-Industries/j1msky-firmware

## ⚡ Status

✅ Flipper GUI - **WORKING** (you see it now!)
✅ Serial Connection - **/dev/ttyACM0**
✅ All Scripts - **READY**
✅ GitHub - **PUBLISHED**
✅ Firmware Fork - **READY TO FLASH**

## 🆘 Troubleshooting

**If GUI doesn't open:**
```bash
# Check if Flipper is connected
lsusb | grep Flipper

# Check serial port
ls -la /dev/ttyACM0

# Restart GUI
pkill -f flipper_gui
python3 j1msky-framework/flipper/flipper_gui.py
```

**If connection fails:**
1. Unplug Flipper
2. Plug back in
3. Wait 5 seconds
4. Click CONNECT

## 🎯 Next Steps

1. **Click CONNECT in GUI** (green button)
2. **Try SubGHz tab** → Click "SCAN 433.92 MHz"
3. **Try NFC tab** → Hold card near Flipper
4. **Flash custom firmware** when ready

---

**Everything is ready to use! The GUI is live on your screen now! 🎉**
