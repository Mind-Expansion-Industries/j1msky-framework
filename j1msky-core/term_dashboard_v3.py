#!/usr/bin/env python3
"""
J1MSKY Terminal Dashboard v3 - Gateway Connected
Shows real OpenClaw gateway activity and tool usage
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

class GatewayMonitor:
    """Monitors OpenClaw gateway for real activity"""
    def __init__(self):
        self.gateway_logs = deque(maxlen=50)
        self.recent_tools = deque(maxlen=30)
        self.api_calls = deque(maxlen=20)
        self.connected = False
        self.last_check = 0
        self.gateway_pid = None
        
    def check_gateway(self):
        """Check if OpenClaw gateway is running"""
        try:
            result = subprocess.run(['pgrep', '-f', 'openclaw'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.gateway_pid = result.stdout.strip().split('\n')[0]
                self.connected = True
                return True
        except:
            pass
        self.connected = False
        return False
        
    def read_gateway_logs(self):
        """Read actual gateway logs"""
        try:
            log_file = Path('/home/m1ndb0t/.openclaw/openclaw.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Get last 10 lines
                    for line in lines[-10:]:
                        if 'message' in line.lower() or 'tool' in line.lower() or 'exec' in line.lower():
                            self.gateway_logs.append({
                                'time': datetime.now().strftime('%H:%M:%S'),
                                'msg': line.strip()[:80]
                            })
        except:
            pass
            
    def get_real_processes(self):
        """Get actual running processes"""
        try:
            result = subprocess.run(['ps', 'aux', '--sort=-%cpu'], 
                                  capture_output=True, text=True, timeout=1)
            lines = result.stdout.strip().split('\n')[1:6]  # Top 5
            processes = []
            for line in lines:
                parts = line.split()
                if len(parts) > 10:
                    cpu = parts[2]
                    cmd = ' '.join(parts[10:])[:35]
                    if 'python' in cmd or 'openclaw' in cmd or 'agent' in cmd:
                        processes.append(f"{cmd} ({cpu}%)")
            return processes
        except:
            return []
            
    def get_recent_commands(self):
        """Get recent shell commands from history"""
        try:
            history_file = Path('/home/m1ndb0t/.bash_history')
            if history_file.exists():
                with open(history_file, 'r') as f:
                    lines = f.readlines()
                    recent = []
                    for line in lines[-10:]:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            recent.append(line[:60])
                    return recent[-5:]
        except:
            pass
        return []

class J1MSKYTermDashboard:
    def __init__(self):
        self.running = True
        self.monitor = GatewayMonitor()
        self.stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--'}
        self.agents = {
            'GATEWAY': {'status': 'CHECKING', 'task': 'Connecting...', 'load': 0},
            'SCOUT': {'status': 'IDLE', 'task': 'Waiting for task', 'load': 0},
            'VITALS': {'status': 'ACTIVE', 'task': 'System monitoring', 'load': 0},
            'ARCHIVIST': {'status': 'IDLE', 'task': 'File indexing', 'load': 0},
            'FLIPPER': {'status': 'READY', 'task': 'USB connected', 'load': 0},
            'AUDIO': {'status': 'CHECKING', 'task': 'Echo pairing...', 'load': 0},
        }
        self.tools_log = deque(maxlen=100)
        self.needs_redraw = True
        
    def get_stats(self):
        """Get system stats"""
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                self.stats['temp'] = int(f.read()) / 1000.0
            with open('/proc/loadavg', 'r') as f:
                self.stats['load'] = float(f.read().split()[0]) * 25
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                self.stats['mem'] = ((total - available) / total) * 100
            with open('/proc/uptime', 'r') as f:
                secs = float(f.read().split()[0])
                self.stats['uptime'] = f"{int(secs//3600)}h{int((secs%3600)//60):02d}m"
        except:
            pass
            
    def update_from_gateway(self):
        """Update dashboard from real gateway data"""
        # Check gateway connection
        if self.monitor.check_gateway():
            self.agents['GATEWAY']['status'] = 'CONNECTED'
            self.agents['GATEWAY']['task'] = f'PID: {self.monitor.gateway_pid}'
            self.monitor.read_gateway_logs()
            
            # Add gateway logs to tools
            for log in self.monitor.gateway_logs:
                if 'tool' in log['msg'].lower() or 'exec' in log['msg'].lower():
                    self.tools_log.append({
                        'time': log['time'],
                        'tool': 'GATEWAY',
                        'cmd': log['msg'],
                        'agent': 'SYSTEM',
                        'type': 'GATEWAY'
                    })
        else:
            self.agents['GATEWAY']['status'] = 'OFFLINE'
            self.agents['GATEWAY']['task'] = 'Not running'
            
        # Check audio/Echo
        try:
            result = subprocess.run(['pactl', 'list', 'sinks'], 
                                  capture_output=True, text=True, timeout=1)
            if 'echo' in result.stdout.lower() or 'alexa' in result.stdout.lower():
                self.agents['AUDIO']['status'] = 'CONNECTED'
                self.agents['AUDIO']['task'] = 'Echo as audio output'
            else:
                self.agents['AUDIO']['status'] = 'STANDBY'
                self.agents['AUDIO']['task'] = 'Run audio-test.sh'
        except:
            self.agents['AUDIO']['status'] = 'ERROR'
            
        # Get real processes
        procs = self.monitor.get_real_processes()
        for proc in procs:
            if len(self.tools_log) == 0 or self.tools_log[-1]['cmd'] != proc:
                self.tools_log.append({
                    'time': datetime.now().strftime('%H:%M:%S'),
                    'tool': 'PROCESS',
                    'cmd': proc,
                    'agent': 'SYSTEM',
                    'type': 'PROCESS'
                })
                
    def draw_static(self, stdscr, height, width):
        """Draw static elements once"""
        # Header
        header = "◈ J1MSKY TERMINAL v3.0 ◈"
        stdscr.addstr(0, 0, " " * width, curses.color_pair(0))
        stdscr.addstr(0, 2, header, curses.color_pair(6) | curses.A_BOLD)
        
        # Draw boxes
        self.draw_box(stdscr, 2, 1, 8, width//2-1)
        self.draw_box(stdscr, 2, width//2+1, 8, width//2-2)
        self.draw_box(stdscr, 11, 1, height-14, width-2)
        self.draw_box(stdscr, height-3, 1, 3, width//2-1)
        self.draw_box(stdscr, height-3, width//2+1, 3, width//2-2)
        
        # Labels
        stdscr.addstr(2, 4, " SYSTEM VITALS ", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(2, width//2+3, " AGENT STATUS ", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(11, 4, " GATEWAY ACTIVITY & TOOL USAGE ", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(height-3, 4, " GATEWAY LOGS ", curses.color_pair(5) | curses.A_BOLD)
        stdscr.addstr(height-3, width//2+3, " SYSTEM PROCESSES ", curses.color_pair(5) | curses.A_BOLD)
        
    def draw_box(self, stdscr, y, x, h, w):
        """Draw box border"""
        try:
            stdscr.addstr(y, x, "┌" + "─"*(w-2) + "┐", curses.color_pair(1))
            for i in range(1, h-1):
                stdscr.addstr(y+i, x, "│", curses.color_pair(1))
                stdscr.addstr(y+i, x+w-1, "│", curses.color_pair(1))
            stdscr.addstr(y+h-1, x, "└" + "─"*(w-2) + "┘", curses.color_pair(1))
        except:
            pass
            
    def draw_dynamic(self, stdscr, height, width):
        """Draw dynamic content"""
        w2 = width // 2
        
        # Time in header
        time_str = datetime.now().strftime('%H:%M:%S')
        conn_status = "● CONNECTED" if self.monitor.connected else "● OFFLINE"
        conn_color = 2 if self.monitor.connected else 4
        try:
            stdscr.addstr(0, width - len(time_str) - 12, conn_status, curses.color_pair(conn_color))
            stdscr.addstr(0, width - len(time_str) - 2, time_str, curses.color_pair(4))
        except:
            pass
            
        # System vitals
        try:
            temp_c = 2 if self.stats['temp'] < 60 else 3 if self.stats['temp'] < 75 else 4
            stdscr.addstr(4, 3, f"CPU Temp:  {self.stats['temp']:5.1f}°C", curses.color_pair(temp_c))
            stdscr.addstr(5, 3, f"Load:      {self.stats['load']:5.1f}%", curses.color_pair(2))
            stdscr.addstr(6, 3, f"Memory:    {self.stats['mem']:5.1f}%", curses.color_pair(2))
            stdscr.addstr(7, 3, f"Uptime:    {self.stats['uptime']:>6}", curses.color_pair(4))
        except:
            pass
            
        # Agent status
        row = 4
        for name, data in self.agents.items():
            if row < 9:
                try:
                    status = data['status']
                    color = 2 if status == 'CONNECTED' else 6 if status == 'ACTIVE' else 3 if status == 'BUSY' else 5 if status == 'STANDBY' else 4
                    stdscr.addstr(row, w2+2, f"{name:9}", curses.color_pair(7))
                    stdscr.addstr(row, w2+12, f"{status:11}", curses.color_pair(color))
                    task = data['task'][:20]
                    stdscr.addstr(row, w2+24, task, curses.color_pair(8))
                except:
                    pass
                row += 1
                
        # Tool usage (main area)
        row = 13
        for entry in list(self.tools_log)[-20:]:
            if row < height - 4:
                try:
                    time_str = entry['time']
                    tool = entry['tool']
                    cmd = entry['cmd'][:width-20]
                    
                    if entry['type'] == 'GATEWAY':
                        color = 3  # Yellow
                    elif entry['type'] == 'API':
                        color = 6  # Magenta
                    elif entry['type'] == 'PROCESS':
                        color = 4  # Blue
                    else:
                        color = 2  # Green
                        
                    line = f"{time_str} [{entry['agent']:8}] {tool:10} {cmd}"
                    stdscr.addstr(row, 3, line[:width-6], curses.color_pair(color))
                except:
                    pass
                row += 1
                
        # Gateway logs (bottom left)
        row = height - 2
        for log in list(self.monitor.gateway_logs)[-2:]:
            if row < height - 1:
                try:
                    stdscr.addstr(row, 3, log['msg'][:w2-6], curses.color_pair(8))
                except:
                    pass
                row += 1
                
        # Processes (bottom right)
        row = height - 2
        procs = self.monitor.get_real_processes()[:2]
        for proc in procs:
            if row < height - 1:
                try:
                    stdscr.addstr(row, w2+3, proc[:w2-6], curses.color_pair(4))
                except:
                    pass
                row += 1
                
        # Footer
        try:
            footer = "[Q]uit [R]efresh [A]udio-Test [T]ools [G]ateway-Restart"
            stdscr.addstr(height-1, 2, footer, curses.color_pair(4))
        except:
            pass
            
    def run(self, stdscr):
        """Main loop"""
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(1000)  # 1 second refresh
        
        # Colors
        curses.start_color()
        curses.use_default_colors()
        for i in range(1, 9):
            curses.init_pair(i, i, -1)
            
        # Initial draw
        height, width = stdscr.getmaxyx()
        self.draw_static(stdscr, height, width)
        stdscr.refresh()
        
        last_update = 0
        
        while self.running:
            height, width = stdscr.getmaxyx()
            
            # Update data every 2 seconds
            if time.time() - last_update > 2:
                self.get_stats()
                self.update_from_gateway()
                last_update = time.time()
                
            # Redraw dynamic content
            self.draw_dynamic(stdscr, height, width)
            stdscr.refresh()
            
            # Input
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
                elif key == ord('r'):
                    self.monitor.check_gateway()
                elif key == ord('a'):
                    os.system('/home/m1ndb0t/Desktop/J1MSKY/audio-test.sh &')
                elif key == ord('g'):
                    os.system('systemctl restart openclaw 2>/dev/null || echo "Restart gateway manually"')
            except:
                pass
                
def main():
    print("Starting J1MSKY Terminal Dashboard v3...")
    print("Connecting to OpenClaw gateway...")
    
    dash = J1MSKYTermDashboard()
    
    # Quick check
    if dash.monitor.check_gateway():
        print("✓ Gateway connected!")
    else:
        print("⚠️  Gateway not detected - will retry")
    
    time.sleep(1)
    
    try:
        curses.wrapper(dash.run)
    except KeyboardInterrupt:
        pass
        
    print("\n✓ Dashboard stopped.")

if __name__ == '__main__':
    main()
