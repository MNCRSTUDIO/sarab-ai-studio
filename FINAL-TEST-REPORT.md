# SARAB AI STUDIO 7.0 – build verification report

## Tests actually run in the build workspace

| Test | Result | Evidence |
|---|---|---|
| ZIP archive integrity (both supplied archives) | PASS | `unzip -t` reported no errors |
| Python syntax (maintained app modules) | PASS | `py_compile` passed |
| Main inline JavaScript | PASS | Extracted script blocks passed `node --check` |
| Shell script syntax | PASS | `bash -n` passed for Termux/start/legacy installer scripts |
| Unit tests | PASS | 6 tests passed |
| Real FFmpeg vertical render | PASS | 5.0 sec MP4, H.264, 720×1280, 12 fps |
| Real FFmpeg landscape + music render | PASS | 5.0 sec MP4, H.264 1280×720 + AAC; 2.0 sec test track looped to 5 sec |
| Mixed image sizes + embedded SRT subtitle | PASS | 5.0 sec 720×1280 MP4; H.264 + AAC + mov_text subtitle streams |
| API status endpoint | PASS | HTTP 200 |
| Unknown job lookup | PASS | HTTP 404 (no false 50% rendering state) |
| Invalid duration | PASS | HTTP 400 |
| API-triggered render | PASS | HTTP 202 queued, then completed |
| Generated MP4 download | PASS | HTTP 200, valid MP4 bytes |
| Bearer-token protection | PASS | No token returned HTTP 401; correct token returned HTTP 200 |
| Multipart image upload | PASS | Valid PNG accepted; upload returned HTTP 201 |
| Termux installation | NOT RUN | This build environment is not an Android/Termux device |
| Render deployment | NOT RUN | No deployment was made to the live service |
| Social media publishing | NOT RUN / NOT IMPLEMENTED | Queue metadata only; OAuth and platform publishing are absent |
| AI image generation | NOT RUN / NOT IMPLEMENTED | No reliable generative image provider is integrated |

## Important scope boundary

This is a consolidated, tested maintenance release of the supplied source, not a complete implementation of every aspirational product feature. The working renderer is a photo slideshow pipeline at 720p and 12 fps. The AI planner and SEO metadata are local rule-based/template functions. It is not a 1080p/4K professional multi-track editor, does not build a native APK, and does not publish to YouTube/Instagram/Facebook.

Termux compatibility has been prepared through project-relative paths and an installer, but still requires a final install/run test on the owner's Android device. Live Render deployment and production multi-user certification have not been performed.
