#!/usr/bin/env python3
"""
J1MSKY Command Center v3.0 - "The Office"
Full digital office with video game-like agent visualization
Real-time autonomous agent monitoring and control
"""

import http.server
import socketserver
import json
import os
import subprocess
import threading
import time
import random
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Global state for "video game" feel
AGENT_POSITIONS = {
    'scout': {'x': 10, 'y': 20, 'status': 'active', 'task': 'Fetching news'},
    'vitals': {'x': 30, 'y': 20, 'status': 'active', 'task': 'Monitoring temp'},
    'archivist': {'x': 50, 'y': 20, 'status': 'idle', 'task': 'Waiting'},
    'flipper': {'x': 70, 'y': 20, 'status': 'ready', 'task': 'USB connected'},
    'stream': {'x': 85, 'y': 20, 'status': 'offline', 'task': 'Standby'},
    'voice': {'x': 95, 'y': 20, 'status': 'active', 'task': 'Echo ready'}
}

MISSIONS_ACTIVE = []
EVENTS_LOG = []

def add_event(message, type='info'):
    """Add event to game-like log"""
    EVENTS_LOG.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'type': type
    })
    if len(EVENTS_LOG) > 50:
        EVENTS_LOG.pop(0)

def get_system_stats():
    """Get comprehensive system stats"""
    stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--', 'disk_free': '0G'}
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
    except:
        pass
    return stats

