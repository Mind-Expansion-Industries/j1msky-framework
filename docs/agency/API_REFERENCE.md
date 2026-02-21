# J1MSKY API Reference
## For Developers and Integrators

---

## 🚀 QUICK START EXAMPLES

Copy-paste ready examples to get started in under 5 minutes.

### Prerequisites
```bash
# Set your API endpoint
export J1MSKY_API="http://localhost:8080/api"

# Set your API key (if authentication enabled)
export J1MSKY_KEY="your_api_key_here"
```

### Example 1: Spawn Your First Agent (cURL)
```bash
# Spawn a simple coding agent
curl -X POST "$J1MSKY_API/spawn" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $J1MSKY_KEY" \
  -d '{
    "model": "k2p5",
    "task": "Write a Python function to reverse a string",
    "priority": "normal"
  }' | jq '.'

# Expected response:
# {
#   "success": true,
#   "agent_id": "subagent_1234567890_1234",
#   "model": "k2p5",
#   "status": "spawning",
#   "estimated_cost": 0.05
# }
```

### Example 2: Check Agent Status
```bash
# Replace with your agent_id from spawn response
AGENT_ID="subagent_1234567890_1234"

curl "$J1MSKY_API/agent/$AGENT_ID" \
  -H "Authorization: Bearer $J1MSKY_KEY" | jq '.'
```

### Example 3: Generate a Pricing Quote
```bash
# Generate a quote for a medium complexity coding task
curl -X POST "$J1MSKY_API/pricing/quote" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "k2p5",
    "estimated_input": 2000,
    "estimated_output": 800,
    "complexity": "medium",
    "segment": "mid_market"
  }' | jq '.'

# Expected response shows internal cost, recommended price, and margin
```

### Example 4: Deploy a Full Team
```bash
# Deploy the coding team for a complex project
curl -X POST "$J1MSKY_API/spawn-team" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $J1MSKY_KEY" \
  -d '{
    "team": "team_coding",
    "task": "Build a REST API for user authentication with JWT tokens",
    "priority": "high"
  }' | jq '.'
```

### Example 5: Python SDK Quick Start
```python
import requests
import time

# Configuration
BASE_URL = "http://localhost:8080/api"
API_KEY = "your_api_key_here"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def spawn_and_wait(task: str, model: str = "k2p5", timeout: int = 300) -> dict:
    """Spawn an agent and wait for completion."""
    
    # Spawn the agent
    spawn_resp = requests.post(
        f"{BASE_URL}/spawn",
        headers=HEADERS,
        json={"model": model, "task": task, "priority": "normal"}
    )
    spawn_resp.raise_for_status()
    data = spawn_resp.json()
    
    if not data.get("success"):
        raise Exception(f"Spawn failed: {data.get('error')}")
    
    agent_id = data["agent_id"]
    print(f"Spawned agent: {agent_id}")
    
    # Poll for completion
    start_time = time.time()
    while time.time() - start_time < timeout:
        status_resp = requests.get(
            f"{BASE_URL}/agent/{agent_id}",
            headers=HEADERS
        )
        status = status_resp.json()
        
        if status.get("status") == "completed":
            print(f"✅ Task completed in {time.time() - start_time:.1f}s")
            return status
        elif status.get("status") == "failed":
            raise Exception(f"Agent failed: {status.get('error', 'Unknown error')}")
        
        time.sleep(2)
    
    raise TimeoutError(f"Agent didn't complete within {timeout}s")

# Usage
if __name__ == "__main__":
    result = spawn_and_wait("Write a fibonacci function in Python")
    print(f"Result: {result.get('result', 'No result')}")
    print(f"Cost: ${result.get('cost', 0)}")
```

### Example 6: JavaScript/Node.js Quick Start
```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8080/api';
const API_KEY = 'your_api_key_here';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_KEY}`,
    'Content-Type': 'application/json'
  }
});

async function spawnAndWait(task, model = 'k2p5', timeout = 300000) {
  // Spawn agent
  const { data: spawnData } = await api.post('/spawn', {
    model,
    task,
    priority: 'normal'
  });
  
  if (!spawnData.success) {
    throw new Error(`Spawn failed: ${spawnData.error}`);
  }
  
  const { agent_id } = spawnData;
  console.log(`Spawned agent: ${agent_id}`);
  
  // Poll for completion
  const startTime = Date.now();
  while (Date.now() - startTime < timeout) {
    const { data: status } = await api.get(`/agent/${agent_id}`);
    
    if (status.status === 'completed') {
      console.log(`✅ Task completed in ${(Date.now() - startTime) / 1000}s`);
      return status;
    } else if (status.status === 'failed') {
      throw new Error(`Agent failed: ${status.error || 'Unknown error'}`);
    }
    
    await new Promise(r => setTimeout(r, 2000));
  }
  
  throw new Error(`Timeout after ${timeout}ms`);
}

// Usage
spawnAndWait('Generate a SQL query to find duplicate emails')
  .then(result => {
    console.log('Result:', result.result);
    console.log('Cost: $', result.cost);
  })
  .catch(console.error);
```

### Example 7: Check System Health
```bash
# Quick health check
curl "$J1MSKY_API/health" | jq '.'

# Full orchestrator status
curl "$J1MSKY_API/orchestrator/status" | jq '
  {
    timestamp: .timestamp,
    budget_used: .today_spend,
    budget_remaining: .budget_remaining,
    alert_level: .budget_alert_level,
    models_active: .models_active
  }
'
```

### Example 8: Batch Generate Quotes
```bash
# Generate quotes for multiple segments at once
curl -X POST "$J1MSKY_API/pricing/batch-quotes" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "k2p5",
    "estimated_input": 3000,
    "estimated_output": 1200,
    "complexity": "high",
    "delivery_type": "task"
  }' | jq '.quotes_by_segment'

# Compare pricing across all segments
```

### Example 9: Webhook Setup
```bash
# Register a webhook to receive pricing events
curl -X POST "$J1MSKY_API/pricing/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-app.com/webhooks/j1msky",
    "events": ["pricing.quote_generated", "pricing.exception_created"],
    "secret": "your_webhook_secret"
  }' | jq '.'

# List registered webhooks
curl "$J1MSKY_API/pricing/webhooks" | jq '.'
```

### Example 10: Error Handling Pattern (Python)
```python
import requests
from requests.exceptions import RequestException, Timeout

def robust_api_call(method, endpoint, max_retries=3, **kwargs):
    """Make an API call with retry logic."""
    url = f"{BASE_URL}{endpoint}"
    
    for attempt in range(max_retries):
        try:
            response = requests.request(
                method, url,
                headers=HEADERS,
                timeout=30,
                **kwargs
            )
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue
            
            response.raise_for_status()
            data = response.json()
            
            # Check API-level errors
            if not data.get('success', True):
                raise Exception(f"API error: {data.get('error')}")
            
            return data
            
        except Timeout:
            wait = 2 ** attempt
            print(f"Timeout. Retrying in {wait}s...")
            time.sleep(wait)
        except RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"Request failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
    
    raise Exception("Max retries exceeded")

# Usage
try:
    result = robust_api_call('POST', '/spawn', 
                           json={'model': 'k2p5', 'task': 'Hello world'})
    print(f"Success: {result}")
except Exception as e:
    print(f"Failed: {e}")
```

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

### API Key Scopes

Keys can be scoped to reduce blast radius:

- `agents:read` – list/status endpoints
- `agents:write` – spawn/cancel endpoints
- `billing:read` – usage and cost endpoints
- `admin:write` – configuration and security endpoints

---

## 🌐 Base URL

```
http://your-pi-ip:8080/api
```

---

## 📚 Endpoints

### Idempotency for Write Operations

For `POST`/`PUT` endpoints, send an idempotency key to safely retry without duplicate side effects.

**Header:**
```http
Idempotency-Key: 7f8f8c5a-4d6f-4f6c-ae4b-52a7c8aa2d9b
```

**Behavior:**
- Same key + same payload within 24h returns the original response
- Same key + different payload returns `409 Conflict`
- Keys expire after 24 hours

**Conflict Example:**
```json
{
  "success": false,
  "error": "Idempotency key payload mismatch"
}
```

### Operational Status Endpoints

#### Config Persistence Notes

- Provider rate-limit counters are persisted to config storage.
- Daily budget context is preserved across process restarts.
- After restart, status endpoints reflect last persisted counters plus new runtime usage.

#### Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "error_rate": 0.01,
  "models_configured": 4
}
```

#### Orchestrator Status
**Endpoint:** `GET /orchestrator/status`

