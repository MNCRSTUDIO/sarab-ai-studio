import os
import shutil
from pathlib import Path

BASE = Path(os.environ.get('SARAB_ROOT', Path(__file__).resolve().parents[2])).resolve()
INPUT = BASE / 'media' / 'input'
OUTPUT = BASE / 'media' / 'output'
MUSIC = BASE / 'media' / 'music'
SUBTITLES = BASE / 'media' / 'subtitles'
TEMP = BASE / 'media' / 'temp'
LOGS = BASE / 'logs'
for _path in (INPUT, OUTPUT, MUSIC, SUBTITLES, TEMP, LOGS):
    _path.mkdir(parents=True, exist_ok=True)

VIDEO_EXTS = {'.mp4', '.mov', '.mkv', '.webm', '.3gp'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.webp'}
AUDIO_EXTS = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac'}

def get_status():
    ff = shutil.which('ffmpeg')
    probe = shutil.which('ffprobe')
    return {
        'status': 'ready' if ff and probe else 'ffmpeg_missing',
        'ffmpeg_path': ff,
        'ffprobe_path': probe,
        'input_dir': str(INPUT),
        'output_dir': str(OUTPUT),
        'images': sum(1 for p in INPUT.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTS),
        'videos': sum(1 for p in INPUT.iterdir() if p.is_file() and p.suffix.lower() in VIDEO_EXTS),
        'music': sum(1 for p in MUSIC.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS),
    }

def list_media():
    items = []
    for p in sorted(INPUT.iterdir()):
        if p.is_file() and p.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS:
            items.append({'name': p.name, 'type': 'image' if p.suffix.lower() in IMAGE_EXTS else 'video', 'size_bytes': p.stat().st_size})
    return items
