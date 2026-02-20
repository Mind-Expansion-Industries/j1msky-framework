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

## Stripe Checkout Wiring (5 min)
1. Create Stripe payment links for Daily and Pro plans (monthly + annual).
2. In `index.html`, update:
   - `CHECKOUT_LINKS.daily_monthly`
   - `CHECKOUT_LINKS.daily_annual`
   - `CHECKOUT_LINKS.pro_monthly`
   - `CHECKOUT_LINKS.pro_annual`
3. Configure Stripe redirect URLs:
   - Success URL: `https://YOUR-DOMAIN/success.html`
   - Cancel URL: `https://YOUR-DOMAIN/cancel.html`
4. Deploy and test each plan button end-to-end.

## Production TODO
- Connect CTA buttons to live Stripe Checkout links
- Connect `captureLead()` to ConvertKit/Mailchimp/API endpoint
- Add analytics (Plausible/GA)
- Replace placeholder gallery with generated samples
- Set launch coupon in Stripe (50% first month) to match page copy
- Validate UTM + checkout attribution in Stripe dashboard (`client_reference_id` / UTM params)
