# J1MSKY Agency - Complete Business Manual
## For Agency Operators and Entrepreneurs

---

## 🚀 QUICK START (5 Minutes)

### What You're Building
J1MSKY is an AI-powered agency that runs itself. You deploy agents to do work, and they operate autonomously while you sleep.

### Your First 5 Minutes:
1. **Open Dashboard:** http://your-pi-ip:8080
2. **Click "Spawn Agent"**
3. **Enter task:** "Research competitors"
4. **Select model:** Kimi K2.5
5. **Watch it work**

---

## 📱 SYSTEM REQUIREMENTS

### Hardware:
- **Minimum:** Raspberry Pi 4 (4GB RAM)
- **Recommended:** Raspberry Pi 4 (8GB RAM)
- **Storage:** 32GB+ SD card
- **Network:** Internet connection

### Software:
- Raspberry Pi OS (64-bit)
- Python 3.11+
- Node.js 18+
- Git

### Access:
- **Local:** http://localhost:8080
- **Network:** http://[pi-ip]:8080
- **Mobile:** Same URLs on your phone

---

## 🏢 THE DASHBOARD

### Navigation Tabs:

#### 1. 🏢 The Office
Your command center. See all agents working in real-time on a video-game style map.

**Features:**
- Live agent positions
- System health monitors
- Quick action buttons
- Event log

**How to use:**
- Watch agents move as they work
- Click agents to see details
- Use quick buttons for common tasks

#### 2. 👥 Teams
Deploy pre-configured teams for specific tasks.

**Available Teams:**
- **Code Team:** Programming, debugging, system architecture
- **Creative Team:** Content creation, design, documentation
- **Research Team:** Web search, data analysis, market research
- **Business Team:** Strategy, planning, revenue optimization

**How to deploy:**
1. Click team card
2. Enter objective
3. Click "Deploy Team"
4. Monitor progress

#### 3. 🤖 Models
Individual AI models you can spawn for specific tasks.

**Available Models:**
- **Kimi K2.5:** Fast, efficient coding ($0.001/1K tokens)
- **Claude Sonnet:** Creative, analytical work ($0.003/1K tokens)
- **Claude Opus:** Deep reasoning, complex tasks ($0.015/1K tokens)

**When to use each:**
- **Quick coding:** Kimi
- **Documentation/design:** Sonnet
- **Architecture decisions:** Opus

#### 4. 🚀 Spawn
Create custom agents with specific tasks.

**Process:**
1. Describe what you need
2. Select priority (Low/Normal/High)
3. Choose model
4. Agent spawns and works

#### 5. ⚡ Rate Limits
Monitor your API usage and costs.

**Shows:**
- Requests used/remaining
- Cost per service
- Rate limit status
- Cooldown timers

---

## 💰 MAKING MONEY

### Revenue Models:

#### 1. AI Agency as a Service ($99/month)
**What you sell:** Managed AI agents for clients

**Setup:**
1. Client pays you $99/month
2. You deploy agents for their tasks
3. Agents work 24/7
4. You keep $99 - API costs = profit

**Example:**
- Client: Small business
- Task: Social media management
- Your cost: ~$30/month in API calls
- Your profit: $69/month per client

#### 2. Pay-Per-Task ($0.10 - $5.00)
**What you sell:** Individual agent tasks

**Pricing:**
- Simple task: $0.50
- Medium task: $2.00
- Complex task: $5.00

**Example tasks:**
- "Write a blog post": $2.00
- "Debug this code": $1.50
- "Research competitors": $3.00

#### 3. Agent Teams ($49/month per team)
**What you sell:** Dedicated agent teams

**Teams available:**
- Code Team: $49/month
- Creative Team: $49/month
- Research Team: $49/month
- Business Team: $49/month

#### 4. Enterprise (Custom)
**What you sell:** Custom solutions

**Contact:** Direct sales
**Price:** $500+/month
**Includes:** Dedicated infrastructure, SLA, support

