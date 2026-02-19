#!/bin/bash
# J1MSKY Website Deployment Script
# One-command deploy to production

set -e

WEBSITE_DIR="/home/m1ndb0t/Desktop/J1MSKY/website"
DEPLOY_TYPE="${1:-local}"

echo "🚀 J1MSKY Website Deploy Script"
echo "================================"
echo ""

case $DEPLOY_TYPE in
    local)
        echo "📍 Deploying locally on port 8080..."
        echo "   URL: http://localhost:8080"
        echo "   Press Ctrl+C to stop"
        echo ""
        cd "$WEBSITE_DIR"
        python3 -m http.server 8080
        ;;
    
    pi)
        echo "🥧 Deploying to Raspberry Pi web server..."
        sudo mkdir -p /var/www/html/j1msky
        sudo cp -r "$WEBSITE_DIR"/* /var/www/html/j1msky/
        echo "   Deployed to: http://$(hostname -I | awk '{print $1}')/j1msky/"
        ;;
    
    vercel)
        echo "▲ Preparing for Vercel deployment..."
        if ! command -v vercel &> /dev/null; then
            echo "   Installing Vercel CLI..."
            npm install -g vercel
        fi
        cd "$WEBSITE_DIR"
        vercel --prod
        ;;
    
    netlify)
        echo "◆ Preparing for Netlify deployment..."
        if ! command -v netlify &> /dev/null; then
            echo "   Installing Netlify CLI..."
            npm install -g netlify-cli
        fi
        cd "$WEBSITE_DIR"
        netlify deploy --prod --dir=.
        ;;
    
    zip)
        echo "📦 Creating deployment archive..."
        OUTPUT="/home/m1ndb0t/Desktop/J1MSKY/j1msky-website-$(date +%Y%m%d).zip"
        cd "$WEBSITE_DIR"
        zip -r "$OUTPUT" .
        echo "   Archive created: $OUTPUT"
        echo "   Upload this to Vercel/Netlify/Cloudflare Pages"
        ;;
    
    *)
        echo "Usage: ./deploy-website.sh [local|pi|vercel|netlify|zip]"
        echo ""
        echo "Options:"
        echo "  local   - Serve locally on port 8080 (default)"
        echo "  pi      - Deploy to Raspberry Pi /var/www/html/"
        echo "  vercel  - Deploy to Vercel (requires account)"
        echo "  netlify - Deploy to Netlify (requires account)"
        echo "  zip     - Create deployment archive"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
