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
