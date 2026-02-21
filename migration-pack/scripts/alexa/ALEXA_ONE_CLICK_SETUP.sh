#!/usr/bin/env bash
set -e

BASE="/home/m1ndb0t/Desktop/J1MSKY"
CFG="$BASE/alexa_commands.json"
EXAMPLE="$BASE/alexa_commands.example.json"

echo "=== J1MSKY Alexa One-Click Setup ==="

# 1) Ensure bridge deps/files exist
if [ ! -f "$BASE/alexa_bridge.py" ]; then
  echo "Missing alexa_bridge.py. Aborting."
  exit 1
fi

# 2) Create local config if missing
if [ ! -f "$CFG" ]; then
  cp "$EXAMPLE" "$CFG"
  echo "Created $CFG from example"
fi

# 3) Beginner-friendly setup mode
read -rp "Use LOCAL mode first (no Home Assistant needed)? [Y/n]: " LOCAL_FIRST
LOCAL_FIRST=${LOCAL_FIRST:-Y}

if [[ "$LOCAL_FIRST" =~ ^[Yy]$ ]]; then
  HA_URL="http://homeassistant.local:8123"
  HA_TOKEN=""
  ECHO_ENTITY="media_player.echo_dot"
  python3 - <<PY
import json
p='$CFG'
with open(p,'r') as f:
    c=json.load(f)
c.setdefault('home_assistant',{})['enabled']=False
c.setdefault('local_mode',{})['enabled']=True
with open(p,'w') as f:
    json.dump(c,f,indent=2)
print('Configured LOCAL mode in',p)
PY
else
  read -rp "Home Assistant base URL [http://homeassistant.local:8123]: " HA_URL
  HA_URL=${HA_URL:-http://homeassistant.local:8123}
  read -rp "Home Assistant Long-Lived Token (leave blank to skip for now): " HA_TOKEN
  read -rp "Echo media_player entity_id [media_player.echo_dot]: " ECHO_ENTITY
  ECHO_ENTITY=${ECHO_ENTITY:-media_player.echo_dot}

  python3 - <<PY
import json
p='$CFG'
with open(p,'r') as f:
    c=json.load(f)
c.setdefault('home_assistant',{})['base_url']='$HA_URL'
if '$HA_TOKEN'.strip():
    c['home_assistant']['token']='$HA_TOKEN'
    c['home_assistant']['enabled']=True
else:
    c['home_assistant']['enabled']=False
c.setdefault('local_mode',{})['enabled']=True
acts=c.setdefault('actions',{})
for k in ['play music','pause music','next track','volume up','volume down']:
    if k in acts and acts[k].get('type')=='ha_service':
        acts[k]['entity_id']='$ECHO_ENTITY'
with open(p,'w') as f:
    json.dump(c,f,indent=2)
print('Updated',p)
PY
fi

# 4) Install Home Assistant package files if HA config path exists
HA_PATHS=("/config" "$HOME/.homeassistant" "/home/homeassistant/.homeassistant")
FOUND=""
for p in "${HA_PATHS[@]}"; do
  if [ -d "$p" ]; then FOUND="$p"; break; fi
done

if [ -n "$FOUND" ]; then
  echo "Detected Home Assistant config at: $FOUND"
  mkdir -p "$FOUND/packages" "$FOUND/custom_sentences/en"
  cp "$BASE/homeassistant/packages/j1msky_bridge.yaml" "$FOUND/packages/j1msky_bridge.yaml"
  cp "$BASE/homeassistant/sentences/en/j1msky.yaml" "$FOUND/custom_sentences/en/j1msky.yaml"
  echo "Copied HA package + sentences."
  echo "IMPORTANT: ensure configuration.yaml has:"
  echo "homeassistant:"
  echo "  packages: !include_dir_named packages"
else
  echo "Could not auto-detect HA config path."
  echo "Manual copy from: $BASE/homeassistant/... to your HA /config"
fi

# 5) Start/restart Alexa bridge
pkill -f "alexa_bridge.py" 2>/dev/null || true
nohup python3 "$BASE/alexa_bridge.py" >/tmp/alexa-bridge.log 2>&1 &
sleep 1

echo "Bridge health:"
curl -s http://127.0.0.1:8091/health || true

echo
cat <<EOF
Setup complete.

Quick test now (works in LOCAL mode too):
curl -X POST http://127.0.0.1:8091/command -H 'Content-Type: application/json' -d '{"command":"play music"}'

If using Home Assistant mode:
1) Restart Home Assistant
2) In HA Developer Tools -> Services, run script.j1msky_play_music
3) If it fails, check token/entity in $CFG

Open local command center:
http://127.0.0.1:8092
EOF
