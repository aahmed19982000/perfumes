"""
Management Command: import_flowry_products
==========================================
يستورد منتجات flowry.store لمشروع Django

الاستخدام:
    python manage.py import_flowry_products

ضعه في:
    your_app/management/commands/import_flowry_products.py
    (أي app موجود في INSTALLED_APPS)

متطلبات:
    pip install requests Pillow
"""

import os
import re
import uuid
import requests
from io import BytesIO
from urllib.parse import urlparse

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify

from products.models import Brand, Category, Product, ProductImage


# ══════════════════════════════════════════════════════════════════
# بيانات المنتجات المستخرجة من flowry.store
# ══════════════════════════════════════════════════════════════════

PRODUCTS_DATA = [
    # ── New Arrivals ──────────────────────────────────────────────
    {
        "name_en": "Tobacco Collection by IBRAQ",
        "name_ar": "مجموعة التبغ من إبراق",
        "brand": "IBRAQ",
        "price": "4800.00",
        "discount_price": "2750.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "رحلة عطرية عبر مجموعة التبغ الفاخرة من إبراق. مزيج فريد يجمع بين دفء التبغ وعمق المكونات الشرقية.",
        "description_en": "A scented journey across the Tobacco Collection by IBRAQ. A unique blend combining the warmth of tobacco with the depth of oriental ingredients.",
        "image_url": None,
        "slug_src": "tobacco-collection-by-ibraq",
    },
    {
        "name_en": "Sense Collection by LAVERNE",
        "name_ar": "مجموعة Sense من لافيرن",
        "brand": "LAVERNE",
        "price": "3800.00",
        "discount_price": "2350.00",
        "gender": "women",
        "collection": "new-arrival",
        "description_ar": "عطر مستوحى من زهرة ترقص كراقصة باليه… يجسد روح الأنوثة والحرية.",
        "description_en": "A fragrance inspired by a flower dancing like a ballet dancer… embodying the spirit of femininity and freedom.",
        "image_url": None,
        "slug_src": "sense-collection-by-laverne",
    },
    {
        "name_en": "Megamare by Orto Parisi",
        "name_ar": "ميجامار من أورتو باريسي للجنسين",
        "brand": "Orto Parisi",
        "price": "2500.00",
        "discount_price": "1499.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "عطر بحري فريد من أورتو باريسي. نوتات الطحالب البحرية والبرغموت والمسك.",
        "description_en": "A unique marine fragrance from Orto Parisi. Notes of sea algae, bergamot, and musk.",
        "image_url": None,
        "slug_src": "megamare-by-orto-parisi",
    },
    {
        "name_en": "Ani by Nishane",
        "name_ar": "أني من نيشان للجنسين",
        "brand": "Nishane",
        "price": "2800.00",
        "discount_price": "1580.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: الزنجبيل والبرغموت والفلفل الوردي. قلب العطر: الهيل والكشمش الأسود والورد التركي.",
        "description_en": "Top notes: Ginger, Bergamot, Pink Pepper. Heart: Cardamom, Black Currant, Turkish Rose.",
        "image_url": None,
        "slug_src": "ani-by-nishane",
    },
    {
        "name_en": "Arrogate Pink by Assaf",
        "name_ar": "أروجيت بينك من أساف للنساء",
        "brand": "Assaf",
        "price": "2200.00",
        "discount_price": "1499.00",
        "gender": "women",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: زهر البرتقال والنيرولي واللوز. قلب العطر: الياسمين والبنفسج والمشمش.",
        "description_en": "Top notes: Orange Blossom, Neroli, Almond. Heart: Jasmine, Violet, Apricot.",
        "image_url": None,
        "slug_src": "arrogate-pink-by-assaf",
    },
    {
        "name_en": "Marijuana by Byredo",
        "name_ar": "ماريجوانا من بيريدو للجنسين",
        "brand": "Byredo",
        "price": "2800.00",
        "discount_price": "1600.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: البوميلو والفلفل الأسود. قلب العطر: الماريجوانا. القاعدة: نجيل الهند وبالو سانتو.",
        "description_en": "Top notes: Pomelo, Black Pepper. Heart: Cannabis. Base: Vetiver, Palo Santo.",
        "image_url": None,
        "slug_src": "marijuana-by-byredo",
    },
    {
        "name_en": "Black Saffron by Byredo",
        "name_ar": "بلاك سافرون من بيريدو للجنسين",
        "brand": "Byredo",
        "price": "2800.00",
        "discount_price": "1600.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: الزعفران وتوت العرعر والجريب فروت. قلب العطر: الجلود والبنفسج الأسود.",
        "description_en": "Top notes: Saffron, Juniper Berry, Grapefruit. Heart: Leather, Black Violet.",
        "image_url": None,
        "slug_src": "black-saffron-by-byredo",
    },
    {
        "name_en": "Marassi Vibes Collection",
        "name_ar": "مجموعة مراسي فايبز",
        "brand": "Flowry",
        "price": "2800.00",
        "discount_price": "2599.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "ثلاثة عطور Premium لكل mood في الصيف… انتعاش الصبح، حضور النهار، وسحر الليل.",
        "description_en": "Three premium fragrances for every summer mood — morning freshness, daytime presence, and evening magic.",
        "image_url": None,
        "slug_src": "marassi-vibes-collection",
    },
    {
        "name_en": "God of Fire by Stephane Humbert Lucas",
        "name_ar": "جود أوف فاير من ستيفان هومبرت للجنسين",
        "brand": "Stephane Humbert Lucas",
        "price": "3600.00",
        "discount_price": "1600.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: المانجو والليمون والزنجبيل والتوت الأحمر. قلب العطر: الكومارين والياسمين وخشب الأرز.",
        "description_en": "Top: Mango, Lemon, Ginger, Red Berries. Heart: Coumarin, Jasmine, Cedarwood.",
        "image_url": None,
        "slug_src": "god-of-fire-by-stephane-humbert",
    },
    {
        "name_en": "Musamam Black Intense by Lattafa",
        "name_ar": "مسمام بلاك إنتنس من لطافة للجنسين",
        "brand": "Lattafa",
        "price": "2550.00",
        "discount_price": "1199.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: الخزامي وجوزة الطيب والمريمية والبرغموت. قلب: خشب الأرز وإبرة الراعي.",
        "description_en": "Top: Lavender, Nutmeg, Sage, Bergamot. Heart: Cedarwood, Geranium.",
        "image_url": None,
        "slug_src": "musamam-black-intense-by-lattafa",
    },
    {
        "name_en": "Hersh Lahab by Alezz Oud",
        "name_ar": "هرش لهب من عزيز عود للجنسين",
        "brand": "Alezz Oud",
        "price": "2150.00",
        "discount_price": "1199.00",
        "gender": "unisex",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: الريحان والفلفل الأسود ونجيل الهند. قلب: الجريب فروت وفلفل تيمور. القاعدة: الباتشولي.",
        "description_en": "Top: Basil, Black Pepper, Vetiver. Heart: Grapefruit, Timur Pepper. Base: Patchouli.",
        "image_url": None,
        "slug_src": "hersh-lahab-by-alezz-oud",
    },
    {
        "name_en": "The Most Wanted by Azzaro",
        "name_ar": "ذا موست ونتد من أزارو للرجال",
        "brand": "Azzaro",
        "price": "2850.00",
        "discount_price": "1199.00",
        "gender": "men",
        "collection": "new-arrival",
        "description_ar": "الإفتتاحية: الهيل. قلب العطر: الطوفي. القاعدة: خشب العنبر.",
        "description_en": "Top: Cardamom. Heart: Toffee. Base: Amberwood.",
        "image_url": None,
        "slug_src": "the-most-wanted-by-azzaro",
    },
    # ── Best Sellers ──────────────────────────────────────────────
    {
        "name_en": "Layton Parfums de Marly",
        "name_ar": "لايتون من بارفيومز دو مارلي للجنسين",
        "brand": "Parfums de Marly",
        "price": "1600.00",
        "discount_price": "1199.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: التفاح والخزامي والبرغموت والماندرين. قلب: إبرة الراعي والبنفسج والياسمين. القاعدة: الفانيليا.",
        "description_en": "Top: Apple, Lavender, Bergamot, Mandarin. Heart: Geranium, Violet, Jasmine. Base: Vanilla.",
        "image_url": "https://flowry.store/cdn/shop/files/layton-parfums-de-marly-llgnsyn-2646810.png",
        "slug_src": "37528",
    },
    {
        "name_en": "Valentino Uomo Born In Roma Intense",
        "name_ar": "فالنتينو أومو بورن إن روما إنتنس للرجال",
        "brand": "Valentino",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: الفانيليا. قلب العطر: الخزامي. القاعدة: نجيل الهند.",
        "description_en": "Top: Vanilla. Heart: Lavender. Base: Vetiver.",
        "image_url": "https://flowry.store/cdn/shop/files/valentino-uomo-born-in-roma-intense-valentino-llrgal-2617713.png",
        "slug_src": "valentino-uomo-born-in-roma-intense-valentino-llrjl",
    },
    {
        "name_en": "Emporio Armani Stronger With You Intensely",
        "name_ar": "إمبوريو أرماني ستروجر ويذ يو إنتنسلي للرجال",
        "brand": "Giorgio Armani",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: الفلفل الوردي والعرعر والبنفسج. قلب: الطوفي والقرفة والخزامي. القاعدة: الفانيليا وحبوب التونكا.",
        "description_en": "Top: Pink Pepper, Juniper, Violet. Heart: Toffee, Cinnamon, Lavender. Base: Vanilla, Tonka Bean.",
        "image_url": "https://flowry.store/cdn/shop/files/emporio-armani-stronger-with-you-intensely-giorgio-armani-llrgal-6259662.webp",
        "slug_src": "emporio-armani-stronger-with-you-intensely-giorgio-armani-llrjl",
    },
    {
        "name_en": "Khamrah Lattafa Perfumes Sealed Master Box",
        "name_ar": "خمرة لطافة - ماستر بوكس مغلق للجنسين",
        "brand": "Lattafa",
        "price": "2100.00",
        "discount_price": "1499.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: القرفة وجوزة الطيب والبرغموت. قلب: التمر وحلوى اللوز ومسك الروم. القاعدة: العنبر والمسك.",
        "description_en": "Top: Cinnamon, Nutmeg, Bergamot. Heart: Date, Marzipan, Rum Musk. Base: Amber, Musk.",
        "image_url": "https://flowry.store/cdn/shop/files/khamrah-lattafa-perfumes-sealed-master-box-llgnsyn-7140378.webp",
        "slug_src": "khamrah-lattafa-perfumes-sealed-master-box-lljnsyn",
    },
    {
        "name_en": "Sauvage Dior Sealed Master Box",
        "name_ar": "سوفاج ديور - ماستر بوكس مغلق للرجال",
        "brand": "Dior",
        "price": "2100.00",
        "discount_price": "1499.00",
        "gender": "men",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: برغموت كالابريا والفلفل. قلب: فلفل سيشوان والخزامي والفلفل الوردي ونجيل الهند. القاعدة: الباتشولي وإبرة الراعي.",
        "description_en": "Top: Calabrian Bergamot, Pepper. Heart: Sichuan Pepper, Lavender, Pink Pepper, Vetiver. Base: Patchouli, Geranium.",
        "image_url": "https://flowry.store/cdn/shop/files/sauvage-dior-sealed-master-box-llrgal-7983938.webp",
        "slug_src": "sauvage-dior-sealed-master-box-llrjl",
    },
    {
        "name_en": "Khamrah Qahwa Lattafa Perfumes",
        "name_ar": "خمرة قهوة لطافة للجنسين",
        "brand": "Lattafa",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: القرفة والهيل والزنجبيل. قلب: حلوى اللوز والفواكه المجففة والزهور البيضاء. القاعدة: المسك والعنبر.",
        "description_en": "Top: Cinnamon, Cardamom, Ginger. Heart: Marzipan, Dried Fruits, White Flowers. Base: Musk, Amber.",
        "image_url": "https://flowry.store/cdn/shop/files/khamrah-qahwa-lattafa-perfumes-llgnsyn-9096716.webp",
        "slug_src": "khamrah-qahwa-lattafa-perfumes",
    },
    {
        "name_en": "Dior Homme Parfum",
        "name_ar": "ديور أوم بارفيوم للرجال",
        "brand": "Dior",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: السوسن من توسكانا والبرتقال الإيطالي. قلب: الجلود والورد. القاعدة: خشب الصندل والأمبريت.",
        "description_en": "Top: Tuscan Iris, Italian Citrus. Heart: Leather, Rose. Base: Sandalwood, Ambrette.",
        "image_url": "https://flowry.store/cdn/shop/files/dior-homme-parfum-dior-llrgal-4064140.webp",
        "slug_src": "dior-homme-parfum-dior-llrjl",
    },
    {
        "name_en": "Tobacco Oud Tom Ford",
        "name_ar": "توباكو عود من توم فورد للجنسين",
        "brand": "Tom Ford",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: الويسكي. قلب: التوابل والقرفة والكزبرة. القاعدة: التبغ والعود والبخور وخشب الصندل.",
        "description_en": "Top: Whiskey. Heart: Spices, Cinnamon, Coriander. Base: Tobacco, Oud, Incense, Sandalwood.",
        "image_url": "https://flowry.store/cdn/shop/files/tobacco-oud-tom-ford-llgnsyn-5647502.webp",
        "slug_src": "tobacco-oud-tom-ford-lljnsyn",
    },
    {
        "name_en": "Imperial by Gissah 100ml",
        "name_ar": "إمبيريال من جيساه 100 مل للجنسين",
        "brand": "Gissah",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: البرغموت الصقلي والفلفل الوردي والدافانا. قلب: العود والعنبر الأبيض وإكليل الجبل. القاعدة: المسك.",
        "description_en": "Top: Sicilian Bergamot, Pink Pepper, Davana. Heart: Oud, White Amber, Rosemary. Base: Musk.",
        "image_url": "https://flowry.store/cdn/shop/files/imperial-by-gissah-100-ml-llgnsyn-9486277.webp",
        "slug_src": "imperial-by-gissah-lljnsn",
    },
    {
        "name_en": "Vanilla Sex Tom Ford",
        "name_ar": "فانيلا سكس من توم فورد للجنسين",
        "brand": "Tom Ford",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: اللوز المر. قلب: الفانيليا والنوتات الزهرية. القاعدة: الفانيليا Ultravanil™ وحبوب التونكا وخشب الصندل.",
        "description_en": "Top: Bitter Almond. Heart: Vanilla, Floral Notes. Base: Ultravanil™ Vanilla, Tonka Bean, Sandalwood.",
        "image_url": "https://flowry.store/cdn/shop/files/vanilla-sex-tom-ford-llgnsyn-2541617.webp",
        "slug_src": "vanilla-sex-tom-ford-lljnsyn",
    },
    {
        "name_en": "Wild Colt Assaf 200ml Master Box",
        "name_ar": "وايلد كولت أساف 200 مل ماستر بوكس للجنسين",
        "brand": "Assaf",
        "price": "2100.00",
        "discount_price": "1499.00",
        "gender": "unisex",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: الزعفران والجريب فروت والنعناع والفلفل الوردي والبرغموت. قلب: زهر البرتقال والزنجبيل.",
        "description_en": "Top: Saffron, Grapefruit, Mint, Pink Pepper, Bergamot. Heart: Orange Blossom, Ginger.",
        "image_url": "https://flowry.store/cdn/shop/files/wild-colt-assaf-200-ml-master-box-llgnsyn-8542781.webp",
        "slug_src": "wild-colt-assaf-200-ml-master-box",
    },
    {
        "name_en": "Born in Roma The Gold Uomo Valentino",
        "name_ar": "بورن إن روما ذا جولد أومو فالنتينو للرجال",
        "brand": "Valentino",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "best-seller",
        "description_ar": "الإفتتاحية: النوتات الشمسية والتوابل وجوزة الطيب. قلب: خشب الأرز من فرجينيا. القاعدة: المسك والعنبر.",
        "description_en": "Top: Solar Notes, Spices, Nutmeg. Heart: Virginia Cedarwood. Base: Musk, Amber.",
        "image_url": "https://flowry.store/cdn/shop/files/born-in-roma-the-gold-uomo-valentino-llrgal-7408451.webp",
        "slug_src": "born-in-roma-the-gold-uomo-valentino",
    },
    # ── For Men ───────────────────────────────────────────────────
    {
        "name_en": "Khamrah Lattafa Perfumes",
        "name_ar": "خمرة لطافة للجنسين",
        "brand": "Lattafa",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "men",
        "description_ar": "الإفتتاحية: القرفة وجوزة الطيب والبرغموت. قلب: التمر وحلوى اللوز ومسك الروم. القاعدة: العنبر والمسك.",
        "description_en": "Top: Cinnamon, Nutmeg, Bergamot. Heart: Date, Marzipan, Rum Musk. Base: Amber, Musk.",
        "image_url": None,
        "slug_src": "khamrah-lattafa-perfumes",
    },
    {
        "name_en": "Sauvage Dior",
        "name_ar": "سوفاج ديور للرجال",
        "brand": "Dior",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "men",
        "description_ar": "الإفتتاحية: برغموت كالابريا والفلفل. قلب: فلفل سيشوان والخزامي والفلفل الوردي ونجيل الهند. القاعدة: الباتشولي وإبرة الراعي وخشب الأرز.",
        "description_en": "Top: Calabrian Bergamot, Pepper. Heart: Sichuan Pepper, Lavender, Pink Pepper, Vetiver. Base: Patchouli, Geranium, Cedarwood.",
        "image_url": None,
        "slug_src": "sauvage-dior",
    },
    {
        "name_en": "Creed Aventus 100ml",
        "name_ar": "كريد أفنتوس 100 مل للرجال",
        "brand": "Creed",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "men",
        "description_ar": "الإفتتاحية: الأناناس والبرغموت والكشمش الأسود والتفاح. قلب: أخشاب البتولا والباتشولي والياسمين والورد. القاعدة: المسك والعنبر.",
        "description_en": "Top: Pineapple, Bergamot, Black Currant, Apple. Heart: Birch, Patchouli, Jasmine, Rose. Base: Musk, Amber.",
        "image_url": None,
        "slug_src": "creed-aventus",
    },
    {
        "name_en": "Dior Homme Intense",
        "name_ar": "ديور أوم إنتنس للرجال",
        "brand": "Dior",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "men",
        "collection": "men",
        "description_ar": "الإفتتاحية: الخزامي. قلب: السوسن والأمبريت والكمثرى. القاعدة: خشب الأرز ونجيل الهند.",
        "description_en": "Top: Lavender. Heart: Iris, Ambrette, Pear. Base: Cedarwood, Vetiver.",
        "image_url": None,
        "slug_src": "dior-homme-intense",
    },
    # ── For Women ─────────────────────────────────────────────────
    {
        "name_en": "Black Afgano Nasomatto",
        "name_ar": "بلاك أفجانو ناسوماتو للجنسين",
        "brand": "Nasomatto",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "women",
        "description_ar": "الإفتتاحية: القنب والنوتات الخضراء. قلب: الراتينجات والأخشاب والتبغ والقهوة. القاعدة: العود والبخور.",
        "description_en": "Top: Cannabis, Green Notes. Heart: Resins, Woods, Tobacco, Coffee. Base: Oud, Incense.",
        "image_url": None,
        "slug_src": "black-afgano-nasomatto",
    },
    {
        "name_en": "Roses Vanille Mancera",
        "name_ar": "روزيز فانيل مانسيرا للجنسين",
        "brand": "Mancera",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "women",
        "description_ar": "الإفتتاحية: الليمون ونوتات الماء. قلب: الورد والسكر. القاعدة: الفانيليا والمسك الأبيض وخشب الصندل.",
        "description_en": "Top: Lemon, Aquatic Notes. Heart: Rose, Sugar. Base: Vanilla, White Musk, Sandalwood.",
        "image_url": None,
        "slug_src": "roses-vanille-mancera",
    },
    {
        "name_en": "Wild Colt Assaf 100ml",
        "name_ar": "وايلد كولت أساف 100 مل للجنسين",
        "brand": "Assaf",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "unisex",
        "collection": "women",
        "description_ar": "الإفتتاحية: الزعفران والجريب فروت والنعناع والفلفل الوردي والبرغموت. قلب: الجلود والباتشولي ونجيل الهند.",
        "description_en": "Top: Saffron, Grapefruit, Mint, Pink Pepper, Bergamot. Heart: Leather, Patchouli, Vetiver.",
        "image_url": None,
        "slug_src": "wild-colt-assaf-100ml",
    },
    {
        "name_en": "SENSE BY LAVERNE",
        "name_ar": "سنس من لافيرن للنساء",
        "brand": "LAVERNE",
        "price": "1600.00",
        "discount_price": "1125.00",
        "gender": "women",
        "collection": "women",
        "description_ar": "الإفتتاحية: توت العليق والخوخ والفلفل الوردي. قلب: الورد الدمشقي والياسمين والسوسن. القاعدة: حبوب التونكا.",
        "description_en": "Top: Raspberry, Peach, Pink Pepper. Heart: Damascus Rose, Jasmine, Iris. Base: Tonka Bean.",
        "image_url": None,
        "slug_src": "sense-by-laverne",
    },
    # ── Deals & Bundles ───────────────────────────────────────────
    {
        "name_en": "Sauvage + Khamrah Bundle",
        "name_ar": "باندل سوفاج + خمرة",
        "brand": "Flowry",
        "price": "1898.00",
        "discount_price": "1698.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Velvet Fire — ثنائية فاخرة تجمع بين الجرأة والدفء. سوفاج من Dior بعطر أروماتك منعش + خمرة شرقي غني.",
        "description_en": "Velvet Fire — a luxurious duo combining boldness and warmth. Sauvage by Dior with its fresh aromatic scent + the rich oriental Khamrah.",
        "image_url": None,
        "slug_src": "sauvage-khamrah-bundle",
    },
    {
        "name_en": "Ramadan Set For Him",
        "name_ar": "طقم رمضان للرجال",
        "brand": "Flowry",
        "price": "3000.00",
        "discount_price": "1999.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "ثلاث شخصيات عطرية تناسب كل لحظة في رمضان؛ من اللقاءات العائلية إلى سهرات التراويح.",
        "description_en": "Three fragrance personalities for every Ramadan moment — family gatherings to evening prayers.",
        "image_url": None,
        "slug_src": "ramadan-set-for-him",
    },
    {
        "name_en": "Premium Set For Him",
        "name_ar": "الطقم المميز للرجال",
        "brand": "Flowry",
        "price": "3000.00",
        "discount_price": "2499.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "ثلاثة عطور استثنائية تجمع بين الفخامة الفرنسية والقوة الشرقية… هيبة وحضور لا يُنسى.",
        "description_en": "Three exceptional fragrances combining French luxury and oriental power — an unforgettable presence.",
        "image_url": None,
        "slug_src": "premium-set-for-him",
    },
    {
        "name_en": "Sauvage + Khamrah + Bleu de Chanel",
        "name_ar": "سوفاج + خمرة + بلو دو شانيل",
        "brand": "Flowry",
        "price": "2797.00",
        "discount_price": "2297.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Day & Depth — 3 عطور مختلفة تكملك في كل حالة.",
        "description_en": "Day & Depth — 3 different fragrances that complete you in every occasion.",
        "image_url": None,
        "slug_src": "sauvage-khamrah-bleu-de-chanel",
    },
    {
        "name_en": "Sauvage + Bleu de Chanel + Aventus Creed",
        "name_ar": "سوفاج + بلو دو شانيل + أفنتوس كريد",
        "brand": "Flowry",
        "price": "2797.00",
        "discount_price": "2297.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Power Tier — 3 عطور رجالي فخمة، ريحتهم واضحة وجذابة.",
        "description_en": "Power Tier — 3 luxury men's fragrances with a clear, attractive presence.",
        "image_url": None,
        "slug_src": "sauvage-bleu-de-chanel-aventus-creed",
    },
    {
        "name_en": "Sauvage + Bleu de Chanel",
        "name_ar": "سوفاج + بلو دو شانيل",
        "brand": "Flowry",
        "price": "1898.00",
        "discount_price": "1698.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Midnight Blue — ثنائية رجالية فاخرة تجمع بين الانتعاش والفخامة.",
        "description_en": "Midnight Blue — a luxurious men's duo combining freshness and elegance.",
        "image_url": None,
        "slug_src": "sauvage-bleu-de-chanel",
    },
    {
        "name_en": "Bleu de Chanel + Aventus Creed",
        "name_ar": "بلو دو شانيل + أفنتوس كريد",
        "brand": "Flowry",
        "price": "1798.00",
        "discount_price": "1598.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "ثنائية رجالية فاخرة تجمع بين الانتعاش والجرأة.",
        "description_en": "A luxurious men's duo combining freshness and boldness.",
        "image_url": None,
        "slug_src": "bleu-de-chanel-aventus-creed",
    },
    {
        "name_en": "Vanilla Sex + Sauvage Bundle",
        "name_ar": "فانيلا سكس + سوفاج",
        "brand": "Flowry",
        "price": "1898.00",
        "discount_price": "1698.00",
        "gender": "unisex",
        "collection": "deals",
        "description_ar": "Dark Vanilla — باندل دافي وراقي يجمع بين النعومة والحدة.",
        "description_en": "Dark Vanilla — a warm and refined bundle combining softness and edge.",
        "image_url": None,
        "slug_src": "vanilla-sex-sauvage-bundle",
    },
    {
        "name_en": "Libre YSL + Coco Mademoiselle",
        "name_ar": "ليبر إيف سان لوران + كوكو مادموازيل",
        "brand": "Flowry",
        "price": "1798.00",
        "discount_price": "1598.00",
        "gender": "women",
        "collection": "deals",
        "description_ar": "Femme Deux — باندل أنوثي جريء بريحتين يعكسان شخصية قوية وذوق راقي.",
        "description_en": "Femme Deux — a bold feminine bundle with two scents reflecting a strong personality and refined taste.",
        "image_url": None,
        "slug_src": "libre-ysl-coco-mademoiselle",
    },
    {
        "name_en": "Sauvage + Khamrah + Wild Colt",
        "name_ar": "سوفاج + خمرة + وايلد كولت",
        "brand": "Flowry",
        "price": "2797.00",
        "discount_price": "2297.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Heavy Blend — 3 عطور بطابع شرقي فخم، ريحتهم ثابتة وتشد من أول لحظة.",
        "description_en": "Heavy Blend — 3 fragrances with a luxurious oriental character, long-lasting and captivating from the first moment.",
        "image_url": None,
        "slug_src": "sauvage-khamrah-wild-colt",
    },
    {
        "name_en": "Wild Colt + Khamrah Bundle",
        "name_ar": "وايلد كولت + خمرة",
        "brand": "Flowry",
        "price": "1798.00",
        "discount_price": "1598.00",
        "gender": "men",
        "collection": "deals",
        "description_ar": "Oud Storm — مزيج شرقي يجمع بين الغموض والقوة.",
        "description_en": "Oud Storm — an oriental blend combining mystery and power.",
        "image_url": None,
        "slug_src": "wild-colt-khamrah-bundle",
    },
]


