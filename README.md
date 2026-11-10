# SARAB AI STUDIO 7.0 – consolidated maintenance release

This release consolidates the supplied V7 and maintenance sources around one API and one FFmpeg slideshow renderer. It preserves the existing web interface and adds a supported upload path, safer API handling, project-relative paths, persistent job records, and a Termux installer.

## Included in this build

- One shared renderer: `backend/video_engine/editor.py`, called by `/api/v1/video/edit`.
- Render duration validation (5–600 seconds), unique output naming, progress tracking, and persistent job records under `logs/jobs/`.
- 720p vertical (720×1280) or landscape (1280×720) output at 12 fps, H.264/AAC, with blurred background fill and local music loop/trim.
- Browser upload for photos, local music, and SRT subtitle files.
- Upload type/size limits, sanitized filenames, API rate limiting, optional bearer-token authentication, and security response headers.
- Correct 404 for unknown jobs; generated output only is served from `/media/output/`.
- `PORT` support for Render and project-relative storage paths for Docker/Termux.
- Valid Python packaging metadata and a one-command Termux installer.

## Termux installation

Extract the ZIP, enter the project directory, then run:

```bash
bash install_termux.sh
bash start.sh
```

The installer creates a full pre-install backup in `~/SARAB-AI-STUDIO-backups/`. Use `bash backup_restore.sh backup` for a manual backup or `bash backup_restore.sh restore /path/to/archive.tar.gz` to restore. Open `http://127.0.0.1:7860` in the Android browser. Grant storage access when prompted. Upload photos, optional licensed audio, and SRT subtitle files using the upload panel. You may also copy files directly into `media/input/` and `media/music/`.

## Render / Docker

The Dockerfile installs FFmpeg and Python dependencies. Render should use the Docker environment or a Python environment with FFmpeg installed. The server listens on the platform `PORT` variable.

Before public exposure, configure `SARAB_API_TOKEN` in the hosting provider's environment settings. Enter the same token in the studio's API access token field. Never commit `.env`, API keys, OAuth secrets, or user tokens.

## API endpoints

- `GET /api/v1/status`
- `GET /api/v1/media`
- `GET /api/v1/music`
- `GET /api/v1/subtitles`
- `POST /api/v1/media/upload` (multipart form-data; images/audio/SRT)
- `POST /api/v1/video/edit` (JSON: `out_name`, `duration`, `format`, optional `music_name` and `subtitle_name`)
- `GET /api/v1/video/jobs/{job_id}`
- `GET /media/output/{filename}`
- `POST /api/v1/ai/plan` (local rule-based plan, not generative AI)
- `POST /api/v1/ai/metadata` (template SEO metadata)

## Honest feature boundaries

- The planner and SEO metadata generator are deterministic/rule-based templates, not a hosted generative AI model.
- Image generation is not implemented as a reliable first-party service in this source package.
- Social publishing is not implemented. The current social uploader only queues jobs; real YouTube/Instagram/Facebook publishing requires platform OAuth, permissions, app review, and account configuration.
- The project does not build a native Android APK. It is a browser/PWA application.
- Music recommendations in the interface are suggestions, not licensed audio files. Upload audio you own or are licensed to use. The renderer uses local music files only and does not scrape YouTube or download arbitrary songs.
- The renderer is a low-resource 720p / 12 fps slideshow pipeline, not a 1080p/4K multi-track professional NLE.
- In-memory rate limiting is per process; this is not a substitute for a reverse proxy/WAF or a persistent multi-worker job queue.
- Render's ephemeral filesystem may be reset on redeploy/restart unless a persistent disk is configured. Configure persistent storage before relying on long-term media/job retention.

## Verification

Run:

```bash
python -m py_compile backend/api/server.py backend/video_engine/engine.py backend/video_engine/editor.py backend/ai_engine/planner.py backend/ai_engine/metadata.py smart_audio.py generate_thumbnail.py patch.py
python -m unittest discover -s tests -v
```

A successful syntax/unit test is not proof of a successful production deployment. Perform an end-to-end render using actual uploaded media in the target Termux/Render environment before switching the live service.
