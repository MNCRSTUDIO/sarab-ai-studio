import os, sys, json, time, threading, subprocess
from http.server import HTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(ROOT)

from backend.video_engine.editor import VideoEditorEngine
from backend.ai_engine.planner import AIPlanner

JOBS_DB = os.path.join(ROOT, "media", "jobs.json")
video_engine = VideoEditorEngine(ROOT)
ai_planner = AIPlanner(ROOT)

def get_jobs():
    if os.path.exists(JOBS_DB):
        try:
            with open(JOBS_DB, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def update_job(jid, data):
    db = get_jobs()
    db[jid] = data
    with open(JOBS_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

class StudioHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _json(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/v1/status":
            self._json({"status": "ready", "version": "7.0-FINAL", "architecture": "unified"})
        elif self.path.startswith("/api/v1/jobs/"):
            jid = self.path.split("/")[-1]
            jobs = get_jobs()
            if jid in jobs:
                self._json(jobs[jid])
            else:
                self._json({"error": "Job not found"}, code=404)
        elif self.path.startswith("/media/output/"):
            clean_name = os.path.basename(self.path.split("?")[0].replace("/media/output/", ""))
            fpath = os.path.join(ROOT, "media", "output", clean_name)
            if os.path.exists(fpath):
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(os.path.getsize(fpath)))
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
                return
            self._json({"error": "File not found"}, code=404)
        else:
            idx = os.path.join(ROOT, "web", "index.html")
            if os.path.exists(idx):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(idx, "rb") as f:
                    self.wfile.write(f.read())
                return
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/v1/video/edit":
            length = int(self.headers.get("Content-Length", 0))
            if length > 10 * 1024 * 1024:
                self._json({"error": "Payload exceeds limit"}, code=413)
                return

            payload = json.loads(self.rfile.read(length).decode("utf-8")) if length > 0 else {}
            jid = f"job_{int(time.time())}"
            out_name = os.path.basename(payload.get("output_filename", f"{jid}.mp4"))
            if not out_name.endswith(".mp4"):
                out_name += ".mp4"

            dur = max(5, int(float(payload.get("duration", 25))))
            prompt = payload.get("prompt", "")
            music = payload.get("music", "lofi")
            fmt = payload.get("format", "9:16")

            job_state = {"job_id": jid, "state": "running", "progress": 15, "file_name": out_name}
            update_job(jid, job_state)

            def task():
                try:
                    out_path = os.path.join(ROOT, "media", "output", out_name)
                    job_state["progress"] = 35
                    update_job(jid, job_state)

                    scenes = ai_planner.fetch_ai_scenes(prompt, fmt, count=5)
                    job_state["progress"] = 65
                    update_job(jid, job_state)

                    target_audio = os.path.join(ROOT, "media", "temp", f"audio_{jid}.mp3")
                    os.makedirs(os.path.dirname(target_audio), exist_ok=True)
                    audio_file = ai_planner.resolve_audio(music, dur, target_audio)

                    job_state["progress"] = 85
                    update_job(jid, job_state)

                    video_engine.compile(scenes, dur, fmt, audio_file, out_path, jid)

                    job_state["state"] = "completed"
                    job_state["progress"] = 100
                    update_job(jid, job_state)

                    subprocess.run(f'cp "{out_path}" /sdcard/Download/ && am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d "file:///sdcard/Download/{out_name}"', shell=True)
                except Exception as err:
                    job_state["state"] = "failed"
                    job_state["error"] = str(err)
                    update_job(jid, job_state)

            threading.Thread(target=task, daemon=True).start()
            self._json({"job_id": jid, "status": "queued"})
        else:
            self._json({"error": "Endpoint not found"}, code=404)

if __name__ == "__main__":
    os.chdir(ROOT)
    server = HTTPServer(("0.0.0.0", 7860), StudioHandler)
    print("SARAB AI STUDIO 7.0 PROD ACTIVE: http://127.0.0.1:7860")
    server.serve_forever()