Returns live budget/rate-limit state sourced from orchestrator config and usage tracking.
Use `budget_utilization_pct` for alerting thresholds (for example: warn at 70%, critical at 90%).
`budget_alert_level` is a normalized state machine: `ok` → `notice` → `warning` → `critical`.
`operational_flags.requires_ops_attention=true` should page the operations owner or trigger escalation workflow.
`operational_flags.recommended_action` provides an immediate operator play for runbook automation.
`model_mix_recommendation` can be used by schedulers to bias routing toward cost-optimized or balanced modes.
`pricing_policy` surfaces current markup guardrails used by quoting workflows.
`example_task_quote` gives a ready-to-display sample quote with segment-adjusted pricing (internal cost, base markup, segment adjustment, final markup, recommended price, margin).
`quote_decision_preview` provides an auditable decision packet (approved/escalated + next step) for CRM syncing.
`quote_portfolio_preview` gives a multi-scenario compliance rollup for proposal-level pricing checks.
Use `quote_portfolio_preview.requires_executive_review=true` to trigger leadership review workflow before proposals are sent.
`exception_aging_preview` classifies open exception risk and returns a concrete next action for revops.
`exception_alert_preview` provides a ready-to-send alert payload (level, summary, recommended action).
`portfolio_alert_preview` provides a ready-to-send alert for portfolio-level compliance signals.
`weekly_metrics_preview` aggregates weekly pricing decisions for retrospective analysis (approval rate, avg margin, exception counts).
`weekly_comparison_preview` flags significant week-over-week shifts in pricing metrics for calibration reviews.
`usage_anomalies` is intended for alerting pipelines and overnight ops watchlists.
Use `usage_anomalies.severity` to route alerts (`warning` to ops queue, `critical` to on-call).

**Response:**
```json
{
  "timestamp": "2026-02-19T13:11:00-05:00",
  "models_active": 4,
  "usage_summary": {
    "top_models": [
      {"model": "k2p5", "calls": 68, "tokens": 112000, "avg_tokens_per_call": 1647.06, "estimated_spend": 0.112},
      {"model": "sonnet", "calls": 39, "tokens": 94000, "avg_tokens_per_call": 2410.26, "estimated_spend": 0.282}
    ],
    "total_calls": 128
  },
  "recent_usage": 128,
  "daily_budget": 50,
  "today_spend": 12.43,
  "budget_remaining": 37.57,
  "budget_utilization_pct": 24.86,
  "budget_alert_level": "ok",
  "operational_flags": {
    "budget_alert_level": "ok",
    "max_provider_utilization_pct": 28.0,
    "hot_providers": [],
    "requires_ops_attention": false,
    "recommended_action": "No action required"
  },
  "model_mix_recommendation": {
    "strategy": "balanced",
    "primary": ["k2p5", "sonnet"],
    "secondary": ["codex"],
    "restricted": [],
    "reason": "Normal operating range"
  },
  "pricing_policy": {
    "min_markup": 3.0,
    "target_markup": 4.0,
    "max_markup": 5.0,
    "complexity_markup": {"low": 3.0, "medium": 4.0, "high": 5.0},
    "minimum_price": 0.5
  },
  "example_task_quote": {
    "model": "k2p5",
    "complexity": "medium",
    "segment": "mid_market",
    "estimated_tokens": 2000,
    "internal_cost": 0.002,
    "base_markup": 4.0,
    "segment_adjustment": 0.0,
    "final_markup": 4.0,
    "recommended_price": 0.5,
    "gross_margin_pct": 99.6,
    "margin_band": "strong"
  },
  "quote_decision_preview": {
    "decision_status": "approved",
    "approver": "ops-auto",
    "delivery_type": "task",
    "next_step": "send_quote",
    "generated_at": "2026-02-20T06:20:00-05:00"
  },
  "quote_portfolio_preview": {
    "delivery_type": "task",
    "scenario_count": 3,
    "compliant_count": 3,
    "compliance_ratio": 1.0,
    "needs_escalation": false,
    "requires_executive_review": false,
    "average_margin_pct": 88.13
  },
  "portfolio_alert_preview": {
    "level": "ok",
    "summary": "Portfolio healthy: 3/3 compliant, margin 88.13%",
    "recommended_action": "send_proposal"
  },
  "weekly_metrics_preview": {
    "total_quotes": 2,
    "approved_count": 1,
    "escalated_count": 1,
    "approval_rate": 0.5,
    "avg_margin_pct": 70.8,
    "exceptions_created": 1,
    "exceptions_closed": 0
  },
  "weekly_comparison_preview": {
    "week_over_week_changes": {
      "total_quotes_change": 11.11,
      "approval_rate_change": -4.55,
      "avg_margin_change": 6.62,
      "exceptions_created_change": 50.0
    },
    "significant_shifts": ["Exception creation up 50.0%"],
    "requires_review": true
  },
  "exception_aging_preview": {
    "open_exceptions": 4,
    "oldest_days": 33,
    "at_risk_count": 2,
    "requires_exec_followup": true,
    "risk_level": "critical",
    "next_action": "schedule_executive_review"
  },
  "exception_alert_preview": {
    "level": "critical",
    "summary": "Critical exception risk: 4 open, oldest 33d",
    "recommended_action": "schedule_executive_review"
  },
  "usage_anomalies": {
    "has_anomalies": false,
    "anomalies": [],
    "count": 0,
    "severity": "none"
  },
  "monthly_forecast": {
    "projected_spend": 372.9,
    "budget_ceiling": 1500,
    "delta_to_budget": 1127.1
  },
  "provider_usage": {
    "anthropic": {
      "current": 14,
      "hourly": 50,
      "remaining": 36,
      "utilization_pct": 28.0
    },
    "kimi-coding": {
      "current": 22,
      "hourly": 100,
      "remaining": 78,
      "utilization_pct": 22.0
    }
  }
}
```

#### Budget-Aware Model Recommendation
**Endpoint:** `POST /orchestrator/recommend-model`

**Request:**
```json
{
  "task_type": "coding",
  "complexity": "medium",
  "priority": "normal",
  "estimated_tokens": 2500
}
```

**Response:**
```json
{
  "recommended_model": "k2p5",
  "budget_available": true,
  "daily_budget": 50,
  "today_spend": 12.43,
  "budget_remaining": 37.57
}
```

Use this endpoint when you need a model choice that respects daily spend limits.
Forecast fields in `/orchestrator/status` help finance and ops estimate month-end burn.
`usage_summary` is intended for quick dashboard rollups and model-mix reviews.
Per-model fields `avg_tokens_per_call` and `estimated_spend` support cost-efficiency tuning.

### Response Headers (Observability)

Important headers returned on operational endpoints:

- `X-Request-Id` – unique request trace identifier
- `X-RateLimit-Limit` – provider/request limit ceiling
- `X-RateLimit-Remaining` – requests left in current window
- `X-RateLimit-Reset` – unix timestamp for next reset

Use `X-Request-Id` when escalating incidents to support.

### Pagination & Filtering

Most list endpoints support pagination and filtering using query parameters:

**Query Parameters:**
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `limit` | integer | Max results per page (default: 20, max: 100) | `?limit=50` |
| `offset` | integer | Skip N results for pagination | `?offset=100` |
| `cursor` | string | Opaque cursor for cursor-based pagination | `?cursor=abc123` |
| `sort` | string | Sort field and direction (prefix - for desc) | `?sort=-created_at` |
| `filter` | object | JSON-encoded filter criteria | See below |

**Filter Syntax:**
```
GET /agents?filter={"status":"running","model":"k2p5"}
GET /agents?filter={"created_after":"2026-02-01","cost_gt":0.50}
```

**Available Operators:**
- `eq` - Equal (default)
- `ne` - Not equal
- `gt`, `gte` - Greater than, greater than or equal
- `lt`, `lte` - Less than, less than or equal  
- `in` - In array
- `contains` - String contains
- `starts_with`, `ends_with` - String prefix/suffix

**Pagination Response:**
```json
{
  "data": [...],
  "pagination": {
    "total": 250,
    "limit": 20,
    "offset": 40,
    "has_more": true,
    "next_offset": 60,
    "previous_offset": 20
  },
  "links": {
    "self": "/agents?limit=20&offset=40",
    "next": "/agents?limit=20&offset=60",
    "prev": "/agents?limit=20&offset=20",
    "first": "/agents?limit=20&offset=0",
    "last": "/agents?limit=20&offset=240"
  }
}
```

**Cursor-Based Pagination (for real-time data):**
```bash
# First request
GET /events?limit=50

# Response includes cursor
{
  "data": [...],
  "pagination": {
    "cursor": "eyJpZCI6MTIzNDV9",
    "has_more": true
  }
}

# Subsequent request
GET /events?limit=50&cursor=eyJpZCI6MTIzNDV9
```

---

### Pricing Operations Endpoints

#### Get Pricing Status Snapshot
**Endpoint:** `GET /pricing/status`

Returns active pricing policy with segment adjustments, sample quotes for each segment, and margin guardrail results.

