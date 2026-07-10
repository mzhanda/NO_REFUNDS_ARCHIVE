"""
NO REFUNDS ARCHIVE - Base Template Variant Generator
从 8 张母版 (B0X_VAR_01.png) 生成 61 个变体

变体策略：
- 色温偏移（暖/冷）
- 亮度/对比度微调
- 轻微旋转 + 裁剪
- 色调偏移（模拟不同灯光/纸张老化）
- 轻微缩放 + 平移
- 随机噪点注入
"""
import os
import random
import math
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

random.seed(42)

BASE_DIR = os.path.join(os.path.dirname(__file__), "assets", "base_templates")
OUTPUT_SIZE = (1254, 1254)

# 各类型的变体数量（包含 VAR_01 母版本身）
VARIANT_COUNTS = {
    "B01": 8,
    "B02": 12,
    "B03": 8,
    "B04": 8,
    "B05": 6,
    "B06": 10,
    "B07": 5,
    "B08": 4,
}


def apply_color_temperature(img, kelvin_shift):
    """Shift color temperature. Positive = warmer, negative = cooler."""
    r, g, b = img.split()
    if kelvin_shift > 0:
        # Warmer: boost red, reduce blue
        r = r.point(lambda x: min(255, int(x * (1 + kelvin_shift * 0.02))))
        b = b.point(lambda x: max(0, int(x * (1 - kelvin_shift * 0.015))))
    else:
        # Cooler: boost blue, reduce red
        b = b.point(lambda x: min(255, int(x * (1 - kelvin_shift * 0.02))))
        r = r.point(lambda x: max(0, int(x * (1 + kelvin_shift * 0.015))))
    return Image.merge("RGB", (r, g, b))


def apply_tint(img, color, strength):
    """Apply a subtle color tint."""
    tint_layer = Image.new("RGB", img.size, color)
    return Image.blend(img, tint_layer, strength)


def apply_vignette(img, strength):
    """Apply subtle vignette darkening."""
    w, h = img.size
    cx, cy = w / 2, h / 2
    max_dist = math.sqrt(cx**2 + cy**2)
    result = img.copy()
    pixels = result.load()
    orig = img.load()
    for y in range(h):
        for x in range(w):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2) / max_dist
            factor = 1 - (dist ** 2) * strength * 0.35
            factor = max(0.4, factor)
            r = int(orig[x, y][0] * factor)
            g = int(orig[x, y][1] * factor)
            b = int(orig[x, y][2] * factor)
            pixels[x, y] = (r, g, b)
    return result


def generate_variants():
    """Main: generate all base template variants."""
    total_generated = 0

    for base_type in sorted(VARIANT_COUNTS.keys()):
        count = VARIANT_COUNTS[base_type]
        src_path = os.path.join(BASE_DIR, f"{base_type}_VAR_01.png")

        if not os.path.exists(src_path):
            print(f"  ✗ Source not found: {src_path}")
            continue

        src_img = Image.open(src_path).convert("RGB")
        print(f"\n{base_type}: generating {count} variants (including VAR_01)")

        # VAR_01 is the original, keep it as-is
        # We already have VAR_01, so generate VAR_02 through VAR_XX
        for var_idx in range(2, count + 1):
            var_id = f"{base_type}_VAR_{var_idx:02d}"
            img = src_img.copy()

            # Apply a unique combination of transforms per variant
            seed = hash(var_id) % 10000
            random.seed(seed)

            # 1. Brightness shift (-12% to +8%)
            brightness = 1.0 + random.uniform(-0.12, 0.08)
            img = ImageEnhance.Brightness(img).enhance(brightness)

            # 2. Contrast shift (-8% to +10%)
            contrast = 1.0 + random.uniform(-0.08, 0.10)
            img = ImageEnhance.Contrast(img).enhance(contrast)

            # 3. Color temperature shift
            kelvin = random.choice([-30, -20, -10, 0, 10, 20, 30, 40])
            if kelvin != 0:
                img = apply_color_temperature(img, kelvin)

            # 4. Subtle tint (warm yellow or cool blue, very subtle)
            if random.random() < 0.5:
                tint_color = random.choice([
                    (255, 248, 220),  # warm cream
                    (240, 245, 255),  # cool blue-white
                    (255, 245, 235),  # aged paper
                    (245, 240, 250),  # slight purple
                ])
                tint_strength = random.uniform(0.02, 0.08)
                img = apply_tint(img, tint_color, tint_strength)

            # 5. Slight rotation + crop (except for B05/B07 which are already narrow)
            if base_type not in ("B05", "B07") and random.random() < 0.7:
                angle = random.uniform(-2.5, 2.5)
                img = img.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=(0, 0, 0))
                # Center crop back to original size
                w, h = img.size
                left = (w - OUTPUT_SIZE[0]) // 2
                top = (h - OUTPUT_SIZE[1]) // 2
                img = img.crop((max(0, left), max(0, top),
                                min(w, left + OUTPUT_SIZE[0]),
                                min(h, top + OUTPUT_SIZE[1])))
                if img.size != OUTPUT_SIZE:
                    img = img.resize(OUTPUT_SIZE, Image.LANCZOS)

            # 6. Subtle zoom/scale shift
            if random.random() < 0.5:
                zoom = random.uniform(0.97, 1.03)
                new_size = (int(OUTPUT_SIZE[0] * zoom), int(OUTPUT_SIZE[1] * zoom))
                img = img.resize(new_size, Image.LANCZOS)
                # Center crop
                left = (new_size[0] - OUTPUT_SIZE[0]) // 2
                top = (new_size[1] - OUTPUT_SIZE[1]) // 2
                img = img.crop((max(0, left), max(0, top),
                                min(new_size[0], left + OUTPUT_SIZE[0]),
                                min(new_size[1], top + OUTPUT_SIZE[1])))
                if img.size != OUTPUT_SIZE:
                    img = img.resize(OUTPUT_SIZE, Image.LANCZOS)

            # 7. Subtle vignette
            if random.random() < 0.6:
                vignette_strength = random.uniform(0.1, 0.45)
                img = apply_vignette(img, vignette_strength)

            # 8. Saturation adjustment
            saturation = random.uniform(0.85, 1.15)
            img = ImageEnhance.Color(img).enhance(saturation)

            # 9. Very subtle blur (simulate different focus/scan quality)
            if random.random() < 0.3:
                blur_radius = random.uniform(0.3, 1.0)
                img = img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

            # 10. Sharpness variation
            sharpness = random.uniform(0.9, 1.15)
            img = ImageEnhance.Sharpness(img).enhance(sharpness)

            # Save
            out_path = os.path.join(BASE_DIR, f"{var_id}.png")
            img.save(out_path, "PNG")
            total_generated += 1
            print(f"  ✓ {var_id}.png")

    print(f"\n{'='*50}")
    print(f"  Total new variants generated: {total_generated}")
    print(f"  Output: {BASE_DIR}")
    print(f"{'='*50}")


if __name__ == "__main__":
    generate_variants()
