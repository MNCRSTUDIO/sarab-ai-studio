# SARAB AI STUDIO — Professional Creator Workspace Upgrade

This package is based on the exact Termux audit archive `SARAB-AI-STUDIO-AUDIT-NOW.tar.gz` and applies the security/free-plan overlay plus a redesigned responsive creator workspace.

## Included and wired to existing backend
- Private token entry and authenticated API requests.
- Multilingual prompt input and local rule-based storyboard endpoint (`/api/v1/ai/plan`).
- SEO metadata draft endpoint (`/api/v1/ai/metadata`). These are templates/rule-based, not live trend research.
- Upload photos, licensed local audio, and SRT subtitles using the authenticated media endpoint.
- Local FFmpeg photo slideshow render, subtitle burn-in, optional user-supplied audio, preview and download.
- Browser-local thumbnail PNG creator from a user-selected image.
- Approval-first social publishing checklist; no automatic upload is claimed.
- Local-first storage notes and copyright-safe audio guidance.
- Security overlay: bearer-token protection, upload size/signature checks, POST rate limiting, no default remote prompt/image calls, no scraped third-party music downloads.

## Not implemented / requires additional services or engineering
- Actual multilingual generative image model and image-to-video model. Current planner is rule-based and current renderer is a still-image slideshow.
- Live trend/keyword research; current SEO metadata is template-based.
- Direct YouTube/Facebook/Instagram upload. Official OAuth apps, platform permissions, and user approval are required.
- Cloud sync/storage. Free cloud tiers are quota-limited; no unlimited free cloud is promised.
- Professional multi-track NLE features such as keyframes, masks, advanced color grading, motion tracking, and multi-layer compositing.
- Copyright-claim immunity. Editing cannot guarantee no claim; use rights-cleared content.

## Install
Extract the ZIP into the existing project root, replacing only the included source/UI/docs/test files. Preserve `media/`, `.access_token`, user uploads and exports. Then run the validation command in the accompanying ChatGPT instructions.
