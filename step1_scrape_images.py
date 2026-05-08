"""
الخطوة 1 — شغّله على جهازك Mac
================================
يجيب صور كل المنتجات من flowry.store ويحفظها في مجلد flowry_images/

الاستخدام:
    pip install requests beautifulsoup4
    python step1_scrape_images.py
"""

import os
import re
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

OUTPUT_DIR   = "flowry_images"
MAPPING_FILE = "flowry_images/slug_to_image.json"
BASE_URL     = "https://flowry.store"
DELAY        = 1.5

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ar-EG,ar;q=0.9,en;q=0.8",
    "Referer": "https://flowry.store/",
}

PRODUCT_SLUGS = [
    "tobacco-collection-by-ibraq",
    "sense-collection-by-laverne",
    "megamare-by-orto-parisi-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "ani-by-nishane-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "arrogate-pink-by-assaf-%D9%84%D9%84%D9%86%D8%B3%D8%A7%D8%A1",
    "marijuana-by-byredo",
    "black-saffron-by-byredo-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "marassi-vibes-collection",
    "god-of-fire-by-stephane-humbert-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "musamam-black-intense-by-lattafa-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "hersh-lahab-by-alezz-oud-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "the-most-wanted-by-azzaro-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84",
    "37528",
    "valentino-uomo-born-in-roma-intense-valentino-llrjl",
    "emporio-armani-stronger-with-you-intensely-giorgio-armani-llrjl",
    "khamrah-lattafa-perfumes-sealed-master-box-lljnsyn",
    "sauvage-dior-sealed-master-box-llrjl",
    "khamrah-qahwa-lattafa-perfumes-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "dior-homme-parfum-dior-llrjl",
    "tobacco-oud-tom-ford-lljnsyn",
    "imperial-by-gissah-lljnsn",
    "vanilla-sex-tom-ford-lljnsyn",
    "wild-colt-assaf-200-ml-master-box-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86",
    "born-in-roma-the-gold-uomo-valentino-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84",
    "8193",
    "sauvage-dior-llrjl",
    "aventus-creed-llrjl",
    "dior-homme-intense-llrjl",
    "black-afgano-nasomatto-lljnsyn",
    "roses-vanille-mancera-lljnsyn",
    "wild-colt-assaf-lljnsyn",
    "sense-by-laverne-llns",
    "sauvag-khamrah",
    "ramadan-set-for-him-1",
    "premium-set-for-him",
    "sauvage-khamrah-wild-colt-1",
    "sauvag-bleu-de-chanel-aventus-creed",
    "sauvage-bleu-de-chanel",
    "bleu-de-chanel-aventus-creed",
    "vanilla-sex-sauvage",
    "libre-yves-saint-laurent-coco-mademoiselle",
    "sauvage-khamrah-wild-colt",
    "wild-cat-khamrah",
]

# slug المنتج في Shopify -> اسم المنتج في Django
SLUG_TO_NAME = {
    "tobacco-collection-by-ibraq":                                              "Tobacco Collection by IBRAQ",
    "sense-collection-by-laverne":                                              "Sense Collection by LAVERNE",
    "megamare-by-orto-parisi-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86":     "Megamare by Orto Parisi",
    "ani-by-nishane-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86":              "Ani by Nishane",
    "arrogate-pink-by-assaf-%D9%84%D9%84%D9%86%D8%B3%D8%A7%D8%A1":            "Arrogate Pink by Assaf",
    "marijuana-by-byredo":                                                      "Marijuana by Byredo",
    "black-saffron-by-byredo-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86":    "Black Saffron by Byredo",
    "marassi-vibes-collection":                                                 "Marassi Vibes Collection",
    "god-of-fire-by-stephane-humbert-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "God of Fire by Stephane Humbert Lucas",
    "musamam-black-intense-by-lattafa-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Musamam Black Intense by Lattafa",
    "hersh-lahab-by-alezz-oud-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86":   "Hersh Lahab by Alezz Oud",
    "the-most-wanted-by-azzaro-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84":        "The Most Wanted by Azzaro",
    "37528":                                                                    "Layton Parfums de Marly",
    "valentino-uomo-born-in-roma-intense-valentino-llrjl":                     "Valentino Uomo Born In Roma Intense",
    "emporio-armani-stronger-with-you-intensely-giorgio-armani-llrjl":         "Emporio Armani Stronger With You Intensely",
    "khamrah-lattafa-perfumes-sealed-master-box-lljnsyn":                      "Khamrah Lattafa Perfumes Sealed Master Box",
    "sauvage-dior-sealed-master-box-llrjl":                                    "Sauvage Dior Sealed Master Box",
    "khamrah-qahwa-lattafa-perfumes-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Khamrah Qahwa Lattafa Perfumes",
    "dior-homme-parfum-dior-llrjl":                                            "Dior Homme Parfum",
    "tobacco-oud-tom-ford-lljnsyn":                                            "Tobacco Oud Tom Ford",
    "imperial-by-gissah-lljnsn":                                               "Imperial by Gissah 100ml",
    "vanilla-sex-tom-ford-lljnsyn":                                            "Vanilla Sex Tom Ford",
    "wild-colt-assaf-200-ml-master-box-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Wild Colt Assaf 200ml Master Box",
    "born-in-roma-the-gold-uomo-valentino-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84": "Born in Roma The Gold Uomo Valentino",
    "8193":                                                                     "Khamrah Lattafa Perfumes",
    "sauvage-dior-llrjl":                                                      "Sauvage Dior",
    "aventus-creed-llrjl":                                                     "Creed Aventus 100ml",
    "dior-homme-intense-llrjl":                                                "Dior Homme Intense",
    "black-afgano-nasomatto-lljnsyn":                                          "Black Afgano Nasomatto",
    "roses-vanille-mancera-lljnsyn":                                           "Roses Vanille Mancera",
    "wild-colt-assaf-lljnsyn":                                                 "Wild Colt Assaf 100ml",
    "sense-by-laverne-llns":                                                   "SENSE BY LAVERNE",
    "sauvag-khamrah":                                                          "Sauvage + Khamrah Bundle",
    "ramadan-set-for-him-1":                                                   "Ramadan Set For Him",
    "premium-set-for-him":                                                     "Premium Set For Him",
    "sauvage-khamrah-wild-colt-1":                                             "Sauvage + Khamrah + Bleu de Chanel",
    "sauvag-bleu-de-chanel-aventus-creed":                                     "Sauvage + Bleu de Chanel + Aventus Creed",
    "sauvage-bleu-de-chanel":                                                  "Sauvage + Bleu de Chanel",
    "bleu-de-chanel-aventus-creed":                                            "Bleu de Chanel + Aventus Creed",
    "vanilla-sex-sauvage":                                                     "Vanilla Sex + Sauvage Bundle",
    "libre-yves-saint-laurent-coco-mademoiselle":                              "Libre YSL + Coco Mademoiselle",
    "sauvage-khamrah-wild-colt":                                               "Sauvage + Khamrah + Wild Colt",
    "wild-cat-khamrah":                                                        "Wild Colt + Khamrah Bundle",
}


