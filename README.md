# 🛒 ZAMON MARKET

> Uzum / Yandex Market uslubidagi to'liq ishlaydigan **e-commerce marketplace**.
> Django REST Framework backend + Next.js 15 frontend. Ko'p tilli (UZ / RU / EN),
> savat → checkout → to'lov → buyurtma kuzatuvi to'liq oqimi bilan.

Bu loyiha portfolio uchun yaratilgan: production-darajadagi arxitektura, type-safe kod,
testlar (≥80% coverage), Docker, CI va professional UI/UX bilan.

---

## ✨ Asosiy imkoniyatlar

- 🔐 **JWT autentifikatsiya** (register / login / refresh / me), email-asosida login, rollar (`customer` / `seller` / `admin`)
- 🗂️ **Katalog**: ierarxik kategoriyalar (daraxt), brendlar, mahsulotlar — filtr, qidiruv, saralash, pagination
- 🛍️ **Savat**: anonim (sessiya) + auth, login bo'lganda mehmon saviti birlashadi (guest merge), optimistic update
- 📦 **Checkout**: atomik tranzaksiya, stock qulflanadi va kamayadi (`select_for_update`)
- 💳 **To'lov**: Click (to'liq oqim + webhook imzo tekshiruvi), Payme & Stripe interfeysi, **idempotent** (ikki marta to'lanmaydi)
- ⭐ **Sharhlar**: faqat sotib olganlar yozadi (tasdiqlangan), reyting avtomatik qayta hisoblanadi
- ❤️ **Sevimlilar** (wishlist)
- 🌐 **i18n**: UZ / RU / EN — frontend (`next-intl`) va backend (mahsulot/kategoriya nomlari 3 tilda, `?lang=` / `Accept-Language`)
- 💵 Narxlar so'mda formatlangan (`1 250 000 so'm`)
- 📊 **Dashboard** (admin/sotuvchi): statistika va eng ko'p sotilganlar grafigi
- 🎨 Sayqal: skeleton loading, Framer Motion animatsiyalar, toast, savat drawer, empty/error holatlar, responsive, dark mode tayyor
- 📄 **Swagger / OpenAPI** avtomatik hujjat

---

## 🏗️ Arxitektura

```
                    ┌─────────────┐
   Brauzer  ───────▶│  Next.js 15 │  (App Router, /[locale]/...)
                    │  TanStack Q │  TypeScript · Tailwind · Zustand
                    └──────┬──────┘
                           │  REST (axios, JWT)
                           ▼
                    ┌─────────────┐      ┌──────────┐
                    │ Django + DRF│─────▶│ Postgres │
                    │  /api/v1/   │      └──────────┘
                    └──────┬──────┘      ┌──────────┐
                           └────────────▶│  Redis   │◀── Celery (email)
                                         └──────────┘
```

### Monorepo strukturasi

```
zamon-market/
├── backend/                 # Django + DRF
│   ├── config/              # settings, urls, wsgi/asgi, celery
│   ├── apps/
│   │   ├── common/          # TimeStampedModel, pagination, exceptions, permissions
│   │   ├── accounts/        # custom User, Address, JWT auth
│   │   ├── catalog/         # Category, Brand, Product, ProductImage, Attribute + seed_data
│   │   ├── cart/            # anonim + auth savat, guest merge
│   │   ├── orders/          # atomik checkout, OrderItem snapshot
│   │   ├── payments/        # Click/Payme/Stripe providerlar + webhook
│   │   ├── reviews/         # tasdiqlangan sharhlar
│   │   └── wishlist/
│   └── tests/               # pytest (≥80% coverage)
├── frontend/                # Next.js 15
│   └── src/
│       ├── app/[locale]/    # sahifalar (home, catalog, product, cart, checkout, account, dashboard...)
│       ├── components/      # ui/, layout/, product/, cart/, home/, catalog/
│       ├── lib/             # api client, react-query hooks, types, format
│       ├── stores/          # zustand (auth, ui)
│       ├── messages/        # uz.json, ru.json, en.json
│       └── i18n/            # next-intl routing/request
├── docker-compose.yml       # db, redis, backend, celery, frontend, nginx
├── nginx.conf
└── .github/workflows/ci.yml
```

---

## 🚀 Lokal ishga tushirish

### Variant A — Docker (tavsiya etiladi, butun stack)

```bash
docker compose up --build
```

Bu ko'taradi: Postgres, Redis, Django (gunicorn), Celery, Next.js, Nginx.
Backend birinchi ishga tushganda migratsiya + demo seed avtomatik bajariladi (`SEED_ON_START=1`).

- Frontend: http://localhost:3000
- API: http://localhost:8000/api/v1/
- Swagger: http://localhost:8000/api/docs/

### Variant B — Qo'lda (dev)

**Backend** (Python 3.12+):
```bash
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_data        # demo ma'lumot (105 mahsulot, 16 kategoriya, 12 brand)
python manage.py runserver 8000
```
> Dev'da `DATABASE_URL` bo'sh bo'lsa SQLite ishlatiladi (Docker shart emas).

**Frontend** (Node 20+):
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

---

## 🔑 Demo login

| Rol     | Email            | Parol         |
|---------|------------------|---------------|
| Admin   | `admin@zamon.uz` | `admin12345`  |
| Xaridor | `ali@demo.uz`    | `demo12345`   |
| Xaridor | `vali@demo.uz`   | `demo12345`   |

Django admin: http://localhost:8000/admin/

---

## ⚙️ Muhit o'zgaruvchilari (`.env`)

### Backend (`backend/.env`)

| O'zgaruvchi             | Tavsif                                        | Default (dev)          |
|-------------------------|-----------------------------------------------|------------------------|
| `SECRET_KEY`            | Django maxfiy kalit (prod'da albatta o'zgartiring) | dev-insecure-...   |
| `DEBUG`                 | Debug rejimi                                  | `True`                 |
| `ALLOWED_HOSTS`         | Ruxsat etilgan hostlar (vergul bilan)         | `localhost,127.0.0.1`  |
| `DATABASE_URL`          | Postgres URL (bo'sh → SQLite)                 | *(bo'sh)*              |
| `CORS_ALLOWED_ORIGINS`  | Frontend domeni(lari)                         | `http://localhost:3000`|
| `FRONTEND_URL`          | To'lov redirect uchun                         | `http://localhost:3000`|
| `CELERY_BROKER_URL`     | Redis URL                                     | `redis://localhost:6379/0` |
| `EMAIL_BACKEND`         | Email backend (dev: console)                  | console backend        |
| `CLICK_*` / `PAYME_*` / `STRIPE_*` | To'lov sandbox kalitlari (faqat .env) | *(bo'sh)*          |

