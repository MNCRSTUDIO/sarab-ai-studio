#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
echo '[1/5] Updating Termux packages...'
pkg update -y
pkg install -y python ffmpeg git clang libjpeg-turbo

echo '[2/5] Preparing storage and project folders...'
mkdir -p media/input media/music media/subtitles media/output media/temp logs backups
termux-setup-storage || true

echo '[3/5] Creating a full pre-install source and media backup...'
STAMP="$(date +%Y%m%d-%H%M%S)"
BACKUP_ROOT="$HOME/SARAB-AI-STUDIO-backups"
mkdir -p "$BACKUP_ROOT"
chmod 700 "$BACKUP_ROOT"
BACKUP="$BACKUP_ROOT/pre-install-$STAMP.tar.gz"
tar -czf "$BACKUP" \
  --exclude='./backups' --exclude='./logs' --exclude='./media/temp' --exclude='./media/output' \
  --exclude='./__pycache__' --exclude='*/__pycache__' --exclude='./.git' .

echo '[4/5] Installing Python dependencies...'
python -m pip install -r requirements.txt

echo '[5/5] Verifying runtime...'
python -m py_compile backend/api/server.py backend/video_engine/editor.py backend/video_engine/engine.py
ffmpeg -version | head -n 1
ffprobe -version | head -n 1
printf '\nInstall complete. Start with: bash start.sh\nFull backup: %s\n' "$BACKUP"