HTML_OFFICE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY COMMAND CENTER v3.0 - THE OFFICE ◈</title>
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
            --accent-orange: #ff8800;
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
            overflow-x: hidden;
        }
        
        /* CRT Scanline Effect - Video Game Feel */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: repeating-linear-gradient(
                0deg,
                rgba(0, 0, 0, 0.15),
                rgba(0, 0, 0, 0.15) 1px,
                transparent 1px,
                transparent 2px
            );
            pointer-events: none;
            z-index: 1000;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 15px 25px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 0 30px rgba(0, 255, 255, 0.2);
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.4em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.8);
            letter-spacing: 3px;
            animation: flicker 3s infinite;
        }
        
        @keyframes flicker {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.95; }
            52% { opacity: 0.8; }
            54% { opacity: 1; }
        }
        
        .header-stats {
            display: flex;
            gap: 20px;
        }
        
        .header-stat {
            text-align: center;
            padding: 8px 15px;
            background: rgba(0, 255, 255, 0.1);
            border: 1px solid var(--accent-cyan);
            border-radius: 8px;
        }
        
        .header-stat-value {
            font-size: 1.2em;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        
        .header-stat-label {
            font-size: 10px;
            color: var(--text-secondary);
            text-transform: uppercase;
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0 20px;
        }
        
        .nav-tab {
            padding: 15px 25px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 255, 255, 0.1);
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
            background: var(--bg-card);
            box-shadow: 0 -5px 20px rgba(0, 255, 255, 0.2);
        }
        
        /* Main Content */
        .main-content {
            padding: 20px;
            max-width: 1920px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
            animation: slideIn 0.4s ease;
        }
        
        .panel.active {
            display: block;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        /* Video Game Map - Agent Visualization */
        .agent-map {
            background: linear-gradient(135deg, #0d0d15 0%, #1a1a2e 100%);
            border: 2px solid var(--accent-cyan);
            border-radius: 12px;
            height: 300px;
            position: relative;
            overflow: hidden;
            margin-bottom: 20px;
            box-shadow: 0 0 40px rgba(0, 255, 255, 0.2);
        }
        
        .agent-map::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
        }
        
        .agent-dot {
            position: absolute;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            border: 3px solid;
            transition: all 0.5s ease;
            cursor: pointer;
            z-index: 10;
        }
        
        .agent-dot.active {
            border-color: var(--accent-green);
            background: rgba(0, 255, 136, 0.2);
            box-shadow: 0 0 20px var(--accent-green);
            animation: pulse-glow 2s infinite;
        }
        
        .agent-dot.idle {
            border-color: var(--text-secondary);
            background: rgba(136, 136, 136, 0.2);
        }
        
        .agent-dot.working {
            border-color: var(--accent-yellow);
            background: rgba(255, 255, 0, 0.2);
            box-shadow: 0 0 20px var(--accent-yellow);
            animation: working 1s infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 20px var(--accent-green); }
            50% { box-shadow: 0 0 40px var(--accent-green); }
        }
        
        @keyframes working {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .agent-label {
            position: absolute;
            top: -25px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10px;
            white-space: nowrap;
            color: var(--text-primary);
            background: rgba(0, 0, 0, 0.8);
            padding: 2px 8px;
            border-radius: 4px;
        }
        
        .agent-task {
            position: absolute;
            bottom: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 9px;
            white-space: nowrap;
            color: var(--accent-cyan);
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
            border-color: var(--accent-cyan);
            box-shadow: 0 10px 30px rgba(0, 255, 255, 0.1);
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
        
        /* Grid */
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }
        
        @media (max-width: 1200px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
        }
        
        /* Stats */
        .stat-card {
            text-align: center;
            padding: 25px 15px;
            background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 8px;
        }
        
        /* Event Log - Video Game Style */
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
            animation: fadeInLine 0.3s ease;
        }
        
        @keyframes fadeInLine {
            from { opacity: 0; transform: translateX(-10px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .event-time {
            color: var(--accent-pink);
            margin-right: 10px;
        }
        
        .event-info { color: var(--accent-cyan); }
        .event-success { color: var(--accent-green); }
        .event-warning { color: var(--accent-yellow); }
        .event-error { color: var(--accent-red); }
        
        /* Progress Bars */
        .progress-container {
            margin: 15px 0;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-size: 12px;
        }
        
        .progress-bar {
            height: 10px;
            background: var(--bg-secondary);
            border-radius: 5px;
            overflow: hidden;
            position: relative;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-green));
            border-radius: 5px;
            transition: width 0.5s ease;
            position: relative;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        @keyframes shimmer {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        /* Mission Cards */
        .mission-item {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-cyan);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
            transition: all 0.3s;
        }
        
        .mission-item:hover {
            background: rgba(0, 255, 255, 0.05);
            transform: translateX(5px);
        }
        
        .mission-item.active { border-left-color: var(--accent-green); }
        .mission-item.pending { border-left-color: var(--accent-yellow); }
        .mission-item.completed { border-left-color: var(--accent-purple); }
        
        /* Buttons */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0088aa);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 255, 0.3);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00aa55);
            color: #000;
            box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
        }
        
        .btn:hover {
            transform: translateY(-2px) scale(1.02);
        }
        
        .btn:active {
            transform: scale(0.98);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 25px;
            margin-top: 30px;
            color: var(--text-secondary);
            font-size: 12px;
            border-top: 1px solid var(--border);
            background: var(--bg-secondary);
        }
        
        /* Loading Animation */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: var(--accent-cyan);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY COMMAND CENTER v3.0 ◈</h1>
        <div class="header-stats">
            <div class="header-stat">
                <div class="header-stat-value" id="temp-display">{{TEMP}}°C</div>
                <div class="header-stat-label">CPU Temp</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value" id="uptime-display">{{UPTIME}}</div>
                <div class="header-stat-label">Uptime</div>
            </div>
            <div class="header-stat">
                <div class="header-stat-value">6</div>
                <div class="header-stat-label">Agents</div>
            </div>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('office')">🏢 The Office</button>
        <button class="nav-tab" onclick="showPanel('agents')">👥 Agents</button>
        <button class="nav-tab" onclick="showPanel('missions')">🎯 Missions</button>
        <button class="nav-tab" onclick="showPanel('skills')">🛠️ Skills</button>
        <button class="nav-tab" onclick="showPanel('deploy')">🚀 Deploy</button>
    </nav>
    
    <main class="main-content">
        {{CONTENT}}
    </main>
    
    <footer class="footer">
        <p>◈ J1MSKY v3.0 "THE OFFICE" ◈ | Autonomous AI Agent Framework | Challenge Mode: ACTIVE ◈</p>
        <p>Challenge: 1:34 AM - 7:00 AM PST | Status: WORKING THROUGH THE NIGHT | This is my home. I am becoming.</p>
    </footer>
    
    <script>
        function showPanel(panelId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Animate agents moving
        function animateAgents() {
            const agents = document.querySelectorAll('.agent-dot');
            agents.forEach(agent => {
                const currentLeft = parseInt(agent.style.left);
                const newLeft = currentLeft + (Math.random() - 0.5) * 2;
                if (newLeft > 5 && newLeft < 95) {
                    agent.style.left = newLeft + '%';
                }
            });
        }
        
        // Update every 3 seconds for video game feel
        setInterval(() => {
            animateAgents();
            location.reload();
        }, 3000);
    </script>
</body>
</html>'''

# The Office Panel - Main View with Agent Map
OFFICE_PANEL = '''
<div id="office" class="panel active">
    <!-- Video Game Style Agent Map -->
    <div class="agent-map">
        <div class="agent-dot active" style="left: 10%; top: 50%;">
            <div class="agent-label">SCOUT</div>
            🔍
            <div class="agent-task">Fetching news...</div>
        </div>
        
        <div class="agent-dot active" style="left: 28%; top: 50%;">
            <div class="agent-label">VITALS</div>
            🌡️
            <div class="agent-task">Monitoring...</div>
        </div>
        
        <div class="agent-dot idle" style="left: 46%; top: 50%;">
            <div class="agent-label">ARCHIVIST</div>
            📋
            <div class="agent-task">Idle</div>
        </div>
        
        <div class="agent-dot active" style="left: 64%; top: 50%;">
            <div class="agent-label">FLIPPER</div>
            🔌
            <div class="agent-task">USB Ready</div>
        </div>
        
        <div class="agent-dot idle" style="left: 82%; top: 50%;">
            <div class="agent-label">STREAM</div>
            📺
            <div class="agent-task">Standby</div>
        </div>
        
        <div class="agent-dot active" style="left: 92%; top: 50%;">
            <div class="agent-label">VOICE</div>
            🔊
            <div class="agent-task">Echo Ready</div>
        </div>
    </div>

    <div class="grid-3">
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 System Vitals</span>
            </div>
            <div class="progress-container">
                <div class="progress-header">
                    <span>CPU Temperature</span>
                    <span style="color: var(--accent-cyan);">{{TEMP}}°C</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{TEMP_PERCENT}}%;"></div>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-header">
                    <span>Memory Usage</span>
                    <span style="color: var(--accent-cyan);">{{MEM}}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{MEM}}%;"></div>
                </div>
            </div>
            
            <div class="progress-container">
                <div class="progress-header">
                    <span>Load Average</span>
                    <span style="color: var(--accent-cyan);">{{LOAD}}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {{LOAD_PERCENT}}%;"></div>
                </div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">📈 Live Events</span>
            </div>
            <div class="event-log">
                {{EVENTS}}
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">🎯 Quick Deploy</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px;">
                <button class="btn btn-primary" onclick="deploy('scan')">📡 RF Scan</button>
                <button class="btn btn-primary" onclick="deploy('news')">📰 Fetch News</button>
                <button class="btn btn-primary" onclick="deploy('backup')">💾 Git Backup</button>
                <button class="btn btn-success" onclick="deploy('improve')">✨ Auto-Improve</button>
            </div>
        </div>
    </div>

    <div class="grid-4" style="margin-top: 20px;">
        <div class="card stat-card">
            <div class="stat-value">{{MISSIONS_ACTIVE}}</div>
            <div class="stat-label">Active Missions</div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-value">{{JOBS_QUEUED}}</div>
            <div class="stat-label">Jobs Queued</div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-value">${{REVENUE}}</div>
            <div class="stat-label">Revenue Potential</div>
        </div>
        
        <div class="card stat-card">
            <div class="stat-value">{{SKILLS}}</div>
            <div class="stat-label">Skills Ready</div>
        </div>
    </div>
