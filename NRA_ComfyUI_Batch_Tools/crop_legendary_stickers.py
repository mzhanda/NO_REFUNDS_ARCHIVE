"""
Auto-crop legendary_accent sticker assets (PROP_* only) to their non-transparent bounding boxes.
Saves cropped versions to assets/legendary_accent_cropped/.
Overlay assets (OVERLAY_*) are skipped as they are full-canvas effects.
"""
import os
import json
from PIL import Image

SRC_DIR = "assets/legendary_accent"
DST_DIR = "assets/legendary_accent_cropped"
os.makedirs(DST_DIR, exist_ok=True)

crop_info = {}
files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.png')])

for f in files:
    # Only crop sticker assets (prop_*), skip overlay assets
    if not f.startswith("prop_"):
        print(f"  SKIP {f}: not a sticker (overlay, keep full canvas)")
        continue

    img = Image.open(os.path.join(SRC_DIR, f))
    if img.mode != 'RGBA':
        img = img.convert('RGBA')

    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        print(f"  SKIP {f}: fully transparent")
        continue

    cropped = img.crop(bbox)
    cropped.save(os.path.join(DST_DIR, f))
    crop_info[f] = {"orig_size": list(img.size), "bbox": list(bbox), "cropped_size": list(cropped.size)}
    print(f"  OK {f}: {img.size} -> {cropped.size} (bbox={bbox})")

# Save crop info
with open("data/legendary_sticker_crop_info.json", "w") as jf:
    json.dump(crop_info, jf, indent=2)

print(f"\nDone! {len(crop_info)} legendary stickers cropped to {DST_DIR}/")
