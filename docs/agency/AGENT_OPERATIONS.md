# J1MSKY Agent Operations Runbook

## Agent Roles
- **Opus (CEO):** architecture + strategic decisions (max 1 major decision/hour)
- **Sonnet (Ops):** implementation + docs + continuity
- **Kimi Lead:** coding architecture + task delegation
- **MiniMax/Codex:** implementation lanes

## Task Routing
1. Intake task
2. Classify: code / content / research / business
3. Assign model by cost-performance
4. Spawn subagent or team
5. Track status in dashboard
6. Commit output + notes

## Priority Policy
- **High:** client-blocking, production bugs
- **Normal:** feature work, docs
- **Low:** polish, refactors

## Rate Limit Policy
- Track in dashboard panel
- Soft warning at 70%
- Hard throttle at 90%
- Cooldown then retry

## Commit Policy
Format:
`[AGENT] [TYPE] message`
Examples:
- `[SONNET] [UI] improve mobile nav spacing`
- `[KIMI] [CODE] add spawn-task validation`
- `[OPUS] [ARCH] finalize team orchestration strategy`

## Backup Policy
- Hourly local commit attempt
- Push when remote allows
- Keep `logs/` and `reports/` updated

## Incident Response
- Dashboard down: restart service + verify port 8080
- Model errors: failover to cheaper/available model
- High temp (>85C): reduce workload + pause heavy jobs

## Daily Closeout
- Generate summary report
- Confirm pending queue
- Review costs vs revenue
- Set next-day priorities