# ══════════════════════════════════════════════════════════════════
# CATEGORIES & BRANDS SETUP
# ══════════════════════════════════════════════════════════════════

CATEGORIES_SETUP = [
    {"name_ar": "للرجال",   "name_en": "For Men",    "slug": "for-men"},
    {"name_ar": "للنساء",   "name_en": "For Women",  "slug": "for-women"},
    {"name_ar": "للجنسين",  "name_en": "Unisex",     "slug": "unisex"},
    {"name_ar": "عروض",     "name_en": "Deals",      "slug": "deals"},
]

GENDER_TO_CATEGORY = {
    "men":    "for-men",
    "women":  "for-women",
    "unisex": "unisex",
}

ALL_BRANDS = sorted(set(p["brand"] for p in PRODUCTS_DATA))


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def download_image(url: str, filename: str) -> ContentFile | None:
    """Download image from URL and return ContentFile."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://flowry.store/",
        }
        resp = requests.get(url, headers=headers, timeout=20)
        if resp.status_code == 200:
            return ContentFile(resp.content, name=filename)
    except Exception as e:
        pass
    return None


def get_image_extension(url: str) -> str:
    path = urlparse(url).path
    ext  = os.path.splitext(path)[-1].lower()
    return ext if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif") else ".jpg"


# ══════════════════════════════════════════════════════════════════
# MANAGEMENT COMMAND
# ══════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = "استيراد منتجات flowry.store إلى قاعدة البيانات"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-images",
            action="store_true",
            help="تخطي تحميل الصور (أسرع)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="حذف كل المنتجات الموجودة قبل الاستيراد",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n🌸 Flowry Product Importer\n"))

        # ── 0. Clear if requested ─────────────────────────────────
        if options["clear"]:
            count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"  🗑  Cleared {count} existing products"))

        # ── 1. Create / get Categories ────────────────────────────
        self.stdout.write("  📂 Creating categories...")
        categories = {}
        for cat_data in CATEGORIES_SETUP:
            cat, created = Category.objects.get_or_create(
                slug=cat_data["slug"],
                defaults={
                    "name_ar": cat_data["name_ar"],
                    "name_en": cat_data["name_en"],
                    "is_active": True,
                },
            )
            categories[cat_data["slug"]] = cat
            status = "✅ Created" if created else "⏭  Exists"
            self.stdout.write(f"    {status}: {cat.name_ar}")

        # Deals category
        deals_cat, _ = Category.objects.get_or_create(
            slug="deals",
            defaults={"name_ar": "عروض وباندلات", "name_en": "Deals & Bundles", "is_active": True},
        )
        categories["deals"] = deals_cat

        # ── 2. Create / get Brands ────────────────────────────────
        self.stdout.write("\n  🏷  Creating brands...")
        brands = {}
        for brand_name in ALL_BRANDS:
            brand, created = Brand.objects.get_or_create(
                slug=slugify(brand_name),
                defaults={"name": brand_name, "is_active": True},
            )
            brands[brand_name] = brand
            if created:
                self.stdout.write(f"    ✅ Created brand: {brand_name}")

        # ── 3. Import Products ────────────────────────────────────
        self.stdout.write(f"\n  📦 Importing {len(PRODUCTS_DATA)} products...\n")

        created_count = 0
        skipped_count = 0
        image_count   = 0

        for data in PRODUCTS_DATA:
            # Determine category
            if data["collection"] == "deals":
                cat = categories["deals"]
            else:
                cat_slug = GENDER_TO_CATEGORY.get(data["gender"], "unisex")
                cat = categories[cat_slug]

            brand = brands.get(data["brand"])

            # Build unique slug
            base_slug = slugify(data["name_en"]) or slugify(data["name_ar"])
            slug      = f"{base_slug}-{uuid.uuid4().hex[:6]}"

            # Check if already exists by name_en
            if Product.objects.filter(name_en=data["name_en"]).exists():
                self.stdout.write(f"    ⏭  Skip (exists): {data['name_en']}")
                skipped_count += 1
                continue

            # ── Download thumbnail ────────────────────────────────
            thumbnail_file = None
            if not options["no_images"] and data.get("image_url"):
                ext  = get_image_extension(data["image_url"])
                fname = f"{base_slug}{ext}"
                self.stdout.write(f"    ⬇  Downloading image for: {data['name_en'][:40]}...")
                thumbnail_file = download_image(data["image_url"], fname)
                if thumbnail_file:
                    image_count += 1
                    self.stdout.write(f"       ✅ Image downloaded")
                else:
                    self.stdout.write(self.style.WARNING(f"       ⚠️  Image download failed"))

            # ── Create product ────────────────────────────────────
            product = Product(
                name_ar        = data["name_ar"],
                name_en        = data["name_en"],
                slug           = slug,
                description_ar = data.get("description_ar", ""),
                description_en = data.get("description_en", ""),
                price          = data["price"],
                discount_price = data.get("discount_price"),
                stock          = 10,  # افتراضي — عدّله لاحقاً
                category       = cat,
                brand          = brand,
                is_active      = True,
                is_featured    = data["collection"] == "best-seller",
            )

            if thumbnail_file:
                product.thumbnail.save(thumbnail_file.name, thumbnail_file, save=False)
            else:
                # نحتاج thumbnail — لو مفيش صورة سيفشل الحفظ
                # هنحط placeholder بسيط
                placeholder_url = "https://placehold.co/600x600/1a1a2e/gold?text=Flowry"
                ph = download_image(placeholder_url, f"{base_slug}_ph.png")
                if ph:
                    product.thumbnail.save(ph.name, ph, save=False)

            try:
                product.save()
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"    ✅ Created: {data['name_en'][:50]}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"    ❌ Failed: {data['name_en'][:40]} — {e}")
                )

        # ── 4. Summary ────────────────────────────────────────────
        self.stdout.write("\n" + "═" * 50)
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Done!\n"
            f"   Created : {created_count} products\n"
            f"   Skipped : {skipped_count} (already exist)\n"
            f"   Images  : {image_count} downloaded\n"
        ))
