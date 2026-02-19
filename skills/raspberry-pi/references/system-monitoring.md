# System Monitoring Reference

Continuous monitoring, logging, and alerting for Raspberry Pi health metrics.

## Temperature Monitoring

### Critical Thresholds (Pi 4)
| Temp | Behavior |
|------|----------|
| < 60°C | Normal operation |
| 60-80°C | Warm, no throttling |
| 80-85°C | Throttling begins |
| > 85°C | Heavy throttling |

### Reading Temperature
```python
import time

def get_cpu_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
        return int(f.read()) / 1000.0

# GPU temperature (same sensor, different method)
import subprocess
def get_gpu_temp():
    result = subprocess.run(['vcgencmd', 'measure_temp'], 
                          capture_output=True, text=True)
    # Output: temp=45.6'C
    return float(result.stdout.split('=')[1].split("'")[0])
```

### Temperature Logging
```python
import csv
import time
from datetime import datetime

def log_temp(interval=60, filename='temps.csv'):
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'temp_c'])
        
        while True:
            temp = get_cpu_temp()
            writer.writerow([datetime.now().isoformat(), temp])
            f.flush()
            time.sleep(interval)
```

### Temperature Alerting
```python
def check_temp_alert(threshold=80):
    temp = get_cpu_temp()
    if temp > threshold:
        # Send notification
        subprocess.run(['notify-send', 'PI OVERHEATING!', f'{temp}°C'])
        # Or log to file
        with open('alerts.log', 'a') as f:
            f.write(f"{datetime.now()}: ALERT - {temp}°C\n")
```

## Throttling Detection

```python
def get_throttle_status():
    result = subprocess.run(['vcgencmd', 'get_throttled'], 
                          capture_output=True, text=True)
    hex_val = int(result.stdout.split('=')[1], 16)
    
    flags = {
        0: 'Under-voltage detected',
        1: 'Arm frequency capped',
        2: 'Currently throttled',
        3: 'Soft temperature limit active',
        16: 'Under-voltage has occurred',
        17: 'Arm frequency capping has occurred',
        18: 'Throttling has occurred',
        19: 'Soft temperature limit has occurred'
    }
    
    active = []
    for bit, desc in flags.items():
        if hex_val & (1 << bit):
            active.append(desc)
    return active
```

## CPU Monitoring

```python
def get_cpu_info():
    # Clock speed
    result = subprocess.run(['vcgencmd', 'measure_clock', 'arm'],
                          capture_output=True, text=True)
    clock_hz = int(result.stdout.split('=')[1])
    clock_mhz = clock_hz / 1_000_000
    
    # Load average
    with open('/proc/loadavg', 'r') as f:
        load = f.read().split()[:3]  # 1, 5, 15 min averages
    
    # CPU usage (percentage)
    with open('/proc/stat', 'r') as f:
        line = f.readline()
        fields = list(map(int, line.split()[1:]))
        idle = fields[3]
        total = sum(fields)
        usage = (1 - idle / total) * 100
    
    return {
        'clock_mhz': clock_mhz,
        'load': load,
        'usage_percent': usage
    }
```

## Memory Monitoring

```python
def get_memory_info():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
    
    mem_total = int(lines[0].split()[1])  # kB
    mem_available = int(lines[2].split()[1])  # kB
    mem_used = mem_total - mem_available
    
    return {
        'total_mb': mem_total / 1024,
        'used_mb': mem_used / 1024,
        'available_mb': mem_available / 1024,
        'usage_percent': (mem_used / mem_total) * 100
    }
```

## Disk Monitoring

```python
import shutil

def get_disk_info(path='/'):
    stat = shutil.disk_usage(path)
    return {
        'total_gb': stat.total / (1024**3),
        'used_gb': stat.used / (1024**3),
        'free_gb': stat.free / (1024**3),
        'usage_percent': (stat.used / stat.total) * 100
    }
```

## Network Monitoring

```python
def get_network_stats(interface='eth0'):
    with open(f'/sys/class/net/{interface}/statistics/rx_bytes', 'r') as f:
        rx_bytes = int(f.read())
    with open(f'/sys/class/net/{interface}/statistics/tx_bytes', 'r') as f:
        tx_bytes = int(f.read())
    
    return {
        'rx_mb': rx_bytes / (1024**2),
        'tx_mb': tx_bytes / (1024**2)
    }
```

## Dashboard Generation

```python
def generate_html_dashboard():
    temp = get_cpu_temp()
    cpu = get_cpu_info()
    mem = get_memory_info()
    disk = get_disk_info()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Pi Monitor</title>
        <meta http-equiv="refresh" content="5">
        <style>
            body {{ font-family: monospace; background: #1a1a1a; color: #0f0; padding: 20px; }}
            .metric {{ margin: 10px 0; padding: 10px; background: #2a2a2a; border-radius: 5px; }}
            .temp-high {{ color: #f44; }}
            .temp-ok {{ color: #4f4; }}
        </style>
    </head>
    <body>
        <h1>🥧 Raspberry Pi Monitor</h1>
        <div class="metric">
            <strong>CPU Temp:</strong> 
            <span class="{'temp-high' if temp > 80 else 'temp-ok'}">{temp:.1f}°C</span>
        </div>
        <div class="metric">
            <strong>CPU Clock:</strong> {cpu['clock_mhz']:.0f} MHz
        </div>
        <div class="metric">
            <strong>Memory:</strong> {mem['used_mb']:.0f}/{mem['total_mb']:.0f} MB 
            ({mem['usage_percent']:.1f}%)
        </div>
        <div class="metric">
            <strong>Disk:</strong> {disk['used_gb']:.1f}/{disk['total_gb']:.1f} GB
        </div>
    </body>
    </html>
    """
    
    with open('/tmp/pi_dashboard.html', 'w') as f:
        f.write(html)
```

## Voltage Monitoring

```python
def get_voltages():
    voltages = {}
    for id in ['core', 'sdram_c', 'sdram_i', 'sdram_p']:
        try:
            result = subprocess.run(['vcgencmd', 'measure_volts', id],
                                  capture_output=True, text=True)
            voltages[id] = float(result.stdout.split('=')[1].split('V')[0])
        except:
            pass
    return voltages
```

## Log Rotation

```python
import gzip
from pathlib import Path

def rotate_logs(log_dir='logs', max_size_mb=10, keep=5):
    log_path = Path(log_dir)
    for log_file in log_path.glob('*.log'):
        size_mb = log_file.stat().st_size / (1024**2)
        if size_mb > max_size_mb:
            # Rotate existing backups
            for i in range(keep-1, 0, -1):
                old = log_path / f"{log_file.stem}.{i}.gz"
                new = log_path / f"{log_file.stem}.{i+1}.gz"
                if old.exists():
                    old.rename(new)
            
            # Compress current log
            with open(log_file, 'rb') as f_in:
                with gzip.open(log_path / f"{log_file.stem}.1.gz", 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Clear original
            log_file.write_text('')
```