---

## 📊 PRICING STRATEGY

### Cost Breakdown:

| Model | Cost per 1K tokens | Typical Task Cost |
|-------|-------------------|-------------------|
| Kimi K2.5 | $0.001 | $0.01 - $0.05 |
| Claude Sonnet | $0.003 | $0.03 - $0.15 |
| Claude Opus | $0.015 | $0.15 - $0.50 |

### Markup Strategy:
**Charge 3-5x your cost**

Example:
- Task costs you: $0.20
- You charge: $0.80 - $1.00
- Profit: $0.60 - $0.80

### Quick Quote Check (Ops-Safe)

Before sending a pay-per-task quote, run:

```bash
curl http://localhost:8080/api/orchestrator/status
```

Look for:
- `pricing_policy` → active markup + minimum price floor
- `example_task_quote` → sample recommended price and margin band
- `pricing_guardrail_check` → whether quote profile is compliant or should escalate

If `pricing_guardrail_check.action` returns `escalate_deal_desk`, do not send final pricing until reviewed.

---

## 🎯 USE CASES

### For Businesses:
- **Content Creation:** Blog posts, social media, emails
- **Research:** Market analysis, competitor research
- **Development:** Code review, debugging, documentation
- **Support:** FAQ generation, documentation

### For Developers:
- **Code Generation:** Boilerplate, utilities
- **Debugging:** Error analysis, fixes
- **Documentation:** API docs, README files
- **Testing:** Test case generation

### For Marketers:
- **Copywriting:** Ads, landing pages, emails
- **SEO:** Keyword research, optimization
- **Analytics:** Data analysis, reports
- **Strategy:** Campaign planning

---

## 🔧 ADVANCED FEATURES

### Agent Swarm:
Deploy multiple agents that work together.

**Example:**
- Agent 1: Research topic
- Agent 2: Write outline
- Agent 3: Write content
- Agent 4: Edit and optimize

**Result:** Complete blog post in 10 minutes

### Auto-Scaling:
System automatically spawns more agents when busy.

**How it works:**
1. Queue builds up
2. System detects load
3. Spawns additional agents
4. Distributes tasks
5. Scales down when done

### Cost Optimization:
Automatically selects cheapest model for the task.

**Logic:**
- Simple task → Kimi (cheapest)
- Creative task → Sonnet (balanced)
- Complex task → Opus (expensive but necessary)

---

## 📈 SCALING YOUR AGENCY

### Phase 1: Solo ($500/month)
- You + J1MSKY
- 5-10 clients
- Manual onboarding
- Profit: ~$300/month

### Phase 2: Growth ($2,000/month)
- 20-50 clients
- Automated onboarding
- Multiple Pi nodes
- Profit: ~$1,200/month

### Phase 3: Scale ($10,000/month)
- 100+ clients
- Full automation
- Pi cluster
- Profit: ~$6,000/month

---

## 🛠️ CUSTOMIZATION

### Adding New Agents:
1. Edit `agents/custom.py`
2. Define agent class
3. Add to dashboard
4. Deploy

### Custom Skills:
1. Create skill file in `skills/`
2. Implement API calls
3. Register in config
4. Use in agents

### White Label:
1. Edit branding in `config/branding.json`
2. Replace logos
3. Customize colors
4. Deploy as your own

---

## 🚨 TROUBLESHOOTING

### Dashboard Not Loading:
1. Check Pi is running: `ping [pi-ip]`
2. Check server: `curl http://localhost:8080`
3. Restart: `./start-teams-v4.sh`

### Agent Not Spawning:
1. Check rate limits tab
2. Verify API keys in config
3. Check logs: `tail /tmp/teams-v4.log`

### High Costs:
1. Review rate limits panel
2. Switch to cheaper models
3. Batch tasks together
4. Set spending alerts

