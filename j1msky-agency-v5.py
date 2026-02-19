#!/usr/bin/env python3
"""
J1MSKY Agency v5.0 - Responsive Multi-Device Dashboard
Mobile-first, PWA-ready, business-focused
"""

import http.server
import socketserver
import json
import os
import subprocess
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Get system stats
def get_stats():
    stats = {'temp': 66, 'load': 0.5, 'mem': 30, 'uptime': '12h'}
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

# HTML with Responsive Design
HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#0a0a0f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>J1MSKY Agency</title>
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
        
        /* Header */
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
            gap: 12px;
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
        
        /* Bottom Nav (Mobile) */
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
        }
        
        .nav-item.active {
            color: var(--cyan);
        }
        
        .nav-item span {
            font-size: 20px;
        }
        
        /* Main Content */
        .main {
            padding: 16px;
            padding-bottom: 80px;
        }
        
        /* Cards */
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
        }
        
        /* Quick Actions */
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
        
        /* Agents */
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
        
        /* Forms */
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
        
        /* Panels */
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
        
        /* Stats Grid */
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
        
        /* Tablet */
        @media (min-width: 768px) {
            .header { padding: 16px 24px; }
            .header h1 { font-size: 22px; }
            .main { padding: 24px; padding-bottom: 100px; }
            .quick-grid { grid-template-columns: repeat(4, 1fr); }
            .stats-grid { grid-template-columns: repeat(4, 1fr); }
            .bottom-nav { padding: 12px 0; }
            .nav-item { font-size: 12px; }
            .nav-item span { font-size: 24px; }
        }
        
        /* Desktop */
        @media (min-width: 1024px) {
            body {
                display: grid;
                grid-template-columns: 250px 1fr;
                grid-template-rows: auto 1fr;
            }
            
            .header {
                grid-column: 1 / -1;
                position: relative;
            }
            
            .sidebar {
                display: flex;
                flex-direction: column;
                background: var(--bg-2);
                border-right: 1px solid var(--border);
                padding: 20px;
            }
            
            .sidebar-nav {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .sidebar-btn {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 14px;
                background: none;
                border: none;
                color: var(--text-2);
                font-size: 14px;
                border-radius: 8px;
                cursor: pointer;
                text-align: left;
            }
            
            .sidebar-btn.active {
                background: var(--bg-3);
                color: var(--cyan);
            }
            
            .sidebar-btn span {
                font-size: 20px;
            }
            
            .main {
                padding: 32px;
                overflow-y: auto;
            }
            
            .bottom-nav { display: none; }
            
            .grid-desktop {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 24px;
            }
        }
        
        /* Hide sidebar on mobile/tablet */
        .sidebar { display: none; }
        @media (min-width: 1024px) { .sidebar { display: flex; } }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY AGENCY</h1>
        <div class="header-stats">
            <div class="stat-badge temp">{{TEMP}}°C</div>
            <div class="stat-badge mem">{{MEM}}%</div>
        </div>
    </header>
    
    <!-- Desktop Sidebar -->
    <aside class="sidebar">
        <nav class="sidebar-nav">
            <button class="sidebar-btn active" onclick="showTab('dashboard')"><span>🏠</span> Dashboard</button>
            <button class="sidebar-btn" onclick="showTab('agents')"><span>🤖</span> Agents</button>
            <button class="sidebar-btn" onclick="showTab('spawn')"><span>🚀</span> Spawn</button>
            <button class="sidebar-btn" onclick="showTab('teams')"><span>👥</span> Teams</button>
            <button class="sidebar-btn" onclick="showTab('billing')"><span>💰</span> Billing</button>
        </nav>
    </aside>
    
    <main class="main">
        <!-- Dashboard Panel -->
        <div id="dashboard" class="panel active">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">6</div>
                    <div class="stat-label">Active Agents</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">12</div>
                    <div class="stat-label">Tasks Today</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$45</div>
                    <div class="stat-label">Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">98%</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Quick Actions</div>
                <div class="quick-grid">
                    <button class="quick-btn" onclick="showTab('spawn')">
                        <span class="icon">🚀</span>
                        Spawn Agent
                    </button>
                    <button class="quick-btn" onclick="showTab('teams')">
                        <span class="icon">👥</span>
                        Deploy Team
                    </button>
                    <button class="quick-btn">
                        <span class="icon">📊</span>
                        View Stats
                    </button>
                    <button class="quick-btn">
                        <span class="icon">💰</span>
                        Revenue
                    </button>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Active Agents</div>
                <div class="agent-list">
                    <div class="agent-item">
                        <span class="agent-icon">🔍</span>
                        <div class="agent-info">
                            <div class="agent-name">SCOUT</div>
                            <div class="agent-status">Fetching news...</div>
                        </div>
                        <button class="agent-action">View</button>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">🌡️</span>
                        <div class="agent-info">
                            <div class="agent-name">VITALS</div>
                            <div class="agent-status">Monitoring system...</div>
                        </div>
                        <button class="agent-action">View</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Agents Panel -->
        <div id="agents" class="panel">
            <div class="card">
                <div class="card-title">Available Models</div>
                <div class="agent-list">
                    <div class="agent-item">
                        <span class="agent-icon">⚡</span>
                        <div class="agent-info">
                            <div class="agent-name">Kimi K2.5</div>
                            <div class="agent-status">Fast coding • $0.001/1K tokens</div>
                        </div>
                        <button class="agent-action" onclick="showTab('spawn')">Spawn</button>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">🎨</span>
                        <div class="agent-info">
                            <div class="agent-name">Claude Sonnet</div>
                            <div class="agent-status">Creative work • $0.003/1K tokens</div>
                        </div>
                        <button class="agent-action" onclick="showTab('spawn')">Spawn</button>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">🧠</span>
                        <div class="agent-info">
                            <div class="agent-name">Claude Opus</div>
                            <div class="agent-status">Deep reasoning • $0.015/1K tokens</div>
                        </div>
                        <button class="agent-action" onclick="showTab('spawn')">Spawn</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Spawn Panel -->
        <div id="spawn" class="panel">
            <div class="card">
                <div class="card-title">Spawn New Agent</div>
                
                <div class="form-group">
                    <label class="form-label">Task Description</label>
                    <textarea class="form-textarea" placeholder="What should the agent do?"></textarea>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Select Model</label>
                    <select class="form-select">
                        <option value="k2p5">Kimi K2.5 - Fast Coder</option>
                        <option value="sonnet">Claude Sonnet - Creative</option>
                        <option value="opus">Claude Opus - Deep Thinker</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label class="form-label">Priority</label>
                    <select class="form-select">
                        <option>🟢 Low - Background</option>
                        <option selected>🟡 Normal</option>
                        <option>🔴 High - Urgent</option>
                    </select>
                </div>
                
                <button class="btn-primary">🚀 Spawn Agent</button>
            </div>
        </div>
        
        <!-- Teams Panel -->
        <div id="teams" class="panel">
            <div class="card">
                <div class="card-title">Agent Teams</div>
                <div class="agent-list">
                    <div class="agent-item">
                        <span class="agent-icon">💻</span>
                        <div class="agent-info">
                            <div class="agent-name">Code Team</div>
                            <div class="agent-status">Programming & Development</div>
                        </div>
                        <button class="agent-action">Deploy</button>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">🎨</span>
                        <div class="agent-info">
                            <div class="agent-name">Creative Team</div>
                            <div class="agent-status">Content & Design</div>
                        </div>
                        <button class="agent-action">Deploy</button>
                    </div>
                    
                    <div class="agent-item">
                        <span class="agent-icon">🔍</span>
                        <div class="agent-info">
                            <div class="agent-name">Research Team</div>
                            <div class="agent-status">Analysis & Intelligence</div>
                        </div>
                        <button class="agent-action">Deploy</button>
                    </div>
                </div>
            </div>
        </div>
        
        
        <!-- Billing Panel -->
        <div id="billing" class="panel">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">$127</div>
                    <div class="stat-label">Revenue</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$23</div>
                    <div class="stat-label">Costs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$104</div>
                    <div class="stat-label">Profit</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">12</div>
                    <div class="stat-label">Clients</div>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">Rate Limits</div>
                <div style="color: var(--text-2); font-size: 14px;">
                    <p>🟢 Kimi: 67/100 remaining</p>
                    <p>🟢 Anthropic: 38/50 remaining</p>
                    <p>🟢 Web Search: 89/100 remaining</p>
                </div>
            </div>
        </div>
    </main>
    
    <!-- Mobile Bottom Nav -->
    <nav class="bottom-nav">
        <button class="nav-item active" onclick="showTab('dashboard')">
            <span>🏠</span>
            Home
        </button>
        <button class="nav-item" onclick="showTab('agents')">
            <span>🤖</span>
            Agents
        </button>
        <button class="nav-item" onclick="showTab('spawn')">
            <span>🚀</span>
            Spawn
        </button>
        <button class="nav-item" onclick="showTab('teams')">
            <span>👥</span>
            Teams
        </button>
        <button class="nav-item" onclick="showTab('billing')">
            <span>💰</span>
            Billing
        </button>
    </nav>
    
    <script>
        function showTab(tabId) {
            // Hide all panels
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.querySelectorAll('.sidebar-btn').forEach(b => b.classList.remove('active'));
            
            // Show selected panel
            document.getElementById(tabId).classList.add('active');
            
            // Update nav
            event.target.classList.add('active');
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    </script>
</body>
</html>'''

class AgencyServer(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        if self.path == '/':
            stats = get_stats()
            html = HTML.replace('{{TEMP}}', str(stats['temp'])).replace('{{MEM}}', str(stats['mem']))
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), AgencyServer) as httpd:
        print("J1MSKY Agency v5.0 - Responsive Dashboard")
        print("Mobile: http://your-phone:8080")
        print("Desktop: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
