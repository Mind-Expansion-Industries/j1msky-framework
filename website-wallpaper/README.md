# WallpaperDaily Monetization Funnel

Deployable client-facing landing page for art-generation subscription.

## Files
- `index.html` — Landing + offer + CTA page for AI wallpaper subscription

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

## Production TODO
- Connect CTA buttons to Stripe Checkout links
- Add email capture + welcome automation
- Add analytics (Plausible/GA)
- Replace placeholder gallery with generated samples
