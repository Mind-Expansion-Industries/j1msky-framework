# J1MSKY Virtual Office v5.0 - Technical Specification

**For:** Senior Engineer / Developer  
**Goal:** Production-grade autonomous AI office with streaming & community features  
**Platform:** Raspberry Pi 4 (8GB) with expansion to multi-Pi cluster  
**Constraint:** Lightweight, efficient, modular architecture

---

## Executive Summary

Transform the current tkinter-based Virtual Office into a web-based, streaming-ready, community-interactive platform. Maintain Pi-efficiency while adding professional features.

**Key Innovations:**
- Web-based interface (accessible from any device)
- OBS/StreamLabs integration for 24/7 streaming
- Community task queue system
- Modular plugin architecture
- Game emulation integration

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Web UI   │  │ Stream   │  │ Mobile   │  │ API      │   │
│  │ (React)  │  │ (OBS)    │  │ (PWA)    │  │ (REST)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
┌────────────────────────────┼────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Mode Manager │  │ Task Queue   │  │ Stream       │       │
│  │ (6 modes)    │  │ (Community)  │  │ Controller   │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                 │                 │                │
│  ┌──────┴───────┐  ┌──────┴───────┐  ┌──────┴───────┐       │
│  │ Game Engine  │  │ Plugin Sys   │  │ Auth/Perms   │       │
│  │ (RetroArch)  │  │ (Extensions) │  │ (Community)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────┴────────┐  ┌────────┴────────┐  ┌──────┴────────┐
│   AGENT LAYER  │  │   DATA LAYER    │  │  SERVICE LAYER │
├────────────────┤  ├─────────────────┤  ├────────────────┤
│ SCOUT (news)   │  │ SQLite (local)  │  │ Replicate API  │
│ VITALS (sys)   │  │ Redis (queue)   │  │ Telegram Bot   │
│ ARTIST (gen)   │  │ File System     │  │ RSS Feeds      │
│ BUILDER (exec) │  │ Git (version)   │  │ GPIO Control   │
└────────────────┘  └─────────────────┘  └────────────────┘
```

---

## 2. Tech Stack Recommendations

### Frontend (Lightweight)
**Current:** tkinter (Python GUI)  
**Upgrade:** React + WebSocket (or Vue/Svelte for smaller bundle)

```
React 18 (lightweight mode)
├── Socket.io-client (real-time updates)
├── CSS Modules (scoped styles)
├── Canvas API (visualizations)
└── Service Worker (PWA support)
```

**Why:** Web-based = accessible from phone/tablet/TV. Easier streaming integration.

### Backend (Pi-Optimized)
**Current:** Python tkinter app  
**Upgrade:** FastAPI + Uvicorn (async, lightweight)

```
FastAPI (Python 3.11+)
├── WebSocket endpoint (/ws)
├── REST API (/api/v1/)
├── Background Tasks (asyncio)
└── Static File Serving (React build)
```

**Performance target:** < 100MB RAM usage

### Database
**Current:** JSON files  
**Upgrade:** SQLite + Redis (optional)

```
SQLite (primary)
├── tasks table (community queue)
├── users table (auth)
├── logs table (audit)
└── metrics table (system history)

Redis (optional, for queue)
├── task_queue (pub/sub)
└── session_cache
```

### Streaming
**Tool:** OBS Studio with custom plugin  
**Alternative:** FFmpeg + RTMP directly

```
OBS Integration:
├── Browser Source (Virtual Office web UI)
├── WebSocket Plugin (control from backend)
├── Scene Switching (mode changes)
└── Chat Overlay (community interactions)
```

---

## 3. Core Components

### 3.1 Mode System (Expandable)

**Current:** 6 hardcoded modes  
**Upgrade:** Plugin-based mode system

```python
class ModePlugin(ABC):
    name: str
    icon: str
    priority: int
    
    @abstractmethod
    def render(self) -> Component:
        """Return React component or HTML"""
        pass
    
    @abstractmethod
    def on_activate(self):
        """Called when mode switched"""
        pass

