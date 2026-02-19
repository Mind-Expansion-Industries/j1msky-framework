#!/usr/bin/env python3
"""
J1MSKY Agency v5.7 - Error Boundaries & Smooth Interactions
Global error handling, scroll polyfill, improved help panel state
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
    <title>J1MSKY Agency v5.7</title>
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
            margin: 0 auto;
            /* Smooth scrolling */
            scroll-behavior: smooth;
            -webkit-overflow-scrolling: touch;
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
        <h1>◈ J1MSKY Agency v5.7</h1>
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
    
    <div id="help" class="panel" tabindex="-1">
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
        <button class="nav-item active" onclick="showTab('dashboard')" aria-label="Dashboard">
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
            isTracking: false,
            
            init() {
                const opts = { passive: true };
                document.addEventListener('touchstart', this.onStart.bind(this), opts);
                document.addEventListener('touchend', this.onEnd.bind(this), opts);
                document.addEventListener('touchcancel', this.onCancel.bind(this), opts);
            },
            
            onStart(e) {
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
                
                const touch = e.changedTouches[0];
                const deltaX = touch.clientX - this.startX;
                const deltaY = touch.clientY - this.startY;
                const deltaTime = Date.now() - this.startTime;
                
                // Validate swipe
                if (deltaTime > this.maxTime) return;
                if (Math.abs(deltaY) > Math.abs(deltaX) * 1.5) return; // Mostly vertical
                if (Math.abs(deltaX) < this.threshold) return;
                
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
                        header.textContent = '◈ J1MSKY Agency v5.7';
                    }
                    if (title) title.textContent = 'J1MSKY Agency v5.7';
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
                if (Math.abs(width - this.lastWidth) < 50) return;
                this.lastWidth = width;
                
                // Force layout recalculation on significant resize
                document.body.style.display = 'none';
                document.body.offsetHeight;
                document.body.style.display = '';
                
                // Re-ensure active panel is visible
                const active = document.querySelector('.panel.active');
                if (active) {
                    active.style.display = 'block';
                }
            },
            
            destroy() {
                if (this.observer) {
                    this.observer.disconnect();
                }
            }
        };
        
        // Focus management for accessibility
        const FocusManager = {
            init() {
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
        
        function hideLoading() {
            document.body.classList.remove('navigating');
        }
        
        function showTab(tabId, pushState = true) {
            // Validate inputs
            if (!tabId || typeof tabId !== 'string') {
                console.error('Invalid tabId:', tabId);
                return;
            }
            
            // Check transition availability
            if (!NavState.canTransition()) {
                console.log('Navigation blocked: cooldown or in progress');
                return;
            }
            
            // Prevent navigating to same tab
            if (tabId === NavState.currentTab) {
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
            
            // Begin transition
            NavState.isTransitioning = true;
            NavState.lastTransitionTime = Date.now();
            showLoading();
            
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
                            n.classList.toggle('active', i === tabIndex);
                        });
                        
                        // Scroll to top smoothly
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                        
                        // Update state
                        NavState.currentTab = tabId;
                        NavState.recordSuccess();
                        
                        if (pushState) {
                            NavState.pushHistory(tabId);
                            history.pushState({ tab: tabId }, '', '#' + tabId);
                        }
                        
                        // Cleanup after transition
                        setTimeout(() => {
                            NavState.isTransitioning = false;
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
                        handleTransitionError(tabId);
                    }
                });
                
            } catch (error) {
                console.error('Error starting transition:', error);
                handleTransitionError(tabId);
            }
        }
        
        function handleTransitionError(tabId) {
            if (NavState.recordFailure()) {
                // Retry once after a short delay
                setTimeout(() => showTab(tabId), 100);
            } else {
                NavState.reset();
                // Fallback to dashboard
                if (tabId !== 'dashboard') {
                    showTab('dashboard');
                }
            }
        }
        
        // Event Listeners
        window.addEventListener('popstate', (e) => {
            if (e.state?.tab) {
                showTab(e.state.tab, false);
            } else {
                showTab('dashboard', false);
            }
        });
        
        document.addEventListener('keydown', (e) => {
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
            
            if (helpVisible) {
                // Store current state before showing help
                helpPanel.dataset.previousTab = NavState.currentTab;
                mainPanels.forEach(p => {
                    p.style.display = 'none';
                    p.classList.remove('active');
                });
                helpPanel.style.display = 'block';
                helpPanel.classList.add('active');
            } else {
                helpPanel.style.display = 'none';
                helpPanel.classList.remove('active');
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
        
        // Prevent double-tap zoom
        let lastTouchEnd = 0;
        document.addEventListener('touchend', (e) => {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) e.preventDefault();
            lastTouchEnd = now;
        }, { passive: false });
        
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
                        window.scrollTo(0, start + (target - start) * ease);
                        
                        if (progress < 1) {
                            requestAnimationFrame(step);
                        }
                    }
                    requestAnimationFrame(step);
                } else {
                    // Fallback for non-object calls
                    window.scrollTo(arguments[0], arguments[1]);
                }
            };
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            TouchHandler.init();
            ConnectionHandler.init();
            ResizeHandler.init();
            FocusManager.init();
            
            const hash = window.location.hash.slice(1);
            const initialTab = (hash && document.getElementById(hash)) ? hash : 'dashboard';
            NavState.pushHistory(initialTab);
            if (!hash) history.replaceState({ tab: 'dashboard' }, '', '#dashboard');
        });
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            ResizeHandler.destroy();
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
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), AgencyServer) as httpd:
        print("J1MSKY Agency v5.7 - Error Boundaries & Smooth Interactions")
        print("Global error handling, scroll polyfill, improved help panel")
        print("Press '?' or 'h' for keyboard shortcuts")
        print("http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
