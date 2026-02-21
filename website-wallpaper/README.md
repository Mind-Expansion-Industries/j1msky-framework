# WallpaperDaily Monetization Funnel

Deployable client-facing landing page for art-generation subscription.

## Files
- `index.html` — Landing + offer + CTA page for AI wallpaper subscription
- `gift.html` — Gift subscription page for viral growth
- `teams.html` — Team/enterprise plans for B2B sales
- `affiliates.html` — Affiliate program for creator partnerships (30% recurring)
- `privacy.html` — Privacy policy page
- `terms.html` — Terms of service page
- `success.html` / `cancel.html` — Stripe redirect completion pages

## Offer Structure
- Free: $0/mo (weekly wallpaper)
- Daily: $3/mo (daily 4K wallpapers)
- Pro: $8/mo (3/day, 8K, commercial license)

## Deploy
```bash
cd /home/m1ndb0t/Desktop/J1MSKY/website-wallpaper
python3 -m http.server 8090
```

Or upload `index.html` to Netlify/Vercel/Cloudflare Pages.

## Lead Capture Wiring (deployable now)
The landing page is configured with a production-safe **Netlify Form**:
- form name: `wallpaper-leads`
- anti-spam honeypot included
- captures: email, selected plan, selected billing, UTM params
- success redirect: `/success.html`

If using a different host, point the form `action` to your backend/CRM endpoint.

## Production TODO
- Connect lead webhook/CRM automation (ConvertKit, Mailchimp, HubSpot, etc.)
- Add analytics (Plausible/GA)
- Replace placeholder gallery with generated samples
- Optional: add Stripe checkout links after validating pricing/offer
- Validate UTM and plan-intent attribution in your CRM

## Conversion Additions
- Sticky bottom CTA bar keeps the launch offer visible while scrolling
- Countdown is mirrored in hero promo + sticky CTA for urgency consistency
- Gift page (`gift.html`) enables viral acquisition through gift purchases
