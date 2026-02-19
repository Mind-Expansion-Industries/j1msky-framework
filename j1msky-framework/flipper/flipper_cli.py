#!/usr/bin/env python3
"""
J1MSKY Flipper Bridge - Working Version
Communicates with Flipper Zero CLI
"""

import serial
import time
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger('flipper')

class FlipperBridge:
    def __init__(self, port='/dev/ttyACM0', baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.connected = False
        
    def connect(self):
        """Connect to Flipper"""
        try:
            logger.info(f"Connecting to Flipper on {self.port}...")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=2)
            time.sleep(2)  # Wait for Flipper boot
            
            # Clear welcome message
            self._clear_buffer()
            
            # Test connection
            self.serial.write(b'\n')
            time.sleep(0.5)
            response = self._read_response()
            
            if '>:' in response or 'flipper' in response.lower():
                self.connected = True
                logger.info("✓ Flipper connected!")
                logger.info("Available commands: help, clear, date, log, gpio, subghz, nfc, ir, badusb")
                return True
            else:
                logger.warning("Connected but unexpected response")
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
            
    def _clear_buffer(self):
        """Clear serial buffer"""
        if self.serial:
            self.serial.reset_input_buffer()
            
    def _read_response(self, timeout=2):
        """Read response from Flipper"""
        response = ""
        start = time.time()
        while time.time() - start < timeout:
            if self.serial.in_waiting:
                data = self.serial.read(self.serial.in_waiting).decode('utf-8', errors='ignore')
                response += data
                if '>:' in data:  # Prompt detected
                    break
            time.sleep(0.1)
        return response
        
    def send_command(self, cmd):
        """Send command to Flipper"""
        if not self.connected:
            logger.error("Not connected")
            return None
            
        try:
            self.serial.write(f"{cmd}\n".encode())
            time.sleep(0.5)
            response = self._read_response()
            
            # Clean up response (remove prompt and escape codes)
            lines = response.split('\n')
            cleaned = []
            for line in lines:
                line = line.strip()
                if line and '>:' not in line and not line.startswith('\x1b['):
                    cleaned.append(line)
                    
            return '\n'.join(cleaned)
            
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return None
            
    def get_info(self):
        """Get Flipper info"""
        return self.send_command("info")
        
    def get_date(self):
        """Get Flipper date/time"""
        return self.send_command("date")
        
    def list_apps(self):
        """List installed apps"""
        return self.send_command("loader list")
        
    def subghz_scan(self, frequency=433920000):
        """Scan SubGHz frequency"""
        logger.info(f"Scanning {frequency/1000000}MHz...")
        return self.send_command(f"subghz rx {frequency}")
        
    def nfc_scan(self):
        """Scan for NFC tags"""
        logger.info("Scanning for NFC tags...")
        return self.send_command("nfc scan")
        
    def ir_tx(self, protocol, address, command):
        """Send IR signal"""
        return self.send_command(f"ir tx {protocol} {address} {command}")
        
    def gpio_set(self, pin, state):
        """Set GPIO pin"""
        return self.send_command(f"gpio write {pin} {state}")
        
    def gpio_read(self, pin):
        """Read GPIO pin"""
        return self.send_command(f"gpio read {pin}")
        
    def badusb_run(self, script_path):
        """Run BadUSB script"""
        return self.send_command(f"badusb run {script_path}")
        
    def screenshot(self, path="/tmp/flipper_screenshot.png"):
        """Take screenshot"""
        result = self.send_command("screen_stream frame")
        # Would need to decode binary data here
        return result
        
    def disconnect(self):
        """Disconnect from Flipper"""
        if self.serial:
            self.serial.close()
            self.connected = False
            logger.info("Disconnected")

def main():
    """Interactive Flipper control"""
    bridge = FlipperBridge()
    
    if not bridge.connect():
        print("Failed to connect. Is Flipper plugged in?")
        return
        
    print("\n◈ J1MSKY Flipper Bridge Active ◈")
    print("Type 'help' for commands, 'quit' to exit\n")
    
    # Show initial info
    print("Flipper Info:")
    print(bridge.get_info())
    print()
    
    try:
        while True:
            cmd = input("flipper> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
            elif cmd.lower() == 'help':
                print("""
Available commands:
  info          - Show Flipper info
  date          - Show date/time
  apps          - List installed apps
  scan rf       - Scan SubGHz (433.92MHz default)
  scan nfc      - Scan for NFC tags
  ir <proto> <addr> <cmd> - Send IR signal
  gpio read <pin>   - Read GPIO pin
  gpio write <pin> <0|1> - Set GPIO pin
  <any Flipper CLI command>
  quit          - Exit
                """)
            elif cmd == 'scan rf':
                print(bridge.subghz_scan())
            elif cmd == 'scan nfc':
                print(bridge.nfc_scan())
            elif cmd.startswith('ir '):
                parts = cmd.split()
                if len(parts) == 4:
                    print(bridge.ir_tx(parts[1], parts[2], parts[3]))
                else:
                    print("Usage: ir <protocol> <address> <command>")
            elif cmd.startswith('gpio '):
                print(bridge.send_command(cmd))
            else:
                response = bridge.send_command(cmd)
                if response:
                    print(response)
                    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        bridge.disconnect()

if __name__ == '__main__':
    main()
