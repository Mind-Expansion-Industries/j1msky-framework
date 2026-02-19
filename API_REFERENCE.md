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
    "retry_after": 3600,
    "request_id": "req_abc123xyz"
  }
}
```

---

## 🔁 Retry Strategies

### Exponential Backoff
Recommended approach for 429 and 503 errors:

```python
import time
import random

def exponential_backoff(attempt, base_delay=1, max_delay=60):
    """Calculate delay with jitter"""
    delay = min(base_delay * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter

# Usage
for attempt in range(5):
    try:
        response = api_call()
        break
    except RateLimitError:
        delay = exponential_backoff(attempt)
        time.sleep(delay)
```

### Circuit Breaker Pattern
Prevent cascading failures:

```python
class CircuitBreaker:
    def __init__(self, threshold=5, timeout=60):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure = None
        self.state = 'closed'  # closed, open, half-open
    
    def call(self, func, *args, **kwargs):
        if self.state == 'open':
            if time.time() - self.last_failure > self.timeout:
                self.state = 'half-open'
            else:
                raise Exception("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            if self.state == 'half-open':
                self.state = 'closed'
                self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = 'open'
            raise e
```

### Retry Decorator
```python
def retry(max_attempts=3, exceptions=(Exception,), backoff=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(backoff * (2 ** attempt))
            return None
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, exceptions=(RateLimitError, ServerError))
def spawn_agent(task):
    return api.spawn(task)
```

---

---

## 🔒 Security Best Practices

### API Key Management

#### Key Rotation Policy
```
Production Keys:
├── Rotate every 90 days
├── Keep 2 active keys during transition
├── Revoke old key 24h after confirming new key works
└── Never commit keys to version control
```

#### Environment-Based Keys
```python
# Development
J1MSKY_API_KEY=dev_sk_xxx

# Staging
J1MSKY_API_KEY=staging_sk_xxx

# Production
J1MSKY_API_KEY=live_sk_xxx
```

#### Key Storage
**DO:**
- Use environment variables
- Store in secrets manager (AWS Secrets Manager, HashiCorp Vault)
- Use encrypted `.env` files (gitignored)
- Rotate keys on team member departure

**DON'T:**
- Hardcode keys in source code
- Share keys via email/Slack
- Use same key for dev/prod
- Include keys in logs

### IP Whitelisting

Restrict API access to specific IP ranges:

```bash
# Configure via API
PUT /api/security/ip-whitelist
{
  "allowed_ips": [
    "192.168.1.0/24",      # Office network
    "10.0.0.0/8",          # VPN range
    "203.0.113.45/32"      # Specific server
  ],
  "enforce": true,
  "log_violations": true
}
```

**Response when blocked:**
```json
{
  "error": {
    "code": 403,
    "message": "IP not whitelisted",
    "your_ip": "198.51.100.23",
    "request_id": "req_abc123xyz"
  }
}
```

### Request Signing

For high-security environments, sign requests with HMAC:

```python
import hmac
import hashlib
import base64
from datetime import datetime

def sign_request(api_key, api_secret, method, path, body):
    timestamp = datetime.utcnow().isoformat()
    
    message = f"{timestamp}\n{method}\n{path}\n{body}"
    signature = hmac.new(
        api_secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'Authorization': f'Bearer {api_key}',
        'X-Timestamp': timestamp,
        'X-Signature': signature
    }

# Usage
headers = sign_request(
    api_key='your_key',
    api_secret='your_secret',
    method='POST',
    path='/api/spawn',
    body='{"model":"k2p5","task":"test"}'
)

response = requests.post(url, headers=headers, json=data)
```

### Audit Logging

Enable comprehensive audit logging:

```bash
# Enable audit log
POST /api/security/audit
{
  "enabled": true,
  "log_level": "verbose",
  "retention_days": 90,
  "include_request_body": false,
  "include_response_body": false,
  "events": [
    "agent.spawn",
    "agent.complete",
    "agent.fail",
    "api.key.used",
    "config.change",
    "security.violation"
  ]
}
```

**Audit Log Entry:**
```json
{
  "timestamp": "2026-02-19T14:30:00Z",
  "event": "agent.spawn",
  "severity": "info",
  "api_key_id": "key_abc123",
  "ip_address": "192.168.1.100",
  "user_agent": "j1msky-sdk/1.0.0",
  "request_id": "req_xyz789",
  "resource": {
    "type": "agent",
    "id": "subagent_1234567890_1234"
  },
  "details": {
    "model": "k2p5",
    "task_preview": "Generate report...",
    "estimated_cost": 0.05
  }
}
```

### Rate Limiting & Abuse Prevention

**Automatic Protections:**
- IP-based rate limiting (separate from API key limits)
- Anomaly detection (unusual traffic patterns)
- Cost spike protection (auto-block if >$100/hour)
- Concurrent agent limits per key

**Manual Controls:**
```bash
# Block suspicious IP
POST /api/security/block-ip
{
  "ip": "198.51.100.100",
  "reason": "suspicious_activity",
  "duration_hours": 24
}

# Revoke compromised key
DELETE /api/keys/{key_id}
{
  "reason": "suspected_leak",
  "notify_user": true
}
```

### Data Privacy

**Agent Task Data:**
- Encrypted at rest (AES-256)
- TLS 1.3 in transit
- Retained for 30 days (configurable)
- Can request immediate deletion

**PII Handling:**
```python
# Automatic PII detection
agent = agency.spawn(
    model='k2p5',
    task='Process customer data',
    privacy={
        'detect_pii': True,
        'mask_pii_in_logs': True,
        'encrypt_output': True,
        'retention_days': 7
    }
)
```

**Compliance:**
- GDPR: Right to deletion, data export
- CCPA: Data inventory, opt-out
- SOC 2 Type II: Available for Enterprise

### Security Checklist

**Pre-Production:**
- [ ] Keys stored in secrets manager
- [ ] IP whitelisting configured
- [ ] Rate limits tested
- [ ] Audit logging enabled
- [ ] Incident response plan documented
- [ ] Security contacts configured

**Monthly Review:**
- [ ] Review access logs for anomalies
- [ ] Check for unused API keys
- [ ] Verify key rotation schedule
- [ ] Review IP whitelist accuracy
- [ ] Test incident response

**Incident Response:**
1. **Suspected Key Leak:** Revoke immediately, rotate all keys
2. **Abnormal Usage:** Block IP, investigate logs
3. **Data Breach:** Notify within 72h, preserve evidence
4. **System Compromise:** Isolate, forensics, restore from backup

### Reporting Security Issues

**Responsible Disclosure:**
- Email: security@j1msky.ai
- GPG Key: [available on security page]
- Bounty: Up to $5,000 for critical vulnerabilities

**Include:**
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (optional)

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
