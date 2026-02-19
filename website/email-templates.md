# J1MSKY Onboarding Email Sequence

Complete email templates for converting trials to paid customers.

---

## Email 1: Welcome (Sent Immediately)

**Subject:** 🎉 Your AI agents are ready — here's your dashboard

```
Hi {{first_name}},

Welcome to J1MSKY! Your 14-day free trial is now active.

🚀 GET STARTED NOW
→ Dashboard Login: [LINK]
→ Quick Setup Video: [LINK] (2 minutes)
→ First Task Templates: [LINK]

Your trial includes:
✓ {{plan_task_limit}} tasks
✓ All agent teams (Code, Creative, Research, Business)
✓ Priority support

WHAT TO TRY FIRST:
Most new users start with one of these:
• "Write a blog post about [your topic]"
• "Review my website homepage copy"
• "Research competitors in [your industry]"
• "Debug this code: [paste your code]"

NEED HELP?
Reply to this email — I read every one personally.

Talk soon,
[Your Name]
Founder, J1MSKY

P.S. Book your free onboarding call here: [CALENDLY_LINK] 
    (15 min — we'll set up your first workflow together)
```

---

## Email 2: Day 2 — First Task Reminder

**Subject:** Have you deployed your first agent yet?

```
Hi {{first_name}},

Quick check-in — how's your first day with J1MSKY?

If you haven't deployed your first task yet, here's the easiest way to start:

1. Log into your dashboard: [LINK]
2. Click "Spawn Agent"
3. Type: "Write a 500-word blog post about [YOUR_TOPIC]"
4. Hit Enter

That's it. Your agent will start working immediately.

STUCK?
Common questions:
→ "What tasks work best?" — [LINK]
→ "How do I get better results?" — [LINK]
→ "Can agents access my code/files?" — [LINK]

Hit reply if you need anything.

[Your Name]
```

---

## Email 3: Day 5 — Success Stories

**Subject:** How Sarah saved 20 hours last month

```
Hi {{first_name}},

I wanted to share how other {{plan_name}} users are leveraging J1MSKY:

CASE STUDY: Sarah's Content Engine
Sarah runs a marketing agency. She was spending 15+ hours/week on content.

Now she:
→ Deploys 3 agents every Monday morning
→ Gets 12 blog posts drafted by Tuesday
→ Spends her time editing (not writing from scratch)

Result: 20 hours saved, 3x more content published.

YOUR TURN:
What repetitive task could you delegate?

→ Research? → Try the Research Team
→ Content? → Try the Creative Team  
→ Code? → Try the Code Team

[Spawn Your First Agent]

[Your Name]

P.S. Sarah's on the Professional plan ($99/mo). At 20 hours saved, 
that's $4.95/hour for AI labor. Pretty good deal.
```

---

## Email 4: Day 10 — Trial Ending Soon

**Subject:** 4 days left — want to keep your agents?

```
Hi {{first_name}},

Your trial ends in 4 days.

CURRENT USAGE:
✓ Tasks completed: {{tasks_completed}}
✓ Time saved (est): {{hours_saved}} hours
✓ Plan: {{plan_name}}

To keep your agents active, choose a plan:

→ Starter ($49/mo): 100 tasks, 2 teams
→ Professional ($99/mo): Unlimited tasks, all teams ← Most Popular
→ Enterprise ($299/mo): Dedicated agents, SLA

[Upgrade Now — Keep My Agents]

QUESTIONS BEFORE YOU DECIDE?
Hit reply or book a quick call: [CALENDLY_LINK]

If J1MSKY isn't right for you, no worries — your agents will simply 
pause at the end of your trial. No charges, no hassle.

[Your Name]
```

---

## Email 5: Day 14 — Last Day (Urgency)

**Subject:** ⏰ Trial ends today — last chance to upgrade

```
Hi {{first_name}},

Your free trial ends TODAY.

WHAT HAPPENS NOW:
→ If you upgrade: Your agents keep working, uninterrupted
→ If you don't: Your account pauses (no charges, no data loss)

YOUR TRIAL BY NUMBERS:
• Tasks completed: {{tasks_completed}}
• Estimated time saved: {{hours_saved}} hours
• Cost if you hired humans: ~${{human_cost}}

UPGRADE IN 30 SECONDS:
[Choose Your Plan →]

NOT READY YET?
Need more time? Reply and I'll extend your trial 7 more days. 
No questions asked.

[Your Name]
```

---

## Email 6: Post-Trial — Win Back (if didn't convert)

**Subject:** We miss you — 40% off to come back?

```
Hi {{first_name}},

I noticed your trial ended and you didn't upgrade.

Totally okay — J1MSKY isn't for everyone.

But before you go: What was the main reason?

A) Too expensive
B) Didn't see the value  
C) Too complicated
D) Not the right time
E) Something else

Just hit reply with A, B, C, D, or E.

If it's about price: I can offer 40% off your first 3 months.
That brings Professional down to $59/mo.

[Claim 40% Off — Come Back]

Either way, thanks for trying J1MSKY.

[Your Name]
```

---

## Email 7: Monthly Newsletter (Ongoing)

**Subject:** New: Custom agents + 3 use cases you haven't tried

```
Hi {{first_name}},

This month's J1MSKY updates:

🆕 NEW FEATURE: Custom Agent Training
Upload your brand guidelines, code standards, or writing samples.
Your agents learn your style. No more generic output.

[Try Custom Training]

📈 TOP USE CASES (Last 30 Days)
1. SEO Content at Scale — How agencies publish 50+ posts/month
2. Code Review Automation — Catch bugs before humans do
3. Competitor Monitoring — Daily intelligence reports

[Read the Guides]

💡 PRO TIP
Chain multiple agents for complex workflows:
→ Research Team: Analyze topic
→ Creative Team: Write outline  
→ Creative Team: Write article
→ Code Team: Publish to CMS

Total time: 15 minutes of your input → Full article in 2 hours.

[Your Name]

P.S. Know someone who needs AI agents? 
Refer them and get 1 month free: [REFERRAL_LINK]
```

---

## Implementation Notes

### Variables to Substitute
- `{{first_name}}` — User's first name
- `{{plan_name}}` — Starter/Professional/Enterprise
- `{{plan_task_limit}}` — Number of tasks in their plan
- `{{tasks_completed}}` — Tasks done during trial
- `{{hours_saved}}` — Estimated hours (tasks_completed × 0.5)
- `{{human_cost}}` — Estimated cost at $50/hour

### Tools
- **Send emails:** ConvertKit, Mailchimp, or Postmark
- **Personalization:** Liquid syntax or Handlebars
- **Tracking:** UTM params on all links
- **Scheduling:** Automate based on signup date

### A/B Test Ideas
1. Subject lines: Emoji vs no emoji
2. CTA buttons: "Upgrade Now" vs "Keep My Agents"
3. Send times: Morning (9am) vs Afternoon (2pm)
4. Social proof: Case study vs testimonial quote

---

*Templates version 1.0 — Update as you learn what converts*
