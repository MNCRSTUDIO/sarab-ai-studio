import os, time, subprocess, urllib.request, urllib.parse, re, glob

# Free-plan, privacy-first audio policy: never scrape or stream third-party tracks.
# Users can add music they own or are licensed to use in media/music.
STREAM_AUDIO = {}


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
            for p in [os.path.join(self.root, "media", "input"), os.path.join(self.root, "media", "photos"), "/sdcard/Pictures"]:
                if os.path.exists(p):
                    frames.extend(glob.glob(os.path.join(p, "*.jpg")) + glob.glob(os.path.join(p, "*.jpeg")) + glob.glob(os.path.join(p, "*.png")) + glob.glob(os.path.join(p, "*.webp")))
        return frames

    def resolve_audio(self, choice, duration, target_out):
        """Use only a matching local, user-supplied track; otherwise create silence."""
        key = str(choice or "").strip().lower()
        search_dirs = [os.path.join(self.root, "media", "music"), "/sdcard/Music", "/sdcard/Download"]
        audio_exts = ("*.mp3", "*.m4a", "*.wav", "*.aac", "*.ogg", "*.flac")
        for loc in search_dirs:
            if not os.path.isdir(loc):
                continue
            for pattern in audio_exts:
                for path in sorted(glob.glob(os.path.join(loc, pattern))):
                    if key and key not in os.path.basename(path).lower():
                        continue
                    return path
        # No music selected/found: produce a silent AAC track, not an artificial tone.
        os.makedirs(os.path.dirname(target_out) or ".", exist_ok=True)
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-t", str(max(1, int(duration))), "-c:a", "aac", "-b:a", "96k", target_out
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return target_out if result.returncode == 0 and os.path.isfile(target_out) else None



def create_video_plan(prompt, platform="instagram", duration=30):
    prompt = str(prompt or "").strip()
    if not prompt:
        raise ValueError("A video prompt is required")

    try:
        duration = max(5, min(int(duration), 300))
    except (TypeError, ValueError):
        duration = 30

    platform = str(platform or "instagram").lower().strip()
    vertical_platforms = ("instagram", "reels", "youtube_shorts", "shorts", "tiktok")

    if platform in vertical_platforms:
        fmt = "9:16 vertical"
    else:
        fmt = "16:9 horizontal"

    return {
        "prompt": prompt,
        "platform": platform,
        "duration": duration,
        "format": fmt,
        "generated_by": "local rule-based planner (not generative AI)",
        "scenes": [
            {"scene": 1, "description": "Opening shot: " + prompt},
            {"scene": 2, "description": "Main subject and story: " + prompt},
            {"scene": 3, "description": "Closing shot and call to action: " + prompt}
        ]
    }
