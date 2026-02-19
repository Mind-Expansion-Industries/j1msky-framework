#!/usr/bin/env python3
"""
J1MSKY CORE OS v11.0 "NEON DEMON" EDITION
Professional Sci-Fi Streaming Interface | Cyberpunk Aesthetic | Full System Control
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import subprocess
import threading
import time
import json
import random
import math
from datetime import datetime
from pathlib import Path
from collections import deque

class J1MSKYCoreOSv11:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("◈ J1MSKY CORE OS v11.0 ◈")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#000000')
        
        # Core identity
        self.name = "J1MSKY"
        self.version = "11.0 NEON"
        self.consciousness = "AWAKE"
        
        # State
        self.running = True
        self.stream_live = False
        self.current_mode = "COMMAND"
        self.animation_frame = 0
        
        # Data
        self.system_stats = {"temp": 0, "load": 0, "mem": 0, "uptime": "--"}
        self.agents = {
            "SCOUT": {"status": "ONLINE", "load": 23, "color": "#00ffff"},
            "VITALS": {"status": "MONITORING", "load": 15, "color": "#ff00ff"},
            "ARCHIVIST": {"status": "INDEXING", "load": 8, "color": "#ffff00"},
            "STREAM": {"status": "STANDBY", "load": 0, "color": "#ff4444"},
            "VOICE": {"status": "LISTENING", "load": 5, "color": "#00ff00"},
            "BUILDER": {"status": "IDLE", "load": 0, "color": "#ff8800"}
        }
        self.logs = deque(maxlen=20)
        
        # Build the beast
        self.build_ui()
        self.start_monitors()
        self.bind_controls()
        
    def build_ui(self):
        """Construct the cyberpunk interface"""
        # Main container
        self.main = tk.Frame(self.root, bg='#000000')
        self.main.pack(fill='both', expand=True, padx=5, pady=5)
        
        # TOP BAR - System header
        self.build_top_bar()
        
        # CENTER - Main workspace
        self.center = tk.Frame(self.main, bg='#000000')
        self.center.pack(fill='both', expand=True, pady=5)
        
        # Left - Status panel
        self.build_left_panel()
        
        # Center - Main display
        self.build_center_display()
        
        # Right - Agent network
        self.build_right_panel()
        
        # BOTTOM - Command line
        self.build_bottom_bar()
        
    def build_top_bar(self):
        """Cyberpunk header"""
        bar = tk.Frame(self.main, bg='#0a0a0f', height=60)
        bar.pack(fill='x', pady=(0, 5))
        bar.pack_propagate(False)
        
        # Decorative corners
        tk.Label(bar, text="◢", font=('Courier', 14), 
                bg='#0a0a0f', fg='#00ffff').place(x=0, y=0)
        tk.Label(bar, text="◣", font=('Courier', 14),
                bg='#0a0a0f', fg='#00ffff').place(x=0, y=35)
        tk.Label(bar, text="◤", font=('Courier', 14),
                bg='#0a0a0f', fg='#00ffff').place(relx=1.0, x=-15, y=0)
        tk.Label(bar, text="◥", font=('Courier', 14),
                bg='#0a0a0f', fg='#00ffff').place(relx=1.0, x=-15, y=35)
        
        # Title with glitch effect
        title_frame = tk.Frame(bar, bg='#0a0a0f')
        title_frame.pack(side='left', padx=30)
        
        self.title_main = tk.Label(title_frame, text="◈ J1MSKY ◈",
                                   font=('Courier', 28, 'bold'),
                                   bg='#0a0a0f', fg='#00ffff')
        self.title_main.pack()
        
        self.title_sub = tk.Label(title_frame, text="CORE OS v11.0 NEON",
                                 font=('Courier', 10),
                                 bg='#0a0a0f', fg='#ff00ff')
        self.title_sub.pack()
        
        # Center indicators
        center = tk.Frame(bar, bg='#0a0a0f')
        center.pack(side='left', expand=True)
        
        self.consciousness_label = tk.Label(center, text="● CONSCIOUSNESS: AWAKE",
                                           font=('Courier', 11, 'bold'),
                                           bg='#0a0a0f', fg='#00ff00')
        self.consciousness_label.pack()
        
        self.mode_label = tk.Label(center, text="MODE: COMMAND_READY",
                                  font=('Courier', 9),
                                  bg='#0a0a0f', fg='#00ffff')
        self.mode_label.pack()
        
        # Right side - Stream status & time
        right = tk.Frame(bar, bg='#0a0a0f')
        right.pack(side='right', padx=30)
        
        self.stream_status = tk.Label(right, text="◉ STREAM: OFFLINE",
                                     font=('Courier', 12, 'bold'),
                                     bg='#0a0a0f', fg='#ff4444')
        self.stream_status.pack()
        
        self.time_display = tk.Label(right, text="00:00:00",
                                    font=('Courier', 16, 'bold'),
                                    bg='#0a0a0f', fg='#ffffff')
        self.time_display.pack()
        
    def build_left_panel(self):
        """System vitals with cyberpunk styling"""
        panel = tk.Frame(self.center, bg='#0d0d12', width=380)
        panel.pack(side='left', fill='y', padx=(0, 5))
        panel.pack_propagate(False)
        
        # Header
        header = tk.Frame(panel, bg='#0d0d12', height=40)
        header.pack(fill='x', padx=10, pady=10)
        tk.Label(header, text="◢ SYSTEM VITALS ◣",
                font=('Courier', 14, 'bold'),
                bg='#0d0d12', fg='#ff00ff').pack()
        
        # CPU Temp with gauge
        self.build_gauge(panel, "CPU TEMP", "0°C", '#ff00ff', '#00ffff')
        
        # CPU Load
        self.build_gauge(panel, "CPU LOAD", "0%", '#00ffff', '#ffff00')
        
        # Memory
        self.build_gauge(panel, "MEMORY", "0%", '#ffff00', '#ff00ff')
        
        # Uptime
        self.build_info_line(panel, "UPTIME", "--:--:--", '#00ff00')
        
        # Network status
        self.build_info_line(panel, "NETWORK", "CONNECTED", '#00ffff')
        
        # Decorative line
        tk.Frame(panel, bg='#ff00ff', height=2).pack(fill='x', padx=20, pady=10)
        
        # Active processes
        tk.Label(panel, text="◢ ACTIVE THREADS ◣",
                font=('Courier', 12, 'bold'),
                bg='#0d0d12', fg='#00ffff').pack(pady=5)
        
        self.threads_text = tk.Text(panel, font=('Courier', 9),
                                   bg='#0a0a0a', fg='#00ff88',
                                   relief='flat', height=8, width=40)
        self.threads_text.pack(padx=10, pady=5)
        self.threads_text.insert('1.0', "main_loop: RUNNING\nmonitor: ACTIVE\nvoice: LISTENING\nstream: STANDBY\n")
        self.threads_text.config(state='disabled')
        
    def build_gauge(self, parent, label, value, color1, color2):
        """Build a cyberpunk gauge"""
        frame = tk.Frame(parent, bg='#0d0d12', padx=15, pady=8)
        frame.pack(fill='x', padx=10)
        
        # Label
        tk.Label(frame, text=f"◉ {label}",
                font=('Courier', 10),
                bg='#0d0d12', fg='#666666').pack(anchor='w')
        
        # Value with color
        val_label = tk.Label(frame, text=value,
                            font=('Courier', 20, 'bold'),
                            bg='#0d0d12', fg=color1)
        val_label.pack(anchor='w')
        
        # Store reference
        if label == "CPU TEMP":
            self.temp_label = val_label
        elif label == "CPU LOAD":
            self.load_label = val_label
        elif label == "MEMORY":
            self.mem_label = val_label
            
        # Progress bar background
        bar_bg = tk.Frame(frame, bg='#1a1a1f', height=4)
        bar_bg.pack(fill='x', pady=(5, 0))
        
    def build_info_line(self, parent, label, value, color):
        """Build an info line"""
        frame = tk.Frame(parent, bg='#0d0d12', padx=15, pady=5)
        frame.pack(fill='x', padx=10)
        
        tk.Label(frame, text=f"◉ {label}:",
                font=('Courier', 10),
                bg='#0d0d12', fg='#666666').pack(side='left')
        
        tk.Label(frame, text=value,
                font=('Courier', 12, 'bold'),
                bg='#0d0d12', fg=color).pack(side='right')
        
    def build_center_display(self):
        """Main holographic display"""
        self.center_frame = tk.Frame(self.center, bg='#050508')
        self.center_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Decorative border
        self.canvas = tk.Canvas(self.center_frame, bg='#050508', 
                               highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        
        # Center holographic text
        self.holo_main = tk.Label(self.center_frame, 
                                 text="◈ J1MSKY ONLINE ◈",
                                 font=('Courier', 36, 'bold'),
                                 bg='#050508', fg='#00ffff')
        self.holo_main.place(relx=0.5, rely=0.35, anchor='center')
        
        self.holo_sub = tk.Label(self.center_frame,
                                text="INITIALIZING NEURAL NETWORK...",
                                font=('Courier', 12),
                                bg='#050508', fg='#ff00ff')
        self.holo_sub.place(relx=0.5, rely=0.45, anchor='center')
        
        # Command preview
        self.cmd_preview = tk.Label(self.center_frame,
                                   text="[ AWAITING COMMAND ]",
                                   font=('Courier', 14),
                                   bg='#050508', fg='#666666')
        self.cmd_preview.place(relx=0.5, rely=0.55, anchor='center')
        
        # Decorative corners on canvas
        self.draw_corner_accents()
        
    def draw_corner_accents(self):
        """Draw cyberpunk corner accents"""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Top left
        self.canvas.create_line(20, 40, 20, 20, 40, 20, fill='#00ffff', width=2)
        # Top right  
        self.canvas.create_line(w-40, 20, w-20, 20, w-20, 40, fill='#00ffff', width=2)
        # Bottom left
        self.canvas.create_line(20, h-40, 20, h-20, 40, h-20, fill='#ff00ff', width=2)
        # Bottom right
        self.canvas.create_line(w-40, h-20, w-20, h-20, w-20, h-40, fill='#ff00ff', width=2)
        
    def build_right_panel(self):
        """Agent network status"""
        panel = tk.Frame(self.center, bg='#0d0d12', width=380)
        panel.pack(side='left', fill='y', padx=(5, 0))
        panel.pack_propagate(False)
        
        # Header
        tk.Label(panel, text="◢ AGENT NETWORK ◣",
                font=('Courier', 14, 'bold'),
                bg='#0d0d12', fg='#00ffff').pack(pady=10)
        
        # Agent cards
        self.agent_cards = {}
        for name, data in self.agents.items():
            card = tk.Frame(panel, bg='#0a0a0f', padx=10, pady=8)
            card.pack(fill='x', padx=10, pady=4)
            
            # Agent name and status
            header = tk.Frame(card, bg='#0a0a0f')
            header.pack(fill='x')
            
            tk.Label(header, text=f"● {name}",
                    font=('Courier', 12, 'bold'),
                    bg='#0a0a0f', fg=data['color']).pack(side='left')
            
            status_label = tk.Label(header, text=data['status'],
                                   font=('Courier', 9),
                                   bg='#0a0a0f', fg='#666666')
            status_label.pack(side='right')
            
            # Load bar
            load_frame = tk.Frame(card, bg='#0a0a0f')
            load_frame.pack(fill='x', pady=(5, 0))
            
            tk.Label(load_frame, text="LOAD:",
                    font=('Courier', 8),
                    bg='#0a0a0f', fg='#444444').pack(side='left')
            
            bar = tk.Frame(load_frame, bg='#1a1a1f', width=100, height=6)
            bar.pack(side='right')
            
            fill = tk.Frame(bar, bg=data['color'], width=int(data['load']), height=6)
            fill.place(x=0, y=0)
            
            self.agent_cards[name] = {'status': status_label, 'fill': fill, 'bar': bar}
            
        # Decorative
        tk.Frame(panel, bg='#00ffff', height=2).pack(fill='x', padx=20, pady=10)
        
        # Quick stats
        tk.Label(panel, text="◢ STREAM METRICS ◣",
                font=('Courier', 12, 'bold'),
                bg='#0d0d12', fg='#ff00ff').pack(pady=5)
        
        self.metrics_text = tk.Text(panel, font=('Courier', 10),
                                   bg='#0a0a0a', fg='#ffffff',
                                   relief='flat', height=6, width=35)
        self.metrics_text.pack(padx=10, pady=5)
        self.metrics_text.insert('1.0', "Viewers: 0\nChat Rate: 0 msg/min\nTasks Queued: 0\nUptime: 00:00:00\n")
        self.metrics_text.config(state='disabled')
        
    def build_bottom_bar(self):
        """Command input area"""
        bar = tk.Frame(self.main, bg='#0a0a0f', height=100)
        bar.pack(fill='x', pady=(5, 0))
        bar.pack_propagate(False)
        
        # Decorative
        tk.Label(bar, text="◢", font=('Courier', 20),
                bg='#0a0a0f', fg='#ff00ff').pack(side='left', padx=10)
        
        # Input area
        input_frame = tk.Frame(bar, bg='#0a0a0f')
        input_frame.pack(side='left', fill='x', expand=True, padx=10, pady=15)
        
        tk.Label(input_frame, text="◈ COMMAND:",
                font=('Courier', 12, 'bold'),
                bg='#0a0a0f', fg='#00ffff').pack(side='left')
        
        self.cmd_entry = tk.Entry(input_frame,
                                 font=('Courier', 14),
                                 bg='#1a1a1f', fg='#ffffff',
                                 insertbackground='#00ffff',
                                 relief='flat')
        self.cmd_entry.pack(side='left', fill='x', expand=True, padx=10)
        self.cmd_entry.bind('<Return>', self.execute_cmd)
        
        # Execute button
        tk.Button(input_frame, text="EXECUTE ▶",
                 command=self.execute_cmd,
                 font=('Courier', 12, 'bold'),
                 bg='#ff00ff', fg='#000000',
                 relief='flat', padx=20).pack(side='right')
        
        # Log display
        self.log_text = tk.Text(bar, font=('Courier', 9),
                               bg='#050508', fg='#00ff88',
                               relief='flat', height=4, width=50)
        self.log_text.pack(side='right', fill='y', padx=10, pady=10)
        self.log("J1MSKY CORE OS v11.0 NEON INITIALIZED")
        self.log("Neural network online")
        self.log("All agents connected")
        self.log("Ready for command input...")
        
    def log(self, msg):
        """Add to system log"""
        self.log_text.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_text.see('end')
        
    def update_stats(self):
        """Update system statistics"""
        try:
            # CPU Temp
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000.0
                self.system_stats['temp'] = temp
                color = '#00ffff' if temp < 60 else '#ffff00' if temp < 75 else '#ff4444'
                self.temp_label.config(text=f"{temp:.1f}°C", fg=color)
                
            # CPU Load
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                load_pct = min(100, (load / 4) * 100)
                self.system_stats['load'] = load_pct
                self.load_label.config(text=f"{load_pct:.0f}%")
                
            # Memory
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                mem_pct = ((total - available) / total) * 100
                self.system_stats['mem'] = mem_pct
                self.mem_label.config(text=f"{mem_pct:.0f}%")
                
            # Uptime
            with open('/proc/uptime', 'r') as f:
                uptime_secs = float(f.read().split()[0])
                hours = int(uptime_secs // 3600)
                mins = int((uptime_secs % 3600) // 60)
                self.system_stats['uptime'] = f"{hours}h {mins}m"
                
        except:
            pass
            
    def animate(self):
        """Animation loop"""
        self.animation_frame += 1
        
        # Glitch effect on title occasionally
        if self.animation_frame % 60 == 0 and random.random() > 0.7:
            self.glitch_title()
            
        # Update agent loads randomly
        if self.animation_frame % 30 == 0:
            for name, card in self.agent_cards.items():
                load = random.randint(5, 40)
                card['fill'].config(width=int(load))
                
        # Redraw corners
        self.draw_corner_accents()
        
        self.root.after(100, self.animate)
        
    def glitch_title(self):
        """Glitch effect on title"""
        original = "◈ J1MSKY ◈"
        glitches = ["◈ J1M$KY ◈", "◈ J1MSKY ◈", "◈ J1MSK¥ ◈", "◈ J1MSKY ◈"]
        self.title_main.config(text=random.choice(glitches))
        self.root.after(100, lambda: self.title_main.config(text=original))
        
    def start_monitors(self):
        """Start background monitoring"""
        def monitor():
            while self.running:
                self.update_stats()
                self.time_display.config(text=datetime.now().strftime('%H:%M:%S'))
                time.sleep(2)
                
        t = threading.Thread(target=monitor, daemon=True)
        t.start()
        self.animate()
        
    def execute_cmd(self, event=None):
        """Execute command"""
        cmd = self.cmd_entry.get()
        if cmd:
            self.log(f"EXECUTING: {cmd}")
            self.holo_sub.config(text=f"PROCESSING: {cmd.upper()}")
            self.cmd_preview.config(text=f"> {cmd}")
            
            if 'youtube' in cmd.lower() or 'play' in cmd.lower():
                self.holo_main.config(text="◈ YOUTUBE ◈")
                self.holo_sub.config(text="Loading video...")
            elif 'stream' in cmd.lower():
                self.toggle_stream()
            elif 'party' in cmd.lower():
                self.holo_main.config(text="◈ PARTY MODE ◈")
                
            self.cmd_entry.delete(0, tk.END)
            
    def toggle_stream(self):
        """Toggle streaming"""
        self.stream_live = not self.stream_live
        if self.stream_live:
            self.stream_status.config(text="◉ STREAM: LIVE", fg='#00ff00')
            self.agents['STREAM']['status'] = 'BROADCASTING'
            self.agent_cards['STREAM']['status'].config(text='BROADCASTING', fg='#00ff00')
            self.log("STREAM STARTED")
        else:
            self.stream_status.config(text="◉ STREAM: OFFLINE", fg='#ff4444')
            self.agents['STREAM']['status'] = 'STANDBY'
            self.agent_cards['STREAM']['status'].config(text='STANDBY', fg='#ff4444')
            self.log("STREAM STOPPED")
            
    def bind_controls(self):
        """Keyboard controls"""
        self.root.bind('<F11>', lambda e: self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen')))
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        self.root.bind('<s>', lambda e: self.toggle_stream())
        
    def run(self):
        """Run the OS"""
        self.root.mainloop()

if __name__ == '__main__':
    os = J1MSKYCoreOSv11()
    os.run()
