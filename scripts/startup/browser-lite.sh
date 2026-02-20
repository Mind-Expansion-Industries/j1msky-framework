#!/usr/bin/env bash
set -euo pipefail

# Lightweight Chromium profile for Raspberry Pi responsiveness
pkill -f chromium 2>/dev/null || true
sleep 1

exec chromium \
  --user-data-dir=/home/m1ndb0t/.config/chromium-lite \
  --process-per-site \
  --disk-cache-size=52428800 \
  --media-cache-size=10485760 \
  --disable-background-networking \
  --disable-component-update \
  --disable-sync \
  --disable-extensions \
  --disable-features=Translate,BackForwardCache,OptimizationHints \
  --enable-gpu-rasterization \
  --ignore-gpu-blocklist \
  "http://127.0.0.1:8080"