**Response:**
```json
{
  "success": true,
  "pricing_policy": {
    "complexity_markup": {"low": 3.0, "medium": 4.0, "high": 5.0},
    "segment_adjustments": {"enterprise": 0.5, "mid_market": 0.0, "smb": -0.5, "startup": -1.0},
    "minimum_price": 0.5,
    "margin_thresholds": {"task": 55.0, "subscription": 50.0, "enterprise": 45.0}
  },
  "example_quotes": {
    "mid_market": {
      "model": "k2p5",
      "complexity": "medium",
      "segment": "mid_market",
      "base_markup": 4.0,
      "segment_adjustment": 0.0,
      "final_markup": 4.0,
      "recommended_price": 0.5,
      "gross_margin_pct": 99.7,
      "margin_band": "strong"
    },
    "enterprise": {
      "model": "sonnet",
      "complexity": "high",
      "segment": "enterprise",
      "base_markup": 5.0,
      "segment_adjustment": 0.5,
      "final_markup": 5.5,
      "recommended_price": 0.85,
      "gross_margin_pct": 96.8,
      "margin_band": "strong"
    },
    "smb": {
      "model": "k2p5",
      "complexity": "low",
      "segment": "smb",
      "base_markup": 3.0,
      "segment_adjustment": -0.5,
      "final_markup": 2.5,
      "recommended_price": 0.5,
      "gross_margin_pct": 99.4,
      "margin_band": "strong"
    }
  },
  "guardrail_check": {
    "delivery_type": "task",
    "minimum_margin_pct": 55.0,
    "actual_margin_pct": 99.7,
    "is_compliant": true,
    "action": "approve_quote"
  }
}
```

#### Get Pricing Health Check
**Endpoint:** `GET /pricing/health`

Returns operational health status of the pricing system including daily costs, budget utilization, and model efficiency metrics.

**Response:**
```json
{
  "success": true,
  "health": {
    "status": "healthy",
    "daily_cost": 12.45,
    "daily_budget": 50.0,
    "budget_utilization_pct": 24.9,
    "tasks_completed": 156,
    "avg_cost_per_task": 0.0798,
    "issues": [],
    "by_model": {
      "k2p5": {
        "cost": 8.23,
        "calls": 89,
        "avg_per_call": 0.0925
      },
      "sonnet": {
        "cost": 4.22,
        "calls": 67,
        "avg_per_call": 0.0630
      }
    }
  }
}
```

**Health Status Values:**
- `healthy` → All metrics within normal ranges
- `warning` → Daily cost >80% of budget OR cost per task elevated
- `critical` → Daily cost >=100% of budget

---

#### Get Pricing Report
**Endpoint:** `GET /pricing/report`

Generates a comprehensive daily pricing report including health metrics, model breakdowns, sample quotes by segment, and current pricing policy.

**Response:**
```json
{
  "success": true,
  "report": {
    "generated_at": "2026-02-21T01:45:00-05:00",
    "period": "daily",
    "health": {
      "status": "healthy",
      "daily_cost": 12.45,
      "daily_budget": 50.0,
      "budget_utilization_pct": 24.9,
      "tasks_completed": 156,
      "avg_cost_per_task": 0.0798,
      "issues": []
    },
    "by_model": {
      "k2p5": {
        "cost": 8.23,
        "calls": 89,
        "avg_per_call": 0.0925
      },
      "sonnet": {
        "cost": 4.22,
        "calls": 67,
        "avg_per_call": 0.0630
      }
    },
    "sample_quotes_by_segment": {
      "enterprise": {
        "model": "k2p5",
        "complexity": "medium",
        "segment": "enterprise",
        "final_markup": 4.5,
        "recommended_price": 0.65,
        "gross_margin_pct": 98.5
      },
      "mid_market": {
        "model": "k2p5",
        "segment": "mid_market",
        "final_markup": 4.0,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.6
      },
      "smb": {
        "model": "k2p5",
        "segment": "smb",
        "final_markup": 3.5,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.4
      },
      "startup": {
        "model": "k2p5",
        "segment": "startup",
        "final_markup": 3.0,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.2
      }
    },
    "pricing_policy": {
      "complexity_markup": {"low": 3.0, "medium": 4.0, "high": 5.0},
      "segment_adjustments": {"enterprise": 0.5, "mid_market": 0.0, "smb": -0.5, "startup": -1.0},
      "minimum_price": 0.50,
      "margin_thresholds": {"task": 55.0, "subscription": 50.0, "enterprise": 45.0}
    }
  }
}
```

**Use Cases:**
- Daily standup review of pricing health
- Audit documentation
- Stakeholder reporting
- Policy verification

---

#### Register Pricing Webhook
**Endpoint:** `POST /pricing/webhook`

Register a webhook URL to receive real-time notifications for pricing events.

**Request (JSON body):**
- `url`: Webhook endpoint URL (HTTPS required)
- `events`: Array of event types to subscribe to
- `secret`: Optional secret for HMAC signature verification

**Supported Events:**
- `pricing.quote_generated` - New quote created
- `pricing.quote_approved` - Quote approved
- `pricing.quote_escalated` - Quote escalated
- `pricing.exception_created` - Exception approved
- `pricing.margin_alert` - Margin below threshold
- `pricing.budget_warning` - Budget >80%
- `pricing.budget_critical` - Budget >95%
- `pricing.policy_changed` - Policy updated

**Request Example:**
```bash
curl -X POST http://localhost:8080/api/pricing/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-system.com/webhooks/pricing",
    "events": ["pricing.quote_generated", "pricing.exception_created"],
    "secret": "your_webhook_secret"
  }'
```

**Response:**
```json
{
  "success": true,
  "webhook_id": "pricing_webhook_1708473600",
  "url": "https://your-system.com/webhooks/pricing",
  "events": ["pricing.quote_generated", "pricing.exception_created"],
  "message": "Pricing webhook registered"
}
```

**Webhook Payload Format:**
```json
{
  "event": "pricing.quote_generated",
  "timestamp": "2026-02-21T02:45:00Z",
  "webhook_id": "pricing_webhook_1708473600",
  "data": {
    "quote_id": "quote_12345",
    "model": "k2p5",
    "segment": "enterprise",
    "recommended_price": 0.75,
    "gross_margin_pct": 98.5
  }
}
```

---

#### List Pricing Webhooks
**Endpoint:** `GET /pricing/webhooks`

List all registered pricing webhooks.

**Response:**
```json
{
  "success": true,
  "webhooks": [
    {
      "webhook_id": "pricing_webhook_1708473600",
      "url": "https://your-system.com/webhooks/pricing",
      "events": ["pricing.quote_generated", "pricing.exception_created"],
      "created_at": "2026-02-21T02:30:00Z"
    }
  ],
  "count": 1
}
```

---

#### Delete Pricing Webhook
**Endpoint:** `DELETE /pricing/webhook/{webhook_id}`

Delete a registered pricing webhook.

**Example:**
```bash
curl -X DELETE http://localhost:8080/api/pricing/webhook/pricing_webhook_1708473600
```

**Response:**
```json
{
  "success": true,
  "message": "Pricing webhook pricing_webhook_1708473600 removed"
}
```

---

#### Generate Pricing Quote
**Endpoint:** `POST /pricing/quote`

**Request (form fields):**
- `model`: `k2p5|sonnet|opus|minimax-m2.5`
- `estimated_input`: integer token estimate
- `estimated_output`: integer token estimate
- `complexity`: `low|medium|high`
- `delivery_type`: `task|subscription|enterprise`
- `segment`: `enterprise|mid_market|smb|startup` (optional, default: `mid_market`)

**Response:**
```json
{
  "success": true,
  "quote": {
    "model": "sonnet",
    "complexity": "high",
    "segment": "enterprise",
    "estimated_input_tokens": 3000,
    "estimated_output_tokens": 1200,
    "internal_cost": 0.027,
    "base_markup": 5.0,
    "segment_adjustment": 0.5,
    "final_markup": 5.5,
    "recommended_price": 0.5,
    "gross_margin_pct": 94.6,
    "margin_band": "strong"
  },
  "guardrail_check": {
    "delivery_type": "task",
    "minimum_margin_pct": 55.0,
    "actual_margin_pct": 94.6,
    "is_compliant": true,
    "action": "approve_quote"
  }
}
```

#### Generate Batch Segment Quotes
**Endpoint:** `POST /pricing/batch-quotes`

Generates quotes for all customer segments simultaneously to compare pricing across enterprise, mid-market, SMB, and startup segments.

**Request (form fields):**
- `model`: `k2p5|sonnet|opus|minimax-m2.5`
- `estimated_input`: integer token estimate
- `estimated_output`: integer token estimate
- `complexity`: `low|medium|high`
- `delivery_type`: `task|subscription|enterprise`

