# J1MSKY Framework - Complete Migration Pack

## What We Built

### Core Architecture
- **J1MSKY Agency Dashboard** - Main control center (port 8080)
- **Alexa Bridge** - Voice command integration (port 8091)
- **Alexa Command Center** - Local UI for testing (port 8092)
- **Work Feed** - Real-time activity monitor (port 8093)

### Scripts Created

#### `/scripts/startup/`
- `bootstrap.sh` - Clone-and-go setup for new machines
- `verify.sh` - Health check all services
- `export-configs.sh` - Backup configuration
- `import-configs.sh` - Restore configuration
- `enable-watchdogs.sh` - Install systemd auto-restart services
- `safe-start.sh` - Smart service starter (checks ports first)
- `start-jimsky-office.sh` - One-click office launch
- `performance-mode-on.sh` - Max performance (stops heavy services)
- `performance-mode-off.sh` - Restore normal operation
- `browser-lite.sh` - Lightweight Chromium for Pi

#### `/scripts/alexa/`
- `alexa_bridge.py` - HTTP bridge for Alexa commands
- `ALEXA_COMMAND_CENTER.py` - Web UI for command testing
- `ALEXA_ONE_CLICK_SETUP.sh` - Quick setup script
- `ALEXA_SETUP.md` - Full setup documentation

#### `/scripts/audio/`
- `fix-alexa-bluetooth.sh` - Repair BT audio connection
- `audio-output-switch.sh` - Route audio between outputs
- `set-audio-profile.sh` - Apply audio profiles
- `youtube-control.sh` - Media playback controls
- `audio-keep-alexa.sh` - Keep Alexa as default sink

#### `/scripts/ops/`
- `low-resource-guard.sh` - Auto-cleanup (runs every 30min)
- `command-audit.sh` - Log recent commands
- `config-snapshot.sh` - Hourly config backups

### Systemd Services (Auto-restart)
- `j1msky-agency.service` - Main dashboard
- `j1msky-alexa-bridge.service` - Alexa integration
- `j1msky-alexa-center.service` - Command center UI
- `j1msky-work-feed.service` - Activity monitor

### Desktop Launchers
- `jimsky_Office.desktop` - Opens office + work feed
- `jimsky_Safe_Start.desktop` - Check ports, start only missing
- `jimsky_Performance_Mode_ON.desktop` - Max performance
- `jimsky_Performance_Mode_OFF.desktop` - Restore services
- `jimsky_Browser_Lite.desktop` - Lightweight browser
- Audio switchers: `J1MSKY_Output_Alexa/Jack/HDMI1/HDMI2.desktop`
- Media: `J1MSKY_YouTube_Play/Pause.desktop`

### Dashboards
- `j1msky-agency-v5.py` - Main agency UI (v6.0.4)
- `work-feed.py` - Real-time work monitor

### Configuration Files
- `alexa_commands.json` - Command definitions
- `audio_profiles.json` - Audio routing profiles
- `model-stack.json` - AI model orchestration config

### Documentation
- `AGENCY_MANUAL.md` - Full agency operations
- `API_REFERENCE.md` - API documentation
- `BUSINESS_SETUP.md` - Monetization guide
- `ALEXA_SETUP.md` - Alexa integration
- `HOMEBASE_MIGRATION.md` - Migration guide
- `BCI_ART_ARCHITECTURE_v7.md` - Brain-to-art project
- `WORKSPACE_MAP.md` - File organization

### Automation (Cron Jobs)
- Hourly config snapshots
- 30-minute command audit
- 30-minute low-resource guard

## Key Features

### Real-Time Visibility
- Live API endpoint at `/api/live`
- Work feed shows commits + logs
- Temperature, memory, process monitoring

### Self-Healing
- Watchdog services auto-restart on crash
- Port conflict detection
- Duplicate process cleanup

### Performance Modes
- Normal: Full dashboard stack
- Performance ON: Minimal services, max speed
- Safe Start: Only start missing services

### Audio System
- Bluetooth (Alexa) audio output
- Profile-based switching (Alexa/Jack/HDMI)
- Auto-heal keeps Alexa as default
- Media controls (YouTube play/pause/next)

## Ports Used
- `8080` - Agency dashboard
- `8091` - Alexa bridge
- `8092` - Command center
- `8093` - Work feed

## How to Restore on New Machine

1. Copy this migration-pack folder to new machine
2. Run: `cd migration-pack && ./scripts/startup/bootstrap.sh`
3. Run: `./scripts/startup/enable-watchdogs.sh`
4. Run: `./scripts/startup/verify.sh`
5. Double-click `jimsky_Safe_Start.desktop` on desktop

## GitHub Repo
`https://github.com/Mind-Expansion-Industries/j1msky-framework`

---
Generated: 2026-02-19
J1MSKY Framework v6.x
