import os, subprocess, shutil

class VideoEditorEngine:
    def __init__(self, root_dir):
        self.root = root_dir

    def compile(self, scenes, duration, fmt, audio_path, output_path, job_id):
        temp_dir = os.path.join(self.root, "media", "temp", f"render_{job_id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        w, h = (720, 1280) if fmt == "9:16" else (1280, 720)
        seg_dur = max(3.0, float(duration) / float(len(scenes)))
        
        # Step 1: Render individual normalized visual clips
        clips = []
        for i, img in enumerate(scenes):
            c_out = os.path.join(temp_dir, f"clip_{i}.mp4")
            vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:black,setsar=1,fps=25,format=yuv420p"
            cmd = [
                "ffmpeg", "-y", "-loop", "1", "-t", str(seg_dur),
                "-i", os.path.abspath(img),
                "-vf", vf,
                "-c:v", "libx264", "-preset", "ultrafast",
                c_out
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(c_out):
                clips.append(c_out)

        # Step 2: Concat silent video track
        concat_txt = os.path.join(temp_dir, "clips.txt")
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in clips:
                f.write(f"file '{os.path.abspath(c)}'\n")

        silent_video = os.path.join(temp_dir, "silent.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
            "-c:v", "copy", silent_video
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Step 3: Clean stream mux with background audio (no desync/stream_loop crash)
        cmd_final = [
            "ffmpeg", "-y",
            "-i", silent_video,
            "-stream_loop", "-1", "-i", os.path.abspath(audio_path),
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-t", str(duration),
            "-movflags", "+faststart",
            os.path.abspath(output_path)
        ]
        res = subprocess.run(cmd_final, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"FFmpeg muxing failed: {res.stderr}")

        return output_path
