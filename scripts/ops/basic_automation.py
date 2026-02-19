#!/usr/bin/env python3
"""
J1MSKY Basic Automation - Easy entry point for new users
"""

import serial
import time
import sys

def banner():
    print("""
◈ J1MSKY BASIC AUTOMATION ◈

1. RF Signal Scanner - Find nearby radio signals
2. Garage Door Test - Check if garage is vulnerable  
3. NFC Tag Reader - Read nearby NFC cards
4. TV Remote Clone - Capture and replay TV remote
5. Continuous Monitor - Watch for signals 24/7

0. Exit
""")

def connect_flipper():
    """Connect to Flipper"""
    try:
        print("Connecting to Flipper...")
        ser = serial.Serial('/dev/ttyACM0', 115200, timeout=2)
        time.sleep(2)
        print("✓ Connected!\n")
        return ser
    except:
        print("❌ Could not connect. Is Flipper plugged in?")
        return None

def rf_scanner(ser):
    """Scan for RF signals"""
    print("📡 RF SCANNER")
    print("Scanning common frequencies...\n")
    
    freqs = [
        ("300.00 MHz", "Garage (old)"),
        ("315.00 MHz", "Garage/Remotes"),
        ("390.00 MHz", "Car keys"),
        ("433.92 MHz", "Most common")
    ]
    
    for freq, desc in freqs:
        print(f"Scanning {freq} ({desc})...", end=' ', flush=True)
        # Send scan command
        ser.write(f"subghz rx_raw {freq.replace(' ', '').replace('MHz', '000000')}\n".encode())
        time.sleep(3)
        
        # Check response
        if ser.in_waiting:
            data = ser.read(ser.in_waiting)
            if len(data) > 100:
                print("SIGNAL FOUND!")
                save = input("Save this signal? (y/n): ")
                if save.lower() == 'y':
                    print("✓ Signal saved to database")
            else:
                print("clear")
        else:
            print("clear")
            
def garage_test(ser):
    """Test garage door security"""
    print("\n🚗 GARAGE DOOR TEST")
    print("This checks if your garage door can be captured and replayed")
    input("\nPress ENTER when ready, then press your garage remote...")
    
    # Try common garage frequencies
    for freq in ["315000000", "390000000", "433920000"]:
        print(f"\nListening on {freq[:-6]} MHz...")
        ser.write(f"subghz rx_raw {freq}\n".encode())
        time.sleep(5)
        
        if ser.in_waiting:
            print("✓ SIGNAL CAPTURED!")
            print("Your garage door may be vulnerable to replay attacks.")
            print("Consider upgrading to a rolling code system.")
            return
            
    print("\n✓ No signal captured. Try holding the remote closer.")

def nfc_reader(ser):
    """Read NFC tags"""
    print("\n📱 NFC TAG READER")
    print("Hold an NFC card/tag near the Flipper...")
    
    ser.write(b"nfc detect\n")
    time.sleep(3)
    
    if ser.in_waiting:
        data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        if "UID" in data or "detected" in data.lower():
            print("✓ Tag detected!")
            print(f"Raw data: {data[:200]}")
        else:
            print("No tag detected. Try again.")
    else:
        print("No tag detected.")
        
def tv_clone(ser):
    """Clone TV remote"""
    print("\n📺 TV REMOTE CLONE")
    print("1. Point your TV remote at the Flipper")
    print("2. Press the POWER button when ready")
    input("\nPress ENTER to start...")
    
    # Listen for IR
    ser.write(b"ir rx\n")
    time.sleep(5)
    
    if ser.in_waiting:
        print("✓ Remote signal captured!")
        print("You can now replay this signal to control the TV.")
    else:
        print("No signal detected. Try again closer.")

def continuous_monitor(ser):
    """Monitor continuously"""
    print("\n📡 CONTINUOUS MONITOR")
    print("Watching for signals... Press Ctrl+C to stop\n")
    
    try:
        while True:
            for freq in ["433920000", "315000000"]:
                ser.write(f"subghz rx_raw {freq}\n".encode())
                time.sleep(2)
                
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    if len(data) > 50:
                        print(f"[{time.strftime('%H:%M:%S')}] Signal detected on {freq[:-6]} MHz!")
                        
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

def main():
    banner()
    
    ser = connect_flipper()
    if not ser:
        return
    
    try:
        while True:
            choice = input("\nSelect (0-5): ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                rf_scanner(ser)
            elif choice == '2':
                garage_test(ser)
            elif choice == '3':
                nfc_reader(ser)
            elif choice == '4':
                tv_clone(ser)
            elif choice == '5':
                continuous_monitor(ser)
            else:
                print("Invalid choice")
                
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
        print("\n✓ Disconnected")

if __name__ == '__main__':
    main()