### Slow Performance:
1. Check CPU temp (should be <80°C)
2. Close unnecessary apps
3. Restart Pi if needed
4. Check memory usage

---

## 📞 SUPPORT

### Documentation:
- Full manual: `AGENCY_MANUAL.md`
- API reference: `API_REFERENCE.md`
- Business guide: `BUSINESS_SETUP.md`

### Community:
- GitHub: github.com/Mind-Expansion-Industries/j1msky-framework
- Issues: Report bugs on GitHub
- Updates: Watch repository

---

## 💡 PRO TIPS

1. **Start small:** Begin with one client, scale gradually
2. **Track costs:** Monitor rate limits daily
3. **Use teams:** They're optimized for specific tasks
4. **Batch work:** Group similar tasks for efficiency
5. **Cache results:** Save common outputs
6. **Automate everything:** Let agents handle routine tasks
7. **Test before selling:** Run tasks yourself first
8. **Price confidently:** 3-5x markup is standard
9. **Document everything:** Create SOPs with agents
10. **Reinvest profits:** Add more Pis, scale up

---

## 🎓 LEARNING PATH

### Week 1: Basics
- Set up your Pi
- Deploy first agent
- Complete 10 tasks
- Understand costs

### Week 2: Operations
- Deploy agent teams
- Handle 5 clients
- Optimize costs
- Document processes

### Week 3: Business
- Launch pricing page
- Get 10 paying clients
- Automate onboarding
- Track metrics

### Week 4: Scale
- Add second Pi
- Hire virtual assistant
- Launch marketing
- Target $1,000/month

---

## 🛠️ TROUBLESHOOTING GUIDE

### Quick Diagnostics

Run this checklist first:
```bash
# Check system health
curl http://localhost:8080/api/system

# Check rate limits
curl http://localhost:8080/api/rate-limits

# View recent logs
tail -f /tmp/teams-v4.log
```

### Common Issues

#### Dashboard Won't Load

**Symptoms:** Browser shows "Connection refused" or timeout

**Solutions:**
1. **Check if service is running:**
   ```bash
   ps aux | grep j1msky-teams
   ```
   If not running: `./start-teams-v4.sh`

2. **Check port availability:**
   ```bash
   sudo lsof -i :8080
   ```
   If port busy: `sudo kill -9 <PID>` then restart

3. **Firewall issues:**
   ```bash
   sudo ufw allow 8080/tcp
   ```

4. **Check for errors:**
   ```bash
   cat /tmp/teams-v4.log | grep ERROR
   ```

#### Agent Spawn Failed

**Symptoms:** "Rate limited" or "Failed to spawn agent" error

**Solutions:**
1. **Check rate limits:**
   - Wait for rate limit reset (shown in dashboard)
   - Switch to cheaper model (Kimi K2.5 vs Sonnet)

2. **Check API keys:**
   ```bash
   cat config/api-keys.json
   ```
   Verify keys are valid and not expired

3. **Model availability:**
   - Some models may be temporarily unavailable
   - Try alternative model

#### High Costs / Budget Alerts

**Symptoms:** Daily cost exceeding $50, budget warnings

**Solutions:**
1. **Switch default model:**
   - Edit `config/model-defaults.json`
   - Set `"default": "k2p5"` (cheapest)

2. **Review expensive tasks:**
   ```bash
   cat logs/usage_$(date +%Y-%m-%d).json
   ```
   Identify which agents/tasks cost most

3. **Set hard budget cap:**
   - Dashboard → Settings → Budget Cap
   - Set to $30/day to force cost-conscious model selection

#### Slow Response Times

**Symptoms:** Agents taking 10+ minutes to complete simple tasks

**Solutions:**
1. **Check system resources:**
   ```bash
   htop  # Check CPU/RAM
   vcgencmd measure_temp  # Check temperature
   ```
   If temp > 80°C: Improve cooling, reduce overclock

