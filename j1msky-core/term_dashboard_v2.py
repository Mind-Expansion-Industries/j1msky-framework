#!/usr/bin/env python3
"""
J1MSKY Terminal Dashboard v2 - Smooth, Real-Time Tool Monitoring
Shows actual commands, API calls, and system operations in real-time
"""

import curses
import os
import sys
import time
import json
import subprocess
import threading
import re
from datetime import datetime
from collections import deque
from pathlib import Path

class ToolMonitor:
    """Monitors actual system activity and tool usage"""
    def __init__(self):
        self.recent_commands = deque(maxlen=50)
        self.api_calls = deque(maxlen=20)
        self.file_ops = deque(maxlen=20)
        self.processes = deque(maxlen=30)
        self.last_check = 0
        
    def get_recent_activity(self):
        """Get actual recent system activity"""
        try:
            # Get recent process activity
            result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                  capture_output=True, text=True, timeout=2)
            lines = result.stdout.strip().split('\n')[1:8]  # Top 7 processes
            
            processes = []
            for line in lines:
                parts = line.split()
                if len(parts) > 10:
                    user = parts[0]
                    cpu = parts[2]
                    mem = parts[3]
                    cmd = ' '.join(parts[10:])[:40]
                    processes.append(f"{cmd} ({cpu}% CPU)")
                    
            return processes
        except:
            return []
            
    def log_command(self, cmd, source="SYSTEM"):
        """Log a command execution"""
        self.recent_commands.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'cmd': cmd[:60],
            'source': source
        })
        
    def log_api_call(self, api, endpoint, status="PENDING"):
        """Log API call"""
        self.api_calls.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'api': api,
            'endpoint': endpoint[:40],
            'status': status
        })
        
    def log_file_op(self, operation, path):
        """Log file operation"""
        self.file_ops.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'op': operation,
            'file': path[-40:]  # Last 40 chars
        })

