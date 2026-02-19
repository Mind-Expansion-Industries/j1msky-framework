# J1MSKY API Reference
## For Developers and Integrators

---

## 🔑 Authentication

### API Key
All requests require an API key in the header:
```
Authorization: Bearer YOUR_API_KEY
```

### Getting an API Key
1. Log into dashboard
2. Go to Settings → API
3. Generate new key
4. Copy and store securely

---

## 🌐 Base URL

```
http://your-pi-ip:8080/api
```

---

## 📚 Endpoints

### 1. Spawn Agent
Create a new agent to complete a task.

**Endpoint:** `POST /spawn`

**Request:**
```json
{
  "model": "k2p5|sonnet|opus",
  "task": "string",
  "priority": "low|normal|high",
  "timeout": 300
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "subagent_1234567890_1234",
  "model": "k2p5",
  "status": "spawning",
  "estimated_cost": 0.05
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/spawn \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "k2p5",
    "task": "Write a Python function to calculate fibonacci",
    "priority": "normal"
  }'
```

---

### 2. Spawn Team
Deploy an entire team for complex tasks.

**Endpoint:** `POST /spawn-team`

**Request:**
```json
{
  "team": "team_coding|team_creative|team_research|team_business",
  "task": "string",
  "priority": "low|normal|high"
}
```

**Response:**
```json
{
  "success": true,
  "agent_id": "subagent_1234567890_5678",
  "team": "team_coding",
  "models": ["kimi-coding/k2p5", "anthropic/claude-sonnet-4-6"],
  "status": "spawning"
}
```

**Example:**
```bash
curl -X POST http://localhost:8080/api/spawn-team \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "team": "team_creative",
    "task": "Design a landing page for our product",
    "priority": "high"
  }'
```

---

### 3. Get Agent Status
Check the status of a spawned agent.

**Endpoint:** `GET /agent/{agent_id}`

**Response:**
```json
{
  "agent_id": "subagent_1234567890_1234",
  "model": "k2p5",
  "status": "running|completed|failed",
  "task": "Write a Python function...",
  "created": "2026-02-19T10:00:00Z",
  "started": "2026-02-19T10:00:05Z",
  "completed": "2026-02-19T10:02:30Z",
  "result": "def fibonacci(n): ...",
  "cost": 0.03
}
```

**Example:**
```bash
curl http://localhost:8080/api/agent/subagent_1234567890_1234 \
  -H "Authorization: Bearer YOUR_KEY"
```

---

### 4. List Active Agents
Get all currently running agents.

**Endpoint:** `GET /agents`

**Response:**
```json
{
  "agents": [
    {
      "agent_id": "subagent_1234567890_1234",
      "model": "k2p5",
      "status": "running",
      "task": "Write Python function..."
    }
  ],
  "count": 1,
  "total_cost_today": 0.45
}
```

---

### 5. Get Rate Limits
Check current rate limit status.

**Endpoint:** `GET /rate-limits`

**Response:**
```json
{
  "limits": {
    "kimi": {
      "used": 45,
      "limit": 100,
      "remaining": 55,
      "reset_at": "2026-02-19T11:00:00Z"
    },
    "anthropic": {
      "used": 12,
      "limit": 50,
      "remaining": 38,
      "reset_at": "2026-02-19T11:00:00Z"
    }
  }
}
```

---

### 6. Get System Stats
Retrieve system health information.

**Endpoint:** `GET /system`

**Response:**
```json
{
  "cpu_temp": 65.5,
  "load_average": 0.75,
  "memory_usage": 45.2,
  "uptime": "24h 15m",
  "disk_free": "45G",
  "active_agents": 3
}
```

---

### 7. Cancel Agent
Stop a running agent.

**Endpoint:** `DELETE /agent/{agent_id}`

**Response:**
```json
{
  "success": true,
  "message": "Agent cancelled",
  "refund": 0.01
}
```

---

## 📊 Webhooks