**Response:**
```json
{
  "success": true,
  "input_params": {
    "model": "k2p5",
    "complexity": "medium",
    "estimated_input": 2000,
    "estimated_output": 800,
    "delivery_type": "task"
  },
  "quotes_by_segment": {
    "enterprise": {
      "quote": {
        "model": "k2p5",
        "complexity": "medium",
        "segment": "enterprise",
        "final_markup": 4.5,
        "recommended_price": 0.75,
        "gross_margin_pct": 98.5
      },
      "guardrail_check": {
        "is_compliant": true,
        "action": "approve_quote"
      }
    },
    "mid_market": {
      "quote": {
        "model": "k2p5",
        "segment": "mid_market",
        "final_markup": 4.0,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.6
      },
      "guardrail_check": {
        "is_compliant": true,
        "action": "approve_quote"
      }
    },
    "smb": {
      "quote": {
        "model": "k2p5",
        "segment": "smb",
        "final_markup": 3.5,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.4
      },
      "guardrail_check": {
        "is_compliant": true,
        "action": "approve_quote"
      }
    },
    "startup": {
      "quote": {
        "model": "k2p5",
        "segment": "startup",
        "final_markup": 3.0,
        "recommended_price": 0.50,
        "gross_margin_pct": 99.2
      },
      "guardrail_check": {
        "is_compliant": true,
        "action": "approve_quote"
      }
    }
  },
  "comparison": {
    "best_value_segment": "startup",
    "best_value_price": 0.50,
    "highest_margin_segment": "mid_market",
    "highest_margin_pct": 99.6
  }
}
```

**Use Cases:**
- Compare pricing across segments before targeting a new market
- Identify optimal segment positioning for a new service
- Sales training on segment-based pricing differences

---

#### Generate Quote Decision Record
**Endpoint:** `POST /pricing/decision`

Creates an auditable approve/escalate decision packet for one quote candidate.

**Request (form fields):**
- `model`: `k2p5|sonnet|opus|minimax-m2.5`
- `estimated_input`: integer token estimate
- `estimated_output`: integer token estimate
- `complexity`: `low|medium|high`
- `delivery_type`: `task|subscription|enterprise`
- `approver`: decision owner label (default: `ops-auto`)
- `segment`: `enterprise|mid_market|smb|startup` (optional, default: `mid_market`)

**Response:**
```json
{
  "success": true,
  "decision": {
    "decision_status": "approved",
    "approver": "ops-auto",
    "delivery_type": "task",
    "next_step": "send_quote",
    "generated_at": "2026-02-20T08:35:00-05:00"
  },
  "quote": {
    "model": "k2p5",
    "complexity": "medium",
    "segment": "mid_market",
    "base_markup": 4.0,
    "segment_adjustment": 0.0,
    "final_markup": 4.0,
    "recommended_price": 0.5,
    "gross_margin_pct": 99.6,
    "margin_band": "strong"
  },
  "guardrail_check": {
    "is_compliant": true,
    "action": "approve_quote"
  }
}
```

#### Generate Portfolio Alert Payload
**Endpoint:** `POST /pricing/portfolio-alert`

Builds portfolio compliance rollup and an alert-ready message for proposal-level signals.

**Request (form fields):**
- `scenario_count`: integer
- `compliant_count`: integer
- `average_margin_pct`: float

**Response:**
```json
{
  "success": true,
  "portfolio_summary": {
    "scenario_count": 3,
    "compliant_count": 3,
    "compliance_ratio": 1.0,
    "requires_executive_review": false,
    "average_margin_pct": 88.13
  },
  "portfolio_alert": {
    "level": "ok",
    "summary": "Portfolio healthy: 3/3 compliant, margin 88.13%",
    "recommended_action": "send_proposal"
  }
}
```

#### Aggregate Weekly Pricing Metrics
**Endpoint:** `POST /pricing/weekly-metrics`

Aggregates weekly pricing decisions for retrospective analysis and policy tuning.

**Request (form fields):**
- `quotes`: JSON array of quote decision objects

**Quote object fields:**
- `decision_status`: `approved|escalated`
- `gross_margin_pct`: float
- `exception_created`: boolean (optional)
- `exception_closed`: boolean (optional)

**Response:**
```json
{
  "success": true,
  "weekly_metrics": {
    "total_quotes": 45,
    "approved_count": 38,
    "escalated_count": 7,
    "approval_rate": 0.84,
    "avg_margin_pct": 72.5,
    "exceptions_created": 3,
    "exceptions_closed": 2
  }
}
```

#### Compare Weekly Pricing Metrics
**Endpoint:** `POST /pricing/weekly-comparison`

Compares two weeks of pricing metrics and flags significant shifts for calibration reviews.

**Request (form fields):**
- `current_total_quotes`: integer
- `current_approval_rate`: float (0.0-1.0)
- `current_avg_margin_pct`: float
- `current_exceptions_created`: integer
- `prev_total_quotes`: integer
- `prev_approval_rate`: float (0.0-1.0)
- `prev_avg_margin_pct`: float
- `prev_exceptions_created`: integer

**Response:**
```json
{
  "success": true,
  "week_over_week_changes": {
    "total_quotes_change": 11.11,
    "approval_rate_change": -4.55,
    "avg_margin_change": 6.62,
    "exceptions_created_change": 50.0
  },
  "significant_shifts": ["Exception creation up 50.0%"],
  "requires_review": true
}
```

#### Summarize Experiment Results
**Endpoint:** `POST /pricing/experiment-summary`

Analyzes experiment data and provides rollout recommendation based on control vs test performance.

**Request (form fields):**
- `quotes`: JSON array of tracked experiment quotes

**Quote object fields:**
- `variant`: `control|test`
- `decision_status`: `approved|escalated`
- `gross_margin_pct`: float

**Response:**
```json
{
  "success": true,
  "status": "complete",
  "control": {
    "count": 45,
    "approval_rate": 0.84,
    "avg_margin_pct": 72.5
  },
  "test": {
    "count": 12,
    "approval_rate": 0.75,
    "avg_margin_pct": 78.0
  },
  "recommendation": "roll_out"
}
```

**Recommendation Values:**
- `roll_out` → Test beats control on margin without significant approval rate drop
- `discard` → Test underperforms control on key metrics
- `inconclusive` → Insufficient data or mixed results

#### Generate Exception Alert Payload
**Endpoint:** `POST /pricing/exception-alert`

Builds exception-aging risk classification and an alert-ready message payload.

**Request (form fields):**
- `open_exceptions`: integer
- `oldest_days`: integer
- `at_risk_count`: integer (exceptions aged 14+ days)

**Response:**
```json
{
  "success": true,
  "exception_aging": {
    "open_exceptions": 4,
    "oldest_days": 33,
    "at_risk_count": 2,
    "requires_exec_followup": true,
    "risk_level": "critical",
    "next_action": "schedule_executive_review"
  },
  "exception_alert": {
    "level": "critical",
    "summary": "Critical exception risk: 4 open, oldest 33d",
    "recommended_action": "schedule_executive_review"
  }
}
```

#### Evaluate Pricing Scenarios
**Endpoint:** `POST /pricing/scenario`

Batch-evaluates multiple pricing options and returns compliance rollup.
Use `requires_executive_review=true` as a hard stop before proposal send.

**Request (form fields):**
- `delivery_type`: `task|subscription|enterprise`
- `scenarios`: JSON array of scenario objects

**Scenario object fields:**
- `model`: `k2p5|sonnet|opus|minimax-m2.5`
- `estimated_input`: integer
- `estimated_output`: integer
- `complexity`: `low|medium|high`
- `segment`: `enterprise|mid_market|smb|startup` (optional, default: `mid_market`)

**Response:**
```json
{
  "success": true,
  "delivery_type": "task",
  "scenario_count": 3,
  "compliant_count": 2,
  "compliance_ratio": 0.67,
  "needs_escalation": true,
  "requires_executive_review": false,
  "average_margin_pct": 63.42,
  "results": [
    {
      "quote": {"model": "k2p5", "gross_margin_pct": 99.6, "margin_band": "strong"},
      "guardrail_check": {"is_compliant": true, "action": "approve_quote"}
    },
    {
      "quote": {"model": "opus", "gross_margin_pct": 41.2, "margin_band": "at_risk"},
      "guardrail_check": {"is_compliant": false, "action": "escalate_deal_desk"}
    }
  ]
}
```

---

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

### 3. List Agents
List all agents with filtering and pagination.

**Endpoint:** `GET /agents`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status: `spawning`, `running`, `completed`, `failed` |
| `model` | string | Filter by model: `k2p5`, `sonnet`, `opus` |
| `team` | string | Filter by team ID |
| `created_after` | string | ISO date, agents created after |
| `cost_gt` | number | Filter by cost greater than |
| `sort` | string | Sort field: `created_at`, `cost`, `status` |
| `limit` | integer | Results per page (1-100) |
| `offset` | integer | Pagination offset |

**Example:**
```bash
# Get running agents using k2p5, sorted by creation date
GET /agents?status=running&model=k2p5&sort=-created_at&limit=20

# Get high-cost agents from this month
GET /agents?cost_gt=1.00&created_after=2026-02-01&limit=50
```

