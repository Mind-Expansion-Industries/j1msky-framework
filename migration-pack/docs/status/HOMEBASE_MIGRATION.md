# Homebase Migration (New Machine)

## Goal
Clone once, run bootstrap once, verify, done.

## 1) Clone + bootstrap
```bash
git clone https://github.com/Mind-Expansion-Industries/j1msky-framework.git ~/Desktop/J1MSKY
cd ~/Desktop/J1MSKY
./scripts/startup/bootstrap.sh ~/Desktop/J1MSKY
```

## 2) Verify services
```bash
./scripts/startup/verify.sh
```

You should see:
- Agency UI on `:8080`
- Alexa bridge on `:8091`
- Alexa Command Center on `:8092`

## 3) Move your configs from old machine
On old machine:
```bash
./scripts/startup/export-configs.sh
```
Copy generated `.tar.gz` to new machine.

On new machine:
```bash
./scripts/startup/import-configs.sh /path/to/export.tar.gz ~/Desktop/J1MSKY
```

## 4) Optional audio fix
```bash
./scripts/audio/fix-alexa-bluetooth.sh EC:0D:E4:92:37:5A
./scripts/audio/set-audio-profile.sh alexa
```

## 5) Optional Home Assistant package install
Copy these into HA config if needed:
- `homeassistant/packages/j1msky_bridge.yaml`
- `homeassistant/sentences/en/j1msky.yaml`

Restart HA.

---

## One-command local controls
- Audio switcher: `./scripts/audio/set-audio-profile.sh list|alexa|jack|hdmi1|hdmi2`
- YouTube media: `./scripts/audio/youtube-control.sh pause|play|next`
- Alexa bridge test:
```bash
curl -X POST http://127.0.0.1:8091/command -H "Content-Type: application/json" -d '{"command":"play music"}'
```
