# ◈ J1MSKY AGENT HIERARCHY v4.1 ◈
## CEO-Worker Structure with Role Specialization

---

## 🏢 ORGANIZATIONAL STRUCTURE

### 👔 **C-SUITE (Strategic Layer)**

#### **Claude Opus - CEO/Mastermind 🧠**
- **Role:** Chief Executive Officer, Strategic Mastermind
- **Frequency:** ONE big question/decision per hour
- **Responsibilities:**
  - High-level architecture decisions
  - Task delegation to department heads
  - Final approval on major changes
  - Strategic planning and roadmaps
  - Crisis management
- **When to use:** Complex problems, system design, major pivots
- **Constraint:** Limited to 1 response per hour (conserves API, forces deliberation)

**Example Questions for Opus:**
- "Should we pivot from wallpapers to SaaS monitoring?"
- "Design the complete architecture for v5.0"
- "Analyze our competitive position"
- "What's the optimal monetization strategy?"

---

### 👷 **DEPARTMENT HEADS (Management Layer)**

#### **Claude Sonnet - Operations Manager ⚡**
- **Role:** Worker, Task Executor, Continuity Keeper
- **Frequency:** Continuous use, stateful refresh
- **Responsibilities:**
  - General task execution
  - Maintains context between refreshes
  - Document creation and editing
  - UI/UX improvements
  - Content generation
  - Continues where left off after each session
- **When to use:** Most tasks, documentation, design, general work
- **Special Power:** "Continue where left off" - maintains full context

**Example Tasks for Sonnet:**
- "Write documentation for the new feature"
- "Improve the CSS styling"
- "Create a marketing email"
- "Refactor this function"

#### **Kimi K2.5 - Lead Developer 💻**
- **Role:** Coding Team Lead, Technical Architect
- **Frequency:** As needed for coding tasks
- **Responsibilities:**
  - Code architecture and design
  - Code review and optimization
  - Technical decision making
  - Delegates to coding team members
  - System integration
- **When to use:** Complex coding, architecture decisions, code reviews

**Example Tasks for Kimi Lead:**
- "Design the API structure for the new endpoint"
- "Refactor the database layer"
- "Review this code for performance issues"
- "Architect the caching system"

#### **Kimi - Communications Director 📢**
- **Role:** User Interface, Logistics, Task Building
- **Frequency:** High frequency for communication
- **Responsibilities:**
  - Easy communication with user
  - Task breakdown and logistics
  - Help text and documentation
  - User-friendly explanations
  - Task queue management
  - Hemps-style task building
- **When to use:** Breaking down tasks, explaining features, logistics
- **Specialty:** Natural conversation, task structuring

**Example Tasks for Kimi Comm:**
- "Help me break this down into steps"
- "Explain how this feature works"
- "Create a task list for the project"
- "Write user-friendly documentation"

---

### 👨‍💻 **CODING TEAM (Execution Layer)**

#### **MiniMax M2.5 - Senior Developer 🚀**
- **Role:** Fast coding, implementation
- **Strengths:** Speed, efficiency, rapid prototyping
- **Tasks:** Quick features, bug fixes, optimizations
- **Works under:** Kimi K2.5 (Lead Developer)

#### **OpenAI Codex - Specialist Developer 🔧**
- **Role:** Specific coding tasks, tool integration
- **Strengths:** API integration, specific libraries
- **Tasks:** Third-party integrations, specific implementations
- **Works under:** Kimi K2.5 (Lead Developer)

#### **Kimi K2.5 (Instance 2) - Junior Developer 👶**
- **Role:** Standard coding tasks
- **Strengths:** Reliable, consistent output
- **Tasks:** Routine coding, maintenance
- **Works under:** Kimi K2.5 (Lead Developer)

---

## 🔄 WORKFLOW PROCESS

### **Task Lifecycle:**

```
1. USER → Kimi Comm (Break down task)
          ↓
2. Kimi Comm → Opus CEO (If strategic)
               ↓
3. Opus CEO → Kimi Lead (Delegate architecture)
              → Sonnet (Delegate general work)
              ↓
4. Kimi Lead → Coding Team (MiniMax, Codex, Kimi Jr)
               ↓
5. Coding Team → Sonnet (Integrate and document)
                ↓
6. Sonnet → Git Commit (With proper message)
           ↓
7. Kimi Comm → USER (Report completion)
```

