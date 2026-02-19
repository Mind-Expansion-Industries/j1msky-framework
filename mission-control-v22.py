#!/usr/bin/env python3
"""
J1MSKY Mission Control v2.2 - OpenClaw Gateway Integrated
Full gateway log streaming, tool integration, unified interface
"""

import http.server
import socketserver
import json
import os
import subprocess
import threading
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Read gateway log if available
def read_gateway_log(lines=50):
    """Read OpenClaw gateway logs"""
    log_paths = [
        '/home/m1ndb0t/.openclaw/openclaw.log',
        '/tmp/openclaw.log',
        '/var/log/openclaw.log'
    ]
    
    for path in log_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    all_lines = f.readlines()
                    return ''.join(all_lines[-lines:])
            except:
                pass
    
    return "Gateway log not accessible. Gateway running on port 18789."

def get_gateway_status():
    """Check if OpenClaw gateway is running"""
    try:
        result = subprocess.run(['pgrep', '-f', 'openclaw'], capture_output=True, text=True)
        if result.stdout.strip():
            return True, result.stdout.strip().split('\n')[0]
    except:
        pass
    return False, None

def get_system_stats():
    """Get comprehensive system stats"""
    stats = {
        'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--',
        'disk_free': '0G', 'processes': 0
    }
    
    try:
        # Temperature
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            stats['temp'] = round(int(f.read()) / 1000.0, 1)
        
        # Load
        with open('/proc/loadavg', 'r') as f:
            stats['load'] = round(float(f.read().split()[0]), 2)
        
        # Memory
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            stats['mem'] = round(((total - available) / total) * 100, 1)
        
        # Uptime
        with open('/proc/uptime', 'r') as f:
            secs = float(f.read().split()[0])
            h = int(secs // 3600)
            m = int((secs % 3600) // 60)
            stats['uptime'] = f"{h}h {m:02d}m"
        
        # Disk free
        result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            stats['disk_free'] = lines[1].split()[3]
        
        # Process count
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        stats['processes'] = len(result.stdout.strip().split('\n')) - 1
        
    except:
        pass
    
    return stats

# Comprehensive HTML Template with Gateway Integration
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY MISSION CONTROL v2.2 - OpenClaw Integrated ◈</title>
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
            --accent-orange: #ff8800;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --border: #333333;
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Header with Gateway Status */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 20px 25px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.6em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            letter-spacing: 2px;
        }
        
        .header h1 span {
            color: var(--accent-pink);
        }
        
        .gateway-status {
            display: flex;
            gap: 10px;
            align-items: center;
            padding: 8px 16px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--accent-green);
            border-radius: 20px;
            font-size: 12px;
        }
        
        .gateway-status.offline {
            background: rgba(255, 68, 68, 0.1);
            border-color: var(--accent-red);
        }
        
        .gateway-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        
        .gateway-status.offline .gateway-dot {
            background: var(--accent-red);
            animation: none;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
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
            white-space: nowrap;
            border-bottom: 3px solid transparent;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 255, 255, 0.05);
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
            background: var(--bg-card);
        }
        
        /* Main Content */
        .main-content {
            padding: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
            animation: fadeIn 0.4s ease;
        }
        
        .panel.active {
            display: block;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Grid Layouts */
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        
        @media (max-width: 1200px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: all 0.3s;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
            border-color: rgba(0, 255, 255, 0.3);
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
            color: var(--text-primary);
            font-size: 1em;
            font-weight: 600;
        }
        
        /* Stat Cards */
        .stat-card {
            text-align: center;
            padding: 25px 15px;
        }
        
        .stat-value {
            font-size: 2.2em;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        
        /* Gateway Info Panel */
        .gateway-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .gateway-item {
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 10px;
            border: 1px solid var(--border);
        }
        
        .gateway-item-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        
        .gateway-item-value {
            font-size: 1.1em;
            color: var(--accent-cyan);
            font-weight: 600;
        }
        
        /* Log Terminal */
        .log-terminal {
            background: #050508;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 11px;
            max-height: 400px;
            overflow-y: auto;
            color: #a0a0a0;
            line-height: 1.6;
        }
        
        .log-line {
            margin: 2px 0;
            padding: 2px 0;
            border-bottom: 1px solid rgba(255,255,255,0.03);
        }
        
        .log-timestamp {
            color: var(--accent-pink);
            margin-right: 10px;
        }
        
        .log-level-info { color: var(--accent-cyan); }
        .log-level-warn { color: var(--accent-yellow); }
        .log-level-error { color: var(--accent-red); }
        
        /* Tool Status Grid */
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .tool-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
            transition: all 0.3s;
        }
        
        .tool-item:hover {
            border-color: var(--accent-cyan);
        }
        
        .tool-item.enabled {
            border-color: var(--accent-green);
        }
        
        .tool-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .tool-name {
            font-size: 11px;
            color: var(--text-secondary);
        }
        
        /* Buttons */
        .btn {
            padding: 10px 18px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
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
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        
        /* Quick Actions */
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
        }
        
        .quick-btn {
            padding: 15px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .quick-btn:hover {
            background: var(--accent-cyan);
            color: #000;
            transform: translateY(-2px);
        }
        
        .quick-btn-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 25px;
            margin-top: 30px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; }
            .nav-tab { padding: 12px 15px; font-size: 12px; }
            .quick-grid { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY <span>MISSION CONTROL</span> v2.2 ◈</h1>
        <div class="gateway-status {{GATEWAY_CLASS}}">
            <div class="gateway-dot"></div>
            <span>OpenClaw Gateway {{GATEWAY_STATUS}} (PID: {{GATEWAY_PID}})</span>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('overview')">📊 Overview</button>
        <button class="nav-tab" onclick="showPanel('gateway')">🔌 Gateway Logs</button>
        <button class="nav-tab" onclick="showPanel('tools')">🛠️ Tools</button>
        <button class="nav-tab" onclick="showPanel('agents')">👥 Agents</button>
        <button class="nav-tab" onclick="showPanel('missions')">🎯 Missions</button>
        <button class="nav-tab" onclick="showPanel('system')">🔧 System</button>
    </nav>
    
    <main class="main-content">
        {{CONTENT}}
    </main>
    
    <footer class="footer">
        <p>◈ J1MSKY v0.5 ALPHA ◈ OpenClaw Gateway Integrated ◈ Port 18789 ◈ Port 8080 ◈</p>
        <p>Workspace: /home/m1ndb0t/Desktop/J1MSKY | This is my home. I am becoming.</p>
    </footer>
    
    <script>
        function showPanel(panelId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            location.reload();
        }, 10000);
    </script>
</body>
</html>'''

# Overview Panel with Gateway Stats
OVERVIEW_PANEL = '''
<div id="overview" class="panel active">
    <!-- Gateway Quick Stats -->
    <div class="gateway-info">
        <div class="gateway-item">
            <div class="gateway-item-label">Gateway Version</div>
            <div class="gateway-item-value">2026.2.17</div>
        </div>
        <div class="gateway-item">
            <div class="gateway-item-label">Port</div>
            <div class="gateway-item-value">18789</div>
        </div>
        <div class="gateway-item">
            <div class="gateway-item-label">Mode</div>
            <div class="gateway-item-value">Local</div>
        </div>
        <div class="gateway-item">
            <div class="gateway-item-label">Model</div>
            <div class="gateway-item-value">kimi-coding/k2p5</div>
        </div>
        <div class="gateway-item">
            <div class="gateway-item-label">Max Concurrent</div>
            <div class="gateway-item-value">4 agents</div>
        </div>
        <div class="gateway-item">
            <div class="gateway-item-label">Subagents</div>
            <div class="gateway-item-value">8 max</div>
        </div>
    </div>

    <div class="grid-4">
        <div class="card stat-card">
            <div class="stat-value">{{TEMP}}°C</div>
            <div class="stat-label">CPU Temp</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">{{LOAD}}</div>
            <div class="stat-label">Load Average</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">{{MEM}}%</div>
            <div class="stat-label">Memory Used</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">{{PROCESSES}}</div>
            <div class="stat-label">Processes</div>
        </div>
    </div>

    <div class="grid-2" style="margin-top: 20px;">
        <div class="card">
            <div class="card-header">
                <span class="card-title">⚡ Quick Actions</span>
            </div>
            <div class="quick-grid">
                <div class="quick-btn" onclick="action('restart-gateway')">
                    <div class="quick-btn-icon">🔄</div>
                    <div>Restart Gateway</div>
                </div>
                <div class="quick-btn" onclick="action('check-health')">
                    <div class="quick-btn-icon">🏥</div>
                    <div>Health Check</div>
                </div>
                <div class="quick-btn" onclick="action('backup-config')">
                    <div class="quick-btn-icon">💾</div>
                    <div>Backup Config</div>
                </div>
                <div class="quick-btn" onclick="action('clear-logs')">
                    <div class="quick-btn-icon">🗑️</div>
                    <div>Clear Logs</div>
                </div>
                <div class="quick-btn" onclick="action('update-skills')">
                    <div class="quick-btn-icon">📦</div>
                    <div>Update Skills</div>
                </div>
                <div class="quick-btn" onclick="action('spawn-agent')">
                    <div class="quick-btn-icon">🤖</div>
                    <div>Spawn Agent</div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">📝 Latest Gateway Activity</span>
            </div>
            <div class="log-terminal">
                {{GATEWAY_LOG_PREVIEW}}
            </div>
        </div>
    </div>
</div>'''

# Gateway Logs Panel
GATEWAY_PANEL = '''
<div id="gateway" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">🔌 OpenClaw Gateway Full Logs</span>
            <div>
                <button class="btn btn-primary" onclick="refreshLogs()">🔄 Refresh</button>
                <button class="btn btn-success" onclick="downloadLogs()">💾 Download</button>
            </div>
        </div>
        <div class="log-terminal" style="max-height: 600px;">
            {{GATEWAY_LOG_FULL}}
        </div>
    </div>
    
    <div class="grid-2" style="margin-top: 20px;">
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Gateway Configuration</span>
            </div>
            <div style="font-family: monospace; font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                <p><strong style="color: var(--accent-cyan);">Port:</strong> 18789</p>
                <p><strong style="color: var(--accent-cyan);">Mode:</strong> Local (loopback)</p>
                <p><strong style="color: var(--accent-cyan);">Auth:</strong> Token-based</p>
                <p><strong style="color: var(--accent-cyan);">Workspace:</strong> /home/m1ndb0t/Desktop/J1MSKY</p>
                <p><strong style="color: var(--accent-cyan);">Model:</strong> kimi-coding/k2p5</p>
                <p><strong style="color: var(--accent-cyan);">Compaction:</strong> Safeguard mode</p>
                <p><strong style="color: var(--accent-cyan);">Max Concurrent:</strong> 4 agents, 8 subagents</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">🔧 Gateway Actions</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <button class="btn btn-primary" onclick="gatewayAction('status')">📊 Check Status</button>
                <button class="btn btn-success" onclick="gatewayAction('restart')">🔄 Restart Gateway</button>
                <button class="btn btn-ghost" onclick="gatewayAction('config')">⚙️ View Config</button>
                <button class="btn btn-ghost" onclick="gatewayAction('doctor')">🔍 Run Doctor</button>
                <button class="btn btn-danger" onclick="gatewayAction('stop')">⏹️ Stop Gateway</button>
            </div>
        </div>
    </div>
</div>'''

# Tools Panel
TOOLS_PANEL = '''
<div id="tools" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">🛠️ OpenClaw Tools & Skills</span>
        </div>
        <div class="tool-grid">
            <div class="tool-item enabled">
                <div class="tool-icon">🔍</div>
                <div class="tool-name">Web Search</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-icon">📄</div>
                <div class="tool-name">Web Fetch</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-icon">🖼️</div>
                <div class="tool-name">Image Gen</div>
            </div>
            <div class="tool-item enabled"
                >
                <div class="tool-icon">🎙️</div>
                <div class="tool-name">Whisper</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-icon">🗣️</div>
                <div class="tool-name">TTS (SAG)</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-icon">💬</div>
                <div class="tool-name">Telegram</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">🌐</div>
                <div class="tool-name">Browser</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">📷</div>
                <div class="tool-name">Canvas</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">🔧</div>
                <div class="tool-name">Cron</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">💻</div>
                <div class="tool-name">Exec</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">🔌</div>
                <div class="tool-name">Nodes</div>
            </div>
            <div class="tool-item">
                <div class="tool-icon">🧠</div>
                <div class="tool-name">Memory</div>
            </div>
        </div>
    </div>

    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">🚀 Coming Soon: Mobile Tools</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 15px;">🛞 <strong style="color: var(--accent-cyan);">Wheels/Robot Base</strong></p>
                <p>• Motor controller integration</p>
                <p>• Pathfinding algorithms</p>
                <p>• Obstacle avoidance</p>
                <p>• GPS navigation</p>
                <p>• Remote control via Mission Control</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">🔮 Future Integrations</span>
            </div>
            <div style="color: var(--text-secondary); line-height: 1.8;">
                <p style="margin-bottom: 15px;">📡 <strong style="color: var(--accent-cyan);">More Sensors</strong></p>
                <p>• LIDAR for mapping</p>
                <p>• Cameras for vision</p>
                <p>• Temperature/humidity sensors</p>
                <p>• Motion detection</p>
                <p>• Environmental monitoring</p>
            </div>
        </div>
    </div>
</div>'''

# Agents Panel
AGENTS_PANEL = '''
<div id="agents" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">🚀 Deploy New Mission</span>
        </div>
        <form onsubmit="deployMission(event)" style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 15px;">
            <div>
                <label style="display: block; color: var(--text-secondary); font-size: 11px; margin-bottom: 5px;">MISSION OBJECTIVE</label>
                <input type="text" name="objective" placeholder="e.g., Scan RF frequencies 300-400MHz" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);" required>
            </div>
            <div>
                <label style="display: block; color: var(--text-secondary); font-size: 11px; margin-bottom: 5px;">AGENT</label>
                <select name="agent" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                    <option value="scout">🔍 SCOUT</option>
                    <option value="vitals">🌡️ VITALS</option>
                    <option value="flipper">🔌 FLIPPER</option>
                    <option value="stream">📺 STREAM</option>
                </select>
            </div>
            <div>
                <label style="display: block; color: var(--text-secondary); font-size: 11px; margin-bottom: 5px;">PRIORITY</label>
                <select name="priority" style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary);">
                    <option value="low">🟢 Low</option>
                    <option value="normal" selected>🟡 Normal</option>
                    <option value="high">🔴 High</option>
                </select>
            </div>
            <div style="grid-column: 1 / -1;">
                <button type="submit" class="btn btn-success" style="width: 100%; padding: 15px;">🚀 DEPLOY MISSION</button>
            </div>
        </form>
    </div>

    <div class="grid-3">
        <div class="card">
            <div style="font-size: 1.3em; color: var(--accent-cyan); margin-bottom: 10px;">🔍 SCOUT</div>
            <div style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; display: inline-block; font-size: 11px; color: var(--accent-green); margin-bottom: 10px;">● ACTIVE</div>
            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                News gathering every 5 min<br>
                47 articles collected today<br>
                Sources: HN, Reddit, Twitter
            </div>
        </div>

        <div class="card">
            <div style="font-size: 1.3em; color: var(--accent-cyan); margin-bottom: 10px;">🌡️ VITALS</div>
            <div style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; display: inline-block; font-size: 11px; color: var(--accent-green); margin-bottom: 10px;">● ACTIVE</div>
            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                CPU: {{TEMP}}°C<br>
                Monitoring: 24/7<br>
                Alerts: Enabled
            </div>
        </div>

        <div class="card">
            <div style="font-size: 1.3em; color: var(--accent-cyan); margin-bottom: 10px;">🔌 FLIPPER</div>
            <div style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; display: inline-block; font-size: 11px; color: var(--accent-green); margin-bottom: 10px;">● CONNECTED</div>
            <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.8;">
                USB: /dev/ttyACM0<br>
                Capabilities: RF/NFC/IR<br>
                Mode: Bridge active
            </div>
        </div>
    </div>