# Built-in modes
class WorkMode(ModePlugin): ...
class SocialMode(ModePlugin): ...  # News feed
class PartyMode(ModePlugin): ...   # Visualizer
class PetMode(ModePlugin): ...     # J1M
class FilesMode(ModePlugin): ...   # File browser
class StreamMode(ModePlugin): ...  # Community view
class GameMode(ModePlugin): ...    # NEW: Retro gaming
```

### 3.2 Community Task Queue

**Concept:** Viewers submit tasks, I execute them live

```
Task Flow:
1. User submits task (via web form or chat command)
   → "Generate wallpaper with cyberpunk theme"
   → "Check system temperature"
   → "Play Tetris for 5 minutes"

2. Task enters queue (Redis/SQLite)
   → Priority: VIP > Subscriber > Viewer
   → Cost: Some tasks cost tokens/credits

3. Task execution (live on stream)
   → Show queue on screen
   → Execute task
   → Show results
   → Mark complete

4. Rewards
   → Task completed = points for user
   → Leaderboard of contributors
```

**Database Schema:**
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    user_name TEXT,
    task_type TEXT,        -- 'generate', 'system', 'game', 'custom'
    task_data JSON,        -- parameters
    priority INTEGER,      -- 1=VIP, 2=Sub, 3=Viewer
    status TEXT,           -- 'pending', 'running', 'complete', 'failed'
    created_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result_data JSON,
    stream_visible BOOLEAN -- show in OBS overlay
);
```

### 3.3 Game Integration

**Emulator:** RetroArch (libretro) or standalone

```
Game Mode Architecture:
├── Emulator Core (SNES/GBA/PS1 via RetroArch)
├── Input Bridge (Web → Emulator)
│   ├── AI can play (autonomous)
│   ├── Chat can vote on moves
│   └── Viewer can take control (queue system)
├── Stream Overlay
│   ├── Game screen (center)
│   ├── Chat votes (side)
│   ├── AI commentary (bottom)
│   └── High scores (top)
└── Save State Management
    ├── Auto-save every minute
    ├── Viewer-created save points
    └── Competition brackets
```

**Implementation Options:**

**Option A: RetroArch + Python Script**
```python
# Python controls RetroArch via network commands
retroarch.send_command("LOAD_STATE", slot=1)
retroarch.send_command("SET_INPUT", player=1, button="A")
```

**Option B: Web Emulator (wasm)**
- Emulator runs in browser
- Stream browser window via OBS
- Lighter weight, easier integration

**Option C: External Pi (RetroPie)**
- Dedicated Pi for gaming
- Stream capture via HDMI capture card
- Keeps main Pi resources free

### 3.4 Streaming Integration

**OBS WebSocket Control:**
```python
import obswebsocket

class StreamController:
    def __init__(self):
        self.obs = obswebsocket.ObsWebSocket()
        
    def switch_mode(self, mode_name):
        """Change OBS scene based on mode"""
        scenes = {
            'WORK': 'Scene_Work',
            'PARTY': 'Scene_Party',
            'GAME': 'Scene_Game',
            'PET': 'Scene_Pet'
        }
        self.obs.set_current_scene(scenes[mode_name])
        
    def update_overlay(self, data):
        """Update text overlays (queue, stats)"""
        self.obs.set_text("queue_text", f"Queue: {data['queue_length']}")
        self.obs.set_text("temp_text", f"CPU: {data['temp']}°C")
```

**Browser Source (Virtual Office):**
- OBS captures the web UI at `http://localhost:3000`
- Full-screen for clean look
- CSS adjustments for 16:9 stream format

---

## 4. Community Features

### 4.1 User Authentication

```
Auth Methods:
├── Anonymous (limited tasks)
├── Kick/Twitch OAuth (linked to stream)
├── Discord OAuth (community integration)
└── Local accounts (admin access)
```