2. **Too many concurrent agents:**
   - Limit to 3-5 active agents on Pi 4
   - Queue tasks instead of spawning all at once

3. **Network issues:**
   ```bash
   ping -c 4 api.openai.com
   ```
   Check internet connectivity

#### Agent Returns Poor Results

**Symptoms:** Output is wrong, incomplete, or off-topic

**Solutions:**
1. **Improve task description:**
   - Be specific and detailed
   - Include examples
   - Define expected output format

2. **Use correct model:**
   - Code → Kimi K2.5
   - Writing → Sonnet
   - Complex reasoning → Opus

3. **Break into smaller tasks:**
   - Instead of one big task, chain 3-4 smaller ones
   - Use teams for complex workflows

#### Git Sync Issues

**Symptoms:** "Failed to commit" or merge conflicts

**Solutions:**
1. **Check git status:**
   ```bash
   cd /home/m1ndb0t/Desktop/J1MSKY
   git status
   ```

2. **Manual sync:**
   ```bash
   git add -A
   git commit -m "Manual sync"
   git pull origin main --rebase
   git push
   ```

3. **Reset if needed:**
   ```bash
   git reset --hard HEAD  # Discard local changes
   git pull
   ```

### Error Code Reference

| Code | Meaning | Fix |
|------|---------|-----|
| `E001` | Rate limit exceeded | Wait 1 hour or switch model |
| `E002` | API key invalid | Check/replace API key |
| `E003` | Model unavailable | Try different model |
| `E004` | Task timeout | Break into smaller tasks |
| `E005` | Out of memory | Reduce concurrent agents |
| `E006` | Disk full | Clean up logs: `rm logs/*.old` |
| `E007` | Network timeout | Check internet connection |
| `E008` | Permission denied | Check file permissions |

### Recovery Procedures

#### Full System Restart

When everything is broken:
```bash
# 1. Stop all services
pkill -f j1msky

# 2. Clear temporary files
rm -f /tmp/teams-v4.log
rm -f /tmp/*.pid

# 3. Check disk space
df -h

# 4. Restart
./start-teams-v4.sh

# 5. Verify
sleep 5
curl http://localhost:8080/api/system
```

#### Database Reset (Last Resort)

**WARNING:** This clears all task history!
```bash
# Backup first
cp logs/usage_*.json logs/backup/

# Reset
rm -f logs/usage_*.json
rm -f config/state.json

# Restart
./start-teams-v4.sh
```

### Getting Help

**Before asking for help, gather:**
1. Output of `curl http://localhost:8080/api/system`
2. Last 50 lines of `/tmp/teams-v4.log`
3. Recent changes made (config edits, etc.)
4. Steps to reproduce the issue

**Support channels:**
- GitHub Issues: github.com/Mind-Expansion-Industries/j1msky-framework
- Discord: discord.gg/j1msky (community)
- Email: support@j1msky.ai (paid users)

---

## 🚀 DEPLOYMENT GUIDE

### Pre-Deployment Checklist

**Hardware Requirements:**
- [ ] Raspberry Pi 4 (4GB or 8GB RAM)
- [ ] 32GB+ microSD card (Class 10 or UHS-I)
- [ ] Power supply (official 5V/3A recommended)
- [ ] Ethernet connection or WiFi configured
- [ ] Case with cooling (fan or heatsink)

**Software Prerequisites:**
- [ ] Raspberry Pi OS (64-bit Lite or Desktop)
- [ ] Python 3.11+ installed
- [ ] Git configured with your credentials
- [ ] SSH access enabled (for headless setup)
- [ ] Static IP or DDNS configured (for remote access)

### Installation Steps

#### Step 1: Prepare the Pi
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git htop curl

# Install Node.js (for future web components)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

#### Step 2: Clone Repository
```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/Mind-Expansion-Industries/j1msky-framework.git

# Enter directory
cd j1msky-framework

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

#### Step 3: Configuration
```bash
# Create config directory
mkdir -p config

