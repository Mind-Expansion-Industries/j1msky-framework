# J1MSKY + Home Assistant Setup (Ready-to-Apply)

You said HA is already installed. Great — do this:

## 1) Enable packages in `configuration.yaml`
Add:
```yaml
homeassistant:
  packages: !include_dir_named packages
```

## 2) Copy package + sentences
Copy files:
- `homeassistant/packages/j1msky_bridge.yaml` -> `/config/packages/j1msky_bridge.yaml`
- `homeassistant/sentences/en/j1msky.yaml` -> `/config/custom_sentences/en/j1msky.yaml`

## 3) Restart Home Assistant
Settings -> System -> Restart

## 4) Verify bridge is running on your Pi
```bash
curl http://127.0.0.1:8091/health
```
Should return:
```json
{"ok": true, "service": "alexa-bridge"}
```

## 5) Test from HA Developer Tools -> Services
Run:
- `script.j1msky_play_music`
- `script.j1msky_pause_music`
- `script.j1msky_next_track`
- `script.j1msky_open_command_center`

## 6) Alexa media entity check
Edit `~/Desktop/J1MSKY/alexa_commands.json` and set real entity id:
```json
"entity_id": "media_player.YOUR_ECHO_ENTITY"
```

## 7) Optional voice phrases (Assist)
Try:
- "J1MSKY play music"
- "J1MSKY pause music"
- "J1MSKY next track"

---

## What this gives you now
- HA -> J1MSKY command bridge
- Music controls via Alexa media player services
- One place to add more actions (YouTube, scenes, generation)

## Next add-ons I can wire next
- Fire TV / YouTube control
- "Generate music" command and route to model pipeline
- Night/focus/stream scenes
