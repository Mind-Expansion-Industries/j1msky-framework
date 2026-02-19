#!/usr/bin/env python3
"""
J1MSKY Alexa Bridge (MVP)
- Receives command requests (webhook or local HTTP)
- Maps phrases -> actions
- Supports Home Assistant webhook calls (recommended)
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import json, os, subprocess, urllib.request

CONFIG_PATH = os.path.expanduser('~/Desktop/J1MSKY/alexa_commands.json')
DEFAULT_CONFIG = {
  "home_assistant": {
    "base_url": "http://homeassistant.local:8123",
    "token": "REPLACE_ME_LONG_LIVED_TOKEN",
    "enabled": False
  },
  "actions": {
    "play music": {"type": "ha_service", "domain": "media_player", "service": "media_play", "entity_id": "media_player.echo_dot"},
    "pause music": {"type": "ha_service", "domain": "media_player", "service": "media_pause", "entity_id": "media_player.echo_dot"},
    "next track": {"type": "ha_service", "domain": "media_player", "service": "media_next_track", "entity_id": "media_player.echo_dot"},
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


def handle_command(text):
    cfg = load_config()
    t = text.strip().lower()
    action = cfg.get('actions', {}).get(t)
    if not action:
        return False, f'Unknown command: {text}'
    if action['type'] == 'ha_service':
        return call_ha_service(cfg, action)
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
