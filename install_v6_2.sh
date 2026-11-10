#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo 'Legacy v6.2 patch installer is retired.'
echo 'Use the consolidated installer: bash install_termux.sh'
exec bash "$ROOT/install_termux.sh"
