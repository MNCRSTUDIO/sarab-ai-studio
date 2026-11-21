import os,sys,json,uuid,threading,subprocess,hmac,secrets,re
from pathlib import Path
from http.server import ThreadingHTTPServer,SimpleHTTPRequestHandler
from urllib.parse import urlparse
from email.parser import BytesParser
from email.policy import default

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.video_engine.editor import VideoEditorEngine
from backend.ai_engine.planner import AIPlanner, create_video_plan
from backend.ai_engine.metadata import generate_seo_metadata

BASE=ROOT/"media"
for d in ("input","photos","music","subtitles","output","temp","ai_generated","logs"):
    (BASE/d).mkdir(parents=True,exist_ok=True)
DB=BASE/"jobs.json"
TOKEN=os.getenv("SARAB_API_TOKEN","").strip()
TOKENFILE=BASE/".access_token"
if not TOKEN:
    if TOKENFILE.exists(): TOKEN=TOKENFILE.read_text().strip()
    else:
        TOKEN=secrets.token_urlsafe(32)
        TOKENFILE.write_text(TOKEN)
    try: TOKENFILE.chmod(0o600)
    except Exception: pass
if not TOKEN:
    raise RuntimeError("SARAB_API_TOKEN or a non-empty media/.access_token is required")
lock=threading.Lock()
rate_lock=threading.Lock()
post_hits={}
POST_LIMIT=30
POST_WINDOW=60
MAX_FILE_BYTES=25*1024*1024

def allowed_post(client):
    now=__import__("time").time()
    with rate_lock:
        hits=[t for t in post_hits.get(client,[]) if now-t < POST_WINDOW]
        if len(hits) >= POST_LIMIT:
            post_hits[client]=hits
            return False
        hits.append(now); post_hits[client]=hits
        return True

def valid_upload(ext, data):
    if ext in (".jpg", ".jpeg"):
        return data.startswith(b"\xff\xd8\xff")
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    if ext == ".wav":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    if ext == ".mp3":
        return data.startswith(b"ID3") or (len(data) > 1 and data[0] == 0xff and (data[1] & 0xe0) == 0xe0)
    if ext in (".m4a", ".aac"):
        return (len(data) >= 8 and data[4:8] == b"ftyp") or (len(data) > 1 and data[0] == 0xff and (data[1] & 0xf6) == 0xf0)
    if ext == ".ogg": return data.startswith(b"OggS")
    if ext == ".flac": return data.startswith(b"fLaC")
    if ext == ".srt":
        try:
            text=data.decode("utf-8-sig")
            return bool(re.search(r"(?m)^\s*\d+\s*\n\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}\s+-->\s+", text))
        except UnicodeDecodeError: return False
    return False

engine=VideoEditorEngine(str(ROOT))
planner=AIPlanner(str(ROOT))
def safe(n):
    n=str(n or "file").replace("\\","/").split("/")[-1]
    n=re.sub(r"[^A-Za-z0-9._ -]","_",n).strip(" .")
    return n or "file"

_safe_filename = safe
def jobs():
    try:
        x=json.loads(DB.read_text()); return x if isinstance(x,dict) else {}
    except Exception: return {}
def save(jid,j):
    with lock:
        x=jobs(); x[jid]=j
        tmp=DB.with_suffix(".tmp"); tmp.write_text(json.dumps(x,indent=2))
        os.replace(tmp,DB)
def auth(h):
    return hmac.compare_digest(h.headers.get("Authorization",""),"Bearer "+TOKEN)
def jsonout(h,x,c=200):
    b=json.dumps(x,ensure_ascii=False).encode()
    h.send_response(c); h.send_header("Content-Type","application/json; charset=utf-8")
    h.send_header("Content-Length",str(len(b))); h.end_headers(); h.wfile.write(b)
def listing(folder,exts):
    return sorted(x.name for x in (BASE/folder).iterdir() if x.is_file() and x.suffix.lower() in exts)