# Create API keys file
cat > config/api-keys.json << 'EOF'
{
  "anthropic": "sk-ant-your-key-here",
  "kimi": "kimi-your-key-here",
  "openai": "sk-your-key-here"
}
EOF

# Set permissions
chmod 600 config/api-keys.json

# Create environment file
cat > .env << 'EOF'
J1MSKY_DASHBOARD_PORT=8080
J1MSKY_LOG_LEVEL=info
J1MSKY_DAILY_BUDGET=50.0
J1MSKY_ENABLE_WEBHOOKS=true
EOF
```

#### Step 4: Test Installation
```bash
# Run diagnostics
python3 -c "import sys; print(sys.version)"
python3 -c "from j1msky_teams_v4 import *; print('Import successful')"

# Check system stats
curl http://localhost:8080/api/system

# Test spawning an agent
curl -X POST http://localhost:8080/api/spawn \
  -H "Content-Type: application/json" \
  -d '{"model": "k2p5", "task": "test deployment"}'
```

#### Step 5: Set Up Systemd Service
```bash
# Create service file
sudo tee /etc/systemd/system/j1msky.service > /dev/null << 'EOF'
[Unit]
Description=J1MSKY Agent Teams
After=network.target

[Service]
Type=simple
User=m1ndb0t
WorkingDirectory=/home/m1ndb0t/Desktop/J1MSKY
Environment=PATH=/home/m1ndb0t/Desktop/J1MSKY/venv/bin
ExecStart=/home/m1ndb0t/Desktop/J1MSKY/venv/bin/python j1msky-teams-v4.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable j1msky
sudo systemctl start j1msky

# Check status
sudo systemctl status j1msky
```

### Production Deployment

#### Reverse Proxy with Nginx
```bash
# Install Nginx
sudo apt install -y nginx

# Create Nginx config
sudo tee /etc/nginx/sites-available/j1msky > /dev/null << 'EOF'
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/j1msky /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### SSL with Let's Encrypt
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

#### Firewall Configuration
```bash
# Install UFW
sudo apt install -y ufw

# Configure
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8080/tcp  # Direct access (optional)

# Enable
sudo ufw enable
sudo ufw status
```

### Monitoring Setup

#### Basic Health Checks
```bash
# Create health check script
cat > ~/health-check.sh << 'EOF'
#!/bin/bash
HEALTH=$(curl -s http://localhost:8080/api/system | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
    echo "ALERT: J1MSKY health check failed at $(date)" | tee -a ~/alerts.log
    # Send notification (configure as needed)
    # curl -X POST "https://your-webhook-url" -d "J1MSKY unhealthy"
fi
EOF

chmod +x ~/health-check.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/m1ndb0t/health-check.sh") | crontab -
```

#### Log Rotation
```bash
# Configure logrotate
sudo tee /etc/logrotate.d/j1msky > /dev/null << 'EOF'
/home/m1ndb0t/Desktop/J1MSKY/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 m1ndb0t m1ndb0t
}
EOF
```

### Backup Strategy

#### Automated Backups
```bash
# Create backup script
cat > ~/backup-j1msky.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/m1ndb0t/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup configs
tar czf "$BACKUP_DIR/config_$DATE.tar.gz" -C /home/m1ndb0t/Desktop/J1MSKY config/

# Backup logs
tar czf "$BACKUP_DIR/logs_$DATE.tar.gz" -C /home/m1ndb0t/Desktop/J1MSKY logs/

# Keep only last 10 backups
ls -t $BACKUP_DIR/config_*.tar.gz | tail -n +11 | xargs rm -f
ls -t $BACKUP_DIR/logs_*.tar.gz | tail -n +11 | xargs rm -f

echo "Backup completed: $DATE"
EOF

chmod +x ~/backup-j1msky.sh

# Daily backup at 2 AM
(crontab -l 2>/dev/null; echo "0 2 * * * /home/m1ndb0t/backup-j1msky.sh") | crontab -
```

