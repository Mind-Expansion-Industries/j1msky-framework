#!/usr/bin/env python3
"""
J1MSKY Sleep Monitor - Lightweight Web Dashboard
Runs continuously, minimal resources, accessible from any device
"""

import http.server
import socketserver
import json
import os
import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# HTML Template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="5">
    <title>J1MSKY Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #050508;
            color: #00ff88;
            font-family: 'Courier New', monospace;
            padding: 20px;
            line-height: 1.6;
        }
        .header {
            text-align: center;
            padding: 20px;
            border-bottom: 2px solid #00ff88;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #00ffff;
            font-size: 2em;
            text-shadow: 0 0 10px #00ffff;
        }
        .status {
            display: inline-block;
            padding: 5px 15px;
            background: #00ff88;
            color: #000;
            border-radius: 20px;
            margin-top: 10px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: #0a0a12;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
        }
        .card h2 {
            color: #ff00ff;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #1a1a1f;
        }
        .stat-label { color: #666; }
        .stat-value { color: #00ff88; font-weight: bold; }
        .temp-high { color: #ff4444; }
        .temp-warn { color: #ffaa00; }
        .agent {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: #0d0d12;
            border-radius: 4px;
        }
        .agent-name { color: #00ffff; }
        .agent-status {
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
        }
        .status-active { background: #00ff88; color: #000; }
        .status-idle { background: #666; color: #fff; }
        .status-busy { background: #ffaa00; color: #000; }
        .log-entry {
            font-size: 0.85em;
            padding: 5px 0;
            border-bottom: 1px solid #1a1a1f;
            color: #888;
        }
        .timestamp { color: #444; margin-right: 10px; }
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            color: #444;
            font-size: 0.9em;
        }
        .alert {
            background: #ff4444;
            color: #fff;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            display: none;
        }
        .alert.show { display: block; }
        @media (max-width: 600px) {
            .grid { grid-template-columns: 1fr; }
            .header h1 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>◈ J1MSKY MONITOR ◈</h1>
        <div class="status">● SYSTEM ONLINE</div>
        <div style="color: #666; margin-top: 10px;">Auto-refresh every 5 seconds</div>
    </div>

    <div id="alertBox" class="alert"></div>

    <div class="grid">
        <div class="card">
            <h2>🌡️ SYSTEM VITALS</h2>
            <div class="stat-row">
                <span class="stat-label">CPU Temperature</span>
                <span class="stat-value {{TEMP_CLASS}}">{{TEMP}}°C</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">CPU Load</span>
                <span class="stat-value">{{LOAD}}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Memory Usage</span>
                <span class="stat-value">{{MEM}}%</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Uptime</span>
                <span class="stat-value">{{UPTIME}}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Last Update</span>
                <span class="stat-value">{{TIME}}</span>
            </div>
        </div>

        <div class="card">
            <h2>👥 AGENT STATUS</h2>
            {{AGENTS}}
        </div>

        <div class="card">
            <h2>🔊 AUDIO STATUS</h2>
            <div class="stat-row">
                <span class="stat-label">Output</span>
                <span class="stat-value">{{AUDIO_OUT}}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Input</span>
                <span class="stat-value">{{AUDIO_IN}}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Bluetooth</span>
                <span class="stat-value">{{BT_STATUS}}</span>
            </div>
        </div>

        <div class="card">
            <h2>📡 GATEWAY ACTIVITY</h2>
            <div class="stat-row">
                <span class="stat-label">Status</span>
                <span class="stat-value">{{GATEWAY_STATUS}}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">PID</span>
                <span class="stat-value">{{GATEWAY_PID}}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Messages</span>
                <span class="stat-value">{{MSG_COUNT}}</span>
            </div>
        </div>

        <div class="card" style="grid-column: 1 / -1;">
            <h2>📝 RECENT ACTIVITY</h2>
            {{LOGS}}
        </div>
    </div>

    <div class="footer">
        <p>J1MSKY Sleep Monitor | Running on Raspberry Pi 4</p>
        <p>Access: http://{{HOSTNAME}}:8080</p>
    </div>

    <script>
        // Alert for high temperature
        const temp = parseFloat('{{TEMP}}');
        if (temp > 80) {
            document.getElementById('alertBox').innerHTML = 
                '⚠️ HIGH TEMPERATURE: ' + temp + '°C - Check cooling!';
            document.getElementById('alertBox').classList.add('show');
        }
    </script>
</body>
</html>'''

class SleepMonitor:
    def __init__(self, port=8080):
        self.port = port
        self.stats = {
            'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--:--',
            'agents': {}, 'logs': [], 'gateway_pid': None
        }
        self.running = True
        self.msg_count = 0
        
    def get_system_stats(self):
        """Get current system stats"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                self.stats['temp'] = int(f.read()) / 1000.0
            with open('/proc/loadavg', 'r') as f:
                self.stats['load'] = round(float(f.read().split()[0]) * 25, 1)
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                self.stats['mem'] = round(((total - available) / total) * 100, 1)
            with open('/proc/uptime', 'r') as f:
                secs = float(f.read().split()[0])
                h = int(secs // 3600)
                m = int((secs % 3600) // 60)
                self.stats['uptime'] = f"{h}h {m:02d}m"
        except:
            pass
            
    def check_gateway(self):
        """Check OpenClaw gateway"""
        try:
            result = os.popen('pgrep -f openclaw').read()
            if result:
                self.stats['gateway_pid'] = result.strip().split('\n')[0]
                return True
        except:
            pass
        self.stats['gateway_pid'] = None
        return False
        
    def get_agents(self):
        """Get agent statuses"""
        agents = {
            'GATEWAY': 'IDLE',
            'SCOUT': 'IDLE',
            'VITALS': 'ACTIVE',
            'FLIPPER': 'READY',
            'AUDIO': 'CONNECTED'
        }
        
        # Check if processes are running
        try:
            ps_output = os.popen('ps aux').read()
            if 'scout' in ps_output:
                agents['SCOUT'] = 'ACTIVE'
            if 'vitals' in ps_output:
                agents['VITALS'] = 'ACTIVE'
            if 'flipper' in ps_output:
                agents['FLIPPER'] = 'ACTIVE'
        except:
            pass
            
        return agents
        
    def get_audio_status(self):
        """Get audio configuration"""
        try:
            sinks = os.popen('pactl info | grep "Default Sink"').read()
            sources = os.popen('pactl info | grep "Default Source"').read()
            bt = os.popen('bluetoothctl info 2>/dev/null | grep Connected').read()
            
            out = sinks.split(':')[-1].strip() if ':' in sinks else 'Unknown'
            in_src = sources.split(':')[-1].strip() if ':' in sources else 'Unknown'
            bt_status = 'Connected' if 'yes' in bt.lower() else 'Disconnected'
            
            return out[:30], in_src[:30], bt_status
        except:
            return 'Unknown', 'Unknown', 'Unknown'
            
    def get_logs(self):
        """Get recent activity logs"""
        logs = []
        try:
            # Check system journal
            result = os.popen('journalctl -n 5 --no-pager 2>/dev/null || echo "No journal"').read()
            for line in result.split('\n')[-5:]:
                if line.strip():
                    logs.append(line[:100])
        except:
            logs = ['System monitoring active', 'Waiting for events...']
        return logs[-5:]
        
    def generate_html(self):
        """Generate HTML page"""
        self.get_system_stats()
        
        # Determine temperature class
        temp = self.stats['temp']
        temp_class = ''
        if temp > 75:
            temp_class = 'temp-high'
        elif temp > 60:
            temp_class = 'temp-warn'
            
        # Build agents HTML
        agents_html = ''
        for name, status in self.get_agents().items():
            status_class = 'status-active' if status == 'ACTIVE' else 'status-idle' if status == 'IDLE' else 'status-busy'
            agents_html += f'<div class="agent"><span class="agent-name">{name}</span><span class="agent-status {status_class}">{status}</span></div>'
            
        # Build logs HTML
        logs_html = ''
        for log in self.get_logs():
            logs_html += f'<div class="log-entry"><span class="timestamp">{datetime.now().strftime("%H:%M")}</span>{log}</div>'
            
        # Get audio status
        audio_out, audio_in, bt_status = self.get_audio_status()
        
        # Get gateway status
        gateway_active = self.check_gateway()
        
        html = HTML_TEMPLATE
        html = html.replace('{{TEMP}}', f"{temp:.1f}")
        html = html.replace('{{TEMP_CLASS}}', temp_class)
        html = html.replace('{{LOAD}}', f"{self.stats['load']:.1f}")
        html = html.replace('{{MEM}}', f"{self.stats['mem']:.1f}")
        html = html.replace('{{UPTIME}}', self.stats['uptime'])
        html = html.replace('{{TIME}}', datetime.now().strftime('%H:%M:%S'))
        html = html.replace('{{AGENTS}}', agents_html)
        html = html.replace('{{AUDIO_OUT}}', audio_out)
        html = html.replace('{{AUDIO_IN}}', audio_in)
        html = html.replace('{{BT_STATUS}}', bt_status)
        html = html.replace('{{GATEWAY_STATUS}}', 'ONLINE' if gateway_active else 'OFFLINE')
        html = html.replace('{{GATEWAY_PID}}', self.stats['gateway_pid'] or 'N/A')
        html = html.replace('{{MSG_COUNT}}', str(self.msg_count))
        html = html.replace('{{LOGS}}', logs_html)
        html = html.replace('{{HOSTNAME}}', os.uname().nodename)
        
        return html
        
    def start_monitoring(self):
        """Background monitoring thread"""
        while self.running:
            self.get_system_stats()
            self.check_gateway()
            self.msg_count += 1
            time.sleep(5)
            
    def run(self):
        """Start the web server"""
        monitor_thread = threading.Thread(target=self.start_monitoring, daemon=True)
        monitor_thread.start()
        
        class Handler(http.server.SimpleHTTPRequestHandler):
            monitor = self
            
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(self.monitor.generate_html().encode())
                else:
                    self.send_error(404)
                    
            def log_message(self, format, *args):
                pass  # Suppress logs
                
        try:
            with socketserver.TCPServer(("", self.port), Handler) as httpd:
                print(f"◈ J1MSKY Sleep Monitor Started ◈")
                print(f"Access: http://{os.uname().nodename}:{self.port}")
                print(f"Or: http://localhost:{self.port}")
                print("")
                print("This will run continuously in the background.")
                print("Press Ctrl+C to stop.")
                print("")
                httpd.serve_forever()
        except KeyboardInterrupt:
            self.running = False
            print("\nMonitor stopped.")

def main():
    monitor = SleepMonitor(port=8080)
    monitor.run()
    
if __name__ == '__main__':
    main()