class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("X-Frame-Options","DENY")
        self.send_header("Referrer-Policy","strict-origin-when-cross-origin")
        self.send_header("Permissions-Policy","camera=(), microphone=(), geolocation=()")
        super().end_headers()
    def check(self):
        if not auth(self):
            jsonout(self,{"error":"Unauthorized"},401); return False
        return True
    def do_GET(self):
        p=urlparse(self.path).path
        if (p.startswith("/api/") or p.startswith("/media/output/")) and not self.check(): return
        if p=="/api/v1/media":
            items=[]
            for folder,category,exts in (("input","image",{".jpg",".jpeg",".png",".webp"}),("music","audio",{".mp3",".wav",".m4a",".aac",".ogg",".flac"}),("subtitles","subtitle",{".srt"})):
                for name in listing(folder,exts):
                    item=BASE/folder/name
                    items.append({"name":name,"category":category,"size_bytes":item.stat().st_size})
            jsonout(self,{"items":items}); return
        if p=="/api/v1/status":
            ok=subprocess.run(["ffmpeg","-version"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
            jsonout(self,{"status":"ready" if ok else "ffmpeg_missing","ffmpeg":ok,"video_engine":{"status":"ready" if ok else "missing","images":len(listing("input",{".jpg",".jpeg",".png",".webp"}))},"generative_video":False}); return
        if p=="/api/v1/music":
            names=listing("music",{".mp3",".wav",".m4a",".aac",".ogg",".flac"})
            jsonout(self,{"items":[{"name":n} for n in names],"music":names}); return
        if p=="/api/v1/subtitles":
            names=listing("subtitles",{".srt"})
            jsonout(self,{"items":[{"name":n} for n in names],"subtitles":names}); return
        if p.startswith("/api/v1/video/jobs/") or p.startswith("/api/v1/jobs/"):
            jid=p.rsplit("/",1)[-1]; j=jobs().get(jid)
            jsonout(self,j or {"error":"Job not found"},200 if j else 404); return
        if p.startswith("/media/output/"):
            f=BASE/"output"/safe(p.rsplit("/",1)[-1])
            if not f.is_file(): jsonout(self,{"error":"Not found"},404); return
            self.send_response(200); self.send_header("Content-Type","video/mp4"); self.send_header("Content-Length",str(f.stat().st_size)); self.send_header("Cache-Control","no-store"); self.send_header("Content-Disposition",'attachment; filename="'+f.name+'"'); self.end_headers()
            with f.open("rb") as stream:
                for chunk in iter(lambda:stream.read(1024*1024),b""): self.wfile.write(chunk)
            return
        if p.startswith("/api/"): jsonout(self,{"error":"Not found"},404); return
        if p in ("/manifest.json", "/sw.js", "/logo.png"):
            asset=ROOT/"web"/p.lstrip("/")
            if asset.is_file():
                content_type={".json":"application/manifest+json", ".js":"application/javascript", ".png":"image/png"}.get(asset.suffix.lower(),"application/octet-stream")
                body=asset.read_bytes(); self.send_response(200); self.send_header("Content-Type",content_type); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body); return
            jsonout(self,{"error":"Not found"},404); return
        f=ROOT/"web"/"index.html"
        if f.is_file():
            b=f.read_bytes(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        jsonout(self,{"error":"Not found"},404)
    def do_POST(self):
        if not self.check(): return
        if not allowed_post(self.client_address[0]):
            jsonout(self,{"error":"Too many requests. Wait one minute and try again."},429); return
        p=urlparse(self.path).path
        try: n=int(self.headers.get("Content-Length","0"))
        except: n=0
        if n<=0 or n>60*1024*1024: jsonout(self,{"error":"Request too large or invalid (60MB limit)"},413); return
        raw=self.rfile.read(n)
        if p=="/api/v1/media/upload":
            ct=self.headers.get("Content-Type","")
            if "multipart/form-data" not in ct: jsonout(self,{"error":"Multipart expected"},400); return
            try:
                msg=BytesParser(policy=default).parsebytes(b"Content-Type: "+ct.encode()+b"\r\nMIME-Version: 1.0\r\n\r\n"+raw)
                result=[]
                for part in msg.iter_parts():
                    fn=part.get_filename()
                    if not fn: continue
                    name=safe(fn); ext=Path(name).suffix.lower()
                    if ext in (".jpg",".jpeg",".png",".webp"): folder="input"
                    elif ext in (".mp3",".wav",".m4a",".aac",".ogg",".flac"): folder="music"
                    elif ext==".srt": folder="subtitles"
                    else: continue
                    data=part.get_payload(decode=True) or b""
                    if not data: continue
                    if len(data) > MAX_FILE_BYTES:
                        jsonout(self,{"error":"Each uploaded file must be 25 MB or smaller."},413); return
                    if not valid_upload(ext,data):
                        jsonout(self,{"error":"File content does not match its allowed file type: "+name},415); return
                    dest=BASE/folder/name
                    if dest.exists(): dest=BASE/folder/(Path(name).stem+"_"+uuid.uuid4().hex[:6]+ext)
                    dest.write_bytes(data); result.append({"name":dest.name,"category":folder})
                jsonout(self,{"uploaded":result}); return
            except Exception as e: jsonout(self,{"error":str(e)[:300]},400); return
        if p not in ("/api/v1/video/edit","/api/v1/ai/plan","/api/v1/ai/metadata"):
            jsonout(self,{"error":"Not found"},404); return
        try: data=json.loads(raw)
        except: jsonout(self,{"error":"Invalid JSON"},400); return
        if p=="/api/v1/ai/plan":
            try:
                jsonout(self,create_video_plan(data.get("prompt",""),data.get("platform","instagram"),data.get("duration",30)))
            except Exception as e:
                jsonout(self,{"error":str(e)[:300]},400)
            return
        if p=="/api/v1/ai/metadata":
            jsonout(self,generate_seo_metadata(data.get("topic","Video")))
            return
        try: duration=max(5,min(600,int(float(data.get("duration",25)))))
        except: jsonout(self,{"error":"Duration must be 5-600"},400); return
        name=safe(data.get("out_name") or data.get("output_filename") or ("video_"+uuid.uuid4().hex[:8]+".mp4"))
        if not name.lower().endswith(".mp4"): name+=".mp4"
        if (BASE/"output"/name).exists():
            name=Path(name).stem+"_"+uuid.uuid4().hex[:6]+".mp4"
        jid="job_"+uuid.uuid4().hex
        j={"job_id":jid,"state":"queued","progress":0,"file_name":name}
        save(jid,j)
        prompt=str(data.get("prompt","")).strip()
        music=str(data.get("music_name") or data.get("online_music") or data.get("music") or "")
        fmt="9:16" if "9:16" in str(data.get("format","")) or "vertical" in str(data.get("format","")).lower() else "16:9"
        def work():
            try:
                j.update(state="running",progress=10); save(jid,j)
                # Deterministic local-first mode: an empty prompt uses the user's uploaded photos.
                scenes=[]
                local_scenes=[str(x) for x in sorted(list((BASE/"input").glob("*"))+list((BASE/"photos").glob("*"))) if x.is_file() and x.suffix.lower() in (".jpg",".jpeg",".png",".webp")]
                # No prompt is sent to an external service by default. Remote image
                # generation is opt-in via SARAB_ALLOW_REMOTE_AI=1 only.
                if prompt and os.getenv("SARAB_ALLOW_REMOTE_AI", "0").strip() == "1":
                    try: scenes=planner.fetch_ai_scenes(prompt,fmt,count=5)
                    except Exception: pass
                if not scenes: scenes=local_scenes
                if not scenes: raise RuntimeError("Upload photos first; no usable scenes found.")
                j.update(progress=40); save(jid,j)
                audio=BASE/"temp"/(jid+".m4a")
                audiofile=planner.resolve_audio(music,duration,str(audio))
                if not audiofile or not os.path.isfile(audiofile): raise RuntimeError("Audio could not be prepared")
                j.update(progress=70); save(jid,j)
                subtitle_name=safe(data.get("subtitle_name","")) if data.get("subtitle_name") else ""
                subtitle_path=(BASE/"subtitles"/subtitle_name) if subtitle_name else None
                if subtitle_path and (not subtitle_path.is_file() or subtitle_path.suffix.lower()!=".srt"):
                    raise RuntimeError("Selected subtitle file was not found in media/subtitles.")
                output=BASE/"output"/name
                engine.compile(scenes,duration,fmt,audiofile,str(output),jid, str(subtitle_path) if subtitle_path else None)
                j.update(state="completed",progress=100,output="/media/output/"+name,file_name=name); save(jid,j)
            except Exception as e:
                j.update(state="failed",error=str(e)[:1000]); save(jid,j)
        threading.Thread(target=work,daemon=True).start()
        jsonout(self,{"job_id":jid,"status":"queued"})
if __name__=="__main__":
    os.chdir(ROOT)
    print("SARAB AI STUDIO: private access enabled (token value is not printed).",flush=True)
    print("Token file:",str(TOKENFILE),flush=True)
    print("Server listening at port",os.getenv("PORT","7860"),flush=True)
    ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT","7860"))),Handler).serve_forever()
