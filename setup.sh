#!/usr/bin/env bash
# ZAMON MARKET — bir buyruqli o'rnatish (macOS / Linux)
# Ishlatish:  bash setup.sh
set -euo pipefail
cd "$(dirname "$0")"

PY=$(command -v python3 || command -v python)
[ -z "$PY" ] && { echo "Python topilmadi (3.12+ kerak)."; exit 1; }

if [ ! -x ".venv/bin/python" ]; then
  echo "[1/4] .venv yaratilmoqda..."
  "$PY" -m venv .venv
fi
VENV=".venv/bin/python"

echo "[2/4] Paketlar o'rnatilmoqda..."
"$VENV" -m pip install --upgrade pip --quiet
"$VENV" -m pip install -r backend/requirements.txt --quiet

echo "[3/4] Baza migratsiyasi..."
"$VENV" backend/manage.py migrate

echo "[4/4] Demo ma'lumot (105 mahsulot)..."
"$VENV" backend/manage.py seed_data

echo ""
echo "Tayyor! Ishga tushirish:"
echo "  ./.venv/bin/python backend/manage.py runserver 8000"
echo "Brauzerda:  http://localhost:8000"
echo "Admin: admin@zamon.uz / admin12345"