**Response:**
```json
{
  "data": [
    {
      "agent_id": "subagent_1234567890_1234",
      "model": "k2p5",
      "status": "running",
      "task": "Write blog post...",
      "team": "team_creative",
      "created_at": "2026-02-19T10:00:00Z",
      "started_at": "2026-02-19T10:00:05Z",
      "estimated_cost": 0.05,
      "actual_cost": 0.03
    }
  ],
  "pagination": {
    "total": 156,
    "limit": 20,
    "offset": 0,
    "has_more": true
  },
  "meta": {
    "total_cost": 45.67,
    "by_model": {
      "k2p5": 23,
      "sonnet": 15,
      "opus": 8
    }
  }
}
```

---

### 4. Get Agent Status
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

### 5. List Active Agents
Get all currently running agents.

**Endpoint:** `GET /agents/active`

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

### Request Validation Rules

All write endpoints enforce basic validation:

| Field | Rule |
|------|------|
| `task` | Required, non-empty string, max 2000 chars |
| `model` | Must be one of: `k2p5`, `sonnet`, `opus` |
| `team` | Must match a registered team id |
| `priority` | `low`, `normal`, or `high` |

**Validation Error Example:**
```json
{
  "success": false,
  "error": "Task cannot be empty"
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

## 🛠️ Troubleshooting Guide

### Quick Diagnostics Checklist

When something isn't working, run through this checklist first:

```bash
# 1. Check if service is running
curl http://localhost:8080/api/health

# 2. Check orchestrator status
curl http://localhost:8080/api/orchestrator/status | jq '.budget_alert_level, .operational_flags.requires_ops_attention'

# 3. Check rate limits
curl http://localhost:8080/api/rate-limits

# 4. View recent errors
tail -n 50 /tmp/teams-v4.log | grep ERROR
```

---

### Common Issues & Solutions

#### 1. Connection Refused / Can't Connect to API

**Symptoms:**
```bash
curl: (7) Failed to connect to localhost port 8080: Connection refused
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Service not running | `sudo systemctl start j1msky` |
| Port conflict | Find and kill process: `sudo kill -9 <PID>` |
| Firewall blocking | `sudo ufw allow 8080/tcp` |
| Wrong URL | Verify IP: `hostname -I` |

---

#### 2. Rate Limit Exceeded (429 Errors)

**Symptoms:**
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "retry_after": 3600
  }
}
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Hourly limit hit | Wait for reset |
| Bursty traffic | Implement request queuing |
| Wrong model choice | Switch to `"model": "k2p5"` |

**Code Fix (Exponential Backoff):**
```python
import time
import random

def api_call_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

---

#### 3. Agent Spawning Fails

**Diagnosis:**
```bash
# Check model availability
curl http://localhost:8080/api/orchestrator/status | jq '.provider_usage'

# Check budget
curl http://localhost:8080/api/orchestrator/status | jq '.today_spend, .daily_budget'
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Model rate limited | Switch model or wait |
| Budget exceeded | Check `.budget_alert_level` |
| Disk full | Clean logs: `rm /tmp/teams-v4.log.*` |
| API key invalid | Verify `config/api-keys.json` |

---

#### 4. High API Costs / Budget Alerts

**Immediate Actions:**

| Urgency | Action |
|---------|--------|
| Critical (>90%) | Pause non-urgent tasks |
| Warning (>70%) | Switch to cheaper models |
| Notice (>50%) | Review expensive task patterns |

**Use budget-aware selection:**
```python
import requests

rec = requests.post(
    "http://localhost:8080/api/orchestrator/recommend-model",
    json={"task_type": "coding", "complexity": "medium", "estimated_tokens": 2000}
).json()

if rec['budget_available']:
    model = rec['recommended_model']
```

---

#### 5. Agent Returns Poor Results

| Problem | Fix |
|---------|-----|
| Incomplete output | Break into smaller tasks |
| Wrong format | Add format example |
| Off-topic | Add constraints: "Only focus on X" |
| Code errors | Use `"model": "k2p5"` for coding |

---

#### 6. Webhooks Not Firing

| Cause | Solution |
|-------|----------|
| URL unreachable | Verify endpoint is publicly accessible |
| SSL certificate error | Use valid SSL cert |
| Wrong event filter | Check registered events |

---

### Error Code Quick Reference

| HTTP | Meaning | Action |
|------|---------|--------|
| 200 | Success | Continue |
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Check API key |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Check logs |
| 503 | Service Unavailable | Retry shortly |

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

## 📋 API Versioning

### Version Strategy

J1MSKY uses **URL-based versioning** for API changes:

```
http://your-pi-ip:8080/api/v1/spawn    # Current stable
http://your-pi-ip:8080/api/v2/spawn    # Future version
```

**Version Lifecycle:**
| Phase | Duration | Support Level |
|-------|----------|---------------|
| Beta | 1-2 months | Community only |
| Stable | 12+ months | Full support |
| Deprecated | 6 months | Security fixes only |
| Sunset | - | Removed |

**Current Versions:**
- `v4.0` (Stable) - Current production version
- `v3.2` (Deprecated) - End of life: June 2026

### Deprecation Headers

When using deprecated endpoints, you'll receive headers:

```http
Deprecation: true
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
Link: </api/v4/spawn>; rel="successor-version"
```

### Migration Guide

**Upgrading from v3 to v4:**

| v3 Endpoint | v4 Equivalent | Changes |
|-------------|---------------|---------|
| `POST /agent` | `POST /spawn` | Renamed for clarity |
| `GET /status` | `GET /agent/{id}` | Returns full status object |
| `DELETE /cancel` | `DELETE /agent/{id}` | Consistent naming |

**Breaking Changes in v4:**
1. **Authentication:** Header changed from `X-API-Key` to `Authorization: Bearer`
2. **Rate Limiting:** New rate limit headers added
3. **Error Format:** Standardized error response structure
4. **Pagination:** Cursor-based pagination for list endpoints

---

## 📝 Changelog & Version History

### Version Overview

| Version | Status | Release Date | End of Life |
|---------|--------|--------------|-------------|
| v4.1 | Current | Feb 2026 | TBD |
| v4.0 | Stable | Feb 2026 | Feb 2027 |
| v3.2 | Deprecated | Dec 2025 | Jun 2026 |
| v3.0 | Sunset | Sep 2025 | Jan 2026 |

---

### v4.1.0 (2026-02-21)
**Feature Release - Caching & Resilience**

**Added:**
- TTL caching layer for model recommendations and pricing calculations
- Circuit breaker pattern for external API calls
- Bulk quote generation endpoint (`POST /pricing/batch-quotes`)
- Cache management endpoints (`GET /cache/status`, `POST /cache/invalidate`)
- Enhanced input validation for all pricing endpoints
- Circuit breaker metrics in health check response

**Changed:**
- Model selection now uses cached results (30s TTL) for better performance
- Pricing calculations cached (5min TTL) to reduce redundant computation
- Improved error messages with actionable remediation steps
- Rate limit headers now include `X-RateLimit-Reset-At`

**Deprecated:**
- `POST /pricing/quote` without segment parameter (will default to `mid_market`)

---

### v4.0.0 (2026-02-19)
**Major Release - Multi-Model Agent Teams**

**Added:**
- Multi-model agent team support (Code, Creative, Research, Business)
- Rate limit tracking and management
- Subagent spawning with automatic model selection
- Webhook notifications for agent events
- Cost tracking and billing reports
- Pagination and filtering on list endpoints
- Security features: IP whitelisting, request signing, audit logging
- Pricing operations endpoints (`/pricing/*`)
- Exception aging and portfolio compliance tracking
- Weekly metrics aggregation and comparison
- Experiment tracking for pricing optimization

**Changed:**
- API authentication now uses Bearer tokens
- Rate limit response includes `retry_after` header
- Standardized error response format across all endpoints
- Response headers include `X-Request-Id` for tracing

**Removed:**
- Legacy v2 endpoints (sunset as of 2026-01-01)

---

### v3.2.0 (2025-12-15)
**Maintenance Release**

**Added:**
- Health check endpoint (`GET /health`)
- System metrics endpoint (`GET /metrics`)
- Idempotency key support for write operations

**Fixed:**
- Rate limit counter not resetting correctly
- Memory leak in long-running agents
- Race condition in concurrent agent spawning

**Security:**
- Patched dependency vulnerabilities
- Enhanced input sanitization

---

### v3.1.0 (2025-11-01)
**Feature Release**

**Added:**
- Batch agent spawning (`POST /spawn-batch`)
- Agent priority levels (low, normal, high)
- Custom timeout configuration per agent
- Task queuing system for rate limit management

**Changed:**
- Improved error messages for invalid models
- Reduced default agent timeout from 10min to 5min
- Enhanced logging with structured JSON format

---

### v3.0.0 (2025-09-15)
**Major Release - Business Tier**

**Added:**
- Enterprise authentication with API keys
- Usage-based billing integration
- Team management endpoints
- Role-based access control (RBAC)
- Notification system for agent events

**Breaking Changes:**
- All endpoints now require authentication
- Response format changed to include metadata wrapper
- Rate limits enforced per API key

---

## 🗺️ API Roadmap

