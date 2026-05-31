"""Demo ma'lumot to'ldiruvchi: kategoriya, brand, mahsulot, sharh, foydalanuvchi.

Ishlatish:  python manage.py seed_data
"""
import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.catalog.models import Brand, Category, Product, ProductImage
from apps.reviews.models import Review

User = get_user_model()

# (uz, ru, en, icon, [subkategoriyalar])
CATEGORY_TREE = [
    ("Elektronika", "Электроника", "Electronics", "smartphone",
     [("Smartfonlar", "Смартфоны", "Smartphones"),
      ("Noutbuklar", "Ноутбуки", "Laptops"),
      ("Quloqchinlar", "Наушники", "Headphones")]),
    ("Maishiy texnika", "Бытовая техника", "Home Appliances", "washing-machine",
     [("Muzlatgichlar", "Холодильники", "Refrigerators"),
      ("Changyutgichlar", "Пылесосы", "Vacuum cleaners")]),
    ("Moda", "Мода", "Fashion", "shirt",
     [("Erkaklar kiyimi", "Мужская одежда", "Men's clothing"),
      ("Ayollar kiyimi", "Женская одежда", "Women's clothing"),
      ("Poyabzal", "Обувь", "Footwear")]),
    ("Uy va bog'", "Дом и сад", "Home & Garden", "home",
     [("Mebel", "Мебель", "Furniture"),
      ("Oshxona", "Кухня", "Kitchen")]),
    ("Go'zallik", "Красота", "Beauty", "sparkles",
     [("Parfyumeriya", "Парфюмерия", "Perfume"),
      ("Parvarish", "Уход", "Skincare")]),
    ("Sport", "Спорт", "Sports", "dumbbell",
     [("Fitnes", "Фитнес", "Fitness"),
      ("Velosipedlar", "Велосипеды", "Bicycles")]),
    ("Bolalar", "Дети", "Kids", "baby",
     [("O'yinchoqlar", "Игрушки", "Toys")]),
    ("Avto tovarlar", "Автотовары", "Auto", "car",
     [("Aksessuarlar", "Аксессуары", "Accessories")]),
]

BRANDS = [
    "Samsung", "Apple", "Xiaomi", "LG", "Sony", "Nike", "Adidas",
    "Bosch", "Philips", "Huawei", "Zara", "HP",
]

# Mahsulot nomlari shablonlari kategoriya kodi bo'yicha
PRODUCT_TEMPLATES = {
    "Smartphones": [("Smartfon", "Смартфон", "Smartphone")],
    "Laptops": [("Noutbuk", "Ноутбук", "Laptop")],
    "Headphones": [("Simsiz quloqchin", "Беспроводные наушники", "Wireless headphones")],
    "Refrigerators": [("Muzlatgich", "Холодильник", "Refrigerator")],
    "Vacuum cleaners": [("Changyutgich", "Пылесос", "Vacuum cleaner")],
    "Men's clothing": [("Erkaklar futbolkasi", "Мужская футболка", "Men's t-shirt")],
    "Women's clothing": [("Ayollar ko'ylagi", "Женское платье", "Women's dress")],
    "Footwear": [("Krossovka", "Кроссовки", "Sneakers")],
    "Furniture": [("Divan", "Диван", "Sofa")],
    "Kitchen": [("Idishlar to'plami", "Набор посуды", "Cookware set")],
    "Perfume": [("Atir", "Парфюм", "Perfume")],
    "Skincare": [("Yuz kremi", "Крем для лица", "Face cream")],
    "Fitness": [("Gantel to'plami", "Набор гантелей", "Dumbbell set")],
    "Bicycles": [("Tog' velosipedi", "Горный велосипед", "Mountain bike")],
    "Toys": [("Konstruktor", "Конструктор", "Building blocks")],
    "Accessories": [("Avto registrator", "Видеорегистратор", "Dash cam")],
}

DESC = {
    "uz": "Yuqori sifatli, original mahsulot. Rasmiy kafolat va tez yetkazib berish bilan.",
    "ru": "Высококачественный оригинальный товар. С официальной гарантией и быстрой доставкой.",
    "en": "High-quality original product. With official warranty and fast delivery.",
}


