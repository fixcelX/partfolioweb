# 🛒 ZAMON MARKET — E-Commerce Portfolio Loyihasi (AI Agent uchun to'liq prompt)

> **AI agentga ko'rsatma:** Quyidagi hujjat — to'liq texnik topshiriq (specification). Uni boshidan oxirigacha o'qib chiq, so'ng bosqichma-bosqich amalga oshir. Har bir bosqich oxirida ishlayotganini ko'rsat (skrinshot / `curl` / test natijalari). Noaniqlik bo'lsa — taxmin qilib davom etma, eng professional yechimni tanla va sababini bir qatorda izohla.

---

## 0. ROL VA STANDART

Sen tajribali **Senior Full-Stack muhandissan** (Django + Next.js, 8+ yil). Bu loyiha — egasining **CV / portfolio**si uchun flagman ish. Maqsad: ish beruvchi ko'rib "buni ishga olamiz" deydigan sifat. Demak:

- Kod **toza, izohlangan, type-safe, test bilan qoplangan** bo'lsin.
- Har bir qaror **production-ready** standartda bo'lsin (xavfsizlik, performance, a11y, SEO).
- "Ishlayapti-ku" yetarli emas — **professional ko'rinish va his** kerak (animatsiya, skeleton loading, empty/error holatlar, responsive).

---

## 1. LOYIHA MAQSADI

**Uzum Market / Yandex Market uslubidagi to'liq ishlaydigan e-commerce (onlayn do'kon) websayti** yaratish. Foydalanuvchi mahsulot ko'radi → savatga qo'shadi → ro'yxatdan o'tadi → buyurtma beradi → to'laydi → buyurtma holatini kuzatadi. Sotuvchi/admin mahsulotlarni boshqaradi.

Bu shunchaki demo emas — **haqiqiy marketplace tajribasi** beradigan sayt.

---

## 2. MAVJUD KOD (asos sifatida)

Repozitoriyda `vazifa28` nomli Django skeleton bor:
- `news/` — Django project (settings, urls, wsgi/asgi)
- `news_app/` — `Category` va `News` modellari bor app
- SQLite, DRF yo'q, frontend yo'q, `SECRET_KEY` ochiq holatda

**Nima qilish kerak:** Bu skeletni e-commerce'ga aylantir. `Category` modeli g'oyasi qoladi (kategoriyalar bizga kerak). `News` modelini olib tashlamay, ixtiyoriy "Blog/Yangiliklar" bo'limiga aylantirsang bo'ladi (bonus). Project nomini `core` yoki `config` ga refactor qil, app'larni qaytadan, toza tashkil et.

---

## 3. TEXNOLOGIYALAR STEKI (aniq)

### Backend
- **Python 3.12+**, **Django 5.x**, **Django REST Framework**
- **PostgreSQL** (production), dev uchun ham Postgres (Docker bilan) — SQLite'dan voz kech
- **JWT auth** — `djangorestframework-simplejwt` (access + refresh, httpOnly cookie strategiyasi)
- **drf-spectacular** — avtomatik OpenAPI/Swagger hujjat
- **django-filter** — filtrlash
- **Pillow** — rasmlar, **django-imagekit** yoki thumbnail uchun
- **Celery + Redis** — fon vazifalari (email yuborish, buyurtma tasdiqlash)
- **django-cors-headers** — frontend bilan bog'lanish
- **django-environ** — `.env` orqali sozlamalar (SECRET_KEY, DB, payment kalitlari hech qachon kodda turmasin)
- **i18n** — Django `modeltranslation` yoki alohida til maydonlari (UZ/RU/EN)
- To'lov: **Click + Payme** (O'zbekiston, sandbox/test) va **Stripe** (xalqaro, test mode) — eng kamida bittasini to'liq, qolganini interfeys darajasida tayyorla
- Test: **pytest-django** + **factory_boy** + coverage (maqsad ≥ 80%)
- Kod sifati: **ruff** (lint+format), **mypy** (type check), **pre-commit**

