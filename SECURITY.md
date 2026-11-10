# Security notes for SARAB AI STUDIO 7.0

## Required before public deployment

1. Set `SARAB_API_TOKEN` to a long random secret in the Render environment. Never commit it.
2. Use HTTPS (Render's HTTPS endpoint is expected). Do not expose the built-in server directly on an untrusted network without a reverse proxy.
3. Keep the app single-owner. The current build does not implement per-user accounts or per-user media isolation.
4. Configure a persistent disk if uploaded media and job history must survive Render restarts/redeploys.
5. Keep upload size limits conservative. The default request body limit is 60 MiB; each accepted file is limited to 30 MiB.
6. Use only media you own or are licensed to use. The application does not bypass copyright detection.
7. Do not store API credentials or OAuth token files inside the ZIP or public repository.

## Implemented controls

- Optional bearer-token authentication for API endpoints and generated video downloads.
- Constant-time API token comparison.
- Per-process request rate limit for POST endpoints.
- Request body size limit.
- Extension allowlist and content validation for images, audio signatures, and UTF-8 SRT files.
- Sanitized upload/output filenames and fixed storage directories.
- Generated-output-only file serving with streaming response.
- Correct 404 for unknown job IDs.
- Security headers including `nosniff`, frame denial, restrictive permissions, referrer policy, and CSP compatible with the current inline UI.

## Remaining limitations

- Rate limiting is in-memory and resets on process restart; it is not a distributed WAF.
- This is a single-owner application, not a multi-tenant SaaS. Do not give the API token to other users.
- No malware scanning is included. FFmpeg/Pillow parsing of uploaded files still has dependency-level risk; keep dependencies updated.
- Native server TLS is not provided; terminate HTTPS at Render/reverse proxy.
- Social OAuth/publishing is not implemented in this build.
