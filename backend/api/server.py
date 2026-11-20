import os
import sys
import json
import uuid
import threading
import subprocess
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from backend.video_engine.editor import VideoEditorEngine
from backend.ai_engine.planner import AIPlanner

JOBS_DB = os.path.join(ROOT, "media", "jobs.json")
os.makedirs(os.path.dirname(JOBS_DB), exist_ok=True)

engine = VideoEditorEngine(ROOT)
planner = AIPlanner(ROOT)
lock = threading.Lock()


def _safe_filename(name):
    name = str(name or "")
    name = name.replace("\\", "/").split("/")[-1]
    name = name.strip()
    if name in ("", ".", ".."):
        return "output"
    return name

def jobs():
    try:
        with open(JOBS_DB, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_job(jid, data):
    with lock:
        d = jobs()
        d[jid] = data
        tmp = JOBS_DB + ".tmp"

        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)

        os.replace(tmp, JOBS_DB)


def fmt(v):
    s = str(v or "").lower()
    return "16:9" if "landscape" in s or "16:9" in s else "9:16"


def authorized(h):
    token = os.getenv("SARAB_API_TOKEN", "").strip()
    if not token:
        return True

    import hmac
    return hmac.compare_digest(
        h.headers.get("Authorization", ""),
        "Bearer " + token
    )


class Handler(SimpleHTTPRequestHandler):

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )
        self.send_header(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()"
        )
        super().end_headers()

    def respond(self, d, c=200):
        b = json.dumps(d).encode()
        self.send_response(c)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path).path

        if p.startswith("/api/") and not authorized(self):
            return self.respond({"error": "Unauthorized"}, 401)

        if p == "/api/v1/status":
            ok = subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            ).returncode == 0

            return self.respond({
                "status": "ready" if ok else "ffmpeg_missing",
                "version": "7.0-maintained",
                "video_engine": {
                    "status": "ready" if ok else "missing",
                    "images": 0
                }
            })

        if (
            p.startswith("/api/v1/video/jobs/")
            or p.startswith("/api/v1/jobs/")
        ):
            j = jobs().get(p.rsplit("/", 1)[-1])
            return self.respond(
                j or {"error": "Job not found"},
                200 if j else 404
            )

        if p.startswith("/media/output/"):
            name = os.path.basename(
                p.split("/media/output/", 1)[-1]
            )
            path = os.path.join(ROOT, "media", "output", name)

            if not os.path.isfile(path):
                return self.respond({"error": "File not found"}, 404)

            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header(
                "Content-Length",
                str(os.path.getsize(path))
            )
            self.end_headers()

            with open(path, "rb") as f:
                for chunk in iter(
                    lambda: f.read(1024 * 1024),
                    b""
                ):
                    self.wfile.write(chunk)
            return

        if p.startswith("/api/"):
            return self.respond({"error": "Endpoint not found"}, 404)

        index = os.path.join(ROOT, "web", "index.html")

        if os.path.isfile(index):
            self.send_response(200)
            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )
            self.end_headers()

            with open(index, "rb") as f:
                self.wfile.write(f.read())
            return

        return self.respond({"error": "Not found"}, 404)

    def do_POST(self):
        if not authorized(self):
            return self.respond({"error": "Unauthorized"}, 401)

        if urlparse(self.path).path != "/api/v1/video/edit":
            return self.respond({"error": "Endpoint not found"}, 404)

        try:
            n = int(self.headers.get("Content-Length", "0"))

            if n <= 0 or n > 10 * 1024 * 1024:
                return self.respond(
                    {"error": "Invalid request size"},
                    413
                )

            data = json.loads(self.rfile.read(n))

        except (ValueError, TypeError):
            return self.respond({"error": "Invalid JSON"}, 400)

        jid = "job_" + uuid.uuid4().hex

        name = os.path.basename(
            str(
                data.get("out_name")
                or data.get("output_filename")
                or jid + ".mp4"
            )
        )[:120]

        if not name.lower().endswith(".mp4"):
            name += ".mp4"

        try:
            duration = max(
                5,
                min(600, int(float(data.get("duration", 25))))
            )
        except (ValueError, TypeError):
            return self.respond(
                {"error": "Duration must be 5-600 seconds"},
                400
            )

        format_ = fmt(data.get("format"))
        prompt = str(data.get("prompt", "")).strip()

        music = str(
            data.get("music_name")
            or data.get("online_music")
            or data.get("music")
            or ""
        )

        job = {
            "job_id": jid,
            "state": "queued",
            "progress": 0,
            "file_name": name
        }

        save_job(jid, job)

        def task():
            try:
                job.update(state="running", progress=10)
                save_job(jid, job)

                scenes = planner.fetch_ai_scenes(
                    prompt,
                    format_,
                    count=5
                )

                if not scenes:
                    raise RuntimeError(
                        "No scenes found. Add local photos or retry."
                    )

                job.update(progress=40)
                save_job(jid, job)

                audio = os.path.join(
                    ROOT,
                    "media",
                    "temp",
                    jid + ".m4a"
                )
                os.makedirs(os.path.dirname(audio), exist_ok=True)

                audio_file = planner.resolve_audio(
                    music,
                    duration,
                    audio
                )

                job.update(progress=70)
                save_job(jid, job)

                output = os.path.join(
                    ROOT,
                    "media",
                    "output",
                    name
                )
                os.makedirs(os.path.dirname(output), exist_ok=True)

                engine.compile(
                    scenes,
                    duration,
                    format_,
                    audio_file,
                    output,
                    jid
                )

                job.update(
                    state="completed",
                    progress=100,
                    output="/media/output/" + name
                )
                save_job(jid, job)

            except Exception as e:
                job.update(
                    state="failed",
                    error=str(e)[:1000]
                )
                save_job(jid, job)

        threading.Thread(
            target=task,
            daemon=True
        ).start()

        return self.respond({
            "job_id": jid,
            "status": "queued"
        })


if __name__ == "__main__":
    os.chdir(ROOT)

    ThreadingHTTPServer(
        ("0.0.0.0", int(os.getenv("PORT", "7860"))),
        Handler
    ).serve_forever()