### Configure Webhook
Receive notifications when agents complete.

**Endpoint:** `POST /webhooks`

**Request:**
```json
{
  "url": "https://your-app.com/webhook",
  "events": ["agent.completed", "agent.failed"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload
```json
{
  "event": "agent.completed",
  "timestamp": "2026-02-19T10:02:30Z",
  "data": {
    "agent_id": "subagent_1234567890_1234",
    "model": "k2p5",
    "task": "Write Python function...",
    "result": "def fibonacci(n): ...",
    "cost": 0.03
  }
}
```

---

## 💰 Billing

### Get Usage
**Endpoint:** `GET /billing/usage`

**Response:**
```json
{
  "period": "2026-02-01 to 2026-02-19",
  "total_cost": 45.67,
  "by_model": {
    "k2p5": 12.34,
    "sonnet": 23.45,
    "opus": 9.88
  },
  "by_day": {
    "2026-02-19": 3.45
  }
}
```

---

## 🔧 SDK Usage

### Python SDK
```python
from j1msky import Agency

# Initialize
agency = Agency(api_key="YOUR_KEY", base_url="http://localhost:8080")

# Spawn agent
agent = agency.spawn(
    model="k2p5",
    task="Write a blog post about AI",
    priority="normal"
)

# Wait for completion
result = agent.wait_for_completion()
print(result.output)
```

### JavaScript SDK
```javascript
const { Agency } = require('j1msky-sdk');

const agency = new Agency({
  apiKey: 'YOUR_KEY',
  baseUrl: 'http://localhost:8080'
});

// Spawn agent
const agent = await agency.spawn({
  model: 'k2p5',
  task: 'Write a blog post about AI',
  priority: 'normal'
});

// Get result
const result = await agent.waitForCompletion();
console.log(result.output);
```

---

## ⚠️ Error Codes

| Code | Meaning | Solution |
|------|---------|----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Check API key |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check logs, retry |
| 503 | Service Unavailable | Server overloaded |

### Error Response
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```

---

## 📈 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /spawn | 100 | 1 hour |
| GET /agent/* | 1000 | 1 hour |
| GET /agents | 100 | 1 hour |
| GET /system | 60 | 1 hour |

---

## 🔒 Security

### Best Practices
1. Store API keys securely
2. Use HTTPS in production
3. Rotate keys regularly
4. Monitor usage
5. Set spending alerts

### IP Whitelist
Restrict API access by IP:
```bash
# In config.json
{
  "allowed_ips": ["192.168.1.0/24", "10.0.0.5"]
}
```

---

## 🧪 Examples

### Example 1: Content Creation Pipeline
```python
# Step 1: Research
researcher = agency.spawn(
    model="sonnet",
    task="Research: Latest AI trends 2026",
    priority="high"
)
research = researcher.wait_for_completion()

# Step 2: Write
writer = agency.spawn(
    model="sonnet", 
    task=f"Write blog post about: {research.summary}",
    priority="normal"
)
article = writer.wait_for_completion()

# Step 3: Edit
editor = agency.spawn(
    model="opus",
    task=f"Edit and improve: {article.output}",
    priority="normal"
)
final = editor.wait_for_completion()
```

### Example 2: Code Review System
```python
# Submit code for review
reviewer = agency.spawn(
    model="k2p5",
    task=f"Review this code:\n{code}",
    priority="normal"
)
review = reviewer.wait_for_completion()

# Apply fixes
fixer = agency.spawn(
    model="k2p5",
    task=f"Fix these issues:\n{review.issues}",
    priority="high"
)
fixed_code = fixer.wait_for_completion()
```

---

## 📚 Resources

- **Full Docs:** https://docs.j1msky.ai
- **GitHub:** https://github.com/Mind-Expansion-Industries/j1msky-framework
- **Support:** support@j1msky.ai
- **Status:** https://status.j1msky.ai

---

*API Version: 4.0*  
*Last Updated: February 19, 2026*