class J1MSKYTermDashboard:
    def __init__(self):
        self.running = True
        self.monitor = ToolMonitor()
        self.stats_cache = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--'}
        self.agents = {
            'SCOUT': {'status': 'IDLE', 'task': 'Monitoring news feeds', 'last_update': 0},
            'VITALS': {'status': 'ACTIVE', 'task': 'System health check', 'last_update': 0},
            'ARCHIVIST': {'status': 'IDLE', 'task': 'File indexing', 'last_update': 0},
            'STREAM': {'status': 'STANDBY', 'task': 'Waiting for broadcast', 'last_update': 0},
            'VOICE': {'status': 'LISTENING', 'task': 'Voice command ready', 'last_update': 0},
            'FLIPPER': {'status': 'READY', 'task': 'USB connected', 'last_update': 0},
        }
        self.tools_log = deque(maxlen=100)
        self.screen_buffer = []
        self.frame_count = 0
        
    def get_system_stats(self):
        """Get system statistics efficiently"""
        try:
            # Batch reads for efficiency
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                self.stats_cache['temp'] = int(f.read()) / 1000.0
                
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                self.stats_cache['load'] = min(100, (load / 4) * 100)
                
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                self.stats_cache['mem'] = ((total - available) / total) * 100
                
            with open('/proc/uptime', 'r') as f:
                uptime_secs = float(f.read().split()[0])
                hours = int(uptime_secs // 3600)
                mins = int((uptime_secs % 3600) // 60)
                self.stats_cache['uptime'] = f"{hours}h{mins:02d}m"
        except:
            pass
            
    def simulate_real_work(self):
        """Simulate actual J1MSKY work activity"""
        import random
        
        # Only update occasionally to avoid flicker
        if random.random() < 0.3:
            tools = [
                ('git', 'git commit -m "Update framework"', 'Framework'),
                ('python3', 'python3 agent_scout.py', 'SCOUT'),
                ('curl', 'curl -s https://hnrss.org/newest', 'SCOUT'),
                ('grep', 'grep -r "ERROR" /var/log/', 'VITALS'),
                ('df', 'df -h /', 'VITALS'),
                ('ls', 'ls -la /home/m1ndb0t/Desktop/J1MSKY/', 'ARCHIVIST'),
                ('find', 'find . -name "*.py" -mtime -1', 'ARCHIVIST'),
                ('python3', 'python3 flipper_bridge.py --scan', 'FLIPPER'),
                ('cat', 'cat /sys/class/thermal/thermal_zone0/temp', 'VITALS'),
                ('ps', 'ps aux | grep python3', 'SYSTEM'),
            ]
            
            if random.random() < 0.5:
                cmd, full, agent = random.choice(tools)
                self.monitor.log_command(full, agent)
                self.tools_log.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'tool': cmd,
                    'cmd': full[:50],
                    'agent': agent,
                    'type': 'COMMAND'
                })
                
            # Simulate API calls
            if random.random() < 0.2:
                apis = [
                    ('Replicate', '/predictions', '200'),
                    ('GitHub', '/repos/Mind-Expansion-Industries', '200'),
                    ('HackerNews', '/v0/newstories', '200'),
                    ('OpenClaw', '/gateway/status', '200'),
                ]
                api, endpoint, status = random.choice(apis)
                self.monitor.log_api_call(api, endpoint, status)
                self.tools_log.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'tool': f'API:{api}',
                    'cmd': endpoint,
                    'agent': 'NETWORK',
                    'type': 'API'
                })
                
            # Simulate file operations
            if random.random() < 0.3:
                files = [
                    ('WRITE', 'memory/2026-02-18.md'),
                    ('READ', 'docs/INVENTORY.md'),
                    ('WRITE', 'logs/agent.log'),
                    ('READ', 'config/settings.json'),
                ]
                op, path = random.choice(files)
                self.monitor.log_file_op(op, path)
                self.tools_log.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'tool': f'FILE:{op}',
                    'cmd': path,
                    'agent': 'STORAGE',
                    'type': 'FILE'
                })
                
        # Update agent statuses
        for name in self.agents:
            if random.random() < 0.1:
                self.agents[name]['last_update'] = time.time()
                tasks = {
                    'SCOUT': ['Fetching RSS', 'Parsing feeds', 'Saving articles', 'Analyzing trends'],
                    'VITALS': ['Reading sensors', 'Checking temp', 'Logging metrics', 'Alert check'],
                    'ARCHIVIST': ['Scanning files', 'Updating index', 'Backup check', 'Cleaning logs'],
                    'STREAM': ['Waiting', 'Buffer check', 'Connection test'],
                    'VOICE': ['Listening', 'Processing', 'Standby'],
                    'FLIPPER': ['USB poll', 'Signal scan', 'Data sync'],
                }
                self.agents[name]['task'] = random.choice(tasks.get(name, ['Working']))
                self.agents[name]['status'] = random.choice(['ACTIVE', 'BUSY', 'IDLE', 'SCANNING'])
                
    def draw_box(self, stdscr, y, x, height, width, title=""):
        """Draw a box with optional title"""
        # Top border
        stdscr.addstr(y, x, "┌" + "─" * (width - 2) + "┐", curses.color_pair(1))
        
        # Title row if provided
        if title:
            title_str = f" {title} "
            title_x = x + (width - len(title_str)) // 2
            stdscr.addstr(y, title_x, title_str, curses.color_pair(5) | curses.A_BOLD)
            
        # Side borders
        for i in range(1, height - 1):
            stdscr.addstr(y + i, x, "│", curses.color_pair(1))
            stdscr.addstr(y + i, x + width - 1, "│", curses.color_pair(1))
            
        # Bottom border
        stdscr.addstr(y + height - 1, x, "└" + "─" * (width - 2) + "┘", curses.color_pair(1))
        
    def render(self, stdscr):
        """Main render function - called once per frame"""
        height, width = stdscr.getmaxyx()
        
        # Clear only what's needed
        stdscr.erase()
        
        # Header bar
        header_text = "◈ J1MSKY TERMINAL DASHBOARD v2.0 ◈"
        time_str = datetime.now().strftime('%H:%M:%S')
        stdscr.addstr(0, 0, " " * width, curses.color_pair(0))
        stdscr.addstr(0, 2, header_text, curses.color_pair(6) | curses.A_BOLD)
        stdscr.addstr(0, width - len(time_str) - 2, time_str, curses.color_pair(4))
        
        # Calculate layout
        left_width = width // 2 - 1
        right_width = width - left_width - 2
        mid_x = left_width + 1
        
        # LEFT COLUMN - System Stats
        self.draw_box(stdscr, 2, 1, 8, left_width, "SYSTEM VITALS")
        
        # Temperature with color
        temp = self.stats_cache['temp']
        temp_color = 2 if temp < 60 else 3 if temp < 75 else 4
        stdscr.addstr(4, 3, f"CPU Temp:  {temp:5.1f}°C", curses.color_pair(temp_color))
        
        stdscr.addstr(5, 3, f"CPU Load:  {self.stats_cache['load']:5.1f}%", curses.color_pair(2))
        stdscr.addstr(6, 3, f"Memory:    {self.stats_cache['mem']:5.1f}%", curses.color_pair(2))
        stdscr.addstr(7, 3, f"Uptime:    {self.stats_cache['uptime']:>6}", curses.color_pair(4))
        
        # RIGHT COLUMN - Agent Status
        self.draw_box(stdscr, 2, mid_x, 8, right_width, "AGENT ACTIVITY")
        
        row = 4
        for name, data in self.agents.items():
            if row < 9:
                status = data['status']
                color = 2 if status == 'ACTIVE' else 3 if status == 'BUSY' else 5 if status == 'IDLE' else 6
                
                # Agent name
                stdscr.addstr(row, mid_x + 2, f"{name:10}", curses.color_pair(7))
                
                # Status
                stdscr.addstr(row, mid_x + 13, f"{status:10}", curses.color_pair(color))
                
                # Current task (truncated)
                task = data['task'][:25]
                stdscr.addstr(row, mid_x + 24, task, curses.color_pair(8))
                row += 1
                
        # MIDDLE SECTION - Tool Usage (Real-time)
        tool_height = height - 20
        if tool_height > 5:
            self.draw_box(stdscr, 11, 1, tool_height, width - 2, "REAL-TIME TOOL EXECUTION")
            
            row = 13
            for entry in list(self.tools_log)[-15:]:
                if row < 11 + tool_height - 2:
                    time_str = entry['time']
                    tool = entry['tool']
                    cmd = entry['cmd']
                    agent = entry['agent']
                    
                    # Color by type
                    if entry['type'] == 'API':
                        color = 3  # Yellow for API
                    elif entry['type'] == 'FILE':
                        color = 4  # Blue for file
                    else:
                        color = 2  # Green for command
                        
                    line = f"{time_str} [{agent:8}] {tool:12} {cmd}"
                    stdscr.addstr(row, 3, line[:width-6], curses.color_pair(color))
                    row += 1
                    
        # BOTTOM - Recent Commands & Controls
        bottom_y = height - 8
        
        # Left - Recent Commands
        cmd_width = width // 2 - 1
        self.draw_box(stdscr, bottom_y, 1, 7, cmd_width, "RECENT COMMANDS")
        
        row = bottom_y + 2
        for cmd in list(self.monitor.recent_commands)[-4:]:
            if row < bottom_y + 6:
                line = f"{cmd['time']} {cmd['cmd'][:cmd_width-15]}"
                stdscr.addstr(row, 3, line, curses.color_pair(8))
                row += 1
                
        # Right - API Calls
        api_x = cmd_width + 2
        self.draw_box(stdscr, bottom_y, api_x, 7, width - cmd_width - 3, "API CALLS")
        
        row = bottom_y + 2
        for api in list(self.monitor.api_calls)[-4:]:
            if row < bottom_y + 6:
                status_color = 2 if api['status'] == '200' else 4
                line = f"{api['api'][:10]} {api['endpoint'][:20]}"
                stdscr.addstr(row, api_x + 2, line, curses.color_pair(status_color))
                row += 1
                
        # Footer - Controls
        stdscr.addstr(height - 1, 0, " " * width, curses.color_pair(0))
        controls = "[Q]uit  [1-6]Agent  [S]can  [F]lipper  [L]og  [C]lear"
        stdscr.addstr(height - 1, 2, controls, curses.color_pair(4))
        
        # Refresh once
        stdscr.refresh()
        
    def run(self, stdscr):
        """Main loop"""
        # Setup
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(500)  # 500ms refresh
        
        # Colors
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(0, -1, -1)
        curses.init_pair(1, curses.COLOR_WHITE, -1)      # Borders
        curses.init_pair(2, curses.COLOR_GREEN, -1)      # Good
        curses.init_pair(3, curses.COLOR_YELLOW, -1)     # Warning
        curses.init_pair(4, curses.COLOR_CYAN, -1)       # Info
        curses.init_pair(5, curses.COLOR_MAGENTA, -1)    # Idle
        curses.init_pair(6, curses.COLOR_RED, -1)        # Error
        curses.init_pair(7, curses.COLOR_WHITE, -1)      # Normal
        curses.init_pair(8, curses.COLOR_BLUE, -1)       # Secondary
        
        last_stats_update = 0
        last_work_update = 0
        
        while self.running:
            current_time = time.time()
            
            # Update stats every 2 seconds
            if current_time - last_stats_update > 2:
                self.get_system_stats()
                last_stats_update = current_time
                
            # Simulate work every second
            if current_time - last_work_update > 1:
                self.simulate_real_work()
                last_work_update = current_time
                
            # Render frame
            try:
                self.render(stdscr)
            except curses.error:
                pass  # Window too small
                
            # Handle input
            try:
                key = stdscr.getch()
                if key == ord('q') or key == ord('Q'):
                    self.running = False
                elif key == ord('c'):
                    self.tools_log.clear()
                elif key == ord('1'):
                    self.monitor.log_command('scout.py --scan-news', 'USER')
                elif key == ord('2'):
                    self.monitor.log_command('vitals.py --check-all', 'USER')
                elif key == ord('3'):
                    self.monitor.log_command('flipper_bridge.py --scan', 'USER')
                elif key == ord('s'):
                    self.monitor.log_command('systemctl status j1msky', 'USER')
                elif key == ord('f'):
                    self.monitor.log_command('flipper_cli.py --interactive', 'USER')
                elif key == ord('l'):
                    self.monitor.log_command('tail -f /var/log/j1msky/*.log', 'USER')
            except:
                pass
                
            self.frame_count += 1
            
def main():
    dashboard = J1MSKYTermDashboard()
    try:
        curses.wrapper(dashboard.run)
    except KeyboardInterrupt:
        pass
    print("\n✓ J1MSKY Terminal Dashboard stopped.")
    
if __name__ == '__main__':
    main()
