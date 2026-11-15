"""Run the midpoint app at http://127.0.0.1:8000 with Python 3.11+."""
import argparse
import json
import mimetypes
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from trip_planner.catalog import Catalog
from trip_planner.claude import ModelError
from trip_planner.config import load_settings
from trip_planner.models import InputError
from trip_planner.planner import plan

ROOT=Path(__file__).resolve().parent
STATIC={"/":"index.html","/app.js":"app.js","/style.css":"style.css","/boston.jpg":"boston.jpg"}

class Handler(BaseHTTPRequestHandler):
    catalog=None

    def send(self,code,body,content_type="application/json; charset=utf-8"):
        data=json.dumps(body,ensure_ascii=False).encode() if isinstance(body,(dict,list)) else body
        self.send_response(code)
        self.send_header("Content-Type",content_type)
        self.send_header("Content-Length",str(len(data)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path=urlparse(self.path).path
        if path=="/api/config":
            return self.send(200,{"provider":os.getenv("PLANNER_PROVIDER","local"),
                "claude_key_configured":bool(os.getenv("ANTHROPIC_API_KEY")),
                "snapshot_date":self.catalog.snapshot["checked_at"],
                "checked_places":len(self.catalog.checked),"historical_records":len(self.catalog.places)})
        if path=="/health":
            return self.send(200,{"status":"ok"})
        if path not in STATIC:
            return self.send(404,{"error":"Page not found."})
        file=ROOT/"web"/STATIC[path]
        self.send(200,file.read_bytes(),mimetypes.guess_type(file.name)[0] or "application/octet-stream")

    def do_POST(self):
        if self.path!="/api/plan":
            return self.send(404,{"error":"Endpoint not found."})
        allowed={f"http://127.0.0.1:{self.server.server_port}",f"http://localhost:{self.server.server_port}"}
        origin=self.headers.get("Origin")
        if origin and origin not in allowed:
            return self.send(403,{"error":"Use the local app to make a plan."})
        if self.headers.get_content_type()!="application/json":
            return self.send(415,{"error":"Send application/json."})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=32768:
                return self.send(413,{"error":"The request is empty or too large."})
            value=json.loads(self.rfile.read(length))
            return self.send(200,plan(value,self.catalog))
        except (InputError,ValueError,UnicodeDecodeError) as exc:
            return self.send(400,{"error":str(exc)})
        except ModelError as exc:
            return self.send(502,{"error":str(exc)})
        except Exception:
            # Avoid sending environment values or local paths to the browser.
            return self.send(500,{"error":"The local planner failed. Please check the request and try again."})

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port",type=int,default=8000)
    parser.add_argument("--open-browser",action="store_true")
    args=parser.parse_args()
    load_settings()
    Handler.catalog=Catalog()
    server=ThreadingHTTPServer(("127.0.0.1",args.port),Handler)
    print(f"Massachusetts Trip Planner: http://127.0.0.1:{args.port}",flush=True)
    print(f"Planner: {os.getenv('PLANNER_PROVIDER','local')}. Press Ctrl+C to stop.",flush=True)
    if args.open_browser:
        webbrowser.open(f"http://127.0.0.1:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__=="__main__":
    main()
