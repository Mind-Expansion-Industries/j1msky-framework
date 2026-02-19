# Alexa Bridge Setup (J1MSKY)

## What this gives you now
- Basic command bridge for Alexa-style commands
- Music controls via Home Assistant + Alexa Media Player
- Task triggers into J1MSKY (backup/start dashboard/etc.)

## Files
- `alexa_bridge.py` (service)
- `alexa_commands.json` (auto-generated command map)

## 1) Start bridge now
```bash
cd ~/Desktop/J1MSKY
python3 alexa_bridge.py
# health check
curl http://localhost:8091/health
```

## 2) Test a command directly
```bash
curl -X POST http://localhost:8091/command \
  -H 'Content-Type: application/json' \
  -d '{"command":"play music"}'
```

## 3) Connect to Alexa (recommended path)
Use **Home Assistant** + **Alexa Media Player** custom integration.

### You must do:
1. Install Home Assistant (if not already)
2. Install HACS
3. Add Alexa Media Player integration (custom)
4. Login your Amazon account in HA
5. Find your Echo entity id (`media_player.echo_dot` etc.)
6. Edit `~/Desktop/J1MSKY/alexa_commands.json`:
   - set `home_assistant.enabled=true`
   - set `home_assistant.base_url`
   - set long-lived `home_assistant.token`
   - set correct `entity_id`

## 4) Optional: run as service
Create systemd unit `/etc/systemd/system/j1msky-alexa-bridge.service`:
```ini
[Unit]
Description=J1MSKY Alexa Bridge
After=network.target

[Service]
User=m1ndb0t
WorkingDirectory=/home/m1ndb0t/Desktop/J1MSKY
ExecStart=/usr/bin/python3 /home/m1ndb0t/Desktop/J1MSKY/alexa_bridge.py
Restart=always
Environment=ALEXA_BRIDGE_PORT=8091

[Install]
WantedBy=multi-user.target
```
Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now j1msky-alexa-bridge
```

## 5) Next phase
- Add YouTube controls (FireTV / Android TV bridge)
- Add music generation trigger command
- Add scene macros (focus mode, stream mode, sleep mode)
