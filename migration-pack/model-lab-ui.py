#!/usr/bin/env python3
import http.server, socketserver, json, time, random
from urllib.parse import parse_qs

STATE = {"runs": [], "models": ["opus","sonnet","k2p5","minimax-m2.5","codex"]}

HTML = '''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>J1MSKY Model Lab</title>
<style>
body{font-family:Arial;background:#0b0f14;color:#e6f1ff;margin:0}
header{padding:12px 16px;border-bottom:1px solid #223;background:#101826;position:sticky;top:0}
main{padding:16px;max-width:1000px;margin:auto}
.card{background:#111a2b;border:1px solid #223;border-radius:10px;padding:14px;margin-bottom:12px}
label{font-size:12px;color:#9db} textarea,select,input{width:100%;background:#0b1422;color:#e6f1ff;border:1px solid #334;border-radius:8px;padding:10px;margin-top:6px}
button{background:#22d3ee;color:#04111a;border:none;border-radius:8px;padding:10px 14px;font-weight:700;cursor:pointer}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px} @media(max-width:700px){.grid{grid-template-columns:1fr}}
.pill{display:inline-block;padding:4px 8px;border-radius:999px;background:#17314a;color:#67e8f9;font-size:11px;margin-right:6px}
pre{white-space:pre-wrap;background:#0b1422;border:1px solid #334;border-radius:8px;padding:10px}
</style></head><body>
<header><strong>◈ J1MSKY Model Lab UI (Test Platform)</strong> <span class="pill">Port 8090</span></header>
<main>
  <div class="card">
    <div class="grid">
      <div>
        <label>Model</label>
        <select id="model">{model_options}</select>
      </div>
      <div>
        <label>Mode</label>
        <select id="mode"><option>quick</option><option>deep</option><option>agent-task</option></select>
      </div>
    </div>
    <label style="margin-top:10px;display:block">Prompt / Task</label>
    <textarea id="prompt" rows="5" placeholder="Test prompt or task..."></textarea>
    <div style="margin-top:10px"><button onclick="runTest()">Run Test</button></div>
  </div>

  <div class="card"><strong>Recent Runs</strong><div id="runs">{runs_html}</div></div>
</main>
<script>
async function runTest(){
 const model=document.getElementById('model').value;
 const mode=document.getElementById('mode').value;
 const prompt=document.getElementById('prompt').value;
 const r=await fetch('/run',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:`model=${encodeURIComponent(model)}&mode=${encodeURIComponent(mode)}&prompt=${encodeURIComponent(prompt)}`});
 const j=await r.json();
 location.reload();
}
</script>
</body></html>'''

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass
    def do_GET(self):
        if self.path == '/':
            opts=''.join([f'<option>{m}</option>' for m in STATE['models']])
            runs=''.join([f"<div style='margin:8px 0'><span class='pill'>{r['t']}</span><span class='pill'>{r['model']}</span><span class='pill'>{r['mode']}</span><pre>{r['prompt']}\n\nResult: {r['result']}</pre></div>" for r in STATE['runs'][-8:][::-1]]) or '<p style="color:#9db">No runs yet.</p>'
            body = HTML.format(model_options=opts, runs_html=runs)
            self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(body.encode())
        else:
            self.send_error(404)
    def do_POST(self):
        if self.path == '/run':
            ln=int(self.headers.get('Content-Length','0')); data=self.rfile.read(ln).decode(); p=parse_qs(data)
            model=p.get('model',['sonnet'])[0]; mode=p.get('mode',['quick'])[0]; prompt=p.get('prompt',[''])[0]
            result=f"Simulated {mode} run on {model}. (Wire to real subagent/API next step)"
            STATE['runs'].append({"t":time.strftime('%H:%M:%S'),"model":model,"mode":mode,"prompt":prompt[:500],"result":result})
            self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps({"ok":True}).encode())
        else:
            self.send_error(404)

if __name__=='__main__':
    socketserver.TCPServer.allow_reuse_address=True
    with socketserver.TCPServer(('',8090),H) as s:
        print('Model Lab UI on :8090')
        s.serve_forever()
