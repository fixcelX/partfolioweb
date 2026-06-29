#!/bin/sh
set -e

echo "Migratsiyalar qo'llanmoqda..."
python manage.py migrate --noinput

python manage.py collectstatic --noinput || true

if [ "$SEED_ON_START" = "1" ]; then
  echo "Demo ma'lumot to'ldirilmoqda..."
  python manage.py seed_data || true
fi

exec gunicorn config.wsgi:application --bind 0.0.0.0:"${PORT:-8000}" --workers 3
