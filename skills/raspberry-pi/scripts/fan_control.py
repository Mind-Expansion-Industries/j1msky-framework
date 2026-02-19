#!/usr/bin/env python3
"""
Fan Control - Automatic temperature-based fan control
Usage: python3 fan_control.py [--pin 18] [--on 70] [--off 60] [--pwm]
"""

import argparse
import sys
import time
from pathlib import Path

# Check if running on actual Pi
def is_raspberry_pi():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'BCM' in f.read() or 'Raspberry' in f.read()
    except:
        return False

def get_cpu_temp():
    """Read CPU temperature"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            return int(f.read().strip()) / 1000.0
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Automatic fan control')
    parser.add_argument('--pin', type=int, default=18,
                       help='GPIO pin for fan (default: 18)')
    parser.add_argument('--on', type=float, default=70.0,
                       help='Temperature to turn fan ON (default: 70°C)')
    parser.add_argument('--off', type=float, default=60.0,
                       help='Temperature to turn fan OFF (default: 60°C)')
    parser.add_argument('--pwm', action='store_true',
                       help='Use PWM for variable speed control')
    parser.add_argument('--interval', type=int, default=5,
                       help='Check interval in seconds (default: 5)')
    args = parser.parse_args()
    
    if args.off >= args.on:
        print("Error: --off temperature must be lower than --on temperature")
        sys.exit(1)
    
    IS_PI = is_raspberry_pi()
    
    if IS_PI:
        try:
            from gpiozero import OutputDevice, PWMOutputDevice
            
            if args.pwm:
                fan = PWMOutputDevice(args.pin)
                print(f"🌀 PWM Fan control on GPIO {args.pin}")
            else:
                fan = OutputDevice(args.pin)
                print(f"🔌 Binary fan control on GPIO {args.pin}")
                
        except ImportError:
            print("Error: gpiozero not installed. Run: pip3 install gpiozero")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing GPIO: {e}")
            sys.exit(1)
    else:
        print("⚠️  Not running on Raspberry Pi - SIMULATION MODE")
        fan = None
    
    print(f"   Turn ON at: {args.on}°C")
    print(f"   Turn OFF at: {args.off}°C")
    print(f"   Check interval: {args.interval}s")
    print(f"   Press Ctrl+C to stop\n")
    
    fan_on = False
    
    try:
        while True:
            temp = get_cpu_temp()
            
            if temp is None:
                print("Failed to read temperature")
                time.sleep(args.interval)
                continue
            
            # Determine fan state
            if not fan_on and temp >= args.on:
                fan_on = True
                if fan:
                    if args.pwm:
                        # Start at 50%, increase with temp
                        speed = min(1.0, 0.5 + (temp - args.on) / 20)
                        fan.value = speed
                        print(f"🌡️  {temp:.1f}°C | Fan ON at {speed*100:.0f}% speed")
                    else:
                        fan.on()
                        print(f"🌡️  {temp:.1f}°C | Fan ON")
                else:
                    print(f"🌡️  {temp:.1f}°C | [SIM] Fan ON")
                    
            elif fan_on and temp <= args.off:
                fan_on = False
                if fan:
                    if args.pwm:
                        fan.value = 0
                    else:
                        fan.off()
                print(f"🌡️  {temp:.1f}°C | Fan OFF")
            
            elif fan_on and args.pwm and fan:
                # Adjust PWM speed based on temperature
                speed = min(1.0, 0.4 + (temp - args.off) / 25)
                if abs(fan.value - speed) > 0.1:  # Only update if significant change
                    fan.value = speed
                    print(f"🌡️  {temp:.1f}°C | Fan speed: {speed*100:.0f}%")
            
            else:
                status = "🟢" if temp < 60 else "🟡" if temp < 75 else "🔴"
                print(f"{status} {temp:.1f}°C | Fan {'ON' if fan_on else 'OFF'}")
            
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping fan control")
        if fan:
            if args.pwm:
                fan.value = 0
            else:
                fan.off()
        print("   Fan turned off")

if __name__ == '__main__':
    main()