### Updating the System

#### Safe Update Process
```bash
# 1. Stop service
sudo systemctl stop j1msky

# 2. Backup current installation
cp -r ~/Desktop/J1MSKY ~/Desktop/J1MSKY-backup-$(date +%Y%m%d)

# 3. Pull latest code
cd ~/Desktop/J1MSKY
git pull origin main

# 4. Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. Start service
sudo systemctl start j1msky

# 6. Verify
sleep 5
curl http://localhost:8080/api/system
```

### Troubleshooting Deployment Issues

**Issue: Service won't start**
```bash
# Check logs
sudo journalctl -u j1msky -n 100

# Check for port conflicts
sudo lsof -i :8080

# Verify Python environment
source venv/bin/activate
python --version
```

**Issue: Permission denied**
```bash
# Fix ownership
sudo chown -R m1ndb0t:m1ndb0t ~/Desktop/J1MSKY

# Fix permissions
chmod 600 config/api-keys.json
chmod 755 *.sh
```

### Troubleshooting Deployment Issues

**Issue: Service won't start**
```bash
# Check logs
sudo journalctl -u j1msky -n 100

# Check for port conflicts
sudo lsof -i :8080

# Verify Python environment
source venv/bin/activate
python --version
```

**Issue: Permission denied**
```bash
# Fix ownership
sudo chown -R m1ndb0t:m1ndb0t ~/Desktop/J1MSKY

# Fix permissions
chmod 600 config/api-keys.json
chmod 755 *.sh
```

**Issue: Out of memory**
```bash
# Check memory
free -h

# Add swap space if needed
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---

## ⚡ PERFORMANCE TUNING

### System-Level Optimizations

#### Raspberry Pi Configuration

**Boot Configuration (`/boot/config.txt`):**
```bash
# Overclock (if cooling is adequate)
arm_freq=2000
over_voltage=6

# GPU memory (minimum since headless)
gpu_mem=16

# Enable 64-bit mode
arm_64bit=1
```

**Memory Optimization:**
```bash
# Reduce swappiness (use RAM before swap)
sudo sysctl vm.swappiness=10

# Add to /etc/sysctl.conf for persistence
echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

#### Python Application Tuning

**Gunicorn Configuration (for production):**
```python
# gunicorn.conf.py
workers = 4  # (2 x CPU cores) + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Memory optimization
preload_app = True
```

**Memory Leak Prevention:**
```python
# In your application
import gc

# Force garbage collection between heavy operations
gc.collect()

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory: {process.memory_info().rss / 1024 / 1024:.1f} MB")
```

### Database Optimization (if applicable)

**SQLite Performance:**
```sql
-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;

-- Increase cache size (in pages)
PRAGMA cache_size=10000;

-- Optimize for bulk operations
PRAGMA synchronous=NORMAL;
```

**Connection Pooling:**
```python
from sqlalchemy import create_engine

engine = create_engine(
    'sqlite:///data.db',
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Caching Strategy

**In-Memory Caching:**
```python
from functools import lru_cache
import time

# Simple LRU cache
@lru_cache(maxsize=128)
def expensive_operation(param):
    return compute_result(param)

# TTL cache implementation
class TTLCache:
    def __init__(self, ttl_seconds=300):
        self.ttl = ttl_seconds
        self.cache = {}
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())
```

**Redis Caching (if available):**
```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Cache with 5 minute TTL
r.setex('key', 300, 'value')

