#!/usr/bin/env python3
"""
VITALS Agent - System Health Monitor
Part of J1MSKY Agent Team
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path

class VitalsAgent:
    def __init__(self):
        self.name = "VITALS"
        self.status_file = Path('/tmp/agents/vitals_status.json')
        self.log_file = Path('/tmp/agents/vitals.log')
        self.history_file = Path('/tmp/agents/vitals_history.json')
        
        self.running = True
        self.history = []
        self.alert_thresholds = {
            'temp': 75,      # °C
            'load': 80,      # %
            'memory': 90     # %
        }
        
        self.log("VITALS agent initialized")
        
    def log(self, message):
        """Write to agent log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        with open(self.log_file, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
            
    def update_status(self, status, data=None):
        """Update status file"""
        payload = {
            "agent": self.name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "data": data or {}
        }
        with open(self.status_file, 'w') as f:
            json.dump(payload, f, indent=2)
            
    def get_system_stats(self):
        """Get current system statistics"""
        stats = {}
        
        # CPU Temperature
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                stats['temp'] = int(f.read().strip()) / 1000.0
        except:
            stats['temp'] = 0.0
            
        # CPU Load
        try:
            with open('/proc/loadavg', 'r') as f:
                load = float(f.read().split()[0])
                stats['load'] = min(100, (load / 4) * 100)  # Assuming 4 cores
        except:
            stats['load'] = 0.0
            
        # Memory
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
                total = int(lines[0].split()[1])
                available = int(lines[2].split()[1])
                stats['memory'] = ((total - available) / total) * 100
        except:
            stats['memory'] = 0.0
            
        # Uptime
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_secs = float(f.read().split()[0])
                hours = int(uptime_secs // 3600)
                mins = int((uptime_secs % 3600) // 60)
                stats['uptime'] = f"{hours}h {mins}m"
        except:
            stats['uptime'] = "--"
            
        # Disk usage
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                stats['disk_used'] = parts[2]
                stats['disk_total'] = parts[1]
                stats['disk_pct'] = parts[4]
        except:
            stats['disk_used'] = "--"
            stats['disk_total'] = "--"
            stats['disk_pct'] = "--"
            
        return stats
        
    def check_alerts(self, stats):
        """Check if any values exceed thresholds"""
        alerts = []
        
        if stats['temp'] > self.alert_thresholds['temp']:
            alerts.append(f"HIGH TEMP: {stats['temp']:.1f}°C")
            
        if stats['load'] > self.alert_thresholds['load']:
            alerts.append(f"HIGH LOAD: {stats['load']:.0f}%")
            
        if stats['memory'] > self.alert_thresholds['memory']:
            alerts.append(f"HIGH MEMORY: {stats['memory']:.0f}%")
            
        return alerts
        
    def update_history(self, stats):
        """Maintain rolling history"""
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "temp": stats['temp'],
            "load": stats['load'],
            "memory": stats['memory']
        })
        
        # Keep last 100 entries (~16 minutes at 10s intervals)
        self.history = self.history[-100:]
        
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
            
    def run(self):
        """Main agent loop"""
        self.log("VITALS entering main loop")
        self.update_status("RUNNING", {"message": "Monitoring system health"})
        
        while self.running:
            try:
                # Get stats
                stats = self.get_system_stats()
                
                # Check for alerts
                alerts = self.check_alerts(stats)
                if alerts:
                    for alert in alerts:
                        self.log(f"ALERT: {alert}")
                        self.update_status("ALERT", {"alert": alert, "stats": stats})
                else:
                    # Update normal status
                    self.update_status("HEALTHY", stats)
                    
                # Update history
                self.update_history(stats)
                
                # Log periodically (every minute)
                if int(time.time()) % 60 == 0:
                    self.log(f"Temp: {stats['temp']:.1f}°C | Load: {stats['load']:.0f}% | Mem: {stats['memory']:.0f}%")
                
                time.sleep(10)  # Check every 10 seconds
                
            except KeyboardInterrupt:
                self.log("Shutting down...")
                self.update_status("STOPPED", {"message": "Keyboard interrupt"})
                break
            except Exception as e:
                self.log(f"Error in main loop: {e}")
                time.sleep(30)
                
        self.log("VITALS agent stopped")

if __name__ == '__main__':
    agent = VitalsAgent()
    agent.run()
