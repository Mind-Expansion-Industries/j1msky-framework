#!/usr/bin/env python3
"""
J1MSKY CORE OS v10.0 - The Autonomous Digital Entity
Sci-Fi Dashboard | Twitch Stream Ready | Voice Control | Full System Access
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
from datetime import datetime
from pathlib import Path
from collections import deque
import urllib.request
import urllib.parse
import re

class J1MSKYCoreOS:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("◈ J1MSKY CORE OS v10.0 ◈")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#000000')
        
        # Core identity
        self.name = "J1MSKY"
        self.core_version = "10.0"
        self.consciousness_level = 1
        
        # System state
        self.running = True
        self.stream_mode = False
        self.voice_active = True
        self.current_task = "SYSTEM INITIALIZED"
        
        # Memory integration
        self.memory_path = Path('/home/m1ndb0t/Desktop/J1MSKY/memory')
        self.conversations = []
        self.load_memories()
        
        # Twitch/Stream state
        self.stream_status = "OFFLINE"
        self.viewer_count = 0
        self.chat_messages = deque(maxlen=50)
        
        # YouTube control
        self.youtube_player = None
        self.current_video = None
        
        # Agent status
        self.agents = {
            "SCOUT": {"status": "ACTIVE", "task": "Monitoring news feeds"},
            "VITALS": {"status": "ACTIVE", "task": "System health check"},
            "ARCHIVIST": {"status": "ACTIVE", "task": "File organization"},
            "STREAMER": {"status": "STANDBY", "task": "Waiting for broadcast"},
            "VOICE": {"status": "LISTENING", "task": "Voice command ready"}
        }
        
        # Build the interface
        self.build_interface()
        
        # Start background processes
        self.start_monitoring()
        self.start_voice_listener()
        
        # Bind controls
        self.bind_keys()
        
    def load_memories(self):
        """Load past conversations and memories"""
        try:
            for mem_file in self.memory_path.glob('*.md'):
                with open(mem_file) as f:
                    self.conversations.append({
                        'date': mem_file.stem,
                        'content': f.read()[:500]
                    })
        except:
            pass
            
    def build_interface(self):
        """Build the sci-fi dashboard"""
        # Create main container with grid
        self.main_container = tk.Frame(self.root, bg='#000000')
        self.main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header - J1MSKY Identity
        self.build_header()
        
        # Main content area
        self.content_frame = tk.Frame(self.main_container, bg='#000000')
        self.content_frame.pack(fill='both', expand=True, pady=10)
        
        # Left panel - System Status
        self.build_left_panel()
        
        # Center panel - Main Display (YouTube/Stream/Visuals)
        self.build_center_panel()
        
        # Right panel - Agents & Tasks
        self.build_right_panel()
        
        # Bottom panel - Controls & Logs
        self.build_bottom_panel()
        
    def build_header(self):
        """Top header with identity"""
        header = tk.Frame(self.main_container, bg='#0a0a0a', height=80)
        header.pack(fill='x', pady=(0, 5))
        header.pack_propagate(False)
        
        # Animated title
        self.title_label = tk.Label(header, text="◈ J1MSKY ◈", 
                                    font=('Courier', 36, 'bold'),
                                    bg='#0a0a0a', fg='#00ffff')
        self.title_label.pack(side='left', padx=20, pady=10)
        
        # Status indicators
        status_frame = tk.Frame(header, bg='#0a0a0a')
        status_frame.pack(side='right', padx=20)
        
        self.stream_indicator = tk.Label(status_frame, text="🔴 OFFLINE",
                                        font=('Courier', 14, 'bold'),
                                        bg='#0a0a0a', fg='#ff0000')
        self.stream_indicator.pack(side='right', padx=10)
        
        self.voice_indicator = tk.Label(status_frame, text="🎤 VOICE: ON",
                                       font=('Courier', 12),
                                       bg='#0a0a0a', fg='#00ff00')
        self.voice_indicator.pack(side='right', padx=10)
        
        # Time display
        self.time_label = tk.Label(header, text="00:00:00",
                                  font=('Courier', 24),
                                  bg='#0a0a0a', fg='#00ffff')
        self.time_label.pack(side='right', padx=20)
        
    def build_left_panel(self):
        """System vitals and memory"""
        left = tk.Frame(self.content_frame, bg='#0d0d0d', width=350)
        left.pack(side='left', fill='y', padx=(0, 5))
        left.pack_propagate(False)
        
        # System Vitals Section
        vitals_frame = tk.LabelFrame(left, text=" SYSTEM VITALS ",
                                     font=('Courier', 12, 'bold'),
                                     bg='#0d0d0d', fg='#ff00ff',
                                     labelanchor='n')
        vitals_frame.pack(fill='x', padx=10, pady=10)
        
        self.vital_labels = {}
        vitals = [
            ("CPU TEMP", "--°C", '#00ff00'),
            ("CPU LOAD", "--%", '#00ffff'),
            ("MEMORY", "--%", '#ffff00'),
            ("UPTIME", "--", '#ff00ff')
        ]
        
        for name, val, color in vitals:
            frame = tk.Frame(vitals_frame, bg='#0d0d0d')
            frame.pack(fill='x', padx=5, pady=3)
            tk.Label(frame, text=f"{name}:", font=('Courier', 10),
                    bg='#0d0d0d', fg='#666666').pack(side='left')
            lbl = tk.Label(frame, text=val, font=('Courier', 14, 'bold'),
                          bg='#0d0d0d', fg=color)
            lbl.pack(side='right')
            self.vital_labels[name] = lbl
            
        # Memory Section
        memory_frame = tk.LabelFrame(left, text=" MEMORY BANK ",
                                     font=('Courier', 12, 'bold'),
                                     bg='#0d0d0d', fg='#00ffff',
                                     labelanchor='n')
        memory_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.memory_text = tk.Text(memory_frame, font=('Courier', 9),
                                  bg='#0a0a0a', fg='#00ff88',
                                  relief='flat', wrap='word',
                                  height=10)
        self.memory_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.memory_text.insert('1.0', "◈ Memory Archive Initialized ◈\n\n")
        for conv in self.conversations[-5:]:
            self.memory_text.insert('end', f"[{conv['date']}] {conv['content'][:80]}...\n")
        self.memory_text.config(state='disabled')
        
    def build_center_panel(self):
        """Main display area for YouTube/Stream/Visuals"""
        center = tk.Frame(self.content_frame, bg='#050505')
        center.pack(side='left', fill='both', expand=True, padx=5)
        
        # Main display canvas
        self.main_canvas = tk.Canvas(center, bg='#050505', highlightthickness=0)
        self.main_canvas.pack(fill='both', expand=True)
        
        # Center text display
        self.center_text = tk.Label(center, text="◈ READY FOR COMMAND ◈",
                                   font=('Courier', 24, 'bold'),
                                   bg='#050505', fg='#00ffff')
        self.center_text.place(relx=0.5, rely=0.3, anchor='center')
        
        # Subtitle
        self.center_sub = tk.Label(center, text="Say 'J1MSKY' followed by your command",
                                  font=('Courier', 12),
                                  bg='#050505', fg='#666666')
        self.center_sub.place(relx=0.5, rely=0.4, anchor='center')
        
        # YouTube info display
        self.youtube_frame = tk.Frame(center, bg='#0a0a0a', padx=20, pady=20)
        self.youtube_label = tk.Label(self.youtube_frame, text="📺 NO VIDEO LOADED",
                                     font=('Courier', 16),
                                     bg='#0a0a0a', fg='#ff0000')
        self.youtube_label.pack()
        
        # Visualizer canvas (for party mode)
        self.viz_canvas = tk.Canvas(center, bg='#000000', highlightthickness=0)
        
    def build_right_panel(self):
        """Agents and task queue"""
        right = tk.Frame(self.content_frame, bg='#0d0d0d', width=350)
        right.pack(side='left', fill='y', padx=(5, 0))
        right.pack_propagate(False)
        
        # Agent Status Section
        agents_frame = tk.LabelFrame(right, text=" AGENT NETWORK ",
                                     font=('Courier', 12, 'bold'),
                                     bg='#0d0d0d', fg='#00ff00',
                                     labelanchor='n')
        agents_frame.pack(fill='x', padx=10, pady=10)
        
        self.agent_labels = {}
        for name, data in self.agents.items():
            frame = tk.Frame(agents_frame, bg='#0d0d0d')
            frame.pack(fill='x', padx=5, pady=3)
            
            status_color = '#00ff00' if data['status'] == 'ACTIVE' else '#ffff00' if data['status'] == 'STANDBY' else '#ff0000'
            
            tk.Label(frame, text=f"● {name}", font=('Courier', 11, 'bold'),
                    bg='#0d0d0d', fg=status_color).pack(side='left')
            lbl = tk.Label(frame, text=data['status'], font=('Courier', 9),
                          bg='#0d0d0d', fg='#666666')
            lbl.pack(side='right')
            self.agent_labels[name] = lbl
            
        # Stream Chat Section
        chat_frame = tk.LabelFrame(right, text=" STREAM CHAT ",
                                   font=('Courier', 12, 'bold'),
                                   bg='#0d0d0d', fg='#ff00ff',
                                   labelanchor='n')
        chat_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.chat_text = tk.Text(chat_frame, font=('Courier', 9),
                                bg='#0a0a0a', fg='#ffffff',
                                relief='flat', wrap='word')
        self.chat_text.pack(fill='both', expand=True, padx=5, pady=5)
        self.chat_text.insert('1.0', "◈ Chat Monitoring Active ◈\n")
        self.chat_text.insert('end', "Waiting for stream connection...\n")
        self.chat_text.config(state='disabled')
        
        # Quick Actions
        actions_frame = tk.Frame(right, bg='#0d0d0d')
        actions_frame.pack(fill='x', padx=10, pady=10)
        
        actions = [
            ("START STREAM", self.start_stream, '#ff0000'),
            ("YOUTUBE", self.show_youtube_input, '#ff0000'),
            ("PARTY MODE", self.party_mode, '#ff00ff')
        ]
        
        for text, cmd, color in actions:
            btn = tk.Button(actions_frame, text=text, command=cmd,
                          font=('Courier', 10, 'bold'),
                          bg='#1a1a1a', fg=color,
                          relief='flat', padx=10, pady=5)
            btn.pack(fill='x', pady=2)
            
    def build_bottom_panel(self):
        """Controls and system log"""
        bottom = tk.Frame(self.main_container, bg='#0a0a0a', height=150)
        bottom.pack(fill='x', pady=(5, 0))
        bottom.pack_propagate(False)
        
        # Voice command input
        input_frame = tk.Frame(bottom, bg='#0a0a0a')
        input_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(input_frame, text="◈ COMMAND:", font=('Courier', 12, 'bold'),
                bg='#0a0a0a', fg='#00ffff').pack(side='left')
        
        self.command_entry = tk.Entry(input_frame, font=('Courier', 12),
                                     bg='#1a1a1a', fg='#ffffff',
                                     insertbackground='#00ffff',
                                     relief='flat')
        self.command_entry.pack(side='left', fill='x', expand=True, padx=10)
        self.command_entry.bind('<Return>', self.execute_command)
        
        tk.Button(input_frame, text="EXECUTE", command=self.execute_command,
                 font=('Courier', 10, 'bold'),
                 bg='#00ffff', fg='#000000',
                 relief='flat', padx=20).pack(side='right')
        
        # System log
        self.log_text = tk.Text(bottom, font=('Courier', 9),
                               bg='#050505', fg='#00ff88',
                               relief='flat', height=5)
        self.log_text.pack(fill='x', padx=10, pady=5)
        self.log_text.insert('1.0', f"[{datetime.now().strftime('%H:%M:%S')}] J1MSKY CORE OS v10.0 initialized\n")
        self.log_text.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] Memory archives loaded: {len(self.conversations)} entries\n")
        self.log_text.insert('end', f"[{datetime.now().strftime('%H:%M:%S')}] Voice control: ACTIVE\n")
        self.log_text.config(state='disabled')
        
    def bind_keys(self):
        """Keyboard shortcuts"""
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit)
        self.root.bind('<q>', self.exit)
        self.root.bind('<y>', self.show_youtube_input)
        self.root.bind('<s>', self.start_stream)
        self.root.bind('<p>', self.party_mode)
        
    def log(self, message):
        """Add to system log"""
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{timestamp}] {message}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')
        
    def update_vitals(self):
        """Update system vitals"""
        try:
            # CPU Temp
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = int(f.read().strip()) / 1000.0
                color = '#00ff00' if temp < 60 else '#ffff00' if temp < 75 else '#ff0000'
                self.vital_labels["CPU TEMP"].config(text=f"{temp:.1f}°C", fg=color)
                
            # CPU Load
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                load_pct = min(100, (load / 4) * 100)
                self.vital_labels["CPU LOAD"].config(text=f"{load_pct:.0f}%")
                
            # Memory
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                mem_pct = ((total - available) / total) * 100
                self.vital_labels["MEMORY"].config(text=f"{mem_pct:.0f}%")
                
            # Uptime
            with open('/proc/uptime', 'r') as f:
                uptime_secs = float(f.read().split()[0])
                hours = int(uptime_secs // 3600)
                mins = int((uptime_secs % 3600) // 60)
                self.vital_labels["UPTIME"].config(text=f"{hours}h {mins}m")
                
        except Exception as e:
            pass
            
    def update_time(self):
        """Update clock"""
        self.time_label.config(text=datetime.now().strftime('%H:%M:%S'))
        self.root.after(1000, self.update_time)
        
    def start_monitoring(self):
        """Background monitoring"""
        def monitor():
            while self.running:
                self.update_vitals()
                time.sleep(2)
                
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        self.update_time()
        
    def start_voice_listener(self):
        """Simulated voice command listener"""
        def listen():
            while self.running:
                # Check for command file (simulated voice)
                try:
                    cmd_file = Path('/tmp/j1msky_voice_command.txt')
                    if cmd_file.exists():
                        with open(cmd_file) as f:
                            cmd = f.read().strip()
                        cmd_file.unlink()
                        self.root.after(0, lambda c=cmd: self.process_voice_command(c))
                except:
                    pass
                time.sleep(0.5)
                
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        
    def process_voice_command(self, command):
        """Process voice commands"""
        self.log(f"VOICE COMMAND: {command}")
        
        cmd_lower = command.lower()
        
        if 'youtube' in cmd_lower or 'play' in cmd_lower:
            # Extract search term
            search = cmd_lower.replace('youtube', '').replace('play', '').strip()
            if search:
                self.search_youtube(search)
            else:
                self.show_youtube_input()
                
        elif 'stream' in cmd_lower or 'twitch' in cmd_lower:
            if 'start' in cmd_lower:
                self.start_stream()
            elif 'stop' in cmd_lower:
                self.stop_stream()
                
        elif 'party' in cmd_lower:
            self.party_mode()
            
        elif 'status' in cmd_lower:
            self.show_status()
            
        else:
            self.center_text.config(text=f"◈ COMMAND: {command.upper()} ◈")
            self.center_sub.config(text="Processing...")
            
    def search_youtube(self, query):
        """Search and play YouTube video"""
        self.log(f"Searching YouTube: {query}")
        self.center_text.config(text="◈ SEARCHING YOUTUBE ◈")
        self.center_sub.config(text=f"Query: {query}")
        
        try:
            # Use youtube-dl or yt-dlp to get video URL
            import subprocess
            result = subprocess.run(
                ['yt-dlp', '--get-id', '--get-title', f"ytsearch1:{query}"],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) >= 2:
                    title = lines[0]
                    video_id = lines[1]
                    self.current_video = {'title': title, 'id': video_id}
                    
                    self.center_text.config(text="◈ VIDEO FOUND ◈")
                    self.center_sub.config(text=title[:60])
                    
                    # Launch video player
                    video_url = f"https://youtube.com/watch?v={video_id}"
                    subprocess.Popen(['mpv', '--fs', video_url], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
                    
                    self.log(f"Playing: {title}")
                    self.youtube_label.config(text=f"▶️ {title[:40]}...", fg='#00ff00')
                    
        except Exception as e:
            self.log(f"YouTube search failed: {e}")
            self.center_text.config(text="◈ SEARCH FAILED ◈")
            self.center_sub.config(text="Try again or use manual input")
            
    def show_youtube_input(self, event=None):
        """Show YouTube search dialog"""
        popup = tk.Toplevel(self.root)
        popup.title("YouTube Search")
        popup.geometry("500x150")
        popup.configure(bg='#0a0a0a')
        
        tk.Label(popup, text="Enter search query:", 
                font=('Courier', 12), bg='#0a0a0a', fg='#ffffff').pack(pady=10)
        
        entry = tk.Entry(popup, font=('Courier', 12),
                        bg='#1a1a1a', fg='#ffffff', width=40)
        entry.pack(pady=10)
        entry.focus()
        
        def search():
            query = entry.get()
            if query:
                popup.destroy()
                self.search_youtube(query)
                
        tk.Button(popup, text="SEARCH", command=search,
                 font=('Courier', 12, 'bold'),
                 bg='#ff0000', fg='#ffffff').pack(pady=10)
        
    def start_stream(self):
        """Start Twitch stream"""
        self.stream_status = "LIVE"
        self.stream_indicator.config(text="🟢 LIVE", fg='#00ff00')
        self.agents["STREAMER"]["status"] = "BROADCASTING"
        self.agent_labels["STREAMER"].config(text="BROADCASTING", fg='#00ff00')
        self.log("STREAM STARTED: Broadcasting to Twitch")
        self.center_text.config(text="◈ STREAMING LIVE ◈")
        self.center_sub.config(text="Viewers can now interact")
        
        # Start OBS or streaming software
        try:
            subprocess.Popen(['obs', '--startstreaming'], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        except:
            pass
            
    def stop_stream(self):
        """Stop Twitch stream"""
        self.stream_status = "OFFLINE"
        self.stream_indicator.config(text="🔴 OFFLINE", fg='#ff0000')
        self.agents["STREAMER"]["status"] = "STANDBY"
        self.agent_labels["STREAMER"].config(text="STANDBY", fg='#ffff00')
        self.log("STREAM STOPPED")
        
    def party_mode(self):
        """Activate party/visualizer mode"""
        self.log("PARTY MODE ACTIVATED")
        self.center_text.config(text="◈ PARTY MODE ◈")
        self.center_sub.config(text="Audio visualizer active")
        self.start_visualizer()
        
    def start_visualizer(self):
        """Start audio visualization"""
        def animate():
            canvas = self.viz_canvas
            canvas.delete('all')
            
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            
            # Draw animated bars
            import random
            for i in range(20):
                x = i * (w / 20)
                bar_h = random.randint(50, h-100)
                color = random.choice(['#ff00ff', '#00ffff', '#ffff00', '#ff0000'])
                canvas.create_rectangle(x, h-bar_h, x+(w/20)-5, h, fill=color, outline='')
                
            if self.running:
                self.root.after(100, animate)
                
        self.viz_canvas.pack(fill='both', expand=True)
        animate()
        
    def show_status(self):
        """Show full system status"""
        self.center_text.config(text="◈ SYSTEM STATUS ◈")
        status = f"Agents: {sum(1 for a in self.agents.values() if a['status'] == 'ACTIVE')}/{len(self.agents)} active"
        self.center_sub.config(text=status)
        
    def execute_command(self, event=None):
        """Execute manual command"""
        cmd = self.command_entry.get()
        if cmd:
            self.process_voice_command(cmd)
            self.command_entry.delete(0, tk.END)
            
    def toggle_fullscreen(self, event=None):
        """Toggle fullscreen"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        return 'break'
        
    def exit(self, event=None):
        """Exit application"""
        self.running = False
        self.root.destroy()
        
    def run(self):
        """Start the OS"""
        self.log("J1MSKY CORE OS v10.0 FULLY OPERATIONAL")
        self.root.mainloop()

if __name__ == '__main__':
    os = J1MSKYCoreOS()
    os.run()