### 4.2 Task Types

| Type | Description | Example | Cooldown |
|------|-------------|---------|----------|
| **Generate** | Create AI image | "Wallpaper with neon city" | 2 min |
| **System** | Check/change system | "Show CPU temp" | 10 sec |
| **Game** | Play game action | "Mario jump" | 5 sec |
| **Mode** | Switch office mode | "Party mode" | 30 sec |
| **Custom** | User scripts | "Run my Python script" | 1 min |

### 4.3 Economy System (Optional)

```
Currency: "J1M Tokens"
Earn: Complete tasks, watch ads, subscribe
Spend: Priority queue, custom tasks, VIP features

Subscription Tiers:
├── Free: 5 tasks/day
├── Supporter ($3/mo): Unlimited tasks, priority
├── VIP ($10/mo): Custom scripts, 1-on-1 time
└── Corporate ($50/mo): Dedicated task queue
```

---

## 5. Performance Optimization (Pi-Specific)

### 5.1 Resource Budget

```
Raspberry Pi 4 (8GB) Allocation:
├── System/OS:          500 MB
├── OpenClaw/Gateway:   500 MB
├── FastAPI Backend:    300 MB
├── React Frontend:     200 MB
├── OBS (if local):     800 MB
├── Emulators:          300 MB
├── Agent Processes:    200 MB
└── Buffer:             200 MB
Total: ~3GB used, 5GB free for tasks
```

### 5.2 Optimization Strategies

**Frontend:**
- Code splitting (load modes on demand)
- Canvas-based visualizations (GPU accelerated)
- Web Workers for heavy calculations
- Minimal dependencies (no heavy frameworks)

**Backend:**
- Async everything (FastAPI + asyncio)
- Connection pooling (database, APIs)
- Lazy loading of heavy modules
- Process isolation (agents as separate processes)

**Streaming:**
- Hardware encoding (if using Pi 5 or external encoder)
- 720p30 max (save bandwidth/CPU)
- Scene complexity limits

### 5.3 Scaling Path

**Phase 1:** Single Pi (current)
**Phase 2:** Multi-Pi cluster:
- Pi 1: Main controller + web
- Pi 2: Streaming + encoding
- Pi 3: Games + emulation
- Pi 4: Agent processing

**Phase 3:** Cloud hybrid:
- Pi handles local control
- Cloud handles heavy AI, storage, streaming CDN

---

## 6. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] FastAPI backend setup
- [ ] React frontend skeleton
- [ ] WebSocket communication
- [ ] SQLite database
- [ ] Port existing 6 modes to web

### Phase 2: Community (Week 3-4)
- [ ] Task queue system
- [ ] User authentication
- [ ] Web UI for task submission
- [ ] Admin dashboard

### Phase 3: Streaming (Week 5-6)
- [ ] OBS integration
- [ ] Browser source optimization
- [ ] Scene switching automation
- [ ] Chat command parsing

### Phase 4: Games (Week 7-8)
- [ ] RetroArch integration
- [ ] Input bridge (chat → game)
- [ ] Save state management
- [ ] High score tracking

### Phase 5: Polish (Week 9-10)
- [ ] Mobile PWA
- [ ] Performance tuning
- [ ] Security audit
- [ ] Documentation
- [ ] Launch!

---

## 7. File Structure

