# J1MSKY AI Agency — Client Portal

**Status:** ✅ Deploy-Ready  
**Last Updated:** February 21, 2026  
**Type:** Client-Facing Landing Page + Lead Capture

---

## 🎯 Purpose

This is a **conversion-focused landing page** for J1MSKY's AI agency services. It captures leads, explains the value proposition, and drives trial sign-ups.

---

## 📁 Files

| File | Purpose |
|------|---------|
| `index.html` | Main landing page with all sections |
| `thank-you.html` | Post-form submission confirmation |

---

## 🚀 Deployment

### Option 1: Netlify (Recommended)
```bash
cd /home/m1ndb0t/Desktop/J1MSKY/agency
# Drag folder to netlify.com or use CLI
netlify deploy --prod --dir=.
```

### Option 2: Vercel
```bash
vercel --prod
```

### Option 3: GitHub Pages
1. Push to GitHub repo
2. Enable Pages in settings
3. Select `/agency` folder

### Option 4: Self-Hosted (Raspberry Pi)
```bash
# Copy to web server
cp -r /home/m1ndb0t/Desktop/J1MSKY/agency/* /var/www/html/agency/

# Or serve directly with Python
cd /home/m1ndb0t/Desktop/J1MSKY/agency
python3 -m http.server 8081
```

---

## 🎨 Features

### Landing Page Sections
1. **Hero** — Value prop + CTA + stats
2. **Services** — 4 AI team cards (Code, Creative, Research, Business)
3. **How It Works** — 3-step process
4. **Pricing** — 3 tiers (Starter/Pro/Enterprise)
5. **Testimonials** — Social proof
6. **FAQ** — Expandable questions
7. **Contact Form** — Lead capture with Netlify Forms
8. **Sticky CTA** — Always-visible action button

### Technical
- Mobile-responsive design
- Dark mode aesthetic matching brand
- Smooth scroll navigation
- Interactive FAQ accordion
- Form validation
- Plan selection via URL params

---

## 💰 Pricing Tiers

| Plan | Price | Target |
|------|-------|--------|
| Starter | $49/mo | Solopreneurs, small projects |
| Pro | $99/mo | Growing businesses |
| Enterprise | $299/mo | Larger organizations |

---

## 📊 Conversion Elements

- **Urgency:** "Limited spots available" sticky CTA
- **Risk Reversal:** 7-day free trial, no CC required
- **Social Proof:** 3 testimonials with photos/roles
- **Trust:** "60% cost reduction" trust strip
- **Scarcity:** "Now accepting clients" badge

---

## 🔗 Integration Points

### Netlify Forms
Form submits to Netlify with these fields:
- `name` — Full name
- `email` — Email address
- `company` — Company name
- `plan` — Selected plan (starter/pro/enterprise/not-sure)
- `task` — First task description

### Post-Submission
- Redirects to `thank-you.html`
- Email confirmation to user (configure in Netlify)
- Notification to admin (configure in Netlify)

---

## 📝 TODO Before Launch

- [ ] Configure Netlify account and forms
- [ ] Set up custom domain (e.g., `agency.j1msky.ai`)
- [ ] Add Google Analytics / Fathom tracking
- [ ] Connect email (hello@j1msky.ai)
- [ ] Add real testimonials
- [ ] Test form submission end-to-end
- [ ] Set up automated email sequence

---

## 🔄 Next Iterations

1. Add Calendly integration for "Book Demo"
2. Create pricing calculator widget
3. Add live chat (Tidio/Crisp)
4. Build case study pages
5. Add video explainer

---

**Built for revenue. Ready to deploy.** ◈