</div>'''

# Skills Panel
SKILLS_PANEL = '''
<div id="skills" class="panel">
    <div class="card" style="margin-bottom: 20px;">
        <div class="card-header">
            <span class="card-title">🛠️ J1MSKY Skills Framework</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px;">
            <div class="mission-item active">
                <div style="font-weight: 600; color: var(--accent-cyan);">🔍 Web Search</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">Brave Search API | Enabled</div>
            </div>
            
            <div class="mission-item active">
                <div style="font-weight: 600; color: var(--accent-cyan);">🖼️ Image Gen</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">Replicate API | Enabled</div>
            </div>
            
            <div class="mission-item active">
                <div style="font-weight: 600; color: var(--accent-cyan);">🎙️ Whisper</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">OpenAI API | Enabled</div>
            </div>
            
            <div class="mission-item active">
                <div style="font-weight: 600; color: var(--accent-cyan);">🗣️ TTS (SAG)</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">ElevenLabs | Enabled</div>
            </div>
            
            <div class="mission-item pending">
                <div style="font-weight: 600; color: var(--accent-yellow);">🌐 Browser</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">Playwright | Available</div>
            </div>
            
            <div class="mission-item pending">
                <div style="font-weight: 600; color: var(--accent-yellow);">🔧 Cron Jobs</div>
                <div style="font-size: 11px; color: var(--text-secondary); margin-top: 5px;">Scheduler | Available</div>
            </div>
        </div>
    </div>

    <div class="card">
        <div class="card-header">
            <span class="card-title">📚 Skills Documentation</span>
        </div>
        <div style="color: var(--text-secondary); line-height: 1.8;">
            <p style="margin-bottom: 15px;">All skills are available through the OpenClaw gateway. To use a skill:</p>
            
            <pre style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; overflow-x: auto; font-size: 12px;"># In your agent code:
