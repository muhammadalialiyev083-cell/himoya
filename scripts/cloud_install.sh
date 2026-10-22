#!/usr/bin/env bash
set -euo pipefail
cd /workspace/UzluksizBCMS-Desktop
python3 -c "import sys,struct; assert sys.version_info[:2] == (3,12) and struct.calcsize('P') == 8"
if [ ! -x .venv/bin/python ]; then
  if [ -e .venv ]; then
    echo "Existing .venv is incompatible; preserve it and create a separate local virtual environment." >&2
    exit 1
  fi
  python3 -m venv .venv
fi
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements-lock.txt
QT_QPA_PLATFORM=offscreen XDG_CACHE_HOME="$PWD/.cache" .venv/bin/python -m pytest -q
