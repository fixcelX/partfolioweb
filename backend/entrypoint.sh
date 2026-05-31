#!/bin/sh
set -e

echo "Migratsiyalar qo'llanmoqda..."
python manage.py migrate --noinput

# Statik fayllarni yig'ish (whitenoise prod'da xizmat qiladi)
python manage.py collectstatic --noinput || true

if [ "$SEED_ON_START" = "1" ]; then
  echo "Demo ma'lumot to'ldirilmoqda..."
  python manage.py seed_data || true
fi

exec "$@"
