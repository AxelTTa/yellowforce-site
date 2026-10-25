#!/usr/bin/env bash
# Build the site and serve docs/ on http://127.0.0.1:8787/
#   tools/serve.sh          production build (same CSP as the live site)
#   tools/serve.sh --dev    build without upgrade-insecure-requests. Needed for Safari/WebKit: with the production CSP
#                           WebKit upgrades every http://127.0.0.1 asset URL to https and the page never loads.
#                           Never deploy a --dev build.
# Port override: PORT=8800 tools/serve.sh
set -euo pipefail
cd "$(dirname "$0")/.."
python3 build.py "$@"
PORT="${PORT:-8787}"
echo "Serving docs/ at http://127.0.0.1:${PORT}/  (Ctrl+C to stop)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 -d docs
