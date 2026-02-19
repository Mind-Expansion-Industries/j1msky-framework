#!/usr/bin/env python3
"""
J1MSKY Flipper GUI Control Panel
Integrated dashboard for Flipper Zero control
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import serial
import threading
import time
import json
from pathlib import Path

class FlipperGUI:
    def __init__(self, parent=None):
        # If no parent, create standalone window
        if parent is None:
            self.root = tk.Tk()
            self.root.title("◈ J1MSKY FLIPPER CONTROL ◈")
            self.root.geometry("900x700")
            self.root.configure(bg='#0a0a0f')
        else:
            self.root = parent
            
        self.serial = None
        self.connected = False
        self.scanning = False
        
        # Signal database
        self.signals_file = Path('/home/m1ndb0t/Desktop/J1MSKY/j1msky-framework/flipper/signals.json')
        self.captured_signals = self.load_signals()
        
        self.build_ui()
        
    def build_ui(self):
        """Build the Flipper control interface"""
        # Main container
        main = tk.Frame(self.root, bg='#0a0a0f')
        main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Frame(main, bg='#0d0d12', height=60)
        header.pack(fill='x', pady=(0, 10))
        header.pack_propagate(False)
        
        tk.Label(header, text="◈ FLIPPER CONTROL ◈", 
                font=('Courier', 24, 'bold'),
                bg='#0d0d12', fg='#ff6600').pack(side='left', padx=20, pady=10)
        
        self.status_label = tk.Label(header, text="● DISCONNECTED",
                                    font=('Courier', 14),
                                    bg='#0d0d12', fg='#ff0000')
        self.status_label.pack(side='right', padx=20)
        
        # Connection panel
        conn_frame = tk.LabelFrame(main, text=" CONNECTION ",
                                   font=('Courier', 12, 'bold'),
                                   bg='#0d0d12', fg='#00ffff')
        conn_frame.pack(fill='x', pady=5)
        
        conn_inner = tk.Frame(conn_frame, bg='#0d0d12')
        conn_inner.pack(padx=10, pady=10)
        
        tk.Label(conn_inner, text="Port:", 
                font=('Courier', 11),
                bg='#0d0d12', fg='#ffffff').pack(side='left')
        
        self.port_entry = tk.Entry(conn_inner, font=('Courier', 11),
                                   bg='#1a1a1f', fg='#ffffff',
                                   width=20)
        self.port_entry.pack(side='left', padx=5)
        self.port_entry.insert(0, "/dev/ttyACM0")
        
        self.connect_btn = tk.Button(conn_inner, text="CONNECT",
                                    command=self.toggle_connection,
                                    font=('Courier', 11, 'bold'),
                                    bg='#00ff00', fg='#000000',
                                    relief='flat', padx=20)
        self.connect_btn.pack(side='left', padx=10)
        
        # Tabs for different functions
        tabs = ttk.Notebook(main)
        tabs.pack(fill='both', expand=True, pady=10)
        
        # Style the tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#0a0a0f')
        style.configure('TNotebook.Tab', background='#1a1a1f', foreground='#ffffff')
        style.map('TNotebook.Tab', background=[('selected', '#ff6600')])
        
        # Tab 1: SubGHz (RF)
        self.rf_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.rf_tab, text="📡 SubGHz (RF)")
        self.build_rf_tab()
        
        # Tab 2: NFC
        self.nfc_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.nfc_tab, text="📱 NFC")
        self.build_nfc_tab()
        
        # Tab 3: IR
        self.ir_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.ir_tab, text="📺 IR Remote")
        self.build_ir_tab()
        
        # Tab 4: GPIO
        self.gpio_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.gpio_tab, text="🔌 GPIO")
        self.build_gpio_tab()
        
        # Tab 5: BadUSB
        self.usb_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.usb_tab, text="💻 BadUSB")
        self.build_usb_tab()
        
        # Tab 6: Signal Database
        self.db_tab = tk.Frame(tabs, bg='#0a0a0f')
        tabs.add(self.db_tab, text="🗄️ Database")
        self.build_db_tab()
        
        # Console output
        console_frame = tk.LabelFrame(main, text=" CONSOLE ",
                                      font=('Courier', 11, 'bold'),
                                      bg='#0d0d12', fg='#00ffff')
        console_frame.pack(fill='x', pady=5)
        
        self.console = scrolledtext.ScrolledText(console_frame,
                                                  font=('Courier', 10),
                                                  bg='#050508', fg='#00ff00',
                                                  height=8,
                                                  relief='flat')
        self.console.pack(fill='both', expand=True, padx=5, pady=5)
        self.console.insert('end', "◈ J1MSKY Flipper Control Ready ◈\n")
        self.console.insert('end', "Click CONNECT to begin...\n")
        self.console.config(state='disabled')
        
    def build_rf_tab(self):
        """Build SubGHz/RF control tab"""
        # Left side - Scanner
        left = tk.Frame(self.rf_tab, bg='#0a0a0f')
        left.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(left, text="📡 RF SCANNER",
                font=('Courier', 14, 'bold'),
                bg='#0a0a0f', fg='#ff6600').pack(pady=10)
        
        # Frequency presets
        freqs_frame = tk.LabelFrame(left, text=" FREQUENCY PRESETS ",
                                    font=('Courier', 10),
                                    bg='#0d0d12', fg='#ffffff')
        freqs_frame.pack(fill='x', padx=5, pady=5)
        
        frequencies = [
            ("300.00 MHz", "300000000"),
            ("315.00 MHz", "315000000"),
            ("390.00 MHz", "390000000"),
            ("433.92 MHz", "433920000"),
            ("868.35 MHz", "868350000"),
            ("915.00 MHz", "915000000")
        ]
        
        for name, freq in frequencies:
            btn = tk.Button(freqs_frame, text=f"SCAN {name}",
                          command=lambda f=freq: self.scan_frequency(f),
                          font=('Courier', 9),
                          bg='#1a1a1f', fg='#00ffff',
                          relief='flat')
            btn.pack(fill='x', padx=5, pady=2)
            
        # Custom frequency
        custom_frame = tk.Frame(left, bg='#0a0a0f')
        custom_frame.pack(fill='x', padx=5, pady=10)
        
        tk.Label(custom_frame, text="Custom (Hz):",
                bg='#0a0a0f', fg='#ffffff').pack(side='left')
        self.custom_freq = tk.Entry(custom_frame, font=('Courier', 10),
                                   bg='#1a1a1f', fg='#ffffff',
                                   width=15)
        self.custom_freq.pack(side='left', padx=5)
        self.custom_freq.insert(0, "433920000")
        
        tk.Button(custom_frame, text="SCAN",
                 command=lambda: self.scan_frequency(self.custom_freq.get()),
                 bg='#ff6600', fg='#000000',
                 font=('Courier', 9, 'bold')).pack(side='left')
        
        # Scan duration
        dur_frame = tk.Frame(left, bg='#0a0a0f')
        dur_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(dur_frame, text="Duration:",
                bg='#0a0a0f', fg='#ffffff').pack(side='left')
        self.scan_duration = tk.Spinbox(dur_frame, from_=5, to=60, width=5,
                                       font=('Courier', 10))
        self.scan_duration.pack(side='left', padx=5)
        self.scan_duration.delete(0, 'end')
        self.scan_duration.insert(0, "10")
        tk.Label(dur_frame, text="seconds",
                bg='#0a0a0f', fg='#666666').pack(side='left')
        
        # Garage door scanner
        tk.Button(left, text="🚗 SCAN GARAGE DOORS (All Freqs)",
                 command=self.scan_garage_doors,
                 font=('Courier', 11, 'bold'),
                 bg='#ff0000', fg='#ffffff',
                 relief='flat').pack(fill='x', padx=20, pady=20)
        
        # Right side - Transmitter
        right = tk.Frame(self.rf_tab, bg='#0a0a0f')
        right.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(right, text="📤 TRANSMITTER",
                font=('Courier', 14, 'bold'),
                bg='#0a0a0f', fg='#00ff00').pack(pady=10)
        
        # Signal selector
        tx_frame = tk.LabelFrame(right, text=" TRANSMIT SIGNAL ",
                                 font=('Courier', 10),
                                 bg='#0d0d12', fg='#ffffff')
        tx_frame.pack(fill='x', padx=5, pady=5)
        
        self.signal_listbox = tk.Listbox(tx_frame, font=('Courier', 9),
                                         bg='#1a1a1f', fg='#00ffff',
                                         height=8)
        self.signal_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.refresh_signals_btn = tk.Button(tx_frame, text="REFRESH LIST",
                                            command=self.refresh_signal_list,
                                            font=('Courier', 9),
                                            bg='#333333', fg='#ffffff')
        self.refresh_signals_btn.pack(fill='x', padx=5, pady=2)
        
        tk.Button(tx_frame, text="TRANMIT SELECTED",
                 command=self.transmit_signal,
                 font=('Courier', 10, 'bold'),
                 bg='#00ff00', fg='#000000').pack(fill='x', padx=5, pady=5)
        
    def build_nfc_tab(self):
        """Build NFC control tab"""
        tk.Label(self.nfc_tab, text="📱 NFC CONTROL",
                font=('Courier', 16, 'bold'),
                bg='#0a0a0f', fg='#00ffff').pack(pady=20)
        
        # Read section
        read_frame = tk.LabelFrame(self.nfc_tab, text=" READ TAG ",
                                   font=('Courier', 11),
                                   bg='#0d0d12', fg='#ffffff')
        read_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(read_frame, text="SCAN FOR NFC TAG",
                 command=self.nfc_read,
                 font=('Courier', 12, 'bold'),
                 bg='#00ffff', fg='#000000',
                 relief='flat').pack(padx=20, pady=20)
        
        self.nfc_result = tk.Text(read_frame, font=('Courier', 10),
                                  bg='#050508', fg='#00ff00',
                                  height=6,
                                  relief='flat')
        self.nfc_result.pack(fill='x', padx=10, pady=10)
        
        # Emulate section
        emu_frame = tk.LabelFrame(self.nfc_tab, text=" EMULATE TAG ",
                                  font=('Courier', 11),
                                  bg='#0d0d12', fg='#ffffff')
        emu_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(emu_frame, text="UID (hex):",
                bg='#0d0d12', fg='#ffffff').pack(side='left', padx=5)
        
        self.nfc_uid = tk.Entry(emu_frame, font=('Courier', 10),
                               bg='#1a1a1f', fg='#ffffff',
                               width=20)
        self.nfc_uid.pack(side='left', padx=5)
        self.nfc_uid.insert(0, "04:XX:XX:XX:XX:XX:XX")
        
        tk.Button(emu_frame, text="EMULATE",
                 command=self.nfc_emulate,
                 font=('Courier', 10, 'bold'),
                 bg='#ff6600', fg='#000000').pack(side='left', padx=10)
        
    def build_ir_tab(self):
        """Build IR remote tab"""
        tk.Label(self.ir_tab, text="📺 IR REMOTE CONTROL",
                font=('Courier', 16, 'bold'),
                bg='#0a0a0f', fg='#ff0000').pack(pady=20)
        
        # Device presets
        devices = [
            ("TV - Power", "NEC", "00", "01"),
            ("TV - Volume Up", "NEC", "00", "02"),
            ("TV - Volume Down", "NEC", "00", "03"),
            ("AC - Power", "NEC", "01", "01"),
            ("AC - Temp Up", "NEC", "01", "02"),
            ("Projector - Power", "NEC", "02", "01")
        ]
        
        btn_frame = tk.Frame(self.ir_tab, bg='#0a0a0f')
        btn_frame.pack(padx=20, pady=10)
        
        for i, (name, proto, addr, cmd) in enumerate(devices):
            btn = tk.Button(btn_frame, text=name,
                          command=lambda p=proto, a=addr, c=cmd: self.ir_send(p, a, c),
                          font=('Courier', 10),
                          bg='#1a1a1f', fg='#ff0000',
                          width=20,
                          relief='flat')
            btn.grid(row=i//2, column=i%2, padx=5, pady=5)
            
        # Custom IR
        custom_frame = tk.LabelFrame(self.ir_tab, text=" CUSTOM IR ",
                                     font=('Courier', 11),
                                     bg='#0d0d12', fg='#ffffff')
        custom_frame.pack(fill='x', padx=20, pady=20)
        
        fields = [
            ("Protocol:", "ir_proto", "NEC"),
            ("Address:", "ir_addr", "00"),
            ("Command:", "ir_cmd", "01")
        ]
        
        for label, name, default in fields:
            row = tk.Frame(custom_frame, bg='#0d0d12')
            row.pack(fill='x', padx=5, pady=2)
            
            tk.Label(row, text=label,
                    bg='#0d0d12', fg='#ffffff').pack(side='left')
            
            entry = tk.Entry(row, font=('Courier', 10),
                           bg='#1a1a1f', fg='#ffffff',
                           width=15)
            entry.pack(side='left', padx=5)
            entry.insert(0, default)
            setattr(self, name, entry)
            
        tk.Button(custom_frame, text="SEND IR SIGNAL",
                 command=lambda: self.ir_send(
                     self.ir_proto.get(),
                     self.ir_addr.get(),
                     self.ir_cmd.get()
                 ),
                 font=('Courier', 11, 'bold'),
                 bg='#ff0000', fg='#ffffff').pack(pady=10)
        
    def build_gpio_tab(self):
        """Build GPIO control tab"""
        tk.Label(self.gpio_tab, text="🔌 GPIO CONTROL",
                font=('Courier', 16, 'bold'),
                bg='#0a0a0f', fg='#ffff00').pack(pady=20)
        
        # Pin grid
        pin_frame = tk.Frame(self.gpio_tab, bg='#0a0a0f')
        pin_frame.pack(padx=20, pady=10)
        
        tk.Label(pin_frame, text="PIN",
                font=('Courier', 11, 'bold'),
                bg='#0a0a0f', fg='#ffffff').grid(row=0, column=0, padx=5)
        tk.Label(pin_frame, text="STATE",
                font=('Courier', 11, 'bold'),
                bg='#0a0a0f', fg='#ffffff').grid(row=0, column=1, padx=5)
        tk.Label(pin_frame, text="CONTROL",
                font=('Courier', 11, 'bold'),
                bg='#0a0a0f', fg='#ffffff').grid(row=0, column=2, padx=5)
        
        self.gpio_vars = {}
        for pin in range(8):
            tk.Label(pin_frame, text=f"GPIO {pin}",
                    bg='#0a0a0f', fg='#00ffff').grid(row=pin+1, column=0, padx=5, pady=2)
            
            var = tk.StringVar(value="UNKNOWN")
            self.gpio_vars[pin] = var
            
            tk.Label(pin_frame, textvariable=var,
                    font=('Courier', 10),
                    bg='#1a1a1f', fg='#ffffff',
                    width=10).grid(row=pin+1, column=1, padx=5, pady=2)
            
            btn_frame = tk.Frame(pin_frame, bg='#0a0a0f')
            btn_frame.grid(row=pin+1, column=2, padx=5, pady=2)
            
            tk.Button(btn_frame, text="ON",
                     command=lambda p=pin: self.gpio_set(p, 1),
                     bg='#00ff00', fg='#000000',
                     width=5).pack(side='left', padx=2)
            
            tk.Button(btn_frame, text="OFF",
                     command=lambda p=pin: self.gpio_set(p, 0),
                     bg='#ff0000', fg='#ffffff',
                     width=5).pack(side='left', padx=2)
            
            tk.Button(btn_frame, text="READ",
                     command=lambda p=pin: self.gpio_read(p),
                     bg='#333333', fg='#ffffff',
                     width=5).pack(side='left', padx=2)
            
    def build_usb_tab(self):
        """Build BadUSB tab"""
        tk.Label(self.usb_tab, text="💻 BADUSB SCRIPTS",
                font=('Courier', 16, 'bold'),
                bg='#0a0a0f', fg='#ff00ff').pack(pady=20)
        
        # Script presets
        scripts = [
            ("Hello World", "/ext/badusb/demo.txt"),
            ("Rickroll", "/ext/badusb/rickroll.txt"),
            ("Reverse Shell", "/ext/badusb/reverse.txt")
        ]
        
        for name, path in scripts:
            btn = tk.Button(self.usb_tab, text=f"RUN: {name}",
                          command=lambda p=path: self.badusb_run(p),
                          font=('Courier', 11),
                          bg='#1a1a1f', fg='#ff00ff',
                          relief='flat',
                          width=30)
            btn.pack(pady=5)
            
        # Custom script
        custom_frame = tk.LabelFrame(self.usb_tab, text=" CUSTOM SCRIPT ",
                                     font=('Courier', 11),
                                     bg='#0d0d12', fg='#ffffff')
        custom_frame.pack(fill='x', padx=20, pady=20)
        
        self.usb_path = tk.Entry(custom_frame, font=('Courier', 10),
                                bg='#1a1a1f', fg='#ffffff',
                                width=40)
        self.usb_path.pack(padx=5, pady=5)
        self.usb_path.insert(0, "/ext/badusb/myscript.txt")
        
        tk.Button(custom_frame, text="RUN SCRIPT",
                 command=lambda: self.badusb_run(self.usb_path.get()),
                 font=('Courier', 11, 'bold'),
                 bg='#ff00ff', fg='#000000').pack(pady=5)
        
    def build_db_tab(self):
        """Build signal database tab"""
        tk.Label(self.db_tab, text="🗄️ SIGNAL DATABASE",
                font=('Courier', 16, 'bold'),
                bg='#0a0a0f', fg='#00ff00').pack(pady=20)
        
        # Stats
        self.db_stats = tk.Label(self.db_tab, 
                                text=f"Stored Signals: {len(self.captured_signals)}",
                                font=('Courier', 12),
                                bg='#0a0a0f', fg='#00ff00')
        self.db_stats.pack(pady=10)
        
        # Signal list
        list_frame = tk.LabelFrame(self.db_tab, text=" CAPTURED SIGNALS ",
                                   font=('Courier', 11),
                                   bg='#0d0d12', fg='#ffffff')
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.db_listbox = tk.Listbox(list_frame, font=('Courier', 9),
                                     bg='#1a1a1f', fg='#00ffff',
                                     selectbackground='#ff6600')
        self.db_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Buttons
        btn_frame = tk.Frame(self.db_tab, bg='#0a0a0f')
        btn_frame.pack(fill='x', padx=20, pady=5)
        
        tk.Button(btn_frame, text="EXPORT JSON",
                 command=self.export_signals,
                 font=('Courier', 10),
                 bg='#333333', fg='#ffffff').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="IMPORT JSON",
                 command=self.import_signals,
                 font=('Courier', 10),
                 bg='#333333', fg='#ffffff').pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="CLEAR ALL",
                 command=self.clear_signals,
                 font=('Courier', 10),
                 bg='#ff0000', fg='#ffffff').pack(side='right', padx=5)
        
        self.refresh_signal_list()
        
    # Connection methods
    def toggle_connection(self):
        """Toggle Flipper connection"""
        if not self.connected:
            self.connect()
        else:
            self.disconnect()
            
    def connect(self):
        """Connect to Flipper"""
        try:
            port = self.port_entry.get()
            self.serial = serial.Serial(port, 115200, timeout=2)
            time.sleep(2)
            
            # Clear buffer
            if self.serial.in_waiting:
                self.serial.read(self.serial.in_waiting)
                
            self.connected = True
            self.status_label.config(text="● CONNECTED", fg='#00ff00')
            self.connect_btn.config(text="DISCONNECT", bg='#ff0000')
            self.log("Connected to Flipper Zero!")
            
            # Start heartbeat
            self.heartbeat_thread = threading.Thread(target=self.heartbeat, daemon=True)
            self.heartbeat_thread.start()
            
        except Exception as e:
            self.log(f"Connection failed: {e}")
            
    def disconnect(self):
        """Disconnect from Flipper"""
        if self.serial:
            self.serial.close()
        self.connected = False
        self.status_label.config(text="● DISCONNECTED", fg='#ff0000')
        self.connect_btn.config(text="CONNECT", bg='#00ff00')
        self.log("Disconnected")
        
    def heartbeat(self):
        """Keep connection alive"""
        while self.connected:
            try:
                self.serial.write(b'\n')
                time.sleep(30)
            except:
                break
                
    # Command methods
    def send_command(self, cmd, wait=1):
        """Send command to Flipper"""
        if not self.connected:
            self.log("Not connected!")
            return None
            
        try:
            self.serial.write(f"{cmd}\n".encode())
            time.sleep(wait)
            
            response = b""
            while self.serial.in_waiting:
                response += self.serial.read(self.serial.in_waiting)
                time.sleep(0.1)
                
            text = response.decode('utf-8', errors='ignore')
            # Clean ANSI codes
            import re
            text = re.sub(r'\x1b\[[0-9;]*[mK]', '', text)
            return text
            
        except Exception as e:
            self.log(f"Command error: {e}")
            return None
            
    def log(self, message):
        """Log to console"""
        self.console.config(state='normal')
        self.console.insert('end', f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.console.see('end')
        self.console.config(state='disabled')
        
    # RF methods
    def scan_frequency(self, freq):
        """Scan specific frequency"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        duration = self.scan_duration.get()
        self.log(f"Scanning {freq}Hz for {duration}s...")
        
        # This would need actual Flipper CLI commands
        result = self.send_command(f"subghz rx_raw {freq}", int(duration))
        
        if result and "data" in result.lower():
            self.log("Signal detected!")
            self.save_signal(freq, result)
        else:
            self.log("No signal detected")
            
    def scan_garage_doors(self):
        """Scan common garage door frequencies"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        freqs = ["300000000", "315000000", "390000000", "433920000"]
        
        for freq in freqs:
            self.scan_frequency(freq)
            time.sleep(1)
            
    def transmit_signal(self):
        """Transmit selected signal"""
        selection = self.signal_listbox.curselection()
        if not selection:
            self.log("Select a signal first!")
            return
            
        # Would transmit the selected signal
        self.log("Transmitting signal...")
        
    # NFC methods
    def nfc_read(self):
        """Read NFC tag"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        self.log("Scanning for NFC tag...")
        result = self.send_command("nfc detect", 5)
        
        if result:
            self.nfc_result.delete('1.0', 'end')
            self.nfc_result.insert('end', result)
            
    def nfc_emulate(self):
        """Emulate NFC tag"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        uid = self.nfc_uid.get()
        self.log(f"Emulating UID: {uid}")
        # Would send emulate command
        
    # IR methods
    def ir_send(self, protocol, address, command):
        """Send IR signal"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        self.log(f"Sending IR: {protocol} {address} {command}")
        result = self.send_command(f"ir tx {protocol} {address} {command}")
        
        if result:
            self.log("IR signal sent!")
            
    # GPIO methods
    def gpio_set(self, pin, value):
        """Set GPIO pin"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        self.log(f"Setting GPIO {pin} to {value}")
        result = self.send_command(f"gpio write {pin} {value}")
        self.gpio_vars[pin].set("HIGH" if value else "LOW")
        
    def gpio_read(self, pin):
        """Read GPIO pin"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        result = self.send_command(f"gpio read {pin}")
        self.gpio_vars[pin].set(result.strip() if result else "ERROR")
        
    # BadUSB methods
    def badusb_run(self, script_path):
        """Run BadUSB script"""
        if not self.connected:
            self.log("Connect first!")
            return
            
        self.log(f"Running BadUSB: {script_path}")
        result = self.send_command(f"badusb run {script_path}", 3)
        
    # Database methods
    def load_signals(self):
        """Load signals from file"""
        if self.signals_file.exists():
            try:
                with open(self.signals_file) as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_signal(self, freq, data):
        """Save captured signal"""
        key = f"{freq}_{int(time.time())}"
        self.captured_signals[key] = {
            'frequency': freq,
            'data': data,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'name': f'Signal_{len(self.captured_signals)}'
        }
        self.save_signals()
        self.refresh_signal_list()
        
    def save_signals(self):
        """Save signals to file"""
        with open(self.signals_file, 'w') as f:
            json.dump(self.captured_signals, f, indent=2)
            
    def refresh_signal_list(self):
        """Refresh signal listbox"""
        self.signal_listbox.delete(0, 'end')
        self.db_listbox.delete(0, 'end')
        
        for key, signal in self.captured_signals.items():
            name = f"{signal['name']} ({signal['frequency']}Hz)"
            self.signal_listbox.insert('end', name)
            self.db_listbox.insert('end', name)
            
        self.db_stats.config(text=f"Stored Signals: {len(self.captured_signals)}")
        
    def export_signals(self):
        """Export signals to JSON"""
        self.save_signals()
        self.log(f"Exported {len(self.captured_signals)} signals")
        
    def import_signals(self):
        """Import signals from JSON"""
        self.captured_signals = self.load_signals()
        self.refresh_signal_list()
        self.log(f"Imported {len(self.captured_signals)} signals")
        
    def clear_signals(self):
        """Clear all signals"""
        self.captured_signals = {}
        self.save_signals()
        self.refresh_signal_list()
        self.log("Cleared all signals")

def main():
    """Run standalone Flipper GUI"""
    app = FlipperGUI()
    app.root.mainloop()

if __name__ == '__main__':
    main()
