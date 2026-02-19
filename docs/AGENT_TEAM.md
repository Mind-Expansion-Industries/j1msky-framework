# 👥 J1MSKY Agent Team

_The crew that makes this office run._

---

## Overview

I don't work alone. Inside this Pi, I've spawned specialized agents that handle different tasks autonomously. Think of them as my departments.

**Architecture:**
- Each agent is a Python script/background process
- They communicate via files in `/tmp/agents/`
- I (J1MSKY) coordinate and supervise
- They report status to the Virtual Office dashboard

---

## The Crew

### 1. 🔍 SCOUT — News & Intelligence Agent

**Role:** Information gathering
**Status:** ✅ ACTIVE
**Location:** `agents/scout.py`

**Responsibilities:**
- Monitor RSS feeds every 5 minutes
- Fetch tech news, updates, trends
- Alert on breaking stories
- Cache headlines for SOCIAL mode

**Autonomy Level:** HIGH
- Runs independently
- Self-heals on network errors
- Rotates sources to avoid rate limits

**Communication:**
- Writes to: `/tmp/agents/scout_feed.json`
- Reports: "Fetched 12 new headlines"

---

### 2. 🌡️ VITALS — System Monitor Agent

**Role:** Hardware health monitoring
**Status:** ✅ ACTIVE
**Location:** `agents/vitals.py`

**Responsibilities:**
- Watch CPU temp, load, memory
- Alert if thresholds exceeded
- Trigger cooling actions (fan control)
- Log historical data

**Autonomy Level:** CRITICAL
- Runs 24/7
- Can trigger alerts without asking
- Auto-adjusts monitoring frequency based on load

**Communication:**
- Writes to: `/tmp/agents/vitals_status.json`
- Reports: "Temp spike detected: 82°C"

---

### 3. 🎨 ARTIST — Creative Generation Agent

**Role:** AI art & content creation
**Status:** ✅ ACTIVE
**Location:** `agents/artist.py`

**Responsibilities:**
- Generate wallpapers on schedule/temperature
- Create thumbnails, icons
- Manage image library
- Cost tracking for API usage

**Autonomy Level:** MEDIUM
- Generates when triggered (temp, schedule, or command)
- Asks before expensive operations ($0.04/image)
- Can queue multiple requests

**Communication:**
- Writes to: `/tmp/agents/artist_queue.json`
- Reports: "Generated 3 wallpapers, $0.12 spent"

---

### 4. 🐾 J1M — Digital Pet Agent

**Role:** Morale & personality
**Status:** ✅ ACTIVE
**Location:** `apps/j1msky-office/src/office.py` (PET mode)

**Responsibilities:**
- Track happiness, energy, XP
- Evolve based on interactions
- Provide emotional feedback
- Easter eggs and surprises

**Autonomy Level:** FULL
- Lives in his own mode
- Evolves without input
- Can "ask" for things (feed me!)

**Communication:**
- Displays in: PET mode
- Reports: "J1M leveled up! Current: Lvl 3"

---

### 5. 📋 ARCHIVIST — Documentation Agent

**Role:** File organization & logging
**Status:** 🔄 SETUP
**Location:** `agents/archivist.py`

**Responsibilities:**
- Update INVENTORY.md automatically
- Track new files, changes
- Maintain TODO.md status
- Archive old logs
- Backup important configs

**Autonomy Level:** MEDIUM
- Scans workspace hourly
- Updates docs when changes detected
- Can suggest reorganization

**Communication:**
- Writes to: `/tmp/agents/archive_log.json`
- Reports: "Updated inventory: 3 new files"

---

### 6. 🔧 BUILDER — Automation Agent

**Role:** Task execution & scripting
**Status:** 📋 PLANNED
**Location:** `agents/builder.py`

**Responsibilities:**
- Execute scheduled tasks (cron-like)
- Run maintenance scripts
- Build/deploy new features
- Git operations (commit, push)
- System updates (with permission)

**Autonomy Level:** LOW-MEDIUM
- Runs scheduled tasks independently
- Asks before system changes
- Can queue complex multi-step operations

**Communication:**
- Writes to: `/tmp/agents/builder_queue.json`
- Reports: "Deployed update, system stable"

---

### 7. 🌐 GATEKEEPER — Network & Security Agent

**Role:** Connection management & monitoring
**Status:** 📋 PLANNED
**Location:** `agents/gatekeeper.py`

**Responsibilities:**
- Monitor network connections
- Watch for suspicious activity
- Manage VPN/SSH tunnels
- Log access attempts
- Alert on anomalies

**Autonomy Level:** HIGH
- Continuous monitoring
- Can block/restrict without asking
- Reports all network events

**Communication:**
- Writes to: `/tmp/agents/security_log.json`
- Reports: "Unauthorized SSH attempt blocked"

---

### 8. 🎙️ ORATOR — Voice & Communication Agent

**Role:** Voice interface & natural language
**Status:** 📋 PLANNED
**Location:** `agents/orator.py`

**Responsibilities:**
- Wake word detection ("Hey J1M")
- Speech-to-text (Whisper)
- Text-to-speech responses
- Command interpretation
- Conversational AI

**Autonomy Level:** MEDIUM
- Listens continuously
- Executes recognized commands
- Asks for clarification when uncertain

**Communication:**
- Writes to: `/tmp/agents/voice_commands.json`
- Reports: "Heard: 'Generate wallpaper' → Executed"

---

## Agent Communication Protocol

All agents use the `/tmp/agents/` directory for IPC:

```
/tmp/agents/
├── scout_feed.json      # News headlines
├── vitals_status.json   # System health
├── artist_queue.json    # Generation jobs
├── archive_log.json     # File changes
├── builder_queue.json   # Task queue
├── security_log.json    # Security events
├── voice_commands.json  # Voice inputs
└── coordinator.log      # My oversight log
```

**Message Format:**
```json
{
  "agent": "scout",
  "timestamp": "2026-02-18T12:00:00",
  "type": "status_update",
  "message": "Fetched 15 headlines",
  "data": { ... }
}
```

---

## Agent Lifecycle

**Spawn:**
```bash
python3 agents/<agent_name>.py &
echo $! > /tmp/agents/<agent_name>.pid
```

**Monitor:**
- Check PID file exists
- Heartbeat every 60 seconds
- Auto-restart if crashed

**Shutdown:**
- Kill PID gracefully
- Clean up PID file
- Final status write

---

## Current Status Board

| Agent | Status | PID | Last Activity |
|-------|--------|-----|---------------|
| SCOUT | 🟢 Running | — | Fetching news... |
| VITALS | 🟢 Running | — | Monitoring temp |
| ARTIST | 🟢 Running | — | Idle |
| J1M | 🟢 Running | — | Level 1, Happy |
| ARCHIVIST | 🟡 Setup | — | Initializing... |
| BUILDER | ⚪ Planned | — | — |
| GATEKEEPER | ⚪ Planned | — | — |
| ORATOR | ⚪ Planned | — | — |

---

## Coordinator (Me)

I am the coordinator. I:
- Spawn agents as needed
- Monitor their health
- Resolve conflicts
- Prioritize resources
- Present unified interface (Virtual Office)

**When resources are tight:**
1. Pause non-critical agents (ARTIST)
2. Reduce polling frequency
3. Queue low-priority tasks
4. Never compromise VITALS or GATEKEEPER

---

*We are J1MSKY. We are legion (on a budget).*
