#!/usr/bin/env python3
"""
J1MSKY Terminal Dashboard - Lightweight TUI
Low resource usage, real-time agent monitoring
"""

import curses
import os
import sys
import time
import json
import subprocess
import threading
from datetime import datetime
from pathlib import Path

class J1MSKYTermDashboard:
    def __init__(self):
        self.running = True
        self.agents = {
            'SCOUT': {'status': 'IDLE', 'load': 0, 'last_msg': 'Ready'},
            'VITALS': {'status': 'IDLE', 'load': 0, 'last_msg': 'Ready'},
            'ARCHIVIST': {'status': 'IDLE', 'load': 0, 'last_msg': 'Ready'},
            'STREAM': {'status': 'STANDBY', 'load': 0, 'last_msg': 'Ready'},
            'VOICE': {'status': 'LISTENING', 'load': 0, 'last_msg': 'Ready'},
            'FLIPPER': {'status': 'DISCONNECTED', 'load': 0, 'last_msg': 'Waiting'},
        }
        self.logs = []
        self.stats = {'temp': 0, 'load': 0, 'mem': 0, 'uptime': '--'}
        self.command_buffer = ""
        
    def get_system_stats(self):
        """Get system statistics"""
        try:
            # CPU Temp
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                self.stats['temp'] = int(f.read().strip()) / 1000.0
                
            # CPU Load
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                self.stats['load'] = min(100, (load / 4) * 100)
                
            # Memory
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                self.stats['mem'] = ((total - available) / total) * 100
                
            # Uptime
            with open('/proc/uptime', 'r') as f:
                uptime_secs = float(f.read().split()[0])
                hours = int(uptime_secs // 3600)
                mins = int((uptime_secs % 3600) // 60)
                self.stats['uptime'] = f"{hours}h{mins}m"
                
        except:
            pass
            
    def draw_header(self, stdscr, width):
        """Draw header bar"""
        header = "◈ J1MSKY TERMINAL v11.0 ◈"
        time_str = datetime.now().strftime('%H:%M:%S')
        status = "ONLINE"
        
        stdscr.addstr(0, 0, " " * width, curses.color_pair(1))
        stdscr.addstr(0, 2, header, curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(0, width - len(time_str) - 2, time_str, curses.color_pair(1))
        stdscr.addstr(0, width // 2 - len(status) // 2, status, curses.color_pair(2))
        
    def draw_vitals(self, stdscr, y, width):
        """Draw system vitals box"""
        box_width = width // 2 - 2
        
        # Header
        stdscr.addstr(y, 2, "┌" + "─" * (box_width - 2) + "┐", curses.color_pair(3))
        stdscr.addstr(y + 1, 2, "│ SYSTEM VITALS" + " " * (box_width - 16) + "│", curses.color_pair(3))
        stdscr.addstr(y + 2, 2, "├" + "─" * (box_width - 2) + "┤", curses.color_pair(3))
        
        # Stats
        temp_color = 2 if self.stats['temp'] < 60 else 4 if self.stats['temp'] < 75 else 5
        stdscr.addstr(y + 3, 2, f"│ CPU: {self.stats['temp']:5.1f}°C ", curses.color_pair(temp_color))
        stdscr.addstr(y + 3, box_width - 3, "│", curses.color_pair(3))
        
        stdscr.addstr(y + 4, 2, f"│ LOAD: {self.stats['load']:5.1f}% ", curses.color_pair(2))
        stdscr.addstr(y + 4, box_width - 3, "│", curses.color_pair(3))
        
        stdscr.addstr(y + 5, 2, f"│ MEM:  {self.stats['mem']:5.1f}% ", curses.color_pair(2))
        stdscr.addstr(y + 5, box_width - 3, "│", curses.color_pair(3))
        
        stdscr.addstr(y + 6, 2, f"│ UP:   {self.stats['uptime']:>6} ", curses.color_pair(2))
        stdscr.addstr(y + 6, box_width - 3, "│", curses.color_pair(3))
        
        stdscr.addstr(y + 7, 2, "└" + "─" * (box_width - 2) + "┘", curses.color_pair(3))
        
    def draw_agents(self, stdscr, y, width):
        """Draw agent status box"""
        box_width = width // 2 - 2
        start_x = width // 2 + 1
        
        # Header
        stdscr.addstr(y, start_x, "┌" + "─" * (box_width - 2) + "┐", curses.color_pair(3))
        stdscr.addstr(y + 1, start_x, "│ AGENT NETWORK" + " " * (box_width - 16) + "│", curses.color_pair(3))
        stdscr.addstr(y + 2, start_x, "├" + "─" * (box_width - 2) + "┤", curses.color_pair(3))
        
        # Agents
        row = y + 3
        for name, data in self.agents.items():
            status = data['status']
            color = 2 if status == 'ACTIVE' else 6 if status == 'IDLE' else 5 if status == 'ERROR' else 4
            bar = "█" * int(data['load'] / 10)
            bar += "░" * (10 - len(bar))
            
            stdscr.addstr(row, start_x, f"│ {name:8} ", curses.color_pair(3))
            stdscr.addstr(row, start_x + 10, f"{status:12}", curses.color_pair(color))
            stdscr.addstr(row, start_x + 23, f"[{bar}]", curses.color_pair(3))
            stdscr.addstr(row, start_x + box_width - 3, "│", curses.color_pair(3))
            row += 1
            
        stdscr.addstr(row, start_x, "└" + "─" * (box_width - 2) + "┘", curses.color_pair(3))
        
    def draw_logs(self, stdscr, y, width, height):
        """Draw log output area"""
        box_height = height - y - 4
        
        # Header
        stdscr.addstr(y, 2, "┌" + "─" * (width - 4) + "┐", curses.color_pair(3))
        stdscr.addstr(y + 1, 2, "│ ACTIVITY LOG" + " " * (width - 17) + "│", curses.color_pair(3))
        stdscr.addstr(y + 2, 2, "├" + "─" * (width - 4) + "┤", curses.color_pair(3))
        
        # Log lines
        for i in range(box_height - 3):
            row = y + 3 + i
            if row < height - 1:
                log_idx = len(self.logs) - box_height + 3 + i
                if log_idx >= 0 and log_idx < len(self.logs):
                    log = self.logs[log_idx]
                    log_str = f"│ {log[:width-6]}"
                    stdscr.addstr(row, 2, log_str.ljust(width - 2), curses.color_pair(7))
                    stdscr.addstr(row, width - 2, "│", curses.color_pair(3))
                else:
                    stdscr.addstr(row, 2, "│" + " " * (width - 4) + "│", curses.color_pair(3))
                    
        # Footer
        stdscr.addstr(height - 2, 2, "└" + "─" * (width - 4) + "┘", curses.color_pair(3))
        
    def draw_command(self, stdscr, height, width):
        """Draw command input line"""
        prompt = "> "
        stdscr.addstr(height - 1, 0, prompt + self.command_buffer.ljust(width - len(prompt) - 1), 
                     curses.color_pair(1) | curses.A_BOLD)
        
    def log(self, message):
        """Add log message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
            
    def update_agents(self):
        """Simulate agent activity"""
        import random
        for name in self.agents:
            if random.random() < 0.1:
                self.agents[name]['load'] = random.randint(5, 40)
                statuses = ['ACTIVE', 'IDLE', 'BUSY', 'STANDBY']
                self.agents[name]['status'] = random.choice(statuses)
                
    def run(self, stdscr):
        """Main run loop"""
        # Setup curses
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)   # Non-blocking input
        stdscr.timeout(100) # Refresh rate
        
        # Colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)      # Header
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Good status
        curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)     # Borders
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # Warning
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)       # Critical
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)   # Idle
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)     # Logs
        
        self.log("J1MSKY Terminal Dashboard initialized")
        self.log("Press 'q' to quit, 'c' for command")
        
        last_update = 0
        
        while self.running:
            # Get screen size
            height, width = stdscr.getmaxyx()
            
            # Clear screen
            stdscr.clear()
            
            # Update data every second
            if time.time() - last_update > 1:
                self.get_system_stats()
                self.update_agents()
                last_update = time.time()
                
            # Draw components
            self.draw_header(stdscr, width)
            self.draw_vitals(stdscr, 2, width)
            self.draw_agents(stdscr, 2, width)
            self.draw_logs(stdscr, 10, width, height)
            self.draw_command(stdscr, height, width)
            
            # Refresh
            stdscr.refresh()
            
            # Handle input
            try:
                key = stdscr.getch()
                if key == ord('q'):
                    self.running = False
                elif key == ord('c'):
                    self.command_buffer = "Command: "
                elif key == ord('f'):
                    self.log("Flipper scan initiated")
                elif key == ord('s'):
                    self.log("System check complete")
                elif key == ord('1'):
                    self.agents['SCOUT']['status'] = 'SCANNING'
                    self.log("SCOUT: Starting news scan")
                elif key == ord('2'):
                    self.agents['VITALS']['status'] = 'CHECKING'
                    self.log("VITALS: Full system check")
                elif key == curses.KEY_BACKSPACE or key == 127:
                    self.command_buffer = self.command_buffer[:-1]
                elif key >= 32 and key < 127:
                    self.command_buffer += chr(key)
                    
            except:
                pass
                
            time.sleep(0.05)
            
def main():
    dashboard = J1MSKYTermDashboard()
    curses.wrapper(dashboard.run)
    print("J1MSKY Terminal Dashboard stopped.")
    
if __name__ == '__main__':
    main()
