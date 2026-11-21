import os
import re
import json
import subprocess


def _safe_name(name):
    name = str(name or "video").replace("\\", "/").split("/")[-1]
    name = re.sub(r"[^a-zA-Z0-9._ -]", "_", name)
    name = name.strip(" .")
    if not name or name in (".", ".."):
        name = "video"
    if not name.lower().endswith(".mp4"):
        name += ".mp4"
    return name


def get_job(job_id):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    path = os.path.join(root, "media", "jobs.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data.get(job_id)
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("id") == job_id:
                    return item
    except (OSError, ValueError, TypeError):
        pass
    return None


class VideoEditorEngine:

    def __init__(self, root_dir):
        self.root = root_dir

    def compile(self, scenes, duration, fmt, audio_path, output_path, job_id, subtitle_path=None):
        if not scenes:
            raise ValueError("No scenes supplied")
        if not audio_path or not os.path.isfile(audio_path):
            raise FileNotFoundError("Audio unavailable")

        temp = os.path.join(self.root, "media", "temp", "render_" + str(job_id))
        os.makedirs(temp, exist_ok=True)

        w, h = (720, 1280) if fmt == "9:16" else (1280, 720)
        seg = float(duration) / len(scenes)
        clips = []

        for i, img in enumerate(scenes):
            if not os.path.isfile(img):
                continue

            out = os.path.join(temp, f"clip_{i}.mp4")
            vf = (
                f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
                "setsar=1,fps=12,format=yuv420p"
            )
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-t", str(seg),
                "-i", os.path.abspath(img), "-vf", vf,
                "-c:v", "libx264", "-preset", "ultrafast",
                "-pix_fmt", "yuv420p", out
            ]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0:
                raise RuntimeError("Clip render failed: " + r.stderr[-1000:])
            clips.append(out)

        if not clips:
            raise RuntimeError("No valid clips")

        listing = os.path.join(temp, "clips.txt")
        with open(listing, "w", encoding="utf-8") as f:
            for c in clips:
                safe_path = c.replace("\\", "\\\\").replace("'", "\\'")
                f.write("file '" + safe_path + "'\n")

        silent = os.path.join(temp, "silent.mp4")
        r = subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
             "-i", listing, "-c", "copy", silent],
            capture_output=True, text=True
        )
        if r.returncode != 0:
            raise RuntimeError("Concat failed: " + r.stderr[-1000:])

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-i", silent,
               "-stream_loop", "-1", "-i", os.path.abspath(audio_path)]
        if subtitle_path:
            if not os.path.isfile(subtitle_path) or not subtitle_path.lower().endswith(".srt"):
                raise FileNotFoundError("Selected SRT subtitle file was not found.")
            # Escape characters meaningful to FFmpeg's filter parser.
            sub = os.path.abspath(subtitle_path).replace("\\\\", "\\\\\\\\").replace(":", "\\\\:").replace("'", "\\\\'").replace(",", "\\\\,").replace("[", "\\\\[").replace("]", "\\\\]")
            cmd += ["-vf", "subtitles='" + sub + "':force_style='FontSize=22,Outline=2,Shadow=1,MarginV=40'"]
            cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p"]
        else:
            cmd += ["-c:v", "copy"]
        cmd += ["-map", "0:v:0", "-map", "1:a:0",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-t", str(duration), "-movflags", "+faststart",
                os.path.abspath(output_path)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("Audio mux failed: " + r.stderr[-1000:])

        return output_path
