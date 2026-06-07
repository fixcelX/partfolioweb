"""Demo ma'lumot to'ldiruvchi: kategoriya, brand, mahsulot, sharh, foydalanuvchi.

105 ta haqiqiy mahsulot (real nom, tavsif va Unsplash rasmlari) bilan to'ldiradi.
Narx, chegirma, ombor, reyting kategoriya bo'yicha realistik tarzda generatsiya
qilinadi. Brand mahsulot nomidan avtomatik aniqlanadi.

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

# Kategoriya nomi -> (ru, en, lucide ikon). Tartib = ko'rinish tartibi.
CATEGORY_META = {
    "Smartfonlar": ("Смартфоны", "Smartphones", "smartphone"),
    "Gadjetlar": ("Гаджеты", "Gadgets", "watch"),
    "Texnologiyalar": ("Технологии", "Technology", "laptop"),
    "Kiyim-kechak": ("Одежда", "Clothing", "shirt"),
    "Sport buyumlari": ("Спорттовары", "Sports goods", "dumbbell"),
    "Maishiy texnika": ("Бытовая техника", "Home appliances", "washing-machine"),
    "Go'zallik va parvarish": ("Красота и уход", "Beauty & care", "sparkles"),
    "Oshxona buyumlari": ("Товары для кухни", "Kitchenware", "utensils"),
    "Avtoulov jihozlari": ("Автотовары", "Auto accessories", "car"),
    "Poyabzallar": ("Обувь", "Footwear", "footprints"),
    "Kompyuter jihozlari": ("Компьютерные комплектующие", "Computer parts", "cpu"),
    "Sport va salomatlik": ("Спорт и здоровье", "Sport & health", "activity"),
    "Aksessuarlar": ("Аксессуары", "Accessories", "glasses"),
    "Bolalar uchun": ("Детям", "For kids", "baby"),
    "Geyming": ("Гейминг", "Gaming", "gamepad-2"),
    "Uy jihozlari": ("Товары для дома", "Home goods", "home"),
    "Kitoblar": ("Книги", "Books", "book-open"),
    "Asbob-uskunalar": ("Инструменты", "Tools", "wrench"),
    "Aqlli uy": ("Умный дом", "Smart home", "lightbulb"),
}

# Narx oralig'i (so'm) kategoriya bo'yicha
PRICE_RANGES = {
    "Smartfonlar": (2_500_000, 17_000_000),
    "Gadjetlar": (250_000, 5_500_000),
    "Texnologiyalar": (450_000, 28_000_000),
    "Kiyim-kechak": (150_000, 2_500_000),
    "Sport buyumlari": (90_000, 1_800_000),
    "Maishiy texnika": (700_000, 11_000_000),
    "Go'zallik va parvarish": (90_000, 6_500_000),
    "Oshxona buyumlari": (120_000, 2_800_000),
    "Avtoulov jihozlari": (150_000, 2_400_000),
    "Poyabzallar": (300_000, 2_600_000),
    "Kompyuter jihozlari": (200_000, 3_800_000),
    "Sport va salomatlik": (150_000, 6_500_000),
    "Aksessuarlar": (120_000, 3_500_000),
    "Bolalar uchun": (120_000, 1_900_000),
    "Geyming": (250_000, 4_200_000),
    "Uy jihozlari": (80_000, 1_400_000),
    "Kitoblar": (49_000, 180_000),
    "Asbob-uskunalar": (180_000, 3_200_000),
    "Aqlli uy": (90_000, 2_600_000),
}

# Brand nomidan aniqlash uchun kalit so'zlar (eng spetsifikdan boshlab)
BRAND_KEYWORDS = [
    "New Balance", "Under Armour", "Ray-Ban", "Galaxy Buds", "Galaxy",
    "Apple", "Samsung", "Xiaomi", "Google Pixel", "OnePlus", "Sony", "JBL",
    "Anker", "ASUS", "Logitech", "Keychron", "HyperX", "Nike", "Adidas",
    "Levi's", "Casio", "Dyson", "L'Oreal", "Philips", "Cerave", "Chanel",
    "Tefal", "Kukmara", "Stanley", "Bosch", "Braun", "Baseus", "Makita",
    "DeLonghi", "Redmond", "Timberland", "Yandex", "Aqara", "Kingston",
    "TP-Link", "Cougar", "SteelSeries", "Xbox", "LEGO", "Triand", "70mai",
]
# Aniqlangan kalitni normalizatsiya qilingan brand nomiga moslash
BRAND_NORMALIZE = {
    "Galaxy": "Samsung", "Galaxy Buds": "Samsung",
    "Google Pixel": "Google", "Xbox": "Microsoft", "70mai": "Xiaomi",
}

# (kategoriya, nom, tavsif, rasm_url)
PRODUCTS = [
    ("Smartfonlar", "Smartfon Apple iPhone 15 Pro 128GB Natural Titanium", "A17 Pro chipli, 120 Gts chastotali Super Retina XDR ekranli premium smartfon. Uch kamerali tizim va titan korpus.", "https://images.unsplash.com/photo-1695048133142-1a20484d2569?auto=format&fit=crop&w=800&q=80"),
    ("Smartfonlar", "Smartfon Samsung Galaxy S24 Ultra 12/256GB Black", "O'rnatilgan S Pen stilusli va Galaxy AI sun'iy intellekt funksiyalariga ega flagman. 200 MP asosiy kamera.", "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?auto=format&fit=crop&w=800&q=80"),
    ("Smartfonlar", "Smartfon Xiaomi Redmi Note 13 Pro 8/256GB Black", "AMOLED ekran, 200 MP kamera va 67W tezkor quvvatlash tizimiga ega eng xaridorgir hamyonbop model.", "https://images.unsplash.com/photo-1598327105666-5b89351aff97?auto=format&fit=crop&w=800&q=80"),
    ("Smartfonlar", "Smartfon Google Pixel 8 Pro 12/128GB Obsidian", "Toza Android tizimi, Tensor G3 protsessori va mobil fotografiya uchun eng ilg'or Google AI kameralari.", "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=800&q=80"),
    ("Smartfonlar", "Smartfon OnePlus 12 16/512GB Silky Black", "Snapdragon 8 Gen 3 protsessori, 5400 mA/soat batareya va ultra tezkor 100W quvvatlagich bilan jihozlangan monster.", "https://images.unsplash.com/photo-1565630916779-e303be97b6f5?auto=format&fit=crop&w=800&q=80"),
    ("Gadjetlar", "Aqlli soat Apple Watch Series 9 GPS 45mm Midnight", "Sog'liq monitoringi, EKG, qon kislorodini o'lchash funksiyalari va imo-ishora bilan boshqarish tizimi.", "https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=800&q=80"),
    ("Gadjetlar", "Smart-braslet Xiaomi Smart Band 8 Black", "1.62 dyuymli AMOLED ekran, 150 tadan ortiq sport rejimlari va 16 kungacha yetadigan batareya quvvati.", "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?auto=format&fit=crop&w=800&q=80"),
    ("Gadjetlar", "Simsiz quloqchinlar Apple AirPods Pro 2 USB-C", "Faol shovqinni bostirish (ANC) va adaptiv shaffoflik rejimiga ega eng mashhur premium quloqchinlar.", "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?auto=format&fit=crop&w=800&q=80"),
    ("Gadjetlar", "Simsiz quloqchinlar Samsung Galaxy Buds2 Pro Graphite", "24-bitli Hi-Fi audio tizimi, ixcham dizayn va ergonamik korpusga ega premium quloqchinlar.", "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?auto=format&fit=crop&w=800&q=80"),
    ("Gadjetlar", "Tashqi akkumulyator Anker PowerCore 20000 mAh 22.5W", "Ikki dona USB-A va bitta Power Delivery USB-C portiga ega tezkor quvvatlovchi ixcham powerbank.", "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Noutbuk Apple MacBook Air 13 M3 8/256GB Space Gray", "M3 chipli energiya tejamkor noutbuk. Kulerlarsiz mutlaqo shovqinsiz ishlaydi, batareyasi 18 soatga yetadi.", "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "O'yin noutbuki ASUS ROG Strix G16 Core i7/RTX 4060", "Intel Core i7 protsessori va NVIDIA RTX 4060 videokartasi bilan jihozlangan yuqori unumdorlikdagi o'yin noutbuki.", "https://images.unsplash.com/photo-1603302576837-37561b2e2302?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "O'yin konsoli Sony PlayStation 5 Slim 1TB", "Yangi ixcham dizayndagi 4K o'yin konsoli. Ultra-tezkor SSD va komplektda 1 dona DualSense kontrolleri.", "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "O'yin sichqonchasi Logitech G Pro X Superlight White", "Kibersportchilar uchun atalgan, bor-yo'g'i 63 gramm og'irlikdagi ultra-engil simsiz professional sichqoncha.", "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Mexanik klaviatura Keychron K2 RGB Wireless", "Gateron Brown svitchlariga ega, Mac va Windows uchun to'liq mos keladigan simsiz ixcham mexanik klaviatura.", "https://images.unsplash.com/photo-1587829741301-dc798b83add3?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Monitor 27\" LG UltraGear 27GP850 Nano IPS", "180 Gts yangilanish chastotasi va 1 ms javob berish vaqtiga ega professional 2K geyming monitor.", "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Portativ kolonka JBL Flip 6 Black", "IP67 suv va changdan himoya standartiga ega, kuchli basli ikki tomonlama portativ dinamik tizimi.", "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Tizimli blok (Kompyuter) HyperX PC Core i5 / RTX 3060", "O'yinlar va strimlar uchun mo'ljallangan, shaffof korpusli va RGB yoritgichli tayyor o'yin shassisi.", "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Simsiz quloqchin Sony WH-1000XM5 Black", "Bozordagi eng eng kuchli shovqin bostirish (ANC) tizimiga ega, to'liq o'lchamli premium quloqchinlar.", "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=800&q=80"),
    ("Texnologiyalar", "Videoregistrator Xiaomi 70mai Dash Cam Pro Plus A500S", "O'rnatilgan GPS moduliga ega, 2.7K o'lchamda tunda ham tiniq tasvirga oladigan avtomobil registratori.", "https://images.unsplash.com/photo-1508974239320-0a029497e820?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Erkaklar xudisi (Hoodie) Oversize Black Premium", "Uch ipli zich va yumshoq futer matosidan tikilgan, qulay va minimalist kundalik kiyim.", "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Krossovka Nike Air Force 1 '07 All White", "Tabiiy charmdan tikilgan, har qanday kiyim uslubiga mos tushuvchi afsonaviy klassik krossovkalar.", "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Ayollar klassik trenchkoti Beige Oversize", "Suv va shamol o'tkazmaydigan materialdan tayyorlangan, bahor va kuz mavsumiga mos elegant trench.", "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Erkaklar sport kostyumi Adidas Originals Gray", "Yumshoq trikotaj matodan tikilgan, sport zali va kundalik sayrlar uchun qulay olimpiyka va shim to'plami.", "https://images.unsplash.com/photo-1483721310020-03333e577078?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Krossovka New Balance 530 White/Silver", "Retro uslubdagi, havo o'tkazuvchan to'rli materialdan tayyorlangan eng qulay yurish krossovkalari.", "https://images.unsplash.com/photo-1539185441755-769473a23570?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Ayollar trikotaj kostyumi Keng shim va ko'fta", "Kuzgi va bahorgi mavsum uchun juda yumshoq, qulay va keng bichimdagi zamonaviy to'plam.", "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Erkaklar charm ko'rtkasi (Koja) Bomber Black", "Ekologik toza va chidamli premium charmdan tikilgan, zamonaviy va qat'iy uslubdagi kurtka.", "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Klassik erkaklar ko'ylagi Slim Fit White", "95% paxtadan tayyorlangan, ofis, maktab va rasmiy tadbirlar uchun tana shakliga mos keluvchi ko'ylak.", "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Ayollar kechki ko'ylagi (Platye) Elegant Black", "Tantanali marosimlar va kechki uchrashuvlar uchun mo'ljallangan nafis va jozibali siluetli ko'ylak.", "https://images.unsplash.com/photo-1566174053879-31528523f8ae?auto=format&fit=crop&w=800&q=80"),
    ("Kiyim-kechak", "Erkaklar jinsi shimi Levi's 511 Slim Fit", "Sifatli va mustahkam denim matosidan tikilgan, yuvganda rangi o'chmaydigan klassik ko'k jinsi.", "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=800&q=80"),
    ("Sport buyumlari", "Yoga va fitnes gilamchasi (Mat) TPE 6mm Grey", "Sirg'almaydigan, ekologik xavfsiz va bo'g'imlarni qattiq poldan himoya qiluvchi qalin fitnes mat.", "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?auto=format&fit=crop&w=800&q=80"),
    ("Sport buyumlari", "Yig'iladigan gantellar to'plami 2 x 10 kg", "Uy sharoitida mushaklarni rivojlantirish uchun og'irligi sozlanadigan, plastik qoplangan sementli gantellar.", "https://images.unsplash.com/photo-1638536532686-d610adfc8e5c?auto=format&fit=crop&w=800&q=80"),
    ("Sport buyumlari", "Fitnes rezinalari to'plami (Rezinoviy jgut) 5 ta yuklama", "Oyoq va dumba mushaklari uchun har xil qarshilik darajasiga ega bo'lgan lateksli sport rezinalari.", "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=800&q=80"),
    ("Sport buyumlari", "Sport shortigi va futbolkasi to'plami Erkaklar uchun", "Tez quriydigan va terni o'ziga yutmaydigan, yugurish va krossfit uchun maxsus sintetik mato.", "https://images.unsplash.com/photo-1556817411-31ae72fa3ea0?auto=format&fit=crop&w=800&q=80"),
    ("Sport buyumlari", "Sport sumkasi (Bag) Under Armour Water-Resistant", "Oyoq kiyim uchun alohida ventilyatsiyali cho'ntakka ega, suv o'tkazmaydigan sig'imli sport sumkasi.", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80"),
    ("Maishiy texnika", "Robot-changyutgich Xiaomi Robot Vacuum S10", "LDS navigatsiyali, 4000 Pa so'rish quvvatiga ega, ham quruq, ham namli tozalash qiluvchi aqlli changyutgich.", "https://images.unsplash.com/photo-1558317374-067fb5f30001?auto=format&fit=crop&w=800&q=80"),
    ("Maishiy texnika", "Aqlli televizor Xiaomi TV A2 43\" Smart Android", "4K Ultra HD o'lchamli, ingichka romsiz dizayndagi va Google Assistant ovozli boshqaruviga ega televizor.", "https://images.unsplash.com/photo-1593305841991-05c297ba4575?auto=format&fit=crop&w=800&q=80"),
    ("Maishiy texnika", "Havo namlagich Xiaomi Smart Humidifier 2", "Ultratovushli, antibakterial UV-C nurli va smartfon orqali boshqariladigan 4.5 litrli havo namlagich.", "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80"),
    ("Maishiy texnika", "Kofe qaynatgich DeLonghi Dedica EC 685.M", "Yumshoq va quyuq ko'pikli kapuchino hamda espresso tayyorlaydigan ixcham va zamonaviy kofe mashinasi.", "https://images.unsplash.com/photo-1517142089942-ba376ce32a2e?auto=format&fit=crop&w=800&q=80"),
    ("Maishiy texnika", "Multipishirgich (Multivarka) Redmond RMC-M90", "45 ta pishirish rejimiga ega, non, sho'rva va dimlamalarni tayyorlay oladigan idishli multipishirgich.", "https://images.unsplash.com/photo-1584269600464-37b1b58a9fe7?auto=format&fit=crop&w=800&q=80"),
    ("Go'zallik va parvarish", "Fen Dyson Supersonic HD15 Nickel/Copper", "Sochlarni haddan tashqari qizib ketishdan himoya qiluvchi va tez qurituvchi afsonaviy premium fen.", "https://images.unsplash.com/photo-1621184455862-c163dfb30e0f?auto=format&fit=crop&w=800&q=80"),
    ("Go'zallik va parvarish", "Soch tekislovchi (Utjug) L'Oreal Professionnel Steampod 3.0", "Sochga zarar yetkazmasdan par yordamida professional darajada tekislovchi stayler.", "https://images.unsplash.com/photo-1522338242992-e1a54906a8da?auto=format&fit=crop&w=800&q=80"),
    ("Go'zallik va parvarish", "Erkaklar uchun trimmer Philips Series 7000 14-in-1", "Soqol, soch va tana tuklarini tozalash uchun zanglamas po'lat pichoqli universal trimmer to'plami.", "https://images.unsplash.com/photo-1621607512214-68297480165e?auto=format&fit=crop&w=800&q=80"),
    ("Go'zallik va parvarish", "Yuz uchun namlovchi krem Cerave Moisturizing Cream", "Quruq va juda quruq terilar uchun gipoallergenik, parabenlarsiz va dermatologlar tomonidan tavsiya etilgan krem.", "https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=800&q=80"),
    ("Go'zallik va parvarish", "Parfumeriya suvi Bleu de Chanel EDP 100ml", "Erkaklar uchun yog'ochli-tsitrusli klassik, uzoq muddat saqlanib turuvchi premium atir.", "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=800&q=80"),
    ("Oshxona buyumlari", "Pichoqlar to'plami Tefal Ice Force 5 dona + stend", "Muzli chiniqtirish texnologiyasi yordamida tayyorlangan, zanglamas po'latdan yasalgan professional pichoqlar.", "https://images.unsplash.com/photo-1593618998160-e34014e67546?auto=format&fit=crop&w=800&q=80"),
    ("Oshxona buyumlari", "Tovoqlar to'plami (Skovoroda) Kukmara Granit 2 ta", "Yopishmaydigan ultra-bardoshli granit qoplamali, qalin devorli quyma alyuminiy tovoqlar to'plami.", "https://images.unsplash.com/photo-1585515320310-259814833e62?auto=format&fit=crop&w=800&q=80"),
    ("Oshxona buyumlari", "Termos zanglamas po'latdan Stanley Classic 1L", "Issiq yoki sovuq ichimliklarni 24 soat davomida saqlab bera oladigan afsonaviy Amerika brendi termosi.", "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=800&q=80"),
    ("Oshxona buyumlari", "Elektr choynak Bosch Twinix 1.7L Black", "Suvsiz yoqishdan himoya tizimi va yashirin isitish elementiga ega ergonomik elektr choynak.", "https://images.unsplash.com/photo-1576092768241-dec231879fc3?auto=format&fit=crop&w=800&q=80"),
    ("Oshxona buyumlari", "Blender to'plami Braun MultiQuick 7", "Aqlli tezlikni boshqarish tizimiga ega, maydalagich va ko'pirtirgichli 1000 Vt quvvatli blender.", "https://images.unsplash.com/photo-1578643463396-0997cb5328c1?auto=format&fit=crop&w=800&q=80"),
    ("Avtoulov jihozlari", "Avtomobil kompressori (Nasos) Xiaomi 70mai Air Compressor", "Belgilangan bosimga yetganda avtomatik o'chadigan, displeyli va ixcham metall korpusli elektr nasos.", "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?auto=format&fit=crop&w=800&q=80"),
    ("Avtoulov jihozlari", "Avtomobil changyutgichi Baseus Capsule Wireless", "Mashina salonidagi yetib borish qiyin bo'lgan joylarni osongina tozalaydigan kuchli simsiz changyutgich.", "https://images.unsplash.com/photo-1607860108855-64acf2078ed9?auto=format&fit=crop&w=800&q=80"),
    ("Avtoulov jihozlari", "Telefon uchun avto-tayanch Magsafe simsiz quvvatlagichli", "Mashina havo yo'naltirgichiga o'rnatiladigan, telefonni magnitda mustahkam ushlab quvvatlovchi jihoz.", "https://images.unsplash.com/photo-1586105251261-72a756497a11?auto=format&fit=crop&w=800&q=80"),
    ("Avtoulov jihozlari", "Avtomobil video-registratori Xiaomi Mi Dash Cam 2", "140 darajali keng ko'rish burchagi va 2K sifatli yozuv tizimiga ega ixcham va ishonchli registrator.", "https://images.unsplash.com/photo-1449965408869-eaa3f722e40d?auto=format&fit=crop&w=800&q=80"),
    ("Avtoulov jihozlari", "Eva korriklari to'plami Chevrolet Gentra uchun", "Suv va loyni o'z kataklarida mukammal ushlab qoluvchi, individual o'lchamdagi premium Eva gilamchalari.", "https://images.unsplash.com/photo-1549399542-7e3f8b79c341?auto=format&fit=crop&w=800&q=80"),
    ("Poyabzallar", "Erkaklar klassik tuflisi Jigarrang charm", "Toza charmdan tikilgan, to'y va rasmiy uchrashuvlar uchun kostyum-shimga mos keluvchi tufli.", "https://images.unsplash.com/photo-1533867617858-e7b97e060509?auto=format&fit=crop&w=800&q=80"),
    ("Poyabzallar", "Ayollar baland poshnali tuflisi (Lodochki) Black Premium", "Klassik 7 sm poshnali, zamsh matoli, har qanday kechki ko'ylakka mos keladigan oqlangan tufli.", "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?auto=format&fit=crop&w=800&q=80"),
    ("Poyabzallar", "Yozgi erkaklar mokasinlari (Lofers) Beige", "Yumshoq, teshikchali havo o'tkazuvchan tabiiy zamshdan qilingan qulay yozgi poyabzal.", "https://images.unsplash.com/photo-1614252369475-531eba835eb1?auto=format&fit=crop&w=800&q=80"),
    ("Poyabzallar", "Ayollar yozgi sandaliyasi (Bosanojka) White", "Yengil platformali, yumshoq bog'ichli va kundalik kiyishga mo'ljallangan qulay yozgi sandaliya.", "https://images.unsplash.com/photo-1560343090-f0409e92791a?auto=format&fit=crop&w=800&q=80"),
    ("Poyabzallar", "Erkaklar qishki botinkasi Timberland Waterproof Brown", "Ichki qismi qalin mo'ynali, suv o'tkazmaydigan va muzlamaydigan mustahkam qishki botinka.", "https://images.unsplash.com/photo-1520639888713-7851133b1ed0?auto=format&fit=crop&w=800&q=80"),
    ("Kompyuter jihozlari", "Tashqi qattiq disk (HDD) WD Elements 1TB", "USB 3.0 interfeysiga ega, shaxsiy arxiv va katta hajmdagi fayllarni saqlash uchun portativ disk.", "https://images.unsplash.com/photo-1531492746076-161ca9bcad58?auto=format&fit=crop&w=800&q=80"),
    ("Kompyuter jihozlari", "Tezkor xotira Kingston FURY Beast DDR4 16GB To'plam", "3200 MGts chastotali, radiatorli va o'yin kompyuterlari unumdorligini oshiruvchi RAM xotira.", "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=800&q=80"),
    ("Kompyuter jihozlari", "Wi-Fi Router TP-Link Archer AX23 Wi-Fi 6", "Yangi avlod Wi-Fi 6 standartidagi, uydagi barcha qurilmalarga uzluksiz yuqori tezlik beruvchi router.", "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?auto=format&fit=crop&w=800&q=80"),
    ("Kompyuter jihozlari", "Ichki SSD drayv Samsung 980 Pro 1TB NVMe M.2", "7000 MB/s gacha o'qish tezligiga ega, Windows va o'yinlarni soniyalarda yuklovchi o'ta tezkor SSD.", "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=800&q=80"),
    ("Kompyuter jihozlari", "Veb-kamera Logitech C922 Pro Stream Full HD", "Strimlar va onlayn darslar uchun 1080p 30fps formatida tiniq tasvir uzatuvchi professional kamera.", "https://images.unsplash.com/photo-1623949556303-b0d17d198863?auto=format&fit=crop&w=800&q=80"),
    ("Sport va salomatlik", "Aqlli tana tarozi Xiaomi Mi Body Composition Scale 2", "Vazndan tashqari tanadagi yog', mushak va suv foizini aniqlab beruvchi Bluetooth aqlli tarozisi.", "https://images.unsplash.com/photo-1574269909862-7e1d70bb8078?auto=format&fit=crop&w=800&q=80"),
    ("Sport va salomatlik", "Massaj pistoleti (Massage Gun) Fascial Gun Black", "Mashg'ulotlardan so'ng mushaklardagi og'riq va charchoqni qoldiruvchi 4 xil nasadkali perkusion massajchi.", "https://images.unsplash.com/photo-1600881333168-2ef49b341f30?auto=format&fit=crop&w=800&q=80"),
    ("Sport va salomatlik", "Velotrenajyor uy uchun Ixcham Magnitli", "Uy sharoitida kardiomashqlar qilish va ozish uchun mo'ljallangan, yuklamasi sozlanadigan velotrenajyor.", "https://images.unsplash.com/photo-1591291621164-2c6367723315?auto=format&fit=crop&w=800&q=80"),
    ("Sport va salomatlik", "Sport uchun Blender-Sheyker (Shaker Bottle)", "Protein va geyner kukunlarini bo'lakchalarsiz mukammal aralashtiruvchi to'rli sport idishi.", "https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=800&q=80"),
    ("Sport va salomatlik", "Yugurish yo'lakchasi (Begovaya dorojka) WalkingPad R1 Pro", "Katlanadigan ixcham dizayn, smartfon orqali boshqaruv va uydan chiqmay jismoniy holatni tiklash imkoniyati.", "https://images.unsplash.com/photo-1576678927484-cc907957088c?auto=format&fit=crop&w=800&q=80"),
    ("Aksessuarlar", "Erkaklar hamyoni (Koshelyok) Tabiiy charm Black", "Karta va naqd pullar uchun maxsus bo'lmalarga ega, RFID himoyali klassik erkaklar hamyoni.", "https://images.unsplash.com/photo-1627123424574-724758594e93?auto=format&fit=crop&w=800&q=80"),
    ("Aksessuarlar", "Quyoshdan himoyalovchi ko'zoynak Ray-Ban Aviator Classic", "UV400 quyosh nurlaridan 100% himoya qiluvchi, metal ramkali dunyoga mashhur ko'zoynak.", "https://images.unsplash.com/photo-1511499767150-a48a237f0083?auto=format&fit=crop&w=800&q=80"),
    ("Aksessuarlar", "Erkaklar qo'l soati Casio Edifice Chronograph", "Kvars mexanizmiga ega, kvarts oynali va 100 metrgacha suv o'tkazmaydigan po'lat qo'l soati.", "https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?auto=format&fit=crop&w=800&q=80"),
    ("Aksessuarlar", "Noutbuk uchun ryukzak Xiaomi Classic Business Backpack", "15.6 dyuymli noutbuk sig'adigan, suv o'tkazmaydigan matoli mustahkam biznes ryukzak.", "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=800&q=80"),
    ("Aksessuarlar", "Soyabon (Zont) Avtomat Xiaomi WD1 90 points", "Birgina tugmani bosish orqali avtomatik ochilib-yopiladigan, kuchli shamolga chidamli soyabon.", "https://images.unsplash.com/photo-1515694346937-94d85e41e6f0?auto=format&fit=crop&w=800&q=80"),
    ("Bolalar uchun", "Bolalar aqlli soati (Smart watch) GPS trekerli", "Ota-onalar uchun bolaning qayerdaligini ko'rish va qo'ng'iroq qilish imkonini beruvchi xavfsizlik soati.", "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"),
    ("Bolalar uchun", "Konstruktor LEGO City Politsiya uchastkasi", "Bolalarning mantiqiy fikrlashini rivojlantiruvchi, sifatli plastik detallardan iborat LEGO to'plami.", "https://images.unsplash.com/photo-1587654780291-39c9404d746b?auto=format&fit=crop&w=800&q=80"),
    ("Bolalar uchun", "Bolalar samokati Triand Scutter Chiroqli g'ildiraklar", "Balandligi sozlanadigan, harakatlanganda g'ildiraklari rangli yonadigan xavfsiz bolalar samokati.", "https://images.unsplash.com/photo-1516627145497-ae6968895b74?auto=format&fit=crop&w=800&q=80"),
    ("Bolalar uchun", "Radioboshqaruvli mashina Monster Truck 4WD", "Masofadan pult orqali boshqariladigan, har qanday to'siqlardan o'ta oladigan katta g'ildirakli jip.", "https://images.unsplash.com/photo-1594787318286-3d835c1d207f?auto=format&fit=crop&w=800&q=80"),
    ("Bolalar uchun", "Rasm chizish to'plami chemodanda 150 ta detal", "Flomasterlar, qalamlar, akvarel buyoqlari va barcha chizish asboblarini o'z ichiga olgan katta to'plam.", "https://images.unsplash.com/photo-1513364776144-60967b0f800f?auto=format&fit=crop&w=800&q=80"),
    ("Geyming", "Geymerlar uchun stul (Kreslo) Cougar Armor One", "Orqa qismi 180 darajaga bukiladigan, uzoq vaqt kompyuter qarshisida o'tirganda belni og'ritmaydigan kreslo.", "https://images.unsplash.com/photo-1592078615290-033ee584e267?auto=format&fit=crop&w=800&q=80"),
    ("Geyming", "O'yin mikrofoni HyperX QuadCast S RGB", "Strimlar, podkastlar va o'yin ichidagi aloqa uchun ideal va tiniq ovoz yozuvchi RGB yoritgichli mikrofon.", "https://images.unsplash.com/photo-1590602847861-f357a9332bbc?auto=format&fit=crop&w=800&q=80"),
    ("Geyming", "O'yin quloqchini HyperX Cloud II Red", "7.1 virtual atrof-muhit ovoz tizimi va olinadigan mikrofoniga ega kibersport afsonasi.", "https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?auto=format&fit=crop&w=800&q=80"),
    ("Geyming", "Klaviatura sichqoncha kovriki (Pad) SteelSeries QcK XXL", "Sichqonchaning o'ta aniq harakatlanishini ta'minlovchi, tikilgan chetlarga ega ulkan sport kovriki.", "https://images.unsplash.com/photo-1629429407759-01cd3d7cfb38?auto=format&fit=crop&w=800&q=80"),
    ("Geyming", "O'yin joystiki (Gamepad) Xbox Wireless Controller Black", "PC va Xbox tizimlariga Bluetooth orqali tez ulanadigan eng qulay va ergonamik geympad.", "https://images.unsplash.com/photo-1580327344181-c1163234e5a0?auto=format&fit=crop&w=800&q=80"),
    ("Uy jihozlari", "Ortopedik yostiq (Anatomik) Memory Foam", "Bo'yin va bosh shaklini eslab qoluvchi, sog'lom uyqu va umurtqa xavfsizligi uchun maxsus yostiq.", "https://images.unsplash.com/photo-1631679706909-1844bbd07221?auto=format&fit=crop&w=800&q=80"),
    ("Uy jihozlari", "Yotoq choyshablari to'plami (Postelnoye belyo) Satina", "100% paxtadan tayyorlangan, ipakdek yumshoq va yuvganda o'z sifatini yo'qotmaydigan ikki kishilik to'plam.", "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=800&q=80"),
    ("Uy jihozlari", "Suyuq sovun tarqatuvchi (Dozator) Avtomat Sensorli", "Qo'lni yaqinlashtirganda avtomatik ravishda ko'pik beruvchi batareyalik zamonaviy sensorli dozator.", "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=800&q=80"),
    ("Uy jihozlari", "Devor soati Minimalist Wood Design", "Tabiiy yog'ochdan ishlangan, shovqinsiz silliq mexanizmga ega zamonaviy devor soati.", "https://images.unsplash.com/photo-1563861826100-9cb868fdbe1c?auto=format&fit=crop&w=800&q=80"),
    ("Uy jihozlari", "Aroma-diffuzor uy uchun (Tayoqchali xushbo'ylatgich)", "Yorqin va yoqimli hidlarni uzoq vaqt davomida xonaga taratib turuvchi tabiiy moyli diffuzor.", "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?auto=format&fit=crop&w=800&q=80"),
    ("Kitoblar", "Atom odatlar - Jeyms Klir (O'zbek tilida)", "Yaxshi odatlarni shakllantirish va yomonlaridan qutulishning eng oddiy va sinovdan o'tgan usullari haqida kitob.", "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=800&q=80"),
    ("Kitoblar", "Boy ota, kambag'al ota - Robert Kiyosaki", "Moliyaviy savodxonlikni oshirish va pullarni to'g'ri boshqarish bo'yicha dunyodagi №1 bestseller kitob.", "https://images.unsplash.com/photo-1592496431122-2349e0fbc666?auto=format&fit=crop&w=800&q=80"),
    ("Kitoblar", "Diqqat: Chalg'ituvchi dunyoda muvaffaqiyat sirlari", "Kal Nyuport qalamiga mansub, diqqatni jamlash va chuqur ishlash qobiliyatini rivojlantiruvchi qo'llanma.", "https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=800&q=80"),
    ("Kitoblar", "Stiv Jobs - Uolter Ayzekson tarjimasi", "Apple kompaniyasi asoschisining hayoti, ijodi va texnologiyalar olamidagi inqiloblari haqidagi to'liq biografiya.", "https://images.unsplash.com/photo-1589998059171-988d887df646?auto=format&fit=crop&w=800&q=80"),
    ("Kitoblar", "Sapiens: Insoniyatning qisqacha tarixi - Yuval Noy Harari", "Insoniyatning paydo bo'lishidan boshlab bugungi kungacha bo'lgan ijtimoiy va tarixiy rivojlanish bosqichlari.", "https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=800&q=80"),
    ("Asbob-uskunalar", "Shurupovert (Akkumulyatorli drel) Makita 18V", "Uy va qurilish ishlari uchun mo'ljallangan, kuchli akkumulyatorli professional shurup buragich.", "https://images.unsplash.com/photo-1504148455328-c376907d081c?auto=format&fit=crop&w=800&q=80"),
    ("Asbob-uskunalar", "Asboblar to'plami keysda 82 dona (Nabor instrumentov)", "Zanglamas xrom-vanadiy po'latdan tayyorlangan, barcha o'lchamdagi klyuchlar va golovkalar to'plami.", "https://images.unsplash.com/photo-1581244277943-fe4a9c777189?auto=format&fit=crop&w=800&q=80"),
    ("Asbob-uskunalar", "Lazerli o'lchagich (Ruletka) Bosch Professional 50m", "Masofani millimetrgacha aniqlikda tezkor o'lchaydigan professional lazerli elektron ruletka.", "https://images.unsplash.com/photo-1572981779307-38b8cabb2407?auto=format&fit=crop&w=800&q=80"),
    ("Asbob-uskunalar", "Yelim quroli (Kleymiy pistolet) 60W + 10 ta tayoqcha", "Qo'l mehnati, dizayn va mayda ta'mirlash ishlari uchun tez qizituvchi sifatli termoyelim quroli.", "https://images.unsplash.com/photo-1530124566582-a618bc2615dc?auto=format&fit=crop&w=800&q=80"),
    ("Asbob-uskunalar", "Elektr lobzik Total 800W Professional", "Yog'och, metall va plastmassa materiallarni turli burchak ostida qiyatib kesuvchi kuchli elektr lobzik.", "https://images.unsplash.com/photo-1426927308491-6380b6a9936f?auto=format&fit=crop&w=800&q=80"),
    ("Aqlli uy", "Aqlli rozetka Yandex Smart Plug Zigbee", "Alisa ovozli yordamchisi orqali uydagi istalgan texnikani masofadan yoqish va o'chirish uchun aqlli rozetka.", "https://images.unsplash.com/photo-1558002038-1055907df827?auto=format&fit=crop&w=800&q=80"),
    ("Aqlli uy", "Aqlli lampochka Xiaomi Mi Smart LED Bulb RGB", "Smartfon va ovoz orqali rangini (16 mln rang) va yorqinligini o'zgartirsa bo'ladigan ekonom lampochka.", "https://images.unsplash.com/photo-1550985543-f47f38aeee65?auto=format&fit=crop&w=800&q=80"),
    ("Aqlli uy", "Aqlli kolonka Yandex Stansiya Layt Alisa bilan", "Musiqa qo'yadigan, bolalarga ertak aytadigan va aqlli uyni boshqaradigan ovozli yordamchiga ega kolonka.", "https://images.unsplash.com/photo-1543512214-318c7553f230?auto=format&fit=crop&w=800&q=80"),
    ("Aqlli uy", "Harakat sensori Aqara Motion Sensor Zigbee", "Xonada harakat sezilganda chiroqlarni avtomatik yoqish yoki xavfsizlik signalizatsiyasini ishga tushirish datchigi.", "https://images.unsplash.com/photo-1545259741-2ea3ebf61fa3?auto=format&fit=crop&w=800&q=80"),
    ("Aqlli uy", "Aqlli eshik qulfi Xiaomi Smart Door Lock E10", "Barmoq izi, parol, NFC karta va smartfon orqali ochiladigan, uy xavfsizligini yuqori darajaga ko'taruvchi qulf.", "https://images.unsplash.com/photo-1622372738946-62e02505feb3?auto=format&fit=crop&w=800&q=80"),
]


def _detect_brand(title: str):
    low = title.lower()
    for kw in BRAND_KEYWORDS:
        if kw.lower() in low:
            return BRAND_NORMALIZE.get(kw, kw)
    return None


def _gen_price(category: str):
    lo, hi = PRICE_RANGES.get(category, (100_000, 2_000_000))
    base = random.randint(lo // 10_000, hi // 10_000) * 10_000
    return Decimal(base - 1_000)  # psixologik narx: ...9 000


def _gen_stock():
    r = random.random()
    if r < 0.10:
        return 0
    if r < 0.30:
        return random.randint(1, 4)
    return random.randint(5, 90)


def _image_variants(url: str):
    """Bitta Unsplash rasmidan galereya uchun bir nechta kesim varianti."""
    yield url
    sep = "&" if "?" in url else "?"
    yield f"{url}{sep}crop=entropy"
    yield f"{url}{sep}crop=edges"


class Command(BaseCommand):
    help = "ZAMON MARKET uchun 105 ta mahsulot bilan demo ma'lumot to'ldiradi."

    @transaction.atomic
    def handle(self, *args, **options):
        random.seed(42)
        self.stdout.write("Eski demo ma'lumot tozalanmoqda...")
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Brand.objects.all().delete()

        # Kategoriyalar (tekis — barchasi yuqori daraja)
        categories: dict[str, Category] = {}
        for order, (uz, (ru, en, icon)) in enumerate(CATEGORY_META.items()):
            categories[uz] = Category.objects.create(
                name_uz=uz, name_ru=ru, name_en=en, icon=icon, order=order
            )

        # Brendlar — mahsulot nomlaridan aniqlangan holda yaratiladi
        brands: dict[str, Brand] = {}

        def brand_for(title: str):
            name = _detect_brand(title)
            if not name:
                return None
            if name not in brands:
                brands[name] = Brand.objects.create(
                    name_uz=name, name_ru=name, name_en=name
                )
            return brands[name]

        sku_n = 1000
        created = 0
        for category, title, body, image_url in PRODUCTS:
            sku_n += 1
            price = _gen_price(category)
            discount = None
            if random.random() < 0.40:
                pct = random.randint(78, 93)
                raw = (price * Decimal(pct) / 100).quantize(Decimal("1"))
                discount = Decimal(int(raw) // 1000 * 1000 + 990)

            product = Product.objects.create(
                name_uz=title,
                name_ru=title,
                name_en=title,
                description_uz=body,
                description_ru=body,
                description_en=body,
                category=categories[category],
                brand=brand_for(title),
                price=price,
                discount_price=discount,
                stock=_gen_stock(),
                sku=f"ZM-{sku_n}",
                rating=Decimal(str(round(random.uniform(3.9, 5.0), 1))),
                reviews_count=random.randint(0, 450),
                sold_count=random.randint(0, 3000),
                is_featured=random.random() < 0.30,
            )
            for o, src in enumerate(_image_variants(image_url)):
                ProductImage.objects.create(
                    product=product, image_url=src, alt=title, order=o
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
        review_texts = [
            "Zo'r mahsulot, tavsiya qilaman!",
            "Sifati a'lo, tez yetkazishdi.",
            "Narxiga to'liq arziydi, rahmat.",
            "Original mahsulot, qadoq ham zo'r.",
            "Kutganimdan ham yaxshi chiqdi.",
        ]
        for p in Product.objects.order_by("?")[:50]:
            for u in random.sample(demo_users, k=random.randint(1, 2)):
                Review.objects.get_or_create(
                    product=p, user=u,
                    defaults={
                        "rating": random.randint(4, 5),
                        "text": random.choice(review_texts),
                        "is_verified": True,
                    },
                )

        self.stdout.write(self.style.SUCCESS(
            f"Tayyor! {created} mahsulot, {len(categories)} kategoriya, "
            f"{len(brands)} brand yaratildi.\n"
            f"Admin: admin@zamon.uz / admin12345\n"
            f"Demo:  ali@demo.uz / demo12345"
        ))
