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

## 📝 Changelog

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

**Changed:**
- API authentication now uses Bearer tokens
- Rate limit response includes `retry_after` header
- Standardized error response format across all endpoints

**Removed:**
- Legacy v2 endpoints (sunset as of 2026-01-01)

### v3.2.0 (2025-12-15)
**Maintenance Release**

**Added:**
- Health check endpoint (`GET /health`)
- System metrics endpoint (`GET /metrics`)

**Fixed:**
- Rate limit counter not resetting correctly
- Memory leak in long-running agents

### v3.1.0 (2025-11-01)
**Feature Release**

**Added:**
- Batch agent spawning (`POST /spawn-batch`)
- Agent priority levels (low, normal, high)
- Custom timeout configuration per agent

**Changed:**
- Improved error messages for invalid models
- Reduced default agent timeout from 10min to 5min

### v3.0.0 (2025-09-15)
**Major Release - Business Tier**

**Added:**
- Enterprise authentication with API keys
- Usage-based billing integration
- Team management endpoints
- Role-based access control (RBAC)

**Breaking Changes:**
- All endpoints now require authentication
- Response format changed to include metadata wrapper

---

## 📚 Resources

- **Full Docs:** https://docs.j1msky.ai
- **GitHub:** https://github.com/Mind-Expansion-Industries/j1msky-framework
- **Support:** support@j1msky.ai
- **Status:** https://status.j1msky.ai

---

*API Version: 4.0*  
*Last Updated: February 19, 2026*
