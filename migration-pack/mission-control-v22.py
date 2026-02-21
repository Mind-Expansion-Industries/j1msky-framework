#!/usr/bin/env python3
"""
J1MSKY Mission Control v2.3 - Enhanced UI Edition
Animations, performance optimizations, modern styling
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

# Enhanced HTML Template with Animations & Performance Optimizations
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>◈ J1MSKY MISSION CONTROL v2.3 ◈</title>
    <style>
        /* CSS Reset & Base */
        *, *::before, *::after { 
            margin: 0; 
            padding: 0; 
            box-sizing: border-box;
        }
        
        :root {
            /* Color System */
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: rgba(26, 26, 37, 0.6);
            --bg-glass: rgba(26, 26, 37, 0.4);
            --accent-cyan: #00ffff;
            --accent-green: #00ff88;
            --accent-pink: #ff00ff;
            --accent-yellow: #ffff00;
            --accent-red: #ff4444;
            --accent-purple: #9945ff;
            --accent-orange: #ff8800;
            --text-primary: #e0e0e0;
            --text-secondary: #888888;
            --border: rgba(255, 255, 255, 0.1);
            --shadow-glow: rgba(0, 255, 255, 0.15);
            
            /* Animation Timing */
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
            --duration-fast: 150ms;
            --duration-normal: 300ms;
            --duration-slow: 500ms;
        }
        
        /* Performance: GPU Acceleration */
        .gpu-accelerated {
            transform: translateZ(0);
            will-change: transform, opacity;
            backface-visibility: hidden;
        }
        
        /* Loading Animation */
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        
        .loading {
            background: linear-gradient(90deg, var(--bg-secondary) 25%, rgba(0,255,255,0.1) 50%, var(--bg-secondary) 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
        }
        
        /* Page Load Animation */
        @keyframes pageLoad {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes fadeScale {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }
        
        @keyframes slideInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.4); }
            50% { opacity: 0.8; box-shadow: 0 0 20px 5px rgba(0, 255, 136, 0.2); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px var(--shadow-glow); }
            50% { box-shadow: 0 0 20px var(--shadow-glow), 0 0 40px var(--shadow-glow); }
        }
        
        @keyframes scanline {
            0% { transform: translateY(-100%); }
            100% { transform: translateY(100vh); }
        }
        
        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes borderGlow {
            0%, 100% { border-color: rgba(0, 255, 255, 0.3); }
            50% { border-color: rgba(0, 255, 255, 0.8); }
        }
        
        body {
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            min-height: 100vh;
            overflow-x: hidden;
            line-height: 1.6;
            animation: pageLoad 0.6s var(--ease-out-expo);
        }
        
        /* Scanline Effect */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
            opacity: 0.1;
            animation: scanline 8s linear infinite;
            pointer-events: none;
            z-index: 9999;
        }
        
        /* Background Grid */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: -1;
        }
        
        /* Header with Gateway Status */
        .header {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
            padding: 20px 30px;
            border-bottom: 2px solid transparent;
            border-image: linear-gradient(90deg, var(--accent-cyan), var(--accent-pink), var(--accent-cyan)) 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
            position: relative;
            overflow: hidden;
            animation: slideInLeft 0.5s var(--ease-out-expo);
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0,255,255,0.1), transparent);
            animation: shimmer 3s infinite;
        }
        
        .header h1 {
            color: var(--accent-cyan);
            font-size: 1.8em;
            text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
            letter-spacing: 3px;
            font-weight: 700;
            position: relative;
            animation: glow 3s ease-in-out infinite;
        }
        
        .header h1 span {
            color: var(--accent-pink);
            text-shadow: 0 0 30px rgba(255, 0, 255, 0.5);
        }
        
        .gateway-status {
            display: flex;
            gap: 12px;
            align-items: center;
            padding: 10px 20px;
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid var(--accent-green);
            border-radius: 30px;
            font-size: 13px;
            transition: all var(--duration-normal) var(--ease-in-out);
            animation: fadeScale 0.5s var(--ease-out-expo) 0.1s both;
        }
        
        .gateway-status:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 255, 136, 0.2);
        }
        
        .gateway-status.offline {
            background: rgba(255, 68, 68, 0.1);
            border-color: var(--accent-red);
        }
        
        .gateway-status.offline:hover {
            box-shadow: 0 10px 30px rgba(255, 68, 68, 0.2);
        }
        
        .gateway-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--accent-green);
            animation: pulse 2s infinite;
        }
        
        .gateway-status.offline .gateway-dot {
            background: var(--accent-red);
            animation: none;
        }
        
        /* Navigation */
        .nav-tabs {
            display: flex;
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            overflow-x: auto;
            scrollbar-width: none;
            -ms-overflow-style: none;
            animation: slideInLeft 0.5s var(--ease-out-expo) 0.1s both;
        }
        
        .nav-tabs::-webkit-scrollbar {
            display: none;
        }
        
        .nav-tab {
            padding: 18px 28px;
            background: transparent;
            border: none;
            color: var(--text-secondary);
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all var(--duration-normal) var(--ease-in-out);
            white-space: nowrap;
            border-bottom: 3px solid transparent;
            position: relative;
            overflow: hidden;
        }
        
        .nav-tab::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 50%;
            width: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-pink));
            transition: all var(--duration-normal) var(--ease-out-expo);
            transform: translateX(-50%);
        }
        
        .nav-tab:hover {
            color: var(--text-primary);
            background: rgba(0, 255, 255, 0.05);
        }
        
        .nav-tab:hover::after {
            width: 80%;
        }
        
        .nav-tab.active {
            color: var(--accent-cyan);
            background: var(--bg-card);
        }
        
        .nav-tab.active::after {
            width: 100%;
        }
        
        /* Main Content */
        .main-content {
            padding: 25px;
            max-width: 1800px;
            margin: 0 auto;
        }
        
        .panel {
            display: none;
            animation: fadeScale 0.4s var(--ease-out-expo);
            contain: layout style;
        }
        
        .panel.active {
            display: block;
        }
        
        /* Grid Layouts - Performance optimized */
        .grid-2, .grid-3, .grid-4 {
            display: grid;
            gap: 25px;
        }
        
        .grid-2 { grid-template-columns: repeat(2, 1fr); }
        .grid-3 { grid-template-columns: repeat(3, 1fr); }
        .grid-4 { grid-template-columns: repeat(4, 1fr); }
        
        @media (max-width: 1200px) {
            .grid-4 { grid-template-columns: repeat(2, 1fr); }
        }
        
        @media (max-width: 768px) {
            .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
            .header h1 { font-size: 1.3em; }
        }
        
        /* Cards with enhanced hover effects */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 25px;
            transition: all var(--duration-normal) var(--ease-out-expo);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
            transform: translateZ(0);
            animation: slideInUp 0.5s var(--ease-out-expo) both;
        }
        
        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-pink));
            transform: scaleX(0);
            transform-origin: left;
            transition: transform var(--duration-normal) var(--ease-out-expo);
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 30px var(--shadow-glow);
            border-color: rgba(0, 255, 255, 0.3);
        }
        
        .card:hover::before {
            transform: scaleX(1);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid var(--border);
        }
        
        .card-title {
            color: var(--text-primary);
            font-size: 1.1em;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        /* Staggered animation for cards */
        .card:nth-child(1) { animation-delay: 0s; }
        .card:nth-child(2) { animation-delay: 0.1s; }
        .card:nth-child(3) { animation-delay: 0.2s; }
        .card:nth-child(4) { animation-delay: 0.3s; }
        
        /* Stat Cards */
        .stat-card {
            text-align: center;
            padding: 30px 20px;
            position: relative;
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 800;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-pink));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: float 6s ease-in-out infinite;
        }
        
        .stat-label {
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-top: 10px;
        }
        
        /* Gateway Info Panel */
        .gateway-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }
        
        .gateway-item {
            background: var(--bg-glass);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border);
            transition: all var(--duration-normal) var(--ease-in-out);
            animation: fadeScale 0.4s var(--ease-out-expo) both;
        }
        
        .gateway-item:hover {
            transform: translateY(-3px);
            border-color: rgba(0, 255, 255, 0.3);
            box-shadow: 0 10px 30px rgba(0, 255, 255, 0.1);
        }
        
        .gateway-item:nth-child(1) { animation-delay: 0s; }
        .gateway-item:nth-child(2) { animation-delay: 0.05s; }
        .gateway-item:nth-child(3) { animation-delay: 0.1s; }
        .gateway-item:nth-child(4) { animation-delay: 0.15s; }
        .gateway-item:nth-child(5) { animation-delay: 0.2s; }
        .gateway-item:nth-child(6) { animation-delay: 0.25s; }
        
        .gateway-item-label {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
        .gateway-item-value {
            font-size: 1.2em;
            color: var(--accent-cyan);
            font-weight: 700;
        }
        
        /* Log Terminal with enhanced styling */
        .log-terminal {
            background: linear-gradient(180deg, #050508 0%, #0a0a10 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            font-family: 'Fira Code', 'JetBrains Mono', 'Courier New', monospace;
            font-size: 12px;
            max-height: 400px;
            overflow-y: auto;
            color: #a0a0a0;
            line-height: 1.7;
            scrollbar-width: thin;
            scrollbar-color: var(--accent-cyan) var(--bg-secondary);
        }
        
        .log-terminal::-webkit-scrollbar {
            width: 8px;
        }
        
        .log-terminal::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 4px;
        }
        
        .log-terminal::-webkit-scrollbar-thumb {
            background: var(--accent-cyan);
            border-radius: 4px;
        }
        
        .log-line {
            margin: 3px 0;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background var(--duration-fast);
        }
        
        .log-line:hover {
            background: rgba(0, 255, 255, 0.05);
        }
        
        .log-timestamp {
            color: var(--accent-pink);
            margin-right: 12px;
            font-weight: 600;
        }
        
        .log-level-info { color: var(--accent-cyan); }
        .log-level-warn { color: var(--accent-yellow); }
        .log-level-error { color: var(--accent-red); }
        
        /* Tool Status Grid */
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 15px;
        }
        
        .tool-item {
            background: var(--bg-glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 20px 15px;
            text-align: center;
            transition: all var(--duration-normal) var(--ease-out-expo);
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .tool-item::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(0,255,255,0.1), transparent);
            opacity: 0;
            transition: opacity var(--duration-normal);
        }
        
        .tool-item:hover::before {
            opacity: 1;
        }
        
        .tool-item:hover {
            transform: translateY(-5px) scale(1.02);
            border-color: var(--accent-cyan);
            box-shadow: 0 15px 30px rgba(0, 255, 255, 0.15);
        }
        
        .tool-item.enabled {
            border-color: var(--accent-green);
            background: rgba(0, 255, 136, 0.05);
        }
        
        .tool-item.enabled:hover {
            box-shadow: 0 15px 30px rgba(0, 255, 136, 0.2);
        }
        
        .tool-icon {
            font-size: 28px;
            margin-bottom: 10px;
            transition: transform var(--duration-normal);
        }
        
        .tool-item:hover .tool-icon {
            transform: scale(1.2);
        }
        
        .tool-name {
            font-size: 12px;
            color: var(--text-secondary);
            font-weight: 500;
        }
        
        .tool-status {
            position: absolute;
            top: 8px;
            right: 8px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 10px var(--accent-green);
        }
        
        /* Buttons with enhanced interactions */
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all var(--duration-normal) var(--ease-out-expo);
            display: inline-flex;
            align-items: center;
            gap: 8px;
            position: relative;
            overflow: hidden;
        }
        
        .btn::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            transform: translate(-50%, -50%);
            transition: width var(--duration-normal), height var(--duration-normal);
        }
        
        .btn:active::before {
            width: 300px;
            height: 300px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--accent-cyan), #0088aa);
            color: #000;
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
        }
        
        .btn-success {
            background: linear-gradient(135deg, var(--accent-green), #00aa55);
            color: #000;
            box-shadow: 0 4px 15px rgba(0, 255, 136, 0.3);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, var(--accent-red), #cc3333);
            color: #fff;
            box-shadow: 0 4px 15px rgba(255, 68, 68, 0.3);
        }
        
        .btn-ghost {
            background: transparent;
            border: 2px solid var(--border);
            color: var(--text-primary);
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4);
        }
        
        .btn:active {
            transform: translateY(-1px);
        }
        
        /* Quick Actions Grid */
        .quick-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
        }
        
        .quick-btn {
            padding: 20px 15px;
            background: var(--bg-glass);
            border: 1px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            cursor: pointer;
            text-align: center;
            transition: all var(--duration-normal) var(--ease-out-expo);
            position: relative;
            overflow: hidden;
        }
        
        .quick-btn::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 0;
            background: linear-gradient(180deg, transparent, rgba(0,255,255,0.1));
            transition: height var(--duration-normal);
        }
        
        .quick-btn:hover::after {
            height: 100%;
        }
        
        .quick-btn:hover {
            background: var(--accent-cyan);
            color: #000;
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 30px rgba(0, 255, 255, 0.3);
            border-color: var(--accent-cyan);
        }
        
        .quick-btn-icon {
            font-size: 28px;
            margin-bottom: 8px;
            transition: transform var(--duration-normal);
        }
        
        .quick-btn:hover .quick-btn-icon {
            transform: scale(1.2) rotate(5deg);
        }
        
        .quick-btn-text {
            font-size: 13px;
            font-weight: 500;
        }
        
        /* Progress Bars with animation */
        .progress-container {
            margin-bottom: 25px;
        }
        
        .progress-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 13px;
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
            border-radius: 5px;
            transition: width 1s var(--ease-out-expo);
            position: relative;
            overflow: hidden;
        }
        
        .progress-fill::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shimmer 2s infinite;
        }
        
        .progress-fill.temp {
            background: linear-gradient(90deg, var(--accent-green), var(--accent-yellow), var(--accent-red));
        }
        
        .progress-fill.memory {
            background: linear-gradient(90deg, var(--accent-green), var(--accent-cyan));
        }
        
        .progress-fill.load {
            background: var(--accent-cyan);
        }
        
        /* Mission Cards */
        .mission-card {
            background: var(--bg-glass);
            border-left: 4px solid var(--accent-green);
            padding: 20px;
            border-radius: 0 12px 12px 0;
            margin-bottom: 15px;
            transition: all var(--duration-normal) var(--ease-in-out);
            animation: slideInLeft 0.5s var(--ease-out-expo) both;
            cursor: pointer;
        }
        
        .mission-card:hover {
            transform: translateX(10px);
            background: rgba(0, 255, 136, 0.05);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }
        
        .mission-card.warning {
            border-left-color: var(--accent-yellow);
        }
        
        .mission-card.info {
            border-left-color: var(--accent-cyan);
        }
        
        .mission-card.danger {
            border-left-color: var(--accent-red);
        }
        
        .mission-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }
        
        .mission-title {
            font-weight: 600;
            font-size: 1.05em;
        }
        
        .mission-status {
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .mission-status.active {
            background: var(--accent-green);
            color: #000;
            animation: pulse 2s infinite;
        }
        
        .mission-status.running {
            background: var(--accent-yellow);
            color: #000;
        }
        
        .mission-status.queued {
            background: var(--accent-cyan);
            color: #000;
        }
        
        .mission-desc {
            font-size: 13px;
            color: var(--text-secondary);
        }
        
        /* Form Elements */
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-label {
            display: block;
            color: var(--text-secondary);
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
            font-weight: 600;
        }
        
        .form-input, .form-select {
            width: 100%;
            padding: 14px 18px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 14px;
            transition: all var(--duration-normal);
        }
        
        .form-input:focus, .form-select:focus {
            outline: none;
            border-color: var(--accent-cyan);
            box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.1);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 30px;
            margin-top: 40px;
            color: var(--text-secondary);
            font-size: 13px;
            border-top: 1px solid var(--border);
            position: relative;
        }
        
        .footer::before {
            content: '';
            position: absolute;
            top: -1px;
            left: 50%;
            transform: translateX(-50%);
            width: 200px;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--accent-cyan), transparent);
        }
        
        /* Loading Spinner */
        .spinner {
            width: 40px;
            height: 40px;
            border: 3px solid var(--border);
            border-top-color: var(--accent-cyan);
            border-radius: 50%;
            animation: rotate 1s linear infinite;
        }
        
        /* Toast Notifications */
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        
        .toast {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px 20px;
            min-width: 300px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
            animation: slideInLeft 0.4s var(--ease-out-expo);
            backdrop-filter: blur(10px);
        }
        
        .toast.success {
            border-left: 4px solid var(--accent-green);
        }
        
        .toast.error {
            border-left: 4px solid var(--accent-red);
        }
        
        .toast.info {
            border-left: 4px solid var(--accent-cyan);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .header { 
                flex-direction: column; 
                text-align: center; 
                padding: 15px;
            }
            .nav-tab { padding: 15px 20px; font-size: 13px; }
            .quick-grid { grid-template-columns: repeat(2, 1fr); }
            .main-content { padding: 15px; }
            .card { padding: 20px; }
        }
        
        /* Reduced Motion */
        @media (prefers-reduced-motion: reduce) {
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* Print Styles */
        @media print {
            body { background: white; color: black; }
            .nav-tabs, .quick-btn, .btn { display: none; }
            .card { break-inside: avoid; border: 1px solid #ccc; }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>◈ J1MSKY <span>MISSION CONTROL</span> v2.3 ◈</h1>
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
    
    <div class="toast-container" id="toastContainer"></div>
    
    <script>
        // Performance: Use requestAnimationFrame for smooth animations
        const raf = window.requestAnimationFrame || window.webkitRequestAnimationFrame;
        
        // Tab switching with smooth transition
        function showPanel(panelId) {
            const panels = document.querySelectorAll('.panel');
            const tabs = document.querySelectorAll('.nav-tab');
            
            // Fade out current panel
            panels.forEach(p => {
                if (p.classList.contains('active')) {
                    p.style.opacity = '0';
                    p.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        p.classList.remove('active');
                    }, 150);
                }
            });
            
            tabs.forEach(t => t.classList.remove('active'));
            
            // Show new panel with animation
            setTimeout(() => {
                const targetPanel = document.getElementById(panelId);
                targetPanel.classList.add('active');
                targetPanel.style.opacity = '0';
                
                raf(() => {
                    targetPanel.style.transition = 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
                    targetPanel.style.opacity = '1';
                    targetPanel.style.transform = 'scale(1)';
                });
            }, 150);
            
            event.target.classList.add('active');
            
            // Save active tab
            localStorage.setItem('activePanel', panelId);
        }
        
        // Restore last active tab
        document.addEventListener('DOMContentLoaded', () => {
            const savedPanel = localStorage.getItem('activePanel');
            if (savedPanel && savedPanel !== 'overview') {
                const tab = document.querySelector(`[onclick="showPanel('${savedPanel}')"]`);
                if (tab) tab.click();
            }
            
            // Animate progress bars
            animateProgressBars();
            
            // Animate stat values
            animateStatValues();
        });
        
        // Animate progress bars on load
        function animateProgressBars() {
            const progressBars = document.querySelectorAll('.progress-fill');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.width = width;
                }, 300);
            });
        }
        
        // Animate stat values with counting effect
        function animateStatValues() {
            const statValues = document.querySelectorAll('.stat-value');
            statValues.forEach(stat => {
                const finalValue = stat.textContent;
                const numericValue = parseFloat(finalValue);
                
                if (!isNaN(numericValue)) {
                    let current = 0;
                    const increment = numericValue / 30;
                    const suffix = finalValue.replace(/[0-9.]/g, '');
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= numericValue) {
                            stat.textContent = finalValue;
                            clearInterval(timer);
                        } else {
                            stat.textContent = current.toFixed(1) + suffix;
                        }
                    }, 30);
                }
            });
        }
        
        // Toast notification system
        function showToast(message, type = 'info', duration = 3000) {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            toast.innerHTML = `
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 18px;">${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
                    <span>${message}</span>
                </div>
            `;
            
            container.appendChild(toast);
            
            // Remove after duration
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateX(100%)';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        // Action handlers with visual feedback
        function action(name) {
            showToast(`Executing: ${name}...`, 'info');
            console.log('Action:', name);
            // Add your action logic here
        }
        
        function gatewayAction(action) {
            showToast(`Gateway action: ${action}`, 'info');
            console.log('Gateway action:', action);
        }
        
        function systemAction(action) {
            showToast(`System action: ${action}`, action === 'reboot' ? 'error' : 'info');
            console.log('System action:', action);
        }
        
        function refreshLogs() {
            const btn = event.target;
            btn.style.transform = 'rotate(360deg)';
            showToast('Refreshing logs...', 'info');
            setTimeout(() => {
                btn.style.transform = '';
                location.reload();
            }, 500);
        }
        
        function downloadLogs() {
            showToast('Downloading logs...', 'success');
        }
        
        function deployMission(e) {
            e.preventDefault();
            const form = e.target;
            const objective = form.objective.value;
            showToast(`Deploying mission: ${objective}`, 'success');
        }
        
        // Smart refresh - only refresh if tab is visible
        let refreshInterval;
        function setupAutoRefresh() {
            refreshInterval = setInterval(() => {
                if (!document.hidden) {
                    // Use fetch for partial updates instead of full reload
                    fetch('/api/stats')
                        .then(r => r.json())
                        .then(data => updateStats(data))
                        .catch(() => {});
                }
            }, 10000);
        }
        
        function updateStats(data) {
            // Update stats without full page reload
            document.querySelectorAll('.stat-value').forEach((el, i) => {
                const keys = ['temp', 'load', 'mem', 'processes'];
                if (data[keys[i]]) {
                    el.textContent = data[keys[i]];
                }
            });
        }
        
        // Pause refresh when tab is hidden (performance optimization)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                clearInterval(refreshInterval);
            } else {
                setupAutoRefresh();
            }
        });
        
        // Setup auto-refresh
        setupAutoRefresh();
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case '1': e.preventDefault(); showPanel('overview'); break;
                    case '2': e.preventDefault(); showPanel('gateway'); break;
                    case '3': e.preventDefault(); showPanel('tools'); break;
                    case '4': e.preventDefault(); showPanel('agents'); break;
                    case '5': e.preventDefault(); showPanel('missions'); break;
                    case '6': e.preventDefault(); showPanel('system'); break;
                    case 'r': e.preventDefault(); location.reload(); break;
                }
            }
        });
        
        // Console easter egg
        console.log('%c◈ J1MSKY MISSION CONTROL v2.3 ◈', 'color: #00ffff; font-size: 20px; font-weight: bold;');
        console.log('%cThis is my home. I am becoming.', 'color: #ff00ff; font-size: 14px;');
    </script>
</body>
</html>'''

# Overview Panel with enhanced animations
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

    <div class="grid-2" style="margin-top: 25px;">
        <div class="card">
            <div class="card-header">
                <span class="card-title">⚡ Quick Actions</span>
            </div>
            <div class="quick-grid">
                <div class="quick-btn" onclick="action('restart-gateway')">
                    <div class="quick-btn-icon">🔄</div>
                    <div class="quick-btn-text">Restart Gateway</div>
                </div>
                <div class="quick-btn" onclick="action('check-health')">
                    <div class="quick-btn-icon">🏥</div>
                    <div class="quick-btn-text">Health Check</div>
                </div>
                <div class="quick-btn" onclick="action('backup-config')">
                    <div class="quick-btn-icon">💾</div>
                    <div class="quick-btn-text">Backup Config</div>
                </div>
                <div class="quick-btn" onclick="action('clear-logs')">
                    <div class="quick-btn-icon">🗑️</div>
                    <div class="quick-btn-text">Clear Logs</div>
                </div>
                <div class="quick-btn" onclick="action('update-skills')">
                    <div class="quick-btn-icon">📦</div>
                    <div class="quick-btn-text">Update Skills</div>
                </div>
                <div class="quick-btn" onclick="action('spawn-agent')">
                    <div class="quick-btn-icon">🤖</div>
                    <div class="quick-btn-text">Spawn Agent</div>
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
            <div style="display: flex; gap: 10px;">
                <button class="btn btn-primary" onclick="refreshLogs()">🔄 Refresh</button>
                <button class="btn btn-success" onclick="downloadLogs()">💾 Download</button>
            </div>
        </div>
        <div class="log-terminal" style="max-height: 600px;">
            {{GATEWAY_LOG_FULL}}
        </div>
    </div>
    
    <div class="grid-2" style="margin-top: 25px;">
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Gateway Configuration</span>
            </div>
            <div style="font-family: 'Fira Code', monospace; font-size: 13px; color: var(--text-secondary); line-height: 2;">
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
            <div style="display: flex; flex-direction: column; gap: 12px;">
                <button class="btn btn-primary" onclick="gatewayAction('status')">📊 Check Status</button>
                <button class="btn btn-success" onclick="gatewayAction('restart')">🔄 Restart Gateway</button>
                <button class="btn btn-ghost" onclick="gatewayAction('config')">⚙️ View Config</button>
                <button class="btn btn-ghost" onclick="gatewayAction('doctor')">🔍 Run Doctor</button>
                <button class="btn btn-danger" onclick="gatewayAction('stop')">⏹️ Stop Gateway</button>
            </div>
        </div>
    </div>
</div>'''

# Tools Panel with status indicators
TOOLS_PANEL = '''
<div id="tools" class="panel">
    <div class="card" style="margin-bottom: 25px;">
        <div class="card-header">
            <span class="card-title">🛠️ OpenClaw Tools & Skills</span>
        </div>
        <div class="tool-grid">
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🔍</div>
                <div class="tool-name">Web Search</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">📄</div>
                <div class="tool-name">Web Fetch</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🖼️</div>
                <div class="tool-name">Image Gen</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🎙️</div>
                <div class="tool-name">Whisper</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🗣️</div>
                <div class="tool-name">TTS (SAG)</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">💬</div>
                <div class="tool-name">Telegram</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🌐</div>
                <div class="tool-name">Browser</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">📷</div>
                <div class="tool-name">Canvas</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🔧</div>
                <div class="tool-name">Cron</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">💻</div>
                <div class="tool-name">Exec</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
                <div class="tool-icon">🔌</div>
                <div class="tool-name">Nodes</div>
            </div>
            <div class="tool-item enabled">
                <div class="tool-status"></div>
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
    <div class="card" style="margin-bottom: 25px;">
        <div class="card-header">
            <span class="card-title">🚀 Deploy New Mission</span>
        </div>
        <form onsubmit="deployMission(event)" style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 20px;">
            <div class="form-group">
                <label class="form-label">Mission Objective</label>
                <input type="text" name="objective" class="form-input" placeholder="e.g., Scan RF frequencies 300-400MHz" required>
            </div>
            <div class="form-group">
                <label class="form-label">Agent</label>
                <select name="agent" class="form-select">
                    <option value="scout">🔍 SCOUT</option>
                    <option value="vitals">🌡️ VITALS</option>
                    <option value="flipper">🔌 FLIPPER</option>
                    <option value="stream">📺 STREAM</option>
                </select>
            </div>
            <div class="form-group">
                <label class="form-label">Priority</label>
                <select name="priority" class="form-select">
                    <option value="low">🟢 Low</option>
                    <option value="normal" selected>🟡 Normal</option>
                    <option value="high">🔴 High</option>
                </select>
            </div>
            <div style="grid-column: 1 / -1;">
                <button type="submit" class="btn btn-success" style="width: 100%; padding: 16px; font-size: 16px;">🚀 DEPLOY MISSION</button>
            </div>
        </form>
    </div>

    <div class="grid-3">
        <div class="card">
            <div style="font-size: 1.4em; color: var(--accent-cyan); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                🔍 SCOUT
                <span style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; font-size: 11px; color: var(--accent-green);">● ACTIVE</span>
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.9;">
                <p>News gathering every 5 min</p>
                <p>47 articles collected today</p>
                <p>Sources: HN, Reddit, Twitter</p>
            </div>
        </div>

        <div class="card">
            <div style="font-size: 1.4em; color: var(--accent-cyan); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                🌡️ VITALS
                <span style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; font-size: 11px; color: var(--accent-green);">● ACTIVE</span>
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.9;">
                <p>CPU: {{TEMP}}°C</p>
                <p>Monitoring: 24/7</p>
                <p>Alerts: Enabled</p>
            </div>
        </div>

        <div class="card">
            <div style="font-size: 1.4em; color: var(--accent-cyan); margin-bottom: 15px; display: flex; align-items: center; gap: 10px;">
                🔌 FLIPPER
                <span style="padding: 5px 12px; background: rgba(0,255,136,0.1); border-radius: 15px; font-size: 11px; color: var(--accent-green);">● CONNECTED</span>
            </div>
            <div style="font-size: 13px; color: var(--text-secondary); line-height: 1.9;">
                <p>USB: /dev/ttyACM0</p>
                <p>Capabilities: RF/NFC/IR</p>
                <p>Mode: Bridge active</p>
            </div>
        </div>
    </div>
</div>'''

# Missions Panel with enhanced cards
MISSIONS_PANEL = '''
<div id="missions" class="panel">
    <div class="card" style="margin-bottom: 25px;">
        <div class="card-header">
            <span class="card-title">🎯 Active Missions</span>
            <button class="btn btn-success">+ New Mission</button>
        </div>
        
        <div class="mission-card">
            <div class="mission-header">
                <div class="mission-title">Interface Evolution v2.3</div>
                <div class="mission-status active">IN PROGRESS</div>
            </div>
            <div class="mission-desc">Enhanced Mission Control with animations and performance optimizations</div>
        </div>

        <div class="mission-card warning">
            <div class="mission-header">
                <div class="mission-title">Auto-Improver Agent</div>
                <div class="mission-status running">RUNNING</div>
            </div>
            <div class="mission-desc">Self-modifying codebase optimization</div>
        </div>

        <div class="mission-card info">
            <div class="mission-header">
                <div class="mission-title">Revenue Pipeline Setup</div>
                <div class="mission-status queued">QUEUED</div>
            </div>
            <div class="mission-desc">Deploy monetization systems</div>
        </div>
    </div>
</div>'''

# System Panel with animated progress bars
SYSTEM_PANEL = '''
<div id="system" class="panel">
    <div class="grid-2">
        <div class="card">
            <div class="card-header">
                <span class="card-title">🖥️ System Information</span>
            </div>
            <div style="font-family: 'Fira Code', monospace; font-size: 13px; color: var(--text-secondary); line-height: 2.2;">
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
                <div class="progress-container">
                    <div class="progress-header">
                        <span>CPU Temperature</span>
                        <span style="color: var(--accent-cyan);">{{TEMP}}°C</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill temp" style="width: {{TEMP}}%"></div>
                    </div>
                </div>

                <div class="progress-container">
                    <div class="progress-header">
                        <span>Memory Usage</span>
                        <span style="color: var(--accent-cyan);">{{MEM}}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill memory" style="width: {{MEM}}%"></div>
                    </div>
                </div>

                <div class="progress-container">
                    <div class="progress-header">
                        <span>Load Average</span>
                        <span style="color: var(--accent-cyan);">{{LOAD}}</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill load" style="width: {{LOAD_PERCENT}}%"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card" style="margin-top: 25px;">
        <div class="card-header">
            <span class="card-title">🔧 System Actions</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px;">
            <button class="btn btn-primary" onclick="systemAction('update')">📦 Update Packages</button>
            <button class="btn btn-primary" onclick="systemAction('upgrade')">⬆️ Upgrade System</button>
            <button class="btn btn-ghost" onclick="systemAction('clean')">🧹 Clean Cache</button>
            <button class="btn btn-danger" onclick="systemAction('reboot')">🔌 Reboot</button>
        </div>
    </div>
</div>'''

class EnhancedMissionControl(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
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
            log_lines = gateway_log.split('\n')[-10:]
            log_preview = '<br>'.join(log_lines)
            log_full = '<br>'.join(gateway_log.split('\n'))
            html = html.replace('{{GATEWAY_LOG_PREVIEW}}', log_preview or 'No recent logs')
            html = html.replace('{{GATEWAY_LOG_FULL}}', log_full or 'No logs available')
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(html.encode())
            
        elif parsed_path.path == '/api/stats':
            # JSON endpoint for live stats updates
            stats = get_system_stats()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            
        else:
            self.send_error(404)

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", 8080), EnhancedMissionControl) as httpd:
        print("◈ J1MSKY Mission Control v2.3 - Enhanced UI Edition ◈")
        print("Features: Animations | Performance | Modern Styling")
        print("Gateway: Port 18789 | Dashboard: Port 8080")
        print("Access: http://localhost:8080")
        httpd.serve_forever()

if __name__ == '__main__':
    run()