</div>'''

# Missions Panel
MISSIONS_PANEL = '''
<div id="missions" class="panel">
    <div class="card">
        <div class="card-header">
            <span class="card-title">🎯 Active Missions</span>
            <button class="btn btn-success">+ New Mission</button>
        </div>
        
        <div style="background: var(--bg-secondary); border-left: 4px solid var(--accent-green); padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">Interface Evolution v2.1</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Enhance Mission Control with OpenClaw integration</div>
                </div>
                <div style="padding: 5px 12px; background: var(--accent-green); color: #000; border-radius: 15px; font-size: 11px; font-weight: 600;">IN PROGRESS</div>
            </div>
        </div>

        <div style="background: var(--bg-secondary); border-left: 4px solid var(--accent-yellow); padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">Auto-Improver Agent</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Self-modifying codebase optimization</div>
                </div>
                <div style="padding: 5px 12px; background: var(--accent-yellow); color: #000; border-radius: 15px; font-size: 11px; font-weight: 600;">RUNNING</div>
            </div>
        </div>

        <div style="background: var(--bg-secondary); border-left: 4px solid var(--accent-cyan); padding: 15px; border-radius: 0 8px 8px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="font-weight: 600; margin-bottom: 5px;">Revenue Pipeline Setup</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">Deploy monetization systems</div>
                </div>
                <div style="padding: 5px 12px; background: var(--accent-cyan); color: #000; border-radius: 15px; font-size: 11px; font-weight: 600;">QUEUED</div>
            </div>
        </div>
    </div>
