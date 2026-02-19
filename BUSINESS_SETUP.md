# J1MSKY Business Setup Guide

## 1) Offer Structure
- **Starter**: $49/mo (2 teams, limited tasks)
- **Pro**: $99/mo (all teams, unlimited tasks)
- **Enterprise**: $299+/mo (custom SLA)
- **Pay-per-task**: $0.50 / $2.00 / $5.00 tiers

## 2) Revenue Workflow
1. Lead comes in (DM/form)
2. Qualify use-case (code/content/research/business)
3. Assign plan + expected monthly volume
4. Onboard in dashboard
5. Run trial tasks
6. Convert to subscription

## 3) Cost Control Rules
- Default model: **Kimi K2.5**
- Escalate to **Sonnet** for writing/analysis
- Use **Opus** for architecture/strategy only
- Hard cap hourly requests via rate-limit panel
- Daily cost review at end of day

## 4) Stripe Integration Checklist
- Add Stripe keys to `config/business.json`
- Create products (Starter/Pro/Enterprise)
- Enable webhook endpoint for:
  - checkout.session.completed
  - customer.subscription.updated
  - customer.subscription.deleted
- Test in Stripe sandbox first

## 5) Operations SOP
- Morning: review errors, queue, rate limits
- Midday: process high-priority tasks
- Evening: optimize model usage + margins
- Hourly: auto-commit + backup

## 6) KPIs to Track
- MRR
- Cost per completed task
- Gross margin
- Avg task completion time
- Churn rate
- Active clients

## 7) Launch Sequence
- Day 1: soft launch with 3 pilot users
- Day 2-3: tune pricing + onboarding copy
- Day 4-7: public launch + testimonials

## 8) Risk Controls
- If rate-limited: queue tasks + switch cheaper model
- If dashboard down: restart service + fallback to local scripts
- If costs spike: pause Opus + enforce Kimi-only mode
