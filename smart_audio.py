"""Local licensed-audio selector. Does not scrape or download copyrighted tracks."""
from pathlib import Path
from backend.video_engine.engine import MUSIC, AUDIO_EXTS

def fetch_ai_recommended_audio(query, output_audio=None):
    """Return a matching local audio path; caller must supply media they may use."""
    q = str(query or '').strip().casefold()
    tracks = sorted(p for p in MUSIC.iterdir() if p.is_file() and p.suffix.lower() in AUDIO_EXTS)
    if not tracks:
        return None
    if not q:
        return str(tracks[0]) if len(tracks) == 1 else None
    matches = [p for p in tracks if q in p.stem.casefold() or p.stem.casefold() in q]
    if len(matches) == 1:
        return str(matches[0])
    if len(tracks) == 1:
        return str(tracks[0])
    return None

if __name__ == '__main__':
    import sys
    print(fetch_ai_recommended_audio(' '.join(sys.argv[1:])))