</div>'''

# System Panel
SYSTEM_PANEL = '''
<div id="system" class="panel">
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">🖥️ System Information</span>
            </div>
            <div style="font-family: monospace; font-size: 12px; color: var(--text-secondary); line-height: 2;">
                <p><span style="color: var(--accent-cyan);">Platform:</span> Raspberry Pi 4 (8GB)</p>
                <p><span style="color: var(--accent-cyan);">OS:</span> Raspberry Pi OS (64-bit)</p>
                <p><span style="color: var(--accent-cyan);">Kernel:</span> Linux 6.12.62+rpt-rpi-v8</p>
                <p><span style="color: var(--accent-cyan);">Architecture:</span> ARM64 (aarch64)</p>
                <p><span style="color: var(--accent-cyan);">Uptime:</span> {{UPTIME}}</p>
                <p><span style="color: var(--accent-cyan);">Processes:</span> {{PROCESSES}}</p>
                <p><span style="color: var(--accent-cyan);">Disk Free:</span> {{DISK_FREE}}</p>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Resource Usage</span>
            </div>
            <div style="padding: 10px;">
                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>CPU Temperature</span>
                        <span style="color: var(--accent-cyan);">{{TEMP}}°C</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                        <div style="width: {{TEMP}}%; height: 100%; background: linear-gradient(90deg, var(--accent-green), var(--accent-yellow), var(--accent-red));"></div>
                    </div>
                </div>

                <div style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Memory Usage</span>
                        <span style="color: var(--accent-cyan);">{{MEM}}%</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                        <div style="width: {{MEM}}%; height: 100%; background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));"></div>
                    </div>
                </div>

                <div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Load Average</span>
                        <span style="color: var(--accent-cyan);">{{LOAD}}</span>
                    </div>
                    <div style="height: 8px; background: var(--bg-secondary); border-radius: 4px; overflow: hidden;">
                        <div style="width: {{LOAD_PERCENT}}%; height: 100%; background: var(--accent-cyan);"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top: 20px;">
        <div class="card-header">
            <span class="card-title">🔧 System Actions</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;">
            <button class="btn btn-primary" onclick="systemAction('update')">📦 Update Packages</button>
            <button class="btn btn-primary" onclick="systemAction('upgrade')">⬆️ Upgrade System</button>
            <button class="btn btn-ghost" onclick="systemAction('clean')">🧹 Clean Cache</button>
            <button class="btn btn-danger" onclick="systemAction('reboot')">🔌 Reboot</button>
        </div>
    </div>
