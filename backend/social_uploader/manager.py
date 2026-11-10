"""Social upload queue metadata only; real platform publishing is not implemented."""
import json
from datetime import datetime, timezone
from pathlib import Path
from backend.video_engine.engine import BASE, OUTPUT

JOBS = BASE / 'exports' / 'social_media'
JOBS.mkdir(parents=True, exist_ok=True)
PLATFORMS = ('youtube', 'instagram', 'facebook')

def get_status():
    return {
        'platforms': {name: {'status': 'not_authorized'} for name in PLATFORMS},
        'upload_system': 'job_queue_only',
        'real_publishing': False,
        'note': 'Real publishing requires platform OAuth, permissions, app review, and account setup.'
    }

def create_upload_job(video, platforms, caption='', title=''):
    path = Path(str(video)).expanduser().resolve()
    # Queue only generated videos from this project; do not accept arbitrary filesystem paths.
    try:
        path.relative_to(OUTPUT.resolve())
    except ValueError:
        return {'error': 'Video must be a generated file inside media/output.'}
    if not path.is_file() or path.suffix.lower() != '.mp4':
        return {'error': 'Generated MP4 file not found.'}
    selected = list(dict.fromkeys(str(p).lower() for p in platforms if str(p).lower() in PLATFORMS))
    if not selected:
        return {'error': 'Select youtube, instagram or facebook'}
    job = {
        'video': path.name, 'platforms': selected, 'title': str(title)[:100],
        'caption': str(caption)[:5000], 'created_at': datetime.now(timezone.utc).isoformat(),
        'status': 'pending_authorization',
        'platform_status': {p: 'awaiting_authorization' for p in selected},
        'publishing_implemented': False
    }
    name = 'job_' + datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f') + '.json'
    (JOBS / name).write_text(json.dumps(job, indent=2, ensure_ascii=False), encoding='utf-8')
    return {'job_file': str(JOBS / name), **job}
