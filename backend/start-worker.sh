#!/bin/sh
set -e

echo "Migratsiyalar qo'llanmoqda..."
python manage.py migrate --noinput

exec celery -A config worker -l info
