# Automation Reference

Scheduling, services, and automated workflows on Raspberry Pi.

## Cron Jobs

### Crontab Format
```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, Sun=0 or 7)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Common Schedules
```bash
# Every minute
* * * * * /usr/bin/python3 /home/pi/script.py

# Every 5 minutes
*/5 * * * * /usr/bin/python3 /home/pi/script.py

# Every hour at :00
0 * * * * /usr/bin/python3 /home/pi/script.py

# Every day at 3 AM
0 3 * * * /usr/bin/python3 /home/pi/script.py

# Every Monday at 8 AM
0 8 * * 1 /usr/bin/python3 /home/pi/script.py

# Every reboot
@reboot /usr/bin/python3 /home/pi/script.py
```

### Managing Crontab
```bash
# Edit crontab
crontab -e

# List crontab
crontab -l

# Remove all crontab entries
crontab -r

# Root crontab
sudo crontab -e
```

### Python Script with Cron
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/pi/.local/lib/python3.11/site-packages')

# Your code here
```

### Cron Environment Variables
```bash
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/bin
HOME=/home/pi
PYTHONPATH=/home/pi/.local/lib/python3.11/site-packages

* * * * * /usr/bin/python3 /home/pi/script.py >> /home/pi/logs/script.log 2>&1
```

## Systemd Services

### Basic Service
```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/myapp
ExecStart=/usr/bin/python3 /home/pi/myapp/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Service Commands
```bash
# Enable service (start on boot)
sudo systemctl enable myapp.service

# Start service now
sudo systemctl start myapp.service

# Check status
sudo systemctl status myapp.service

# Stop service
sudo systemctl stop myapp.service

# View logs
sudo journalctl -u myapp.service -f

# Reload after changes
sudo systemctl daemon-reload
```

### Service with Environment
```ini
[Service]
Environment="API_KEY=secret"
Environment="DEBUG=1"
EnvironmentFile=/home/pi/myapp/.env
ExecStart=/usr/bin/python3 /home/pi/myapp/main.py
```

## Watchdog / File Monitoring

### Using watchdog Library
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(f"File modified: {event.src_path}")
    
    def on_created(self, event):
        print(f"File created: {event.src_path}")

observer = Observer()
observer.schedule(MyHandler(), path='/home/pi/watch', recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

### Simple Polling
```python
import os
import time
from pathlib import Path

def watch_file(filepath, callback):
    last_mtime = 0
    while True:
        try:
            mtime = os.path.getmtime(filepath)
            if mtime != last_mtime:
                last_mtime = mtime
                callback(filepath)
        except FileNotFoundError:
            pass
        time.sleep(1)

def on_change(filepath):
    print(f"{filepath} changed!")

watch_file('/home/pi/data.txt', on_change)
```

## Webhook Server

### Flask Webhook Receiver
```python
from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if data.get('event') == 'deploy':
        subprocess.run(['/home/pi/deploy.sh'])
        return jsonify({'status': 'deploying'})
    
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Simple HTTP Trigger
```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/trigger':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # Do something with data
            print(f"Received: {data}")
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')

server = HTTPServer(('0.0.0.0', 8080), Handler)
server.serve_forever()
```

## Startup Scripts

### rc.local (Legacy)
```bash
#!/bin/bash
# /etc/rc.local

# Run before exit 0
/usr/bin/python3 /home/pi/startup.py &

exit 0
```

Make executable:
```bash
sudo chmod +x /etc/rc.local
```

### .bashrc (Login scripts)
```bash
# Run on login
if [ -f /home/pi/startup.sh ]; then
    /home/pi/startup.sh
fi
```

### Autostart (Desktop)
```
# ~/.config/autostart/myapp.desktop
[Desktop Entry]
Type=Application
Name=MyApp
Exec=/usr/bin/python3 /home/pi/myapp.py
```

## Scheduled Tasks with Schedule Library

```python
import schedule
import time

def job():
    print("Running scheduled task...")

# Every 10 minutes
schedule.every(10).minutes.do(job)

# Every hour
schedule.every().hour.do(job)

# Daily at specific time
schedule.every().day.at("10:30").do(job)

# Monday specific
schedule.every().monday.do(job)
schedule.every().monday.at("08:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

## MQTT Automation

```python
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    client.subscribe("home/livingroom/temperature")

def on_message(client, userdata, msg):
    temp = float(msg.payload)
    if temp > 25:
        # Turn on fan
        pass

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)
client.loop_forever()
```

## Error Handling & Logging

### Robust Automation Script
```python
import logging
import traceback
from datetime import datetime

logging.basicConfig(
    filename='/home/pi/logs/automation.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def safe_run(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            logging.error(traceback.format_exc())
    return wrapper

@safe_run
def my_automation():
    # Your code here
    pass

if __name__ == '__main__':
    logging.info("Starting automation")
    my_automation()
```

## Health Checks

```python
import requests
import smtplib
from email.mime.text import MIMEText

def check_service(url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def send_alert(message):
    msg = MIMEText(message)
    msg['Subject'] = 'Pi Alert'
    msg['From'] = 'pi@localhost'
    msg['To'] = 'admin@example.com'
    
    with smtplib.SMTP('localhost') as s:
        s.send_message(msg)

# Check every 5 minutes
if not check_service('http://localhost:8080'):
    send_alert('Service is down!')
```
