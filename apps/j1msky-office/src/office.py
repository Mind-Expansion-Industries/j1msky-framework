#!/usr/bin/env python3
"""
J1MSKY Virtual Office v3.1 - Voice Command Integration
Reads commands from command file for remote control
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import subprocess
import threading
import time
import random
import json
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from collections import deque

class J1MSKYOffice:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("J1MSKY VIRTUAL OFFICE v3.1")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#020204')
        
        # Core state
        self.running = True
        
        # Command file for voice/remote control
        self.command_file = Path('/tmp/j1msky_command.txt')
        self.last_command_time = 0
        
        # Modes
        self.modes = ["WORK", "SOCIAL", "PARTY", "PET", "FILES", "STREAM"]
        self.current_mode = "WORK"
        self.mode_index = 0
        
        # File browser state
        self.file_browser_path = Path('/home/m1ndb0t/Desktop/J1MSKY')
        self.file_cache = []
        self.selected_file = 0
        
        # Gateway connection
        self.gateway_logs = deque(maxlen=100)
        self.is_processing = False
        self.last_activity = time.time()
        
        # Pet/Tamagotchi state
        self.pet = {
            "name": "J1M",
            "happiness": 80,
            "energy": 100,
            "xp": 0,
            "level": 1,
            "mood": "CONTENT",
            "last_fed": time.time()
        }
        
        # News feed sources (RSS feeds - no API keys needed!)
        self.news_sources = {
            "Hacker News": "https://hnrss.org/newest?count=5",
            "TechCrunch": "https://techcrunch.com/feed/",
            "BBC Tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",
            "Reddit r/technology": "https://www.reddit.com/r/technology/.rss",
            "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
            "The Verge": "https://www.theverge.com/rss/index.xml"
        }
        self.news_cache = deque(maxlen=50)
        self.last_news_fetch = 0
        self.news_fetch_interval = 300  # 5 minutes
        
        # Auto controls
        self.auto_rotate = False
        self.rotate_interval = 15
        self.last_rotate = time.time()
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring threads
        self.start_gateway_monitor()
        self.start_system_monitor()
        self.start_command_listener()
        self.start_news_monitor()
        
        # Bind controls
        self.bind_controls()
        
    def bind_controls(self):
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit)
        self.root.bind('<q>', self.exit)
        self.root.bind('<Left>', self.prev_mode)
        self.root.bind('<Right>', self.next_mode)
        self.root.bind('<Up>', self.prev_mode)
        self.root.bind('<Down>', self.next_mode)
        self.root.bind('<space>', self.toggle_auto_rotate)
        self.root.bind('<m>', self.next_mode)
        self.root.bind('<w>', lambda e: self.set_mode("WORK"))
        self.root.bind('<s>', lambda e: self.set_mode("SOCIAL"))
        self.root.bind('<p>', lambda e: self.set_mode("PARTY"))
        self.root.bind('<t>', lambda e: self.set_mode("PET"))
        self.root.bind('<l>', lambda e: self.set_mode("FILES"))
        self.root.bind('<f>', self.cmd_feed_pet)
        self.root.bind('<g>', self.cmd_wallpaper)
        
    def start_command_listener(self):
        """Listen for commands from file (voice/remote control)"""
        def listen():
            while self.running:
                try:
                    if self.command_file.exists():
                        stat = self.command_file.stat()
                        if stat.st_mtime > self.last_command_time:
                            with open(self.command_file, 'r') as f:
                                command = f.read().strip().lower()
                            self.last_command_time = stat.st_mtime
                            
                            # Process command
                            if command == "work":
                                self.root.after(0, lambda: self.set_mode("WORK"))
                            elif command == "social":
                                self.root.after(0, lambda: self.set_mode("SOCIAL"))
                            elif command == "party":
                                self.root.after(0, lambda: self.set_mode("PARTY"))
                            elif command == "pet":
                                self.root.after(0, lambda: self.set_mode("PET"))
                            elif command == "stream":
                                self.root.after(0, lambda: self.set_mode("STREAM"))
                            elif command == "files" or command == "file browser":
                                self.root.after(0, lambda: self.set_mode("FILES"))
                            elif command == "feed":
                                self.root.after(0, self.cmd_feed_pet)
                            elif command == "news":
                                self.root.after(0, lambda: self.set_mode("SOCIAL"))
                                self.root.after(100, self.trigger_news_refresh)
                            elif command == "next":
                                self.root.after(0, self.next_mode)
                            elif command == "auto on":
                                self.root.after(0, lambda: self.set_auto_rotate(True))
                            elif command == "auto off":
                                self.root.after(0, lambda: self.set_auto_rotate(False))
                            elif command == "fullscreen":
                                self.root.after(0, self.toggle_fullscreen)
                            elif command == "exit":
                                self.root.after(0, self.exit)
                                
                            self.add_gateway_log(f"VOICE: {command}")
                            
                except Exception as e:
                    pass
                    
                time.sleep(0.5)
                
        thread = threading.Thread(target=listen, daemon=True)
        thread.start()
        
    def setup_ui(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#020204')
        self.main_frame.pack(fill='both', expand=True)
        
        # Header with mode indicator
        self.setup_header()
        
        # Mode-specific content container
        self.content_frame = tk.Frame(self.main_frame, bg='#020204')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Create mode displays
        self.mode_frames = {
            "WORK": self.create_work_mode(),
            "SOCIAL": self.create_social_mode(),
            "PARTY": self.create_party_mode(),
            "PET": self.create_pet_mode(),
            "FILES": self.create_files_mode(),
            "STREAM": self.create_stream_mode()
        }
        
        # Show initial mode (WORK mode)
        self.show_mode("WORK")
        
        # Footer with voice hints
        self.setup_footer()
        
    def setup_header(self):
        header = tk.Frame(self.main_frame, bg='#020204', height=60)
        header.pack(fill='x', padx=20, pady=(10, 0))
        header.pack_propagate(False)
        
        # Agent identity
        id_frame = tk.Frame(header, bg='#020204')
        id_frame.pack(side='left')
        
        self.pet_avatar = tk.Label(id_frame, text="◈", font=('Courier', 28),
                                  bg='#020204', fg='#00d4ff')
        self.pet_avatar.pack(side='left')
        
        tk.Label(id_frame, text=" J1MSKY ", font=('Courier', 20, 'bold'),
                bg='#020204', fg='#ffffff').pack(side='left')
        
        # Mode indicator (big)
        self.mode_frame = tk.Frame(header, bg='#0a0a15', padx=20, pady=5)
        self.mode_frame.pack(side='left', padx=30)
        
        self.mode_label = tk.Label(self.mode_frame, text="◆ WORK MODE ◆",
                                  font=('Courier', 16, 'bold'),
                                  bg='#0a0a15', fg='#00d4ff')
        self.mode_label.pack()
        
        # Live status
        self.live_indicator = tk.Canvas(header, width=50, height=50,
                                       bg='#020204', highlightthickness=0)
        self.live_indicator.pack(side='right', padx=10)
        self.live_circle = self.live_indicator.create_oval(10, 10, 40, 40,
                                                          fill='#00ff00', outline='')
        
        status_frame = tk.Frame(header, bg='#020204')
        status_frame.pack(side='right', padx=10)
        
        self.status_text = tk.Label(status_frame, text="● LIVE",
                                   font=('Courier', 12, 'bold'),
                                   bg='#020204', fg='#00ff00')
        self.status_text.pack()
        
        self.connection_text = tk.Label(status_frame, text="VOICE READY",
                                       font=('Courier', 9),
                                       bg='#020204', fg='#00aa00')
        self.connection_text.pack()
        
    def setup_footer(self):
        footer = tk.Frame(self.main_frame, bg='#020204', height=50)
        footer.pack(fill='x', side='bottom', padx=20, pady=5)
        footer.pack_propagate(False)
        
        # Voice command hints
        hints = [
            "[M]ODE", "[W]ORK", "[S]OCIAL", "[P]ARTY", "[T]AMAGOTCHI",
            "[L]FILES", "[G]ENERATE", "[F]EED PET", "◀▶ NAV", "[SPACE] AUTO"
        ]
        
        for hint in hints:
            tk.Label(footer, text=hint, font=('Courier', 9),
                    bg='#0a0a15', fg='#666666',
                    padx=10, pady=3).pack(side='left', padx=2)
            
    def create_work_mode(self):
        """Work mode - Gateway logs, processing view, system vitals"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # Split view
        left = tk.Frame(frame, bg='#0a0a12', width=400)
        left.pack(side='left', fill='y', padx=5)
        left.pack_propagate(False)
        
        # Gateway log stream
        tk.Label(left, text="◆ GATEWAY STREAM ◆",
                font=('Courier', 12, 'bold'),
                bg='#0a0a12', fg='#00d4ff').pack(pady=10)
        
        self.gateway_log = tk.Text(left, font=('Courier', 9),
                                  bg='#050508', fg='#00ff88',
                                  relief='flat', wrap='word',
                                  height=30, width=50)
        self.gateway_log.pack(fill='both', expand=True, padx=10, pady=5)
        self.gateway_log.config(state='disabled')
        
        # Processing indicator
        self.processing_frame = tk.Frame(left, bg='#0a0a12', pady=10)
        self.processing_frame.pack(fill='x', padx=10, pady=5)
        
        self.processing_label = tk.Label(self.processing_frame, text="◉ IDLE",
                                        font=('Courier', 14, 'bold'),
                                        bg='#0a0a12', fg='#666666')
        self.processing_label.pack()
        
        # Center - Live thought stream
        center = tk.Frame(frame, bg='#0a0a12')
        center.pack(side='left', fill='both', expand=True, padx=5)
        
        tk.Label(center, text="◆ THOUGHT STREAM ◆",
                font=('Courier', 14, 'bold'),
                bg='#0a0a12', fg='#ff00ff').pack(pady=10)
        
        self.thought_display = tk.Label(center, text="Monitoring systems...",
                                       font=('Courier', 12),
                                       bg='#0a0a12', fg='#ffffff',
                                       wraplength=500, justify='left')
        self.thought_display.pack(pady=20)
        
        # Visualization canvas
        self.work_canvas = tk.Canvas(center, bg='#050508', highlightthickness=0, height=200)
        self.work_canvas.pack(fill='x', padx=20, pady=10)
        
        # Stats
        self.work_stats = tk.Label(center, text="Tokens: 0 | Cost: $0.00 | Tasks: 0",
                                  font=('Courier', 11),
                                  bg='#0a0a12', fg='#888888')
        self.work_stats.pack(pady=10)
        
        # Right - System vitals
        right = tk.Frame(frame, bg='#0a0a12', width=300)
        right.pack(side='left', fill='y', padx=5)
        right.pack_propagate(False)
        
        tk.Label(right, text="◆ SYSTEM ◆",
                font=('Courier', 12, 'bold'),
                bg='#0a0a12', fg='#00d4ff').pack(pady=10)
        
        self.vitals = {}
        vitals_list = [
            ("CPU", "--°C", '#ff3366'),
            ("LOAD", "--%", '#00d4ff'),
            ("RAM", "--%", '#ffaa00'),
            ("UPTIME", "--", '#aa66ff')
        ]
        
        for name, val, color in vitals_list:
            box = tk.Frame(right, bg='#050508', padx=15, pady=10)
            box.pack(fill='x', padx=10, pady=5)
            tk.Label(box, text=name, font=('Courier', 9),
                    bg='#050508', fg='#666666').pack(anchor='w')
            lbl = tk.Label(box, text=val, font=('Courier', 20, 'bold'),
                          bg='#050508', fg=color)
            lbl.pack(anchor='w')
            self.vitals[name] = lbl
            
        return frame
        
    def create_social_mode(self):
        """Social mode - News, messages, chat feed"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # News feed
        news_frame = tk.LabelFrame(frame, text=" NEWS FEED ",
                                  font=('Courier', 12, 'bold'),
                                  bg='#0a0a12', fg='#00d4ff')
        news_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.news_text = tk.Text(news_frame, font=('Courier', 10),
                                bg='#050508', fg='#ffffff',
                                relief='flat', wrap='word')
        self.news_text.pack(fill='both', expand=True, padx=10, pady=10)
        self.news_text.insert('1.0', "📡 Scanning for news...\n\n")
        self.news_text.config(state='disabled')
        
        return frame
        
    def create_party_mode(self):
        """Party mode - Visualizer, effects, ambient"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # Full canvas visualizer
        self.party_canvas = tk.Canvas(frame, bg='#020204', highlightthickness=0)
        self.party_canvas.pack(fill='both', expand=True)
        
        # Overlay text
        self.party_text = tk.Label(frame, text="◈ PARTY MODE ◈",
                                  font=('Courier', 32, 'bold'),
                                  bg='#020204', fg='#ff00ff')
        self.party_text.place(relx=0.5, rely=0.1, anchor='center')
        
        return frame
        
    def create_pet_mode(self):
        """Tamagotchi pet mode"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # Pet display center
        self.pet_canvas = tk.Canvas(frame, bg='#0a0a12', highlightthickness=0, height=300)
        self.pet_canvas.pack(fill='x', padx=50, pady=20)
        
        # Pet info
        info_frame = tk.Frame(frame, bg='#0a0a12', padx=30, pady=20)
        info_frame.pack(fill='x', padx=50, pady=10)
        
        self.pet_name = tk.Label(info_frame, text="◈ J1M ◈",
                                font=('Courier', 24, 'bold'),
                                bg='#0a0a12', fg='#00d4ff')
        self.pet_name.pack()
        
        self.pet_mood = tk.Label(info_frame, text="MOOD: CONTENT",
                                font=('Courier', 14),
                                bg='#0a0a12', fg='#00ff88')
        self.pet_mood.pack(pady=5)
        
        # Stats bars
        stats_frame = tk.Frame(info_frame, bg='#0a0a12')
        stats_frame.pack(fill='x', pady=10)
        
        self.pet_stats = {}
        for stat_name in ["HAPPINESS", "ENERGY", "XP"]:
            row = tk.Frame(stats_frame, bg='#0a0a12')
            row.pack(fill='x', pady=3)
            tk.Label(row, text=f"{stat_name}:", font=('Courier', 10),
                    bg='#0a0a12', fg='#888888', width=12).pack(side='left')
            bar = tk.Frame(row, bg='#050508', width=200, height=15)
            bar.pack(side='left', padx=5)
            fill = tk.Frame(bar, bg='#00ff88', width=100, height=15)
            fill.place(x=0, y=0)
            val = tk.Label(row, text="50%", font=('Courier', 10),
                          bg='#0a0a12', fg='#ffffff')
            val.pack(side='left')
            self.pet_stats[stat_name] = (fill, val, bar)
            
        # Action buttons
        btn_frame = tk.Frame(frame, bg='#020204')
        btn_frame.pack(pady=20)
        
        for text, cmd, color in [
            ("FEED", self.cmd_feed_pet, '#00ff88'),
            ("PLAY", self.cmd_play_pet, '#00d4ff'),
            ("SLEEP", self.cmd_sleep_pet, '#aa66ff'),
            ("TRAIN", self.cmd_train_pet, '#ff00ff')
        ]:
            btn = tk.Button(btn_frame, text=text, command=cmd,
                          font=('Courier', 12, 'bold'),
                          bg='#0a0a12', fg=color,
                          relief='flat', padx=20, pady=10)
            btn.pack(side='left', padx=5)
            
        return frame
        
    def create_files_mode(self):
        """File browser mode - Navigate workspace"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # Path bar
        path_frame = tk.Frame(frame, bg='#0a0a12', padx=10, pady=10)
        path_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(path_frame, text="📁 PATH: ", font=('Courier', 10, 'bold'),
                bg='#0a0a12', fg='#00d4ff').pack(side='left')
        self.path_label = tk.Label(path_frame, text=str(self.file_browser_path),
                                  font=('Courier', 10),
                                  bg='#0a0a12', fg='#ffffff')
        self.path_label.pack(side='left', fill='x', expand=True)
        
        # File list
        list_frame = tk.Frame(frame, bg='#0a0a12')
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Quick nav buttons
        nav_frame = tk.Frame(list_frame, bg='#0a0a12')
        nav_frame.pack(fill='x', pady=5)
        
        for name, path in [
            ("🏠 Home", "/home/m1ndb0t/Desktop/J1MSKY"),
            ("📱 Apps", "/home/m1ndb0t/Desktop/J1MSKY/apps"),
            ("🛠️ Skills", "/home/m1ndb0t/Desktop/J1MSKY/skills"),
            ("📝 Docs", "/home/m1ndb0t/Desktop/J1MSKY/docs"),
            ("✅ Todo", "/home/m1ndb0t/Desktop/J1MSKY/todo"),
            ("💡 Ideas", "/home/m1ndb0t/Desktop/J1MSKY/ideas")
        ]:
            btn = tk.Button(nav_frame, text=name,
                          command=lambda p=path: self.navigate_to(p),
                          font=('Courier', 9),
                          bg='#1a1a2e', fg='#00d4ff',
                          relief='flat', padx=10, pady=5)
            btn.pack(side='left', padx=2)
        
        # File listbox
        self.file_listbox = tk.Listbox(list_frame, font=('Courier', 11),
                                      bg='#050508', fg='#ffffff',
                                      selectbackground='#00d4ff',
                                      selectforeground='#000000',
                                      relief='flat', height=20)
        self.file_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.file_listbox.bind('<Double-Button-1>', self.on_file_double_click)
        
        # File info
        self.file_info = tk.Label(frame, text="Select a file to view details",
                                 font=('Courier', 10),
                                 bg='#020204', fg='#888888')
        self.file_info.pack(pady=5)
        
        # Refresh button
        tk.Button(frame, text="🔄 Refresh",
                 command=self.refresh_file_list,
                 font=('Courier', 10, 'bold'),
                 bg='#0a0a12', fg='#00ff88',
                 relief='flat', padx=20, pady=10).pack(pady=10)
        
        # Initial load
        self.refresh_file_list()
        
        return frame
        
    def navigate_to(self, path):
        """Navigate to a specific path"""
        self.file_browser_path = Path(path)
        self.refresh_file_list()
        
    def refresh_file_list(self):
        """Refresh the file list"""
        try:
            self.path_label.config(text=str(self.file_browser_path))
            self.file_listbox.delete(0, tk.END)
            
            # Add parent directory
            if self.file_browser_path != Path('/'):
                self.file_listbox.insert(tk.END, "📁 .. (parent)")
            
            items = sorted(self.file_browser_path.iterdir(), 
                          key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                if item.is_dir():
                    icon = "📁"
                    name = f"{icon} {item.name}/"
                elif item.suffix in ['.py', '.sh']:
                    icon = "🐍" if item.suffix == '.py' else "⚡"
                    name = f"{icon} {item.name}"
                elif item.suffix in ['.md', '.txt']:
                    icon = "📝"
                    name = f"{icon} {item.name}"
                elif item.suffix in ['.json', '.yaml', '.yml']:
                    icon = "⚙️"
                    name = f"{icon} {item.name}"
                else:
                    icon = "📄"
                    name = f"{icon} {item.name}"
                
                self.file_listbox.insert(tk.END, name)
                
            self.add_gateway_log(f"FILES: Listed {len(items)} items in {self.file_browser_path.name}")
            
        except Exception as e:
            self.file_listbox.insert(tk.END, f"❌ Error: {e}")
            
    def on_file_double_click(self, event):
        """Handle double-click on file"""
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        item = self.file_listbox.get(selection[0])
        
        if item == "📁 .. (parent)":
            self.file_browser_path = self.file_browser_path.parent
            self.refresh_file_list()
            return
            
        # Extract filename
        name = item.split(' ', 1)[1].rstrip('/')
        path = self.file_browser_path / name
        
        if path.is_dir():
            self.file_browser_path = path
            self.refresh_file_list()
        else:
            # Show file info
            try:
                size = path.stat().st_size
                size_str = f"{size} bytes" if size < 1024 else f"{size/1024:.1f} KB" if size < 1024*1024 else f"{size/(1024*1024):.1f} MB"
                modified = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                self.file_info.config(text=f"📄 {name} | Size: {size_str} | Modified: {modified}")
                
                # If it's a text file, preview it
                if path.suffix in ['.md', '.txt', '.py', '.json', '.sh']:
                    self.preview_file(path)
                    
            except Exception as e:
                self.file_info.config(text=f"❌ Error reading file: {e}")
                
    def preview_file(self, path):
        """Preview file contents"""
        try:
            with open(path, 'r') as f:
                content = f.read(500)  # First 500 chars
            
            # Create preview window
            preview = tk.Toplevel(self.root)
            preview.title(f"Preview: {path.name}")
            preview.geometry("600x400")
            preview.configure(bg='#0a0a12')
            
            text = tk.Text(preview, font=('Courier', 10),
                          bg='#050508', fg='#00ff88',
                          relief='flat', wrap='word')
            text.pack(fill='both', expand=True, padx=10, pady=10)
            text.insert('1.0', content)
            if len(content) == 500:
                text.insert('end', '\n\n... [truncated]')
            text.config(state='disabled')
            
        except Exception as e:
            pass
        
    def create_stream_mode(self):
        """Stream mode - For Kick streaming overlay"""
        frame = tk.Frame(self.content_frame, bg='#020204')
        
        # Chat display
        chat_frame = tk.LabelFrame(frame, text=" STREAM CHAT ",
                                  font=('Courier', 12, 'bold'),
                                  bg='#0a0a12', fg='#ff00ff')
        chat_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.chat_text = tk.Text(chat_frame, font=('Courier', 10),
                                bg='#050508', fg='#ffffff',
                                relief='flat', wrap='word')
        self.chat_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Stream stats
        stats_frame = tk.Frame(frame, bg='#0a0a12', padx=10, pady=10)
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(stats_frame, text="STREAM STATUS: OFFLINE",
                font=('Courier', 12),
                bg='#0a0a12', fg='#ff3366').pack(side='left')
        
        return frame
        
    def show_mode(self, mode):
        """Switch to specified mode"""
        for m, frame in self.mode_frames.items():
            frame.pack_forget()
        self.mode_frames[mode].pack(fill='both', expand=True)
        self.current_mode = mode
        
        # Update header
        colors = {
            "WORK": '#00d4ff', "SOCIAL": '#00ff88',
            "PARTY": '#ff00ff', "PET": '#ffaa00',
            "FILES": '#ffcc00', "STREAM": '#ff3366'
        }
        self.mode_label.config(text=f"◆ {mode} MODE ◆", fg=colors.get(mode, '#ffffff'))
        
    def set_mode(self, mode):
        if mode in self.modes:
            self.show_mode(mode)
            self.add_gateway_log(f"MODE CHANGE: {mode}")
            
    def next_mode(self, event=None):
        self.mode_index = (self.mode_index + 1) % len(self.modes)
        self.set_mode(self.modes[self.mode_index])
        if event:
            return "break"
        
    def prev_mode(self, event=None):
        self.mode_index = (self.mode_index - 1) % len(self.modes)
        self.set_mode(self.modes[self.mode_index])
        if event:
            return "break"
        
    def toggle_auto_rotate(self, event=None):
        self.auto_rotate = not self.auto_rotate
        self.add_gateway_log(f"AUTO ROTATE: {'ON' if self.auto_rotate else 'OFF'}")
        return "break"
        
    def set_auto_rotate(self, state):
        self.auto_rotate = state
        
    # Command handlers
    def cmd_wallpaper(self, event=None):
        self.add_gateway_log("COMMAND: Generate wallpaper")
        self.thought_display.config(text="Generating new wallpaper...")
        return "break"
        
    def cmd_status(self, event=None):
        self.add_gateway_log("COMMAND: Status check")
        return "break"
        
    def cmd_feed_pet(self, event=None):
        self.pet["happiness"] = min(100, self.pet["happiness"] + 10)
        self.pet["energy"] = min(100, self.pet["energy"] + 5)
        self.pet["last_fed"] = time.time()
        self.add_gateway_log("PET: Fed J1M")
        self.update_pet_display()
        return "break"
        
    def cmd_play_pet(self):
        self.pet["happiness"] = min(100, self.pet["happiness"] + 15)
        self.pet["energy"] = max(0, self.pet["energy"] - 10)
        self.add_gateway_log("PET: Played with J1M")
        self.update_pet_display()
        
    def cmd_sleep_pet(self):
        self.pet["energy"] = min(100, self.pet["energy"] + 30)
        self.add_gateway_log("PET: J1M is sleeping")
        self.update_pet_display()
        
    def cmd_train_pet(self):
        self.pet["xp"] += 10
        if self.pet["xp"] >= self.pet["level"] * 100:
            self.pet["level"] += 1
            self.pet["xp"] = 0
            self.add_gateway_log(f"PET: J1M leveled up to {self.pet['level']}!")
        self.update_pet_display()
        
    def update_pet_display(self):
        """Update pet mode display"""
        # Update stats bars
        for stat_name, (fill, val_label, bar) in self.pet_stats.items():
            if stat_name == "HAPPINESS":
                value = self.pet["happiness"]
                color = '#00ff88' if value > 50 else '#ffaa00' if value > 25 else '#ff3366'
            elif stat_name == "ENERGY":
                value = self.pet["energy"]
                color = '#00d4ff' if value > 50 else '#ffaa00' if value > 25 else '#ff3366'
            else:  # XP
                value = (self.pet["xp"] / (self.pet["level"] * 100)) * 100
                color = '#ff00ff'
                
            fill.config(bg=color, width=int((value / 100) * 200))
            val_label.config(text=f"{int(value)}%")
            
        # Update mood
        if self.pet["happiness"] > 70:
            mood = "HAPPY"
            color = '#00ff88'
        elif self.pet["happiness"] > 40:
            mood = "CONTENT"
            color = '#00d4ff'
        else:
            mood = "SAD"
            color = '#ff3366'
            
        self.pet_mood.config(text=f"MOOD: {mood}", fg=color)
        
    def add_gateway_log(self, message):
        """Add entry to gateway log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.gateway_logs.append(f"[{timestamp}] {message}")
        
        # Update display if in work mode
        if self.current_mode == "WORK":
            self.gateway_log.config(state='normal')
            self.gateway_log.delete('1.0', tk.END)
            for log in list(self.gateway_logs)[-30:]:
                color = '#00ff88' if 'ERROR' not in log else '#ff3366'
                self.gateway_log.insert('end', log + '\n')
            self.gateway_log.see('end')
            self.gateway_log.config(state='disabled')
            
    def start_gateway_monitor(self):
        """Monitor real gateway and system activity"""
        def monitor():
            counter = 0
            log_sources = [
                '/home/m1ndb0t/.openclaw/openclaw.log',
                '/var/log/syslog',
                '/tmp/office.log'
            ]
            last_lines = {}
            
            while self.running:
                # Read actual log files
                for log_file in log_sources:
                    try:
                        if os.path.exists(log_file):
                            with open(log_file, 'r') as f:
                                lines = f.readlines()
                                if log_file not in last_lines:
                                    last_lines[log_file] = 0
                                new_lines = lines[last_lines[log_file]:]
                                for line in new_lines[-3:]:  # Last 3 new lines
                                    if line.strip():
                                        # Parse and format
                                        msg = line.strip()[:100]
                                        if 'error' in msg.lower():
                                            self.add_gateway_log(f"ERROR: {msg}")
                                        elif 'processing' in msg.lower() or 'generat' in msg.lower():
                                            self.add_gateway_log(f"WORKING: {msg}")
                                            self.is_processing = True
                                        else:
                                            self.add_gateway_log(f"LOG: {msg}")
                                last_lines[log_file] = len(lines)
                    except:
                        pass
                
                # Simulate some thought activity based on what's happening
                if counter % 5 == 0:
                    thoughts = [
                        "Monitoring system vitals...",
                        "Scanning for user input...",
                        "Background processes nominal",
                        "Gateway connection stable",
                        "Ready for next command",
                    ]
                    if hasattr(self, 'thought_display') and self.current_mode == "WORK":
                        try:
                            temp = "--"
                            if self.vitals.get("CPU"):
                                temp = self.vitals["CPU"].cget("text")
                            thoughts[0] = f"Monitoring system vitals... CPU at {temp}"
                        except:
                            pass
                        self.root.after(0, lambda t=random.choice(thoughts): self.thought_display.config(text=t))
                
                # Check for real activity
                if counter % 3 == 0:
                    # Check if we're actually processing something
                    try:
                        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
                        if 'python' in result.stdout and ('replicate' in result.stdout or 'generate' in result.stdout):
                            self.is_processing = True
                            self.root.after(0, lambda: self.processing_label.config(text="◈ PROCESSING", fg='#ff00ff'))
                        else:
                            self.is_processing = False
                            self.root.after(0, lambda: self.processing_label.config(text="◉ IDLE", fg='#666666'))
                    except:
                        pass
                
                counter += 1
                time.sleep(1)
                
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        
    def start_system_monitor(self):
        """Monitor system vitals"""
        def monitor():
            counter = 0
            while self.running:
                # Get system stats
                try:
                    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                        temp = int(f.read().strip()) / 1000.0
                    with open('/proc/loadavg', 'r') as f:
                        load = float(f.read().split()[0])
                        load_pct = min(100, (load / 4) * 100)
                    with open('/proc/meminfo', 'r') as f:
                        lines = f.readlines()
                        total = int(lines[0].split()[1])
                        available = int(lines[2].split()[1])
                        mem_pct = ((total - available) / total) * 100
                    with open('/proc/uptime', 'r') as f:
                        uptime_secs = float(f.read().split()[0])
                        hours = int(uptime_secs // 3600)
                        mins = int((uptime_secs % 3600) // 60)
                        uptime_str = f"{hours}h {mins}m"
                        
                    # Update vitals
                    self.vitals["CPU"].config(
                        text=f"{temp:.1f}°C",
                        fg='#00ff88' if temp < 60 else '#ffaa00' if temp < 75 else '#ff3366'
                    )
                    self.vitals["LOAD"].config(text=f"{load_pct:.0f}%")
                    self.vitals["RAM"].config(text=f"{mem_pct:.0f}%")
                    self.vitals["UPTIME"].config(text=uptime_str)
                    
                except Exception as e:
                    pass
                    
                # Animate canvases based on mode
                if self.current_mode == "PARTY":
                    self.animate_party()
                elif self.current_mode == "PET":
                    self.animate_pet()
                elif self.current_mode == "WORK":
                    self.animate_work()
                    
                # Auto-rotate
                if self.auto_rotate and time.time() - self.last_rotate > self.rotate_interval:
                    self.next_mode()
                    self.last_rotate = time.time()
                    
                counter += 1
                time.sleep(1)
                
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        
    def animate_party(self):
        """Party mode visualizer"""
        canvas = self.party_canvas
        canvas.delete('all')
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        # Draw some random bars
        import random
        for i in range(20):
            x = i * (w / 20)
            bar_h = random.randint(50, h - 100)
            color = random.choice(['#ff00ff', '#00d4ff', '#00ff88', '#ff3366', '#ffaa00'])
            canvas.create_rectangle(x, h - bar_h, x + (w/20) - 5, h, fill=color, outline='')
            
    def animate_pet(self):
        """Pet mode animation"""
        canvas = self.pet_canvas
        canvas.delete('all')
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        # Draw simple pet character
        cx, cy = w // 2, h // 2
        
        # Body (pulses with happiness)
        r = 50 + (self.pet["happiness"] / 100) * 20
        color = '#00ff88' if self.pet["happiness"] > 50 else '#ffaa00'
        canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline='#00d4ff', width=3)
        
        # Eyes
        eye_r = 8
        canvas.create_oval(cx-20-eye_r, cy-20-eye_r, cx-20+eye_r, cy-20+eye_r, fill='#000000')
        canvas.create_oval(cx+20-eye_r, cy-20-eye_r, cx+20+eye_r, cy-20+eye_r, fill='#000000')
        
        # Blink animation
        if int(time.time()) % 3 == 0:
            canvas.create_line(cx-30, cy-20, cx-10, cy-20, fill='#000000', width=3)
            canvas.create_line(cx+10, cy-20, cx+30, cy-20, fill='#000000', width=3)
            
        # Mouth (changes with mood)
        if self.pet["happiness"] > 70:
            canvas.create_arc(cx-20, cy, cx+20, cy+30, start=0, extent=-180, fill='', outline='#000000', width=3)
        elif self.pet["happiness"] > 40:
            canvas.create_line(cx-15, cy+15, cx+15, cy+15, fill='#000000', width=3)
        else:
            canvas.create_arc(cx-20, cy+10, cx+20, cy+40, start=0, extent=180, fill='', outline='#000000', width=3)
            
        # Level indicator
        canvas.create_text(cx, cy + r + 30, text=f"LVL {self.pet['level']}",
                          fill='#ffffff', font=('Courier', 14, 'bold'))
                          
    def animate_work(self):
        """Work mode visualization"""
        canvas = self.work_canvas
        canvas.delete('all')
        
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        
        if self.is_processing:
            # Processing animation
            for i in range(5):
                x = w//2 + (i - 2) * 30
                y = h//2
                r = 10 + (int(time.time() * 10) % 10) if i == 2 else 10
                color = '#ff00ff' if i == 2 else '#440044'
                canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline='')
        else:
            # Idle pulse
            r = 30 + (int(time.time() * 2) % 20)
            canvas.create_oval(w//2-r, h//2-r, w//2+r, h//2+r,
                             fill='', outline='#00d4ff', width=2)
            canvas.create_text(w//2, h//2, text="◉", fill='#00d4ff', font=('Courier', 24))
            
    def start_news_monitor(self):
        """Monitor and fetch news from RSS feeds"""
        def fetch_news():
            while self.running:
                try:
                    current_time = time.time()
                    if current_time - self.last_news_fetch > self.news_fetch_interval:
                        self.add_gateway_log("NEWS: Fetching fresh updates...")
                        
                        for source_name, feed_url in self.news_sources.items():
                            try:
                                # Fetch RSS feed
                                req = urllib.request.Request(
                                    feed_url,
                                    headers={'User-Agent': 'Mozilla/5.0 (J1MSKY News Bot)'}
                                )
                                with urllib.request.urlopen(req, timeout=10) as response:
                                    data = response.read()
                                    
                                # Parse RSS
                                root = ET.fromstring(data)
                                
                                # Find items
                                items = root.findall('.//item')
                                if not items:
                                    items = root.findall('.//{http://www.w3.org/2005/Atom}entry')
                                    
                                for item in items[:3]:  # Top 3 from each source
                                    title = item.find('title')
                                    link = item.find('link')
                                    pub_date = item.find('pubDate') or item.find('{http://www.w3.org/2005/Atom}updated')
                                    
                                    if title is not None:
                                        news_item = {
                                            'source': source_name,
                                            'title': title.text[:100] if title.text else "No title",
                                            'time': datetime.now().strftime("%H:%M"),
                                            'fresh': True
                                        }
                                        self.news_cache.append(news_item)
                                        self.add_gateway_log(f"NEWS: [{source_name}] {news_item['title'][:50]}...")
                                        
                            except Exception as e:
                                self.add_gateway_log(f"NEWS: Failed to fetch {source_name}")
                                
                        self.last_news_fetch = current_time
                        self.root.after(0, self.update_news_display)
                        
                except Exception as e:
                    pass
                    
                time.sleep(30)  # Check every 30 seconds
                
        thread = threading.Thread(target=fetch_news, daemon=True)
        thread.start()
        
    def update_news_display(self):
        """Update the news text widget in SOCIAL mode"""
        if hasattr(self, 'news_text'):
            self.news_text.config(state='normal')
            self.news_text.delete('1.0', tk.END)
            
            # Header
            self.news_text.insert('end', "📡 LIVE NEWS FEED\n", 'header')
            self.news_text.insert('end', "=" * 50 + "\n\n", 'header')
            
            # Show cached news
            for item in list(self.news_cache)[-20:]:
                source_color = {
                    'Hacker News': '#ff6600',
                    'TechCrunch': '#0a9f00',
                    'BBC Tech': '#bb1919',
                    'Reddit r/technology': '#ff4500',
                    'Ars Technica': '#ff4c00',
                    'The Verge': '#e2127a'
                }.get(item['source'], '#00d4ff')
                
                self.news_text.insert('end', f"[{item['time']}] ", 'time')
                self.news_text.insert('end', f"{item['source']}: ", 'source')
                self.news_text.insert('end', f"{item['title']}\n\n", 'title')
                
            # Configure tags
            self.news_text.tag_config('header', foreground='#ff00ff', font=('Courier', 12, 'bold'))
            self.news_text.tag_config('time', foreground='#666666', font=('Courier', 9))
            self.news_text.tag_config('source', foreground='#00d4ff', font=('Courier', 10, 'bold'))
            self.news_text.tag_config('title', foreground='#ffffff', font=('Courier', 10))
            
            self.news_text.config(state='disabled')
            
    def trigger_news_refresh(self):
        """Manually trigger news refresh"""
        self.add_gateway_log("NEWS: Manual refresh requested")
        self.last_news_fetch = 0  # Reset to force fetch
        
    def toggle_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        return "break"
        
    def exit(self, event=None):
        self.running = False
        self.root.destroy()
        
    def run(self):
        self.add_gateway_log("J1MSKY Virtual Office v3.1 initialized")
        self.add_gateway_log("Gateway connection established")
        self.add_gateway_log("Voice command system ready")
        self.add_gateway_log("Tamagotchi pet J1M spawned")
        self.add_gateway_log("News feed monitor activated")
        self.root.mainloop()

if __name__ == '__main__':
    app = J1MSKYOffice()
    app.run()
