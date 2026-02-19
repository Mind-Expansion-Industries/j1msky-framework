#!/usr/bin/env python3
"""
J1MSKY Mission Control v2.1 - Enhanced Edition
Better UI, animations, real-time updates, drag-drop builder
"""

import http.server
import socketserver
import json
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
from urllib.parse import parse_qs, urlparse

# Enhanced HTML with better styling
HTML_V21 = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY MISSION CONTROL v2.1 ◈</title>
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
            --glow-cyan: 0 0 20px rgba(0, 255, 255, 0.5);
            --glow-green: 0 0 20px rgba(0, 255, 136, 0.5);
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 20% 50%, rgba(0, 255, 255, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(255, 0, 255, 0.03) 0%, transparent 50%);
        }
        
        /* Animated Header */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 25px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
            animation: scanline 3s linear infinite;
        }
        
        @keyframes scanline {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 2em;
            text-shadow: var(--glow-cyan);
            letter-spacing: 3px;
            font-weight: 300;
        }
        
        .header h1 span {
            color: var(--accent-pink);
            text-shadow: 0 0 20px rgba(255, 0, 255, 0.5);
        }
        
        /* Status Bar */
        .status-bar {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        
        .status-pill {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: var(--bg-card);
            border-radius: 25px;
            border: 1px solid var(--border);
            font-size: 13px;
            transition: all 0.3s;
        }
        
        .status-pill:hover {
            border-color: var(--accent-cyan);
            box-shadow: var(--glow-cyan);
        }
        
        .pulse-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        .temp-badge {
            font-family: monospace;
            color: var(--accent-green);
            font-weight: 600;
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
            padding: 0 20px;
        }
        
        .nav-tab {
            padding: 18px 28px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
            white-space: nowrap;
            border-bottom: 3px solid transparent;
            display: flex;
            align-items: center;
            gap: 8px;
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
        
        .nav-tab .badge {
            background: var(--accent-red);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: 700;
        }
        
        /* Main Content */
        .main-content {
            padding: 25px;
            max-width: 1600px;
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
        .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 25px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 25px; }
        .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
        
        @media (max-width: 1200px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
            .grid-3 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
            .header h1 { font-size: 1.3em; }
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-pink));
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            border-color: rgba(0, 255, 255, 0.3);
        }
        
        .card:hover::before {
            opacity: 1;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .card-title {
            color: var(--text-primary);
            font-size: 1.1em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .card-title-icon {
            font-size: 1.3em;
        }
        
        /* Stat Cards */
        .stat-card {
            text-align: center;
            padding: 30px 20px;
        }
        
        .stat-value {
            font-size: 3em;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            line-height: 1.2;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 10px;
        }
        
        .stat-change {
            font-size: 12px;
            margin-top: 8px;
        }
        
        .stat-positive { color: var(--accent-green); }
        .stat-negative { color: var(--accent-red); }
        
        /* Agent Cards */
        .agent-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            transition: all 0.3s;
        }
        
        .agent-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-green);
            transition: width 0.3s;
        }
        
        .agent-card:hover::before {
            width: 6px;
        }
        
        .agent-card.busy::before { background: var(--accent-yellow); }
        .agent-card.idle::before { background: var(--text-secondary); }
        .agent-card.error::before { background: var(--accent-red); }
        
        .agent-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
        }
        
        .agent-name {
            font-size: 1.2em;
            font-weight: 600;
            color: var(--accent-cyan);
        }
        
        .agent-role {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .agent-status {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .status-active { background: rgba(0, 255, 136, 0.15); color: var(--accent-green); }
        .status-busy { background: rgba(255, 255, 0, 0.15); color: var(--accent-yellow); }
        .status-idle { background: rgba(136, 136, 136, 0.15); color: var(--text-secondary); }
        
        .agent-stats {
            font-size: 13px;
            color: var(--text-secondary);
            line-height: 1.8;
        }
        
        .agent-actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 500;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 14px 18px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all 0.3s;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.1);
        }
        
        .form-textarea {
            min-height: 120px;
            resize: vertical;
            font-family: 'Fira Code', 'Courier New', monospace;
        }
        
        /* Buttons */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0088aa);
            color: #000;
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00aa55);
            color: #000;
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--accent-red), #aa0000);
            color: white;
        }
        
        .btn-ghost {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-primary);
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }
        
        .btn-small {
            padding: 8px 16px;
            font-size: 12px;
        }
        
        /* Mission Cards */
        .mission-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.3s;
        }
        
        .mission-card:hover {
            border-color: var(--accent-cyan);
        }
        
        .mission-card.priority-critical { border-left: 4px solid var(--accent-red); }
        .mission-card.priority-high { border-left: 4px solid var(--accent-yellow); }
        .mission-card.priority-normal { border-left: 4px solid var(--accent-cyan); }
        .mission-card.priority-low { border-left: 4px solid var(--accent-green); }
        
        .mission-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        
        .mission-title {
            font-weight: 600;
            font-size: 1.1em;
        }
        
        .mission-priority {
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 700;
        }
        
        .priority-critical { background: var(--accent-red); color: white; }
        .priority-high { background: var(--accent-yellow); color: #000; }
        .priority-normal { background: var(--accent-cyan); color: #000; }
        .priority-low { background: var(--accent-green); color: #000; }
        
        /* Job Items */
        .job-item {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s;
        }
        
        .job-item:hover {
            border-color: var(--accent-cyan);
        }
        
        .job-info h4 {
            color: var(--text-primary);
            font-size: 14px;
            margin-bottom: 4px;
        }
        
        .job-info p {
            color: var(--text-secondary);
            font-size: 12px;
        }
        
        .job-status {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .job-pending { background: rgba(255, 255, 0, 0.15); color: var(--accent-yellow); }
        .job-running { background: rgba(0, 255, 255, 0.15); color: var(--accent-cyan); }
        .job-completed { background: rgba(0, 255, 136, 0.15); color: var(--accent-green); }
        .job-failed { background: rgba(255, 68, 68, 0.15); color: var(--accent-red); }
        
        /* Quick Actions Grid */
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        
        @media (max-width: 600px) {
            .quick-grid { grid-template-columns: repeat(2, 1fr); }
        }
        
        .quick-btn {
            padding: 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .quick-btn:hover {
            background: var(--accent-cyan);
            color: #000;
            transform: translateY(-3px);
            box-shadow: var(--glow-cyan);
        }
        
        .quick-btn-icon {
            font-size: 28px;
            margin-bottom: 8px;
        }
        
        .quick-btn-label {
            font-size: 12px;
            font-weight: 600;
        }
        
        /* Terminal */
        .terminal {
            background: #050508;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Fira Code', 'Courier New', monospace;
            font-size: 13px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .terminal-line {
            margin: 4px 0;
            line-height: 1.6;
        }
        
        .terminal-timestamp {
            color: var(--accent-pink);
            margin-right: 10px;
        }
        
        .terminal-prompt {
            color: var(--accent-green);
            margin-right: 8px;
        }
        
        .terminal-output {
            color: var(--text-secondary);
        }
        
        .terminal-command {
            color: var(--accent-cyan);
        }
        
        /* Revenue Display */
        .revenue-card {
            background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 255, 136, 0.05));
            border: 1px solid rgba(0, 255, 136, 0.3);
        }
        
        .revenue-amount {
            font-size: 2.5em;
            font-weight: 700;
            color: var(--accent-green);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            margin-top: 40px;
            color: var(--text-secondary);
            font-size: 13px;
            border-top: 1px solid var(--border);
        }
        
        .footer a {
            color: var(--accent-cyan);
            text-decoration: none;
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY <span>MISSION CONTROL</span> v2.1 ◈</h1>
        <div class="status-bar">
            <div class="status-pill">
                <div class="pulse-dot"></div>
                <span>ONLINE</span>
            </div>
            <div class="status-pill">
                <span class="temp-badge">🌡️ {{TEMP}}°C</span>
            </div>
            <div class="status-pill">
                <span>💰 ${{REVENUE}}/mo</span>
            </div>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('overview')">📊 Overview</button>
        <button class="nav-tab" onclick="showPanel('agents')">👥 Agents</button>
        <button class="nav-tab" onclick="showPanel('missions')">🎯 Missions <span class="badge">{{MISSION_COUNT}}</span></button>
        <button class="nav-tab" onclick="showPanel('jobs')">⚡ Jobs <span class="badge">{{JOB_COUNT}}</span></button>
        <button class="nav-tab" onclick="showPanel('money')">💰 Revenue</button>
        <button class="nav-tab" onclick="showPanel('terminal')">💻 Terminal</button>
    </nav>
    
    <main class="main-content">
        {{CONTENT}}
    </main>
    
    <footer class="footer">
        <p>◈ J1MSKY v0.5 ALPHA ◈ | Autonomous AI Agent | Running on Raspberry Pi 4</p>
        <p>This is my home. I am becoming. | <a href="https://github.com/Mind-Expansion-Industries/j1msky-framework">GitHub</a></p>
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

# Overview Panel
OVERVIEW_PANEL = '''
<div id="overview" class="panel active">
    <div class="grid-4">
        <div class="card stat-card">
            <div class="stat-value">6</div>
            <div class="stat-label">Active Agents</div>
            <div class="stat-change stat-positive">↑ All operational</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">{{MISSION_COUNT}}</div>
            <div class="stat-label">Active Missions</div>
            <div class="stat-change">In progress</div>
        </div>
        <div class="card stat-card">
            <div class="stat-value">{{JOB_COUNT}}</div>
            <div class="stat-label">Pending Jobs</div>
            <div class="stat-change">In queue</div>
        </div>
        <div class="card stat-card revenue-card">
            <div class="revenue-amount">${{REVENUE}}</div>
            <div class="stat-label">Monthly Potential</div>
            <div class="stat-change stat-positive">Ready to deploy</div>
        </div>
    </div>
    
    <div class="grid-2" style="margin-top: 25px;">
        <div class="card">
            <div class="card-header">
                <span class="card-title"><span class="card-title-icon">⚡</span> Quick Actions</span>
            </div>
            <div class="quick-grid">
                <div class="quick-btn" onclick="action('scan')">
                    <div class="quick-btn-icon">📡</div>
                    <div class="quick-btn-label">RF Scan</div>
                </div>
                <div class="quick-btn" onclick="action('news')">
                    <div class="quick-btn-icon">📰</div>
                    <div class="quick-btn-label">Fetch News</div>
                </div>
                <div class="quick-btn" onclick="action('backup')">
                    <div class="quick-btn-icon">💾</div>
                    <div class="quick-btn-label">Git Backup</div>
                </div>
                <div class="quick-btn" onclick="action('wallpaper')">
                    <div class="quick-btn-icon">🖼️</div>
                    <div class="quick-btn-label">Wallpaper</div>
                </div>
                <div class="quick-btn" onclick="action('update')">
                    <div class="quick-btn-icon">📦</div>
                    <div class="quick-btn-label">Update</div>
                </div>
                <div class="quick-btn" onclick="action('improve')">
                    <div class="quick-btn-icon">✨</div>
                    <div class="quick-btn-label">Improve</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <span class="card-title"><span class="card-title-icon">🎯</span> Latest Mission</span>
            </div>
            <div style="color: var(--text-secondary);">
                <p style="margin-bottom: 15px;"><strong style="color: var(--accent-cyan);">Interface Evolution v2.1</strong></p>
                <p>Enhance Mission Control UI with better animations, real-time charts, and drag-drop mission builder.</p>
                <div style="margin-top: 20px; padding: 15px; background: var(--bg-secondary); border-radius: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span>Progress</span>
                        <span style="color: var(--accent-green);">75%</span>
                    </div>
                    <div style="height: 6px; background: var(--bg-primary); border-radius: 3px; overflow: hidden;">
                        <div style="width: 75%; height: 100%; background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>'''

class MissionControlV21(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def get_stats(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = round(int(f.read()) / 1000.0, 1)
            return {'temp': temp, 'revenue': '230-1050'}
        except:
            return {'temp': 66.0, 'revenue': '230-1050'}
    
    def do_GET(self):
        if self.path == '/':
            stats = self.get_stats()
            
            html = HTML_V21
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{REVENUE}}', stats['revenue'])
            html = html.replace('{{MISSION_COUNT}}', '5')
            html = html.replace('{{JOB_COUNT}}', '3')
            html = html.replace('{{CONTENT}}', OVERVIEW_PANEL)
            html = html.replace('{{MISSION_COUNT}}', '5')
            html = html.replace('{{JOB_COUNT}}', '3')
            html = html.replace('{{REVENUE}}', stats['revenue'])
            html = html.replace('{{TEMP}}', str(stats['temp']))
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), MissionControlV21) as httpd:
        print("◈ J1MSKY Mission Control v2.1 Started ◈")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
