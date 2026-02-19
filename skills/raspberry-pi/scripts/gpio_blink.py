#!/usr/bin/env python3
"""
GPIO Blink - Basic LED test
Usage: python3 gpio_blink.py [--pin 17] [--on 1] [--off 1] [--count 0]
"""

import argparse
import sys
import time

def main():
    parser = argparse.ArgumentParser(description='Blink LED on GPIO pin')
    parser.add_argument('--pin', type=int, default=17,
                       help='GPIO pin number (default: 17)')
    parser.add_argument('--on', type=float, default=1.0,
                       help='Seconds to keep LED on (default: 1)')
    parser.add_argument('--off', type=float, default=1.0,
                       help='Seconds to keep LED off (default: 1)')
    parser.add_argument('--count', type=int, default=0,
                       help='Number of blinks, 0=infinite (default: 0)')
    args = parser.parse_args()
    
    try:
        from gpiozero import LED
    except ImportError:
        print("❌ gpiozero not installed. Install with: pip3 install gpiozero")
        sys.exit(1)
    
    print(f"💡 Blinking LED on GPIO {args.pin}")
    print(f"   ON: {args.on}s, OFF: {args.off}s")
    if args.count > 0:
        print(f"   Count: {args.count}")
    else:
        print(f"   Count: infinite (Ctrl+C to stop)")
    print()
    
    try:
        led = LED(args.pin)
        count = 0
        
        while args.count == 0 or count < args.count:
            count += 1
            led.on()
            print(f"   🔆 ON  (blink {count})")
            time.sleep(args.on)
            
            led.off()
            print(f"   ⚫ OFF (blink {count})")
            time.sleep(args.off)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        try:
            led.off()
            led.close()
        except:
            pass
        print("   LED turned off and GPIO cleaned up")

if __name__ == '__main__':
    main()
