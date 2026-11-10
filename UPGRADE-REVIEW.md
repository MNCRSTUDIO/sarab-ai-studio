# SARAB AI STUDIO 7.0 – consolidated source review

## Source baseline

The build uses the uploaded `sarab-ai-studio-v7-zero-cost.zip` as its primary baseline and checks the uploaded maintenance build and `UPGRADE-REVIEW.md` for previously identified defects. The two source ZIPs passed archive integrity checks.

## Consolidated changes

1. Replaced the mixed/duplicated API rendering path with one shared renderer: `backend/video_engine/editor.py`.
2. Made storage paths project-relative and configurable through `SARAB_ROOT`, removing the hard-coded `~/MASTER-MNCR-AI-STUDIO` dependency from the renderer.
3. Reworked the API server with `ThreadingHTTPServer`, Render `PORT` support, correct status codes, job 404 behavior, request-size limits, filename validation, API bearer-token support, POST rate limiting, security headers, and generated-output-only streaming.
4. Added validated multipart upload for JPG/JPEG/PNG/WEBP, supported local audio, and SRT subtitle files.
5. Added persistent job JSON records; a render interrupted by a server restart is reported as failed rather than left falsely running.
6. Added a one-at-a-time default render limit for low-memory environments.
7. Upgraded the single renderer profile to 720p at 12 fps for vertical and landscape slideshow output, with local music loop/trim and audio fade-out; mixed image sizes and embedded SRT subtitle tracks were also rendered successfully.
8. Connected the browser to the upload endpoint, local music selector, actual status API, asynchronous job polling, and authenticated video download.
9. Replaced the broken legacy `patch.py` with a valid retired-entry-point notice; replaced the false APK builder with a clear PWA-only notice.
10. Updated the Termux installer, Dockerfile, requirements, documentation, and test suite.
11. Removed automatic arbitrary music scraping; music must be supplied by the user with appropriate rights.
12. Disabled the misleading copyright-fingerprint evasion routine. Transcoding cannot create music/video usage rights.

## Known limitations

- AI planner and SEO metadata are rule-based/templates, not a generative model.
- No reliable AI image-generation service is integrated.
- Social uploader remains a job queue; actual OAuth and publishing are not implemented.
- No native APK build pipeline.
- The editor is a 720p/12fps slideshow renderer, not a multi-track professional NLE or 1080p/4K mastering pipeline.
- Single-owner only; no per-user storage isolation or accounts.
- Rate limiting is per-process; use a reverse proxy/WAF for public exposure.
- Render storage persistence depends on configuring a persistent disk.
- Android/Termux install was not executed on the owner's phone; live Render deployment was not performed.

See `FINAL-TEST-REPORT.md`, `SECURITY.md`, and `README.md` before deployment.
