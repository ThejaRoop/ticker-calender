#!/usr/bin/env bash
# Fool-proof Ubuntu setup for the ticker-calendar alert server.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "==> Ticker Calendar Ubuntu setup"
echo "    Project: $PROJECT_DIR"

# Pick the best available Python (3.10+ preferred, 3.8+ supported with pinned deps)
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3.9 python3.8 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    PYTHON="$candidate"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "ERROR: Python 3 not found."
  echo "Install with: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
  exit 1
fi

PY_VERSION="$("$PYTHON" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "==> Using $PYTHON (version $PY_VERSION)"

if ! "$PYTHON" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 8) else 1)'; then
  echo "ERROR: Python 3.8 or newer is required."
  exit 1
fi

# System packages sometimes needed for lxml wheels on minimal Ubuntu
if command -v apt-get >/dev/null 2>&1; then
  echo "==> Installing system packages (safe to skip if already installed)..."
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3-venv python3-pip libxml2-dev libxslt1-dev zlib1g-dev || true
fi

echo "==> Creating virtual environment"
"$PYTHON" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing Python dependencies"
python -m pip install -r requirements.txt

echo "==> Running install verification"
python run_server.py doctor

echo "==> Scheduled jobs"
python run_server.py list

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  1. Test one rule:  source .venv/bin/activate && python run_server.py run-rule popular_weekday"
echo "  2. Start server:   source .venv/bin/activate && python run_server.py serve"
echo "  3. systemd:        edit deploy/ticker-calendar.service paths, then:"
echo "                     sudo cp deploy/ticker-calendar.service /etc/systemd/system/"
echo "                     sudo systemctl daemon-reload && sudo systemctl enable --now ticker-calendar"