# Retrieve
cached = r.get('key')
```

### Async I/O Optimization

**Using asyncio for Concurrent Operations:**
```python
import asyncio
import aiohttp

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_one(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_one(session, url):
    async with session.get(url) as response:
        return await response.text()

# Run concurrently
urls = ['http://api1.com', 'http://api2.com', 'http://api3.com']
results = asyncio.run(fetch_all(urls))
```

### Load Testing

**Using Apache Bench:**
```bash
# Install
sudo apt-get install apache2-utils

# Basic load test
ab -n 1000 -c 10 http://localhost:8080/api/system

# Results interpretation:
# - Requests/sec: Higher is better
# - Time per request: Lower is better
# - Failed requests: Should be 0
```

**Using Locust (Python-based):**
```python
# locustfile.py
from locust import HttpUser, task, between

class J1MSKYUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def spawn_agent(self):
        self.client.post("/api/spawn", json={
            "model": "k2p5",
            "task": "Performance test task"
        })
    
    @task(3)
    def check_status(self):
        self.client.get("/api/agents")
```

### Monitoring Performance

**Key Metrics to Track:**

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Response Time (p50) | < 200ms | > 500ms |
| Response Time (p99) | < 1000ms | > 3000ms |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 85% |
| Memory Usage | < 80% | > 90% |
| Disk I/O | < 50 MB/s | > 100 MB/s |

**Custom Metrics Script:**
```python
import psutil
import time
from prometheus_client import Gauge, start_http_server

# Define metrics
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage')
MEM_USAGE = Gauge('memory_usage_percent', 'Memory usage')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage')

def collect_metrics():
    while True:
        CPU_USAGE.set(psutil.cpu_percent())
        MEM_USAGE.set(psutil.virtual_memory().percent)
        DISK_USAGE.set(psutil.disk_usage('/').percent)
        time.sleep(10)

# Start metrics server
start_http_server(9090)
collect_metrics()
```

### Bottleneck Analysis

**Identify Slow Operations:**
```python
import time
from contextlib import contextmanager

@contextmanager
def timer(operation_name):
    start = time.time()
    yield
    elapsed = time.time() - start
    print(f"{operation_name}: {elapsed:.3f}s")

# Usage
with timer("Database query"):
    results = db.query()

with timer("API call"):
    response = api.fetch()
```

**Profiling with cProfile:**
```bash
# Run with profiler
python -m cProfile -o profile.stats j1msky-teams-v4.py

# Analyze results
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative')
p.print_stats(20)
"
```

### Scaling Strategies

**Vertical Scaling (Bigger Pi):**
- Raspberry Pi 4 → 8GB model
- External SSD for storage
- Active cooling for overclocking

**Horizontal Scaling (Multiple Pis):**
```
Load Balancer (Nginx)
    ├── Pi Node 1 (Port 8081)
    ├── Pi Node 2 (Port 8082)
    └── Pi Node 3 (Port 8083)
```

**Queue-Based Architecture:**
```
Request → Queue (Redis/RabbitMQ) → Worker Nodes → Results
```

### Performance Checklist

**Before Launch:**
- [ ] Load tested with expected traffic
- [ ] Memory leaks checked (run overnight)
- [ ] Database queries optimized
- [ ] Static assets cached/CDN'd
- [ ] Error monitoring configured

**Weekly:**
- [ ] Review response time trends
- [ ] Check for slow queries
- [ ] Monitor error rates
- [ ] Review resource utilization

**Monthly:**
- [ ] Capacity planning review
- [ ] Performance regression testing
- [ ] Optimize based on usage patterns
- [ ] Update performance baselines

---

## 🔮 FUTURE FEATURES

Coming soon:
- Mobile app (iOS/Android)
- Voice control
- Advanced analytics
- Multi-language support
- API for developers
- Plugin marketplace
- Training courses

---

## ◈ CONCLUSION

You now have an AI agency that:
- Works 24/7
- Scales automatically
- Costs pennies per task
- Earns dollars per client
- Improves itself

**Your job:** Deploy agents, monitor dashboard, collect revenue.

**The agents' job:** Everything else.

Welcome to the future of work.

---

*Manual Version: 1.0*  
*Last Updated: February 19, 2026*  
*Status: Business-Ready*
