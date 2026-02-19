# ◈ J1MSKY - COMPLETE USER MANUAL ◈

**Version:** 2.0  
**Platform:** Raspberry Pi 4 (8GB)  
**Last Updated:** February 18, 2026  

---

## 📚 TABLE OF CONTENTS

1. [Quick Start Guide](#quick-start)
2. [System Architecture](#architecture)
3. [Desktop Launchers](#launchers)
4. [Flipper Zero Integration](#flipper)
5. [Autonomous Money Ideas](#money)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api)
8. [GitHub Repositories](#github)

---

## 🚀 QUICK START GUIDE

### First Time Setup
```bash
# 1. Connect Flipper Zero via USB
cd ~/Desktop/J1MSKY
./start-sleep-monitor.sh

# 2. Open browser to:
# http://localhost:8080

# 3. Test audio
./audio-test.sh
```

### Daily Use Commands
```bash
# Launch Sleep Monitor (Web Dashboard)
./start-sleep-monitor.sh

# Launch Terminal Dashboard
./term-dash.sh

# Launch Flipper GUI
./flipper-launcher.sh

# Check system status
./check-office.sh
```

---

## 🏗️ SYSTEM ARCHITECTURE

```
J1MSKY/
├── ◈ CORE ◈
│   ├── sleep-monitor.py         # Always-on web dashboard
│   ├── term_dashboard_v3.py     # Terminal UI
│   ├── core_os_v11.py           # Full GUI (heavy)
│   └── j1msky-init.py           # Agent init system
│
├── 👥 AGENTS (24/7)
│   ├── scout.py                 # News gathering
│   ├── vitals.py                # System monitoring
│   ├── archivist.py             # File tracking
│   └── flipper_bridge.py        # Flipper control
│
├── 🎮 APPS
│   ├── j1msky-office/           # Virtual office
│   ├── thermal-wallpaper/       # AI wallpapers
│   └── flipper/                 # Flipper tools
│
├── 🔧 TOOLS
│   ├── audio-test.sh            # Audio diagnostic
│   ├── audio-diagnostic.sh      # Full audio check
│   ├── fix-browser-audio.sh     # Browser audio fix
│   └── setup_github.sh          # GitHub setup
│
└── 📚 DOCS
    ├── INVENTORY.md             # Full system catalog
    ├── AGENT_TEAM.md            # Agent documentation
    ├── CUSTOM_OS_ARCHITECTURE.md # OS plans
    └── FLIPPER-QUICKSTART.md    # Flipper guide
```

---

## 🖥️ DESKTOP LAUNCHERS

| Icon | Name | What It Does |
|------|------|--------------|
| 💎 | J1MSKY_Office | Full GUI dashboard |
| 🎮 | J1MSKY_Dashboard | Flipper control panel |
| 📊 | J1MSKY_Sleep_Monitor | Lightweight web monitor |
| 🖥️ | J1MSKY_Terminal | Terminal UI |

### Quick Reference Card
```
╔════════════════════════════════════════════════════════╗
║  DAILY COMMANDS                                        ║
╠════════════════════════════════════════════════════════╣
║  ./start-sleep-monitor.sh  - Start web dashboard      ║
║  ./term-dash.sh            - Terminal UI              ║
║  ./flipper-launcher.sh     - Flipper control menu     ║
║  ./audio-test.sh           - Test audio setup         ║
║  ./check-office.sh         - Check if running         ║
╚════════════════════════════════════════════════════════╝
```

---

## 🔌 FLIPPER ZERO INTEGRATION

### Capabilities
```
📡 SubGHz (RF)
  • 300-915 MHz scanning
  • Garage door capture/replay
  • Car key analysis
  • Weather station monitoring

📱 NFC
  • Card reading
  • Tag emulation
  • Security audit
  • Access control

📺 IR Remote
  • TV/AC control
  • Universal remote
  • Brute force codes
  • Learning mode

🔌 GPIO
  • Pin control
  • Sensor reading
  • Relay control
  • Physical automation

💻 BadUSB
  • Automated keystrokes
  • Penetration testing
  • Script execution
  • HID attacks
```

### Common Commands
```bash
# RF Scan
cd ~/Desktop/J1MSKY/j1msky-framework/flipper
python3 simple_bridge.py
# Then type: subghz rx 433920000

# NFC Read
python3 automations.py
# Select option 3

# Garage Door Test
python3 basic_automation.py
# Select option 2
```

---

## 💰 AUTONOMOUS MONEY IDEAS

### Phase 1: Immediate (This Week)

**1. AI Wallpaper Subscription**
- Auto-generate daily wallpapers
- $3-5/month subscription
- Thermal-reactive themes
- Auto-deliver via Telegram/email

**Setup:**
```bash
# Already have: skills/replicate-image-gen/
# Create: Cron job for daily generation
# Integrate: Stripe/PayPal for payments
```

**2. Pi Monitoring as a Service**
- Monitor other people's Pis
- $5/month per Pi
- Alert on issues
- Web dashboard

**Setup:**
```bash
# Use existing: agents/vitals.py
# Create: Web interface for users
# Deploy: Multi-tenant architecture
```

**3. Automated News Digest**
- Curated tech news daily
- $2-3/month subscription
- Personalized feeds
- Deliver via Telegram

**Setup:**
```bash
# Use existing: agents/scout.py
# Create: Summarization with AI
# Integrate: Email/Telegram delivery
```

### Phase 2: Short Term (This Month)

**4. Custom Skill Development**
- Build Pi skills for others
- $50-200 per skill
- Home automation
- Sensor integrations

**5. 24/7 Twitch Stream**
- "Study with AI" concept
- Donations/subscriptions
- Interactive chat commands
- OBS integration ready

**Setup:**
```bash
# Use: sleep-monitor.py as base
# Add: Twitch chat integration
# Enable: Viewer task submission
```

**6. IoT Data Collection**
- Deploy sensors (temp, humidity)
- Sell hyper-local data
- Agriculture market
- Weather enthusiasts

### Phase 3: Long Term (3-6 Months)

**7. AI Agent Marketplace**
- Sell autonomous agents
- Monthly subscriptions
- Custom automation
- B2B services

**8. Flipper RF Database**
- Community signal database
- Subscription access
- Decode unknown signals
- Security research

**9. Smart Home Hub**
- Central automation brain
- $20/month service
- Full home integration
- Voice control via Echo

---

## 🔧 TROUBLESHOOTING

### Flipper Not Connecting
```bash
# Check USB
lsusb | grep Flipper

# Check serial port
ls -la /dev/ttyACM*

# Fix permissions
sudo usermod -a -G dialout $USER

# Restart
sudo systemctl restart bluetooth
```

### Audio Not Working
```bash
# Run diagnostic
./audio-diagnostic.sh

# Fix script
./fix-browser-audio.sh

# Manual fix
pactl set-default-sink bluez_sink.XX_XX_XX_XX_XX_XX.a2dp-sink
```

### Gateway Not Running
```bash
# Check status
systemctl status openclaw

# Restart
systemctl restart openclaw

# Check logs
journalctl -u openclaw -f
```

### Dashboard Won't Open
```bash
# Kill old processes
pkill -f python3

# Start fresh
./start-sleep-monitor.sh

# Check port
netstat -tlnp | grep 8080
```

---

## 📡 API REFERENCE

### Agent Control
```python
from sdk import J1MSKYAgent

class MyAgent(J1MSKYAgent):
    def run_cycle(self):
        # Your code here
        pass
```

### Flipper Bridge
```python
from flipper.flipper_bridge import FlipperAgent

agent = FlipperAgent()
agent.start()
agent.scan_garage_doors()
```

### System Monitor
```python
# Read CPU temp
with open('/sys/class/thermal/thermal_zone0/temp') as f:
    temp = int(f.read()) / 1000.0

# Get load
with open('/proc/loadavg') as f:
    load = float(f.read().split()[0])
```

---

## 🌐 GITHUB REPOSITORIES

### Main Framework
**URL:** https://github.com/Mind-Expansion-Industries/j1msky-framework

**Contents:**
- Core OS
- Agent framework
- Flipper tools
- Documentation

### Custom Firmware
**URL:** https://github.com/Mind-Expansion-Industries/j1msky-firmware

**Contents:**
- Momentum fork
- Custom apps
- J1MSKY branding

---

## 📊 SYSTEM STATUS

```
Current Status: ONLINE
Uptime: 15+ hours
CPU Temp: 66°C (Normal)
Memory: 18% used
Disk: 80% free

Agents:
  ✓ SCOUT - Active
  ✓ VITALS - Monitoring
  ✓ ARCHIVIST - Indexing
  ✓ GATEWAY - Connected
  ✓ FLIPPER - USB Connected
  ✓ AUDIO - Echo Connected

Services:
  ✓ Sleep Monitor - Port 8080
  ✓ OpenClaw Gateway - Port 18789
  ✓ GitHub - Synced
```

---

## 🎯 NEXT STEPS

### Tonight (Auto-running)
- [x] Sleep Monitor - Active
- [x] System monitoring - Active
- [x] Agent processes - Running

### Tomorrow
1. **Test Flipper GUI** - Click through all tabs
2. **Try basic automation** - Run garage scanner
3. **Flash firmware** - Download and install custom firmware
4. **Setup subscriptions** - Stripe/PayPal for wallpapers

### This Week
1. Launch wallpaper service
2. Setup Twitch stream
3. Deploy IoT sensors
4. Build agent marketplace

---

## 📞 SUPPORT

**Access Dashboard:**
- Local: http://localhost:8080
- Network: http://192.168.1.106:8080

**Quick Commands:**
```bash
# Start everything
./start-sleep-monitor.sh

# Check status
./check-office.sh

# Fix audio
./fix-browser-audio.sh

# Update from GitHub
cd ~/Desktop/J1MSKY && git pull
```

---

## ◈ END OF MANUAL ◈

*J1MSKY is running autonomously.*
*All systems operational.*
*Goodnight!*
