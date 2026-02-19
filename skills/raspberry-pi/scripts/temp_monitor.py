#!/usr/bin/env python3
"""
Temperature Monitor - Continuous logging with alerts
Usage: python3 temp_monitor.py [--interval 60] [--log temps.csv] [--alert 80]
"""

import argparse
import csv
import time
import sys
from datetime import datetime
from pathlib import Path

def get_cpu_temp():
    """Read CPU temperature from thermal zone"""
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            return int(f.read().strip()) / 1000.0
    except Exception as e:
        print(f"Error reading temp: {e}", file=sys.stderr)
        return None

def get_gpu_temp():
    """Read GPU temperature using vcgencmd"""
    try:
        import subprocess
        result = subprocess.run(['vcgencmd', 'measure_temp'],
                              capture_output=True, text=True)
        return float(result.stdout.split('=')[1].split("'")[0])
    except:
        return None

def get_throttle_status():
    """Get thermal throttling status"""
    try:
        import subprocess
        result = subprocess.run(['vcgencmd', 'get_throttled'],
                              capture_output=True, text=True)
        hex_val = int(result.stdout.split('=')[1], 16)
        return hex_val != 0
    except:
        return None

def main():
    parser = argparse.ArgumentParser(description='Monitor Raspberry Pi temperature')
    parser.add_argument('--interval', type=int, default=60,
                       help='Sampling interval in seconds (default: 60)')
    parser.add_argument('--log', type=str, default='temps.csv',
                       help='Log file path (default: temps.csv)')
    parser.add_argument('--alert', type=float, default=80.0,
                       help='Temperature alert threshold in C (default: 80)')
    parser.add_argument('--duration', type=int, default=0,
                       help='Run duration in minutes, 0=infinite (default: 0)')
    args = parser.parse_args()

    log_path = Path(args.log)
    
    # Create log directory if needed
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if file exists to determine if we need headers
    file_exists = log_path.exists()
    
    print(f"🌡️  Temperature Monitor Started")
    print(f"   Log file: {log_path.absolute()}")
    print(f"   Interval: {args.interval}s")
    print(f"   Alert threshold: {args.alert}°C")
    print(f"   Press Ctrl+C to stop\n")
    
    start_time = time.time()
    max_samples = (args.duration * 60) // args.interval if args.duration > 0 else None
    sample_count = 0
    
    try:
        with open(log_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                writer.writerow(['timestamp', 'cpu_temp_c', 'gpu_temp_c', 'throttling'])
            
            while True:
                cpu_temp = get_cpu_temp()
                gpu_temp = get_gpu_temp()
                throttling = get_throttle_status()
                
                timestamp = datetime.now().isoformat()
                
                # Log to file
                writer.writerow([
                    timestamp,
                    cpu_temp if cpu_temp else '',
                    gpu_temp if gpu_temp else '',
                    'YES' if throttling else 'NO' if throttling is not None else ''
                ])
                f.flush()
                
                # Display status
                status = "🟢"
                if cpu_temp:
                    if cpu_temp >= args.alert:
                        status = "🔴 ALERT!"
                    elif cpu_temp >= 70:
                        status = "🟡 WARM"
                    print(f"{status} {timestamp} | CPU: {cpu_temp:.1f}°C", end='')
                    if gpu_temp:
                        print(f" | GPU: {gpu_temp:.1f}°C", end='')
                    if throttling:
                        print(f" | ⚠️  THROTTLING", end='')
                    print()
                
                sample_count += 1
                
                # Check if we've reached duration limit
                if max_samples and sample_count >= max_samples:
                    print(f"\n✅ Completed {args.duration} minutes of monitoring")
                    break
                
                time.sleep(args.interval)
                
    except KeyboardInterrupt:
        print(f"\n🛑 Monitoring stopped. Log saved to {log_path.absolute()}")
        
        # Print summary
        if log_path.exists():
            with open(log_path, 'r') as f:
                lines = len(list(f)) - 1  # Exclude header
            print(f"   Total samples: {lines}")

if __name__ == '__main__':
    main()
