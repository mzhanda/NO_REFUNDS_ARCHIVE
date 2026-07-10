"""
Auto-crop all prop assets to their non-transparent bounding boxes.
Saves cropped versions to assets/props_cropped/.
"""
import os
import json
from PIL import Image

SRC_DIR = "assets/props"
DST_DIR = "assets/props_cropped"
os.makedirs(DST_DIR, exist_ok=True)

crop_info = {}
files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.png')])

for f in files:
    img = Image.open(os.path.join(SRC_DIR, f))
    if img.mode != 'RGBA':
        print(f"  SKIP {f}: not RGBA")
        continue
    
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    if not bbox:
        print(f"  SKIP {f}: fully transparent")
        continue
    
    cropped = img.crop(bbox)
    cropped.save(os.path.join(DST_DIR, f))
    crop_info[f] = {"orig_size": list(img.size), "bbox": list(bbox), "cropped_size": list(cropped.size)}
    print(f"  OK {f}: {img.size} -> {cropped.size} (bbox={bbox})")

# Save crop info for the composer to reference
with open("data/prop_crop_info.json", "w") as jf:
    json.dump(crop_info, jf, indent=2)

print(f"\nDone! {len(crop_info)} props cropped to {DST_DIR}/")
