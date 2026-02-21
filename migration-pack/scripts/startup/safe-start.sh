#!/usr/bin/env bash
set -euo pipefail

# Safe-start: only starts/restarts missing services, avoids port conflicts
# Services/ports:
# 8080 -> j1msky-agency.service
# 8091 -> j1msky-alexa-bridge.service
# 8092 -> j1msky-alexa-center.service
# 8093 -> j1msky-work-feed.service

need_port(){ ss -tln | awk '{print $4}' | grep -q ":$1$"; }
ensure_service(){
  local svc="$1"
  systemctl --user is-enabled "$svc" >/dev/null 2>&1 || systemctl --user enable "$svc" >/dev/null 2>&1 || true
}
start_if_needed(){
  local port="$1" svc="$2"
  if need_port "$port"; then
    echo "[ok] :$port already listening"
  else
    echo "[fix] :$port missing -> starting $svc"
    ensure_service "$svc"
    systemctl --user restart "$svc" || systemctl --user start "$svc" || true
    sleep 1
    if need_port "$port"; then
      echo "[ok] :$port restored"
    else
      echo "[warn] :$port still down"
    fi
  fi
}

echo "== jimsky safe-start =="

# Make sure units exist (if not, run watchdog installer)
if ! systemctl --user list-unit-files | grep -q 'j1msky-agency.service'; then
  echo "[init] installing watchdog units"
  /home/m1ndb0t/Desktop/J1MSKY/scripts/startup/enable-watchdogs.sh || true
fi

start_if_needed 8080 j1msky-agency.service
start_if_needed 8091 j1msky-alexa-bridge.service
start_if_needed 8092 j1msky-alexa-center.service
start_if_needed 8093 j1msky-work-feed.service

echo
curl -fsS http://127.0.0.1:8091/health >/dev/null 2>&1 && echo "[ok] Alexa bridge health good" || echo "[warn] Alexa bridge health check failed"

echo "Done."