### Frontend
- **Next.js 14/15 (App Router)** + **TypeScript (strict)**
- **Tailwind CSS** + **shadcn/ui** (komponent bazasi)
- **TanStack Query (React Query)** — server state, caching, optimistic update
- **Zustand** — savat/UI state (yoki client state)
- **next-intl** — ko'p tillilik (UZ/RU/EN)
- **React Hook Form + Zod** — formalar va validatsiya
- **Framer Motion** — animatsiya
- **next/image** — optimizatsiya
- Test: **Vitest + React Testing Library**, **Playwright** (E2E smoke testlar)
- Lint: **ESLint + Prettier**

### Infratuzilma
- **Docker + docker-compose** (backend, frontend, postgres, redis, celery, nginx)
- **GitHub Actions** CI (lint + test har push'da)
- Deploy ko'rsatmasi: backend → Railway/Render/VPS, frontend → Vercel
- `.env.example` har ikkala tomon uchun

---

## 4. MONOREPO STRUKTURA

```
zamon-market/
├── backend/
│   ├── config/                 # Django project (eski 'news')
│   ├── apps/
│   │   ├── accounts/           # User, profil, auth, manzillar
│   │   ├── catalog/            # Category, Brand, Product, ProductImage, Attribute
│   │   ├── cart/               # Savat
│   │   ├── orders/             # Buyurtma, OrderItem, status
│   │   ├── payments/           # Click/Payme/Stripe integratsiya
│   │   ├── reviews/            # Sharh va reyting
│   │   └── common/             # base modellar, utillar, pagination
│   ├── tests/
│   ├── manage.py
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/                # App Router (locale segmenti bilan: /[locale]/...)
│   │   ├── components/         # ui/, layout/, product/, cart/, checkout/
│   │   ├── features/           # domenga bo'lingan logika
│   │   ├── lib/                # api client, hooks, utils
│   │   ├── stores/             # zustand
│   │   ├── messages/           # uz.json, ru.json, en.json
│   │   └── types/
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md                   # arxitektura, ishga tushirish, skrinshotlar
```

---

## 5. MA'LUMOTLAR BAZASI SXEMASI (asosiy modellar)

> Har bir modelda `created_at`, `updated_at` bo'lsin (`common.TimeStampedModel` dan meros). Nom maydonlari UZ/RU/EN da (i18n).

- **User** (custom, `AbstractUser` dan): email bilan login, telefon, avatar, rol (`customer` / `seller` / `admin`)
- **Address**: user, viloyat, shahar, ko'cha, default flag
- **Category**: nom (i18n), slug, parent (self-FK — daraxt/ierarxiya), icon, rasm
- **Brand**: nom, logo, slug
- **Product**: nom (i18n), slug, tavsif (i18n), category, brand, narx, chegirma narxi, sklad miqdori (stock), SKU, reyting (cache), sotilgan soni, `is_active`, `is_featured`
- **ProductImage**: product, rasm, tartib (galereya uchun)
- **Attribute / AttributeValue**: rang, o'lcham va h.k. (variantlar uchun) — kamida soddalashtirilgan variant tizimi
- **Cart / CartItem**: user (yoki anonim sessiya kaliti), product, miqdor
- **Order**: user, raqam (UZM-000123), status (`pending`/`paid`/`shipped`/`delivered`/`cancelled`), manzil, jami summa, to'lov usuli
- **OrderItem**: order, product (snapshot: nom+narx saqlanadi), miqdor, narx
- **Payment**: order, provayder (click/payme/stripe), transaction_id, status, summa, raw_payload
- **Review**: product, user, reyting (1–5), matn, tasdiqlangan (faqat sotib olganlar yoza oladi)
- **Wishlist**: user, products (M2M)
- **Coupon** (bonus): kod, chegirma %, amal qilish muddati

---

## 6. BACKEND — API (REST)

Barchasi `/api/v1/` префикс ostida. DRF ViewSet/Router + drf-spectacular hujjat (`/api/docs/`).

**Auth (`accounts`)**
- `POST /auth/register/`, `POST /auth/login/` (JWT), `POST /auth/refresh/`, `POST /auth/logout/`
- `GET/PATCH /auth/me/`, `GET/POST/PUT/DELETE /addresses/`

**Catalog (`catalog`)** — public (auth shart emas)
- `GET /categories/` (daraxt ko'rinishida), `GET /categories/{slug}/`
- `GET /brands/`
- `GET /products/` — filtrlash (`?category=&brand=&min_price=&max_price=&rating=`), qidiruv (`?search=`), saralash (`?ordering=price,-rating,-created_at`), pagination
- `GET /products/{slug}/` — to'liq, o'xshash mahsulotlar bilan
- `GET /products/featured/`, `GET /products/new/`, `GET /products/bestsellers/`

**Cart (`cart`)** — anonim + auth (sessiya birlashtirish login bo'lganda)
- `GET /cart/`, `POST /cart/items/`, `PATCH /cart/items/{id}/`, `DELETE /cart/items/{id}/`

**Orders (`orders`)** — auth
- `POST /orders/` (checkout: savatdan buyurtma yaratadi, stockni kamaytiradi atomik tranzaksiyada)
- `GET /orders/`, `GET /orders/{number}/`

**Payments (`payments`)**
- `POST /payments/{provider}/create/` — to'lov sessiyasi/linkini yaratadi
- `POST /payments/{provider}/webhook/` — provayder callback (imzo tekshirish bilan!)

**Reviews / Wishlist**
- `GET/POST /products/{slug}/reviews/`
- `GET /wishlist/`, `POST/DELETE /wishlist/{product_id}/`

**Talablar:**
- Hamma endpoint validatsiya, to'g'ri status kodlar, izchil xato formati (`{ "detail": ..., "errors": {...} }`)
- Throttling (login/register'da rate limit)
- Pagination (`PageNumberPagination`, sahifa hajmi sozlanadi)
- `select_related`/`prefetch_related` bilan N+1 muammosini oldini ol
- Stock tekshiruvi va `transaction.atomic` checkout'da

---

## 7. FRONTEND — SAHIFALAR

URL `/[locale]/...` (uz default). Hamma sahifa **mobil-first, responsive**, skeleton loading, error/empty holatlar bilan.

1. **Bosh sahifa (`/`)** — hero banner/karusel, kategoriya tezkor havolalar, "Tavsiya etilgan", "Yangi", "Eng ko'p sotilgan" mahsulot lentalari, aksiya bloklari
2. **Katalog (`/catalog`, `/category/[slug]`)** — chap tomonda filtr paneli (narx slider, brand, reyting, kategoriya), grid, saralash, sahifalash/infinite scroll, URL'ga sinxron filtrlar
3. **Mahsulot sahifasi (`/product/[slug]`)** — rasm galereya (zoom), narx+chegirma, variant tanlash, "savatga", "sevimlilarga", tavsif/xususiyat tablari, sharhlar bo'limi, o'xshash mahsulotlar
4. **Savat (`/cart`)** — miqdor o'zgartirish, o'chirish, jami hisob, "rasmiylashtirish"
5. **Checkout (`/checkout`)** — manzil tanlash/kiritish, yetkazib berish usuli, to'lov usuli (Click/Payme/Stripe), buyurtma xulosasi → to'lov
6. **To'lov natijasi (`/checkout/success`, `/failed`)**
7. **Profil (`/account`)** — buyurtmalar tarixi va holati, manzillar, sozlamalar, sevimlilar
8. **Auth (`/login`, `/register`)** — chiroyli, validatsiyali formalar
9. **Qidiruv (`/search`)** — debounce bilan jonli qidiruv, takliflar (autocomplete)
10. **Sotuvchi/Admin dashboard (`/dashboard`)** — mahsulot CRUD, buyurtmalar, oddiy statistika grafiklari (savdo, top mahsulotlar)
11. **404 / xato sahifalar** — brendlangan

**Global UI:** sticky header (logotip, qidiruv, til tanlash, savat badge, profil), mega-menu kategoriyalar, footer, toast bildirishnomalar, til almashtirish (UZ/RU/EN), narxlar so'mda formatlangan (`1 250 000 so'm`).

---

## 8. DIZAYN TIZIMI

**Figma:** Sen Uzum/Yandex Market uslubidagi mashhur, ochiq/tekin e-commerce Figma UI kit'ini referens qilib ol (masalan "E-commerce Web UI Kit" turidagi community fayllar). Aniq bittasini tanla, README'da havolasini yoz, va undan **dizayn tilini** (ranglar, shrift, spacing, komponent uslubi) izchil ko'chir. Piksel-quvchilik shart emas, lekin **professional, zamonaviy, izchil** bo'lsin.

**Dizayn tokenlari (Tailwind config'da o'zgaruvchi sifatida):**
- **Primary rang:** binafsha/siyohrang (Uzum uslubi, masalan `#7000FF` atrofida) — yoki tanlangan kit ranglari
- Neutral kulrang shkala, success/danger/warning
- **Shrift:** Inter yoki Manrope (lotin + kirill qo'llab-quvvatlaydigan)
- Radius: yumshoq (`rounded-xl`), nozik soyalar, 8px grid spacing
- Dark mode (bonus, lekin tavsiya)
- Komponentlar: tugma, input, card, badge, modal, drawer (savat), skeleton — hammasi shadcn/ui asosida, izchil

**Sifat detallari:** hover/active holatlar, fokus halqalari (a11y), mikro-animatsiyalar (savatga qo'shilganda), skeleton shimmer, rasm lazy-load.

---

## 9. KO'P TILLILIK (UZ / RU / EN)

- Frontend: `next-intl`, `messages/uz.json|ru.json|en.json`, URL `/[locale]/`
- Backend: mahsulot/kategoriya nomlari va tavsiflari 3 tilda (i18n maydonlari), API `Accept-Language` yoki `?lang=` ga qarab to'g'ri tilni qaytaradi
- Default: **uz**. Til almashtirgich header'da, tanlov saqlanadi (cookie)
- Sana, son, valyuta formatlash har til uchun to'g'ri (so'm hamma tilda)

---

## 10. TO'LOV (real, sandbox/test)

- **Click** va **Payme** (O'zbekiston) — test/sandbox merchant kalitlari bilan. Kamida bittasini **to'liq oqim** (yaratish → redirect/QR → webhook → buyurtma `paid`). Webhook imzosini **albatta tekshir**.
- **Stripe** (xalqaro) — test mode, Checkout Session.
- To'lov kalitlari **faqat `.env`da**, hech qachon kodda yoki frontda emas.
- Idempotentlik: bir buyurtma ikki marta to'lanib qolmasin.
- Muvaffaqiyat/xato sahifalari, email tasdiq (Celery orqali, console backend dev'da).

---

## 11. XAVFSIZLIK (majburiy)

- `SECRET_KEY`, DB parol, payment kalitlari — `.env` (eski ochiq kalitni almashtir!)
- `DEBUG=False` prod'da, `ALLOWED_HOSTS` to'g'ri
- HTTPS-only cookie, JWT refresh httpOnly cookie'da, CSRF himoyasi
- CORS faqat frontend domeniga ruxsat
- Rate limiting (auth endpointlar), parol validatsiyasi
- Webhook imzo tekshiruvi, SQL injection/XSS yo'qligi (DRF+ORM bilan tabiiy himoya)
- Fayl yuklashda tur/hajm tekshiruvi

---

## 12. TEST VA SIFAT

- Backend: pytest, factory_boy; auth, catalog filtr, cart, checkout (stock+atomik), payment webhook uchun testlar. Coverage ≥ 80%.
- Frontend: Vitest (komponent/hook), Playwright smoke (bosh sahifa → mahsulot → savat → checkout oqimi).
- CI (GitHub Actions): har push'da lint + type-check + test. Yashil bo'lmasa merge yo'q.
- `ruff`, `mypy`, `eslint`, `prettier`, `pre-commit`.

---

## 13. SEED / DEMO MA'LUMOT

- Management command `seed_data`: 8–12 kategoriya (ierarxiya), 10+ brand, **60–100 realistik mahsulot** (3 tilda nom/tavsif, narx so'mda, rasmlar — placeholder yoki tekin stock rasmlar), demo sharhlar, 1 admin + 2 demo foydalanuvchi.
- README'da demo login ma'lumotlari.
- Sayt birinchi ochilganda **bo'sh ko'rinmasin** — to'la, jonli marketplace taassuroti bersin.

---

## 14. DEPLOY VA HUJJAT

- `docker-compose up` bilan butun stack ko'tarilsin (db, redis, backend, celery, frontend, nginx).
- `README.md`: arxitektura diagrammasi, lokal ishga tushirish (qadam-baqadam), `.env` o'zgaruvchilar jadvali, API hujjat havolasi, **skrinshotlar/GIF**, jonli demo havolasi (deploy qilingan bo'lsa).
- Deploy ko'rsatmasi: backend (Railway/Render), frontend (Vercel), media uchun S3/Cloudinary varianti.

---

## 15. BOSQICHLI REJA (shu tartibda bajar, har bosqichda ko'rsat)

1. **Setup:** monorepo, Docker, Postgres, Django + DRF skeleton, Next.js skeleton, CI, `.env.example`, eski `SECRET_KEY`ni almashtirish.
2. **Auth:** custom User, JWT, register/login/me, frontend login/register sahifalari.
3. **Catalog backend:** modellar, migratsiyalar, admin, seed, products/categories API + filtr/qidiruv/saralash + Swagger.
4. **Catalog frontend:** dizayn tizimi/Tailwind tokenlari, header/footer, bosh sahifa, katalog, mahsulot sahifasi.
5. **Cart + Wishlist:** backend + frontend (drawer, badge, optimistic update).
6. **Checkout + Orders:** manzil, buyurtma yaratish (atomik), buyurtma tarixi.
7. **Payments:** Click/Payme/Stripe sandbox, webhook, success/failed.
8. **Reviews + Search + i18n** to'liq.
9. **Dashboard** (sotuvchi/admin), statistika.
10. **Sayqal:** animatsiya, skeleton, a11y, SEO (metadata, sitemap, OpenGraph), performance (Lighthouse ≥ 90), testlar, README, deploy.

> Har bosqich oxirida: ishlayotganini isbotla (skrinshot/curl/test log), keyin keyingisiga o't.

---

## 16. QABUL KRITERIYALARI (tugadi deyish uchun)

- [ ] Mehmon: ko'radi → savatga → ro'yxatdan o'tadi → buyurtma → (test) to'laydi → holatni ko'radi — **to'liq oqim ishlaydi**
- [ ] UZ/RU/EN almashadi, hamma narx so'mda to'g'ri formatda
- [ ] Mobil va desktopda chiroyli (responsive), Lighthouse perf/a11y/SEO ≥ 90
- [ ] API Swagger'da to'liq hujjatlangan
- [ ] Testlar yashil, CI ishlaydi, coverage ≥ 80%
- [ ] `docker-compose up` bilan to'liq ko'tariladi, README to'liq
- [ ] Hech qanday maxfiy kalit kodda yo'q

---

## 17. NIMA QILMA (anti-pattern)

- Sirlarni (kalit/parol) kodga yozma
- SQLite'ni production uchun ishlatma
- Dizaynni "tashlab ketma" — har sahifa sayqallangan bo'lsin
- N+1 so'rovlar, validatsiyasiz endpoint, test'siz feature qoldirma
- Yarim ishlaydigan "TODO" qoldirma — bosqich tugaganda u to'liq ishlasin

---

## 18. 💡 BONUS G'OYALAR (CV'ni kuchaytiradi — imkon bo'lsa qo'sh)

1. **Jonli qidiruv autocomplete** (debounce + so'nggi qidiruvlar)
2. **"Yaqinda ko'rilgan mahsulotlar"** (localStorage)
3. **Taqqoslash** (compare) — 2–3 mahsulotni yonma-yon
4. **Kupon/promokod** tizimi
5. **Buyurtma holati timeline** (pending → paid → shipped → delivered, vizual)
6. **Dark mode** toggle
7. **PWA** — o'rnatiladigan, offline savat
8. **Real-time bildirishnoma** (buyurtma holati o'zgarganda — WebSocket/Django Channels)
9. **Tavsiya algoritmi** (oddiy: shu kategoriya/birga sotib olinganlar)
10. **Admin dashboard grafiklar** (savdo dinamikasi, top mahsulotlar — Recharts)
11. **SEO:** dinamik sitemap, OpenGraph/Twitter card, structured data (Product schema.org)
12. **Email chiroyli shablonlar** (buyurtma tasdiqi)
13. **Skeleton + Framer Motion sahifa o'tishlari** — premium his
14. **Stock kam qolganda "faqat 3 ta qoldi"** badge
15. **Mehmon savati login'da birlashishi** (guest → user merge)

---

*Boshlashdan oldin: monorepo strukturasini yarat, README'ga arxitektura rejasini yoz, keyin 15-bo'limdagi 1-bosqichdan boshla.*
