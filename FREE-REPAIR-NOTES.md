# SARAB AI STUDIO — Free Plan Repair Overlay

This overlay is based on the uploaded `SARAB-AI-STUDIO-AUDIT-NOW.tar.gz` source archive.

## Changes in this overlay

- API routes and generated-video downloads continue to require the bearer token.
- Existing token files are restricted to owner read/write permissions where supported; the token value is never printed.
- POST requests are rate-limited to 30 per client IP per 60 seconds (in-memory; resets on restart).
- Uploads are limited to 25 MiB per file and checked against basic file signatures (image/audio) or UTF-8 SRT timestamp structure.
- Browser PWA manifest and service-worker assets are served from their actual files instead of returning the HTML page.
- Remote AI image generation is disabled by default. Prompts stay local unless the owner explicitly sets `SARAB_ALLOW_REMOTE_AI=1`.
- Automatic third-party music downloads are removed. A selected local audio file is used; if none is selected/found, a silent audio track is generated. Upload only music you own or are licensed to use.
- The rule-based planner and template SEO remain rule-based; no paid API is added.

## Verified here

- Python compilation passed for server, planner, editor, and generator.
- 10 unit tests passed, including upload-signature checks, SRT validation, and POST rate-limit behavior.

## Important limitations

- This is still a local-photo slideshow renderer, not a generative AI video model or professional multi-track editor.
- AI image generation remains off by default and is not guaranteed free or unlimited.
- Social media publishing remains a queue/placeholder; no real platform OAuth or automatic upload is added.
- No native Android APK build pipeline is added; the browser app remains a PWA.
- Rate limiting is per-process and is not a replacement for a production WAF.
- A live Render deployment and installation on the owner's phone have not been tested by this repair build.

## Installation

Extract the ZIP into the existing project root, allowing it to replace only the included source/test/docs files. Do not delete `media/`, `.access_token`, uploaded photos, music, subtitles, or rendered output. Then run the validation commands provided in the ChatGPT conversation.