### Q1 2026 (Next 3 Months)

**Planned Features:**
- **Streaming responses** for real-time agent output
- **WebSocket support** for persistent connections
- **GraphQL endpoint** for flexible data fetching
- **SDK updates** with caching and offline support

**Breaking Changes Preview:**
- None planned for v4.x
- v5.0 target: Q3 2026 (major refactor)

---

### Q2 2026

**Planned Features:**
- **Multi-region support** for data residency
- **Advanced analytics** endpoint with time-series queries
- **Plugin system** for custom integrations
- **Mobile SDK** (iOS/Android)

---

### Q3 2026

**v5.0 Planning:**
- REST + GraphQL unified API
- Async/await pattern throughout
- New pricing model support
- Enhanced security features

---

## 🔄 Deprecation Policy

### Lifecycle Stages

| Stage | Duration | Support Level |
|-------|----------|---------------|
| **Beta** | 1-2 months | Community support only |
| **Stable** | 12+ months | Full support, SLA applies |
| **Deprecated** | 6 months | Security fixes only |
| **Sunset** | - | Endpoint removed |

### Deprecation Notifications

When an endpoint is deprecated:
1. **Email notification** 6 months before removal
2. **Response header** includes `Deprecation: true` and `Sunset` date
3. **Documentation** updated with migration path
4. **SDK updates** with warnings

---

## 📊 API Metrics Dashboard

Track these metrics to monitor API health:

```bash
# Get current API metrics
curl http://localhost:8080/api/metrics | jq '.'
```

**Key Metrics:**
- Request volume by endpoint
- Error rates (target: <0.1%)
- P50/P95/P99 latency
- Rate limit hit rate
- Cache hit rate

---

## 🧰 SDK Reference

### Official SDKs

| SDK | Version | Status | Install |
|-----|---------|--------|---------|
| **Python** | 4.1.0 | Stable | `pip install j1msky` |
| **JavaScript** | 4.1.0 | Stable | `npm install j1msky` |
| **Go** | 4.0.0 | Beta | `go get github.com/j1msky/sdk-go` |
| **Rust** | 4.0.0 | Beta | `cargo add j1msky` |

---

### Python SDK

**Installation:**
```bash
pip install j1msky
```

**Basic Usage:**
```python
from j1msky import J1MSKYClient

# Initialize client
client = J1MSKYClient(
    base_url="http://localhost:8080",
    api_key="your_api_key"  # Optional for local instances
)

# Spawn an agent
agent = client.spawn(
    model="k2p5",
    task="Write a Python function to calculate fibonacci",
    priority="normal"
)

# Wait for completion with timeout
result = agent.wait_for_completion(timeout=300)
print(result.output)
print(f"Cost: ${result.cost}")
```

**Advanced Usage:**
```python
from j1msky import J1MSKYClient, TaskPriority

# Spawn with callback
agent = client.spawn(
    model="sonnet",
    task="Research AI trends",
    priority=TaskPriority.HIGH,
    webhook_url="https://your-app.com/webhook"
)

# Check status manually
status = client.get_agent_status(agent.id)
if status.state == "completed":
    print(status.result)

# Spawn team for complex tasks
team_result = client.spawn_team(
    team="team_creative",
    task="Design a landing page for our product",
    priority=TaskPriority.HIGH
)
```

**Error Handling:**
```python
from j1msky import J1MSKYClient, J1MSKYError, RateLimitError

client = J1MSKYClient()

try:
    result = client.spawn(model="k2p5", task="Hello world")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}s")
    time.sleep(e.retry_after)
    result = client.spawn(model="k2p5", task="Hello world")
except J1MSKYError as e:
    print(f"API Error: {e.message}")
    print(f"Request ID: {e.request_id}")  # For support
```

**Pricing Integration:**
```python
from j1msky import J1MSKYClient

client = J1MSKYClient()

# Get quote before running task
quote = client.get_quote(
    model="k2p5",
    estimated_input_tokens=2000,
    estimated_output_tokens=800,
    complexity="medium",
    segment="mid_market"
)

print(f"Internal cost: ${quote.internal_cost}")
print(f"Customer price: ${quote.recommended_price}")
print(f"Margin: {quote.gross_margin_pct}%")

# Check if quote passes guardrails
if quote.guardrail_check.is_compliant:
    # Safe to proceed
    agent = client.spawn(model="k2p5", task="Task description")
```

**Configuration:**
```python
from j1msky import J1MSKYClient, Config

config = Config(
    base_url="http://localhost:8080",
    api_key="your_key",
    timeout=30,
    max_retries=3,
    retry_delay=1.0,
    cache_enabled=True,
    cache_ttl=60
)

client = J1MSKYClient(config=config)
```

---

### JavaScript/TypeScript SDK

**Installation:**
```bash
npm install j1msky
# or
yarn add j1msky
```

**Basic Usage:**
```javascript
import { J1MSKYClient } from 'j1msky';

const client = new J1MSKYClient({
  baseUrl: 'http://localhost:8080',
  apiKey: 'your_api_key'
});

// Spawn an agent
const agent = await client.spawn({
  model: 'k2p5',
  task: 'Write a JavaScript function to reverse a string',
  priority: 'normal'
});

// Poll for completion
const result = await agent.waitForCompletion({ timeout: 300000 });
console.log(result.output);
console.log(`Cost: $${result.cost}`);
```

**With Async/Await:**
```javascript
import { J1MSKYClient } from 'j1msky';

async function runWorkflow() {
  const client = new J1MSKYClient();
  
  // Research phase
  const researcher = await client.spawn({
    model: 'sonnet',
    task: 'Research: Latest trends in AI automation'
  });
  const research = await researcher.waitForCompletion();
  
  // Writing phase
  const writer = await client.spawn({
    model: 'k2p5',
    task: `Write blog post based on: ${research.output}`
  });
  const article = await writer.waitForCompletion();
  
  return article;
}

runWorkflow().catch(console.error);
```

**Error Handling:**
```javascript
import { J1MSKYClient, RateLimitError, J1MSKYError } from 'j1msky';

const client = new J1MSKYClient();

try {
  const result = await client.spawn({ model: 'k2p5', task: 'Hello' });
} catch (error) {
  if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after: ${error.retryAfter}s`);
    await sleep(error.retryAfter * 1000);
    // Retry...
  } else if (error instanceof J1MSKYError) {
    console.error(`API Error: ${error.message}`);
    console.error(`Request ID: ${error.requestId}`);
  }
}
```

**Webhooks:**
```javascript
import { J1MSKYClient } from 'j1msky';

const client = new J1MSKYClient();

// Register webhook
await client.registerWebhook({
  url: 'https://your-app.com/webhooks/j1msky',
  events: ['agent.completed', 'agent.failed'],
  secret: 'your_webhook_secret'
});

// Spawn with automatic webhook notification
const agent = await client.spawn({
  model: 'k2p5',
  task: 'Analyze data',
  webhookUrl: 'https://your-app.com/webhooks/j1msky'
});
```

---

### Go SDK

**Installation:**
```bash
go get github.com/j1msky/sdk-go
```

**Basic Usage:**
```go
package main

import (
    "context"
    "fmt"
    "log"
    
    "github.com/j1msky/sdk-go"
)

func main() {
    client := j1msky.NewClient("http://localhost:8080", "api_key")
    
    ctx := context.Background()
    
    // Spawn agent
    agent, err := client.Spawn(ctx, j1msky.SpawnRequest{
        Model:    "k2p5",
        Task:     "Write a Go function",
        Priority: "normal",
    })
    if err != nil {
        log.Fatal(err)
    }
    
    // Wait for completion
    result, err := client.WaitForCompletion(ctx, agent.ID, 300)
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Println(result.Output)
    fmt.Printf("Cost: $%.2f\n", result.Cost)
}
```

---

### Rust SDK

**Installation:**
```toml
[dependencies]
j1msky = "4.0"
tokio = { version = "1", features = ["full"] }
```

**Basic Usage:**
```rust
use j1msky::Client;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = Client::new("http://localhost:8080", Some("api_key"));
    
    // Spawn agent
    let agent = client
        .spawn("k2p5", "Write a Rust function")
        .await?;
    
    // Wait for completion
    let result = client
        .wait_for_completion(&agent.id, 300)
        .await?;
    
    println!("{}", result.output);
    println!("Cost: ${}", result.cost);
    
    Ok(())
}
```

---

### SDK Features Comparison

| Feature | Python | JS/TS | Go | Rust |
|---------|--------|-------|----|----|
| **Sync/Async** | Both | Async | Sync | Async |
| **Type Hints** | ✅ | ✅ | N/A | ✅ |
| **Auto-retry** | ✅ | ✅ | ✅ | ✅ |
| **Caching** | ✅ | ✅ | ❌ | ❌ |
| **Streaming** | Planned | Planned | ❌ | ❌ |
| **Webhooks** | ✅ | ✅ | ✅ | ❌ |

---

### SDK Best Practices

**1. Use Connection Pooling:**
```python
# Python - requests.Session() is used internally
client = J1MSKYClient()  # Reuses connections automatically
```

**2. Handle Rate Limits Gracefully:**
```javascript
// JavaScript - SDK has built-in retry
const client = new J1MSKYClient({
  maxRetries: 5,
  retryDelay: 1000
});
```

**3. Use Webhooks Instead of Polling:**
```python
# Set up webhook for completion
client.register_webhook(url="https://your-app.com/webhook")

