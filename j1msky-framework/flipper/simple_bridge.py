#!/usr/bin/env python3
"""
J1MSKY Flipper Bridge - Simple Working Version
"""

import serial
import time
import sys

print("◈ J1MSKY Flipper Bridge ◈")
print("Connecting to Flipper Zero...")

try:
    # Open serial connection
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=3)
    print("✓ Serial port opened")
    
    # Wait for Flipper to boot/be ready
    time.sleep(2)
    
    # Clear any initial output
    if ser.in_waiting:
        ser.read(ser.in_waiting)
    
    print("✓ Flipper connected!")
    print("\nAvailable commands:")
    print("  info        - Show Flipper info")
    print("  date        - Show date/time")  
    print("  log         - View logs")
    print("  gpio        - GPIO control")
    print("  subghz      - SubGHz commands")
    print("  nfc         - NFC commands")
    print("  ir          - IR commands")
    print("  help        - Show all commands")
    print("  quit        - Exit")
    print("\nType command and press Enter:")
    
    while True:
        try:
            # Get user input
            cmd = input("\nflipper> ").strip()
            
            if cmd.lower() in ['quit', 'exit', 'q']:
                break
                
            if not cmd:
                continue
                
            # Send command
            ser.write(f"{cmd}\r\n".encode())
            time.sleep(0.5)
            
            # Read response
            response = b""
            start_time = time.time()
            while time.time() - start_time < 3:
                if ser.in_waiting:
                    data = ser.read(ser.in_waiting)
                    response += data
                    time.sleep(0.1)
                    if b'>:' in data or not ser.in_waiting:
                        break
                else:
                    time.sleep(0.05)
            
            # Clean and print response
            if response:
                # Remove ANSI escape codes
                import re
                cleaned = re.sub(rb'\x1b\[[0-9;]*[mK]', b'', response)
                text = cleaned.decode('utf-8', errors='ignore')
                # Remove echo of command
                lines = text.split('\n')
                output = '\n'.join([l for l in lines if cmd not in l and '>:' not in l and l.strip()])
                if output.strip():
                    print(output)
                else:
                    print("(no output)")
            else:
                print("(no response)")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
    
    ser.close()
    print("✓ Disconnected")
    
except serial.SerialException as e:
    print(f"❌ Failed to connect: {e}")
    print("Make sure Flipper is plugged in via USB")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
