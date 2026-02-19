# ◈ J1MSKY UNIFIED MODEL STACK v5.1 ◈
## Complete Integration: Anthropic + Kimi + MiniMax + Codex

---

## 🎯 MODEL HIERARCHY (CEO-Worker Structure)

### 👔 C-SUITE (Strategic Decisions)

**Claude Opus (CEO/Mastermind)**
- **Provider:** anthropic (anthropic:default)
- **Cost:** $0.015/1K tokens
- **Frequency:** 1x per hour (strategic only)
- **Role:** Architecture, major decisions, complex reasoning
- **Fallback:** Claude Sonnet
- **When to use:**
  - System architecture design
  - Business strategy pivots
  - Complex problem solving
  - Code review (critical)

---

### 👷 MANAGEMENT (Operations)

**Claude Sonnet (Operations Manager)**
- **Provider:** anthropic (anthropic:default)
- **Cost:** $0.003/1K tokens
- **Frequency:** Continuous
- **Role:** Implementation, documentation, continuity
- **Fallback:** Kimi K2.5
- **When to use:**
  - General implementation
  - Documentation writing
  - UI/UX design
  - Content creation
  - Maintains context between sessions

---

### 👨‍💻 TECHNICAL LEADERSHIP

**Kimi K2.5 (Lead Developer)**
- **Provider:** kimi-coding (kimi-coding:default)
- **Cost:** $0.001/1K tokens
- **Frequency:** As needed
- **Role:** Code architecture, technical design
- **Fallback:** MiniMax M2.5
- **When to use:**
  - Code architecture decisions
  - Technical design reviews
  - Complex coding tasks
  - Task delegation to dev team

---

### ⚡ ENGINEERING TEAM

**MiniMax M2.5 (Senior Developer)**
- **Provider:** minimax-portal (minimax-portal:default)
- **Status:** ✅ Active (expires in 365d)
- **Cost:** $0.001/1K tokens
- **Frequency:** High
- **Role:** Fast coding, implementation, prototyping
- **Fallback:** OpenAI Codex
- **When to use:**
  - Rapid prototyping
  - Quick implementations
  - Feature development
  - Bug fixes
  - UI components

**OpenAI Codex (Specialist Developer)**
- **Provider:** openai-codex (openai-codex:default)
- **Status:** ✅ Active (expires in 10d, 5h remaining)
- **Cost:** $0.002/1K tokens
- **Frequency:** Specialist tasks
- **Role:** API integrations, specialized coding
- **Fallback:** Claude Sonnet
- **When to use:**
  - API integrations
  - Third-party tool connections
  - Specialized implementations
  - Tool building

---

## 🔄 ORCHESTRATION FLOW

```
USER REQUEST
    ↓
[Task Classification]
    ↓
    ├─ Architecture/Strategy → Opus (CEO)
    ├─ Implementation → Sonnet (Ops)
    ├─ Code Architecture → Kimi Lead
    ├─ Fast Coding → MiniMax
    └─ API/Integration → Codex
    ↓
[Execution]
    ↓
[Result Delivery]
    ↓
[Commit with [AGENT] tag]
```

---

## 📊 RATE LIMITS & BUDGET

| Provider | Hourly Limit | Current | Status |
|----------|--------------|---------|--------|
| Anthropic (Opus/Sonnet) | 50 | 0 | 🟢 Ready |
| Kimi Coding | 100 | 0 | 🟢 Ready |
| MiniMax Portal | 100 | 0 | 🟢 Ready (365d) |
| OpenAI Codex | 20 | 0 | 🟢 Ready (10d left) |

**Daily Budget:** $50.00  
**Alert Threshold:** 80% ($40.00)

---

## 💰 COST OPTIMIZATION

### Cheapest to Most Expensive:
1. **Kimi K2.5** - $0.001/1K (default for coding)
2. **MiniMax M2.5** - $0.001/1K (fast implementations)
3. **OpenAI Codex** - $0.002/1K (specialist work)
4. **Claude Sonnet** - $0.003/1K (general work)
5. **Claude Opus** - $0.015/1K (strategy only)

