#!/bin/bash
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$ROOT/backups"
case "$1" in
    backup)
        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        tar -czf "$ROOT/backups/sarab_backup_$TIMESTAMP.tar.gz" --exclude='media/temp*' --exclude='backups' -C "$ROOT" .
        echo "[+] Backup created: backups/sarab_backup_$TIMESTAMP.tar.gz"
        ;;
    restore)
        LATEST=$(ls -t "$ROOT"/backups/sarab_backup_*.tar.gz 2>/dev/null | head -n1)
        if [ -n "$LATEST" ]; then
            tar -xzf "$LATEST" -C "$ROOT"
            echo "[+] Restored from: $LATEST"
        else
            echo "[-] No backup archive found"
        fi
        ;;
    *)
        echo "Usage: ./backup_restore.sh [backup|restore]"
        ;;
esac
