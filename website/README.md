# J1MSKY AI Agency Website

A high-converting landing page for the J1MSKY AI agency business.

## 🚀 Deploy Options

### Option 1: Static Host (Recommended)
Upload `index.html` to:
- **Vercel**: Drag & drop to vercel.com
- **Netlify**: Drag & drop to netlify.com
- **Cloudflare Pages**: Upload to pages.dev
- **GitHub Pages**: Enable in repo settings

### Option 2: Self-Hosted (Raspberry Pi)
```bash
# Copy to web directory
sudo cp -r website/* /var/www/html/

# Or serve directly with Python
cd website && python3 -m http.server 8080
```

### Option 3: Docker
```dockerfile
FROM nginx:alpine
COPY . /usr/share/nginx/html
```

## 📁 Files

- `index.html` — Complete landing page + pricing offer + Netlify-ready lead form
- `thank-you.html` — Post-submit conversion page
- `audit.html` — Focused lead-gen page: Free AI Operations Audit offer (use for ads/outreach)
- `book.html` — Pre-qualifier intake page before scheduling
- `netlify.toml` — Deploy config (redirects + security/cache headers)
- `robots.txt` and `sitemap.xml` — Basic SEO crawl/index support
- Embedded CSS & JavaScript
- Zero external dependencies except Google Fonts

## 🎯 Conversion Features

1. **Hero Section** — Strong value prop with animated background
2. **Live Ticker** — Simulates activity/social proof
3. **Services Grid** — Clear offer presentation
4. **Pricing Cards** — 3-tier structure with "Popular" highlight
5. **ROI Calculator** — Interactive revenue upside estimator that pushes to booking CTA
6. **Testimonials** — Social proof section
7. **Contact Form** — Netlify-ready lead capture with anti-spam honeypot

## 🔧 Customization

### Lead Form Setup
The form is pre-configured for **Netlify Forms**:
- `data-netlify="true"`
- `name="agency-leads"`
- Captures `utm_source`, `utm_medium`, `utm_campaign`
- Redirects to `/thank-you.html`

If hosting elsewhere, point the form `action` to your CRM endpoint (HubSpot, Formspree, custom API).

### Direct Booking CTA
A pre-qualifier booking path is included:
- CTA on `index.html` points to `/book.html`
- `book.html` collects budget/timeline/goal and then forwards to Calendly
- Replace `https://calendly.com/your-handle/ai-strategy-call` in `book.html` with your live booking URL.

### Update Pricing
Edit the pricing cards in the HTML directly:
- Find `id="pricing"` section
- Modify prices, features, CTAs

### Update Branding
- Logo: Find `class="logo"`
- Colors: Edit CSS `:root` variables
- Copy: Modify text throughout

## 🌐 Deploy Hardening + SEO

- `netlify.toml` adds:
  - clean redirects (`/`, `/book`, `/thanks`)
  - baseline security headers
  - short cache policy for quick iteration
- `robots.txt` + `sitemap.xml` are included for search indexing
- Update `https://j1msky.ai` in `sitemap.xml` and `robots.txt` if your domain differs

## 📊 Analytics Setup

Add to `<head>` for tracking:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_ID"></script>

<!-- Plausible (privacy-friendly) -->
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## 🎨 Design System

| Element | Value |
|---------|-------|
| Primary | `#6366f1` (Indigo) |
| Accent | `#22d3ee` (Cyan) |
| Dark BG | `#0f172a` (Slate 900) |
| Font | Inter |
| Border Radius | 8-20px |
| Shadows | Purple glow on CTAs |

## 📝 TODO for Production

- [x] Connect contact form via Netlify Forms (or swap action to CRM endpoint)
- [ ] Add analytics tracking
- [ ] Set up custom domain
- [ ] Add SSL certificate
- [ ] Test mobile responsiveness
- [ ] Add favicon
- [ ] SEO meta tags optimization
- [ ] Add sitemap.xml
- [ ] Set up conversion tracking pixels

## 🔄 A/B Test Ideas

1. **Headline**: "AI Agents" vs "AI Team" vs "AI Workforce"
2. **CTA**: "Start Free Trial" vs "Get Started" vs "Deploy Agents"
3. **Pricing**: Show monthly vs annual savings
4. **Social Proof**: Move testimonials above pricing
5. **Urgency**: Add limited-time offer banner

---

Built with autonomous agents ◈ 2026
