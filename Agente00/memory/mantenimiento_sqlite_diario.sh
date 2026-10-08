#!/bin/bash
set -euo pipefail

export PATH="$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"

OPENCLAW="$(command -v openclaw)"
PYTHON="$(command -v python3)"
DB="$HOME/.openclaw/agents/main/agent/openclaw-agent.sqlite"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Inicio mantenimiento SQLite"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ejecutando memory index"
"$OPENCLAW" memory index --agent main

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Ejecutando ANALYZE main"

"$PYTHON" - "$DB" <<'PY'
import sqlite3
import sys
import time

path = sys.argv[1]
con = sqlite3.connect(path)

start = time.monotonic()
con.execute("ANALYZE main")
con.commit()
elapsed = time.monotonic() - start

con.close()

print(f"ANALYZE main: OK ({elapsed:.3f} s)")
PY

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Mantenimiento SQLite finalizado OK"
