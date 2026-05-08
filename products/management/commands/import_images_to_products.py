import os, json
from django.core.management.base import BaseCommand
from django.core.files import File
from products.models import Product

SLUG_TO_NAME = {
    "tobacco-collection-by-ibraq": "Tobacco Collection by IBRAQ",
    "sense-collection-by-laverne": "Sense Collection by LAVERNE",
    "megamare-by-orto-parisi-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Megamare by Orto Parisi",
    "ani-by-nishane-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Ani by Nishane",
    "arrogate-pink-by-assaf-%D9%84%D9%84%D9%86%D8%B3%D8%A7%D8%A1": "Arrogate Pink by Assaf",
    "marijuana-by-byredo": "Marijuana by Byredo",
    "black-saffron-by-byredo-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Black Saffron by Byredo",
    "marassi-vibes-collection": "Marassi Vibes Collection",
    "god-of-fire-by-stephane-humbert-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "God of Fire by Stephane Humbert Lucas",
    "musamam-black-intense-by-lattafa-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Musamam Black Intense by Lattafa",
    "hersh-lahab-by-alezz-oud-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Hersh Lahab by Alezz Oud",
    "the-most-wanted-by-azzaro-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84": "The Most Wanted by Azzaro",
    "37528": "Layton Parfums de Marly",
    "valentino-uomo-born-in-roma-intense-valentino-llrjl": "Valentino Uomo Born In Roma Intense",
    "emporio-armani-stronger-with-you-intensely-giorgio-armani-llrjl": "Emporio Armani Stronger With You Intensely",
    "khamrah-lattafa-perfumes-sealed-master-box-lljnsyn": "Khamrah Lattafa Perfumes Sealed Master Box",
    "sauvage-dior-sealed-master-box-llrjl": "Sauvage Dior Sealed Master Box",
    "khamrah-qahwa-lattafa-perfumes-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Khamrah Qahwa Lattafa Perfumes",
    "dior-homme-parfum-dior-llrjl": "Dior Homme Parfum",
    "tobacco-oud-tom-ford-lljnsyn": "Tobacco Oud Tom Ford",
    "imperial-by-gissah-lljnsn": "Imperial by Gissah 100ml",
    "vanilla-sex-tom-ford-lljnsyn": "Vanilla Sex Tom Ford",
    "wild-colt-assaf-200-ml-master-box-%D9%84%D9%84%D8%AC%D9%86%D8%B3%D9%8A%D9%86": "Wild Colt Assaf 200ml Master Box",
    "born-in-roma-the-gold-uomo-valentino-%D9%84%D9%84%D8%B1%D8%AC%D8%A7%D9%84": "Born in Roma The Gold Uomo Valentino",
    "8193": "Khamrah Lattafa Perfumes",
    "sauvage-dior-llrjl": "Sauvage Dior",
    "aventus-creed-llrjl": "Creed Aventus 100ml",
    "dior-homme-intense-llrjl": "Dior Homme Intense",
    "black-afgano-nasomatto-lljnsyn": "Black Afgano Nasomatto",
    "roses-vanille-mancera-lljnsyn": "Roses Vanille Mancera",
    "wild-colt-assaf-lljnsyn": "Wild Colt Assaf 100ml",
    "sense-by-laverne-llns": "SENSE BY LAVERNE",
    "sauvag-khamrah": "Sauvage + Khamrah Bundle",
    "ramadan-set-for-him-1": "Ramadan Set For Him",
    "premium-set-for-him": "Premium Set For Him",
    "sauvage-khamrah-wild-colt-1": "Sauvage + Khamrah + Bleu de Chanel",
    "sauvag-bleu-de-chanel-aventus-creed": "Sauvage + Bleu de Chanel + Aventus Creed",
    "sauvage-bleu-de-chanel": "Sauvage + Bleu de Chanel",
    "bleu-de-chanel-aventus-creed": "Bleu de Chanel + Aventus Creed",
    "vanilla-sex-sauvage": "Vanilla Sex + Sauvage Bundle",
    "libre-yves-saint-laurent-coco-mademoiselle": "Libre YSL + Coco Mademoiselle",
    "sauvage-khamrah-wild-colt": "Sauvage + Khamrah + Wild Colt",
    "wild-cat-khamrah": "Wild Colt + Khamrah Bundle",
}

class Command(BaseCommand):
    help = "ربط الصور المحلية بالمنتجات"

    def add_arguments(self, parser):
        parser.add_argument("--images-dir", default="flowry_images")
        parser.add_argument("--overwrite", action="store_true")

    def handle(self, *args, **options):
        images_dir = options["images_dir"]
        overwrite  = options["overwrite"]
        mapping_file = os.path.join(images_dir, "slug_to_image.json")

        self.stdout.write("\n🖼  Image Importer\n")

        if not os.path.isdir(images_dir):
            self.stdout.write(self.style.ERROR(f"❌ مجلد مش موجود: {images_dir}"))
            return

        with open(mapping_file, encoding="utf-8") as f:
            mapping = json.load(f)

        self.stdout.write(f"  📄 Mapping loaded: {len(mapping)} entries\n")
        updated = skipped = failed = 0

        for slug, info in mapping.items():
            if not info:
                failed += 1
                continue

            # استخرج اسم الملف سواء كان dict أو string
            if isinstance(info, dict):
                filename     = info.get("file", "")
                product_name = info.get("product_name") or SLUG_TO_NAME.get(slug)
            else:
                filename     = info
                product_name = SLUG_TO_NAME.get(slug)

            if not filename or not product_name:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Skip slug: {slug[:50]}"))
                failed += 1
                continue

            try:
                product = Product.objects.get(name_en=product_name)
            except Product.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Not found: {product_name}"))
                failed += 1
                continue

            if product.thumbnail and not overwrite:
                self.stdout.write(f"  ⏭  Skip: {product_name[:45]}")
                skipped += 1
                continue

            img_path = os.path.join(images_dir, filename)
            if not os.path.exists(img_path):
                self.stdout.write(self.style.ERROR(f"  ❌ File missing: {filename}"))
                failed += 1
                continue

            try:
                with open(img_path, "rb") as f:
                    product.thumbnail.save(filename, File(f), save=True)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {product_name[:50]}"))
                updated += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ {product_name[:40]}: {e}"))
                failed += 1

        self.stdout.write(f"\n✅ Updated:{updated} | Skipped:{skipped} | Failed:{failed}\n")
        if skipped:
            self.stdout.write("💡 لاستبدال الصور الموجودة: --overwrite\n")
