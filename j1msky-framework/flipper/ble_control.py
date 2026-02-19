#!/usr/bin/env python3
"""
Flipper Bluetooth/BLE Control Script
Kitchen Sink mode - Aggressive BLE scanning
"""

import serial
import time
import sys

class FlipperBluetooth:
    def __init__(self, port='/dev/ttyACM0'):
        self.port = port
        self.serial = None
        
    def connect(self):
        try:
            print("Connecting to Flipper...")
            self.serial = serial.Serial(self.port, 115200, timeout=2)
            time.sleep(2)
            print("✓ Connected!")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
            
    def send_cmd(self, cmd, wait=1):
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
            
    def ble_scan(self, duration=10):
        """Scan for BLE devices"""
        print(f"\n📡 BLE SCAN - {duration} seconds")
        print("Scanning for Bluetooth Low Energy devices...")
        
        # Start BLE scan
        result = self.send_cmd("ble scan", duration)
        
        if result:
            print("\nFound devices:")
            print(result[:1000])  # Limit output
        else:
            print("No devices found or scan failed")
            
    def ble_spam(self, count=50):
        """BLE advertisement spam (Kitchen Sink mode)"""
        print(f"\n🔥 BLE SPAM MODE - {count} packets")
        print("Sending BLE advertisements...")
        
        for i in range(count):
            # Send BLE advertisement with random data
            self.send_cmd("ble spam", 0.1)
            if i % 10 == 0:
                print(f"Sent {i}/{count} packets...")
                
        print(f"✓ Sent {count} BLE spam packets")
        
    def ble_kitchen_sink(self, duration=30):
        """Kitchen Sink mode - Everything at once"""
        print("\n" + "="*50)
        print("◈ KITCHEN SINK MODE ACTIVATED ◈")
        print("="*50)
        print("\nThis mode will:")
        print("  • Aggressive BLE scanning")
        print("  • BLE advertisement spam")
        print("  • Bluetooth discovery flood")
        print(f"  • Run for {duration} seconds")
        print("\n⚠️  May interfere with nearby Bluetooth devices")
        print("="*50 + "\n")
        
        start = time.time()
        packet_count = 0
        
        try:
            while time.time() - start < duration:
                # Rapid BLE scan
                self.send_cmd("ble scan", 0.5)
                packet_count += 1
                
                # BLE spam
                self.send_cmd("ble spam", 0.1)
                packet_count += 1
                
                # BT inquiry
                self.send_cmd("bt inquiry", 0.5)
                packet_count += 1
                
                elapsed = time.time() - start
                print(f"[{elapsed:.1f}s] Packets: {packet_count}", end='\r')
                
        except KeyboardInterrupt:
            print("\n\nStopped by user")
            
        print(f"\n\n✓ Kitchen Sink complete!")
        print(f"  Duration: {time.time() - start:.1f}s")
        print(f"  Total packets: {packet_count}")
        
    def disconnect(self):
        if self.serial:
            self.serial.close()
            print("✓ Disconnected")

def main():
    print("◈ J1MSKY Flipper Bluetooth Control ◈\n")
    
    bt = FlipperBluetooth()
    if not bt.connect():
        return
        
    print("\nOptions:")
    print("1. BLE Scan (10 seconds)")
    print("2. BLE Spam (50 packets)")
    print("3. KITCHEN SINK (30 seconds - aggressive)")
    print("0. Exit")
    
    choice = input("\nSelect: ").strip()
    
    if choice == '1':
        bt.ble_scan(10)
    elif choice == '2':
        bt.ble_spam(50)
    elif choice == '3':
        bt.ble_kitchen_sink(30)
    else:
        print("Exiting...")
        
    bt.disconnect()

if __name__ == '__main__':
    main()
