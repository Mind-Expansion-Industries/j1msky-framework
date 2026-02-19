#!/usr/bin/env python3
"""
I2C Scanner - Detect and identify I2C devices
Usage: python3 i2c_scan.py [--bus 1]
"""

import argparse
import subprocess
import sys

def main():
    parser = argparse.ArgumentParser(description='Scan I2C bus for devices')
    parser.add_argument('--bus', type=int, default=1,
                       help='I2C bus number (default: 1)')
    args = parser.parse_args()
    
    print(f"🔍 Scanning I2C bus {args.bus}...")
    print()
    
    # Check if i2cdetect is available
    try:
        result = subprocess.run(['which', 'i2cdetect'], capture_output=True)
        if result.returncode != 0:
            print("❌ i2cdetect not found. Install with:")
            print("   sudo apt-get install i2c-tools")
            sys.exit(1)
    except:
        pass
    
    # Run i2cdetect
    try:
        result = subprocess.run(
            ['i2cdetect', '-y', str(args.bus)],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            print("\nMake sure I2C is enabled:")
            print("   sudo raspi-config → Interfacing Options → I2C → Enable")
            sys.exit(1)
        
        print(result.stdout)
        
        # Parse output for device summary
        addresses = []
        for line in result.stdout.split('\n'):
            if line.startswith('70:'):
                continue  # Skip header/footer lines
            parts = line.split()
            if len(parts) > 1 and parts[0].endswith(':'):
                for addr in parts[1:]:
                    if addr not in ['--', 'UU'] and len(addr) == 2:
                        addresses.append(f"0x{addr}")
        
        if addresses:
            print(f"✅ Found {len(addresses)} device(s): {', '.join(addresses)}")
            print("\n📋 Common I2C addresses:")
            common = {
                '0x27': 'LCD 1602/2004 (PCF8574)',
                '0x3f': 'LCD 1602/2004 (alt address)',
                '0x48': 'ADS1115 ADC',
                '0x50': 'AT24 EEPROM',
                '0x68': 'DS1307/DS3231 RTC, MPU6050 IMU',
                '0x76': 'BMP280/BME280 (alt)',
                '0x77': 'BMP280/BME280, BME680',
            }
            for addr in addresses:
                if addr in common:
                    print(f"   {addr}: {common[addr]}")
        else:
            print("⚠️  No I2C devices detected")
            print("\nTroubleshooting:")
            print("   • Check wiring (SDA→GPIO2, SCL→GPIO3)")
            print("   • Verify pull-up resistors (4.7kΩ)")
            print("   • Ensure device is powered")
            print("   • Check if I2C is enabled: sudo raspi-config")
            
    except FileNotFoundError:
        print("❌ i2cdetect not found. Install i2c-tools:")
        print("   sudo apt-get update")
        print("   sudo apt-get install i2c-tools")
        sys.exit(1)

if __name__ == '__main__':
    main()