class Command(BaseCommand):
    help = "ZAMON MARKET uchun demo ma'lumot to'ldiradi."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write("Eski demo ma'lumot tozalanmoqda...")
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        brands = [
            Brand.objects.create(name_uz=b, name_ru=b, name_en=b) for b in BRANDS
        ]

        leaf_categories = []
        for order, (uz, ru, en, icon, subs) in enumerate(CATEGORY_TREE):
            parent = Category.objects.create(
                name_uz=uz, name_ru=ru, name_en=en, icon=icon, order=order
            )
            for s_uz, s_ru, s_en in subs:
                child = Category.objects.create(
                    name_uz=s_uz, name_ru=s_ru, name_en=s_en, parent=parent
                )
                leaf_categories.append(child)

        sku_n = 1000
        created = 0
        for cat in leaf_categories:
            templates = PRODUCT_TEMPLATES.get(cat.name_en, [("Mahsulot", "Товар", "Product")])
            n = random.randint(5, 9)
            for _ in range(n):
                t_uz, t_ru, t_en = random.choice(templates)
                brand = random.choice(brands)
                sku_n += 1
                model = f"{brand.name_en} {random.choice(['Pro', 'Max', 'Lite', 'Plus', 'X', 'S'])}{random.randint(1, 20)}"
                price = Decimal(random.randint(50, 2500) * 10000)
                has_discount = random.random() < 0.4
                discount = (
                    (price * Decimal(random.randint(75, 95)) / 100).quantize(Decimal("1"))
                    if has_discount else None
                )
                p = Product.objects.create(
                    name_uz=f"{t_uz} {model}",
                    name_ru=f"{t_ru} {model}",
                    name_en=f"{t_en} {model}",
                    description_uz=DESC["uz"],
                    description_ru=DESC["ru"],
                    description_en=DESC["en"],
                    category=cat,
                    brand=brand,
                    price=price,
                    discount_price=discount,
                    stock=random.randint(0, 80),
                    sku=f"SKU-{sku_n}",
                    rating=Decimal(str(round(random.uniform(3.8, 5.0), 1))),
                    reviews_count=random.randint(0, 240),
                    sold_count=random.randint(0, 1500),
                    is_featured=random.random() < 0.25,
                )
                # Galereya (Picsum placeholder — internet bo'lganda ko'rinadi)
                for o in range(random.randint(2, 4)):
                    seed = (sku_n * 10 + o)
                    ProductImage.objects.create(
                        product=p,
                        image_url=f"https://picsum.photos/seed/zm{seed}/600/600",
                        alt=p.name_uz,
                        order=o,
                    )
                created += 1

        # Foydalanuvchilar
        if not User.objects.filter(email="admin@zamon.uz").exists():
            User.objects.create_superuser(
                email="admin@zamon.uz", password="admin12345",
                first_name="Admin", role="admin",
            )
        demo_users = []
        for em, name in [("ali@demo.uz", "Ali"), ("vali@demo.uz", "Vali")]:
            u, _ = User.objects.get_or_create(
                email=em, defaults={"first_name": name, "role": "customer"}
            )
            u.set_password("demo12345")
            u.save()
            demo_users.append(u)

        # Demo sharhlar (tasdiqlangan)
        review_texts = {
            "uz": ["Zo'r mahsulot, tavsiya qilaman!", "Sifati a'lo, tez yetkazishdi.", "Narxiga arziydi."],
            "ru": ["Отличный товар!", "Качество супер."],
        }
        for p in Product.objects.order_by("?")[:40]:
            for u in random.sample(demo_users, k=random.randint(1, 2)):
                Review.objects.get_or_create(
                    product=p, user=u,
                    defaults={
                        "rating": random.randint(4, 5),
                        "text": random.choice(review_texts["uz"]),
                        "is_verified": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor! {created} mahsulot, {len(leaf_categories)} kategoriya, "
            f"{len(brands)} brand yaratildi.\n"
            f"Admin: admin@zamon.uz / admin12345\n"
            f"Demo:  ali@demo.uz / demo12345"
        ))