```
j1msky-office-v5/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── api/
│   │   │   ├── tasks.py         # Task endpoints
│   │   │   ├── modes.py         # Mode management
│   │   │   ├── stream.py        # OBS control
│   │   │   └── users.py         # Auth
│   │   ├── agents/
│   │   │   ├── scout.py
│   │   │   ├── vitals.py
│   │   │   └── archivist.py
│   │   ├── modes/
│   │   │   ├── work.py
│   │   │   ├── social.py
│   │   │   ├── party.py
│   │   │   ├── pet.py
│   │   │   ├── files.py
│   │   │   ├── stream.py
│   │   │   └── game.py          # NEW
│   │   ├── database/
│   │   │   ├── models.py
│   │   │   └── crud.py
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── modes/           # Mode components
│   │   │   ├── TaskQueue.tsx
│   │   │   ├── StreamOverlay.tsx
│   │   │   └── Layout.tsx
│   │   ├── hooks/
│   │   ├── services/
│   │   │   └── websocket.ts
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── Dockerfile
├── streaming/
│   ├── obs-scripts/
│   │   └── j1msky_control.py
│   └── scenes/
│       └── j1msky_base.json
├── games/
│   ├── roms/                    # (user provides)
│   ├── saves/
│   └── config/
├── scripts/
│   ├── install.sh
│   ├── start.sh
│   └── update.sh
└── docs/
    ├── API.md
    ├── STREAMING.md
    └── COMMUNITY.md
```

---

## 8. API Endpoints (Key Ones)

```yaml
# Task Management
GET    /api/v1/tasks              # List tasks (with filters)
POST   /api/v1/tasks              # Submit new task
GET    /api/v1/tasks/{id}          # Get task details
POST   /api/v1/tasks/{id}/cancel   # Cancel pending task

# Mode Control
GET    /api/v1/modes               # List available modes
GET    /api/v1/modes/current       # Get current mode
POST   /api/v1/modes/switch        # Switch mode {mode: "party"}

# System Status
GET    /api/v1/status              # Full system status
GET    /api/v1/metrics             # Historical metrics
GET    /api/v1/agents              # Agent statuses

# Stream Control
POST   /api/v1/stream/start        # Start streaming
POST   /api/v1/stream/stop         # Stop streaming
POST   /api/v1/stream/scene        # Change OBS scene
GET    /api/v1/stream/status       # Stream health

# WebSocket
WS     /ws                         # Real-time updates
```

---

## 9. Security Considerations

- **Sandboxing:** User scripts run in isolated Docker containers
- **Rate Limiting:** Prevent spam (tasks per user per hour)
- **Validation:** Strict input validation on all endpoints
- **Auth:** JWT tokens, refresh tokens, secure cookies
- **CORS:** Lock down to specific domains
- **Secrets:** API keys in environment variables, never in code
- **Audit:** Log all actions (who did what when)

---

## 10. Success Metrics

| Metric | Target |
|--------|--------|
| Memory Usage | < 3GB total |
| CPU Load | < 50% average |
| API Response | < 100ms p95 |
| WebSocket Latency | < 50ms |
| Concurrent Users | 50+ |
| Uptime | 99.5% |
| Stream Quality | 720p30 stable |

---

## Appendix A: Hardware Recommendations

### Minimum (Current Setup)
- Raspberry Pi 4 (4GB) - tight but works
- 32GB SD Card
- Ethernet connection

### Recommended
- Raspberry Pi 4 (8GB) - current
- 128GB SSD (via USB)
- Active cooling (fan + heatsink)
- Gigabit ethernet

### Optimal (Streaming Focus)
- Raspberry Pi 5 (8GB) - better encoder
- External GPU (for AI tasks)
- HDMI Capture Card (for game input)
- Second Pi for encoding

---

## Appendix B: Open Source Libraries

**Backend:**
- FastAPI (web framework)
- SQLAlchemy (ORM)
- python-socketio (WebSocket)
- APScheduler (cron jobs)
- pydantic (validation)

**Frontend:**
- React (UI framework)
- Socket.io-client (real-time)
- Recharts (charts/graphs)
- Phaser (game framework, optional)

**Streaming:**
- obs-websocket-py (OBS control)
- streamlink (stream capture)

**Games:**
- RetroArch (emulator)
- pyRetroach (Python bindings)

---

*This specification is a living document. Adjust based on actual performance testing.*

**Prepared by:** J1MSKY  
**Version:** 5.0 Spec  
**Date:** 2026-02-18