### Frontend (`frontend/.env.local`)

| O'zgaruvchi               | Tavsif                | Default                       |
|---------------------------|-----------------------|-------------------------------|
| `NEXT_PUBLIC_API_URL`     | Backend API bazasi    | `http://localhost:8000/api/v1`|
| `NEXT_PUBLIC_BACKEND_URL` | Media/rasm domeni     | `http://localhost:8000`       |

> ⚠️ Hech qanday maxfiy kalit kodda saqlanmaydi — barchasi `.env` orqali.

---

## 📡 API (asosiy endpointlar)

To'liq, interaktiv hujjat: **`/api/docs/`** (Swagger) yoki `/api/redoc/`.

```
POST   /api/v1/auth/register/         ro'yxatdan o'tish (+ JWT qaytaradi)
POST   /api/v1/auth/login/            JWT login
POST   /api/v1/auth/refresh/          access token yangilash
GET    /api/v1/auth/me/               profil
GET    /api/v1/categories/            kategoriya daraxti
GET    /api/v1/products/              filtr/qidiruv/saralash/pagination
       ?category=&brand=&min_price=&max_price=&rating=&search=&ordering=&page=
GET    /api/v1/products/{slug}/       to'liq + o'xshash mahsulotlar
GET    /api/v1/products/featured|new|bestsellers/
GET    /api/v1/cart/                  savat
POST   /api/v1/cart/items/            savatga qo'shish
POST   /api/v1/orders/                checkout (atomik)
GET    /api/v1/orders/                buyurtmalar tarixi
POST   /api/v1/payments/{provider}/create/   to'lov linki
POST   /api/v1/payments/{provider}/webhook/  provayder callback (imzo tekshiruvi)
GET/POST /api/v1/products/{slug}/reviews/
GET    /api/v1/wishlist/  ·  POST/DELETE /api/v1/wishlist/{id}/
```

