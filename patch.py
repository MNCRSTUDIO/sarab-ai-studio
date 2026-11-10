"""Legacy patch entry point retained for compatibility.
The old file contained malformed Python and performed brittle text replacements.
Use install_termux.sh for the supported installation path.
"""
from pathlib import Path
import sys

if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    required = [root / 'backend/api/server.py', root / 'backend/video_engine/editor.py']
    missing = [str(p) for p in required if not p.is_file()]
    if missing:
        print('Missing required project files:')
        print('\n'.join(missing))
        sys.exit(1)
    print('Legacy patch script is retired. Run: bash install_termux.sh')
