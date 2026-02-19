#!/usr/bin/env python3
"""
flipper-bridge - J1MSKY Flipper Zero Integration
USB/Bluetooth communication with Flipper for RF, BadUSB, SubGHz, etc.
"""

import os
import sys
import json
import time
import serial
import serial.tools.list_ports
import threading
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
import logging

logger = logging.getLogger('flipper-bridge')

@dataclass
class FlipperCommand:
    """Command to send to Flipper"""
    module: str  # 'subghz', 'badusb', 'nfc', 'ir', 'gpio'
    action: str  # 'send', 'read', 'emulate', etc.
    data: Dict
    callback: Optional[Callable] = None

class FlipperBridge:
    """Bridge between J1MSKY and Flipper Zero"""
    
    # Flipper USB VID/PID
    FLIPPER_VID = 0x0483
    FLIPPER_PID = 0x5740
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self.connected = False
        self.running = False
        self.command_queue: List[FlipperCommand] = []
        self.callbacks: Dict[str, Callable] = {}
        
        # Status tracking
        self.last_ping = 0
        self.flipper_info = {}
        
    def find_flipper(self) -> Optional[str]:
        """Auto-detect Flipper Zero USB port"""
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            # Check for Flipper VID/PID
            if port.vid == self.FLIPPER_VID and port.pid == self.FLIPPER_PID:
                logger.info(f"Found Flipper at {port.device}")
                return port.device
                
            # Check description
            if 'flipper' in port.description.lower():
                logger.info(f"Found Flipper at {port.device} (by description)")
                return port.device
                
        # Common Flipper port names
        common_ports = ['/dev/ttyACM0', '/dev/ttyUSB0', '/dev/tty.usbmodem*']
        for pattern in common_ports:
            import glob
            matches = glob.glob(pattern)
            if matches:
                return matches[0]
                
        return None
        
    def connect(self) -> bool:
        """Connect to Flipper Zero"""
        try:
            if self.port is None:
                self.port = self.find_flipper()
                
            if self.port is None:
                logger.error("Flipper Zero not found. Is it plugged in?")
                return False
                
            logger.info(f"Connecting to Flipper at {self.port}...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                write_timeout=1
            )
            
            # Wait for connection
            time.sleep(2)
            
            # Send ping to verify
            if self._send_ping():
                self.connected = True
                self.running = True
                logger.info("✓ Flipper connected!")
                
                # Start listener thread
                self.listener_thread = threading.Thread(target=self._listener_loop, daemon=True)
                self.listener_thread.start()
                
                return True
            else:
                logger.error("Flipper didn't respond to ping")
                self.serial.close()
                return False
                
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from Flipper"""
        self.running = False
        self.connected = False
        
        if self.serial:
            self.serial.close()
            self.serial = None
            
        logger.info("Flipper disconnected")
        
    def _send_ping(self) -> bool:
        """Send ping to verify connection"""
        try:
            # Simple ping command
            ping_cmd = {"type": "ping", "timestamp": time.time()}
            self._send_raw(json.dumps(ping_cmd) + "\n")
            
            # Wait for response
            time.sleep(0.5)
            if self.serial.in_waiting:
                response = self.serial.readline().decode().strip()
                data = json.loads(response)
                return data.get('type') == 'pong'
                
        except:
            pass
        return False
        
    def _send_raw(self, data: str):
        """Send raw data to Flipper"""
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode())
            self.serial.flush()
            
    def _listener_loop(self):
        """Background thread to listen for Flipper messages"""
        while self.running:
            try:
                if self.serial and self.serial.in_waiting:
                    line = self.serial.readline().decode().strip()
                    if line:
                        self._handle_message(line)
                        
                # Process command queue
                if self.command_queue:
                    cmd = self.command_queue.pop(0)
                    self._execute_command(cmd)
                    
                time.sleep(0.01)
                
            except Exception as e:
                logger.error(f"Listener error: {e}")
                time.sleep(1)
                
    def _handle_message(self, message: str):
        """Handle incoming message from Flipper"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            if msg_type == 'pong':
                self.last_ping = time.time()
                
            elif msg_type == 'subghz_capture':
                # Received RF signal
                logger.info(f"RF Signal captured: {data}")
                self._trigger_callback('subghz_capture', data)
                
            elif msg_type == 'nfc_read':
                # NFC tag read
                logger.info(f"NFC Tag read: {data}")
                self._trigger_callback('nfc_read', data)
                
            elif msg_type == 'ir_receive':
                # IR signal received
                logger.info(f"IR Signal received: {data}")
                self._trigger_callback('ir_receive', data)
                
            elif msg_type == 'gpio_event':
                # GPIO pin change
                self._trigger_callback('gpio', data)
                
            else:
                logger.debug(f"Unknown message: {data}")
                
        except json.JSONDecodeError:
            logger.warning(f"Non-JSON message: {message}")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            
    def _execute_command(self, cmd: FlipperCommand):
        """Execute a command on Flipper"""
        try:
            payload = {
                'type': cmd.module,
                'action': cmd.action,
                'data': cmd.data,
                'timestamp': time.time()
            }
            
            self._send_raw(json.dumps(payload) + "\n")
            logger.info(f"Sent {cmd.module}/{cmd.action} to Flipper")
            
        except Exception as e:
            logger.error(f"Command failed: {e}")
            
    def _trigger_callback(self, event: str, data: Dict):
        """Trigger registered callback"""
        if event in self.callbacks:
            try:
                self.callbacks[event](data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
                
    # Public API methods
    
    def on(self, event: str, callback: Callable):
        """Register event callback"""
        self.callbacks[event] = callback
        
    def subghz_send(self, frequency: float, data: str):
        """Send SubGHz signal"""
        cmd = FlipperCommand(
            module='subghz',
            action='send',
            data={'frequency': frequency, 'data': data}
        )
        self.command_queue.append(cmd)
        
    def subghz_capture(self, frequency: float, duration: int = 10):
        """Capture SubGHz signals"""
        cmd = FlipperCommand(
            module='subghz',
            action='capture',
            data={'frequency': frequency, 'duration': duration}
        )
        self.command_queue.append(cmd)
        
    def nfc_read(self):
        """Read NFC tag"""
        cmd = FlipperCommand(
            module='nfc',
            action='read',
            data={}
        )
        self.command_queue.append(cmd)
        
    def nfc_emulate(self, uid: str):
        """Emulate NFC tag"""
        cmd = FlipperCommand(
            module='nfc',
            action='emulate',
            data={'uid': uid}
        )
        self.command_queue.append(cmd)
        
    def ir_send(self, protocol: str, address: str, command: str):
        """Send IR signal"""
        cmd = FlipperCommand(
            module='ir',
            action='send',
            data={'protocol': protocol, 'address': address, 'command': command}
        )
        self.command_queue.append(cmd)
        
    def badusb_run(self, script: str):
        """Run BadUSB script"""
        cmd = FlipperCommand(
            module='badusb',
            action='run',
            data={'script': script}
        )
        self.command_queue.append(cmd)
        
    def gpio_read(self, pin: int):
        """Read GPIO pin"""
        cmd = FlipperCommand(
            module='gpio',
            action='read',
            data={'pin': pin}
        )
        self.command_queue.append(cmd)
        
    def gpio_write(self, pin: int, value: bool):
        """Write to GPIO pin"""
        cmd = FlipperCommand(
            module='gpio',
            action='write',
            data={'pin': pin, 'value': value}
        )
        self.command_queue.append(cmd)

# High-level J1MSKY integration
class FlipperAgent:
    """Flipper as a J1MSKY Agent"""
    
    def __init__(self):
        self.bridge = FlipperBridge()
        self.known_signals = {}
        self.capture_log = []
        
    def start(self):
        """Start Flipper agent"""
        logger.info("Starting Flipper Agent...")
        
        # Setup callbacks
        self.bridge.on('subghz_capture', self._on_subghz)
        self.bridge.on('nfc_read', self._on_nfc)
        self.bridge.on('ir_receive', self._on_ir)
        
        # Try to connect
        if self.bridge.connect():
            logger.info("Flipper Agent active")
            return True
        else:
            logger.warning("Flipper not connected, retrying in background...")
            # Start retry loop
            threading.Thread(target=self._retry_connect, daemon=True).start()
            return False
            
    def _retry_connect(self):
        """Background retry connection"""
        while not self.bridge.connected:
            time.sleep(5)
            if self.bridge.connect():
                break
                
    def _on_subghz(self, data):
        """Handle SubGHz capture"""
        freq = data.get('frequency')
        signal_data = data.get('data')
        
        # Store in known signals
        key = f"{freq}_{hash(signal_data) % 10000}"
        self.known_signals[key] = {
            'frequency': freq,
            'data': signal_data,
            'timestamp': time.time(),
            'decoded': None
        }
        
        # Try to identify
        self._identify_signal(key)
        
        # Log
        self.capture_log.append({
            'type': 'subghz',
            'frequency': freq,
            'timestamp': time.time()
        })
        
        logger.info(f"Captured SubGHz signal at {freq}MHz")
        
    def _on_nfc(self, data):
        """Handle NFC read"""
        uid = data.get('uid')
        tag_type = data.get('type')
        
        logger.info(f"NFC Tag: {uid} ({tag_type})")
        
        # Could trigger actions based on tag
        if uid in self._get_known_tags():
            self._execute_tag_action(uid)
            
    def _on_ir(self, data):
        """Handle IR receive"""
        protocol = data.get('protocol')
        address = data.get('address')
        command = data.get('command')
        
        logger.info(f"IR: {protocol} - {address}:{command}")
        
    def _identify_signal(self, key: str):
        """Try to identify unknown RF signal"""
        # Query online database (if available)
        # For now, just mark as unknown
        signal = self.known_signals[key]
        
        # Common frequency ranges
        freq = signal['frequency']
        if 300 <= freq <= 450:
            signal['likely'] = 'Garage/Car Key'
        elif 800 <= freq <= 950:
            signal['likely'] = 'ISM Band/Remote'
        elif 2400 <= freq <= 2500:
            signal['likely'] = 'Bluetooth/WiFi'
            
    def _get_known_tags(self) -> List[str]:
        """Get list of known NFC tag UIDs"""
        # Load from config
        return []
        
    def _execute_tag_action(self, uid: str):
        """Execute action for known tag"""
        logger.info(f"Executing action for tag {uid}")
        # Trigger J1MSKY actions
        
    def scan_garage_doors(self):
        """Scan for garage door remotes (common frequencies)"""
        frequencies = [300.0, 315.0, 390.0, 433.92]
        
        for freq in frequencies:
            logger.info(f"Scanning {freq}MHz for garage remotes...")
            self.bridge.subghz_capture(freq, duration=30)
            time.sleep(35)  # Wait for capture
            
    def replay_last_signal(self):
        """Replay last captured signal"""
        if self.capture_log:
            last = self.capture_log[-1]
            if last['type'] == 'subghz':
                key = f"{last['frequency']}_{hash(last.get('data', '')) % 10000}"
                if key in self.known_signals:
                    signal = self.known_signals[key]
                    self.bridge.subghz_send(
                        signal['frequency'],
                        signal['data']
                    )
                    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'connected': self.bridge.connected,
            'known_signals': len(self.known_signals),
            'captures': len(self.capture_log),
            'last_ping': self.bridge.last_ping
        }

def main():
    """Test Flipper bridge"""
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', help='Serial port')
    parser.add_argument('--scan', action='store_true', help='Scan garage frequencies')
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    agent = FlipperAgent()
    
    if args.scan:
        agent.start()
        time.sleep(2)
        agent.scan_garage_doors()
    else:
        bridge = FlipperBridge(port=args.port)
        if bridge.connect():
            print("Flipper connected! Press Ctrl+C to exit")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                bridge.disconnect()
        else:
            print("Failed to connect. Make sure Flipper is plugged in.")

if __name__ == '__main__':
    main()
