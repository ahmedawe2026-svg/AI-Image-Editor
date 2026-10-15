import json, os, tempfile, uuid
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
from urllib.request import Request, urlopen
import urllib.error

ROOT=os.path.dirname(os.path.abspath(__file__))
COMFY=os.environ.get("COMFY_URL","http://127.0.0.1:8188")

class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw): super().__init__(*a,directory=ROOT,**kw)
    def send_json(self,obj,code=200):
        raw=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type","application/json; charset=utf-8")
        self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/api/comfy/status":
            try:
                r=urlopen(COMFY+"/system_stats",timeout=2)
                self.send_json({"ok":r.status==200,"url":COMFY})
            except Exception: self.send_json({"ok":False,"url":COMFY})
            return
        super().do_GET()
    def do_POST(self):
        if self.path!="/api/edit": self.send_json({"message":"Not found"},404); return
        # V5 transport layer: accept multipart input and prompt; actual workflow execution
        # is intentionally delegated to a local ComfyUI workflow configured by the user.
        length=int(self.headers.get("Content-Length","0"))
        body=self.rfile.read(length)
        self.send_json({"ok":False,"message":"طبقة الربط جاهزة، لكن لم يتم تثبيت Workflow/Model محلي بعد. شغّل ComfyUI ثم ضع Workflow متوافقًا في workflows/."},501)
    def log_message(self,fmt,*args): print(fmt%args)

if __name__=="__main__":
    print("AI Image Editor V5 — http://127.0.0.1:8765")
    ThreadingHTTPServer(("127.0.0.1",8765),Handler).serve_forever()
