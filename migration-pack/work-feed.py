#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, html, os, json, datetime

WS="/home/m1ndb0t/Desktop/J1MSKY"

PAGE='''<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1" />
<title>jimsky Work Feed</title>
<style>
body{font-family:Arial;background:#0b0f14;color:#e6f1ff;margin:0;padding:16px}
.card{background:#111a2b;border:1px solid #223;border-radius:10px;padding:14px;margin-bottom:12px}
h2{margin:0 0 8px 0}.muted{color:#9db;font-size:12px}
pre{white-space:pre-wrap;background:#0b1422;border:1px solid #334;border-radius:8px;padding:10px;max-height:320px;overflow:auto}
a{color:#67e8f9}
</style></head><body>
<div class="card"><h2>◈ jimsky Work Feed</h2><div class="muted">Live snapshot of what I’m doing + recent outputs</div></div>
<div class="card"><h3>Recent Commits</h3><pre>{commits}</pre></div>
<div class="card"><h3>Recent Logs</h3><pre>{logs}</pre></div>
<div class="card"><h3>Quick Links</h3>
<a href="http://127.0.0.1:8080">Office Dashboard</a> · 
<a href="http://127.0.0.1:8092">Alexa Command Center</a> · 
<a href="/api/status">API Status JSON</a>
</div>
</body></html>'''

class H(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass
    def _json(self,code,obj):
        self.send_response(code); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(json.dumps(obj).encode())
    def do_GET(self):
        if self.path == '/api/status':
            now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commits=self._git_commits(8)
            logs=self._logs(30)
            return self._json(200,{"ok":True,"time":now,"commits":commits,"logs":logs})
        commits='\n'.join(self._git_commits(10))
        logs='\n'.join(self._logs(40))
        body=PAGE.format(commits=html.escape(commits), logs=html.escape(logs))
        self.send_response(200); self.send_header('Content-Type','text/html'); self.end_headers(); self.wfile.write(body.encode())
    def _git_commits(self,n):
        try:
            out=subprocess.check_output(['bash','-lc',f'cd {WS} && git log --oneline -n {n}'],text=True)
            return [l for l in out.splitlines() if l.strip()]
        except Exception as e:
            return [f'git log unavailable: {e}']
    def _logs(self,n):
        files=['/tmp/j1msky-agency.log','/tmp/alexa-bridge.log','/tmp/alexa-cmd-center.log','/home/m1ndb0t/Desktop/J1MSKY/logs/command-audit.log']
        out=[]
        for p in files:
            if os.path.exists(p):
                try:
                    with open(p,'r',errors='ignore') as f:
                        lines=f.readlines()[-max(1,n//len(files)):]
                        out.append(f'--- {p} ---')
                        out.extend([x.rstrip()[:180] for x in lines if x.strip()])
                except Exception as e:
                    out.append(f'{p}: {e}')
        return out or ['No logs yet']

if __name__=='__main__':
    HTTPServer(('0.0.0.0',8093),H).serve_forever()