### Cost Strategy:
- Default to Kimi/MiniMax for coding
- Use Sonnet for general tasks
- Reserve Opus for architecture (1x/hour max)
- Use Codex only for API integrations
- Automatic fallback to cheaper models when rate limited

---

## 🛠️ USAGE EXAMPLES

### Example 1: Build New Feature
```
Opus (CEO): Design architecture
    ↓
Kimi (Lead): Technical design
    ↓
MiniMax (Dev): Implement fast
    ↓
Sonnet (Ops): Document feature
    ↓
[Commit: [TEAM] built feature X]
```

### Example 2: Fix Critical Bug
```
Sonnet (Ops): Analyze bug
    ↓
Kimi (Lead): Root cause analysis
    ↓
MiniMax (Dev): Quick fix
    ↓
Sonnet (Ops): Test & verify
    ↓
[Commit: [MINIMAX] fixed critical bug]
```

### Example 3: API Integration
```
Opus (CEO): Integration strategy
    ↓
Kimi (Lead): Design API layer
    ↓
Codex (Specialist): Build integration
    ↓
Sonnet (Ops): Write docs
    ↓
[Commit: [CODEX] integrated Stripe API]
```

### Example 4: Documentation
```
Sonnet (Ops): Write comprehensive docs
    ↓
[Commit: [SONNET] added user manual]
```

---

## 📁 FILES IN UNIFIED STACK

| File | Purpose |
|------|---------|
| `config/model-stack.json` | Model configuration & rate limits |
| `orchestrator.py` | Unified orchestration logic |
| `j1msky-agency-v5.py` | Responsive dashboard (all models) |
| `AGENCY_MANUAL.md` | Operator guide |
| `API_REFERENCE.md` | Developer docs |
| `BUSINESS_SETUP.md` | Revenue guide |
| `AGENT_OPERATIONS.md` | Runbook |

---

## 🚀 QUICK COMMANDS

### Check Model Status
```bash
python3 orchestrator.py
```

### Get Model for Task
```python
from orchestrator import orchestrator
model = orchestrator.get_model_for_task("coding", "medium")
# Returns: "k2p5" or "minimax-m2.5"
```

### Get Team for Project
```python
team = orchestrator.get_team_for_project("web_app")
# Returns: {'lead': 'k2p5', 'frontend': 'minimax-m2.5', ...}
```

### Estimate Cost
```python
cost = orchestrator.estimate_cost("opus", 2000)
# Returns: $0.03
```

---

## ✅ INTEGRATION STATUS

- [x] Anthropic (Opus + Sonnet) - ✅ Active
- [x] Kimi Coding (K2.5) - ✅ Active
- [x] MiniMax Portal (M2.5) - ✅ Active (365d)
- [x] OpenAI Codex - ✅ Active (10d remaining)
- [x] Fallback chains configured
- [x] Rate limit tracking
- [x] Cost optimization
- [x] Unified orchestrator
- [x] Dashboard integration

---

## 📈 DASHBOARD ACCESS

**Current Dashboard:** `j1msky-agency-v5.py`
- URL: http://localhost:8080
- All 5 models integrated
- Rate limit panel
- Cost tracking
- Team deployment

---

## 🎯 TONIGHT'S AUTONOMOUS OPERATION

With full model stack, I will:

1. **Opus (1x/hour):** Strategic architecture decisions
2. **Sonnet (continuous):** Implementation, docs, continuity
3. **Kimi Lead:** Code architecture, task delegation
4. **MiniMax:** Fast coding, UI components, implementations
5. **Codex:** API integrations, specialist tools

**All commits tagged:** `[MODEL] [TYPE] description`

---

**Full model stack is LIVE and OPERATIONAL.**  
**All 5 models ready for autonomous agency operation.** 🚀

*Version: 5.1*  
*Status: All Models Integrated*  
*Orchestration: Active*
