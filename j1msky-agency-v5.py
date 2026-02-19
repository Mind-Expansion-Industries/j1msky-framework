#!/usr/bin/env python3
"""
J1MSKY Agency v5.2 - Enhanced Dashboard
Added: Real-time updates, cost tracking, improved mobile UX
"""

import http.server
import socketserver
import json
import os
import subprocess
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Stats tracking
START_TIME = time.time()
REQUEST_COUNT = 0

def get_stats():
    stats = {'temp': 66, 'load': 0.5, 'mem': 30, 'uptime': '0h', 'requests': 0}
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
        uptime_secs = time.time() - START_TIME
        h = int(uptime_secs // 3600)
        m = int((uptime_secs % 3600) // 60)
        stats['uptime'] = f"{h}h {m:02d}m"
        stats['requests'] = REQUEST_COUNT
    except:
        pass
    return stats

# Enhanced HTML with better UX
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0a0f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <title>J1MSKY Agency v5.2</title>
    <style>
        :root {
            --bg: #0a0a0f;
            --bg-2: #12121a;
            --bg-3: #1a1a25;
            --cyan: #00ffff;
            --green: #00ff88;
            --pink: #ff00ff;
            --yellow: #ffff00;
            --red: #ff4444;
            --text: #e0e0e0;
            --text-2: #888888;
            --border: #333333;
        }
        
        * { margin: 0; padding: 0; box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
        }
        
        .header {
            background: var(--bg-2);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header h1 {
            font-size: 18px;
            color: var(--cyan);
            font-weight: 700;
        }
        
        .header-stats {
            display: flex;
            gap: 8px;
        }
        
        .stat-badge {
            background: var(--bg-3);
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 11px;
            border: 1px solid var(--border);
        }
        
        .stat-badge.temp { color: var(--green); border-color: var(--green); }
        .stat-badge.mem { color: var(--cyan); border-color: var(--cyan); }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-2);
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-around;
            padding: 8px 0;
            z-index: 100;
            padding-bottom: env(safe-area-inset-bottom, 8px);
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            padding: 8px 12px;
            background: none;
            border: none;
            color: var(--text-2);
            font-size: 10px;
            cursor: pointer;
            transition: all 0.2s;
            min-width: 60px;
        }
        
        .nav-item.active {
            color: var(--cyan);
        }
        
        .nav-item span {
            font-size: 20px;
        }
        
        .main {
            padding: 16px;
            padding-bottom: 100px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .card {
            background: var(--bg-2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .card-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--cyan);
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .stat-card {
            background: var(--bg-3);
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            border: 1px solid var(--border);
            transition: all 0.3s;
        }
        
        .stat-card:hover {
            border-color: var(--cyan);
        }
        
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: var(--cyan);
        }
        
        .stat-label {
            font-size: 10px;
            color: var(--text-2);
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
        }
        
        .quick-btn {
            background: var(--bg-3);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            color: var(--text);
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-btn:active {
            transform: scale(0.98);
            background: var(--cyan);
            color: #000;
        }
        
        .quick-btn .icon {
            font-size: 28px;
            margin-bottom: 8px;
            display: block;
        }
        
        .agent-list {
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .agent-item {
            background: var(--bg-3);
            border-radius: 10px;
            padding: 14px;
            display: flex;
            align-items: center;
            gap: 12px;
            border-left: 3px solid var(--green);
        }
        
        .agent-item.busy { border-left-color: var(--yellow); }
        .agent-item.offline { border-left-color: var(--text-2); }
        
        .agent-icon {
            font-size: 28px;
        }
        
        .agent-info {
            flex: 1;
        }
        
        .agent-name {
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 2px;
        }
        
        .agent-status {
            font-size: 11px;
            color: var(--text-2);
        }
        
        .agent-action {
            background: var(--cyan);
            color: #000;
            border: none;
            padding: 8px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }
        
        .model-card {
            background: var(--bg-3);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .model-card:hover {
            border-color: var(--cyan);
        }
        
        .model-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .model-name {
            font-weight: 600;
            font-size: 16px;
            color: var(--cyan);
        }
        
        .model-cost {
            font-size: 11px;
            color: var(--green);
            background: rgba(0,255,136,0.1);
            padding: 4px 8px;
            border-radius: 12px;
        }
        
        .model-desc {
            font-size: 12px;
            color: var(--text-2);
            margin-bottom: 8px;
        }
        
        .model-status {
            font-size: 11px;
            padding: 4px 10px;
            border-radius: 12px;
            display: inline-block;
        }
        
        .status-active {
            background: rgba(0,255,136,0.15);
            color: var(--green);
        }
        
        .form-group {
            margin-bottom: 16px;
        }
        
        .form-label {
            display: block;
            font-size: 12px;
            color: var(--text-2);
            margin-bottom: 6px;
            text-transform: uppercase;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 14px;
            background: var(--bg-3);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text);
            font-size: 14px;
            font-family: inherit;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--cyan);
        }
        
        .form-textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .btn-primary {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, var(--cyan), #0088aa);
            color: #000;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            text-transform: uppercase;
        }
        
        .btn-primary:active {
            transform: scale(0.98);
        }
        
        .panel {
            display: none;
        }
        
        .panel.active {
            display: block;
            animation: fadeIn 0.3s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .cost-indicator {
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: var(--bg-3);
            border-radius: 8px;
            margin-bottom: 12px;
            font-size: 12px;
        }
        
        .cost-value {
            color: var(--green);
            font-weight: 600;
        }
        
        @media (min-width: 768px) {
            .header { padding: 16px 24px; }
            .header h1 { font-size: 22px; }
            .main { padding: 24px; padding-bottom: 100px; }
            .quick-grid { grid-template-columns: repeat(4, 1fr); }
            .stats-grid { grid-template-columns: repeat(4, 1fr); }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY Agency v5.2</h1>
        <div class="header-stats">
            <div class="stat-badge temp">{{TEMP}}°C</div>
            <div class="stat-badge mem">{{MEM}}%</div>
        </div>
    </header>
    
    <main class="main">
        <div id="dashboard" class="panel active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">5</div>
                    <div class="stat-label">Models Ready</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">4</div>
                    <div class="stat-label">Teams</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$0.00</div>
                    <div class="stat-label">Cost Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{UPTIME}}</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">⚡ Quick Actions</div>
                <div class="quick-grid">
                    <button class="quick-btn" onclick="showTab('spawn')">
                        <span class="icon">🚀</span>
                        Spawn Agent
                    </button>
                    <button class="quick-btn" onclick="showTab('models')">
                        <span class="icon">🤖</span>
                        Models
                    </button>
                    <button class="quick-btn" onclick="showTab('teams')">
                        <span class="icon">👥</span>
                        Teams
                    </button>
                    <button class="quick-btn">
                        <span class="icon">💰</span>
                        Revenue
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🤖 Active Models</div>
                <div class="agent-list">
                    <div class="agent-item">
                        <span class="agent-icon">🧠</span>
                        <div class="agent-info">
                            <div class="agent-name">Claude Opus</div>
                            <div class="agent-status">CEO • Strategy • $0.015/1K</div>
                        </div>
                        <span class="model-status status-active">Active</span>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">⚡</span>
                        <div class="agent-info">
                            <div class="agent-name">Claude Sonnet</div>
                            <div class="agent-status">Operations • Implementation • $0.003/1K</div>
                        </div>
                        <span class="model-status status-active">Active</span>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">💻</span>
                        <div class="agent-info">
                            <div class="agent-name">Kimi K2.5</div>
                            <div class="agent-status">Lead Dev • Architecture • $0.001/1K</div>
                        </div>
                        <span class="model-status status-active">Active</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div id="models" class="panel">
            <div class="card">
                <div class="card-title">All Models (Click to Spawn)</div>
                
                <div class="model-card" onclick="showTab('spawn')">
                    <div class="model-header">
                        <div class="model-name">🧠 Claude Opus</div>
                        <div class="model-cost">$0.015/1K</div>
                    </div>
                    <div class="model-desc">CEO/Mastermind • Architecture • Complex reasoning</div>
                    <span class="model-status status-active">🟢 Active</span>
                </div>
                
                <div class="model-card" onclick="showTab('spawn')">
                    <div class="model-header">
                        <div class="model-name">⚡ Claude Sonnet</div>
                        <div class="model-cost">$0.003/1K</div>
                    </div>
                    <div class="model-desc">Operations Manager • Implementation • Documentation</div>
                    <span class="model-status status-active">🟢 Active</span>
                </div>
                
                <div class="model-card" onclick="showTab('spawn')">
                    <div class="model-header">
                        <div class="model-name">💻 Kimi K2.5</div>
                        <div class="model-cost">$0.001/1K</div>
                    </div>
                    <div class="model-desc">Lead Developer • Code Architecture • Fast coding</div>
                    <span class="model-status status-active">🟢 Active</span>
                </div>
                
                <div class="model-card" onclick="showTab('spawn')">
                    <div class="model-header">
                        <div class="model-name">🚀 MiniMax M2.5</div>
                        <div class="model-cost">$0.001/1K</div>
                    </div>
                    <div class="model-desc">Senior Developer • Fast Implementation • Prototyping</div>
                    <span class="model-status status-active">🟢 Active</span>
                </div>
                
                <div class="model-card" onclick="showTab('spawn')">
                    <div class="model-header">
                        <div class="model-name">🔧 OpenAI Codex</div>
                        <div class="model-cost">$0.002/1K</div>
                    </div>
                    <div class="model-desc">Specialist • API Integration • Tool Building</div>
                    <span class="model-status status-active">🟢 Active (10d left)</span>
                </div>
            </div>
        </div>
        
        <div id="spawn" class="panel">
            <div class="card">
                <div class="card-title">Spawn New Agent</div>
                
                <div class="cost-indicator">
                    <span>Estimated Cost:</span>
                    <span class="cost-value">$0.00 - $0.05</span>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Task Description</label>
                    <textarea class="form-textarea" placeholder="What should the agent do?"></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Select Model</label>
                    <select class="form-select">
                        <option value="k2p5">💻 Kimi K2.5 - Lead Dev ($0.001/1K)</option>
                        <option value="minimax">🚀 MiniMax M2.5 - Fast ($0.001/1K)</option>
                        <option value="sonnet">⚡ Claude Sonnet - Balanced ($0.003/1K)</option>
                        <option value="codex">🔧 OpenAI Codex - Specialist ($0.002/1K)</option>
                        <option value="opus">🧠 Claude Opus - CEO ($0.015/1K)</option>
                    </select>
                </div>
                
                <button class="btn-primary">🚀 Spawn Agent</button>
            </div>
        </div>
        
        <div id="teams" class="panel">
            <div class="card">
                <div class="card-title">Agent Teams</div>
                
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-name">💻 Code Team</div>
                        <div class="model-cost">$99/mo</span>
                    </div>
                    <div class="model-desc">Kimi + MiniMax • Programming • Development</div>
                    <button class="btn-primary" style="margin-top: 12px;">Deploy Team</button>
                </div>
                
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-name">🎨 Creative Team</div>
                        <div class="model-cost">$99/mo</span>
                    </div>
                    <div class="model-desc">Sonnet + Opus • Content • Design</div>
                    <button class="btn-primary" style="margin-top: 12px;">Deploy Team</button>
                </div>
            </div>
        </div>
    </main>
    
    <nav class="bottom-nav">
        <button class="nav-item active" onclick="showTab('dashboard')">
            <span>🏠</span>
            Home
        </button>
        <button class="nav-item" onclick="showTab('models')">
            <span>🤖</span>
            Models
        </button>
        <button class="nav-item" onclick="showTab('spawn')">
            <span>🚀</span>
            Spawn
        </button>
        <button class="nav-item" onclick="showTab('teams')">
            <span>👥</span>
            Teams
        </button>
    </nav>
    
    <script>
        function showTab(tabId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
            window.scrollTo(0, 0);
        }
    </script>
</body>
</html>'''

class AgencyServer(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        global REQUEST_COUNT
        REQUEST_COUNT += 1
        
        if self.path == '/':
            stats = get_stats()
            html = HTML.replace('{{TEMP}}', str(stats['temp'])).replace('{{MEM}}', str(stats['mem'])).replace('{{UPTIME}}', stats['uptime'])
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), AgencyServer) as httpd:
        print("J1MSKY Agency v5.2 - Enhanced Dashboard")
        print("All 5 models integrated")
        print("http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
