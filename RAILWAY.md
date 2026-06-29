# ZAMON MARKET — Railway.app Deploy Qo'llanma

## 1. Railway'da loyiha yaratish

1. [Railway.app](https://railway.app) ga kiring, GitHub ulanganligini tekshiring
2. **New Project** → **Deploy from GitHub repo** → repo'ni tanlang
3. Railway avtomatik Dockerfile'larni topadi

## 2. PostgreSQL bazasi

- **+ New** → **Database** → **Add PostgreSQL**
- `DATABASE_URL` avtomatik yaratiladi (boshqa xizmatlarga Reference qilish mumkin)

## 3. Backend xizmati

Backend Django + DRF + Storefront server-rendered saytni bitta xizmatda beradi.

### Xizmat yaratish:
1. **+ New** → **Deploy from GitHub repo** → repo'ni yana tanlang
2. Xizmat paydo bo'lgach, uni bosing → **Settings**

### Sozlamalar:
| Bo'lim | O'zgartirish |
|--------|-------------|
| **General → Name** | `zamon-market` |
| **Deploy → Root Directory** | `/backend` |
| **Deploy → Custom Start Command** | (bo'sh qoldiring — Dockerfile avtomatik ishlaydi) |

### Environment Variables:
| Variable | Qiymat |
|----------|--------|
| `SECRET_KEY` | *(Generate — kuchli kalit)* |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `.railway.app` |
| `DATABASE_URL` | PostgreSQL dan **Reference Variable** qiling |
| `CORS_ALLOWED_ORIGINS` | Frontend domeni (keyin qo'shasiz) |
| `FRONTEND_URL` | Frontend domeni (keyin qo'shasiz) |
| `SEED_ON_START` | `1` (birinchi deployda demo ma'lumot to'ldiradi) |
| `CELERY_TASK_ALWAYS_EAGER` | `True` (agar Celery Worker bo'lmasa) |

> **MUHIM:** `DATABASE_URL` ni PostgreSQL'dan Reference qilish:
> Variables da `DATABASE_URL` yozing, qiymat maydonida PostgreSQL xizmatini tanlang

### Networking:
- **Generate Domain** ni bosing
- Domen: `https://zamon-market.up.railway.app` (masalan)

### Deploy:
- **Deploy** tugmasini bosing
- **Deploy Logs** dan kuzating: `migrate` → `collectstatic` → `seed_data` → `gunicorn`
- Tayyor bo'lgach, domenni oching

## 4. Frontend xizmati (Next.js 15)

Agar Next.js frontend kerak bo'lsa:

1. **+ New** → **Deploy from GitHub repo** → repo'ni yana tanlang
2. **Settings** → **Root Directory**: `/frontend`
3. **Variables** ga qo'shing:

| Variable | Qiymat |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | `https://zamon-market.up.railway.app/api/v1` |
| `NEXT_PUBLIC_BACKEND_URL` | `https://zamon-market.up.railway.app` |

4. **Networking** → **Generate Domain**
5. Backend `CORS_ALLOWED_ORIGINS` ga frontend domenini qo'shing

## 5. Celery Worker (ixtiyoriy)

Fondagi jarayonlar (email, order tasdiqlash) uchun:

1. **+ New** → **Deploy from GitHub repo** → repo'ni yana tanlang
2. **Root Directory**: `/backend`
3. **Custom Start Command** → yoqing va yozing: `./start-worker.sh`
4. `DATABASE_URL` va `CELERY_BROKER_URL` ni backend dagidek qo'shing

## 6. Tekshirish

Deploy tugagach:

| Sahifa | URL |
|--------|-----|
| Sayt (storefront) | `https://zamon-market.up.railway.app/` |
| API | `https://zamon-market.up.railway.app/api/v1/` |
| Swagger | `https://zamon-market.up.railway.app/api/docs/` |
| Admin | `https://zamon-market.up.railway.app/admin/` |

## Debug (agar "Not Found" chiqsa)

1. **Deploy Logs** ni oching — backend ishga tushganmi?
2. **Variables** da `DATABASE_URL` to'g'ri reference qilinganmi?
3. `ALLOWED_HOSTS` ga `.railway.app` qo'yilganmi?
4. Railway'da PORT avtomatik beriladi — `start.sh` dagi `${PORT:-8000}` uni oladi
5. Agar seed_data uzoq vaqt olsa, `SEED_ON_START=1` ni olib tashlang
6. Log'da xato bo'lsa, Railway dashboard → Deploy Logs → chekkadagi **...** → **Download Logs**