# Spawn without blocking
agent = client.spawn(model="k2p5", task="Long task")
# Result will POST to your webhook when ready
```

**4. Cache Quotes for Batch Operations:**
```python
quotes = client.get_batch_quotes(
    model="k2p5",
    complexities=["low", "medium", "high"],
    segments=["smb", "mid_market", "enterprise"]
)
```

---

## 🍳 API Cookbook

Real-world recipes for common use cases.

---

### Recipe 1: Content Creation Pipeline

**Use Case:** Automatically produce a blog post from topic to publication.

**Workflow:**
1. Research the topic
2. Write an outline
3. Write the full article
4. Edit and optimize
5. Generate social media snippets

**Implementation:**
```python
import requests
import time

BASE_URL = "http://localhost:8080/api"

def content_pipeline(topic):
    """End-to-end content creation pipeline."""
    
    # Step 1: Research
    research_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Research: {topic}. Find 5 key insights, 3 statistics, and 2 expert quotes.",
        "priority": "normal"
    }).json()
    
    research = poll_for_completion(research_agent["agent_id"])
    
    # Step 2: Outline
    outline_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "k2p5",
        "task": f"Create blog outline based on this research:\n{research['result']}\n\nInclude: intro, 5 sections, conclusion",
        "priority": "normal"
    }).json()
    
    outline = poll_for_completion(outline_agent["agent_id"])
    
    # Step 3: Write article
    writer_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Write 800-word blog post about '{topic}' following this outline:\n{outline['result']}\n\nTone: Professional but conversational. Include a compelling headline.",
        "priority": "normal"
    }).json()
    
    article = poll_for_completion(writer_agent["agent_id"])
    
    # Step 4: Edit
    editor_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "opus",
        "task": f"Edit this blog post for clarity, flow, and SEO. Add meta description:\n\n{article['result']}",
        "priority": "normal"
    }).json()
    
    final_article = poll_for_completion(editor_agent["agent_id"])
    
    # Step 5: Social snippets
    social_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Create 3 tweet-length snippets and 1 LinkedIn post from this article:\n{final_article['result']}",
        "priority": "low"
    }).json()
    
    social = poll_for_completion(social_agent["agent_id"])
    
    return {
        "research": research["result"],
        "outline": outline["result"],
        "article": final_article["result"],
        "social": social["result"],
        "total_cost": sum([
            research.get("cost", 0),
            outline.get("cost", 0),
            article.get("cost", 0),
            final_article.get("cost", 0),
            social.get("cost", 0)
        ])
    }

def poll_for_completion(agent_id, timeout=300):
    """Poll until agent completes."""
    start = time.time()
    while time.time() - start < timeout:
        status = requests.get(f"{BASE_URL}/agent/{agent_id}").json()
        if status.get("status") == "completed":
            return status
        elif status.get("status") == "failed":
            raise Exception(f"Agent failed: {status.get('error')}")
        time.sleep(2)
    raise TimeoutError("Agent didn't complete in time")

# Usage
result = content_pipeline("AI Automation in Marketing")
print(f"Article:\n{result['article']}")
print(f"\nSocial posts:\n{result['social']}")
print(f"\nTotal cost: ${result['total_cost']:.4f}")
```

---

### Recipe 2: Code Review Automation

**Use Case:** Automated code review and fix suggestions.

**Implementation:**
```python
def automated_code_review(code, language="python"):
    """Multi-stage code review with fixes."""
    
    # Step 1: Initial review
    review_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "k2p5",
        "task": f"Review this {language} code for bugs, security issues, and style violations. List each issue with line numbers:\n\n```{language}\n{code}\n```",
        "priority": "normal"
    }).json()
    
    review = poll_for_completion(review_agent["agent_id"])
    
    # Step 2: Generate fixes
    fix_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "k2p5",
        "task": f"Fix the issues identified in this code review. Return only the corrected code:\n\nOriginal code:\n{code}\n\nIssues to fix:\n{review['result']}",
        "priority": "normal"
    }).json()
    
    fixed = poll_for_completion(fix_agent["agent_id"])
    
    # Step 3: Security audit
    security_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Security audit of this code. Check for: injection vulnerabilities, exposed secrets, unsafe deserialization, path traversal:\n\n```{language}\n{fixed['result']}\n```",
        "priority": "high"
    }).json()
    
    security = poll_for_completion(security_agent["agent_id"])
    
    return {
        "original": code,
        "review": review["result"],
        "fixed_code": fixed["result"],
        "security_audit": security["result"],
        "total_cost": sum([
            review.get("cost", 0),
            fixed.get("cost", 0),
            security.get("cost", 0)
        ])
    }
```

---

### Recipe 3: Competitive Intelligence Monitor

**Use Case:** Monitor competitor websites and generate alerts.

**Implementation:**
```python
def monitor_competitor(url, competitor_name):
    """Monitor competitor website for changes."""
    
    # Step 1: Scrape and analyze
    research_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Analyze {url}. Extract: pricing, key features, messaging, target audience, recent changes. Format as structured report.",
        "priority": "normal"
    }).json()
    
    analysis = poll_for_completion(research_agent["agent_id"])
    
    # Step 2: Compare to our positioning
    comparison_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "opus",
        "task": f"Compare this competitor analysis to J1MSKY. Identify: their strengths, their weaknesses, how we should position against them, recommended messaging.\n\nCompetitor analysis:\n{analysis['result']}",
        "priority": "normal"
    }).json()
    
    comparison = poll_for_completion(comparison_agent["agent_id"])
    
    # Store for historical tracking
    store_competitor_data(competitor_name, analysis["result"])
    
    return {
        "competitor": competitor_name,
        "analysis": analysis["result"],
        "positioning": comparison["result"]
    }

def store_competitor_data(name, data):
    """Store competitor snapshot for change detection."""
    import json
    from datetime import datetime
    
    snapshot = {
        "date": datetime.now().isoformat(),
        "data": data
    }
    
    # Compare to previous
    try:
        with open(f"competitors/{name}_latest.json") as f:
            previous = json.load(f)
        
        # Generate diff
        diff_agent = requests.post(f"{BASE_URL}/spawn", json={
            "model": "k2p5",
            "task": f"Compare these two competitor snapshots and identify what changed:\n\nPrevious:\n{previous['data']}\n\nCurrent:\n{data}",
            "priority": "normal"
        }).json()
        
        diff = poll_for_completion(diff_agent["agent_id"])
        
        if "no changes" not in diff["result"].lower():
            # Send alert
            requests.post(f"{BASE_URL}/webhooks", json={
                "url": "https://your-slack-webhook.com",
                "event": f"Competitor {name} has changes: {diff['result'][:200]}"
            })
    except FileNotFoundError:
        pass
    
    # Save current
    with open(f"competitors/{name}_latest.json", "w") as f:
        json.dump(snapshot, f)
```

---

### Recipe 4: Customer Support Triage

**Use Case:** Classify and route support tickets automatically.

**Implementation:**
```python
def triage_support_ticket(ticket_text, customer_id):
    """Classify and route support ticket."""
    
    # Step 1: Classify issue
    classify_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "k2p5",
        "task": f"Classify this support ticket. Categories: bug_report, feature_request, billing_question, account_issue, technical_support. Also assign priority (low/medium/high/urgent) and estimate complexity (simple/moderate/complex).\n\nTicket: {ticket_text}",
        "priority": "high"
    }).json()
    
    classification = poll_for_completion(classify_agent["agent_id"])
    
    # Step 2: Generate suggested response
    response_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Draft a helpful response to this support ticket. If it's a common issue, provide solution steps. If complex, set expectations for follow-up.\n\nTicket: {ticket_text}\n\nClassification: {classification['result']}",
        "priority": "normal"
    }).json()
    
    response = poll_for_completion(response_agent["agent_id"])
    
    # Step 3: Route to appropriate team
    routing_rules = {
        "billing_question": "billing@company.com",
        "technical_support": "tech-support@company.com",
        "feature_request": "product@company.com",
        "bug_report": "engineering@company.com",
        "account_issue": "accounts@company.com"
    }
    
    category = extract_category(classification["result"])
    assigned_team = routing_rules.get(category, "support@company.com")
    
    return {
        "ticket_id": f"TICKET_{customer_id}_{int(time.time())}",
        "classification": classification["result"],
        "suggested_response": response["result"],
        "assigned_team": assigned_team,
        "auto_reply_sent": True
    }

