#!/usr/bin/env python3
"""
Flipper Bridge Daemon - Runs continuously, auto-detects Flipper
"""

import sys
import os
sys.path.insert(0, '/home/m1ndb0t/Desktop/J1MSKY/j1msky-framework')

# Import directly
exec(open('/home/m1ndb0t/Desktop/J1MSKY/j1msky-framework/flipper/flipper_bridge.py').read())

import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [FLIPPER] %(message)s'
)

print("◈ J1MSKY Flipper Bridge Daemon ◈")
print("Waiting for Flipper Zero connection...")
print("(Plug in your Flipper via USB)")

agent = FlipperAgent()

# Try to connect
if agent.start():
    print("✓ Flipper connected!")
    print(f"Known signals: {agent.get_status()['known_signals']}")
else:
    print("⚠ Flipper not detected. Retrying every 5 seconds...")
    print("Press Ctrl+C to exit")
    
    try:
        while True:
            time.sleep(5)
            status = agent.get_status()
            if status['connected']:
                print("✓ Flipper connected!")
                break
    except KeyboardInterrupt:
        print("\nDaemon stopped")
