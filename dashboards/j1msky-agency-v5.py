#!/usr/bin/env python3
"""
J1MSKY Agency v6.0.27 - Resize Flicker Reduction
Patch release: extends live log escaping to include quotes for stricter HTML safety and rendering stability
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="theme-color" content="#0a0a0f">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title>J1MSKY Agency v6.0.27</title>
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
            --nav-height: 70px;
            --header-height: 56px;
            --safe-bottom: env(safe-area-inset-bottom, 0px);
        }
        
        * { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box; 
            -webkit-tap-highlight-color: transparent;
            -webkit-touch-callout: none;
            user-select: none;
        }
        
        /* Prevent body scroll when navigating */
        body.navigating { overflow: hidden; }
        
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            min-height: 100dvh;
            min-height: -webkit-fill-available; /* iOS Safari fix */
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            contain: layout style paint;
        }
        
        /* Fix for mobile viewport height with dynamic toolbars */
        @supports (height: 100dvh) {
            body {
                min-height: 100dvh;
            }
        }
        
        /* iOS momentum scrolling */
        .main {
            -webkit-overflow-scrolling: touch;
        }
        
        .header {
            background: var(--bg-2);
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: var(--header-height);
            z-index: 100;
            /* GPU acceleration */
            transform: translateZ(0);
            will-change: transform;
        }
        
        .header h1 {
            font-size: 18px;
            background: linear-gradient(90deg, var(--cyan), var(--green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }
        
        .header-stats {
            display: flex;
            gap: 8px;
            align-items: center;
        }
        
        .help-btn {
            background: var(--bg-3);
            border: 1px solid var(--border);
            border-radius: 50%;
            width: 32px;
            height: 32px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            font-size: 14px;
            color: var(--text-2);
            transition: all 0.2s;
        }
        
        .help-btn:hover {
            background: var(--cyan);
            color: var(--bg);
            border-color: var(--cyan);
        }
        
        .stat-badge {
            background: var(--bg-3);
            padding: 6px 10px;
            border-radius: 20px;
            font-size: 11px;
            border: 1px solid var(--border);
            transition: opacity 0.3s ease;
        }
        
        .stat-badge.temp { color: var(--green); border-color: var(--green); }
        .stat-badge.mem { color: var(--cyan); border-color: var(--cyan); }
        
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            height: var(--nav-height);
            background: var(--bg-2);
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-around;
            align-items: center;
            z-index: 100;
            /* iOS safe area + fixed height for consistency */
            padding-bottom: var(--safe-bottom);
            /* GPU acceleration for smooth transitions */
            transform: translateZ(0);
            will-change: transform;
            /* Prevent rubber-banding issues */
            overscroll-behavior: none;
        }
        
        .nav-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 8px 16px;
            background: none;
            border: none;
            color: var(--text-2);
            font-size: 11px;
            cursor: pointer;
            transition: color 0.15s ease-out;
            min-width: 64px;
            min-height: 48px; /* WCAG minimum touch target */
            /* Better touch response */
            touch-action: manipulation;
            -webkit-touch-callout: none;
        }
        
        .nav-item:active {
            transform: scale(0.95);
            transition: transform 0.1s;
        }
        
        .nav-item.active {
            color: var(--cyan);
        }
        
        .nav-item span {
            font-size: 22px;
            line-height: 1;
            transition: transform 0.2s ease-out;
        }
        
        .nav-item.active span {
            transform: translateY(-2px);
        }
        
        .main {
            padding: 16px;
            /* Account for fixed header + nav + safe areas */
            padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 16px);
            padding-top: calc(var(--header-height) + 16px);
            max-width: 1400px;
            width: 100%;
            margin: 0 auto;
            /* Smooth scrolling */
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
            overscroll-behavior-y: contain;
            touch-action: pan-y;
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
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .stat-card:hover {
            border-color: var(--cyan);
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 255, 255, 0.1);
        }
        
        .stat-card:active {
            transform: translateY(0);
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
            /* Containment for better render performance */
            contain: layout style paint;
            min-width: 0;
        }
        
        .panel.active {
            display: block;
            animation: fadeIn 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        /* Reduced motion preference */
        @media (prefers-reduced-motion: reduce) {
            .panel.active {
                animation: none;
            }
            .nav-item span {
                transition: none;
            }
            .stat-card:hover {
                transform: none;
                box-shadow: none;
            }
            body.navigating::after {
                animation: none;
            }
        }
        
        /* Loading state */
        body.navigating .main {
            opacity: 0.7;
            pointer-events: none;
        }
        
        body.navigating::after {
            content: '';
            position: fixed;
            top: 50%;
            left: 50%;
            width: 40px;
            height: 40px;
            margin: -20px 0 0 -20px;
            border: 3px solid var(--bg-3);
            border-top-color: var(--cyan);
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            z-index: 1000;
            pointer-events: none;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Offline state */
        body.offline .header h1 {
            color: var(--red);
        }
        
        /* Help panel specific styles */
        #help {
            animation: fadeIn 0.3s ease-out;
        }
        
        #help .agent-item {
            cursor: default;
        }
        
        #help .agent-item:hover {
            border-left-color: var(--cyan);
        }
        
        /* Ripple effect for buttons */
        .nav-item, .quick-btn, .btn-primary {
            position: relative;
            overflow: hidden;
        }
        
        .nav-item::after, .quick-btn::after, .btn-primary::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            background: rgba(0, 255, 255, 0.2);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
        }
        
        .nav-item:active::after, .quick-btn:active::after, .btn-primary:active::after {
            width: 200%;
            height: 200%;
        }

        .nav-item:focus-visible,
        .quick-btn:focus-visible,
        .btn-primary:focus-visible,
        .help-btn:focus-visible,
        .agent-action:focus-visible,
        .form-input:focus-visible,
        .form-select:focus-visible,
        .form-textarea:focus-visible {
            outline: 2px solid var(--cyan);
            outline-offset: 2px;
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
        
        /* Small phones */
        @media (max-width: 360px) {
            .main {
                padding-left: 12px;
                padding-right: 12px;
            }
            .quick-grid,
            .stats-grid {
                gap: 8px;
            }
            .nav-item {
                min-width: 56px;
                padding: 8px 10px;
            }
            .header h1 {
                font-size: 16px;
            }
        }

        /* Tablet */
        @media (min-width: 768px) {
            :root {
                --nav-height: 64px;
                --header-height: 60px;
            }
            .header { padding: 16px 24px; }
            .header h1 { font-size: 20px; }
            .main { padding: 24px; padding-bottom: calc(var(--nav-height) + var(--safe-bottom) + 24px); padding-top: calc(var(--header-height) + 24px); }
            .quick-grid { grid-template-columns: repeat(3, 1fr); }
            .stats-grid { grid-template-columns: repeat(4, 1fr); }
            .nav-item { font-size: 12px; }
            .nav-item span { font-size: 24px; }
        }
        
        /* Desktop */
        @media (min-width: 1024px) {
            :root {
                --nav-height: 0px; /* Side nav on desktop */
            }
            .header { padding: 16px 32px; }
            .header h1 { font-size: 24px; }
            .main { 
                padding: 32px; 
                padding-bottom: 32px;
                padding-top: calc(var(--header-height) + 32px);
                max-width: 1400px;
            }
            .quick-grid { grid-template-columns: repeat(4, 1fr); }
            .bottom-nav {
                position: fixed;
                left: 0;
                top: var(--header-height);
                bottom: 0;
                width: 240px;
                height: auto;
                flex-direction: column;
                justify-content: flex-start;
                padding: 16px 0;
                border-top: none;
                border-right: 1px solid var(--border);
            }
            .nav-item {
                flex-direction: row;
                justify-content: flex-start;
                gap: 12px;
                padding: 16px 24px;
                width: 100%;
                font-size: 14px;
            }
            .nav-item span { font-size: 20px; }
            body { padding-left: 240px; }
        }
        
        /* Large desktop */
        @media (min-width: 1440px) {
            .main { max-width: 1600px; }
            .bottom-nav { width: 260px; }
            body { padding-left: 260px; }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY Agency v6.0.27</h1>
        <div class="header-stats">
            <div class="stat-badge temp">{{TEMP}}°C</div>
            <div class="stat-badge mem">{{MEM}}%</div>
            <button class="help-btn" onclick="toggleHelp()" title="Help (? or h)" aria-label="Help" aria-expanded="false">?</button>
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
                        <div class="model-cost">$99/mo</div>
                    </div>
                    <div class="model-desc">Kimi + MiniMax • Programming • Development</div>
                    <button class="btn-primary" style="margin-top: 12px;">Deploy Team</button>
                </div>
                
                <div class="model-card">
                    <div class="model-header">
                        <div class="model-name">🎨 Creative Team</div>
                        <div class="model-cost">$99/mo</div>
                    </div>
                    <div class="model-desc">Sonnet + Opus • Content • Design</div>
                    <button class="btn-primary" style="margin-top: 12px;">Deploy Team</button>
                </div>
            </div>
        </div>
    </main>
    
    <div id="help" class="panel" tabindex="-1" aria-hidden="true">
        <div class="card">
            <div class="card-title">⌨️ Keyboard Shortcuts</div>
            <div class="agent-list">
                <div class="agent-item">
                    <div class="agent-info">
                        <div class="agent-name">1 - 4</div>
                        <div class="agent-status">Navigate to tab 1-4</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-info">
                        <div class="agent-name">Alt + ←</div>
                        <div class="agent-status">Go back</div>
                    </div>
                </div>
                <div class="agent-item">
                    <div class="agent-info">
                        <div class="agent-name">Swipe Left/Right</div>
                        <div class="agent-status">Next/Previous tab (mobile)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <nav class="bottom-nav">
        <button class="nav-item active" onclick="showTab('dashboard')" aria-label="Dashboard" aria-current="page">
            <span>🏠</span>
            Home
        </button>
        <button class="nav-item" onclick="showTab('models')" aria-label="Models">
            <span>🤖</span>
            Models
        </button>
        <button class="nav-item" onclick="showTab('spawn')" aria-label="Spawn Agent">
            <span>🚀</span>
            Spawn
        </button>
        <button class="nav-item" onclick="showTab('teams')" aria-label="Teams">
            <span>👥</span>
            Teams
        </button>
    </nav>
    
    <script>
        // Navigation State Management
        const NavState = {
            currentTab: 'dashboard',
            isTransitioning: false,
            pendingTab: null,
            queuedTab: null,
            transitionTimeoutId: null,
            queuedNavTimeoutId: null,
            popstateTimeoutId: null,
            transitionCooldown: 150,
            lastTransitionTime: 0,
            history: [],
            maxHistory: 10,
            tabs: ['dashboard', 'models', 'spawn', 'teams'],
            failedTransitions: 0,
            maxRetries: 3,
            
            canTransition() {
                const now = Date.now();
                if (this.isTransitioning) return false;
                if (now - this.lastTransitionTime < this.transitionCooldown) return false;
                return true;
            },

            normalizeTab(tabId) {
                if (!tabId || typeof tabId !== 'string') return 'dashboard';
                return this.tabs.includes(tabId) ? tabId : 'dashboard';
            },
            
            pushHistory(tabId) {
                if (this.history.length >= this.maxHistory) {
                    this.history.shift();
                }
                if (this.history[this.history.length - 1] !== tabId) {
                    this.history.push(tabId);
                }
            },
            
            goBack() {
                if (this.history.length < 2) return false;
                this.history.pop();
                return this.history[this.history.length - 1];
            },
            
            getNextTab() {
                const idx = this.tabs.indexOf(this.currentTab);
                return this.tabs[(idx + 1) % this.tabs.length];
            },
            
            getPrevTab() {
                const idx = this.tabs.indexOf(this.currentTab);
                return this.tabs[(idx - 1 + this.tabs.length) % this.tabs.length];
            },
            
            recordSuccess() {
                this.failedTransitions = 0;
            },
            
            recordFailure() {
                this.failedTransitions++;
                return this.failedTransitions < this.maxRetries;
            },
            
            reset() {
                this.isTransitioning = false;
                this.pendingTab = null;
                this.queuedTab = null;
                if (this.transitionTimeoutId) {
                    clearTimeout(this.transitionTimeoutId);
                    this.transitionTimeoutId = null;
                }
                if (this.popstateTimeoutId) {
                    clearTimeout(this.popstateTimeoutId);
                    this.popstateTimeoutId = null;
                }
                if (this.queuedNavTimeoutId) {
                    clearTimeout(this.queuedNavTimeoutId);
                    this.queuedNavTimeoutId = null;
                }
                this.failedTransitions = 0;
                hideLoading();
            }
        };
        
        // Touch/Swipe Handling with improved edge rejection
        const TouchHandler = {
            startX: 0,
            startY: 0,
            startTime: 0,
            threshold: 80,
            maxTime: 300,
            edgeThreshold: 20, // Ignore swipes starting too close to edge
            minIntervalMs: 180,
            lastSwipeAt: 0,
            isTracking: false,
            
            init() {
                // Only enable swipe navigation on touch-centric devices.
                if (!(window.matchMedia && window.matchMedia('(pointer: coarse)').matches)) {
                    return;
                }
                const opts = { passive: true };
                document.addEventListener('touchstart', this.onStart.bind(this), opts);
                document.addEventListener('touchend', this.onEnd.bind(this), opts);
                document.addEventListener('touchcancel', this.onCancel.bind(this), opts);
            },
            
            onStart(e) {
                // Ignore gestures starting on interactive controls.
                if (e.target && e.target.closest('button, a, input, textarea, select, label, [role="button"]')) {
                    this.isTracking = false;
                    return;
                }

                if (!e.touches || e.touches.length === 0) {
                    this.isTracking = false;
                    return;
                }

                const touch = e.touches[0];
                const viewportWidth = window.innerWidth;
                
                // Ignore edge touches (iOS edge swipe gestures)
                if (touch.clientX < this.edgeThreshold || 
                    touch.clientX > viewportWidth - this.edgeThreshold) {
                    this.isTracking = false;
                    return;
                }
                
                this.startX = touch.clientX;
                this.startY = touch.clientY;
                this.startTime = Date.now();
                this.isTracking = true;
            },
            
            onEnd(e) {
                if (!this.isTracking) return;
                this.isTracking = false;

                if (!e.changedTouches || e.changedTouches.length === 0) return;
                const touch = e.changedTouches[0];
                const deltaX = touch.clientX - this.startX;
                const deltaY = touch.clientY - this.startY;
                const deltaTime = Date.now() - this.startTime;
                
                // Validate swipe
                if (deltaTime > this.maxTime) return;
                if (Math.abs(deltaY) > Math.abs(deltaX) * 1.5) return; // Mostly vertical
                if (Math.abs(deltaX) < this.threshold) return;
                
                // Guard against swipe burst spam / in-flight transitions
                if (NavState.isTransitioning) return;
                const now = Date.now();
                if (now - this.lastSwipeAt < this.minIntervalMs) return;
                this.lastSwipeAt = now;

                // Execute navigation
                if (deltaX > 0) {
                    showTab(NavState.getPrevTab());
                } else {
                    showTab(NavState.getNextTab());
                }
            },
            
            onCancel() {
                this.isTracking = false;
            }
        };
        
        // Online/Offline Detection with debouncing
        const ConnectionHandler = {
            offlineTimer: null,
            debounceMs: 1000,
            
            init() {
                window.addEventListener('online', () => this.setOnline(true));
                window.addEventListener('offline', () => this.setOnline(false));
                this.updateStatus(navigator.onLine);
            },

            destroy() {
                if (this.offlineTimer) {
                    clearTimeout(this.offlineTimer);
                    this.offlineTimer = null;
                }
            },
            
            setOnline(isOnline) {
                clearTimeout(this.offlineTimer);
                
                if (isOnline) {
                    this.updateStatus(true);
                } else {
                    // Debounce offline events
                    this.offlineTimer = setTimeout(() => {
                        this.updateStatus(false);
                    }, this.debounceMs);
                }
            },
            
            updateStatus(isOnline) {
                const header = document.querySelector('.header h1');
                const title = document.querySelector('title');
                
                if (isOnline) {
                    document.body.classList.remove('offline');
                    if (header) {
                        header.style.color = '';
                        header.textContent = '◈ J1MSKY Agency v6.0.27';
                    }
                    if (title) title.textContent = 'J1MSKY Agency v6.0.27';
                } else {
                    document.body.classList.add('offline');
                    if (header) {
                        header.style.color = 'var(--red)';
                        header.textContent = '◈ Agency (Offline)';
                    }
                    if (title) title.textContent = 'Agency (Offline)';
                }
            }
        };
        
        // ResizeObserver for responsive adjustments
        const ResizeHandler = {
            observer: null,
            lastWidth: 0,
            lastHeight: 0,
            debounceTimer: null,
            
            init() {
                if (window.ResizeObserver) {
                    this.observer = new ResizeObserver(entries => {
                        clearTimeout(this.debounceTimer);
                        this.debounceTimer = setTimeout(() => this.handleResize(entries[0]), 100);
                    });
                    this.observer.observe(document.body);
                } else {
                    // Fallback for older browsers
                    window.addEventListener('resize', () => {
                        clearTimeout(this.debounceTimer);
                        this.debounceTimer = setTimeout(() => this.handleResize(), 100);
                    });
                }
                
                // Orientation change (mobile)
                window.addEventListener('orientationchange', () => {
                    setTimeout(() => this.handleResize(), 300);
                });
            },
            
            handleResize(entry) {
                const width = entry?.contentRect?.width || window.innerWidth;
                const height = entry?.contentRect?.height || window.innerHeight;
                if (Math.abs(width - this.lastWidth) < 50 && Math.abs(height - this.lastHeight) < 50) return;
                this.lastWidth = width;
                this.lastHeight = height;

                // Smooth layout refresh without body hide/show flicker.
                requestAnimationFrame(() => {
                    // Re-ensure active panel is visible
                    const active = document.querySelector('.panel.active');
                    if (active) {
                        active.style.display = 'block';
                    }

                    // Keep help overlay consistent through resize/orientation changes.
                    if (typeof helpVisible !== 'undefined' && helpVisible) {
                        const helpPanel = document.getElementById('help');
                        if (helpPanel) helpPanel.style.display = 'block';
                    }
                });
            },
            
            destroy() {
                if (this.debounceTimer) {
                    clearTimeout(this.debounceTimer);
                    this.debounceTimer = null;
                }
                if (this.observer) {
                    this.observer.disconnect();
                    this.observer = null;
                }
            }
        };
        
        // Focus management for accessibility
        const FocusManager = {
            init() {
                document.querySelectorAll('.panel').forEach((panel) => {
                    if (!panel.hasAttribute('tabindex')) panel.setAttribute('tabindex', '-1');
                });
                // Restore focus after navigation
                document.addEventListener('click', (e) => {
                    if (e.target.closest('.nav-item')) {
                        // Move focus to main content after nav click
                        setTimeout(() => {
                            const active = document.querySelector('.panel.active');
                            if (active) active.focus();
                        }, 100);
                    }
                });
            }
        };
        
        function showLoading() {
            document.body.classList.add('navigating');
            const main = document.querySelector('.main');
            if (main) main.setAttribute('aria-busy', 'true');
            if (typeof StatsUpdater !== 'undefined') {
                StatsUpdater.pauseForTransition();
            }
        }

        function hideLoading() {
            document.body.classList.remove('navigating');
            const main = document.querySelector('.main');
            if (main) main.setAttribute('aria-busy', 'false');
            if (typeof StatsUpdater !== 'undefined') {
                StatsUpdater.resumeAfterTransition();
            }
        }
        
        function showTab(tabId, pushState = true) {
            tabId = NavState.normalizeTab(tabId);
            
            // Prevent duplicate or conflicting transitions
            if (tabId === NavState.currentTab || tabId === NavState.pendingTab) {
                return;
            }

            // Check transition availability; queue latest request instead of dropping it.
            if (!NavState.canTransition()) {
                NavState.queuedTab = tabId;
                if (!NavState.queuedNavTimeoutId) {
                    NavState.queuedNavTimeoutId = setTimeout(() => {
                        const nextTab = NavState.queuedTab;
                        NavState.queuedTab = null;
                        NavState.queuedNavTimeoutId = null;
                        if (nextTab && nextTab !== NavState.currentTab) showTab(nextTab);
                    }, NavState.transitionCooldown + 10);
                }
                return;
            }
            
            // Verify target exists
            const targetPanel = document.getElementById(tabId);
            if (!targetPanel) {
                console.error('Panel not found:', tabId);
                if (!NavState.recordFailure()) {
                    console.error('Max retries exceeded, resetting state');
                    NavState.reset();
                }
                return;
            }
            
            // If help overlay is open, close it before navigating.
            if (typeof helpVisible !== 'undefined' && helpVisible) {
                toggleHelp();
            }

            // Begin transition
            NavState.isTransitioning = true;
            NavState.pendingTab = tabId;
            NavState.lastTransitionTime = Date.now();
            showLoading();

            // Watchdog: prevent stuck transitioning state if a frame/update is dropped.
            if (NavState.transitionTimeoutId) clearTimeout(NavState.transitionTimeoutId);
            NavState.transitionTimeoutId = setTimeout(() => {
                if (NavState.isTransitioning && NavState.pendingTab === tabId) {
                    NavState.reset();
                }
            }, Math.max(1000, NavState.transitionCooldown * 6));
            
            try {
                const panels = document.querySelectorAll('.panel');
                const navItems = document.querySelectorAll('.nav-item');
                const tabIndex = NavState.tabs.indexOf(tabId);
                
                // Validate tab index
                if (tabIndex === -1) {
                    throw new Error('Invalid tab index for: ' + tabId);
                }
                
                // Hide current panels
                panels.forEach(p => p.classList.remove('active'));
                
                // Use requestAnimationFrame for smooth transition
                requestAnimationFrame(() => {
                    try {
                        // Show target panel
                        targetPanel.style.display = 'block';
                        targetPanel.offsetHeight; // Force reflow
                        targetPanel.classList.add('active');
                        
                        // Update navigation
                        navItems.forEach((n, i) => {
                            const isActive = i === tabIndex;
                            n.classList.toggle('active', isActive);
                            if (isActive) {
                                n.setAttribute('aria-current', 'page');
                            } else {
                                n.removeAttribute('aria-current');
                            }
                        });
                        
                        // Scroll to top (respect reduced-motion preferences)
                        const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                        if (!document.hidden) {
                            window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
                        }
                        
                        // Update state
                        NavState.currentTab = tabId;
                        SessionStore.save(tabId);
                        NavState.recordSuccess();
                        
                        if (pushState) {
                            NavState.pushHistory(tabId);
                            safePushState({ tab: tabId }, '#' + tabId);
                        }
                        
                        // Cleanup after transition
                        setTimeout(() => {
                            NavState.isTransitioning = false;
                            NavState.pendingTab = null;
                            if (NavState.transitionTimeoutId) {
                                clearTimeout(NavState.transitionTimeoutId);
                                NavState.transitionTimeoutId = null;
                            }
                            hideLoading();
                            // Hide inactive panels for performance
                            panels.forEach(p => {
                                if (!p.classList.contains('active')) {
                                    p.style.display = 'none';
                                }
                            });
                        }, NavState.transitionCooldown);
                        
                    } catch (innerError) {
                        console.error('Error during transition:', innerError);
                        handleTransitionError(tabId, pushState);
                    }
                });
                
            } catch (error) {
                console.error('Error starting transition:', error);
                handleTransitionError(tabId, pushState);
            }
        }
        
        function handleTransitionError(tabId, pushState = true) {
            if (NavState.recordFailure()) {
                // Retry once after a short delay
                setTimeout(() => showTab(tabId, pushState), 100);
            } else {
                NavState.reset();
                // Fallback to dashboard
                if (tabId !== 'dashboard') {
                    showTab('dashboard', pushState);
                }
            }
        }
        
        // Session persistence
        const SessionStore = {
            STORAGE_KEY: 'j1msky_last_tab',
            
            save(tabId) {
                try {
                    sessionStorage.setItem(this.STORAGE_KEY, tabId);
                } catch (e) {
                    console.warn('Session storage not available');
                }
            },
            
            load() {
                try {
                    return sessionStorage.getItem(this.STORAGE_KEY);
                } catch (e) {
                    return null;
                }
            },
            
            clear() {
                try {
                    sessionStorage.removeItem(this.STORAGE_KEY);
                } catch (e) {}
            }
        };
        
        window.addEventListener('popstate', (e) => {
            const targetTab = NavState.normalizeTab(e.state?.tab || window.location.hash.slice(1) || 'dashboard');

            // Ensure overlay state doesn't conflict with browser history navigation.
            if (typeof helpVisible !== 'undefined' && helpVisible) {
                toggleHelp();
            }

            // If a transition is already active, defer popstate nav slightly.
            if (NavState.isTransitioning) {
                if (NavState.popstateTimeoutId) clearTimeout(NavState.popstateTimeoutId);
                NavState.popstateTimeoutId = setTimeout(() => {
                    NavState.popstateTimeoutId = null;
                    showTab(targetTab, false);
                }, NavState.transitionCooldown + 20);
                return;
            }

            showTab(targetTab, false);
        });
        
        function isTypingTarget(el) {
            if (!el) return false;
            const tag = (el.tagName || '').toLowerCase();
            return el.isContentEditable || tag === 'input' || tag === 'textarea' || tag === 'select';
        }

        function safePushState(state, hash) {
            try {
                history.pushState(state, '', hash);
            } catch (e) {
                // no-op on environments that restrict history mutations
            }
        }

        function safeReplaceState(state, hash) {
            try {
                history.replaceState(state, '', hash);
            } catch (e) {
                // no-op on environments that restrict history mutations
            }
        }

        function syncNavAriaFromActive() {
            const navItems = document.querySelectorAll('.nav-item');
            navItems.forEach((n) => {
                if (n.classList.contains('active')) n.setAttribute('aria-current', 'page');
                else n.removeAttribute('aria-current');
            });
        }

        document.addEventListener('keydown', (e) => {
            if (isTypingTarget(e.target)) return;
            if (e.altKey && e.key === 'ArrowLeft') {
                e.preventDefault();
                const prev = NavState.goBack();
                if (prev) showTab(prev);
                return;
            }
            if (e.key === '?' || e.key === 'h' || e.key === 'H') {
                e.preventDefault();
                toggleHelp();
                return;
            }
            if (!e.ctrlKey && !e.metaKey && !e.altKey) {
                const num = parseInt(e.key);
                if (num >= 1 && num <= 4) {
                    e.preventDefault();
                    showTab(NavState.tabs[num - 1]);
                }
            }
        });
        
        // Toggle help panel with state management
        let helpVisible = false;
        function toggleHelp() {
            const helpPanel = document.getElementById('help');
            if (!helpPanel) return;
            
            helpVisible = !helpVisible;
            const mainPanels = document.querySelectorAll('.main .panel');
            
            const helpBtn = document.querySelector('.help-btn');
            if (helpBtn) helpBtn.setAttribute('aria-expanded', helpVisible ? 'true' : 'false');

            if (helpVisible) {
                // Store current state before showing help
                helpPanel.dataset.previousTab = NavState.currentTab;
                mainPanels.forEach(p => {
                    p.style.display = 'none';
                    p.classList.remove('active');
                });
                helpPanel.style.display = 'block';
                helpPanel.classList.add('active');
                helpPanel.setAttribute('aria-hidden', 'false');
            } else {
                helpPanel.style.display = 'none';
                helpPanel.classList.remove('active');
                helpPanel.setAttribute('aria-hidden', 'true');
                // Restore previous tab
                const previousTab = helpPanel.dataset.previousTab || NavState.currentTab;
                const current = document.getElementById(previousTab);
                if (current) {
                    current.style.display = 'block';
                    current.classList.add('active');
                }
            }
        }
        
        // Close help on Escape key
        document.addEventListener('keydown', (e) => {
            if (isTypingTarget(e.target)) return;
            if (e.key === 'Escape' && helpVisible) {
                e.preventDefault();
                toggleHelp();
            }
        });
        
        // Visibility handling
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                document.body.classList.add('paused');
            } else {
                document.body.classList.remove('paused');
                requestAnimationFrame(() => {
                    const active = document.querySelector('.panel.active');
                    if (active) active.style.display = 'block';
                });
            }
        });
        
        // Prevent double-tap zoom (without interfering with form/button taps)
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            if (e.target && e.target.closest('button, a, input, textarea, select, label, [role="button"]')) {
                lastTouchEnd = Date.now();
                return;
            }
            const now = Date.now();
            if (now - lastTouchEnd <= 300) e.preventDefault();
            lastTouchEnd = now;
        }, { passive: false });
        
        // Real-time stats updater
        const StatsUpdater = {
            interval: null,
            inFlight: false,
            controller: null,
            pausedByTransition: false,
            lastLogHtml: '',
            lastMetaText: '',
            updateInterval: 5000, // 5 seconds
            
            init() {
                this.start();
                // Resume on visibility change
                document.addEventListener('visibilitychange', () => {
                    if (document.hidden) {
                        this.stop();
                    } else {
                        this.start();
                        this.update(); // Immediate update on return
                    }
                });
            },
            
            start() {
                if (this.interval) return;
                this.interval = setInterval(() => this.update(), this.updateInterval);
            },
            
            stop() {
                if (this.interval) {
                    clearInterval(this.interval);
                    this.interval = null;
                }
                if (this.controller) {
                    this.controller.abort();
                    this.controller = null;
                }
                // Reset transient polling state to avoid stale locks after resume.
                this.inFlight = false;
                this.pausedByTransition = false;
            },

            pauseForTransition() {
                this.pausedByTransition = true;
                this.stop();
            },

            resumeAfterTransition() {
                if (!this.pausedByTransition || document.hidden) return;
                this.pausedByTransition = false;
                this.start();
            },
            
            async update() {
                if (this.inFlight || document.hidden) return;
                this.inFlight = true;
                this.controller = new AbortController();
                try {
                    const res = await fetch('/api/live', { cache: 'no-store', signal: this.controller.signal });
                    if (!res.ok) throw new Error('live endpoint error');
                    const data = await res.json();

                    // Update header badges
                    const tempBadge = document.querySelector('.stat-badge.temp');
                    const memBadge = document.querySelector('.stat-badge.mem');
                    if (tempBadge) tempBadge.textContent = `${data.temp}°C`;
                    if (memBadge) memBadge.textContent = `${data.mem}%`;

                    // Ensure live panel exists
                    let panel = document.getElementById('live-watch-panel');
                    if (!panel) {
                        panel = document.createElement('div');
                        panel.id = 'live-watch-panel';
                        panel.className = 'card';
                        panel.innerHTML = `
                          <div class="card-title">📡 Live Watch</div>
                          <div id="live-watch-meta" style="font-size:12px;color:var(--text-2);margin-bottom:8px"></div>
                          <div id="live-watch-log" style="font-family:monospace;font-size:12px;line-height:1.5;max-height:180px;overflow:auto;background:var(--bg-3);border:1px solid var(--border);border-radius:8px;padding:10px"></div>
                        `;
                        const dashboard = document.getElementById('dashboard');
                        if (dashboard) dashboard.appendChild(panel);
                    }

                    const meta = document.getElementById('live-watch-meta');
                    const nextMeta = `req:${data.requests} • py:${data.python_procs} • updated:${data.now}`;
                    if (meta && this.lastMetaText !== nextMeta) {
                        meta.textContent = nextMeta;
                        this.lastMetaText = nextMeta;
                    }

                    const log = document.getElementById('live-watch-log');
                    if (log) {
                        const esc = (v) => String(v)
                            .replace(/&/g, '&amp;')
                            .replace(/</g, '&lt;')
                            .replace(/>/g, '&gt;')
                            .replace(/"/g, '&quot;')
                            .replace(/'/g, '&#39;');
                        const nextLogHtml = (data.logs || []).map(l => `<div>${esc(l)}</div>`).join('');
                        if (this.lastLogHtml !== nextLogHtml) {
                            log.innerHTML = nextLogHtml;
                            this.lastLogHtml = nextLogHtml;
                        }
                    }

                    // pulse effect
                    const badges = document.querySelectorAll('.header-stats .stat-badge');
                    badges.forEach(badge => {
                        badge.style.animation = 'pulse 0.4s ease';
                        setTimeout(() => badge.style.animation = '', 400);
                    });
                } catch (e) {
                    // keep silent in UI; dashboard still usable
                } finally {
                    this.inFlight = false;
                    this.controller = null;
                }
            }
        };
        
        // Add pulse animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `;
        document.head.appendChild(style);
        
        // Error Boundary for uncaught errors
        window.addEventListener('error', (e) => {
            console.error('Global error:', e.message);
            NavState.reset();
            // Prevent complete crash
            e.preventDefault();
        });
        
        window.addEventListener('unhandledrejection', (e) => {
            console.error('Unhandled promise rejection:', e.reason);
            NavState.reset();
            e.preventDefault();
        });
        
        // Smooth scroll polyfill for older browsers
        if (!('scrollBehavior' in document.documentElement.style)) {
            const nativeScrollTo = window.scrollTo.bind(window);
            window.scrollTo = function(options) {
                if (typeof options === 'object' && options.top !== undefined) {
                    const start = window.pageYOffset;
                    const target = options.top;
                    const duration = 300;
                    const startTime = performance.now();
                    
                    function step(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        const ease = 1 - Math.pow(1 - progress, 3);
                        nativeScrollTo(0, start + (target - start) * ease);
                        
                        if (progress < 1) {
                            requestAnimationFrame(step);
                        }
                    }
                    requestAnimationFrame(step);
                } else {
                    // Fallback for non-object calls
                    nativeScrollTo(arguments[0], arguments[1]);
                }
            };
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            TouchHandler.init();
            ConnectionHandler.init();
            ResizeHandler.init();
            FocusManager.init();
            StatsUpdater.init();
            syncNavAriaFromActive();
            
            // Determine initial tab: hash > session > default
            const hash = window.location.hash.slice(1);
            const sessionTab = SessionStore.load();
            const initialTab = NavState.normalizeTab(hash || sessionTab || 'dashboard');
            
            NavState.pushHistory(initialTab);
            if (!hash) safeReplaceState({ tab: initialTab }, '#' + initialTab);
            
            // Sync UI with initial tab
            if (initialTab !== 'dashboard') {
                showTab(initialTab, false);
            }
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            ResizeHandler.destroy();
            StatsUpdater.stop();
            ConnectionHandler.destroy();
            // Keep SessionStore intact so tab persistence survives refresh/reopen.
        });
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
        elif self.path == '/api/live':
            stats = get_stats()
            # lightweight process count
            py_count = 0
            try:
                out = subprocess.run(['bash','-lc','ps aux | grep python | grep -v grep | wc -l'], capture_output=True, text=True)
                py_count = int((out.stdout or '0').strip() or 0)
            except Exception:
                py_count = 0

            # gather short logs from known files
            logs = []
            for p in ['/tmp/alexa-bridge.log','/tmp/j1msky-agency.log','/tmp/alexa-cmd-center.log']:
                try:
                    if os.path.exists(p):
                        with open(p, 'r', errors='ignore') as f:
                            lines = f.readlines()[-3:]
                            for ln in lines:
                                t = ln.strip()
                                if t:
                                    logs.append(f"{os.path.basename(p)}: {t[:120]}")
                except Exception:
                    pass
            if not logs:
                logs = ['Live watch online', 'No recent log lines']

            payload = {
                'temp': stats.get('temp', 0),
                'mem': stats.get('mem', 0),
                'uptime': stats.get('uptime', '0h'),
                'requests': REQUEST_COUNT,
                'python_procs': py_count,
                'now': datetime.now().strftime('%H:%M:%S'),
                'logs': logs[:12]
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode())
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), AgencyServer) as httpd:
        print("")
        print("╔══════════════════════════════════════════════════════════╗")
        print("║          J1MSKY Agency v6.0.27 - Transition Guard Patch          ║")
        print("╠══════════════════════════════════════════════════════════╣")
        print("║  ✓ Real-time stats updater                               ║")
        print("║  ✓ Session persistence across refreshes                  ║")
        print("║  ✓ Error boundaries & recovery                           ║")
        print("║  ✓ Swipe navigation & gesture support                    ║")
        print("║  ✓ Offline detection & visual feedback                   ║")
        print("║  ✓ Responsive mobile/tablet/desktop layouts              ║")
        print("╚══════════════════════════════════════════════════════════╝")
        print("")
        print("http://localhost:8080")
        print("")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
