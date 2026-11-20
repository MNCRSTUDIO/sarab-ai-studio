import os
import subprocess


class VideoEditorEngine:

    def __init__(self, root_dir):
        self.root = root_dir

    def compile(
        self,
        scenes,
        duration,
        fmt,
        audio_path,
        output_path,
        job_id
    ):
        if not scenes:
            raise ValueError("No scenes supplied")

        if not audio_path or not os.path.isfile(audio_path):
            raise FileNotFoundError("Audio unavailable")

        temp = os.path.join(
            self.root,
            "media",
            "temp",
            "render_" + job_id
        )
        os.makedirs(temp, exist_ok=True)

        w, h = (
            (720, 1280)
            if fmt == "9:16"
            else (1280, 720)
        )

        seg = float(duration) / len(scenes)
        clips = []

        for i, img in enumerate(scenes):

            if not os.path.isfile(img):
                continue

            out = os.path.join(
                temp,
                f"clip_{i}.mp4"
            )

            vf = (
                f"scale={w}:{h}:"
                "force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,"
                "setsar=1,fps=12,format=yuv420p"
            )

            cmd = [
                "ffmpeg",
                "-y",
                "-loop", "1",
                "-t", str(seg),
                "-i", os.path.abspath(img),
                "-vf", vf,
                "-c:v", "libx264",
                "-preset", "ultrafast",
                "-pix_fmt", "yuv420p",
                out
            ]

            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )

            if r.returncode != 0:
                raise RuntimeError(
                    "Clip render failed: "
                    + r.stderr[-1000:]
                )

            clips.append(out)

        if not clips:
            raise RuntimeError("No valid clips")

        listing = os.path.join(
            temp,
            "clips.txt"
        )

        with open(
            listing,
            "w",
            encoding="utf-8"
        ) as f:

            for c in clips:
                safe_path = (
                    c.replace("\\", "\\\\")
                    .replace("'", "\\'")
                )
                f.write(
                    "file '" + safe_path + "'\n"
                )

        silent = os.path.join(
            temp,
            "silent.mp4"
        )

        r = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f", "concat",
                "-safe", "0",
                "-i", listing,
                "-c", "copy",
                silent
            ],
            capture_output=True,
            text=True
        )

        if r.returncode != 0:
            raise RuntimeError(
                "Concat failed: "
                + r.stderr[-1000:]
            )

        os.makedirs(
            os.path.dirname(output_path),
            exist_ok=True
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i", silent,
            "-stream_loop", "-1",
            "-i", os.path.abspath(audio_path),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100",
            "-t", str(duration),
            "-movflags", "+faststart",
            os.path.abspath(output_path)
        ]

        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if r.returncode != 0:
            raise RuntimeError(
                "Audio mux failed: "
                + r.stderr[-1000:]
            )

        return output_path