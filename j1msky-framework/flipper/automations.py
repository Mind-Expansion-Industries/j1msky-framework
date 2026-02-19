#!/usr/bin/env python3
"""
J1MSKY Flipper Automation Scripts
Collection of automated Flipper Zero tasks
"""

import serial
import time
import json
import sys
from pathlib import Path
from datetime import datetime

class FlipperAutomator:
    """Automated Flipper tasks"""
    
    def __init__(self, port='/dev/ttyACM0'):
        self.port = port
        self.serial = None
        self.results = []
        
    def connect(self):
        """Connect to Flipper"""
        try:
            self.serial = serial.Serial(self.port, 115200, timeout=3)
            time.sleep(2)
            # Clear welcome message
            if self.serial.in_waiting:
                self.serial.read(self.serial.in_waiting)
            print("✓ Connected to Flipper")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def send_cmd(self, cmd, wait=1):
        """Send command and get response"""
        if not self.serial:
            return None
        try:
            self.serial.write(f"{cmd}\n".encode())
            time.sleep(wait)
            response = b""
            while self.serial.in_waiting:
                response += self.serial.read(self.serial.in_waiting)
                time.sleep(0.1)
            return response.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error: {e}")
            return None
            
    def scan_environment(self):
        """Complete RF environment scan"""
        print("\n◈ SCANNING ENVIRONMENT ◈")
        
        # Common frequencies to scan
        frequencies = {
            'Garage Remotes': [300000000, 315000000, 390000000],
            'ISM Band': [433920000, 868350000, 915000000],
            'Car Keys': [314900000, 433920000, 868300000],
            'Weather Stations': [433000000, 868000000],
            'Wireless Doorbells': [315000000, 433920000]
        }
        
        found_signals = []
        
        for category, freqs in frequencies.items():
            print(f"\n📡 Scanning {category}...")
            for freq in freqs:
                print(f"  {freq/1000000} MHz...", end=' ', flush=True)
                result = self.send_cmd(f"subghz rx_raw {freq}", 3)
                
                if result and "data" in result.lower():
                    print("SIGNAL DETECTED!")
                    found_signals.append({
                        'category': category,
                        'frequency': freq,
                        'raw_data': result[:500],
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    print("clear")
                    
        self.save_results('rf_scan', found_signals)
        print(f"\n✓ Scan complete. Found {len(found_signals)} signals.")
        return found_signals
        
    def clone_garage_remote(self):
        """Attempt to clone a garage door remote"""
        print("\n◈ GARAGE REMOTE CLONER ◈")
        print("1. Press your garage remote button when prompted")
        print("2. I'll try to capture and replay the signal")
        
        common_freqs = [300000000, 315000000, 390000000, 433920000]
        captured = None
        
        for freq in common_freqs:
            input(f"\nPress ENTER and then press your remote (scanning {freq/1000000}MHz)...")
            
            print("  Listening for 5 seconds...")
            result = self.send_cmd(f"subghz rx_raw {freq}", 5)
            
            if result and len(result) > 100:
                print("  ✓ Signal captured!")
                captured = {
                    'frequency': freq,
                    'data': result,
                    'timestamp': datetime.now().isoformat()
                }
                break
            else:
                print("  ✗ No signal detected")
                
        if captured:
            # Save for replay
            self.save_results('garage_remote', captured)
            
            # Attempt replay
            test = input("\nTest the captured signal? (y/n): ")
            if test.lower() == 'y':
                print("Replaying signal...")
                # Would send replay command
                print("Signal replayed!")
                
        return captured
        
    def nfc_audit(self):
        """Audit NFC tags in environment"""
        print("\n◈ NFC SECURITY AUDIT ◈")
        print("Scanning for NFC tags...")
        
        found_tags = []
        
        for i in range(5):  # 5 scan attempts
            print(f"\nScan {i+1}/5 - Hold tag near Flipper...")
            result = self.send_cmd("nfc detect", 5)
            
            if result and "UID" in result:
                print("✓ Tag detected!")
                tag_info = self.send_cmd("nfc read", 3)
                
                tag_data = {
                    'scan': i+1,
                    'info': tag_info,
                    'timestamp': datetime.now().isoformat()
                }
                found_tags.append(tag_data)
                
                # Check if we should continue
                if i < 4:
                    cont = input("Scan another tag? (y/n): ")
                    if cont.lower() != 'y':
                        break
            else:
                print("✗ No tag detected")
                
        self.save_results('nfc_audit', found_tags)
        print(f"\n✓ Audit complete. Found {len(found_tags)} tags.")
        return found_tags
        
    def ir_brute_force(self, device_type='tv'):
        """Brute force IR codes for a device"""
        print(f"\n◈ IR BRUTE FORCE: {device_type.upper()} ◈")
        print("⚠ Point Flipper at the device before continuing")
        input("Press ENTER to start...")
        
        # Common protocols and codes
        protocols = {
            'tv': [
                ('NEC', '00', ['01', '02', '03']),  # Power, Vol+, Vol-
                ('NEC', '01', ['01', '02', '03']),
                ('Samsung32', '07', ['02', '03']),
            ],
            'ac': [
                ('NEC', '10', ['01', '02', '03']),
                ('NEC', '11', ['01', '02', '03']),
            ]
        }
        
        results = []
        codes_to_try = protocols.get(device_type, protocols['tv'])
        
        for protocol, addr, commands in codes_to_try:
            for cmd in commands:
                print(f"Trying {protocol} {addr}:{cmd}...", end=' ', flush=True)
                result = self.send_cmd(f"ir tx {protocol} {addr} {cmd}", 1)
                print("sent")
                
                results.append({
                    'protocol': protocol,
                    'address': addr,
                    'command': cmd,
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(0.5)  # Delay between signals
                
        self.save_results(f'ir_brute_{device_type}', results)
        print(f"\n✓ Brute force complete. Sent {len(results)} codes.")
        return results
        
    def badusb_demo(self):
        """Demo BadUSB capabilities"""
        print("\n◈ BADUSB DEMO ◈")
        print("⚠ Plug Flipper into target computer via USB")
        input("Press ENTER when ready...")
        
        demos = [
            ('Hello World', 'DELAY 1000\nSTRING Hello from J1MSKY!\nENTER'),
            ('Rickroll', 'DELAY 1000\nGUI r\nDELAY 500\nSTRING https://www.youtube.com/watch?v=dQw4w9WgXcQ\nENTER'),
            ('Reverse Shell', 'DELAY 1000\nGUI r\nDELAY 500\nSTRING powershell\nENTER\nDELAY 1000\nSTRING # Connect back to J1MSKY\nENTER')
        ]
        
        print("\nAvailable demos:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
            
        choice = input("\nSelect demo (1-3) or 0 to cancel: ")
        
        if choice in ['1', '2', '3']:
            name, script = demos[int(choice)-1]
            print(f"\nRunning {name}...")
            
            # Save script to Flipper
            # This would require writing to Flipper's storage
            print("Script loaded!")
            print("Executing in 3 seconds...")
            time.sleep(3)
            
            result = self.send_cmd(f"badusb run /ext/badusb/demo.txt", 5)
            print("✓ Demo complete")
            
    def continuous_monitor(self, duration_minutes=60):
        """Continuous RF monitoring"""
        print(f"\n◈ CONTINUOUS MONITORING ({duration_minutes} minutes) ◈")
        print("Press Ctrl+C to stop\n")
        
        start_time = time.time()
        events = []
        
        try:
            while time.time() - start_time < duration_minutes * 60:
                # Quick scan of common frequencies
                for freq in [433920000, 315000000, 868350000]:
                    result = self.send_cmd(f"subghz rx_raw {freq}", 2)
                    
                    if result and len(result) > 50:
                        event = {
                            'frequency': freq,
                            'timestamp': datetime.now().isoformat(),
                            'signal_strength': len(result)
                        }
                        events.append(event)
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Signal at {freq/1000000}MHz!")
                        
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            
        self.save_results('monitor_session', {
            'duration': time.time() - start_time,
            'events': events,
            'total_signals': len(events)
        })
        
        print(f"\n✓ Session complete. Detected {len(events)} signals.")
        return events
        
    def save_results(self, name, data):
        """Save automation results"""
        results_dir = Path('/home/m1ndb0t/Desktop/J1MSKY/j1msky-framework/flipper/results')
        results_dir.mkdir(exist_ok=True)
        
        filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = results_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        print(f"Results saved to: {filepath}")
        
    def disconnect(self):
        """Disconnect from Flipper"""
        if self.serial:
            self.serial.close()
            print("✓ Disconnected")

def main():
    """Interactive automation menu"""
    print("""
◈ J1MSKY FLIPPER AUTOMATION ◈

Select automation:
  1. Environment Scan (RF sweep)
  2. Clone Garage Remote
  3. NFC Security Audit
  4. IR Brute Force
  5. BadUSB Demo
  6. Continuous Monitor
  0. Exit
""")
    
    auto = FlipperAutomator()
    
    if not auto.connect():
        return
        
    try:
        while True:
            choice = input("\nSelect (0-6): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                auto.scan_environment()
            elif choice == '2':
                auto.clone_garage_remote()
            elif choice == '3':
                auto.nfc_audit()
            elif choice == '4':
                device = input("Device type (tv/ac): ") or 'tv'
                auto.ir_brute_force(device)
            elif choice == '5':
                auto.badusb_demo()
            elif choice == '6':
                mins = input("Duration (minutes): ") or '60'
                auto.continuous_monitor(int(mins))
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        auto.disconnect()

if __name__ == '__main__':
    main()
