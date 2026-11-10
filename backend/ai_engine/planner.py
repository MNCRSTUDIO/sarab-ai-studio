import os, time, subprocess, urllib.request, urllib.parse, re, glob

STREAM_AUDIO = {
    "lofi": "https://ia801503.us.archive.org/15/items/chill-lofi-song/Chill%20Lofi%20Song.mp3",
    "cinematic": "https://ia800109.us.archive.org/33/items/ambient-relaxing-music/Ambient%20Music.mp3",
    "upbeat": "https://ia600109.us.archive.org/33/items/ambient-relaxing-music/Upbeat%20Funk.mp3",
    "acoustic": "https://ia801503.us.archive.org/15/items/chill-lofi-song/Acoustic%20Guitar.mp3"
}

class AIPlanner:
    def __init__(self, root_dir):
        self.root = root_dir

    def sanitize(self, text):
        clean = re.sub(r"(?i)(generate|multiple images|video|then create|fps|slideshow)", "", str(text))
        return " ".join(clean.split()).strip() or str(text)

    def fetch_ai_scenes(self, prompt, fmt="9:16", count=5):
        clean_p = self.sanitize(prompt)
        ai_dir = os.path.join(self.root, "media", "ai_generated")
        os.makedirs(ai_dir, exist_ok=True)
        w, h = (720, 1280) if fmt == "9:16" else (1280, 720)

        angles = [
            "wide angle daylight cinematic landscape",
            "detailed close up expressive camera view",
            "aerial drone cinematic motion",
            "golden hour daylight atmospheric angle",
            "medium candid cinematic action capture"
        ]

        frames = []
        for i in range(count):
            out_img = os.path.join(ai_dir, f"scene_{int(time.time())}_{i}.jpg")
            full_prompt = f"{clean_p}, {angles[i % len(angles)]}, 8k photorealistic cinematic"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full_prompt)}?width={w}&height={h}&nologo=true&seed={int(time.time()) + i*137}"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=20) as resp, open(out_img, "wb") as f:
                    f.write(resp.read())
                if os.path.exists(out_img) and os.path.getsize(out_img) > 2000:
                    frames.append(out_img)
            except Exception:
                pass

        if not frames:
            for p in [os.path.join(self.root, "media", "photos"), "/sdcard/Pictures"]:
                if os.path.exists(p):
                    frames.extend(glob.glob(os.path.join(p, "*.jpg")))
        return frames

    def resolve_audio(self, choice, duration, target_out):
        key = str(choice).lower().strip().replace("custom:", "")
        for k, url in STREAM_AUDIO.items():
            if k in key:
                try:
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=12) as resp, open(target_out, "wb") as f:
                        f.write(resp.read())
                    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", target_out], stdout=subprocess.PIPE)
                    if p.returncode == 0 and os.path.getsize(target_out) > 5000:
                        return target_out
                except Exception:
                    pass

        for loc in [os.path.join(self.root, "media", "music"), "/sdcard/Music", "/sdcard/Download"]:
            if os.path.exists(loc):
                for ext in ("*.mp3", "*.m4a", "*.wav", "*.aac"):
                    for m in glob.glob(os.path.join(loc, ext)):
                        if key and key in os.path.basename(m).lower():
                            return m
                        if not key:
                            return m

        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi",
            "-i", f"sine=frequency=261.63:duration={duration}",
            "-af", "volume=0.32,chorus=0.7:0.9:55:0.4:0.25:2",
            "-c:a", "aac", "-b:a", "128k", target_out
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return target_out