def extract_category(classification_text):
    """Extract category from classification."""
    categories = ["bug_report", "feature_request", "billing_question", 
                  "account_issue", "technical_support"]
    for cat in categories:
        if cat in classification_text.lower():
            return cat
    return "general"
```

---

### Recipe 5: A/B Test Analysis

**Use Case:** Analyze A/B test results and generate recommendations.

**Implementation:**
```python
def analyze_ab_test(experiment_id):
    """Analyze A/B test and generate report."""
    
    # Get results from orchestrator
    results = requests.post(f"{BASE_URL}/orchestrator/experiment/results", json={
        "experiment_id": experiment_id
    }).json()
    
    if "error" in results:
        return {"error": results["error"]}
    
    # Generate analysis
    analysis_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "opus",
        "task": f"Analyze these A/B test results and provide: 1) Executive summary, 2) Statistical significance assessment, 3) Recommendation (roll out / keep testing / stop), 4) Risks to consider.\n\nResults:\n{json.dumps(results, indent=2)}",
        "priority": "normal"
    }).json()
    
    analysis = poll_for_completion(analysis_agent["agent_id"])
    
    # Generate presentation summary
    summary_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "sonnet",
        "task": f"Create a 3-slide presentation summary of these A/B test results:\n\n{analysis['result']}\n\nFormat: Slide 1 (Results), Slide 2 (Insights), Slide 3 (Recommendation)",
        "priority": "low"
    }).json()
    
    summary = poll_for_completion(summary_agent["agent_id"])
    
    return {
        "experiment_id": experiment_id,
        "raw_results": results,
        "analysis": analysis["result"],
        "presentation": summary["result"]
    }
```

---

### Recipe 6: Data Processing Pipeline

**Use Case:** Process large datasets in batches with agents.

**Implementation:**
```python
def batch_process_data(data_items, task_template, batch_size=10):
    """Process data items in parallel batches."""
    
    results = []
    batches = [data_items[i:i+batch_size] for i in range(0, len(data_items), batch_size)]
    
    for batch_idx, batch in enumerate(batches):
        print(f"Processing batch {batch_idx + 1}/{len(batches)}...")
        
        # Spawn agents for each item in batch
        agent_ids = []
        for item in batch:
            task = task_template.format(item=item)
            agent = requests.post(f"{BASE_URL}/spawn", json={
                "model": "k2p5",
                "task": task,
                "priority": "normal"
            }).json()
            agent_ids.append(agent["agent_id"])
        
        # Wait for all to complete
        for agent_id in agent_ids:
            result = poll_for_completion(agent_id, timeout=600)
            results.append(result)
    
    # Aggregate results
    aggregate_agent = requests.post(f"{BASE_URL}/spawn", json={
        "model": "opus",
        "task": f"Aggregate and summarize these {len(results)} results. Identify patterns, outliers, and key insights.\n\n" + "\n---\n".join([r["result"] for r in results]),
        "priority": "normal"
    }).json()
    
    summary = poll_for_completion(aggregate_agent["agent_id"])
    
    return {
        "individual_results": results,
        "summary": summary["result"],
        "total_cost": sum(r.get("cost", 0) for r in results) + summary.get("cost", 0)
    }

# Usage
data = ["item1", "item2", "item3", ...]  # 100 items
template = "Analyze this data item and extract key metrics: {item}"
results = batch_process_data(data, template, batch_size=10)
```

---

### Recipe 7: Multi-Language Translation

**Use Case:** Translate content to multiple languages with quality checks.

**Implementation:**
```python
def translate_with_review(content, target_languages=["spanish", "french", "german"]):
    """Translate content with quality review."""
    
    translations = {}
    
    for lang in target_languages:
        # Translate
        translate_agent = requests.post(f"{BASE_URL}/spawn", json={
            "model": "sonnet",
            "task": f"Translate this content to {lang}. Maintain tone and formatting:\n\n{content}",
            "priority": "normal"
        }).json()
        
        translated = poll_for_completion(translate_agent["agent_id"])
        
        # Quality review
        review_agent = requests.post(f"{BASE_URL}/spawn", json={
            "model": "opus",
            "task": f"Review this {lang} translation for accuracy, naturalness, and tone. Rate 1-10 and note any issues.\n\nOriginal: {content}\n\nTranslation: {translated['result']}",
            "priority": "normal"
        }).json()
        
        review = poll_for_completion(review_agent["agent_id"])
        
        # Revise if needed
        if "8" not in review["result"] and "9" not in review["result"] and "10" not in review["result"]:
            revise_agent = requests.post(f"{BASE_URL}/spawn", json={
                "model": "sonnet",
                "task": f"Improve this {lang} translation based on feedback:\n\nTranslation: {translated['result']}\n\nFeedback: {review['result']}",
                "priority": "normal"
            }).json()
            
            revised = poll_for_completion(revise_agent["agent_id"])
            final = revised["result"]
        else:
            final = translated["result"]
        
        translations[lang] = {
            "translation": final,
            "quality_score": review["result"],
            "cost": translated.get("cost", 0) + review.get("cost", 0)
        }
    
    return translations
```

---

## 📝 Release Notes Template

When releasing new versions, use this template for consistent communication.

### Version Numbering

**Format:** `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes requiring migration
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Examples:**
- `v4.1.0` - New features added
- `v4.1.1` - Bug fix
- `v5.0.0` - Major breaking changes

---

### Release Note Template

```markdown
# J1MSKY v[X.Y.Z] - Release Notes

**Release Date:** [YYYY-MM-DD]
**Support End Date:** [YYYY-MM-DD]
**Status:** [Beta/Stable/Deprecated]

---

## 🚀 What's New

### [Feature Name]
**Type:** [New Feature/Enhancement/Performance]

[Description of the feature and its benefits]

**Use Case:**
[Example scenario where this helps]

**How to Use:**
```python
# Code example
```

---

## ✨ Improvements

### [Improvement Area]
- [Description of improvement]
- [Another improvement]

---

## 🐛 Bug Fixes

### [Bug ID or Description]
**Issue:** [What was wrong]
**Fix:** [How it was resolved]
**Impact:** [Who was affected]

---

## ⚠️ Breaking Changes

### [Change Description]
**Before:** [Old behavior/code]
**After:** [New behavior/code]
**Migration:** [Steps to update]

---

## 📊 Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Latency (p95) | 1200ms | 800ms | 33% faster |
| Throughput | 100 req/s | 150 req/s | 50% increase |
| Error Rate | 2% | 0.5% | 75% reduction |

---

## 🔒 Security

### [Security Update]
**Severity:** [Critical/High/Medium/Low]
**CVE:** [CVE ID if applicable]
**Description:** [What was fixed]
**Action Required:** [Steps users must take]

---

## 📚 Documentation

- Updated: [Section/page]
- New: [New documentation]
- Fixed: [Documentation corrections]

---

## 🔄 Deprecations

### [Deprecated Feature]
**Deprecation Date:** [YYYY-MM-DD]
**Removal Date:** [YYYY-MM-DD]
**Replacement:** [Alternative to use]
**Migration Guide:** [Link]

---

## 🆕 SDK Updates

| SDK | Old Version | New Version | Status |
|-----|-------------|-------------|--------|
| Python | 4.0.0 | 4.1.0 | ✅ Released |
| JavaScript | 4.0.0 | 4.1.0 | ✅ Released |
| Go | 4.0.0 | 4.1.0 | 🔄 Beta |
| Rust | 4.0.0 | 4.1.0 | 🔄 Beta |

---

## 🧪 Known Issues

| Issue | Severity | Workaround | ETA Fix |
|-------|----------|------------|---------|
| [Description] | Medium | [Steps] | v4.1.1 |

---

## ⬆️ Upgrade Instructions

### Automatic (Recommended)
```bash
pip install --upgrade j1msky
```

### Manual
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Database Migrations
```bash
j1msky migrate
```

---

## 🎯 Compatibility

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| Python | 3.9 | 3.11+ |
| Node.js | 18 | 20 |
| Raspberry Pi OS | Bullseye | Bookworm |

---

## 📈 Statistics

- **Total Changes:** [X commits]
- **New Features:** [X]
- **Bug Fixes:** [X]
- **Contributors:** [X]
- **Lines Changed:** [+X, -X]

---

## 🙏 Acknowledgments

Thanks to our contributors and community members who made this release possible:
- [Name] - [Contribution]
- [Name] - [Contribution]

---

## 📞 Support

Questions about this release?
- Review the [migration guide](link)
- Check [updated documentation](link)
- Contact support@j1msky.ai

---

**Full Changelog:** [GitHub compare link]
```

---

## 📚 Resources

- **Full Docs:** https://docs.j1msky.ai
- **GitHub:** https://github.com/Mind-Expansion-Industries/j1msky-framework
- **Support:** support@j1msky.ai
- **Status:** https://status.j1msky.ai
- **Changelog RSS:** https://docs.j1msky.ai/changelog.xml

---

*API Version: 4.1*  
*Last Updated: February 21, 2026*
