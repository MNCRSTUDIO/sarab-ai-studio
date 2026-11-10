Run unit checks from the project root:

```bash
python -m unittest discover -s tests -v
```

Run the FFmpeg smoke test manually by uploading a few images and optional licensed audio through the web UI, or place them in `media/input` and `media/music`, start the server, and submit a 5-second render. Verify the resulting MP4 with `ffprobe`.
