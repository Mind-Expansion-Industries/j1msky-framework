#!/usr/bin/env python3
"""
J1MSKY Mission Control v2.0 - Advanced Agent Dashboard
Multi-panel interface for assigning jobs, missions, and tasks
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
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Mission database
MISSIONS_DB = "/tmp/j1msky_missions.json"
JOBS_QUEUE = "/tmp/j1msky_jobs.json"

class MissionControl:
    def __init__(self):
        self.missions = []
        self.jobs = []
        self.agent_status = {}
        self.load_data()
        
    def load_data(self):
        """Load missions and jobs from disk"""
        try:
            if os.path.exists(MISSIONS_DB):
                with open(MISSIONS_DB, 'r') as f:
                    self.missions = json.load(f)
        except:
            self.missions = []
            
        try:
            if os.path.exists(JOBS_QUEUE):
                with open(JOBS_QUEUE, 'r') as f:
                    self.jobs = json.load(f)
        except:
            self.jobs = []
    
    def save_data(self):
        """Save missions and jobs to disk"""
        try:
            with open(MISSIONS_DB, 'w') as f:
                json.dump(self.missions, f)
            with open(JOBS_QUEUE, 'w') as f:
                json.dump(self.jobs, f)
        except:
            pass
    
    def create_mission(self, name, agent, objective, priority="normal"):
        """Create a new mission"""
        mission = {
            "id": len(self.missions) + 1,
            "name": name,
            "agent": agent,
            "objective": objective,
            "priority": priority,
            "status": "active",
            "created": datetime.now().isoformat(),
            "completed": None,
            "logs": []
        }
        self.missions.append(mission)
        self.save_data()
        return mission
    
    def create_job(self, name, command, schedule="now"):
        """Create a new job"""
        job = {
            "id": len(self.jobs) + 1,
            "name": name,
            "command": command,
            "schedule": schedule,
            "status": "pending",
            "created": datetime.now().isoformat(),
            "started": None,
            "completed": None,
            "output": ""
        }
        self.jobs.append(job)
        self.save_data()
        return job
    
    def execute_job(self, job_id):
        """Execute a job immediately"""
        for job in self.jobs:
            if job["id"] == job_id and job["status"] == "pending":
                job["status"] = "running"
                job["started"] = datetime.now().isoformat()
                self.save_data()
                
                try:
                    result = subprocess.run(
                        job["command"], 
                        shell=True, 
                        capture_output=True, 
                        text=True, 
                        timeout=300
                    )
                    job["output"] = result.stdout + result.stderr
                    job["status"] = "completed" if result.returncode == 0 else "failed"
                except subprocess.TimeoutExpired:
                    job["output"] = "Job timed out after 5 minutes"
                    job["status"] = "timeout"
                except Exception as e:
                    job["output"] = str(e)
                    job["status"] = "error"
                
                job["completed"] = datetime.now().isoformat()
                self.save_data()
                return job
        return None

mission_control = MissionControl()

HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY MISSION CONTROL v2.0 ◈</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-tertiary: #1a1a25;
            --accent-cyan: #00ffff;
            --accent-green: #00ff88;
            --accent-pink: #ff00ff;
            --accent-yellow: #ffff00;
            --accent-red: #ff4444;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --border: #333333;
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', 'Courier New', monospace;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        /* Header */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            padding: 20px;
            border-bottom: 2px solid var(--accent-cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.8em;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
            letter-spacing: 2px;
        }
        
        .status-bar {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 15px;
            background: var(--bg-tertiary);
            border-radius: 20px;
            border: 1px solid var(--border);
        }
        
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .temp-display {
            font-family: monospace;
            color: var(--accent-green);
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
        }
        
        .nav-tab {
            padding: 15px 25px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s;
            white-space: nowrap;
            border-bottom: 3px solid transparent;
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: var(--bg-tertiary);
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            border-bottom-color: var(--accent-cyan);
            background: var(--bg-tertiary);
        }
        
        .nav-tab .badge {
            background: var(--accent-red);
            color: white;
            padding: 2px 6px;
            border-radius: 10px;
            font-size: 10px;
            margin-left: 5px;
        }
        
        /* Main Content */
        .main-content {
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
        }
        
        .panel.active {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Grid Layout */
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
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .card:hover {
            transform: translateY(-2px);
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
            color: var(--accent-pink);
            font-size: 1.1em;
            font-weight: 600;
        }
        
        .card-actions {
            display: flex;
            gap: 8px;
        }
        
        /* Forms */
        .form-group {
            margin-bottom: 15px;
        }
        
        .form-label {
            display: block;
            margin-bottom: 5px;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .form-input, .form-select, .form-textarea {
            width: 100%;
            padding: 12px 15px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 14px;
            transition: border-color 0.3s;
        }
        
        .form-input:focus, .form-select:focus, .form-textarea:focus {
            outline: none;
            border-color: var(--accent-cyan);
        }
        
        .form-textarea {
            min-height: 100px;
            resize: vertical;
            font-family: monospace;
        }
        
        /* Buttons */
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
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
        
        .btn-warning {
            background: linear-gradient(135deg, var(--accent-yellow), #aaaa00);
            color: #000;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 255, 255, 0.3);
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 12px;
        }
        
        /* Agent Cards */
        .agent-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            position: relative;
            overflow: hidden;
        }
        
        .agent-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-green);
        }
        
        .agent-card.busy::before { background: var(--accent-yellow); }
        .agent-card.idle::before { background: var(--text-secondary); }
        .agent-card.error::before { background: var(--accent-red); }
        
        .agent-name {
            font-weight: 600;
            color: var(--accent-cyan);
            font-size: 1.1em;
        }
        
        .agent-status {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            margin-top: 8px;
        }
        
        .status-active { background: rgba(0, 255, 136, 0.2); color: var(--accent-green); }
        .status-busy { background: rgba(255, 255, 0, 0.2); color: var(--accent-yellow); }
        .status-idle { background: rgba(136, 136, 136, 0.2); color: var(--text-secondary); }
        
        .agent-stats {
            margin-top: 10px;
            font-size: 12px;
            color: var(--text-secondary);
        }
        
        /* Mission Cards */
        .mission-card {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid var(--accent-cyan);
        }
        
        .mission-card.priority-high { border-left-color: var(--accent-red); }
        .mission-card.priority-medium { border-left-color: var(--accent-yellow); }
        .mission-card.priority-low { border-left-color: var(--accent-green); }
        
        .mission-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 10px;
        }
        
        .mission-title {
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .mission-priority {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 10px;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .priority-high { background: var(--accent-red); color: white; }
        .priority-medium { background: var(--accent-yellow); color: black; }
        .priority-low { background: var(--accent-green); color: black; }
        
        .mission-meta {
            font-size: 12px;
            color: var(--text-secondary);
            margin-top: 8px;
        }
        
        /* Job Queue */
        .job-item {
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .job-info h4 {
            color: var(--text-primary);
            font-size: 14px;
        }
        
        .job-info p {
            color: var(--text-secondary);
            font-size: 11px;
            margin-top: 4px;
        }
        
        .job-status {
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
        }
        
        .job-pending { background: rgba(255, 255, 0, 0.2); color: var(--accent-yellow); }
        .job-running { background: rgba(0, 255, 255, 0.2); color: var(--accent-cyan); }
        .job-completed { background: rgba(0, 255, 136, 0.2); color: var(--accent-green); }
        .job-failed { background: rgba(255, 68, 68, 0.2); color: var(--accent-red); }
        
        /* Stats */
        .stat-box {
            text-align: center;
            padding: 20px;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            color: var(--accent-cyan);
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            margin-top: 5px;
        }
        
        /* Terminal Output */
        .terminal {
            background: #000;
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .terminal-line {
            margin: 3px 0;
        }
        
        .terminal-timestamp {
            color: var(--accent-pink);
        }
        
        .terminal-command {
            color: var(--accent-cyan);
        }
        
        .terminal-output {
            color: var(--text-secondary);
        }
        
        /* Quick Actions */
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 10px;
        }
        
        .quick-btn {
            padding: 15px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            cursor: pointer;
            text-align: center;
            transition: all 0.3s;
        }
        
        .quick-btn:hover {
            background: var(--accent-cyan);
            color: #000;
        }
        
        .quick-btn-icon {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header { flex-direction: column; text-align: center; }
            .header h1 { font-size: 1.4em; }
            .nav-tab { padding: 12px 15px; font-size: 12px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY MISSION CONTROL v2.0 ◈</h1>
        <div class="status-bar">
            <div class="status-indicator">
                <div class="status-dot"></div>
                <span>SYSTEM ONLINE</span>
            </div>
            <div class="temp-display">
                🌡️ {{TEMP}}°C
            </div>
        </div>
    </header>
    
    <nav class="nav-tabs">
        <button class="nav-tab active" onclick="showPanel('overview')">📊 Overview</button>
        <button class="nav-tab" onclick="showPanel('agents')">👥 Agents</button>
        <button class="nav-tab" onclick="showPanel('missions')">🎯 Missions <span class="badge" id="mission-count">{{MISSION_COUNT}}</span></button>
        <button class="nav-tab" onclick="showPanel('jobs')">⚡ Jobs <span class="badge" id="job-count">{{JOB_COUNT}}</span></button>
        <button class="nav-tab" onclick="showPanel('terminal')">💻 Terminal</button>
        <button class="nav-tab" onclick="showPanel('system')">🔧 System</button>
    </nav>
    
    <main class="main-content">
        <!-- OVERVIEW PANEL -->
        <div id="overview" class="panel active">
            <div class="grid-4">
                <div class="card stat-box">
                    <div class="stat-value">6</div>
                    <div class="stat-label">Active Agents</div>
                </div>
                <div class="card stat-box">
                    <div class="stat-value">{{MISSION_COUNT}}</div>
                    <div class="stat-label">Active Missions</div>
                </div>
                <div class="card stat-box">
                    <div class="stat-value">{{JOB_COUNT}}</div>
                    <div class="stat-label">Pending Jobs</div>
                </div>
                <div class="card stat-box">
                    <div class="stat-value" style="color: var(--accent-green);">{{UPTIME}}</div>
                    <div class="stat-label">Uptime</div>
                </div>
            </div>
            
            <div class="grid-2" style="margin-top: 20px;">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">⚡ Quick Actions</span>
                    </div>
                    <div class="quick-actions">
                        <button class="quick-btn" onclick="quickAction('scan')">
                            <div class="quick-btn-icon">📡</div>
                            <div>RF Scan</div>
                        </button>
                        <button class="quick-btn" onclick="quickAction('news')">
                            <div class="quick-btn-icon">📰</div>
                            <div>Fetch News</div>
                        </button>
                        <button class="quick-btn" onclick="quickAction('backup')">
                            <div class="quick-btn-icon">💾</div>
                            <div>Git Backup</div>
                        </button>
                        <button class="quick-btn" onclick="quickAction('wallpaper')">
                            <div class="quick-btn-icon">🖼️</div>
                            <div>New Wallpaper</div>
                        </button>
                        <button class="quick-btn" onclick="quickAction('update')">
                            <div class="quick-btn-icon">🔄</div>
                            <div>Update System</div>
                        </button>
                        <button class="quick-btn" onclick="quickAction('restart')">
                            <div class="quick-btn-icon">🔄</div>
                            <div>Restart Agents</div>
                        </button>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🎯 Recent Missions</span>
                        <button class="btn btn-primary btn-small" onclick="showPanel('missions')">+ New</button>
                    </div>
                    {{RECENT_MISSIONS}}
                </div>
            </div>
        </div>
        
        <!-- AGENTS PANEL -->
        <div id="agents" class="panel">
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <span class="card-title">🚀 Deploy Agent Mission</span>
                </div>
                <form id="mission-form" onsubmit="createMission(event)">
                    <div class="grid-2">
                        <div class="form-group">
                            <label class="form-label">Agent</label>
                            <select class="form-select" id="agent-select" required>
                                <option value="">Select Agent...</option>
                                <option value="scout">🔍 SCOUT - News Gathering</option>
                                <option value="vitals">🌡️ VITALS - System Monitor</option>
                                <option value="archivist">📋 ARCHIVIST - File Tracking</option>
                                <option value="flipper">🔌 FLIPPER - RF/IR/NFC</option>
                                <option value="stream">📺 STREAM - Twitch/Telemetry</option>
                                <option value="voice">🔊 VOICE - Audio Control</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Priority</label>
                            <select class="form-select" id="priority-select">
                                <option value="low">🟢 Low</option>
                                <option value="normal" selected>🟡 Normal</option>
                                <option value="high">🔴 High</option>
                                <option value="critical">💀 Critical</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Mission Objective</label>
                        <input type="text" class="form-input" id="mission-name" placeholder="e.g., Scan garage door frequencies in area" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Details / Parameters</label>
                        <textarea class="form-textarea" id="mission-details" placeholder="Frequency range: 300-400MHz&#10;Duration: 5 minutes&#10;Save results to: /tmp/scan_results.json"></textarea>
                    </div>
                    <button type="submit" class="btn btn-success">🚀 DEPLOY MISSION</button>
                </form>
            </div>
            
            <div class="grid-3">
                <div class="agent-card active">
                    <div class="agent-name">🔍 SCOUT</div>
                    <div class="agent-status status-active">● ACTIVE</div>
                    <div class="agent-stats">
                        Last run: 2 min ago<br>
                        Tasks: 47 completed<br>
                        Source: Hacker News
                    </div>
                </div>
                <div class="agent-card active">
                    <div class="agent-name">🌡️ VITALS</div>
                    <div class="agent-status status-active">● ACTIVE</div>
                    <div class="agent-stats">
                        CPU: {{TEMP}}°C<br>
                        Load: {{LOAD}}%<br>
                        Uptime: {{UPTIME}}
                    </div>
                </div>
                <div class="agent-card idle">
                    <div class="agent-name">📋 ARCHIVIST</div>
                    <div class="agent-status status-idle">○ IDLE</div>
                    <div class="agent-stats">
                        Files indexed: 1,247<br>
                        Last scan: 1 hour ago<br>
                        Changes: None
                    </div>
                </div>
                <div class="agent-card active">
                    <div class="agent-name">🔌 FLIPPER</div>
                    <div class="agent-status status-active">● USB CONNECTED</div>
                    <div class="agent-stats">
                        Device: Flipper Zero<br>
                        Mode: Bridge<br>
                        Capabilities: RF/NFC/IR
                    </div>
                </div>
                <div class="agent-card idle">
                    <div class="agent-name">📺 STREAM</div>
                    <div class="agent-status status-idle">○ IDLE</div>
                    <div class="agent-stats">
                        Platform: Twitch<br>
                        Status: Offline<br>
                        Ready to start
                    </div>
                </div>
                <div class="agent-card active">
                    <div class="agent-name">🔊 VOICE</div>
                    <div class="agent-status status-active">● ECHO CONNECTED</div>
                    <div class="agent-stats">
                        Output: Echo/Alexa<br>
                        Input: Bluetooth<br>
                        Status: Ready
                    </div>
                </div>
            </div>
        </div>
        
        <!-- MISSIONS PANEL -->
        <div id="missions" class="panel">
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <span class="card-title">🎯 Create New Mission</span>
                </div>
                <form onsubmit="createFullMission(event)">
                    <div class="grid-2">
                        <div class="form-group">
                            <label class="form-label">Mission Name</label>
                            <input type="text" class="form-input" name="name" placeholder="RF Site Survey" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Assigned Agent</label>
                            <select class="form-select" name="agent" required>
                                <option value="scout">🔍 SCOUT</option>
                                <option value="vitals">🌡️ VITALS</option>
                                <option value="archivist">📋 ARCHIVIST</option>
                                <option value="flipper">🔌 FLIPPER</option>
                                <option value="stream">📺 STREAM</option>
                                <option value="voice">🔊 VOICE</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Objective</label>
                        <input type="text" class="form-input" name="objective" placeholder="What should the agent accomplish?" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Priority</label>
                        <select class="form-select" name="priority">
                            <option value="low">🟢 Low - Background task</option>
                            <option value="normal" selected>🟡 Normal - Standard priority</option>
                            <option value="high">🔴 High - Urgent</option>
                            <option value="critical">💀 Critical - Immediate</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-success">🚀 LAUNCH MISSION</button>
                </form>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📋 Mission History</span>
                </div>
                <div id="mission-list">
                    {{MISSIONS_LIST}}
                </div>
            </div>
        </div>
        
        <!-- JOBS PANEL -->
        <div id="jobs" class="panel">
            <div class="card" style="margin-bottom: 20px;">
                <div class="card-header">
                    <span class="card-title">⚡ Create New Job</span>
                </div>
                <form onsubmit="createJob(event)">
                    <div class="form-group">
                        <label class="form-label">Job Name</label>
                        <input type="text" class="form-input" name="name" placeholder="e.g., Backup to GitHub" required>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Command</label>
                        <textarea class="form-textarea" name="command" placeholder="cd ~/Desktop/J1MSKY && git add -A && git commit -m 'Backup' && git push" required></textarea>
                    </div>
                    <div class="grid-2">
                        <div class="form-group">
                            <label class="form-label">Schedule</label>
                            <select class="form-select" name="schedule">
                                <option value="now">⚡ Run Now</option>
                                <option value="cron">🕐 Cron Schedule</option>
                                <option value="once">📅 Once</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">&nbsp;</label>
                            <button type="submit" class="btn btn-success" style="width: 100%">⚡ QUEUE JOB</button>
                        </div>
                    </div>
                </form>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📋 Job Queue</span>
                    <button class="btn btn-primary btn-small" onclick="runAllJobs()">▶ Run All Pending</button>
                </div>
                <div id="job-list">
                    {{JOBS_LIST}}
                </div>
            </div>
        </div>
        
        <!-- TERMINAL PANEL -->
        <div id="terminal" class="panel">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">💻 Command Terminal</span>
                    </div>
                    <form onsubmit="runTerminalCommand(event)">
                        <div class="form-group">
                            <label class="form-label">Command</label>
                            <input type="text" class="form-input" id="terminal-input" placeholder="Enter command..." autocomplete="off">
                        </div>
                        <button type="submit" class="btn btn-primary">▶ Execute</button>
                    </form>
                    <div class="terminal" id="terminal-output" style="margin-top: 15px; min-height: 200px;">
                        <div class="terminal-line">
                            <span class="terminal-timestamp">[{{TIME}}]</span>
                            <span class="terminal-command">$</span>
                            <span class="terminal-output">J1MSKY Terminal Ready. Type commands above.</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">📝 Quick Commands</span>
                    </div>
                    <div class="quick-actions">
                        <button class="quick-btn" onclick="sendCommand('htop')">htop</button>
                        <button class="quick-btn" onclick="sendCommand('df -h')">Disk Usage</button>
                        <button class="quick-btn" onclick="sendCommand('free -h')">Memory</button>
                        <button class="quick-btn" onclick="sendCommand('git status')">Git Status</button>
                        <button class="quick-btn" onclick="sendCommand('lsusb')">USB Devices</button>
                        <button class="quick-btn" onclick="sendCommand('bluetoothctl devices')">Bluetooth</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- SYSTEM PANEL -->
        <div id="system" class="panel">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🌡️ System Vitals</span>
                    </div>
                    <div style="padding: 10px;">
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">CPU Temperature</span>
                            <span style="color: var(--accent-cyan); font-weight: 600;">{{TEMP}}°C</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">CPU Load</span>
                            <span style="color: var(--accent-cyan); font-weight: 600;">{{LOAD}}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">Memory Usage</span>
                            <span style="color: var(--accent-cyan); font-weight: 600;">{{MEM}}%</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">Disk Free</span>
                            <span style="color: var(--accent-green); font-weight: 600;">{{DISK_FREE}}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0;">
                            <span style="color: var(--text-secondary);">Uptime</span>
                            <span style="color: var(--accent-cyan); font-weight: 600;">{{UPTIME}}</span>
                        </div>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">🔊 Audio Status</span>
                    </div>
                    <div style="padding: 10px;">
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">Output</span>
                            <span style="color: var(--accent-green); font-weight: 600;">{{AUDIO_OUT}}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid var(--border);">
                            <span style="color: var(--text-secondary);">Input</span>
                            <span style="color: var(--accent-green); font-weight: 600;">{{AUDIO_IN}}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; padding: 10px 0;">
                            <span style="color: var(--text-secondary);">Bluetooth</span>
                            <span style="color: var(--accent-green); font-weight: 600;">{{BT_STATUS}}</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-top: 20px;">
                <div class="card-header">
                    <span class="card-title">🔄 System Actions</span>
                </div>
                <div class="quick-actions">
                    <button class="quick-btn" onclick="systemAction('restart-agents')">🔄 Restart Agents</button>
                    <button class="quick-btn" onclick="systemAction('clear-logs')">🗑️ Clear Logs</button>
                    <button class="quick-btn" onclick="systemAction('update-system')">📦 Update System</button>
                    <button class="quick-btn" onclick="systemAction('reboot')">🔌 Reboot Pi</button>
                </div>
            </div>
        </div>
    </main>
    
    <script>
        // Tab switching
        function showPanel(panelId) {
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.getElementById(panelId).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Quick actions
        function quickAction(action) {
            fetch('/api/action/' + action, { method: 'POST' })
                .then(r => r.json())
                .then(data => alert(data.message))
                .catch(e => console.error(e));
        }
        
        // Mission creation
        function createMission(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            fetch('/api/mission', {
                method: 'POST',
                body: new URLSearchParams(formData)
            }).then(() => {
                alert('🚀 Mission deployed!');
                location.reload();
            });
        }
        
        function createFullMission(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            fetch('/api/mission', {
                method: 'POST',
                body: new URLSearchParams(formData)
            }).then(() => {
                alert('🚀 Mission launched!');
                location.reload();
            });
        }
        
        // Job creation
        function createJob(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            fetch('/api/job', {
                method: 'POST',
                body: new URLSearchParams(formData)
            }).then(() => {
                alert('⚡ Job queued!');
                location.reload();
            });
        }
        
        function runAllJobs() {
            fetch('/api/jobs/run-all', { method: 'POST' })
                .then(() => alert('▶ All pending jobs started!'));
        }
        
        // Terminal
        function runTerminalCommand(e) {
            e.preventDefault();
            const cmd = document.getElementById('terminal-input').value;
            sendCommand(cmd);
            document.getElementById('terminal-input').value = '';
        }
        
        function sendCommand(cmd) {
            fetch('/api/terminal', {
                method: 'POST',
                body: 'command=' + encodeURIComponent(cmd),
                headers: {'Content-Type': 'application/x-www-form-urlencoded'}
            })
            .then(r => r.json())
            .then(data => {
                const output = document.getElementById('terminal-output');
                const line = document.createElement('div');
                line.className = 'terminal-line';
                line.innerHTML = '<span class="terminal-timestamp">[' + data.time + ']</span> <span class="terminal-command">$</span> <span class="terminal-output">' + data.output.substring(0, 500) + '</span>';
                output.appendChild(line);
                output.scrollTop = output.scrollHeight;
            });
        }
        
        // System actions
        function systemAction(action) {
            if (confirm('Are you sure?')) {
                fetch('/api/system/' + action, { method: 'POST' })
                    .then(r => r.json())
                    .then(data => alert(data.message));
            }
        }
        
        // Auto-refresh every 10 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('mission-count').textContent = data.missions;
                    document.getElementById('job-count').textContent = data.jobs;
                });
        }, 10000);
    </script>
</body>
</html>'''

class MissionHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Suppress logs
    
    def get_system_stats(self):
        """Get current system stats"""
        stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--', 'disk_free': '0G'}
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                stats['temp'] = round(int(f.read()) / 1000.0, 1)
            with open('/proc/loadavg', 'r') as f:
                stats['load'] = round(float(f.read().split()[0]) * 25, 1)
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
            # Disk free
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                stats['disk_free'] = lines[1].split()[3]
        except:
            pass
        return stats
    
    def get_audio_status(self):
        try:
            result = subprocess.run(['pactl', 'info'], capture_output=True, text=True)
            sinks = [l for l in result.stdout.split('\n') if 'Default Sink' in l]
            sources = [l for l in result.stdout.split('\n') if 'Default Source' in l]
            out = sinks[0].split(':')[-1].strip()[:20] if sinks else 'Unknown'
            in_src = sources[0].split(':')[-1].strip()[:20] if sources else 'Unknown'
            
            bt_result = subprocess.run(['bluetoothctl', 'info'], capture_output=True, text=True)
            bt_status = 'Connected' if 'yes' in bt_result.stdout.lower() else 'Disconnected'
            return out, in_src, bt_status
        except:
            return 'Unknown', 'Unknown', 'Unknown'
    
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        
        if path == '/':
            stats = self.get_system_stats()
            out, in_src, bt = self.get_audio_status()
            
            # Generate missions list HTML
            missions_html = ""
            for m in reversed(mission_control.missions[-5:]):
                priority_class = f"priority-{m.get('priority', 'normal')}"
                status = m.get('status', 'unknown')
                missions_html += f'''
                <div class="mission-card {priority_class}">
                    <div class="mission-header">
                        <span class="mission-title">{m.get('name', 'Unnamed')}</span>
                        <span class="mission-priority priority-{m.get('priority', 'normal')}">{m.get('priority', 'normal').upper()}</span>
                    </div>
                    <div style="color: var(--text-secondary); font-size: 13px;">{m.get('objective', 'No objective')}</div>
                    <div class="mission-meta">Agent: {m.get('agent', 'Unknown').upper()} | Status: {status.upper()}</div>
                </div>'''
            
            if not missions_html:
                missions_html = '<div style="color: var(--text-secondary); text-align: center; padding: 20px;">No missions yet. Create one above!</div>'
            
            # Generate jobs list HTML
            jobs_html = ""
            for j in reversed(mission_control.jobs[-10:]):
                status_class = f"job-{j.get('status', 'pending')}"
                jobs_html += f'''
                <div class="job-item">
                    <div class="job-info">
                        <h4>{j.get('name', 'Unnamed')}</h4>
                        <p>{j.get('command', 'No command')[:50]}...</p>
                    </div>
                    <span class="job-status {status_class}">{j.get('status', 'PENDING').upper()}</span>
                </div>'''
            
            if not jobs_html:
                jobs_html = '<div style="color: var(--text-secondary); text-align: center; padding: 20px;">No jobs in queue</div>'
            
            html = HTML_TEMPLATE
            html = html.replace('{{TEMP}}', str(stats['temp']))
            html = html.replace('{{LOAD}}', str(stats['load']))
            html = html.replace('{{MEM}}', str(stats['mem']))
            html = html.replace('{{UPTIME}}', stats['uptime'])
            html = html.replace('{{DISK_FREE}}', stats['disk_free'])
            html = html.replace('{{TIME}}', datetime.now().strftime('%H:%M:%S'))
            html = html.replace('{{AUDIO_OUT}}', out)
            html = html.replace('{{AUDIO_IN}}', in_src)
            html = html.replace('{{BT_STATUS}}', bt)
            html = html.replace('{{MISSION_COUNT}}', str(len([m for m in mission_control.missions if m.get('status') == 'active'])))
            html = html.replace('{{JOB_COUNT}}', str(len([j for j in mission_control.jobs if j.get('status') == 'pending'])))
            html = html.replace('{{MISSIONS_LIST}}', missions_html)
            html = html.replace('{{JOBS_LIST}}', jobs_html)
            html = html.replace('{{RECENT_MISSIONS}}', missions_html[:500] if missions_html else '<p style="color: var(--text-secondary);">No recent missions</p>')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        elif path == '/api/status':
            active_missions = len([m for m in mission_control.missions if m.get('status') == 'active'])
            pending_jobs = len([j for j in mission_control.jobs if j.get('status') == 'pending'])
            self.send_json({'missions': active_missions, 'jobs': pending_jobs})
            
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode()
        params = parse_qs(body)
        
        if path == '/api/mission':
            name = params.get('name', ['Unnamed'])[0]
            agent = params.get('agent', ['scout'])[0]
            objective = params.get('objective', ['No objective'])[0]
            priority = params.get('priority', ['normal'])[0]
            
            mission = mission_control.create_mission(name, agent, objective, priority)
            self.send_json({'success': True, 'mission': mission})
            
        elif path == '/api/job':
            name = params.get('name', ['Unnamed'])[0]
            command = params.get('command', [''])[0]
            schedule = params.get('schedule', ['now'])[0]
            
            job = mission_control.create_job(name, command, schedule)
            
            if schedule == 'now':
                threading.Thread(target=mission_control.execute_job, args=(job['id'],), daemon=True).start()
            
            self.send_json({'success': True, 'job': job})
            
        elif path == '/api/jobs/run-all':
            for job in mission_control.jobs:
                if job.get('status') == 'pending':
                    threading.Thread(target=mission_control.execute_job, args=(job['id'],), daemon=True).start()
            self.send_json({'success': True, 'message': 'All jobs started'})
            
        elif path == '/api/terminal':
            command = params.get('command', [''])[0]
            try:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd='/home/m1ndb0t/Desktop/J1MSKY')
                output = result.stdout + result.stderr
                if not output:
                    output = "Command executed successfully (no output)"
            except subprocess.TimeoutExpired:
                output = "Command timed out after 30 seconds"
            except Exception as e:
                output = str(e)
            
            self.send_json({'time': datetime.now().strftime('%H:%M:%S'), 'output': output[:2000]})
            
        elif path.startswith('/api/action/'):
            action = path.split('/')[-1]
            self.send_json({'success': True, 'message': f'Action {action} triggered'})
            
        elif path.startswith('/api/system/'):
            action = path.split('/')[-1]
            self.send_json({'success': True, 'message': f'System action {action} initiated'})
            
        else:
            self.send_error(404)
    
    def send_json(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run_server(port=8080):
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), MissionHandler) as httpd:
        print(f"◈ J1MSKY Mission Control v2.0 Started ◈")
        print(f"Access: http://localhost:{port}")
        print(f"       http://{os.uname().nodename}:{port}")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
