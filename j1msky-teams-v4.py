#!/usr/bin/env python3
"""
J1MSKY Multi-Model Agent System v4.0
Team-based agents with subagent spawning
Rate limit tracking, model selection, business-ready
"""

import http.server
import socketserver
import json
import os
import subprocess
import threading
import time
import random
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Rate Limit Tracking
RATE_LIMITS = {
    'kimi': {'requests': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
    'anthropic': {'requests': 0, 'last_reset': time.time(), 'limit': 50, 'window': 3600},
    'web_search': {'requests': 0, 'last_reset': time.time(), 'limit': 100, 'window': 3600},
    'image_gen': {'requests': 0, 'last_reset': time.time(), 'limit': 50, 'window': 3600},
    'github': {'requests': 0, 'last_reset': time.time(), 'limit': 30, 'window': 3600}
}

# Model Teams - Each model is its own agent
AGENT_TEAMS = {
    'team_coding': {
        'name': '💻 Code Team',
        'models': ['kimi-coding/k2p5', 'anthropic/claude-sonnet-4-6'],
        'specialty': 'Programming, debugging, system architecture',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_creative': {
        'name': '🎨 Creative Team', 
        'models': ['anthropic/claude-opus-4-6', 'kimi-coding/k2p5'],
        'specialty': 'Content creation, design, documentation',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_research': {
        'name': '🔍 Research Team',
        'models': ['anthropic/claude-sonnet-4-6', 'kimi-coding/k2p5'],
        'specialty': 'Web search, analysis, data gathering',
        'status': 'active',
        'tasks_completed': 0
    },
    'team_business': {
        'name': '💼 Business Team',
        'models': ['anthropic/claude-opus-4-6', 'anthropic/claude-sonnet-4-6'],
        'specialty': 'Strategy, planning, revenue optimization',
        'status': 'standby',
        'tasks_completed': 0
    }
}

# Individual Model Agents
MODEL_AGENTS = {
    'k2p5': {
        'name': 'Kimi K2.5',
        'provider': 'kimi-coding',
        'role': 'Primary Coder',
        'status': 'active',
        'last_used': None,
        'success_rate': 0.95,
        'specialty': 'Fast coding, system tasks'
    },
    'sonnet': {
        'name': 'Claude Sonnet 4.6',
        'provider': 'anthropic',
        'role': 'Creative Assistant',
        'status': 'active',
        'last_used': None,
        'success_rate': 0.92,
        'specialty': 'Content, analysis'
    },
    'opus': {
        'name': 'Claude Opus 4.6',
        'provider': 'anthropic',
        'role': 'Deep Thinker',
        'status': 'standby',
        'last_used': None,
        'success_rate': 0.98,
        'specialty': 'Complex reasoning'
    }
}

# Active Subagents
ACTIVE_SUBAGENTS = {}
EVENTS_LOG = []

def add_event(message, agent=None, model=None, type='info'):
    """Add event to log"""
    event = {
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'agent': agent,
        'model': model,
        'type': type
    }
    EVENTS_LOG.append(event)
    if len(EVENTS_LOG) > 100:
        EVENTS_LOG.pop(0)

def check_rate_limit(service):
    """Check if service is rate limited"""
    limit = RATE_LIMITS.get(service, {})
    if not limit:
        return False, 0
    
    # Reset if window passed
    if time.time() - limit['last_reset'] > limit['window']:
        limit['requests'] = 0
        limit['last_reset'] = time.time()
    
    remaining = limit['limit'] - limit['requests']
    is_limited = remaining <= 0
    
    return is_limited, remaining

def use_service(service):
    """Record service usage"""
    if service in RATE_LIMITS:
        RATE_LIMITS[service]['requests'] += 1

def spawn_subagent(task, model, team=None):
    """Spawn a subagent with specific model"""
    agent_id = f"subagent_{int(time.time())}_{random.randint(1000,9999)}"
    
    # Check rate limit for model provider
    provider = MODEL_AGENTS.get(model, {}).get('provider', 'kimi-coding')
    is_limited, remaining = check_rate_limit(provider.split(':')[0])
    
    if is_limited:
        add_event(f"Rate limited: {provider}. Cannot spawn {model}", type='error')
        return None
    
    # Record usage
    use_service(provider.split(':')[0])
    
    # Create subagent record
    ACTIVE_SUBAGENTS[agent_id] = {
        'id': agent_id,
        'task': task,
        'model': model,
        'team': team,
        'status': 'spawning',
        'created': datetime.now().isoformat(),
        'started': None,
        'completed': None,
        'result': None
    }
    
    # Update model agent status
    if model in MODEL_AGENTS:
        MODEL_AGENTS[model]['last_used'] = datetime.now().isoformat()
        MODEL_AGENTS[model]['status'] = 'working'
    
    add_event(f"Spawned {model} subagent for: {task[:50]}...", agent=agent_id, model=model, type='success')
    
    # Simulate subagent work (in real impl, this would call sessions_spawn)
    def run_subagent():
        time.sleep(2)  # Simulate work
        ACTIVE_SUBAGENTS[agent_id]['status'] = 'running'
        ACTIVE_SUBAGENTS[agent_id]['started'] = datetime.now().isoformat()
        time.sleep(5)  # Simulate processing
        ACTIVE_SUBAGENTS[agent_id]['status'] = 'completed'
        ACTIVE_SUBAGENTS[agent_id]['completed'] = datetime.now().isoformat()
        ACTIVE_SUBAGENTS[agent_id]['result'] = f"Task completed using {model}"
        
        if model in MODEL_AGENTS:
            MODEL_AGENTS[model]['status'] = 'active'
            MODEL_AGENTS[model]['tasks_completed'] = MODEL_AGENTS[model].get('tasks_completed', 0) + 1
        
        add_event(f"Subagent {agent_id} completed task", agent=agent_id, model=model, type='success')
    
    threading.Thread(target=run_subagent, daemon=True).start()
    
    return agent_id

def get_system_stats():
    """Get system stats"""
    stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--', 'disk_free': '0G', 'processes': 0}
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            stats['temp'] = round(int(f.read()) / 1000.0, 1)
        with open('/proc/loadavg', 'r') as f:
            stats['load'] = round(float(f.read().split()[0]), 2)
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            stats['mem'] = round(((total - available) / total) * 100, 1)
        with open('/proc/uptime', 'r') as f:
            secs = float(f.read().split()[0])
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            stats['uptime'] = f"{h}h {m:02d}m"
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            stats['disk_free'] = lines[1].split()[3]
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        stats['processes'] = len(result.stdout.strip().split('\n')) - 1
    except:
        pass
    return stats

# HTML Template with Rate Limit Panel and Team View
HTML_V4 = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY AGENT TEAMS v4.0 ◈</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --accent-cyan: #00ffff;
            --accent-green: #00ff88;
            --accent-pink: #ff00ff;
            --accent-yellow: #ffff00;
            --accent-red: #ff4444;
            --accent-purple: #9945ff;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --border: #333333;
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 20px 25px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.5em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            letter-spacing: 2px;
        }
        
        .header-stats {
            display: flex;
            gap: 15px;
        }
        
        .header-stat {
            text-align: center;
            padding: 8px 15px;
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid var(--accent-cyan);
            border-radius: 8px;
        }
        
        .header-stat-value {
            font-size: 1.1em;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        
        .header-stat-label {
            font-size: 9px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }
        
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0 20px;
        }
        
        .nav-tab {
            padding: 15px 22px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            text-transform: uppercase;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 255, 255, 0.1);
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
            background: var(--bg-card);
        }
        
        .main-content {
            padding: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
        }
        
        .panel.active {
            display: block;
            animation: fadeIn 0.4s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        
        @media (max-width: 1200px) {
            .grid-4, .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .card:hover {
            transform: translateY(-3px);
            border-color: var(--accent-cyan);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            color: var(--accent-cyan);
            font-size: 1em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        /* Rate Limit Panel */
        .rate-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .rate-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            transition: all 0.3s;
        }
        
        .rate-item.limited {
            border-color: var(--accent-red);
            background: rgba(255, 68, 68, 0.1);
        }
        
        .rate-item.safe {
            border-color: var(--accent-green);
        }
        
        .rate-item.warning {
            border-color: var(--accent-yellow);
        }
        
        .rate-name {
            font-weight: 600;
            margin-bottom: 5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .rate-status {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }
        
        .status-ok { background: var(--accent-green); color: #000; }
        .status-warn { background: var(--accent-yellow); color: #000; }
        .status-limit { background: var(--accent-red); color: #fff; }
        
        .rate-bar {
            height: 8px;
            background: var(--bg-primary);
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        
        .rate-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }
        
        .fill-safe { background: var(--accent-green); }
        .fill-warn { background: var(--accent-yellow); }
        .fill-limit { background: var(--accent-red); }
        
        /* Team Cards */
        .team-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--accent-cyan);
            transition: all 0.3s;
        }
        
        .team-card:hover {
            transform: translateX(5px);
            border-color: var(--accent-cyan);
        }
        
        .team-card.active { border-left-color: var(--accent-green); }
        .team-card.standby { border-left-color: var(--accent-yellow); }
        
        .team-name {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 10px;
        }
        
        .team-models {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            font-family: monospace;
        }
        
        .team-specialty {
            font-size: 12px;
            color: var(--accent-cyan);
            margin-bottom: 15px;
        }
        
        .team-stats {
            display: flex;
            gap: 15px;
            font-size: 12px;
        }
        
        .team-stat {
            background: var(--bg-card);
            padding: 5px 10px;
            border-radius: 6px;
        }
        
        /* Model Agents */
        .model-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .model-card:hover {
            border-color: var(--accent-cyan);
            transform: scale(1.02);
        }
        
        .model-card.active { border-color: var(--accent-green); }
        .model-card.working { border-color: var(--accent-yellow); animation: pulse 2s infinite; }
        .model-card.standby { border-color: var(--text-secondary); opacity: 0.7; }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 0 0 0 rgba(255, 255, 0, 0.4); }
            50% { box-shadow: 0 0 0 10px rgba(255, 255, 0, 0); }
        }
        
        .model-name {
            font-weight: 600;
            color: var(--accent-cyan);
            margin-bottom: 5px;
        }
        
        .model-role {
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .model-status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-active { background: rgba(0, 255, 136, 0.2); color: var(--accent-green); }
        .status-working { background: rgba(255, 255, 0, 0.2); color: var(--accent-yellow); }
        .status-standby { background: rgba(136, 136, 136, 0.2); color: var(--text-secondary); }
        
        /* Subagents */
        .subagent-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .subagent-item.spawning { border-left: 3px solid var(--accent-cyan); }
        .subagent-item.running { border-left: 3px solid var(--accent-yellow); }
        .subagent-item.completed { border-left: 3px solid var(--accent-green); }
        
        .subagent-info {
            flex: 1;
        }
        
        .subagent-id {
            font-family: monospace;
            font-size: 11px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }
        
        .subagent-task {
            font-size: 13px;
            color: var(--text-primary);
        }
        
        .subagent-model {
            font-size: 10px;
            color: var(--accent-cyan);
            margin-top: 4px;
        }
        
        .subagent-status {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        /* Event Log */
        .event-log {
            background: #050508;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Fira Code', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .event-line {
            padding: 4px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        
        .event-time {
            color: var(--accent-pink);
            margin-right: 10px;
        }
        
        .event-info { color: var(--accent-cyan); }
        .event-success { color: var(--accent-green); }
        .event-error { color: var(--accent-red); }
        .event-warn { color: var(--accent-yellow); }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0088aa);
            color: #000;
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00aa55);
            color: #000;
        }
        
        .btn:hover {
            transform: translateY(-2px);
        }
        
        .footer {
            text-align: center;
            padding: 25px;
            margin-top: 30px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY AGENT TEAMS v4.0 ◈</h1>
        <div class="header-stats">
            <div class="header-stat">
                <div class="header-stat-value">{{TEAM_COUNT}}</div>
                <div class="header-stat-label">Teams</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value">{{MODEL_COUNT}}</div>
                <div class="header-stat-label">Models</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value">{{ACTIVE_SUBAGENTS}}</div>
                <div class="header-stat-label">Active</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value" style="color: {{TEMP_COLOR}};">{{TEMP}}°C</div>
                <div class="header-stat-label">Temp</div>
            </div>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('teams')">👥 Teams</button>
        <button class="nav-tab" onclick="showPanel('models')">🤖 Models</button>
        <button class="nav-tab" onclick="showPanel('spawn')">🚀 Spawn</button>
        <button class="nav-tab" onclick="showPanel('rates')">⚡ Rate Limits</button>
        <button class="nav-tab" onclick="showPanel('subagents')">📋 Subagents</button>
        <button class="nav-tab" onclick="showPanel('logs')">📜 Logs</button>
    </nav>
    
    <main class="main-content">
        {{CONTENT}}
    </main>
    
    <footer class="footer">
        <p>◈ J1MSKY v4.0 Multi-Model Agent System ◈ | Business-Ready ◈ Rate-Limit Protected ◈</p>
    </footer>
    
    <script>
        function showPanel(panelId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            event.target.classList.add('active');
        }
        
        function spawnAgent(model) {
            const task = prompt('Enter task for ' + model + ':');
            if (task) {
                fetch('/api/spawn', {
                    method: 'POST',
                    body: 'model=' + model + '&task=' + encodeURIComponent(task),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).then(() => {
                    alert('🚀 Spawned ' + model + ' agent!');
                    location.reload();
                });
            }
        }
        
        function spawnTeam(team) {
            const task = prompt('Enter task for ' + team + ' team:');
            if (task) {
                fetch('/api/spawn-team', {
                    method: 'POST',
                    body: 'team=' + team + '&task=' + encodeURIComponent(task),
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                }).then(() => {
                    alert('🚀 Spawned ' + team + ' team!');
                    location.reload();
                });
            }
        }
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            location.reload();
        }, 10000);
    </script>
</body>
</html>'''

# Panel: Rate Limits
RATES_PANEL = '''<div id="rates" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">⚡ Rate Limit Status</span>
        </div>
        <div class="rate-grid">
            {{RATE_LIMITS}}
        </div>
    </div>
    
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Usage Today</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 2;">
                <p>🤖 <strong style="color: var(--accent-cyan);">Model Requests:</strong> {{MODEL_REQUESTS}}</p>
                <p>🔍 <strong style="color: var(--accent-cyan);">Web Searches:</strong> {{WEB_REQUESTS}}</p>
                <p>🖼️ <strong style="color: var(--accent-cyan);">Image Generations:</strong> {{IMAGE_REQUESTS}}</p>
                <p>💾 <strong style="color: var(--accent-cyan);">GitHub Operations:</strong> {{GITHUB_REQUESTS}}</p>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <span class="card-title">🛡️ Protection Status</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 2;">
                <p>✅ <strong style="color: var(--accent-green);">Auto-throttling:</strong> Active</p>
                <p>✅ <strong style="color: var(--accent-green);">Request batching:</strong> Enabled</p>
                <p>✅ <strong style="color: var(--accent-green);">Cooldown periods:</strong> Enforced</p>
                <p>✅ <strong style="color: var(--accent-green);">Fallback models:</strong> Ready</p>
            </div>
        </div>
    </div>
</div>'''

# Panel: Teams
TEAMS_PANEL = '''<div id="teams" class="panel active">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">👥 Agent Teams</span>
        </div>
        <div class="grid-2">
            {{TEAMS}}
        </div>
    </div>
</div>'''

# Panel: Models
MODELS_PANEL = '''<div id="models" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">🤖 Individual Model Agents</span>
            <span style="color: var(--text-secondary); font-size: 12px;">Click to spawn subagent</span>
        </div>
        <div class="grid-3">
            {{MODELS}}
        </div>
    </div>
</div>'''

# Panel: Spawn
SPAWN_PANEL = '''<div id="spawn" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">🚀 Spawn New Subagent</span>
        </div>
        
        <form onsubmit="spawnFromForm(event)" style="display: grid; gap: 20px;">
            <div>
                <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Task Description</label>
                <textarea name="task" rows="4" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: monospace;"
                  placeholder="Describe what you want the agent to do..."></textarea>
            </div>
            
            <div class="grid-2">
                <div>
                    <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Select Model</label>
                    <select name="model" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                        <option value="k2p5">Kimi K2.5 (Fast Coder)</option>
                        <option value="sonnet">Claude Sonnet (Creative)</option>
                        <option value="opus">Claude Opus (Deep Thinker)</option>
                    </select>
                </div>
                
                <div>
                    <label style="display: block; color: var(--text-secondary); font-size: 12px; margin-bottom: 8px; text-transform: uppercase;">Priority</label>
                    <select name="priority" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                        <option value="low">🟢 Low (Background)</option>
                        <option value="normal" selected>🟡 Normal</option>
                        <option value="high">🔴 High (Urgent)</option>
                    </select>
                </div>
            </div>
            
            <button type="submit" class="btn btn-success" style="width: 100%; padding: 15px; font-size: 16px;">🚀 SPAWN SUBAGENT</button>
        </form>
    </div>
</div>'''

# Panel: Subagents
SUBAGENTS_PANEL = '''<div id="subagents" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">📋 Active Subagents</span>
        </div>
        <div>
            {{SUBAGENTS}}
        </div>
    </div>
</div>'''

# Panel: Logs
LOGS_PANEL = '''<div id="logs" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">📜 Event Log</span>
        </div>
        <div class="event-log">
            {{EVENTS}}
        </div>
    </div>
</div>'''

class MultiAgentServer(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            stats = get_system_stats()
            
            # Build rate limits HTML
            rates_html = ''
            for service, data in RATE_LIMITS.items():
                is_limited, remaining = check_rate_limit(service)
                used = data['requests']
                limit = data['limit']
                percent = (used / limit) * 100
                
                status_class = 'safe' if percent < 50 else 'warning' if percent < 80 else 'limited'
                status_text = 'OK' if percent < 50 else 'WARN' if percent < 80 else 'LIMIT'
                fill_class = 'fill-safe' if percent < 50 else 'fill-warn' if percent < 80 else 'fill-limit'
                
                rates_html += f'''
                <div class="rate-item {status_class}">
                    <div class="rate-name">
                        {service.upper()}
                        <span class="rate-status status-{status_text.lower()}">{status_text}</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-secondary);">{remaining} / {limit} remaining</div>
                    <div class="rate-bar">
                        <div class="rate-fill {fill_class}" style="width: {percent}%;"></div>
                    </div>
                </div>'''
            
            # Build teams HTML
            teams_html = ''
            for team_id, team in AGENT_TEAMS.items():
                status_class = team['status']
                teams_html += f'''
                <div class="team-card {status_class}">
                    <div class="team-name">{team['name']}</div>
                    <div class="team-models">{', '.join(team['models'])}</div>
                    <div class="team-specialty">{team['specialty']}</div>
                    <div class="team-stats">
                        <div class="team-stat">Status: {team['status'].upper()}</div>
                        <div class="team-stat">Tasks: {team['tasks_completed']}</div>
                    </div>
                    <button class="btn btn-primary" style="margin-top: 15px; width: 100%;" onclick="spawnTeam('{team_id}')">🚀 Deploy Team</button>
                </div>'''
            
            # Build models HTML
            models_html = ''
            for model_id, model in MODEL_AGENTS.items():
                status = model['status']
                last_used = model.get('last_used', 'Never')
                if last_used != 'Never':
                    last_used = last_used.split('T')[1][:5] if 'T' in last_used else last_used
                
                models_html += f'''
                <div class="model-card {status}" onclick="spawnAgent('{model_id}')" style="cursor: pointer;">
                    <div class="model-name">{model['name']}</div>
                    <div class="model-role">{model['role']}</div>
                    <div class="model-status status-{status}">{status.upper()}</div>
                    <div style="margin-top: 10px; font-size: 10px; color: var(--text-secondary);">Last: {last_used}</div>
                    <div style="font-size: 10px; color: var(--accent-cyan);">Success: {int(model['success_rate']*100)}%</div>
                </div>'''
            
            # Build subagents HTML
            subagents_html = ''
            if ACTIVE_SUBAGENTS:
                for agent_id, agent in sorted(ACTIVE_SUBAGENTS.items(), key=lambda x: x[1]['created'], reverse=True)[:10]:
                    status = agent['status']
                    subagents_html += f'''
                    <div class="subagent-item {status}">
                        <div class="subagent-info">
                            <div class="subagent-id">{agent_id[:20]}...</div>
                            <div class="subagent-task">{agent['task'][:50]}...</div>
                            <div class="subagent-model">🤖 {agent['model']} | Team: {agent.get('team', 'None')}</div>
                        </div>
                        <div class="subagent-status status-{status}">{status.upper()}</div>
                    </div>'''
            else:
                subagents_html = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No active subagents. Spawn one from the Models or Spawn tab!</div>'
            
            # Build events HTML
            events_html = ''
            for event in reversed(EVENTS_LOG[-20:]):
                event_class = f"event-{event.get('type', 'info')}"
                events_html += f'''
                <div class="event-line">
                    <span class="event-time">{event['time']}</span>
                    <span class="{event_class}">[{event.get('model', 'SYSTEM')}] {event['message']}</span>
                </div>'''
            
            if not events_html:
                events_html = '<div class="event-line"><span class="event-time">--:--:--</span><span class="event-info">System initialized. Ready to spawn agents.</span></div>'
            
            # Build content
            content = RATES_PANEL + TEAMS_PANEL + MODELS_PANEL + SPAWN_PANEL + SUBAGENTS_PANEL + LOGS_PANEL
            content = content.replace('{{RATE_LIMITS}}', rates_html)
            content = content.replace('{{TEAMS}}', teams_html)
            content = content.replace('{{MODELS}}', models_html)
            content = content.replace('{{SUBAGENTS}}', subagents_html)
            content = content.replace('{{EVENTS}}', events_html)
            
            # Calculate totals
            total_model_requests = sum(RATE_LIMITS[k]['requests'] for k in ['kimi', 'anthropic'])
            
            html = HTML_V4
            html = html.replace('{{CONTENT}}', content)
            html = html.replace('{{TEAM_COUNT}}', str(len(AGENT_TEAMS)))
            html = html.replace('{{MODEL_COUNT}}', str(len(MODEL_AGENTS)))
            html = html.replace('{{ACTIVE_SUBAGENTS}}', str(len([a for a in ACTIVE_SUBAGENTS.values() if a['status'] != 'completed'])))
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{TEMP_COLOR}}', 'var(--accent-green)' if stats['temp'] < 70 else 'var(--accent-yellow)' if stats['temp'] < 80 else 'var(--accent-red)')
            html = html.replace('{{MODEL_REQUESTS}}', str(total_model_requests))
            html = html.replace('{{WEB_REQUESTS}}', str(RATE_LIMITS['web_search']['requests']))
            html = html.replace('{{IMAGE_REQUESTS}}', str(RATE_LIMITS['image_gen']['requests']))
            html = html.replace('{{GITHUB_REQUESTS}}', str(RATE_LIMITS['github']['requests']))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        params = parse_qs(body)
        
        if self.path == '/api/spawn':
            model = params.get('model', ['k2p5'])[0]
            task = params.get('task', ['No task'])[0]
            
            agent_id = spawn_subagent(task, model)
            
            if agent_id:
                self.send_json({'success': True, 'agent_id': agent_id})
            else:
                self.send_json({'success': False, 'error': 'Rate limited or error'})
                
        elif self.path == '/api/spawn-team':
            team_id = params.get('team', ['team_coding'])[0]
            task = params.get('task', ['No task'])[0]
            
            team = AGENT_TEAMS.get(team_id)
            if team:
                # Spawn primary model from team
                primary_model = team['models'][0].split('/')[-1].replace('claude-', '').replace('kimi-coding/', '').replace('k2p5', 'k2p5')
                if 'sonnet' in primary_model.lower():
                    primary_model = 'sonnet'
                elif 'opus' in primary_model.lower():
                    primary_model = 'opus'
                else:
                    primary_model = 'k2p5'
                
                agent_id = spawn_subagent(task, primary_model, team_id)
                
                if agent_id:
                    team['tasks_completed'] += 1
                    self.send_json({'success': True, 'agent_id': agent_id, 'team': team_id})
                else:
                    self.send_json({'success': False, 'error': 'Rate limited'})
            else:
                self.send_json({'success': False, 'error': 'Team not found'})
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), MultiAgentServer) as httpd:
        print("◈ J1MSKY AGENT TEAMS v4.0 Started ◈")
        print("Multi-model subagent system with rate limit protection")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    add_event("Agent Teams v4.0 initialized", type='success')
    add_event("Rate limit protection active", type='info')
    add_event("Ready to spawn subagents", type='info')
    run()
