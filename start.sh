#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
mkdir -p logs media/input media/music media/subtitles media/output media/temp
if [ -f logs/server.pid ] && kill -0 "$(cat logs/server.pid)" 2>/dev/null; then
  echo "SARAB AI STUDIO is already running (PID $(cat logs/server.pid))."
  echo "Open http://127.0.0.1:7860"
  exit 0
fi
nohup python -m backend.api.server >> logs/server.log 2>&1 &
echo $! > logs/server.pid
sleep 2
if kill -0 "$(cat logs/server.pid)" 2>/dev/null; then
  echo "SARAB AI STUDIO started."
  echo "Open http://127.0.0.1:7860"
  echo "Private access token is stored at: media/.access_token"
  echo "To stop: kill $(cat logs/server.pid)"
else
  echo "Server did not start. Check logs/server.log"
  exit 1
fi