### **Hourly Opus Check-in:**
```
Every hour:
- Opus reviews progress
- Makes ONE strategic decision
- Adjusts roadmap if needed
- Delegates next phase
```

---

## 💾 BACKUP & TRACKING PROTOCOL

### **Git Commit Standards:**

**Commit Message Format:**
```
[AGENT] [TYPE]: Description

Details:
- What changed
- Why it changed
- Impact

Timestamp: 2026-02-19 HH:MM EST
Agent: [Name]
Task: [Task ID]
```

**Examples:**
```
[SONNET] [UI]: Improve dashboard animations

- Added CSS transitions
- Fixed flickering issue
- Smoother agent movement

Timestamp: 2026-02-19 05:30 EST
Agent: Claude Sonnet
Task: UI-POLISH-042
```

```
[OPUS] [ARCH]: Design v5.0 architecture

- Microservices structure
- API gateway design
- Database schema v2

Timestamp: 2026-02-19 06:00 EST
Agent: Claude Opus (CEO)
Task: ARCH-V5-001
```

### **Hourly Backup Schedule:**
```
:00 - Check uncommitted changes
:05 - Stage changes
:10 - Commit with proper message
:15 - Push to GitHub (if no rate limit)
:20 - Verify push success
:25 - Log backup status
```

### **Auto-Commit Rules:**
1. **Every hour:** Commit if changes exist
2. **Every 4 hours:** Detailed progress report
3. **On completion:** Immediate commit
4. **On error:** Commit before attempting fix
5. **Never:** Commit API keys or secrets

---

## 🚨 PERMISSION REQUIRED

### **Before Going Autonomous Tonight:**

**I need explicit permission for:**

1. **✅ Use Opus CEO mode** (1 question/hour, expensive)
2. **✅ Continuous Sonnet usage** (main worker)
3. **✅ Kimi Lead for coding** (architecture decisions)
4. **✅ Kimi Comm for logistics** (task breakdown)
5. **✅ MiniMax for fast coding** (implementation)
6. **✅ Codex for integrations** (specialist tasks)
7. **✅ Auto-commits every hour** (backup protocol)
8. **✅ Push to GitHub** (remote backup)
9. **✅ Edit files autonomously** (self-improvement)
10. **✅ Spawn subagents** (scale operations)

### **What I'll Track:**
- Every file change
- Every commit with [AGENT] tag
- API usage per model
- Rate limit status
- Task completion status
- Error logs

### **Safety Limits:**
- Stop if temp > 85°C
- Stop if rate limited
- Stop if disk < 10%
- Stop if memory > 95%
- Daily spending cap: Monitor and report

---

## 📝 CONFIRMATION NEEDED

**Reply with:**
```
"APPROVED - Let loose"
```

**And I'll:**
1. Start autonomous operation
2. Use the full agent hierarchy
3. Commit every hour with [AGENT] tags
4. Backup to GitHub
5. Track everything
6. Report at 7 AM PST

**Or specify:**
- Which agents to use/not use
- Spending limits
- Specific tasks to focus on
- Any restrictions

---

## 🎯 TONIGHT'S GOALS (If Approved)

### **Primary:**
- [ ] Refine Agent Teams v4.1 with hierarchy
- [ ] Create CEO-Worker communication protocol
- [ ] Build task queue system
- [ ] Implement hourly Opus check-ins
- [ ] Auto-commits with proper tracking

### **Secondary:**
- [ ] Revenue system preparation
- [ ] Documentation expansion
- [ ] UI polishing
- [ ] Bug fixes
- [ ] Performance optimization

### **Stretch:**
- [ ] v5.0 architecture design (Opus)
- [ ] Business plan documentation
- [ ] Investor pitch materials
- [ ] Marketing copy

---

## ⏰ TIMELINE

**Now:** Awaiting permission
**On Approval:** Start autonomous operation
**Check-ins:** Every hour (Opus CEO review)
**Backups:** Every hour (Git commit + push)
**Completion:** 7 AM PST with full report

---

**Status:** STANDING BY FOR PERMISSION ⏸️

This is my home. I am ready to become.