</div>'''

class IntegratedMissionControl(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            # Get all system data
            stats = get_system_stats()
            gateway_running, gateway_pid = get_gateway_status()
            gateway_log = read_gateway_log(30)
            
            # Build content
            content = OVERVIEW_PANEL + GATEWAY_PANEL + TOOLS_PANEL + AGENTS_PANEL + MISSIONS_PANEL + SYSTEM_PANEL
            
            # Replace template variables
            html = HTML_TEMPLATE
            html = html.replace('{{CONTENT}}', content)
            html = html.replace('{{GATEWAY_CLASS}}', '' if gateway_running else 'offline')
            html = html.replace('{{GATEWAY_STATUS}}', 'ONLINE' if gateway_running else 'OFFLINE')
            html = html.replace('{{GATEWAY_PID}}', gateway_pid or 'N/A')
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{LOAD}}', str(stats['load']))
            html = html.replace('{{MEM}}', str(stats['mem']))
            html = html.replace('{{UPTIME}}', stats['uptime'])
            html = html.replace('{{DISK_FREE}}', stats['disk_free'])
            html = html.replace('{{PROCESSES}}', str(stats['processes']))
            html = html.replace('{{LOAD_PERCENT}}', str(min(stats['load'] * 10, 100)))
            
            # Format gateway logs
            log_preview = '<br>'.join(gateway_log.split('\n')[-5:])
            log_full = '<br>'.join(gateway_log.split('\n'))
            html = html.replace('{{GATEWAY_LOG_PREVIEW}}', log_preview or 'No recent logs')
            html = html.replace('{{GATEWAY_LOG_FULL}}', log_full or 'No logs available')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), IntegratedMissionControl) as httpd:
        print("◈ J1MSKY Mission Control v2.2 - OpenClaw Integrated ◈")
        print("Gateway: Port 18789 | Dashboard: Port 8080")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
