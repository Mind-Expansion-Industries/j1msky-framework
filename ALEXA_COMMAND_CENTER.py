#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, urllib.request

HTML='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>jimsky Alexa Command Center</title>
<style>body{font-family:Arial;background:#0b0f14;color:#e6f1ff;margin:0;padding:18px}button{width:100%;padding:14px;margin:8px 0;border:0;border-radius:10px;background:#22d3ee;color:#03131a;font-weight:700} .card{max-width:680px;margin:auto;background:#111a2b;border:1px solid #223;border-radius:12px;padding:16px}</style></head><body><div class="card"><h2>jimsky Alexa Command Center</h2>
<button onclick="send('play music')">▶ Play Music</button>
<button onclick="send('pause music')">⏸ Pause Music</button>
<button onclick="send('next track')">⏭ Next Track</button>
<button onclick="send('volume up')">🔊 Volume Up</button>
<button onclick="send('volume down')">🔉 Volume Down</button>
<hr style="border-color:#223; margin:10px 0"/>
<button onclick="send('set audio alexa')">🟦 Output: Alexa BT</button>
<button onclick="send('set audio jack')">🟩 Output: 3.5mm Jack</button>
<button onclick="send('set audio hdmi1')">🟨 Output: HDMI 1</button>
<button onclick="send('set audio hdmi2')">🟧 Output: HDMI 2</button>
<hr style="border-color:#223; margin:10px 0"/>
<button onclick="send('youtube pause')">⏸ YouTube Pause</button>
<button onclick="send('youtube play')">▶ YouTube Play</button>
<button onclick="send('youtube next')">⏭ YouTube Next</button>
<hr style="border-color:#223; margin:10px 0"/>
<button onclick="send('open command center')">🖥 Open Command Center</button>
<button onclick="send('run backup')">💾 Run Backup</button>
<pre id="out"></pre>
</div><script>
async function send(cmd){
 const r=await fetch('/cmd',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd})});
 const j=await r.json(); document.getElementById('out').textContent=JSON.stringify(j,null,2);
}
</script></body></html>'''

class H(BaseHTTPRequestHandler):
    def _json(self, code,obj):
        self.send_response(code); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(obj).encode())
    def log_message(self, *args): pass
    def do_GET(self):
        if self.path=='/':
            self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(HTML.encode()); return
        self.send_response(404); self.end_headers()
    def do_POST(self):
        if self.path!='/cmd': return self._json(404,{"ok":False})
        ln=int(self.headers.get('Content-Length','0')); raw=self.rfile.read(ln)
        try: data=json.loads(raw.decode())
        except: data={}
        cmd=data.get('command','')
        req=urllib.request.Request('http://127.0.0.1:8091/command',data=json.dumps({'command':cmd}).encode(),method='POST')
        req.add_header('Content-Type','application/json')
        try:
            with urllib.request.urlopen(req,timeout=12) as r:
                resp=json.loads(r.read().decode())
            return self._json(200,resp)
        except Exception as e:
            return self._json(500,{"ok":False,"error":str(e)})

if __name__=='__main__':
    HTTPServer(('0.0.0.0',8092),H).serve_forever()
