# products/utils.py

from PIL import Image
import os


def compress_image(image_field, max_width=1200, quality=85):
    """
    تضغط الصورة وتحولها لـ WebP بدون فقدان ملحوظ في الجودة
    """
    img = Image.open(image_field)

    # ── تحويل RGBA أو P لـ RGB عشان WebP ────────────────────────
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # ── تصغير الأبعاد لو أكبر من max_width مع الحفاظ على النسبة ──
    if img.width > max_width:
        ratio      = max_width / img.width
        new_height = int(img.height * ratio)
        img        = img.resize((max_width, new_height), Image.LANCZOS)

    # ── حفظ مكان الصورة الأصلية بامتداد .webp ───────────────────
    old_path    = image_field.path
    webp_path   = os.path.splitext(old_path)[0] + ".webp"

    img.save(webp_path, format="WEBP", quality=quality, optimize=True)

    # ── حذف الصورة الأصلية لو كانت مختلفة عن الـ webp ──────────
    if old_path != webp_path and os.path.exists(old_path):
        os.remove(old_path)

    return os.path.basename(webp_path)