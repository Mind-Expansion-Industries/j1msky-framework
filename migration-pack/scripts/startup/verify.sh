#!/usr/bin/env bash
set -euo pipefail

echo "== J1MSKY Homebase Verify =="

ok(){ echo "[OK] $1"; }
warn(){ echo "[WARN] $1"; }

# repo
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then ok "Git repo detected"; else warn "Not in git repo"; fi

# ports/services
for p in 8080 8091 8092; do
  if ss -tlnp | grep -q ":$p"; then ok "Port $p listening"; else warn "Port $p not listening"; fi
done

for svc in j1msky-agency.service j1msky-alexa-bridge.service j1msky-alexa-center.service; do
  if systemctl --user is-active --quiet "$svc"; then ok "Service $svc active"; else warn "Service $svc inactive"; fi
done

# endpoints
curl -fsS http://127.0.0.1:8080 >/dev/null 2>&1 && ok "Agency UI reachable" || warn "Agency UI not reachable"
curl -fsS http://127.0.0.1:8091/health >/dev/null 2>&1 && ok "Alexa bridge healthy" || warn "Alexa bridge not healthy"
curl -fsS http://127.0.0.1:8092 >/dev/null 2>&1 && ok "Alexa command center reachable" || warn "Alexa command center not reachable"

# audio utilities
for c in pactl bluetoothctl cvlc jq; do
  command -v "$c" >/dev/null 2>&1 && ok "$c installed" || warn "$c missing"
done

# config presence
for f in \
  alexa_commands.json \
  audio_profiles.json \
  scripts/audio/fix-alexa-bluetooth.sh \
  scripts/audio/set-audio-profile.sh; do
  [ -f "$f" ] && ok "Found $f" || warn "Missing $f"
done

# quick sink info
echo
echo "Default sink:"
pactl info | sed -n 's/^Default Sink: /- /p' || true

echo
echo "Verify complete."
