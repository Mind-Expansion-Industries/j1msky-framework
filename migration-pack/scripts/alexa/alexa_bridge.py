#!/usr/bin/env python3
"""
J1MSKY Alexa Bridge (MVP)
- Receives command requests (webhook or local HTTP)
- Maps phrases -> actions
- Supports Home Assistant webhook calls (recommended)
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json, os, subprocess, urllib.request, shlex

CONFIG_PATH = os.path.expanduser('~/Desktop/J1MSKY/alexa_commands.json')
DEFAULT_CONFIG = {
  "home_assistant": {
    "base_url": "http://homeassistant.local:8123",
    "token": "REPLACE_ME_LONG_LIVED_TOKEN",
    "enabled": False
  },
  "local_mode": {
    "enabled": True,
    "streams": [
      "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one",
      "https://stream.live.vc.bbcmedia.co.uk/bbc_6music",
      "https://ice1.somafm.com/groovesalad-128-mp3"
    ]
  },
  "actions": {
    "play music": {"type": "music", "op": "play"},
    "pause music": {"type": "music", "op": "pause"},
    "next track": {"type": "music", "op": "next"},
    "volume up": {"type": "music", "op": "volup"},
    "volume down": {"type": "music", "op": "voldown"},
    "morning ops": {"type": "shell", "command": "cd ~/Desktop/J1MSKY && ./start-office-windowed.sh"},
    "run backup": {"type": "shell", "command": "cd ~/Desktop/J1MSKY && git add -A && git commit -m '[ALEXA] backup trigger' || true"}
  }
}


def load_config():
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)


def call_ha_service(cfg, action):
    ha = cfg.get('home_assistant', {})
    if not ha.get('enabled'):
        return False, 'Home Assistant integration disabled'
    url = f"{ha['base_url']}/api/services/{action['domain']}/{action['service']}"
    payload = {"entity_id": action.get('entity_id')}
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), method='POST')
    req.add_header('Authorization', f"Bearer {ha['token']}")
    req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            return True, f'HA service called ({r.status})'
    except Exception as e:
        return False, str(e)


def run_shell(command):
    try:
        out = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=20)
        return out.returncode == 0, (out.stdout + out.stderr).strip()[:500]
    except Exception as e:
        return False, str(e)


def _state_path():
    return os.path.expanduser('~/Desktop/J1MSKY/.alexa_bridge_state.json')


def _load_state():
    p = _state_path()
    if os.path.exists(p):
        try:
            with open(p, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {"stream_index": 0, "volume": 100}


def _save_state(state):
    with open(_state_path(), 'w') as f:
        json.dump(state, f)


def _music_action(cfg, op):
    state = _load_state()
    streams = cfg.get('local_mode', {}).get('streams', [])
    if not streams:
        return False, 'No streams configured in local_mode.streams'

    if op == 'play':
        idx = state.get('stream_index', 0) % len(streams)
        url = streams[idx]
        # stop old player then start
        subprocess.run('pkill -f "cvlc --intf dummy"', shell=True)
        cmd = f"nohup cvlc --intf dummy --play-and-exit {shlex.quote(url)} >/tmp/alexa-music.log 2>&1 &"
        subprocess.run(cmd, shell=True)
        return True, f'Playing stream {idx+1}/{len(streams)}'

    if op == 'pause':
        subprocess.run('pkill -f "cvlc --intf dummy"', shell=True)
        return True, 'Playback stopped'

    if op == 'next':
        state['stream_index'] = (state.get('stream_index', 0) + 1) % len(streams)
        _save_state(state)
        return _music_action(cfg, 'play')

    if op == 'volup':
        subprocess.run('pactl set-sink-volume @DEFAULT_SINK@ +5%', shell=True)
        return True, 'Volume increased'

    if op == 'voldown':
        subprocess.run('pactl set-sink-volume @DEFAULT_SINK@ -5%', shell=True)
        return True, 'Volume decreased'

    return False, f'Unknown music op: {op}'


def handle_command(text):
    cfg = load_config()
    t = text.strip().lower()
    action = cfg.get('actions', {}).get(t)
    if not action:
        return False, f'Unknown command: {text}'
    if action['type'] == 'ha_service':
        ok, msg = call_ha_service(cfg, action)
        # fallback to local music if HA disabled and this is media control
        if not ok and cfg.get('local_mode', {}).get('enabled') and action.get('service', '').startswith('media_'):
            op_map = {
                'media_play': 'play',
                'media_pause': 'pause',
                'media_next_track': 'next'
            }
            op = op_map.get(action.get('service', ''), 'play')
            return _music_action(cfg, op)
        return ok, msg
    if action['type'] == 'music':
        return _music_action(cfg, action.get('op', 'play'))
    if action['type'] == 'shell':
        return run_shell(action['command'])
    return False, 'Unsupported action type'


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

    def do_GET(self):
        if self.path.startswith('/health'):
            return self._json(200, {'ok': True, 'service': 'alexa-bridge'})
        return self._json(404, {'ok': False})

    def do_POST(self):
        if self.path.startswith('/command'):
            ln = int(self.headers.get('Content-Length', '0'))
            raw = self.rfile.read(ln).decode()
            ctype = self.headers.get('Content-Type', '')
            text = ''
            if 'application/json' in ctype:
                data = json.loads(raw or '{}')
                text = data.get('command', '')
            else:
                data = parse_qs(raw)
                text = (data.get('command') or [''])[0]
            ok, msg = handle_command(text)
            return self._json(200 if ok else 400, {'ok': ok, 'message': msg, 'command': text})
        return self._json(404, {'ok': False})


def main():
    port = int(os.environ.get('ALEXA_BRIDGE_PORT', '8091'))
    s = HTTPServer(('0.0.0.0', port), H)
    print(f'Alexa bridge listening on :{port}')
    s.serve_forever()


if __name__ == '__main__':
    main()