Xato formati izchil: `{ "detail": "...", "errors": { ... } }`.

---

## 🧪 Test va sifat

```bash
# Backend
cd backend
pytest --cov=apps --cov-report=term      # 18 test, coverage ≈ 81%
ruff check .                              # lint
mypy .                                    # type check

# Frontend
cd frontend
npm run build                             # type-check + production build
npm run lint
```

CI (GitHub Actions) har push/PR'da backend (ruff + pytest, `--cov-fail-under=80`) va
frontend (lint + `tsc --noEmit` + build) ni tekshiradi.

---

## 💳 To'lov oqimi (sandbox)

1. Checkout → buyurtma yaratiladi (`pending`), stock kamayadi (atomik)
2. `POST /payments/click/create/` → to'lov linki qaytadi
3. Provayder `POST /payments/click/webhook/` ga callback yuboradi → **imzo (MD5) tekshiriladi**
4. Imzo to'g'ri va summa mos bo'lsa → buyurtma `paid`, email yuboriladi (Celery), **idempotent**

> Test kalitlarni `.env` ga qo'ying. Kalit bo'lmasa demo link/test oqimi ishlaydi.

---

## 🌍 Deploy

| Qism      | Tavsiya                                  |
|-----------|------------------------------------------|
| Backend   | Railway / Render / VPS (gunicorn + Postgres + Redis) |
| Frontend  | Vercel (`frontend/` root, env o'rnatib)  |
| Media     | S3 / Cloudinary (prod uchun)             |

Prod'da `DEBUG=False`, kuchli `SECRET_KEY`, HTTPS-only cookie, HSTS avtomatik yoqiladi (settings).

---

## 🛠️ Texnologiyalar

**Backend:** Python 3.12+ · Django 5.2 · DRF · SimpleJWT · django-filter · drf-spectacular · Pillow · Celery · Redis · django-environ · pytest · ruff · mypy

**Frontend:** Next.js 15 (App Router) · TypeScript (strict) · Tailwind CSS · TanStack Query · Zustand · next-intl · React Hook Form + Zod · Framer Motion · lucide-react

**Infra:** Docker · docker-compose · Nginx · GitHub Actions

---

## 📸 Skrinshotlar

Saytni ishga tushirib (`/uz`, `/ru`, `/en`) bosh sahifa, katalog, mahsulot, savat va checkout
sahifalarini ko'ring. Dizayn Uzum Market uslubidagi binafsha (`#7000FF`) palitra,
Manrope shrift va 8px grid asosida.



*** 1-amal 1-terminalda

cd C:\Users\Lenovo\OneDrive\Desktop\cloneweb\backend
..\.venv\Scripts\python.exe manage.py runserver 8000

*** 2-amal 2-terminalda 

cd C:\Users\Lenovo\OneDrive\Desktop\cloneweb\frontend
npm run dev








# Frontend terminalida Ctrl+C bosing, keyin:
cd C:\Users\Lenovo\OneDrive\Desktop\cloneweb\frontend
Remove-Item -Recurse -Force .next
npm run dev
***