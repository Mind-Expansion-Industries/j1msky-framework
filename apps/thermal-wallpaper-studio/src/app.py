#!/usr/bin/env python3
"""
Thermal-Reactive Wallpaper Studio
Generates AI wallpapers based on Pi temperature with system tray control
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import subprocess
import threading
import time
import json
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request

# Add skill scripts to path
sys.path.insert(0, '/home/m1ndb0t/Desktop/J1MSKY/skills/replicate-image-gen/scripts')

class ThermalWallpaperStudio:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌡️ Thermal Wallpaper Studio")
        self.root.geometry("500x600")
        self.root.configure(bg='#1a1a2e')
        
        # Config
        self.config_file = Path.home() / '.config' / 'thermal-wallpaper-studio' / 'config.json'
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.load_config()
        
        # State
        self.current_temp = 0
        self.running = True
        self.generating = False
        self.total_cost = 0.0
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring
        self.start_monitoring()
        
    def load_config(self):
        defaults = {
            'cold_threshold': 60,
            'hot_threshold': 75,
            'auto_generate': False,  # DISABLED by default to save credits
            'api_token': os.environ.get('REPLICATE_API_TOKEN', ''),
            'total_cost': 0.0,
            'wallpaper_count': 0
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    saved = json.load(f)
                    defaults.update(saved)
            except:
                pass
        
        self.config = defaults
        self.total_cost = self.config.get('total_cost', 0.0)
        
    def save_config(self):
        self.config['total_cost'] = self.total_cost
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.root, text="🌡️ Thermal Wallpaper Studio", 
                        font=('Helvetica', 18, 'bold'),
                        bg='#1a1a2e', fg='#00d4ff')
        title.pack(pady=10)
        
        # Temperature Display
        self.temp_frame = tk.Frame(self.root, bg='#16213e', padx=20, pady=15)
        self.temp_frame.pack(fill='x', padx=20, pady=10)
        
        self.temp_label = tk.Label(self.temp_frame, text="--°C",
                                  font=('Helvetica', 48, 'bold'),
                                  bg='#16213e', fg='#00ff88')
        self.temp_label.pack()
        
        self.temp_status = tk.Label(self.temp_frame, text="Checking...",
                                   font=('Helvetica', 12),
                                   bg='#16213e', fg='#888888')
        self.temp_status.pack()
        
        # Quick Generate
        quick_frame = tk.Frame(self.root, bg='#1a1a2e')
        quick_frame.pack(fill='x', padx=20, pady=10)
        
        prompt_label = tk.Label(quick_frame, text="Quick Generate:",
                               font=('Helvetica', 11, 'bold'),
                               bg='#1a1a2e', fg='#ffffff')
        prompt_label.pack(anchor='w')
        
        self.prompt_entry = tk.Entry(quick_frame, font=('Helvetica', 11),
                                     bg='#0f3460', fg='#ffffff',
                                     insertbackground='white',
                                     relief='flat')
        self.prompt_entry.pack(fill='x', pady=5)
        self.prompt_entry.insert(0, "cyberpunk cityscape, neon lights, rain")
        
        btn_frame = tk.Frame(quick_frame, bg='#1a1a2e')
        btn_frame.pack(fill='x')
        
        self.gen_btn = tk.Button(btn_frame, text="🎨 Generate",
                                command=self.generate_custom,
                                bg='#e94560', fg='white',
                                font=('Helvetica', 10, 'bold'),
                                relief='flat', padx=15, pady=5)
        self.gen_btn.pack(side='left', padx=2)
        
        tk.Button(btn_frame, text="🎲 Lucky",
                 command=self.generate_lucky,
                 bg='#533483', fg='white',
                 font=('Helvetica', 10),
                 relief='flat', padx=10, pady=5).pack(side='left', padx=2)
        
        tk.Button(btn_frame, text="🌡️ Thermal",
                 command=self.generate_thermal,
                 bg='#00d4ff', fg='black',
                 font=('Helvetica', 10),
                 relief='flat', padx=10, pady=5).pack(side='left', padx=2)
        
        # Stats
        stats_frame = tk.Frame(self.root, bg='#16213e', padx=15, pady=10)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(stats_frame, text="📊 Statistics",
                font=('Helvetica', 11, 'bold'),
                bg='#16213e', fg='#ffffff').pack(anchor='w')
        
        self.stats_text = tk.Label(stats_frame, 
                                  text=f"Wallpapers: {self.config.get('wallpaper_count', 0)}\n"
                                       f"Est. Cost: ${self.total_cost:.2f}",
                                  font=('Helvetica', 10),
                                  bg='#16213e', fg='#aaaaaa',
                                  justify='left')
        self.stats_text.pack(anchor='w', pady=5)
        
        # Manual Mode Notice
        notice_frame = tk.Frame(self.root, bg='#0f3460', padx=15, pady=10)
        notice_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(notice_frame, text="✋ MANUAL MODE",
                font=('Helvetica', 12, 'bold'),
                bg='#0f3460', fg='#00ff88').pack()
        tk.Label(notice_frame, text="Images generate ONLY when you click a button",
                font=('Helvetica', 10),
                bg='#0f3460', fg='#aaaaaa').pack()
        tk.Label(notice_frame, text="💰 ~$0.04 per image",
                font=('Helvetica', 9),
                bg='#0f3460', fg='#ffaa00').pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        
        # Status bar
        self.status = tk.Label(self.root, text="Ready - Click a button to generate wallpaper",
                              bd=1, relief='sunken', anchor='w',
                              bg='#0f3460', fg='#888888')
        self.status.pack(side='bottom', fill='x')
        
        # Bind hotkey
        self.root.bind('<Return>', lambda e: self.generate_custom())
        
    def get_cpu_temp(self):
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                return int(f.read().strip()) / 1000.0
        except:
            return 50.0
    
    def update_temp_display(self):
        temp = self.get_cpu_temp()
        self.current_temp = temp
        
        # Update label
        self.temp_label.config(text=f"{temp:.1f}°C")
        
        # Color based on temp
        cold = int(self.cold_entry.get() or 60)
        hot = int(self.hot_entry.get() or 75)
        
        if temp < cold:
            color = '#00ff88'  # Green
            status = "🟢 Cool & Efficient"
            theme = "cold"
        elif temp < hot:
            color = '#ffaa00'  # Orange
            status = "🟡 Warm & Working"
            theme = "neutral"
        else:
            color = '#ff3366'  # Red
            status = "🔴 Hot & Throttling!"
            theme = "hot"
        
        self.temp_label.config(fg=color)
        self.temp_status.config(text=status, fg=color)
    
    def start_monitoring(self):
        """Just monitor temperature for display - NO auto-generation"""
        def monitor():
            while self.running:
                self.update_temp_display()
                time.sleep(5)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def generate_custom(self):
        prompt = self.prompt_entry.get()
        if prompt:
            self.generate_wallpaper(prompt)
    
    def generate_lucky(self):
        prompts = [
            "neon cyberpunk city at night with flying cars",
            "peaceful Japanese garden with cherry blossoms and koi pond",
            "futuristic space station orbiting a purple nebula",
            "retro 80s sunset with palm trees and grid lines",
            "underwater coral reef with bioluminescent creatures",
            "steampunk clockwork city with airships",
            "northern lights over snowy mountains",
            "abstract geometric art with gradient colors",
            "vintage library with floating books and warm lighting",
            "alien landscape with two moons and strange plants"
        ]
        import random
        prompt = random.choice(prompts)
        self.prompt_entry.delete(0, tk.END)
        self.prompt_entry.insert(0, prompt)
        self.generate_wallpaper(prompt)
    
    def generate_thermal(self):
        """Generate wallpaper based on current temperature - MANUAL ONLY"""
        temp = self.current_temp
        cold = self.config.get('cold_threshold', 60)
        hot = self.config.get('hot_threshold', 75)
        
        if temp < cold:
            prompts = [
                f"icy arctic landscape, aurora borealis, frozen glaciers, deep blue and cyan colors, calm serene atmosphere, 4k wallpaper",
                f"underwater ice cave, crystal formations, ethereal blue light filtering through, mysterious and cold, digital art",
                f"snow-covered mountain peak at dawn, crisp cold air, pale blue sky, minimalist and peaceful"
            ]
        elif temp < hot:
            prompts = [
                f"golden hour forest, warm sunlight through trees, balanced peaceful nature scene, earth tones, 4k wallpaper",
                f"gentle rolling hills at sunset, soft orange and purple gradient sky, serene landscape photography",
                f"misty lake reflection at twilight, balanced composition, calming neutral colors, atmospheric"
            ]
        else:
            prompts = [
                f"volcanic eruption with flowing lava, intense orange and red flames, dramatic powerful scene, 4k wallpaper",
                f"burning cyberpunk city, neon signs melting in heat, intense red and orange glow, chaotic energy",
                f"surface of the sun, solar flares, extreme heat visualization, fiery orange and yellow plasma"
            ]
        
        import random
        prompt = random.choice(prompts)
        self.generate_wallpaper(prompt, thermal=True)
    
    def generate_wallpaper(self, prompt, thermal=False):
        if self.generating:
            return
        
        self.generating = True
        self.gen_btn.config(state='disabled', text="⏳ Generating...")
        self.status.config(text="Generating image...", fg='#00d4ff')
        self.progress.pack(fill='x', padx=20, pady=5, before=self.status)
        self.progress.start()
        
        def do_generate():
            try:
                # Import replicate
                import replicate
                
                # Generate
                output = replicate.run(
                    "openai/gpt-image-1.5",
                    input={"prompt": prompt, "quality": "high"}
                )
                
                # Get URL
                if isinstance(output, list) and len(output) > 0:
                    url = output[0].url if hasattr(output[0], 'url') else str(output[0])
                elif hasattr(output, 'url'):
                    url = output.url
                else:
                    url = str(output)
                
                # Download
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = ".webp" if ".webp" in url else ".png"
                filename = f"wallpaper_{timestamp}{ext}"
                filepath = Path.home() / 'Pictures' / 'Wallpapers' / filename
                filepath.parent.mkdir(parents=True, exist_ok=True)
                
                urllib.request.urlretrieve(url, filepath)
                
                # Set wallpaper
                env = os.environ.copy()
                env['DISPLAY'] = ':0'
                env['XDG_RUNTIME_DIR'] = '/run/user/1000'
                subprocess.run(['pcmanfm', '--set-wallpaper', str(filepath)], 
                             capture_output=True, env=env)
                
                # Update stats
                self.config['wallpaper_count'] = self.config.get('wallpaper_count', 0) + 1
                self.total_cost += 0.04  # Rough estimate per image
                self.save_config()
                
                self.root.after(0, lambda: self.on_generate_complete(True, str(filepath)))
                
            except Exception as gen_error:
                self.root.after(0, lambda err=gen_error: self.on_generate_complete(False, str(err)))
        
        thread = threading.Thread(target=do_generate)
        thread.start()
    
    def on_generate_complete(self, success, message):
        self.generating = False
        self.gen_btn.config(state='normal', text="🎨 Generate")
        self.progress.stop()
        self.progress.pack_forget()
        
        if success:
            self.status.config(text=f"✅ Wallpaper set: {Path(message).name}", fg='#00ff88')
            self.stats_text.config(text=f"Wallpapers: {self.config.get('wallpaper_count', 0)}\n"
                                       f"Est. Cost: ${self.total_cost:.2f}")
        else:
            self.status.config(text=f"❌ Error: {message}", fg='#ff3366')
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        self.running = False
        self.save_config()
        self.root.destroy()

if __name__ == '__main__':
    app = ThermalWallpaperStudio()
    app.run()