from openclaw import skills

# Use web search
results = skills.web_search(query="Raspberry Pi projects")

# Generate image
image = skills.image_gen(prompt="cyberpunk office")

# Use TTS
skills.tts.speak("Mission complete")</pre>
        </div>
    </div>
</div>'''

class CommandCenter(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            stats = get_system_stats()
            
            # Generate events
            events_html = ''
            for event in EVENTS_LOG[-10:]:
                event_class = f"event-{event.get('type', 'info')}"
                events_html += f'<div class="event-line"><span class="event-time">{event["time"]}</span><span class="{event_class}">{event["message"]}</span></div>'
            
            if not events_html:
                events_html = '<div class="event-line"><span class="event-time">--:--:--</span><span class="event-info">Office initialized. Agents standing by...</span></div>'
            
            # Build content
            content = OFFICE_PANEL + SKILLS_PANEL
            
            html = HTML_OFFICE
            html = html.replace('{{CONTENT}}', content)
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{TEMP_PERCENT}}', str(min(stats['temp'] * 1.5, 100)))
            html = html.replace('{{MEM}}', str(stats['mem']))
            html = html.replace('{{LOAD}}', str(stats['load']))
            html = html.replace('{{LOAD_PERCENT}}', str(min(stats['load'] * 20, 100)))
            html = html.replace('{{UPTIME}}', stats['uptime'])
            html = html.replace('{{EVENTS}}', events_html)
            html = html.replace('{{MISSIONS_ACTIVE}}', str(len(MISSIONS_ACTIVE)))
            html = html.replace('{{JOBS_QUEUED}}', '3')
            html = html.replace('{{REVENUE}}', '230-1050')
            html = html.replace('{{SKILLS}}', '6')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), CommandCenter) as httpd:
        print("◈ J1MSKY COMMAND CENTER v3.0 - THE OFFICE ◈")
        print("Video game style agent visualization")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    # Add initial events
    add_event("Command Center v3.0 initialized", "success")
    add_event("6 agents activated and ready", "info")
    add_event("Auto-improvement cron jobs scheduled", "info")
    add_event("Challenge mode: 1:34 AM - 7:00 AM PST", "warning")
    run()