def fix_url(url):
    """أصلح الـ URLs اللي بتبدأ بـ //"""
    if url and url.startswith("//"):
        return "https:" + url
    return url


def get_best_image(slug, page_html):
    """استخرج أفضل صورة من الصفحة"""
    soup = BeautifulSoup(page_html, "html.parser")
    images = []

    # 1. og:image — الأدق دايماً
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        url = fix_url(og["content"].split("?")[0])
        if "cdn/shop" in url:
            images.append(url)

    # 2. JSON-LD
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, list):
                data = data[0]
            imgs = data.get("image", [])
            if isinstance(imgs, str):
                imgs = [imgs]
            for img in imgs:
                url = fix_url(img.split("?")[0])
                if "cdn/shop" in url:
                    images.append(url)
        except Exception:
            pass

    # 3. Regex على كل الصفحة
    raw_urls = re.findall(r'(?:https?:)?//flowry\.store/cdn/shop/files/[^\s"\'<>?\\]+', page_html)
    for u in raw_urls:
        url = fix_url(u)
        if any(url.lower().endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
            images.append(url)

    if not images:
        return None

    # رجّع الأولى (og:image هي الأدق)
    return images[0]


def download_image(url, save_path):
    r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
    if r.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        return True
    return False


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    mapping = {}  # slug -> {"file": filename, "product_name": name}

    print("🌸 Flowry Image Scraper\n")
    total = len(PRODUCT_SLUGS)

    for i, slug in enumerate(PRODUCT_SLUGS, 1):
        product_name = SLUG_TO_NAME.get(slug, slug)
        print(f"[{i}/{total}] {product_name[:50]}")

        url = f"{BASE_URL}/products/{slug}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                print(f"  ⚠️  HTTP {r.status_code}")
                mapping[slug] = None
                time.sleep(DELAY)
                continue
        except Exception as e:
            print(f"  ❌ Request error: {e}")
            mapping[slug] = None
            time.sleep(DELAY)
            continue

        img_url = get_best_image(slug, r.text)

        if not img_url:
            print(f"  ⚠️  No image found")
            mapping[slug] = None
            time.sleep(DELAY)
            continue

        ext = os.path.splitext(urlparse(img_url).path)[-1].lower() or ".webp"
        clean = re.sub(r"[^\w]", "_", slug)[:60]
        filename = f"{clean}{ext}"
        save_path = os.path.join(OUTPUT_DIR, filename)

        if os.path.exists(save_path):
            print(f"  ⏭  Already exists: {filename}")
            mapping[slug] = {"file": filename, "product_name": product_name}
            time.sleep(0.3)
            continue

        try:
            success = download_image(img_url, save_path)
            if success:
                size_kb = os.path.getsize(save_path) // 1024
                print(f"  ✅ {filename} ({size_kb} KB)")
                mapping[slug] = {"file": filename, "product_name": product_name}
            else:
                print(f"  ❌ Download failed (HTTP error)")
                mapping[slug] = None
        except Exception as e:
            print(f"  ❌ {e}")
            mapping[slug] = None

        time.sleep(DELAY)

    # احفظ الـ mapping
    with open(MAPPING_FILE, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    found = sum(1 for v in mapping.values() if v)
    print(f"\n{'═'*50}")
    print(f"✅ Done! {found}/{total} images downloaded")
    print(f"📄 Mapping: {MAPPING_FILE}")
    print(f"\n➡️  الخطوة الجاية:")
    print(f"   cp import_images_to_products.py products/management/commands/")
    print(f"   cp -r flowry_images/ /Users/ahmev/Code/perfumes/")
    print(f"   python manage.py import_images_to_products")


if __name__ == "__main__":
    main()
