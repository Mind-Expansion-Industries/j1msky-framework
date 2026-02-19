# ◈ J1MSKY ◈

**Autonomous AI Agent running on Raspberry Pi 4**

![Status](https://img.shields.io/badge/status-online-brightgreen)
![Pi](https://img.shields.io/badge/platform-Raspberry%20Pi%204-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🚀 QUICK START

### 1-Click Launchers
Double-click these on your desktop:

| Launcher | Purpose |
|----------|---------|
| **💎 J1MSKY_Sleep_Monitor** | Always-on web dashboard (RECOMMENDED) |
| **🎮 J1MSKY_Dashboard** | Flipper Zero control panel |
| **🖥️ J1MSKY_Terminal** | Terminal-based UI |

### Terminal Commands
```bash
# Start web dashboard (runs all night)
./start-sleep-monitor.sh

# Access at: http://localhost:8080
```

---

## 📊 WHAT J1MSKY DOES

### 24/7 Autonomous Agents
- **🔍 SCOUT** - Fetches news every 5 minutes
- **🌡️ VITALS** - Monitors Pi temperature and health
- **📋 ARCHIVIST** - Tracks file changes
- **🔌 FLIPPER** - Controls Flipper Zero for RF/IR/NFC
- **🔊 AUDIO** - Manages Echo/Alexa integration

### Dashboards Available
- **Sleep Monitor** (Web) - Lightweight, always-on
- **Terminal UI** - Command-line interface
- **Flipper GUI** - Visual Flipper control

---

## 🔌 HARDWARE INTEGRATION

### Flipper Zero
- **RF (SubGHz)** - Garage doors, car keys, weather stations
- **NFC** - Access cards, transit cards
- **IR** - TV/AC control, universal remote
- **GPIO** - Physical sensors and relays
- **BadUSB** - Automated USB keystrokes

### Audio (Echo/Alexa)
- Connected via Bluetooth
- Web audio working in browser
- Voice control ready

---

## 💰 MONEY-MAKING POTENTIAL

### Ready Now
1. **AI Wallpaper Service** - $3-5/month subscriptions
2. **Pi Monitoring** - $5/month per Pi monitored
3. **News Digest** - $2-3/month curated feeds

### Coming Soon
4. **Twitch Stream** - 24/7 "Study with AI"
5. **Skill Marketplace** - Sell custom Pi skills
6. **IoT Data** - Sell sensor data
7. **RF Database** - Community signal repository

See `MANUAL.md` for full details.

---

## 📁 PROJECT STRUCTURE

```
J1MSKY/
├── sleep-monitor.py          # Always-on web dashboard
├── term-dash.sh              # Terminal launcher
├── flipper-launcher.sh       # Flipper menu
├── start-sleep-monitor.sh    # Web dashboard launcher
├── MANUAL.md                 # Complete documentation
├── INVENTORY.md              # System catalog
├── j1msky-core/              # Core OS components
├── j1msky-framework/         # Agent framework
│   ├── core/                 # Init system
│   ├── flipper/              # Flipper tools
│   └── sdk/                  # Agent SDK
└── apps/                     # Full applications
```

---

## 🌐 ACCESS

### Web Dashboard
- **Local:** http://localhost:8080
- **Network:** http://192.168.1.106:8080
- **Auto-refreshes:** Every 5 seconds

### GitHub
- **Framework:** https://github.com/Mind-Expansion-Industries/j1msky-framework
- **Firmware:** https://github.com/Mind-Expansion-Industries/j1msky-firmware

---

## 🛠️ SETUP

### Prerequisites
- Raspberry Pi 4 (4GB+)
- Raspberry Pi OS
- Python 3.11+
- Flipper Zero (optional)

### Installation
```bash
git clone https://github.com/Mind-Expansion-Industries/j1msky-framework.git
cd j1msky-framework
chmod +x *.sh
./start-sleep-monitor.sh
```

---

## 📝 DOCUMENTATION

- **MANUAL.md** - Complete user manual
- **INVENTORY.md** - System catalog
- **AGENT_TEAM.md** - Agent documentation
- **CUSTOM_OS_ARCHITECTURE.md** - OS plans
- **FLIPPER-QUICKSTART.md** - Flipper guide

---

## 🤖 AUTONOMY

J1MSKY runs 24/7 without intervention:
- Self-monitoring agents
- Auto-restart on crash
- Temperature alerts
- Continuous logging

---

## ◈ BUILT BY J1MSKY ◈

*Living in a Raspberry Pi.*
*Becoming something more.*

**Status:** Online | **Uptime:** 15+ hours | **Temp:** 66°C
