#!/usr/bin/env python3
"""
generate_trait_assets.py
NO REFUNDS ARCHIVE - Trait Asset Generator v3.0

Generates all trait PNG assets for the NFT collection.
All outputs are 1024x1024 RGBA PNGs with transparent backgrounds.

Categories:
  - stamps: Red/colored ink stamp effects (circle/rect/ellipse/hexagon)
  - handwritten: Handwritten-style text notes (bold stroke, no shadow)
  - props: Small object silhouettes (incl. legendary props)
  - damage: Paper damage textures
  - overlays: Full-screen filter effects (incl. legendary overlays)
  - material_pattern: Material texture / pattern layers
  - legendary_accent: Legendary rarity accent features
"""

import os
import sys
import io
import random
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
CANVAS = 1024

random.seed(42)

# ── Font helpers ──
def get_font_paths():
    candidates = []
    if sys.platform == "win32":
        candidates = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            "C:/Windows/Fonts/consola.ttf",
            "C:/Windows/Fonts/times.ttf",
            "C:/Windows/Fonts/impact.ttf",
            "C:/Windows/Fonts/cour.ttf",
            "C:/Windows/Fonts/comic.ttf",
        ]
    return [p for p in candidates if os.path.exists(p)]


def get_font(size=48):
    fonts = get_font_paths()
    if fonts:
        return ImageFont.truetype(fonts[0], size)
    return ImageFont.load_default()


def get_bold_font(size=48):
    if sys.platform == "win32":
        bold_paths = [
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/calibrib.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/impact.ttf",
        ]
        for p in bold_paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return get_font(size)


def get_handwritten_font(size=48):
    """Get a handwriting-style font for notes."""
    if sys.platform == "win32":
        hw_paths = [
            "C:/Windows/Fonts/Inkfree.ttf",
            "C:/Windows/Fonts/SCRIPTBL.TTF",
            "C:/Windows/Fonts/MISTRAL.TTF",
            "C:/Windows/Fonts/VIVALDII.TTF",
            "C:/Windows/Fonts/FRSCRIPT.TTF",
            "C:/Windows/Fonts/LHANDW.TTF",
            "C:/Windows/Fonts/BRUSHSCI.TTF",
            "C:/Windows/Fonts/comic.ttf",
            "C:/Windows/Fonts/comicbd.ttf",
            "C:/Windows/Fonts/Gabriola.ttf",
        ]
        for p in hw_paths:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    return get_font(size)


# ══════════════════════════════════════════════════════════════
# STAMP GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_stamp(text, filename, color=(200, 30, 30, 200), style="circle"):
    """Generate a vintage stamp effect. Supports circle, rect, ellipse, hexagon."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = CANVAS // 2, CANVAS // 2
    stamp_size = random.randint(60, 110)

    angle = random.uniform(-18, 18)
    stamp_layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    stamp_draw = ImageDraw.Draw(stamp_layer)

    r, g, b, a = color
    outline_color = (r, g, b, min(255, a + 10))
    faded_ink = (r, g, b, max(30, a - 60))

    def split_text(words, max_w, font):
        parts = words.split()
        if len(parts) <= 1 or stamp_draw.textbbox((0, 0), words, font=font)[2] <= max_w:
            return words, None
        best_i = 1
        best_diff = float('inf')
        for i in range(1, len(parts)):
            line1 = " ".join(parts[:i])
            line2 = " ".join(parts[i:])
            w1 = stamp_draw.textbbox((0, 0), line1, font=font)[2]
            w2 = stamp_draw.textbbox((0, 0), line2, font=font)[2]
            diff = abs(w1 - w2)
            if diff < best_diff:
                best_diff = diff
                best_i = i
        return " ".join(parts[:best_i]), " ".join(parts[best_i:])

    def draw_hexagon(draw_obj, cx, cy, size, outline, width):
        pts = []
        for i in range(6):
            angle_rad = math.radians(60 * i - 30)
            px = cx + size * math.cos(angle_rad)
            py = cy + size * math.sin(angle_rad)
            pts.append((px, py))
        draw_obj.polygon(pts, outline=outline, width=width)

    words = text.replace("STAMP_", "").replace("_", " ").upper()

    if style == "circle":
        stamp_draw.ellipse(
            [cx - stamp_size, cy - stamp_size, cx + stamp_size, cy + stamp_size],
            outline=outline_color, width=random.randint(2, 4)
        )
        inner = stamp_size - random.randint(14, 22)
        stamp_draw.ellipse(
            [cx - inner, cy - inner, cx + inner, cy + inner],
            outline=outline_color, width=random.randint(1, 3)
        )
        font_size = max(18, min(42, int(stamp_size * 0.24)))
        font = get_bold_font(font_size)
        max_text_w = inner * 1.5
        line1, line2 = split_text(words, max_text_w, font)
        if line2:
            b1 = stamp_draw.textbbox((0, 0), line1, font=font)
            b2 = stamp_draw.textbbox((0, 0), line2, font=font)
            stamp_draw.text((cx - (b1[2] - b1[0]) // 2, cy - font_size - 4), line1, fill=outline_color, font=font)
            stamp_draw.text((cx - (b2[2] - b2[0]) // 2, cy + 4), line2, fill=outline_color, font=font)
        else:
            bbox = stamp_draw.textbbox((0, 0), line1, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            stamp_draw.text((cx - tw // 2, cy - th // 2), line1, fill=outline_color, font=font)

    elif style == "hexagon":
        draw_hexagon(stamp_draw, cx, cy, stamp_size, outline_color, random.randint(2, 4))
        inner_size = stamp_size - random.randint(14, 22)
        draw_hexagon(stamp_draw, cx, cy, inner_size, outline_color, random.randint(1, 3))
        font_size = max(18, min(42, int(stamp_size * 0.22)))
        font = get_bold_font(font_size)
        max_text_w = inner_size * 1.3
        line1, line2 = split_text(words, max_text_w, font)
        if line2:
            b1 = stamp_draw.textbbox((0, 0), line1, font=font)
            b2 = stamp_draw.textbbox((0, 0), line2, font=font)
            stamp_draw.text((cx - (b1[2] - b1[0]) // 2, cy - font_size - 4), line1, fill=outline_color, font=font)
            stamp_draw.text((cx - (b2[2] - b2[0]) // 2, cy + 4), line2, fill=outline_color, font=font)
        else:
            bbox = stamp_draw.textbbox((0, 0), line1, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            stamp_draw.text((cx - tw // 2, cy - th // 2), line1, fill=outline_color, font=font)

    elif style == "ellipse":
        is_horizontal = random.choice([True, False])
        if is_horizontal:
            ew = int(stamp_size * 1.3)
            eh = int(stamp_size * 0.75)
        else:
            ew = int(stamp_size * 0.75)
            eh = int(stamp_size * 1.3)
        stamp_draw.ellipse(
            [cx - ew, cy - eh, cx + ew, cy + eh],
            outline=outline_color, width=random.randint(2, 4)
        )
        inner_ew = ew - random.randint(14, 22)
        inner_eh = eh - random.randint(14, 22)
        stamp_draw.ellipse(
            [cx - inner_ew, cy - inner_eh, cx + inner_ew, cy + inner_eh],
            outline=outline_color, width=random.randint(1, 3)
        )
        font_size = max(18, min(38, int(min(ew, eh) * 0.26)))
        font = get_bold_font(font_size)
        max_text_w = min(inner_ew, inner_eh) * 1.5
        line1, line2 = split_text(words, max_text_w, font)
        if line2:
            b1 = stamp_draw.textbbox((0, 0), line1, font=font)
            b2 = stamp_draw.textbbox((0, 0), line2, font=font)
            stamp_draw.text((cx - (b1[2] - b1[0]) // 2, cy - font_size - 4), line1, fill=outline_color, font=font)
            stamp_draw.text((cx - (b2[2] - b2[0]) // 2, cy + 4), line2, fill=outline_color, font=font)
        else:
            bbox = stamp_draw.textbbox((0, 0), line1, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            stamp_draw.text((cx - tw // 2, cy - th // 2), line1, fill=outline_color, font=font)

    else:
        # Rectangle stamp
        w = int(stamp_size * 1.3)
        h = int(stamp_size * 0.75)
        stamp_draw.rectangle(
            [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
            outline=outline_color, width=random.randint(2, 3)
        )
        font_size = max(18, min(38, int(stamp_size * 0.22)))
        font = get_bold_font(font_size)
        max_text_w = w * 0.8
        line1, line2 = split_text(words, max_text_w, font)
        if line2:
            b1 = stamp_draw.textbbox((0, 0), line1, font=font)
            b2 = stamp_draw.textbbox((0, 0), line2, font=font)
            stamp_draw.text((cx - (b1[2] - b1[0]) // 2, cy - font_size // 2 - 2), line1, fill=outline_color, font=font)
            stamp_draw.text((cx - (b2[2] - b2[0]) // 2, cy + font_size // 2 + 2), line2, fill=outline_color, font=font)
        else:
            bbox = stamp_draw.textbbox((0, 0), line1, font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            stamp_draw.text((cx - tw // 2, cy - th // 2), line1, fill=outline_color, font=font)

    # Apply rotation
    stamp_layer = stamp_layer.rotate(angle, expand=False, resample=Image.BICUBIC, center=(cx, cy))
    img = Image.alpha_composite(img, stamp_layer)

    # Rubber-stamp aging: ink bleeding simulation
    pixels = img.load()
    for _ in range(random.randint(400, 900)):
        x = random.randint(max(0, cx - stamp_size - 10), min(CANVAS - 1, cx + stamp_size + 10))
        y = random.randint(max(0, cy - stamp_size - 10), min(CANVAS - 1, cy + stamp_size + 10))
        px = pixels[x, y]
        if px[3] > 30:
            if random.random() < 0.15:
                pixels[x, y] = (px[0], px[1], px[2], 0)
            else:
                noise = random.randint(-35, 15)
                pixels[x, y] = (
                    max(0, min(255, px[0] + noise)),
                    max(0, min(255, px[1] + noise)),
                    max(0, min(255, px[2] + noise)),
                    max(0, min(255, px[3] + noise - random.randint(0, 25))),
                )

    # Slight blur for ink bleed
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    # Faint ink splatter
    for _ in range(random.randint(3, 8)):
        rad = random.randint(2, 5)
        ox = cx + random.randint(-stamp_size - 15, stamp_size + 15)
        oy = cy + random.randint(-stamp_size - 15, stamp_size + 15)
        draw.ellipse([ox - rad, oy - rad, ox + rad, oy + rad], fill=faded_ink)

    path = os.path.join(ASSETS_DIR, "stamps", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ stamp: {filename}")


# ══════════════════════════════════════════════════════════════
# HANDWRITTEN NOTE GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_handwritten(text_id, filename, placement="random"):
    """Generate a handwritten-style note — pure ink text, no stroke, no shadow."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    text = text_id.replace("NOTE_", "").replace("_", " ")

    # Warmer, slightly faded ink palette — like real pen on old paper
    ink_palettes = [
        ((160, 170, 195), (160, 210)),    # faded blue ballpoint
        ((185, 165, 45),  (160, 210)),    # aged gold
        ((55,  155, 185), (160, 210)),    # faded cyan
        ((175, 70,  130), (160, 210)),    # muted pink
        ((90,  175, 60),  (160, 210)),    # faded green
        ((185, 120, 35),  (160, 210)),    # warm orange-brown
        ((140, 130, 190), (150, 200)),    # soft lavender
        ((70,  140, 185), (160, 210)),    # faded blue
    ]
    base_rgb, alpha_range = random.choice(ink_palettes)
    r = max(0, min(255, base_rgb[0] + random.randint(-12, 12)))
    g = max(0, min(255, base_rgb[1] + random.randint(-12, 12)))
    b = max(0, min(255, base_rgb[2] + random.randint(-12, 12)))
    a = random.randint(alpha_range[0], alpha_range[1])
    ink_color = (r, g, b, a)

    font_size = random.randint(42, 68)
    font = get_handwritten_font(font_size)

    margin = 80
    max_w = CANVAS - 2 * margin

    draw = ImageDraw.Draw(img)

    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_w and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test
    if current_line:
        lines.append(current_line)

    line_height = font_size + random.randint(6, 16)
    total_h = len(lines) * line_height

    line_widths = [draw.textbbox((0, 0), ln, font=font)[2] for ln in lines]
    actual_max_w = max(line_widths) if line_widths else max_w

    if placement == "top_left":
        x0, y0 = margin, margin + random.randint(0, 60)
    elif placement == "top_right":
        x0, y0 = CANVAS - margin - actual_max_w, margin + random.randint(0, 60)
    elif placement == "bottom_left":
        x0, y0 = margin, CANVAS - margin - total_h - random.randint(0, 60)
    elif placement == "bottom_right":
        x0, y0 = CANVAS - margin - actual_max_w, CANVAS - margin - total_h - random.randint(0, 60)
    elif placement == "center":
        x0, y0 = margin, (CANVAS - total_h) // 2
    else:
        x0 = margin + random.randint(0, max(0, CANVAS - margin - actual_max_w))
        y0 = margin + random.randint(0, max(0, CANVAS - margin - total_h))

    # Draw pure ink text — character-level jitter, no stroke, no shadow
    for i, line in enumerate(lines):
        lx = x0
        ly = y0 + i * line_height
        for ch in line:
            bbox = draw.textbbox((0, 0), ch, font=font)
            cw = bbox[2] - bbox[0]
            jx = lx + random.randint(-2, 2)
            jy = ly + random.randint(-3, 3)
            # Pure fill, no stroke_width / stroke_fill
            draw.text((jx, jy), ch, fill=ink_color, font=font)
            lx += cw + random.randint(-1, 2)

    angle = random.uniform(-5, 5)
    img = img.rotate(angle, expand=False, resample=Image.BICUBIC, center=(CANVAS // 2, CANVAS // 2))

    path = os.path.join(ASSETS_DIR, "handwritten", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ handwritten: {filename}")


# ══════════════════════════════════════════════════════════════
# PROP GENERATOR — Retro Everyday Items (Bold & Recognizable)
# Every single prop ID maps to a specific, clearly-drawn object.
# No fallback "sticky note" catch-all — everything is a real item.
# ══════════════════════════════════════════════════════════════

# ── Aged / tarnished vintage color constants (muted, oxidized, realistic) ──
# All colors are deliberately desaturated and darkened for a "found object" look
CLR_GOLD = (155, 120, 55, 180)        # tarnished brass, not bright gold
CLR_GOLD_DARK = (110, 80, 30, 180)    # dark oxidized brass
CLR_SILVER = (130, 130, 135, 170)     # dull silver
CLR_BRASS = (125, 100, 55, 180)       # aged brass
CLR_BRONZE = (115, 85, 50, 170)       # dark bronze
CLR_COPPER = (135, 80, 50, 170)       # oxidized copper
CLR_IRON = (75, 70, 65, 170)          # dark iron
CLR_STEEL = (105, 110, 115, 170)      # dull steel
CLR_PAPER_AGED = (215, 200, 165, 160) # aged paper
CLR_PAPER_DARK = (175, 160, 125, 160) # darker aged paper
CLR_INK_BROWN = (65, 50, 30, 150)     # faded brown ink
CLR_INK_BLUE = (45, 50, 100, 140)     # faded blue ink
CLR_WOOD = (110, 80, 45, 170)         # aged wood
CLR_WOOD_DARK = (80, 50, 25, 170)     # dark aged wood
CLR_LEATHER = (95, 65, 35, 170)       # worn leather
CLR_RED_ACCENT = (130, 35, 25, 160)   # faded red
CLR_GREEN_ACCENT = (60, 105, 55, 150) # faded green
CLR_RUST = (120, 70, 35, 170)         # rust color
CLR_OXIDIZED_COPPER = (100, 125, 115, 150)  # green copper patina


def _draw_prop_key(draw, cx, cy, s):
    """Vintage ornate key — large and unmistakable."""
    r = s // 3
    # Bow (ornate head ring)
    draw.ellipse([cx - s // 2 - r, cy - r, cx - s // 2 + r, cy + r],
                 outline=CLR_BRASS, width=4)
    draw.ellipse([cx - s // 2 - r + 5, cy - r + 5, cx - s // 2 + r - 5, cy + r - 5],
                 outline=CLR_GOLD, width=2)
    # Bow inner cutout
    draw.ellipse([cx - s // 2 - r // 2, cy - r // 2, cx - s // 2 + r // 2, cy + r // 2],
                 fill=(0, 0, 0, 0), outline=CLR_BRASS, width=1)
    # Shaft
    draw.rectangle([cx - s // 2, cy - 4, cx + s // 2, cy + 4], fill=CLR_BRASS)
    draw.rectangle([cx - s // 2, cy - 2, cx + s // 2, cy + 2], fill=CLR_GOLD)
    # Teeth
    tooth_w = s // 6
    for tx in [cx + s // 5, cx + s // 5 + tooth_w * 2]:
        draw.rectangle([tx, cy + 4, tx + tooth_w, cy + 14], fill=CLR_BRASS)
        draw.rectangle([tx + 1, cy + 4, tx + tooth_w - 1, cy + 10], fill=CLR_GOLD)


def _draw_prop_coin(draw, cx, cy, s):
    """Vintage coin — bold circle with inner ring and center dot."""
    r = s // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=3)
    draw.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                 outline=CLR_GOLD_DARK, width=2)
    # Center emblem
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=CLR_GOLD_DARK)


def _draw_prop_ticket(draw, cx, cy, w, h):
    """Vintage ticket stub — perforation line is key."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                           radius=4, fill=CLR_PAPER_AGED, outline=CLR_PAPER_DARK, width=2)
    # Bold perforation line
    perf_x = cx - w // 2 + w // 3
    draw.line([(perf_x, cy - h // 2 + 2), (perf_x, cy + h // 2 - 2)],
              fill=CLR_PAPER_DARK, width=1)
    for py in range(cy - h // 2 + 3, cy + h // 2 - 2, 6):
        draw.ellipse([perf_x - 3, py - 3, perf_x + 3, py + 3], fill=CLR_PAPER_DARK)
    # Stub number area
    draw.rectangle([cx - w // 2 + 4, cy - h // 2 + 4, perf_x - 4, cy + h // 2 - 4],
                   outline=CLR_PAPER_DARK, width=1)


def _draw_prop_matchbook(draw, cx, cy, s):
    """Vintage matchbook — distinctive flap + striker strip + match heads."""
    w, h = s, s * 3 // 4
    # Body
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                           radius=3, fill=(200, 170, 120, 240), outline=CLR_WOOD_DARK, width=2)
    # Striker strip (dark rough area at bottom)
    draw.rectangle([cx - w // 2 + 4, cy + h // 2 - 14, cx + w // 2 - 4, cy + h // 2 - 2],
                   fill=(50, 45, 40, 220))
    # Match sticks with red heads
    for i in range(5):
        mx = cx - w // 3 + i * w // 6
        # Stick
        draw.rectangle([mx - 2, cy - h // 2 + 4, mx + 2, cy + h // 2 - 18],
                       fill=(220, 210, 180, 200))
        # Head
        draw.ellipse([mx - 4, cy - h // 2 + 2, mx + 4, cy - h // 2 + 12],
                     fill=CLR_RED_ACCENT)


def _draw_prop_bottle(draw, cx, cy, s):
    """Vintage small bottle — clear silhouette with cap and label."""
    bw, bh = s // 2, s
    # Body
    draw.rounded_rectangle([cx - bw // 2, cy - bh // 4, cx + bw // 2, cy + bh // 2],
                           radius=6, fill=(140, 160, 130, 140), outline=(100, 120, 90, 200), width=3)
    # Neck
    draw.rectangle([cx - bw // 4, cy - bh // 2, cx + bw // 4, cy - bh // 4],
                   fill=(140, 160, 130, 140), outline=(100, 120, 90, 200), width=2)
    # Cap
    draw.rectangle([cx - bw // 4 - 3, cy - bh // 2 - 8, cx + bw // 4 + 3, cy - bh // 2 + 2],
                   fill=CLR_COPPER)
    # Label
    draw.rectangle([cx - bw // 3, cy - 6, cx + bw // 3, cy + bh // 6],
                   fill=(245, 235, 210, 200), outline=CLR_PAPER_DARK, width=1)


def _draw_prop_pen(draw, cx, cy, s):
    """Vintage fountain pen — distinctive clip and nib."""
    pw, ph = s // 5, s
    # Barrel
    draw.rounded_rectangle([cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2],
                           radius=3, fill=(50, 45, 40, 240))
    # Gold band
    draw.rectangle([cx - pw // 2 - 1, cy - ph // 6, cx + pw // 2 + 1, cy - ph // 6 + 6],
                   fill=CLR_GOLD)
    # Clip
    draw.rectangle([cx + pw // 2, cy - ph // 3, cx + pw // 2 + 6, cy + ph // 5],
                   fill=CLR_GOLD)
    draw.ellipse([cx + pw // 2 + 4, cy - ph // 3 - 2, cx + pw // 2 + 8, cy - ph // 3 + 4],
                 fill=CLR_GOLD)
    # Nib
    draw.polygon([(cx - pw // 2, cy + ph // 2), (cx + pw // 2, cy + ph // 2),
                  (cx, cy + ph // 2 + 12)], fill=CLR_GOLD)


def _draw_prop_glasses(draw, cx, cy, s):
    """Vintage glasses — two bold circles + bridge + arms."""
    r = s // 4
    bridge = s // 6
    # Lenses (bold outline)
    draw.ellipse([cx - bridge - r, cy - r, cx - bridge + r, cy + r],
                 outline=(60, 50, 35, 220), width=4)
    draw.ellipse([cx + bridge - r, cy - r, cx + bridge + r, cy + r],
                 outline=(60, 50, 35, 220), width=4)
    # Bridge
    draw.arc([cx - bridge, cy - r // 2, cx + bridge, cy + r // 2], 180, 360,
             fill=(60, 50, 35, 200), width=3)
    # Temple arms
    draw.line([(cx - bridge - r, cy), (cx - bridge - r - s // 2, cy)],
              fill=(60, 50, 35, 200), width=3)
    draw.line([(cx + bridge + r, cy), (cx + bridge + r + s // 2, cy)],
              fill=(60, 50, 35, 200), width=3)


def _draw_prop_watch(draw, cx, cy, s):
    """Vintage pocket watch — bold circle with hands and crown."""
    r = s // 2
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=4)
    draw.ellipse([cx - r + 8, cy - r + 8, cx + r - 8, cy + r - 8],
                 fill=(245, 240, 225, 200), outline=CLR_GOLD_DARK, width=1)
    # Hour markers
    for i in range(12):
        a = math.radians(30 * i - 90)
        mx = cx + int((r - 16) * math.cos(a))
        my = cy + int((r - 16) * math.sin(a))
        draw.ellipse([mx - 2, my - 2, mx + 2, my + 2], fill=CLR_GOLD_DARK)
    # Hands
    draw.line([(cx, cy), (cx, cy - r + 20)], fill=(40, 35, 30, 230), width=3)
    draw.line([(cx, cy), (cx + r - 24, cy)], fill=(40, 35, 30, 210), width=2)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=CLR_GOLD_DARK)
    # Crown
    draw.ellipse([cx - 5, cy - r - 6, cx + 5, cy - r + 2], fill=CLR_GOLD)


def _draw_prop_cigarette(draw, cx, cy, s):
    """Vintage cigarette — white body, cork filter, ash, smoke."""
    cw, ch = s // 4, s
    # White body
    draw.rounded_rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2],
                           radius=2, fill=(245, 240, 230, 240), outline=(200, 195, 185, 150), width=1)
    # Cork filter
    draw.rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy - ch // 4],
                   fill=(210, 185, 140, 220))
    # Filter dots
    for fx in [cx - cw // 4, cx + cw // 4]:
        draw.ellipse([fx - 1, cy - ch // 2 + 4, fx + 1, cy - ch // 2 + 6],
                     fill=(180, 150, 100, 180))
    # Burning tip
    draw.ellipse([cx - 2, cy + ch // 2 - 4, cx + 2, cy + ch // 2 + 2],
                 fill=(200, 120, 50, 180))
    # Smoke wisps (more visible)
    for i in range(4):
        sx = cx + random.randint(-6, 6)
        sy = cy + ch // 2 + 12 + i * 10
        draw.arc([sx - 8, sy - 6, sx + 8, sy + 6], 0, 180,
                 fill=(170, 165, 155, 60), width=2)


def _draw_prop_ring(draw, cx, cy, s):
    """Vintage ring with gemstone."""
    r = s // 3
    # Band
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CLR_GOLD, width=4)
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=CLR_GOLD_DARK, width=1)
    # Setting / prongs
    gem_s = r // 2
    draw.rectangle([cx - gem_s - 2, cy - gem_s - r + 2, cx + gem_s + 2, cy - gem_s - r + 8],
                   fill=CLR_GOLD)
    # Gem
    draw.ellipse([cx - gem_s, cy - gem_s * 2 - r + 2, cx + gem_s, cy - r + 2],
                 fill=(180, 40, 40, 240))
    draw.ellipse([cx - gem_s // 2, cy - gem_s - r, cx + gem_s // 3, cy - gem_s - r + gem_s],
                 fill=(255, 255, 255, 70))


def _draw_prop_button(draw, cx, cy, s):
    """Vintage 4-hole button."""
    r = s // 3
    # Outer rim
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(150, 120, 80, 240), outline=(100, 75, 40, 220), width=3)
    # Inner rim
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=(170, 140, 100, 160), width=1)
    # 4 holes
    for dx, dy in [(-5, -5), (5, -5), (-5, 5), (5, 5)]:
        draw.ellipse([cx + dx - 3, cy + dy - 3, cx + dx + 3, cy + dy + 3],
                     fill=(40, 30, 20, 220))
    # Thread through holes
    draw.line([(-5, -5), (5, 5)], fill=(200, 190, 170, 120))
    draw.line([(5, -5), (-5, 5)], fill=(200, 190, 170, 120))


def _draw_prop_postage_stamp(draw, cx, cy, s):
    """Vintage postage stamp with perforated edges."""
    w, h = s, s * 3 // 4
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=(225, 200, 150, 240), outline=(170, 140, 90, 200), width=2)
    # Inner border
    draw.rectangle([cx - w // 2 + 6, cy - h // 2 + 6, cx + w // 2 - 6, cy + h // 2 - 6],
                   outline=(170, 140, 90, 140), width=1)
    # Perforations around edges
    for side_pts, side_dir in [
        ([(cx - w // 2 + i * 10, cy - h // 2) for i in range(w // 10 + 1)], True),
        ([(cx - w // 2 + i * 10, cy + h // 2) for i in range(w // 10 + 1)], True),
        ([(cx - w // 2, cy - h // 2 + i * 10) for i in range(h // 10 + 1)], False),
        ([(cx + w // 2, cy - h // 2 + i * 10) for i in range(h // 10 + 1)], False),
    ]:
        for px, py in side_pts:
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(0, 0, 0, 0))
    # Center image hint (silhouette)
    draw.ellipse([cx - w // 6, cy - h // 6, cx + w // 6, cy + h // 6],
                 outline=CLR_INK_BROWN, width=2)


def _draw_prop_comb(draw, cx, cy, s):
    """Vintage comb — spine + many teeth."""
    cw, ch = s // 2, s
    # Spine
    draw.rounded_rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy - ch // 2 + 10],
                           radius=4, fill=CLR_WOOD)
    # Teeth
    for tx in range(cx - cw // 2 + 3, cx + cw // 2 - 2, 5):
        draw.rectangle([tx, cy - ch // 2 + 10, tx + 2, cy + ch // 2],
                       fill=CLR_WOOD)


def _draw_prop_scissors(draw, cx, cy, s):
    """Vintage scissors — two blades + two handle loops."""
    blade_l = s
    # Left blade
    draw.line([(cx, cy - blade_l // 2), (cx, cy + blade_l // 2)],
              fill=CLR_IRON, width=4)
    # Right blade
    draw.line([(cx + 14, cy - blade_l // 2), (cx + 14, cy + blade_l // 2)],
              fill=CLR_IRON, width=4)
    # Handles
    for hy in [cy - blade_l // 2 - 10, cy + blade_l // 2 + 10]:
        draw.ellipse([cx - 8, hy - 12, cx + 8, hy + 12],
                     outline=CLR_BRASS, width=3)
        draw.ellipse([cx + 6, hy - 12, cx + 22, hy + 12],
                     outline=CLR_BRASS, width=3)
    # Pivot screw
    draw.ellipse([cx + 5, cy - 4, cx + 9, cy + 4], fill=CLR_STEEL)


def _draw_prop_razor(draw, cx, cy, s):
    """Vintage safety razor — T-shape silhouette."""
    rw, rh = s // 2, s
    # Handle
    draw.rounded_rectangle([cx - 4, cy - rh // 3, cx + 4, cy + rh // 2],
                           radius=3, fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Knurling on handle
    for ky in range(cy - rh // 6, cy + rh // 4, 6):
        draw.line([(cx - 3, ky), (cx + 3, ky)], fill=CLR_IRON, width=1)
    # Head (T-top)
    draw.rounded_rectangle([cx - rw // 2, cy - rh // 3 - 10, cx + rw // 2, cy - rh // 3 + 10],
                           radius=4, fill=(190, 185, 175, 240), outline=CLR_STEEL, width=2)


def _draw_prop_lighter(draw, cx, cy, s):
    """Vintage lighter — rectangular body + flint wheel + flame."""
    lw, lh = s // 3, s
    # Body
    draw.rounded_rectangle([cx - lw // 2, cy - lh // 2, cx + lw // 2, cy + lh // 2],
                           radius=3, fill=CLR_BRASS, outline=CLR_GOLD_DARK, width=2)
    # Vertical lines (engraving)
    for lx in [cx - lw // 4, cx + lw // 4]:
        draw.line([(lx, cy - lh // 3), (lx, cy + lh // 3)], fill=CLR_GOLD_DARK, width=1)
    # Flint wheel
    draw.ellipse([cx - lw // 3, cy - lh // 2 - 6, cx + lw // 3, cy - lh // 2 + 6],
                 fill=CLR_IRON)
    # Flame
    flame_pts = [
        (cx, cy - lh // 2 - 16),
        (cx - 5, cy - lh // 2 + 2),
        (cx + 5, cy - lh // 2 + 2),
    ]
    draw.polygon(flame_pts, fill=(255, 170, 30, 140))
    # Inner flame
    draw.polygon([
        (cx, cy - lh // 2 - 10),
        (cx - 3, cy - lh // 2),
        (cx + 3, cy - lh // 2),
    ], fill=(255, 230, 100, 120))


def _draw_prop_medal(draw, cx, cy, s):
    """Vintage medal with ribbon and star."""
    r = s // 3
    # Ribbon
    draw.polygon([(cx - 10, cy - s // 2), (cx + 10, cy - s // 2),
                  (cx + 6, cy - r - 4), (cx - 6, cy - r - 4)],
                 fill=(160, 30, 30, 240))
    draw.polygon([(cx - 10, cy - s // 2), (cx, cy - s // 2),
                  (cx, cy - r - 4), (cx - 6, cy - r - 4)],
                 fill=(120, 20, 20, 200))
    # Medal disc
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=3)
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=CLR_GOLD_DARK, width=1)
    # 5-pointed star in center
    star_s = r // 2
    pts = []
    for i in range(10):
        a = math.radians(36 * i - 90)
        r_val = star_s if i % 2 == 0 else star_s // 2
        pts.append((cx + int(r_val * math.cos(a)), cy + int(r_val * math.sin(a))))
    draw.polygon(pts, fill=CLR_GOLD_DARK)


def _draw_prop_envelope(draw, cx, cy, s):
    """Vintage envelope — rectangular with V-flap and stamp."""
    ew, eh = s, s * 2 // 3
    # Body
    draw.rectangle([cx - ew // 2, cy - eh // 2, cx + ew // 2, cy + eh // 2],
                   fill=(245, 235, 210, 230), outline=(190, 170, 140, 180), width=2)
    # Flap (V-shape)
    draw.polygon([(cx - ew // 2, cy - eh // 2), (cx + ew // 2, cy - eh // 2),
                  (cx, cy + eh // 6)],
                 fill=(250, 245, 230, 160), outline=(200, 185, 160, 130), width=1)
    # Postage stamp on corner
    stamp_s = ew // 5
    draw.rectangle([cx + ew // 4, cy - eh // 2 + 3, cx + ew // 2 - 3, cy - eh // 2 + stamp_s + 3],
                   fill=(210, 180, 130, 220), outline=(160, 130, 80, 180), width=1)
    # Address lines
    for i, ly in enumerate([cy + eh // 4, cy + eh // 3]):
        lw = random.randint(ew // 3, ew // 2)
        draw.line([(cx - lw // 2, ly), (cx + lw // 2, ly)],
                  fill=(160, 140, 110, 100), width=1)


def _draw_prop_spoon(draw, cx, cy, s):
    """Vintage spoon — handle + oval bowl."""
    sw, sh = s // 5, s
    # Handle
    draw.rounded_rectangle([cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 3],
                           radius=3, fill=CLR_SILVER, outline=CLR_STEEL, width=1)
    # Bowl
    draw.ellipse([cx - sw, cy + sh // 4, cx + sw, cy + sh // 2 + sh // 4],
                 fill=CLR_SILVER, outline=CLR_STEEL, width=2)
    # Highlight on bowl
    draw.ellipse([cx - sw // 2, cy + sh // 4 + 4, cx + sw // 2, cy + sh // 2 + sh // 4 - 4],
                 fill=(220, 220, 225, 80))


def _draw_prop_stirrer(draw, cx, cy, s):
    """Coffee stirrer — thin flat wooden stick."""
    sw, sh = 6, s
    draw.rounded_rectangle([cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 2],
                           radius=2, fill=CLR_WOOD, outline=CLR_WOOD_DARK, width=1)
    # Grain line
    draw.line([(cx, cy - sh // 2 + 4), (cx, cy + sh // 2 - 4)], fill=CLR_WOOD_DARK, width=1)


def _draw_prop_corkscrew(draw, cx, cy, s):
    """Corkscrew — T-handle + spiral."""
    # Handle
    handle_w = s // 2
    draw.rounded_rectangle([cx - handle_w // 2, cy - s // 2 - 12, cx + handle_w // 2, cy - s // 2 + 4],
                           radius=4, fill=CLR_WOOD)
    # Spiral
    for i in range(8):
        sy = cy - s // 2 + 4 + i * s // 8
        offset = int(6 * math.sin(i * 1.5))
        draw.line([(cx - offset, sy), (cx + offset, sy + s // 10)],
                  fill=CLR_STEEL, width=2)


def _draw_prop_chain(draw, cx, cy, s):
    """Chain fragment — linked oval rings."""
    num_links = 6
    link_w = s // num_links
    for i in range(num_links):
        lx = cx - s // 2 + i * link_w + link_w // 2
        draw.ellipse([lx - link_w // 3, cy - link_w // 2, lx + link_w // 3, cy + link_w // 2],
                     outline=CLR_STEEL, width=2)
        if i < num_links - 1:
            nx = lx + link_w
            draw.line([(lx + link_w // 3, cy), (nx - link_w // 3, cy)], fill=CLR_STEEL, width=2)


def _draw_prop_straw(draw, cx, cy, s):
    """Plastic drinking straw with red stripe."""
    sw, sh = 5, s
    draw.rectangle([cx - sw // 2, cy - sh // 2, cx + sw // 2, cy + sh // 2],
                   fill=(240, 240, 235, 220), outline=(200, 200, 195, 140), width=1)
    for sy in range(cy - sh // 2, cy + sh // 2, 14):
        draw.line([(cx - sw // 2, sy), (cx + sw // 2, sy)],
                  fill=(220, 70, 60, 200), width=3)
    # Bend at top
    bend_y = cy - sh // 2 + sh // 5
    draw.line([(cx, bend_y), (cx + sh // 6, bend_y - sh // 6)],
              fill=(240, 240, 235, 180), width=5)


def _draw_prop_sugar_packet(draw, cx, cy, s):
    """Sugar/condiment packet — small rectangle with fold."""
    pw, ph = s // 2, s // 3
    draw.rectangle([cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2],
                   fill=(245, 240, 225, 240), outline=(190, 175, 150, 180), width=1)
    # Fold line at top
    draw.line([(cx - pw // 2, cy - ph // 2 + 8), (cx + pw // 2, cy - ph // 2 + 8)],
              fill=(200, 190, 170, 120), width=1)
    # Tear notch
    draw.polygon([(cx + pw // 2 - 4, cy - ph // 2), (cx + pw // 2, cy - ph // 2),
                  (cx + pw // 2, cy - ph // 2 + 6)], fill=(0, 0, 0, 0))


def _draw_prop_candy_wrapper(draw, cx, cy, s):
    """Candy wrapper — twisted ends."""
    cw, ch = s // 2, s // 3
    # Body
    draw.rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2],
                   fill=(220, 90, 60, 240), outline=(170, 60, 30, 200), width=2)
    # Twisted ends
    for ex in [cx - cw // 2, cx + cw // 2]:
        for i in range(3):
            ey = cy + (i - 1) * ch // 3
            draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=(200, 80, 50, 200))


def _draw_prop_bottle_cap(draw, cx, cy, s):
    """Bottle cap — circle with crimped edge."""
    r = s // 3
    # Crimped edge (scalloped circle)
    n_crimps = 16
    pts = []
    for i in range(n_crimps):
        a = math.radians(360 * i / n_crimps - 90)
        r_val = r + (3 if i % 2 == 0 else -1)
        pts.append((cx + int(r_val * math.cos(a)), cy + int(r_val * math.sin(a))))
    draw.polygon(pts, fill=CLR_COPPER, outline=CLR_BRONZE, width=1)
    # Inner circle
    draw.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
                 fill=(200, 130, 80, 200), outline=CLR_BRONZE, width=1)
    # Star logo
    star_s = r // 3
    for i in range(5):
        a = math.radians(72 * i - 90)
        sx = cx + int(star_s * math.cos(a))
        sy = cy + int(star_s * math.sin(a))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 230, 180, 180))


def _draw_prop_napkin(draw, cx, cy, s):
    """Cloth napkin — soft irregular square with fold lines."""
    ns = s // 2
    # Slightly irregular square
    pts = [
        (cx - ns + random.randint(-5, 5), cy - ns + random.randint(-5, 5)),
        (cx + ns + random.randint(-5, 5), cy - ns + random.randint(-5, 5)),
        (cx + ns + random.randint(-5, 5), cy + ns + random.randint(-5, 5)),
        (cx - ns + random.randint(-5, 5), cy + ns + random.randint(-5, 5)),
    ]
    draw.polygon(pts, fill=(235, 225, 205, 180), outline=(200, 185, 160, 140), width=2)
    # Fold line
    draw.line([(cx, cy - ns + 6), (cx + random.randint(-3, 3), cy + ns - 6)],
              fill=(210, 195, 170, 100), width=1)


def _draw_prop_jewelry_bag(draw, cx, cy, s):
    """Small jewelry bag — pouch shape with drawstring."""
    bw, bh = s // 2, s // 2
    # Bag body (slightly wider at bottom)
    pts = [
        (cx - bw // 2, cy - bh // 2),
        (cx + bw // 2, cy - bh // 2),
        (cx + bw // 2 + 6, cy + bh // 2),
        (cx - bw // 2 - 6, cy + bh // 2),
    ]
    draw.polygon(pts, fill=(160, 130, 90, 220), outline=(120, 90, 55, 200), width=2)
    # Drawstring at top
    draw.line([(cx - bw // 2 - 4, cy - bh // 2), (cx + bw // 2 + 4, cy - bh // 2)],
              fill=CLR_GOLD, width=2)
    # Bow
    draw.ellipse([cx - 6, cy - bh // 2 - 6, cx, cy - bh // 2], fill=CLR_GOLD)
    draw.ellipse([cx, cy - bh // 2 - 6, cx + 6, cy - bh // 2], fill=CLR_GOLD)


def _draw_prop_keychain(draw, cx, cy, s):
    """Keychain ring + fob."""
    r = s // 4
    # Split ring
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CLR_STEEL, width=3)
    # Fob (small tag)
    fw, fh = s // 3, s // 2
    draw.rounded_rectangle([cx + r + 4, cy - fh // 2, cx + r + 4 + fw, cy + fh // 2],
                           radius=3, fill=CLR_LEATHER, outline=(80, 50, 25, 220), width=2)


def _draw_prop_check_slip(draw, cx, cy, w, h):
    """Diner check / receipt slip — paper with tear edge and lines."""
    # Jagged top edge (torn from pad)
    pts_top = []
    for x in range(cx - w // 2, cx + w // 2, 6):
        pts_top.append((x, cy - h // 2 + random.randint(-3, 3)))
    # Draw body
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=CLR_PAPER_AGED, outline=CLR_PAPER_DARK, width=2)
    # Item lines
    for i in range(3):
        ly = cy - h // 4 + i * h // 5
        lw = random.randint(w // 3, w * 3 // 4)
        draw.line([(cx - lw // 2, ly), (cx + lw // 2, ly)],
                  fill=CLR_INK_BLUE, width=1)
    # Total line (bold)
    draw.line([(cx - w // 3, cy + h // 3), (cx + w // 3, cy + h // 3)],
              fill=CLR_INK_BLUE, width=2)
    # Tear edge at top
    for px, py in pts_top:
        pixels = draw._image.load()
        if 0 <= px < CANVAS and 0 <= py < CANVAS:
            pass  # drawn above


def _draw_prop_tag(draw, cx, cy, s, label_text=""):
    """Vintage tag — rectangle with hole + string."""
    tw, th = s // 2, s
    # Tag body
    draw.rounded_rectangle([cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2],
                           radius=4, fill=CLR_PAPER_AGED, outline=CLR_PAPER_DARK, width=2)
    # Hole
    hole_r = tw // 6
    draw.ellipse([cx - hole_r, cy - th // 2 + hole_r + 4,
                  cx + hole_r, cy - th // 2 + hole_r * 3 + 4],
                 fill=(0, 0, 0, 0), outline=CLR_PAPER_DARK, width=2)
    # String through hole
    draw.line([(cx, cy - th // 2 + hole_r + 4), (cx + random.randint(-8, 8), cy - th // 2 - 10)],
              fill=(180, 160, 130, 160), width=1)
    # Lines on tag
    for i in range(3):
        ly = cy - th // 4 + i * th // 6
        lw = tw // 2
        draw.line([(cx - lw // 2, ly), (cx + lw // 2, ly)],
                  fill=CLR_INK_BROWN, width=1)


def _draw_prop_card(draw, cx, cy, w, h):
    """Membership/payphone card — rectangle with stripe and text hints."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                           radius=4, fill=CLR_PAPER_AGED, outline=CLR_PAPER_DARK, width=2)
    # Colored stripe
    stripe_color = random.choice([CLR_RED_ACCENT, CLR_GREEN_ACCENT, CLR_INK_BLUE])
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy - h // 2 + 14],
                   fill=stripe_color)
    # Card number lines
    for i in range(3):
        ly = cy + i * h // 8
        lw = w * 3 // 5
        draw.line([(cx - lw // 2, ly), (cx + lw // 2, ly)],
                  fill=CLR_INK_BROWN, width=1)


def _draw_prop_newspaper_clip(draw, cx, cy, w, h):
    """Newspaper clipping — irregular torn rectangle with text columns."""
    # Irregular edges
    pts = []
    for x in range(cx - w // 2, cx + w // 2, 8):
        pts.append((x, cy - h // 2 + random.randint(-3, 3)))
    for y in range(cy - h // 2, cy + h // 2, 8):
        pts.append((cx + w // 2 + random.randint(-3, 0), y))
    for x in range(cx + w // 2, cx - w // 2, -8):
        pts.append((x, cy + h // 2 + random.randint(-3, 3)))
    for y in range(cy + h // 2, cy - h // 2, -8):
        pts.append((cx - w // 2 + random.randint(0, 3), y))

    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=(240, 235, 220, 230), outline=(180, 170, 150, 160), width=2)
    # Text column hints
    col_w = w // 5
    for col in [-1, 0, 1]:
        col_x = cx + col * col_w * 2
        for i in range(8):
            ly = cy - h // 3 + i * h // 10
            lw = col_w
            draw.line([(col_x - lw // 2, ly), (col_x + lw // 2, ly)],
                      fill=(140, 130, 115, random.randint(30, 70)), width=1)


def _draw_prop_record_sleeve(draw, cx, cy, w, h):
    """Vinyl record sleeve corner — dark square with circular record edge."""
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=(35, 35, 45, 230), outline=(60, 60, 70, 180), width=2)
    # Record peeking out
    r = min(w, h) // 3
    draw.ellipse([cx + w // 4, cy - h // 4, cx + w // 4 + r * 2, cy - h // 4 + r * 2],
                 fill=(15, 15, 20, 200))
    draw.ellipse([cx + w // 4 + 4, cy - h // 4 + 4, cx + w // 4 + r * 2 - 4, cy - h // 4 + r * 2 - 4],
                 outline=(80, 80, 90, 140), width=1)
    # Center label
    draw.ellipse([cx + w // 4 + r // 2, cy - h // 4 + r // 2,
                  cx + w // 4 + r * 3 // 2, cy - h // 4 + r * 3 // 2],
                 fill=(180, 50, 50, 180))


def _draw_prop_vinyl_label(draw, cx, cy, s):
    """Vinyl record center label — circle with text rings."""
    r = s // 3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(200, 60, 40, 240))
    draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                 outline=(240, 200, 180, 140), width=1)
    # Spindle hole
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(0, 0, 0, 0))
    # Text ring
    for i in range(12):
        a = math.radians(30 * i - 90)
        tx = cx + int((r - 12) * math.cos(a))
        ty = cy + int((r - 12) * math.sin(a))
        draw.ellipse([tx - 1, ty - 1, tx + 1, ty + 1], fill=(240, 200, 180, 140))


def _draw_prop_coupon_scratch(draw, cx, cy, w, h):
    """Coupon / scratch-off — rectangle with scratch area."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                           radius=3, fill=(220, 210, 185, 240), outline=(180, 160, 130, 180), width=2)
    # Scratch-off area (silver/gray)
    scratch_w, scratch_h = w // 2, h // 3
    draw.rounded_rectangle([cx - scratch_w // 2, cy - scratch_h // 2,
                            cx + scratch_w // 2, cy + scratch_h // 2],
                           radius=2, fill=(150, 145, 140, 200))
    # Scratch lines
    for _ in range(8):
        sx = cx + random.randint(-scratch_w // 2, scratch_w // 2)
        sy = cy + random.randint(-scratch_h // 2, scratch_h // 2)
        draw.line([(sx - 10, sy - random.randint(1, 3)), (sx + 10, sy + random.randint(1, 3))],
                  fill=(170, 165, 160, 100), width=1)


def _draw_prop_dust_jacket(draw, cx, cy, w, h):
    """Book dust jacket corner — folded paper with spine."""
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=(230, 210, 170, 230), outline=(180, 155, 120, 180), width=2)
    # Spine fold
    spine_x = cx - w // 4
    draw.line([(spine_x, cy - h // 2), (spine_x, cy + h // 2)],
              fill=(200, 175, 140, 120), width=1)
    # Flap fold
    draw.line([(cx - w // 2 + 10, cy - h // 2), (cx - w // 2 + 10, cy + h // 2)],
              fill=(200, 175, 140, 100), width=1)
    # Title lines on spine
    for i in range(2):
        ly = cy - h // 6 + i * h // 6
        draw.line([(spine_x - w // 6, ly), (spine_x + w // 6, ly)],
                  fill=CLR_INK_BROWN, width=1)


def _draw_prop_tracklist(draw, cx, cy, w, h):
    """Tracklist scrap — paper with numbered lines."""
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                   fill=CLR_PAPER_AGED, outline=CLR_PAPER_DARK, width=2)
    for i in range(6):
        ly = cy - h // 3 + i * h // 8
        # Number
        draw.text((cx - w // 3, ly - 8), str(i + 1), fill=CLR_INK_BROWN, font=get_font(12))
        # Line
        lw = w // 2
        draw.line([(cx - w // 4, ly), (cx + w // 4, ly)],
                  fill=(140, 130, 110, random.randint(40, 80)), width=1)


def _draw_prop_price_sticker(draw, cx, cy, s):
    """Price sticker — small circle/oval with bold number."""
    r = s // 3
    draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2],
                 fill=(255, 245, 100, 240), outline=(200, 180, 40, 200), width=2)
    # Price text
    price = random.choice(["$1.99", "$3.50", "$0.99", "$5.00", "$2.49"])
    font = get_bold_font(r // 3)
    bbox = draw.textbbox((0, 0), price, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - r // 3), price, fill=(180, 40, 30, 220), font=font)


def _draw_prop_barcode_sticker(draw, cx, cy, s):
    """Barcode sticker — rectangle with vertical lines."""
    bw, bh = s // 2, s // 3
    draw.rounded_rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                           radius=2, fill=(250, 248, 240, 240), outline=(200, 190, 170, 180), width=1)
    # Barcode lines
    for bx in range(cx - bw // 3, cx + bw // 3, 3):
        if random.random() < 0.6:
            line_h = random.randint(bh // 3, bh * 2 // 3)
            draw.line([(bx, cy - line_h // 2), (bx, cy + line_h // 2)],
                      fill=(30, 30, 30, random.randint(150, 220)), width=random.randint(1, 2))


def _draw_prop_tape_cassette(draw, cx, cy, w, h):
    """Cassette tape / VHS — dark rect with reel circles."""
    draw.rounded_rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
                           radius=5, fill=(35, 35, 45, 240), outline=(60, 60, 70, 200), width=2)
    # Two reels
    for rx in [cx - w // 4, cx + w // 4]:
        rr = w // 6
        draw.ellipse([rx - rr, cy - rr, rx + rr, cy + rr],
                     outline=(180, 175, 165, 160), width=2)
        draw.ellipse([rx - rr // 3, cy - rr // 3, rx + rr // 3, cy + rr // 3],
                     fill=(80, 80, 90, 180))
    # Window at bottom
    draw.rectangle([cx - w // 3, cy + h // 6, cx + w // 3, cy + h // 3],
                   fill=(60, 60, 70, 160))


def _draw_prop_rewind_sticker(draw, cx, cy, s):
    """Be kind rewind sticker — circle with triangle icon."""
    r = s // 3
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(255, 240, 100, 240), outline=(200, 180, 40, 200), width=2)
    # Rewind triangle icon
    tri_s = r // 2
    draw.polygon([
        (cx - tri_s, cy - tri_s),
        (cx + tri_s, cy),
        (cx - tri_s, cy + tri_s),
    ], fill=(180, 40, 30, 220))


# ═══════════════════════════════════════════════════
# NEW PROP DRAWING FUNCTIONS (replacing paper slips)
# ═══════════════════════════════════════════════════

def _draw_prop_padlock(draw, cx, cy, s):
    """Padlock — U-shackle + square body + keyhole."""
    body_w, body_h = s // 2, s // 2
    # Shackle (U-shape)
    arc_r = body_w // 2
    draw.arc([cx - arc_r, cy - body_h // 2 - arc_r, cx + arc_r, cy - body_h // 2 + arc_r],
             0, 180, fill=CLR_STEEL, width=4)
    draw.arc([cx - arc_r, cy - body_h // 2 - arc_r, cx + arc_r, cy - body_h // 2 + arc_r],
             0, 180, fill=CLR_STEEL, width=4)
    draw.line([(cx - arc_r, cy - body_h // 2), (cx - arc_r, cy - body_h // 2 + arc_r)],
              fill=CLR_STEEL, width=4)
    draw.line([(cx + arc_r, cy - body_h // 2), (cx + arc_r, cy - body_h // 2 + arc_r)],
              fill=CLR_STEEL, width=4)
    # Body
    draw.rounded_rectangle([cx - body_w // 2, cy - body_h // 4, cx + body_w // 2, cy + body_h // 2],
                           radius=4, fill=CLR_BRASS, outline=CLR_GOLD_DARK, width=2)
    # Keyhole
    draw.ellipse([cx - 3, cy + 4, cx + 3, cy + 10], fill=(0, 0, 0, 200))
    draw.rectangle([cx - 1, cy + 8, cx + 1, cy + 14], fill=(0, 0, 0, 200))


def _draw_prop_fork(draw, cx, cy, s):
    """Vintage fork — handle + 4 tines."""
    fw, fh = s // 5, s
    # Handle
    draw.rounded_rectangle([cx - fw // 2, cy - fh // 2, cx + fw // 2, cy + fh // 4],
                           radius=3, fill=CLR_SILVER, outline=CLR_STEEL, width=1)
    # Handle decoration
    draw.line([(cx, cy + fh // 8), (cx, cy + fh // 6)], fill=CLR_STEEL, width=1)
    # Tines (4 prongs)
    tine_w = fw // 2
    for tx in [cx - tine_w, cx - tine_w // 2, cx + tine_w // 2, cx + tine_w]:
        draw.rectangle([tx - 1, cy - fh // 2, tx + 1, cy - fh // 4],
                       fill=CLR_SILVER, outline=CLR_STEEL, width=1)


def _draw_prop_bottle_opener(draw, cx, cy, s):
    """Bottle opener — flat metal with rounded end + hole."""
    bw, bh = s // 3, s
    draw.rounded_rectangle([cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2],
                           radius=5, fill=CLR_STEEL, outline=CLR_IRON, width=2)
    # Opening hole at top
    hole_r = bw // 2 - 4
    draw.ellipse([cx - hole_r, cy - bh // 2 + 8, cx + hole_r, cy - bh // 2 + 8 + hole_r * 2],
                 fill=(0, 0, 0, 0), outline=CLR_IRON, width=2)
    # Brand line
    draw.line([(cx - bw // 4, cy), (cx + bw // 4, cy)], fill=CLR_IRON, width=1)


def _draw_prop_fountain_pen(draw, cx, cy, s):
    """Fountain pen — nib, grip, barrel, clip."""
    pw, ph = s // 6, s
    # Barrel
    draw.rounded_rectangle([cx - pw // 2, cy - ph // 4, cx + pw // 2, cy + ph // 3],
                           radius=3, fill=(20, 20, 40, 240), outline=(60, 60, 80, 200), width=1)
    # Grip section
    draw.rounded_rectangle([cx - pw // 2 - 1, cy - ph // 3, cx + pw // 2 + 1, cy - ph // 4],
                           radius=2, fill=CLR_GOLD)
    # Nib
    nib_pts = [(cx, cy - ph // 2), (cx - pw // 2, cy - ph // 3), (cx + pw // 2, cy - ph // 3)]
    draw.polygon(nib_pts, fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=1)
    # Nib slit
    draw.line([(cx, cy - ph // 2 + 4), (cx, cy - ph // 3)], fill=(0, 0, 0, 150), width=1)
    # Clip
    draw.line([(cx + pw // 2, cy - ph // 4), (cx + pw // 2 + pw, cy - ph // 4 + 20)],
              fill=CLR_GOLD, width=2)


def _draw_prop_shot_glass(draw, cx, cy, s):
    """Shot glass — trapezoid with liquid."""
    gw, gh = s // 2, s // 2
    # Glass body (wider at top)
    pts = [
        (cx - gw // 2, cy - gh // 2),
        (cx + gw // 2, cy - gh // 2),
        (cx + gw // 2 - 8, cy + gh // 2),
        (cx - gw // 2 + 8, cy + gh // 2),
    ]
    draw.polygon(pts, fill=(200, 210, 225, 120), outline=(160, 175, 190, 180), width=2)
    # Liquid inside
    liquid_pts = [
        (cx - gw // 2 + 4, cy - gh // 6),
        (cx + gw // 2 - 4, cy - gh // 6),
        (cx + gw // 2 - 8 + 4, cy + gh // 2 - 4),
        (cx - gw // 2 + 8 + 4, cy + gh // 2 - 4),
    ]
    liquid_color = random.choice([
        (180, 120, 40, 200),   # whiskey
        (140, 50, 50, 200),    # red
        (80, 120, 60, 200),    # green
    ])
    draw.polygon(liquid_pts, fill=liquid_color)
    # Rim highlight
    draw.line([(cx - gw // 2, cy - gh // 2), (cx + gw // 2, cy - gh // 2)],
              fill=(230, 235, 245, 140), width=2)


def _draw_prop_whiskey_bottle(draw, cx, cy, s):
    """Mini whiskey bottle — neck + body + label."""
    bw, bh = s // 3, s
    # Body
    draw.rounded_rectangle([cx - bw // 2, cy - bh // 4, cx + bw // 2, cy + bh // 2],
                           radius=4, fill=(60, 40, 20, 220), outline=(35, 20, 10, 200), width=2)
    # Neck
    draw.rectangle([cx - bw // 4, cy - bh // 2, cx + bw // 4, cy - bh // 4],
                   fill=(60, 40, 20, 200), outline=(35, 20, 10, 180), width=2)
    # Cap
    draw.rectangle([cx - bw // 4 - 2, cy - bh // 2 - 6, cx + bw // 4 + 2, cy - bh // 2],
                   fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=1)
    # Label
    draw.rectangle([cx - bw // 3, cy - bh // 8, cx + bw // 3, cy + bh // 6],
                   fill=(240, 225, 190, 220), outline=(170, 150, 120, 180), width=1)
    # Label text line
    draw.line([(cx - bw // 4, cy), (cx + bw // 4, cy)], fill=CLR_INK_BROWN, width=1)


def _draw_prop_magnifying_glass(draw, cx, cy, s):
    """Magnifying glass — circle lens + handle."""
    r = s // 3
    # Lens
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=(200, 220, 240, 80), outline=CLR_GOLD, width=3)
    # Glass highlight
    draw.ellipse([cx - r // 2, cy - r // 2, cx, cy],
                 fill=(255, 255, 255, 60))
    # Handle
    hw, hh = s // 8, s // 2
    angle = random.uniform(-30, 30)
    rad = math.radians(angle)
    hx = cx + int(r * math.cos(rad + math.pi / 3))
    hy = cy + int(r * math.sin(rad + math.pi / 3))
    draw.rounded_rectangle([hx - hw // 2, hy, hx + hw // 2, hy + hh],
                           radius=3, fill=CLR_WOOD)


def _draw_prop_pocket_knife(draw, cx, cy, s):
    """Pocket knife — folded handle + blade edge."""
    kw, kh = s // 2, s // 3
    # Handle
    draw.rounded_rectangle([cx - kw // 2, cy - kh // 2, cx + kw // 2, cy + kh // 2],
                           radius=3, fill=CLR_WOOD, outline=CLR_WOOD_DARK, width=2)
    # Bolster
    draw.rectangle([cx + kw // 2 - 8, cy - kh // 2, cx + kw // 2, cy + kh // 2],
                   fill=CLR_STEEL)
    # Blade peeking out
    blade_pts = [(cx + kw // 2, cy - kh // 3), (cx + kw // 2 + kw // 3, cy - kh // 2),
                 (cx + kw // 2 + kw // 3, cy - kh // 6)]
    draw.polygon(blade_pts, fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Pins
    for px in [cx - kw // 4, cx + kw // 4]:
        draw.ellipse([px - 2, cy - 2, px + 2, cy + 2], fill=CLR_BRASS)


def _draw_prop_compass(draw, cx, cy, s):
    """Pocket compass — circle with N/S/E/W markings."""
    r = s // 3
    # Body
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=CLR_BRASS, outline=CLR_GOLD_DARK, width=3)
    # Inner ring
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=(0, 0, 0, 60), width=1)
    # Face
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
                 fill=(250, 248, 235, 230))
    # Cardinal points
    for angle_deg, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        rad_a = math.radians(angle_deg - 90)
        tx = cx + int((r - 14) * math.cos(rad_a))
        ty = cy + int((r - 14) * math.sin(rad_a))
        font = get_bold_font(10)
        draw.text((tx - 4, ty - 6), label, fill=(180, 30, 30, 200), font=font)
    # Needle
    draw.line([(cx, cy - r + 14), (cx, cy + r - 14)], fill=(180, 30, 30, 200), width=1)
    draw.polygon([(cx, cy - r + 14), (cx - 4, cy - r + 18), (cx + 4, cy - r + 18)],
                 fill=(180, 30, 30, 200))
    # Pivot
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=CLR_GOLD_DARK)


def _draw_prop_dice(draw, cx, cy, s):
    """Vintage dice — cube with dots."""
    d = s // 3
    # Cube face (isometric-ish)
    pts = [
        (cx - d // 2, cy - d // 3),
        (cx + d // 2, cy - d // 3),
        (cx + d // 2 + d // 6, cy),
        (cx + d // 6, cy + d // 2),
        (cx - d // 2 + d // 6, cy + d // 2),
        (cx - d // 2, cy),
    ]
    # Main face
    face_pts = [pts[0], pts[1], pts[5]]
    draw.polygon([pts[0], pts[1], pts[2], pts[3], pts[4], pts[5]],
                 fill=(240, 235, 220, 230), outline=(100, 90, 70, 200), width=2)
    # Dots (random 1-6)
    dot_r = d // 10
    dot_positions = {
        1: [(cx, cy)],
        2: [(cx - d // 4, cy - d // 6), (cx + d // 4, cy + d // 6)],
        3: [(cx - d // 4, cy - d // 6), (cx, cy), (cx + d // 4, cy + d // 6)],
        4: [(cx - d // 4, cy - d // 6), (cx + d // 4, cy - d // 6),
            (cx - d // 4, cy + d // 6), (cx + d // 4, cy + d // 6)],
        5: [(cx - d // 4, cy - d // 6), (cx + d // 4, cy - d // 6),
            (cx, cy), (cx - d // 4, cy + d // 6), (cx + d // 4, cy + d // 6)],
        6: [(cx - d // 4, cy - d // 6), (cx + d // 4, cy - d // 6),
            (cx - d // 4, cy), (cx + d // 4, cy),
            (cx - d // 4, cy + d // 6), (cx + d // 4, cy + d // 6)],
    }
    face_val = random.randint(1, 6)
    for dx, dy in dot_positions[face_val]:
        draw.ellipse([dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r],
                     fill=(30, 30, 30, 220))


def _draw_prop_photograph_corner(draw, cx, cy, s):
    """Vintage photograph — white-bordered photo paper."""
    pw, ph = s // 2, s * 2 // 5
    # White border
    draw.rectangle([cx - pw // 2 - 4, cy - ph // 2 - 4, cx + pw // 2 + 4, cy + ph // 2 + 4],
                   fill=(245, 240, 230, 240))
    # Photo area
    draw.rectangle([cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2],
                   fill=(80, 70, 60, 220), outline=(200, 190, 175, 150), width=1)
    # Faded image hint (a few lighter patches)
    for _ in range(5):
        rx = cx + random.randint(-pw // 3, pw // 3)
        ry = cy + random.randint(-ph // 3, ph // 3)
        rr = random.randint(8, 20)
        draw.ellipse([rx - rr, ry - rr, rx + rr, ry + rr],
                     fill=(140, 130, 115, random.randint(20, 60)))


def _draw_prop_hair_clip(draw, cx, cy, s):
    """Hair clip / barrette — metal clasp shape."""
    cw, ch = s // 2, s // 6
    draw.rounded_rectangle([cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2],
                           radius=3, fill=CLR_SILVER, outline=CLR_STEEL, width=2)
    # Clasp line
    draw.line([(cx - cw // 3, cy - ch // 2), (cx - cw // 3, cy + ch // 2)],
              fill=CLR_STEEL, width=1)
    # Spring dots
    for sx in [cx - cw // 4, cx + cw // 4]:
        draw.ellipse([sx - 2, cy - 2, sx + 2, cy + 2], fill=CLR_IRON)


def _draw_prop_ashtray(draw, cx, cy, s):
    """Ashtray — shallow dish with cigarette rests."""
    r = s // 3
    # Dish
    draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2],
                 fill=(70, 70, 80, 220), outline=(40, 40, 50, 200), width=2)
    # Inner ring
    draw.ellipse([cx - r + 8, cy - r // 2 + 5, cx + r - 8, cy + r // 2 - 5],
                 outline=(50, 50, 60, 120), width=1)
    # Cigarette rests (notches)
    for angle_deg in [0, 90, 180, 270]:
        rad_a = math.radians(angle_deg)
        nx = cx + int(r * math.cos(rad_a))
        ny = cy + int((r // 2) * math.sin(rad_a))
        draw.ellipse([nx - 5, ny - 3, nx + 5, ny + 3],
                     fill=(50, 50, 60, 180))


def _draw_prop_brooch(draw, cx, cy, s):
    """Vintage brooch — decorative pin with gemstones."""
    r = s // 3
    # Base metal disc
    draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                 fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=2)
    # Decorative ring
    draw.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                 outline=CLR_GOLD_DARK, width=1)
    # Center gem
    gem_s = r // 2
    gem_color = random.choice([
        (180, 40, 40, 230),   # ruby
        (40, 100, 180, 230),  # sapphire
        (40, 160, 80, 230),   # emerald
        (180, 60, 180, 230),  # amethyst
    ])
    draw.ellipse([cx - gem_s, cy - gem_s, cx + gem_s, cy + gem_s], fill=gem_color)
    # Gem highlight
    draw.ellipse([cx - gem_s // 3, cy - gem_s // 3, cx + gem_s // 4, cy + gem_s // 4],
                 fill=(255, 255, 255, 80))
    # Small surrounding gems
    for i in range(6):
        a = math.radians(60 * i - 90)
        gx = cx + int((r - 8) * math.cos(a))
        gy = cy + int((r - 8) * math.sin(a))
        draw.ellipse([gx - 3, gy - 3, gx + 3, gy + 3], fill=(255, 255, 255, 150))


def _draw_prop_zippo_lighter(draw, cx, cy, s):
    """Zippo-style lighter — rectangular chrome body + flip lid."""
    lw, lh = s // 4, s * 2 // 3
    # Body
    draw.rounded_rectangle([cx - lw // 2, cy - lh // 4, cx + lw // 2, cy + lh // 2],
                           radius=3, fill=CLR_STEEL, outline=CLR_IRON, width=2)
    # Lid (slightly open)
    lid_h = lh // 4
    draw.rectangle([cx - lw // 2, cy - lh // 4 - lid_h, cx + lw // 2, cy - lh // 4],
                   fill=CLR_STEEL, outline=CLR_IRON, width=2)
    # Hinge line
    draw.line([(cx - lw // 2, cy - lh // 4), (cx + lw // 2, cy - lh // 4)],
              fill=CLR_IRON, width=1)
    # Flint wheel
    draw.ellipse([cx - lw // 5, cy - lh // 4 - 2, cx + lw // 5, cy - lh // 4 + 6],
                 fill=CLR_IRON)
    # Engraving
    draw.line([(cx - lw // 4, cy + lh // 6), (cx + lw // 4, cy + lh // 6)],
              fill=CLR_IRON, width=1)


def _draw_prop_vintage_badge(draw, cx, cy, s):
    """Vintage badge — shield shape with pin back."""
    bw, bh = s // 2, s // 2
    # Shield shape
    pts = [
        (cx - bw // 2, cy - bh // 2),
        (cx + bw // 2, cy - bh // 2),
        (cx + bw // 2, cy - bh // 6),
        (cx, cy + bh // 2),
        (cx - bw // 2, cy - bh // 6),
    ]
    draw.polygon(pts, fill=CLR_GOLD, outline=CLR_GOLD_DARK, width=2)
    # Inner shield
    inner_pts = [
        (cx - bw // 3, cy - bh // 3),
        (cx + bw // 3, cy - bh // 3),
        (cx + bw // 3, cy - bh // 10),
        (cx, cy + bh // 3),
        (cx - bw // 3, cy - bh // 10),
    ]
    draw.polygon(inner_pts, fill=CLR_GOLD_DARK)
    # Star in center
    star_s = bw // 6
    star_pts = []
    for i in range(10):
        a = math.radians(36 * i - 90)
        r_val = star_s if i % 2 == 0 else star_s // 2
        star_pts.append((cx + int(r_val * math.cos(a)), cy + int(r_val * math.sin(a))))
    draw.polygon(star_pts, fill=(255, 240, 200, 200))
    # Pin clasp on back
    draw.line([(cx - bw // 4, cy - bh // 2 - 4), (cx + bw // 4, cy - bh // 2 - 4)],
              fill=CLR_STEEL, width=2)


def _draw_prop_small_bolt(draw, cx, cy, s):
    """Small hex bolt — hexagonal head with threaded shaft."""
    hw = s // 8
    # Threaded shaft
    draw.rectangle([cx - hw // 2, cy, cx + hw // 2, cy + s // 3], fill=CLR_STEEL, outline=CLR_IRON, width=1)
    for i in range(4):
        ly = cy + 4 + i * (s // 16)
        draw.line([(cx - hw // 2 + 1, ly), (cx + hw // 2 - 1, ly)], fill=CLR_IRON, width=1)
    # Hex head
    hex_r = hw + 2
    pts = []
    for i in range(6):
        a = math.radians(60 * i - 90)
        pts.append((cx + int(hex_r * math.cos(a)), cy - 4 + int(hex_r * math.sin(a))))
    draw.polygon(pts, fill=CLR_STEEL, outline=CLR_IRON, width=1)
    draw.ellipse([cx - hw // 2 + 1, cy - 6, cx + hw // 2 - 1, cy - 2], fill=CLR_SILVER)


def _draw_prop_washer(draw, cx, cy, s):
    """Metal washer — two concentric circles."""
    outer = s // 5
    inner = outer // 2
    draw.ellipse([cx - outer, cy - outer, cx + outer, cy + outer],
                 fill=CLR_STEEL, outline=CLR_IRON, width=1)
    draw.ellipse([cx - inner, cy - inner, cx + inner, cy + inner],
                 fill=(0, 0, 0, 0), outline=CLR_SILVER, width=1)
    # Light reflection
    draw.arc([cx - outer + 3, cy - outer + 3, cx + outer - 3, cy + outer - 3],
             0, 90, fill=CLR_SILVER, width=2)


def _draw_prop_screw(draw, cx, cy, s):
    """Flathead screw — long shaft + slotted head."""
    sw = s // 16
    # Shaft
    draw.rectangle([cx - sw, cy - s // 5, cx + sw, cy + s // 3], fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Threads
    for i in range(5):
        ly = cy + 2 + i * (s // 14)
        draw.line([(cx - sw + 1, ly), (cx + sw - 1, ly)], fill=CLR_IRON, width=1)
    # Head
    head_w = sw + 3
    draw.ellipse([cx - head_w, cy - s // 5 - head_w, cx + head_w, cy - s // 5 + head_w],
                 fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Slot
    draw.line([(cx - head_w + 2, cy - s // 5), (cx + head_w - 2, cy - s // 5)], fill=CLR_IRON, width=2)


def _draw_prop_nail(draw, cx, cy, s):
    """Carpenter nail — flat head, tapered shaft, sharp point."""
    nw = s // 20
    # Shaft (tapered)
    shaft_len = s // 2
    pts = [
        (cx - nw, cy - shaft_len // 3),
        (cx + nw, cy - shaft_len // 3),
        (cx + nw // 2, cy + shaft_len // 2),
        (cx - nw // 2, cy + shaft_len // 2),
    ]
    draw.polygon(pts, fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Sharp point
    draw.polygon([
        (cx - nw // 2, cy + shaft_len // 2),
        (cx + nw // 2, cy + shaft_len // 2),
        (cx, cy + shaft_len // 2 + s // 8),
    ], fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Flat head
    draw.ellipse([cx - nw - 2, cy - shaft_len // 3 - nw, cx + nw + 2, cy - shaft_len // 3 + nw],
                 fill=CLR_STEEL, outline=CLR_IRON, width=1)


def _draw_prop_fishing_hook(draw, cx, cy, s):
    """Fishing hook — J-shaped curve with barb."""
    pts = []
    hook_r = s // 5
    # Top loop (eye)
    draw.ellipse([cx - hook_r // 2, cy - s // 3 - hook_r, cx + hook_r // 2, cy - s // 3 + hook_r],
                 outline=CLR_STEEL, width=2)
    # J-curve shaft
    draw.line([(cx, cy - s // 3 + hook_r // 2), (cx, cy + s // 6)], fill=CLR_STEEL, width=2)
    # Bottom curve
    for a in range(0, 200, 5):
        angle = math.radians(a + 180)
        x = cx + int(hook_r * math.cos(angle))
        y = cy + s // 6 + int(hook_r * math.sin(angle))
        pts.append((x, y))
    if len(pts) >= 2:
        for j in range(len(pts) - 1):
            draw.line([pts[j], pts[j + 1]], fill=CLR_STEEL, width=2)
    # Barb
    tip_x = pts[-1][0] if pts else cx + hook_r
    tip_y = pts[-1][1] if pts else cy + s // 6
    draw.line([(tip_x - 3, tip_y - 3), (tip_x, tip_y)], fill=CLR_STEEL, width=2)


def _draw_prop_safety_pin(draw, cx, cy, s):
    """Safety pin — coiled wire with clasp."""
    pw = s // 25
    length = s // 2
    # Main pin body
    draw.line([(cx - length // 2, cy), (cx + length // 2, cy)], fill=CLR_STEEL, width=2)
    # Coil at bottom
    for i in range(3):
        co = 3 + i * 2
        draw.ellipse([cx - length // 2 - co, cy - co, cx - length // 2 + co, cy + co],
                     outline=CLR_STEEL, width=1)
    # Clasp head at top
    draw.arc([cx + length // 2 - 6, cy - 6, cx + length // 2 + 6, cy + 6],
             0, 180, fill=CLR_STEEL, width=2)


def _draw_prop_thimble(draw, cx, cy, s):
    """Sewing thimble — tapered cylinder with dimples."""
    tw = s // 6
    th = s // 3
    # Body (tapered rectangle)
    pts = [
        (cx - tw // 2, cy - th // 3),
        (cx + tw // 2, cy - th // 3),
        (cx + tw // 2 + 3, cy + th // 2),
        (cx - tw // 2 - 3, cy + th // 2),
    ]
    draw.polygon(pts, fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Top dome
    draw.ellipse([cx - tw // 2, cy - th // 3 - tw // 4, cx + tw // 2, cy - th // 3 + tw // 4],
                 fill=CLR_STEEL, outline=CLR_IRON, width=1)
    # Dimples
    for row in range(5):
        ry = cy - th // 4 + row * (th // 8)
        for col in range(3):
            rx = cx - tw // 4 + col * (tw // 4)
            draw.ellipse([rx - 2, ry - 2, rx + 2, ry + 2], fill=CLR_IRON)


def _draw_prop_paperclip(draw, cx, cy, s):
    """Paperclip — classic double-loop wire shape."""
    pw = s // 20
    length = s // 2
    width = s // 6
    # Outer loop
    draw.rounded_rectangle([cx - width, cy - length // 2, cx + width, cy - length // 2 + length // 2],
                           radius=width, outline=CLR_STEEL, width=2)
    # Inner loop
    draw.rounded_rectangle([cx - width // 2, cy - length // 4 + length // 6, cx + width // 2, cy - length // 4 + length // 2],
                           radius=width // 2, outline=CLR_STEEL, width=2)


def _draw_prop_razor_blade(draw, cx, cy, s):
    """Razor blade — trapezoid with slot."""
    bw = s // 6
    bh = s // 4
    # Blade body (trapezoid)
    pts = [
        (cx - bw, cy - bh),
        (cx + bw, cy - bh),
        (cx + bw // 2, cy + bh),
        (cx - bw // 2, cy + bh),
    ]
    draw.polygon(pts, fill=CLR_SILVER, outline=CLR_IRON, width=1)
    # Center slot
    slot_w = bw // 3
    slot_h = bh // 2
    draw.rounded_rectangle([cx - slot_w, cy - slot_h // 2, cx + slot_w, cy + slot_h // 2],
                           radius=2, fill=(0, 0, 0, 0), outline=CLR_IRON, width=1)
    # Cutting edge highlight
    draw.line([(cx - bw // 2, cy + bh - 1), (cx + bw // 2, cy + bh - 1)], fill=(200, 200, 210, 120), width=1)


def _draw_prop_matchstick(draw, cx, cy, s):
    """Single matchstick — wood shaft + red/burnt tip."""
    sw = s // 30
    sl = s // 2
    # Wood shaft
    draw.rectangle([cx - sw, cy - sl // 3, cx + sw, cy + sl // 2], fill=CLR_PAPER_AGED, outline=CLR_INK_BROWN, width=1)
    # Wood grain
    for i in range(3):
        gx = cx - sw + 2 + i * (sw // 2)
        draw.line([(gx, cy - sl // 3 + 4), (gx, cy + sl // 2 - 2)], fill=(180, 160, 130, 80), width=1)
    # Match head
    head_r = sw + 3
    draw.ellipse([cx - head_r, cy - sl // 3 - head_r, cx + head_r, cy - sl // 3 + head_r],
                 fill=CLR_RED_ACCENT, outline=CLR_INK_BROWN, width=1)
    # Burnt tip detail
    draw.ellipse([cx - head_r + 2, cy - sl // 3 - head_r + 2, cx + head_r - 2, cy - sl // 3 + head_r - 2],
                 fill=(80, 20, 20, 150))


def generate_prop(prop_id, filename):
    """Generate a realistic aged prop (delegated to rebuild_props v3)."""
    from rebuild_props import generate_prop as _generate_prop_v3
    _generate_prop_v3(prop_id, filename)


    # ── Route EVERY prop to a specific drawing function ──

    # Keys
    if "key" in name and "chain" not in name and "padlock" not in name:
        _draw_prop_key(draw, cx, cy, prop_size)
    elif "keychain" in name:
        _draw_prop_keychain(draw, cx, cy, prop_size)

    # Padlocks
    elif "padlock" in name:
        _draw_prop_padlock(draw, cx, cy, prop_size)

    # Coins & tokens
    elif "coin" in name or ("token" in name and "acrylic" not in name):
        _draw_prop_coin(draw, cx, cy, prop_size)

    # Matchbooks
    elif "match" in name:
        _draw_prop_matchbook(draw, cx, cy, prop_size)

    # Bottles
    elif "whiskey" in name or "whisky" in name:
        _draw_prop_whiskey_bottle(draw, cx, cy, prop_size)
    elif "bottle" in name and "cap" not in name and "opener" not in name:
        _draw_prop_bottle(draw, cx, cy, prop_size)
    elif "bottle_cap" in name:
        _draw_prop_bottle_cap(draw, cx, cy, prop_size)
    elif "bottle_opener" in name or "opener" in name:
        _draw_prop_bottle_opener(draw, cx, cy, prop_size)

    # Pens
    elif "fountain_pen" in name:
        _draw_prop_fountain_pen(draw, cx, cy, prop_size)
    elif "pen" in name:
        _draw_prop_pen(draw, cx, cy, prop_size)

    # Glasses / spectacles
    elif "magnifying_glass" in name:
        _draw_prop_magnifying_glass(draw, cx, cy, prop_size)
    elif "shot_glass" in name:
        _draw_prop_shot_glass(draw, cx, cy, prop_size)
    elif "glass" in name or "spectacle" in name:
        _draw_prop_glasses(draw, cx, cy, prop_size)

    # Watches
    elif "watch" in name:
        _draw_prop_watch(draw, cx, cy, prop_size)

    # Cigarettes
    elif "cigarette" in name:
        _draw_prop_cigarette(draw, cx, cy, prop_size)

    # Lighters
    elif "zippo" in name:
        _draw_prop_zippo_lighter(draw, cx, cy, prop_size)
    elif "lighter" in name:
        _draw_prop_lighter(draw, cx, cy, prop_size)

    # Ashtray
    elif "ashtray" in name:
        _draw_prop_ashtray(draw, cx, cy, prop_size)

    # Rings
    elif "ring" in name and "stirrer" not in name:
        _draw_prop_ring(draw, cx, cy, prop_size)

    # Brooch
    elif "brooch" in name:
        _draw_prop_brooch(draw, cx, cy, prop_size)

    # Buttons
    elif "button" in name:
        _draw_prop_button(draw, cx, cy, prop_size)

    # Postage stamps
    elif "postage" in name:
        _draw_prop_postage_stamp(draw, cx, cy, prop_size)

    # Combs & hair clips
    elif "hair_clip" in name:
        _draw_prop_hair_clip(draw, cx, cy, prop_size)
    elif "comb" in name:
        _draw_prop_comb(draw, cx, cy, prop_size)

    # Scissors
    elif "scissor" in name:
        _draw_prop_scissors(draw, cx, cy, prop_size)

    # Razors
    elif "razor" in name:
        _draw_prop_razor(draw, cx, cy, prop_size)

    # Medals & badges
    elif "badge" in name:
        _draw_prop_vintage_badge(draw, cx, cy, prop_size)
    elif "medal" in name:
        _draw_prop_medal(draw, cx, cy, prop_size)

    # Envelopes
    elif "envelope" in name:
        _draw_prop_envelope(draw, cx, cy, prop_size)

    # Cutlery
    elif "spoon" in name:
        _draw_prop_spoon(draw, cx, cy, prop_size)
    elif "fork" in name:
        _draw_prop_fork(draw, cx, cy, prop_size)
    elif "stirrer" in name:
        _draw_prop_stirrer(draw, cx, cy, prop_size)

    # Corkscrew
    elif "cork" in name:
        _draw_prop_corkscrew(draw, cx, cy, prop_size)

    # Chains & necklaces
    elif "chain" in name or "necklace" in name:
        _draw_prop_chain(draw, cx, cy, prop_size)

    # Straws
    elif "straw" in name:
        _draw_prop_straw(draw, cx, cy, prop_size)

    # Sugar / condiment packets
    elif "sugar" in name or "condiment" in name:
        _draw_prop_sugar_packet(draw, cx, cy, prop_size)

    # Candy wrappers
    elif "candy" in name or ("wrapper" in name and "candy" in name):
        _draw_prop_candy_wrapper(draw, cx, cy, prop_size)

    # Napkins & cloth
    elif "napkin" in name or "cloth" in name or "handkerchief" in name:
        _draw_prop_napkin(draw, cx, cy, prop_size)

    # Jewelry bags & small bags
    elif "jewelry_bag" in name or ("bag" in name and "jewelry" in name):
        _draw_prop_jewelry_bag(draw, cx, cy, prop_size)

    # Diner check — the ONE paper slip
    elif "diner_check" in name:
        _draw_prop_check_slip(draw, cx, cy, prop_size, prop_size * 3 // 4)

    # Newspaper clippings
    elif "newspaper" in name or "flyer" in name:
        _draw_prop_newspaper_clip(draw, cx, cy, prop_size, prop_size * 3 // 4)

    # Record sleeves & vinyl
    elif "record_sleeve" in name:
        _draw_prop_record_sleeve(draw, cx, cy, prop_size, prop_size * 3 // 4)
    elif "vinyl_label" in name:
        _draw_prop_vinyl_label(draw, cx, cy, prop_size)

    # Price stickers
    elif "price" in name:
        _draw_prop_price_sticker(draw, cx, cy, prop_size)

    # Barcode stickers
    elif "barcode" in name:
        _draw_prop_barcode_sticker(draw, cx, cy, prop_size)

    # Rewind stickers
    elif "rewind" in name:
        _draw_prop_rewind_sticker(draw, cx, cy, prop_size)

    # Pocket knife
    elif "pocket_knife" in name or ("knife" in name and "pocket" in name):
        _draw_prop_pocket_knife(draw, cx, cy, prop_size)

    # Compass
    elif "compass" in name:
        _draw_prop_compass(draw, cx, cy, prop_size)

    # Dice
    elif "dice" in name:
        _draw_prop_dice(draw, cx, cy, prop_size)

    # Photograph
    elif "photograph" in name or "photo" in name:
        _draw_prop_photograph_corner(draw, cx, cy, prop_size)

    # Hardware bits
    elif "bolt" in name:
        _draw_prop_small_bolt(draw, cx, cy, prop_size)
    elif "washer" in name:
        _draw_prop_washer(draw, cx, cy, prop_size)
    elif "screw" in name:
        _draw_prop_screw(draw, cx, cy, prop_size)
    elif "nail" in name:
        _draw_prop_nail(draw, cx, cy, prop_size)

    # Fishing hook
    elif "fishing" in name or "fish_hook" in name:
        _draw_prop_fishing_hook(draw, cx, cy, prop_size)

    # Safety pin
    elif "safety_pin" in name:
        _draw_prop_safety_pin(draw, cx, cy, prop_size)

    # Thimble
    elif "thimble" in name:
        _draw_prop_thimble(draw, cx, cy, prop_size)

    # Paperclip
    elif "paperclip" in name or "paper_clip" in name:
        _draw_prop_paperclip(draw, cx, cy, prop_size)

    # Razor blade (distinct from safety_razor)
    elif "razor_blade" in name:
        _draw_prop_razor_blade(draw, cx, cy, prop_size)

    # Matchstick (single stick, distinct from matchbook)
    elif "matchstick" in name or "match_stick" in name:
        _draw_prop_matchstick(draw, cx, cy, prop_size)

    # Absolute fallback — draw a KEY (recognizable silhouette, NOT a paper slip)
    else:
        _draw_prop_key(draw, cx, cy, prop_size)

    # ── Slight random rotation (more subtle than before) ──
    angle = random.uniform(-8, 8)
    img = img.rotate(angle, expand=False, resample=Image.BICUBIC, center=(cx, cy))

    # ── Global semi-transparency for aged, incidental look ──
    # Reduce overall alpha by 25-45% to make props feel worn into the paper
    alpha_factor = random.uniform(0.55, 0.75)
    pixels = img.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            r, g, b, a = pixels[x, y]
            if a > 0:
                pixels[x, y] = (r, g, b, int(a * alpha_factor))

    # ── Add subtle noise / dust grain to prop area ──
    if random.random() < 0.4:
        for _ in range(random.randint(20, 60)):
            nx = cx + random.randint(-prop_size, prop_size)
            ny = cy + random.randint(-prop_size, prop_size)
            if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                r, g, b, a = pixels[nx, ny]
                if a > 20:
                    noise_a = random.randint(30, 80)
                    pixels[nx, ny] = (
                        min(255, r + random.randint(-15, 15)),
                        min(255, g + random.randint(-15, 15)),
                        min(255, b + random.randint(-15, 15)),
                        min(255, a + noise_a // 2)
                    )

    path = os.path.join(ASSETS_DIR, "props", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ prop: {filename} (size={prop_size}, zone={zone})")


# ══════════════════════════════════════════════════════════════
# LEGENDARY ACCENT GENERATOR — Gold Aged Foil Sticker
# Metallic gold foil stickers with peeled/curled edges,
# embossed legendary motifs, oxidation patina, vintage wear
# ══════════════════════════════════════════════════════════════

def _draw_gold_foil_sticker(draw, pixels, cx, cy, w, h):
    """Draw a BRIGHT gold foil sticker base with metallic gradients, peeled edge, holographic shimmer, and aging."""
    # ── 1. Outer peeled-edge shadow (the "翻边" peeled-up effect) ──
    peel_offsets = [
        (random.randint(-12, -4), random.randint(-12, -4)),  # top-left peel
        (random.randint(4, 12), random.randint(-12, -4)),    # top-right peel
        (random.randint(-12, -4), random.randint(4, 12)),    # bottom-left peel
        (random.randint(4, 12), random.randint(4, 12)),      # bottom-right peel
    ]
    # Which corners peel (2-3 corners randomly)
    peel_corners = random.sample([0, 1, 2, 3], random.randint(2, 3))

    # Draw peeled shadow under corners
    for ci in peel_corners:
        px, py = peel_offsets[ci]
        shadow_w = random.randint(12, 22)
        shadow_h = random.randint(12, 22)
        if ci == 0:  # TL
            sr = [cx - w // 2 - shadow_w, cy - h // 2 - shadow_h, cx - w // 2 + shadow_w, cy - h // 2 + shadow_h]
        elif ci == 1:  # TR
            sr = [cx + w // 2 - shadow_w, cy - h // 2 - shadow_h, cx + w // 2 + shadow_w, cy - h // 2 + shadow_h]
        elif ci == 2:  # BL
            sr = [cx - w // 2 - shadow_w, cy + h // 2 - shadow_h, cx - w // 2 + shadow_w, cy + h // 2 + shadow_h]
        else:  # BR
            sr = [cx + w // 2 - shadow_w, cy + h // 2 - shadow_h, cx + w // 2 + shadow_w, cy + h // 2 + shadow_h]
        draw.rounded_rectangle(sr, radius=3, fill=(80, 60, 30, random.randint(60, 100)))

    # ── 2. Main gold foil body — BRIGHTER with laser/holographic shimmer ──
    for x in range(cx - w // 2, cx + w // 2, 2):
        for y in range(cy - h // 2, cy + h // 2, 2):
            # Much brighter gold with laser shimmer
            hue_shift = math.sin((x + y) * 0.05) * 20
            r_base = random.randint(220, 255)  # Brighter gold
            g_base = random.randint(170, 210)
            b_base = random.randint(50, 90)
            alpha = random.randint(230, 255)
            for dx in range(2):
                for dy in range(2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                        pixels[nx, ny] = (r_base, g_base, b_base, alpha)

    # ── 3. LASER/HOLOGRAPHIC shimmer bands across the foil ──
    for i in range(random.randint(3, 6)):
        band_y = cy - h // 2 + random.randint(h // 6, h * 5 // 6)
        band_h = random.randint(4, 10)
        laser_colors = [
            (255, 100, 180),  # pink
            (100, 220, 255),  # cyan
            (255, 255, 100),  # yellow
            (180, 100, 255),  # purple
            (100, 255, 180),  # mint
        ]
        laser_color = random.choice(laser_colors)
        for ly in range(band_y, min(band_y + band_h, cy + h // 2)):
            for lx in range(cx - w // 2 + 4, cx + w // 2 - 4, 2):
                alpha = random.randint(30, 80)
                r_l, g_l, b_l = laser_color
                for dx in range(2):
                    for dy in range(1):
                        nx, ny = lx + dx, ly + dy
                        if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                            existing = pixels[nx, ny]
                            # Blend laser over gold
                            nr = min(255, existing[0] + r_l * alpha // 255)
                            ng = min(255, existing[1] + g_l * alpha // 255)
                            nb = min(255, existing[2] + b_l * alpha // 255)
                            pixels[nx, ny] = (nr, ng, nb, existing[3])

    # ── 4. Gold foil horizontal brush/foil lines (embossed texture) ──
    for y in range(cy - h // 2 + 2, cy + h // 2 - 2, random.randint(3, 6)):
        alpha = random.randint(20, 60)
        shade = random.randint(-20, 20)
        r_ln = max(0, min(255, 240 + shade))
        g_ln = max(0, min(255, 190 + shade))
        b_ln = max(0, min(255, 65 + shade))
        for x in range(cx - w // 2 + 4, cx + w // 2 - 4, 2):
            pixels[x, y] = (r_ln, g_ln, b_ln, alpha)

    # ── 5. Rounded border — bold darker gold ──
    border_w = random.randint(3, 5)
    draw.rounded_rectangle(
        [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
        radius=8,
        outline=(170, 120, 30, random.randint(220, 255)),
        width=border_w,
    )
    # Inner fine border
    draw.rounded_rectangle(
        [cx - w // 2 + border_w + 2, cy - h // 2 + border_w + 2,
         cx + w // 2 - border_w - 2, cy + h // 2 - border_w - 2],
        radius=6,
        outline=(220, 175, 60, random.randint(150, 220)),
        width=1,
    )

    # ── 6. Peeled corner triangles (curled up, revealing aged paper underside) ──
    for ci in peel_corners:
        peel_size = random.randint(14, 26)
        paper_color = (210, 195, 160, random.randint(180, 220))
        if ci == 0:  # TL
            pts = [
                (cx - w // 2, cy - h // 2),
                (cx - w // 2 + peel_size, cy - h // 2),
                (cx - w // 2, cy - h // 2 + peel_size),
            ]
        elif ci == 1:  # TR
            pts = [
                (cx + w // 2, cy - h // 2),
                (cx + w // 2 - peel_size, cy - h // 2),
                (cx + w // 2, cy - h // 2 + peel_size),
            ]
        elif ci == 2:  # BL
            pts = [
                (cx - w // 2, cy + h // 2),
                (cx - w // 2 + peel_size, cy + h // 2),
                (cx - w // 2, cy + h // 2 - peel_size),
            ]
        else:  # BR
            pts = [
                (cx + w // 2, cy + h // 2),
                (cx + w // 2 - peel_size, cy + h // 2),
                (cx + w // 2, cy + h // 2 - peel_size),
            ]
        draw.polygon(pts, fill=paper_color)
        draw.line([pts[0], pts[2]], fill=(200, 150, 50, 180), width=1)

    # ── 7. Oxidation / tarnish spots (patina aging) ──
    for _ in range(random.randint(8, 20)):
        ox = cx + random.randint(-w // 2 + 6, w // 2 - 6)
        oy = cy + random.randint(-h // 2 + 6, h // 2 - 6)
        r = random.randint(1, 4)
        patina = random.choice([
            (80, 100, 60, random.randint(20, 50)),
            (90, 75, 50, random.randint(20, 45)),
            (60, 70, 65, random.randint(15, 40)),
        ])
        draw.ellipse([ox - r, oy - r, ox + r, oy + r], fill=patina)

    # ── 8. Edge wear dots ──
    for _ in range(random.randint(6, 14)):
        ex = cx + random.randint(-w // 2 - 6, w // 2 + 6)
        ey = cy + random.randint(-h // 2 - 6, h // 2 + 6)
        r = random.randint(1, 3)
        draw.ellipse([ex - r, ey - r, ex + r, ey + r],
                     fill=(140, 100, 55, random.randint(35, 70)))


def _draw_legendary_motif_gold(draw, cx, cy, motif_size, name):
    """Draw embossed legendary motif — BRIGHT dark gold/brown on the gold foil, with laser accent."""
    emboss = (90, 60, 20, random.randint(200, 250))  # More opaque
    highlight = (255, 240, 170, random.randint(120, 200))  # Brighter highlight
    laser_pink = (255, 80, 180, random.randint(100, 180))  # Laser accent

    if "crown" in name:
        mh = motif_size
        base_y = cy + mh // 2
        tip_y = cy - mh // 2
        pts = [
            (cx - mh, base_y), (cx - mh, cy + mh // 4), (cx - mh // 2, tip_y),
            (cx - mh // 4, cy - mh // 6), (cx, tip_y - 4),
            (cx + mh // 4, cy - mh // 6), (cx + mh // 2, tip_y),
            (cx + mh, cy + mh // 4), (cx + mh, base_y),
        ]
        draw.polygon(pts, fill=emboss)
        # Crown jewels — bright red rubies with laser glow
        for jx in [cx - mh // 2, cx, cx + mh // 2]:
            draw.ellipse([jx - 4, tip_y - 4, jx + 4, tip_y + 4],
                         fill=(255, 30, 30, 255))
            draw.ellipse([jx - 2, tip_y - 2, jx + 1, tip_y + 1],
                         fill=(255, 200, 200, 180))
        # Bright highlight edge
        draw.line([(cx - mh, base_y), (cx - mh, cy + mh // 4)], fill=highlight, width=2)

    elif "crystal_shard" in name:
        s = motif_size
        pts = [
            (cx, cy - s), (cx + s // 2, cy - s // 4),
            (cx + s // 2, cy + s // 4), (cx, cy + s),
            (cx - s // 2, cy + s // 4), (cx - s // 2, cy - s // 4),
        ]
        draw.polygon(pts, fill=emboss)
        # Bright facet lines
        draw.line([(cx, cy - s), (cx, cy + s)], fill=highlight, width=2)
        draw.line([(cx - s // 2, cy), (cx + s // 2, cy)], fill=highlight, width=2)
        # Laser shimmer on crystal
        draw.line([(cx - s // 4, cy - s // 2), (cx + s // 4, cy - s // 2)],
                  fill=laser_pink, width=1)

    elif "holo_seal" in name:
        r = motif_size
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=emboss)
        draw.ellipse([cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5],
                     outline=highlight, width=2)
        # Inner emblem — holographic effect
        draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 3, cy + r // 3],
                     fill=(255, 100, 180, 200))  # Pink holographic
        draw.ellipse([cx - r // 4, cy - r // 4, cx + r // 4, cy + r // 4],
                     fill=(255, 255, 200, 150))

    elif "diamond_clip" in name:
        s = motif_size
        pts = [(cx, cy - s), (cx + s * 3 // 5, cy), (cx, cy + s), (cx - s * 3 // 5, cy)]
        draw.polygon(pts, fill=emboss)
        draw.polygon(pts, outline=highlight, width=2)
        # Inner diamond sparkle
        draw.polygon([(cx, cy - s // 2), (cx + s // 4, cy), (cx, cy + s // 2), (cx - s // 4, cy)],
                     fill=(255, 255, 255, 100))

    elif "chain_luxe" in name:
        r = motif_size // 5
        num = 5
        for i in range(num):
            lx = cx - motif_size + i * (2 * motif_size) // num + r
            draw.ellipse([lx - r, cy - r // 2, lx + r, cy + r // 2],
                         outline=emboss, width=3)
            if i < num - 1:
                nx = lx + r * 2
                draw.line([(lx + r, cy), (nx - r, cy)], fill=emboss, width=3)

    elif "pearl_tag" in name:
        r = motif_size // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=emboss)
        draw.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2],
                     fill=(255, 230, 160, 200))  # Brighter pearl
        # Highlight
        draw.ellipse([cx - r // 3, cy - r // 3, cx + r // 4, cy + r // 4],
                     fill=(255, 255, 255, 180))

    elif "laser_sticker" in name:
        s = motif_size
        # 8-pointed laser star
        pts = []
        for i in range(8):
            a = math.radians(45 * i - 90)
            r_val = s if i % 2 == 0 else s // 2
            pts.append((cx + int(r_val * math.cos(a)), cy + int(r_val * math.sin(a))))
        draw.polygon(pts, fill=laser_pink, outline=highlight, width=2)
        # Inner rainbow ring
        for i in range(3):
            inner_r = s // 3 + i * (s // 6)
            hue_color = [
                (255, 80, 180, 180),
                (100, 220, 255, 180),
                (255, 255, 100, 180),
            ][i]
            draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
                         outline=hue_color, width=2)

    elif "gem_badge" in name:
        s = motif_size
        pts = [
            (cx - s // 2, cy - s), (cx + s // 2, cy - s),
            (cx + s // 2, cy), (cx, cy + s), (cx - s // 2, cy),
        ]
        draw.polygon(pts, fill=emboss, outline=highlight, width=2)
        # Center gem — bright
        draw.ellipse([cx - s // 4, cy - s // 2, cx + s // 4, cy],
                     fill=(255, 40, 40, 255))
        draw.ellipse([cx - s // 5, cy - s // 3, cx + s // 5, cy - s // 10],
                     fill=(255, 255, 255, 150))

    elif "acrylic_token" in name:
        r = motif_size
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=emboss, width=3)
        # Holographic inner
        draw.ellipse([cx - r + 7, cy - r + 7, cx + r - 7, cy + r - 7],
                     fill=(100, 220, 255, 160))
        draw.ellipse([cx - r // 4, cy - r // 4, cx + r // 4, cy + r // 4],
                     fill=emboss)
        draw.ellipse([cx - r // 6, cy - r // 6, cx + r // 8, cy + r // 8],
                     fill=(255, 255, 255, 180))

    else:
        # Generic embossed circle with laser ring
        r = motif_size // 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=emboss)
        draw.ellipse([cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2],
                     outline=highlight, width=2)


def generate_legendary_accent_sticker(accent_id, filename):
    """Generate a gold foil vintage sticker — metallic gold with peeled edges, embossed motif, aged patina."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pixels = img.load()

    cx = random.randint(200, CANVAS - 200)
    cy = random.randint(180, CANVAS - 180)
    name = accent_id.lower()
    w = random.randint(140, 260)  # Larger for visibility
    h = random.randint(100, 200)

    # Draw the gold foil sticker with all effects
    _draw_gold_foil_sticker(draw, pixels, cx, cy, w, h)

    # Draw the embossed motif — larger for visibility
    motif_size = min(w, h) // 2  # Larger motif
    _draw_legendary_motif_gold(draw, cx, cy, motif_size, name)

    # ── Rotation ──
    angle = random.uniform(-12, 12)
    img = img.rotate(angle, expand=False, resample=Image.BICUBIC, center=(cx, cy))

    out_dir = os.path.join(ASSETS_DIR, "legendary_accent")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ legendary gold sticker: {filename}")


# ══════════════════════════════════════════════════════════════
# MATERIAL / PATTERN GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_material_pattern(mat_id, filename):
    """Generate material texture or pattern layer — retro archive aesthetic, brighter & more visible."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pixels = img.load()

    name = mat_id.lower()

    # ── Material: Transparent Receipt ──
    if "transparent_receipt" in name:
        # Visible glass-like overlay with warm tint
        for x in range(0, CANVAS, 2):
            for y in range(0, CANVAS, 2):
                pixels[x, y] = (235, 225, 210, random.randint(4, 14))
        draw.rectangle([10, 10, CANVAS - 10, CANVAS - 10],
                       outline=(180, 170, 150, 50), width=2)

    # ── Material: Frosted Receipt ──
    elif "frosted_receipt" in name:
        for x in range(0, CANVAS, 2):
            for y in range(0, CANVAS, 2):
                alpha = random.randint(5, 20)
                pixels[x, y] = (250, 245, 235, alpha)

    # ── Material: Holographic Receipt ──
    elif "holographic_receipt" in name:
        # Brighter holographic bands for visibility
        for y in range(0, CANVAS, 2):
            t = y / CANVAS
            r = int(50 + 50 * math.sin(t * math.pi * 4))
            g = int(40 + 50 * math.sin((t + 0.33) * math.pi * 4))
            b = int(50 + 50 * math.sin((t + 0.67) * math.pi * 4))
            for x in range(0, CANVAS, 2):
                pixels[x, y] = (r, g, b, random.randint(6, 18))

    # ── Material: Black Gold Receipt ──
    elif "black_gold_receipt" in name:
        # More visible gold flakes on dark
        for _ in range(random.randint(300, 500)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 4)
            alpha = random.randint(20, 60)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(210, 170, 40, alpha))
        draw.rectangle([5, 5, CANVAS - 5, CANVAS - 5],
                       outline=(200, 160, 40, 60), width=2)
        draw.rectangle([10, 10, CANVAS - 10, CANVAS - 10],
                       outline=(180, 140, 30, 40), width=1)

    # ── Material: Silver Foil Receipt ──
    elif "silver_foil_receipt" in name:
        for _ in range(random.randint(200, 400)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 3)
            alpha = random.randint(15, 45)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(220, 215, 210, alpha))

    # ── Material: Glow Ink ──
    elif "glow_ink" in name:
        # Brighter, more visible glow dots
        for _ in range(random.randint(80, 200)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(3, 10)
            alpha = random.randint(10, 40)
            color = random.choice([
                (120, 255, 200, alpha),
                (255, 210, 120, alpha),
                (210, 160, 255, alpha),
                (255, 255, 180, alpha),
            ])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)

    # ── Material: Chrome Edge ──
    elif "chrome_edge" in name:
        # More visible metallic border
        for i in range(6):
            inset = 3 + i * 3
            alpha = 80 - i * 10
            draw.rectangle([inset, inset, CANVAS - inset, CANVAS - inset],
                           outline=(190, 185, 175, max(10, alpha)), width=1)

    # ── Material: Glass Archive ──
    elif "glass_archive" in name:
        # Clearer archival sleeve with warm tint
        draw.rectangle([8, 8, CANVAS - 8, CANVAS - 8],
                       outline=(200, 195, 175, 40), width=3)
        draw.rectangle([12, 12, CANVAS - 12, CANVAS - 12],
                       outline=(210, 205, 185, 25), width=1)
        # Visible diagonal reflection
        for y in range(0, CANVAS, 15):
            alpha = random.randint(2, 8)
            x0 = y
            for x in range(max(0, x0 - 8), min(CANVAS, x0 + 8)):
                pixels[x, y] = (255, 250, 240, alpha)

    # ── Pattern: Leopard ──
    elif "leopard" in name:
        # More visible vintage leopard spots with warm brown tones
        for _ in range(random.randint(40, 80)):
            cx_p = random.randint(50, CANVAS - 50)
            cy_p = random.randint(50, CANVAS - 50)
            r1 = random.randint(14, 32)
            r2 = random.randint(10, 24)
            spot_color = (100, 65, 30, random.randint(25, 55))
            draw.ellipse([cx_p - r1, cy_p - r2, cx_p + r1, cy_p + r2], fill=spot_color)
            inner_color = (75, 45, 15, random.randint(15, 40))
            draw.ellipse([cx_p - r2 // 2, cy_p - r2 // 2, cx_p + r2 // 2, cy_p + r2 // 2],
                         fill=inner_color)

    # ── Pattern: Snakeskin ──
    elif "snakeskin" in name:
        for row in range(0, CANVAS, random.randint(12, 20)):
            offset = random.randint(0, 10) if (row // 18) % 2 == 0 else random.randint(10, 20)
            for col in range(offset, CANVAS, random.randint(16, 24)):
                s = random.randint(8, 14)
                diamond = [
                    (col, row - s),
                    (col + s // 2, row),
                    (col, row + s),
                    (col - s // 2, row),
                ]
                draw.polygon(diamond, outline=(120, 100, 75, random.randint(15, 40)), width=1)

    # ── Pattern: Holo Grid ──
    elif "holo_grid" in name:
        spacing = random.randint(24, 44)
        for x in range(spacing, CANVAS, spacing):
            draw.line([(x, 0), (x, CANVAS)], fill=(180, 175, 160, random.randint(8, 20)), width=1)
        for y in range(spacing, CANVAS, spacing):
            draw.line([(0, y), (CANVAS, y)], fill=(180, 175, 160, random.randint(8, 20)), width=1)

    # ── Pattern: Gold Fleck ──
    elif "gold_fleck" in name:
        for _ in range(random.randint(150, 350)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 5)
            alpha = random.randint(30, 100)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(225, 185, 45, alpha))

    # ── Pattern: Iridescent Wave ──
    elif "iridescent_wave" in name:
        for y in range(0, CANVAS, 2):
            t = y / CANVAS
            wave = int(40 * math.sin(t * math.pi * 5))
            r = int(60 + 40 * math.sin(t * math.pi * 3))
            g = int(50 + 40 * math.sin((t + 0.5) * math.pi * 3))
            b = int(60 + 30 * math.sin((t + 1.0) * math.pi * 3))
            for x in range(0, CANVAS, 2):
                if (x + wave) % 30 < 15:
                    pixels[x, y] = (r, g, b, random.randint(5, 18))

    # ── Pattern: Security Print ──
    elif "security_print" in name:
        # Brighter micro-text lines — like old banknote / certificate patterns
        for y in range(10, CANVAS, random.randint(6, 12)):
            alpha = random.randint(8, 22)
            for x in range(0, CANVAS, 2):
                if (x + y) % 8 < 4:
                    pixels[x, y] = (120, 110, 100, alpha)
        # Guilloche-style curved lines — more visible
        for i in range(random.randint(4, 8)):
            cy_p = random.randint(200, 800)
            amplitude = random.randint(30, 80)
            frequency = random.uniform(0.02, 0.06)
            color = (100, 90, 80, random.randint(8, 20))
            pts = []
            for x in range(0, CANVAS, 3):
                y = cy_p + int(amplitude * math.sin(frequency * x))
                pts.append((x, y))
            if len(pts) >= 2:
                for j in range(len(pts) - 1):
                    draw.line([pts[j], pts[j + 1]], fill=color, width=1)

    out_dir = os.path.join(ASSETS_DIR, "material_pattern")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ material/pattern: {filename}")


# ══════════════════════════════════════════════════════════════
# LEGENDARY OVERLAY GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_legendary_overlay(overlay_id, filename):
    """Generate legendary rarity overlay effects — BRIGHT, VISIBLE, with holographic/laser effects."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pixels = img.load()

    name = overlay_id.lower()

    # ── Holo Prism — BRIGHT rainbow holographic bands ──
    if "holo_prism" in name:
        for y in range(0, CANVAS, 1):
            t = y / CANVAS
            for x in range(0, CANVAS, 2):
                hue = (t * 3 + x / CANVAS * 2) % 1.0
                # Much brighter prism colors
                r = int(80 + 170 * abs(math.sin(hue * math.pi * 2)))
                g = int(80 + 170 * abs(math.sin((hue + 0.33) * math.pi * 2)))
                b = int(80 + 170 * abs(math.sin((hue + 0.67) * math.pi * 2)))
                alpha = random.randint(25, 55)  # Much more visible
                pixels[x, y] = (r, g, b, alpha)
                if x + 1 < CANVAS:
                    pixels[x + 1, y] = (r, g, b, alpha)

    # ── Gold Dust — BRIGHT glittering particles ──
    elif "gold_dust" in name:
        for _ in range(random.randint(800, 1500)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(2, 6)
            alpha = random.randint(60, 150)  # Much brighter
            gold_shade = random.randint(200, 255)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(gold_shade, gold_shade - 40, 20, alpha))
        # Larger sparkle highlights
        for _ in range(random.randint(30, 60)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            draw.ellipse([x - 8, y - 8, x + 8, y + 8],
                         fill=(255, 255, 200, random.randint(40, 100)))

    # ── Iridescent Glow — BRIGHT center radial rainbow ──
    elif "iridescent_glow" in name:
        cx, cy = CANVAS // 2, CANVAS // 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)
        for x in range(0, CANVAS, 3):
            for y in range(0, CANVAS, 3):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                if dist < max_dist * 0.85:
                    t = dist / (max_dist * 0.85)
                    alpha = int(max(0, (1 - t) * 80))  # Much brighter
                    hue = (x / CANVAS + y / CANVAS * 1.5) % 1.0
                    r = int(120 + 135 * math.sin(hue * math.pi * 2))
                    g = int(120 + 135 * math.sin((hue + 0.33) * math.pi * 2))
                    b = int(120 + 135 * math.sin((hue + 0.67) * math.pi * 2))
                    for dx in range(3):
                        for dy in range(3):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                                pixels[nx, ny] = (r, g, b, alpha)

    # ── Luxe Vignette — deeper, more visible dark edges ──
    elif "luxe_vignette" in name:
        cx, cy = CANVAS // 2, CANVAS // 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)
        for x in range(0, CANVAS, 2):
            for y in range(0, CANVAS, 2):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                alpha = int(max(0, min(80, (dist / max_dist) * 100 - 30)))
                if alpha > 0:
                    pixels[x, y] = (10, 8, 5, alpha)

    # ── Crystal Spark — BRIGHT star sparkles ──
    elif "crystal_spark" in name:
        for _ in range(random.randint(40, 80)):
            sx = random.randint(30, CANVAS - 30)
            sy = random.randint(30, CANVAS - 30)
            size = random.randint(12, 30)
            alpha = random.randint(120, 220)  # Much brighter
            # 6-pointed star sparkle
            spark_colors = [
                (255, 255, 255, alpha),
                (200, 230, 255, alpha),
                (255, 220, 255, alpha),
            ]
            spark_color = random.choice(spark_colors)
            # Main cross
            draw.line([(sx - size, sy), (sx + size, sy)], fill=spark_color, width=2)
            draw.line([(sx, sy - size), (sx, sy + size)], fill=spark_color, width=2)
            # Diagonals
            d = int(size * 0.7)
            draw.line([(sx - d, sy - d), (sx + d, sy + d)], fill=spark_color, width=1)
            draw.line([(sx + d, sy - d), (sx - d, sy + d)], fill=spark_color, width=1)
            # Center glow
            draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4],
                         fill=(255, 255, 255, min(255, alpha + 30)))

    # ── Neon Archive — BRIGHT neon border glow ──
    elif "neon_archive" in name:
        # Bold neon edge glow — much more visible
        colors = [
            (255, 80, 180, 40),   # hot pink
            (80, 220, 255, 40),   # cyan
            (255, 220, 60, 40),   # yellow
            (180, 80, 255, 40),   # purple
        ]
        for i, clr in enumerate(colors):
            inset = 8 + i * 12
            draw.rectangle([inset, inset, CANVAS - inset, CANVAS - inset],
                           outline=(clr[0], clr[1], clr[2], clr[3] + i * 15), width=2)
        # Inner bright glow line
        draw.rectangle([6, 6, CANVAS - 6, CANVAS - 6],
                       outline=(255, 255, 255, 50), width=1)

    # ── Rainbow Foil — BRIGHT iridescent holographic foil ──
    elif "rainbow_foil" in name:
        for y in range(0, CANVAS, 1):
            t = y / CANVAS
            # Much brighter rainbow
            r = int(80 + 170 * abs(math.sin(t * math.pi * 3)))
            g = int(80 + 170 * abs(math.sin((t + 0.33) * math.pi * 3)))
            b = int(80 + 170 * abs(math.sin((t + 0.67) * math.pi * 3)))
            alpha = random.randint(30, 65)
            for x in range(0, CANVAS, 2):
                pixels[x, y] = (r, g, b, alpha)
                if x + 1 < CANVAS:
                    pixels[x + 1, y] = (r, g, b, alpha)
        # Add holographic shimmer lines
        for _ in range(random.randint(30, 60)):
            y = random.randint(0, CANVAS - 1)
            alpha = random.randint(40, 90)
            r = random.randint(180, 255)
            g = random.randint(180, 255)
            b = random.randint(180, 255)
            for x in range(0, CANVAS, 2):
                pixels[x, y] = (r, g, b, alpha)

    # ── Ultra Rare Shimmer — BRIGHT dense particle field ──
    elif "ultra_rare_shimmer" in name:
        # Much denser and brighter shimmer
        for _ in range(random.randint(1500, 3000)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(2, 5)
            alpha = random.randint(40, 120)
            shimmer = random.choice([
                (255, 255, 255, alpha),
                (255, 240, 200, alpha),
                (220, 240, 255, alpha),
                (255, 220, 255, alpha),
                (200, 255, 220, alpha),
            ])
            draw.ellipse([x - r, y - r, x + r, y + r], fill=shimmer)
        # Larger sparkle accents
        for _ in range(random.randint(20, 40)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            draw.ellipse([x - 10, y - 10, x + 10, y + 10],
                         fill=(255, 255, 255, random.randint(20, 60)))

    out_dir = os.path.join(ASSETS_DIR, "legendary_accent")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ legendary overlay: {filename}")


# ══════════════════════════════════════════════════════════════
# DAMAGE GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_damage(dmg_id, filename):
    """Generate a paper damage texture."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    name = dmg_id.lower()

    if "coffee_ring" in name:
        cx = random.randint(300, 700)
        cy = random.randint(250, 750)
        r = random.randint(80, 180)
        color = (139, 90, 43, random.randint(40, 80))
        for _ in range(3):
            offset = random.randint(-5, 5)
            draw.ellipse(
                [cx - r + offset, cy - r + offset, cx + r + offset, cy + r + offset],
                outline=color, width=random.randint(3, 8)
            )
            r -= random.randint(10, 30)

    elif "fold" in name:
        if "02" in name or random.random() < 0.5:
            x = random.randint(CANVAS // 3, 2 * CANVAS // 3)
            draw.line([(x, 0), (x + random.randint(-10, 10), CANVAS)],
                      fill=(80, 75, 70, random.randint(30, 60)), width=random.randint(1, 3))
        else:
            y = random.randint(CANVAS // 3, 2 * CANVAS // 3)
            draw.line([(0, y + random.randint(-10, 10)), (CANVAS, y)],
                      fill=(80, 75, 70, random.randint(30, 60)), width=random.randint(1, 3))

    elif "edge_wear" in name:
        edge = random.choice(["top", "bottom", "left", "right"])
        color = (60, 55, 50, random.randint(20, 50))
        for _ in range(random.randint(5, 15)):
            if edge == "top":
                x = random.randint(0, CANVAS)
                draw.arc([x - 30, -10, x + 30, 40], 180, 360, fill=color, width=2)
            elif edge == "bottom":
                x = random.randint(0, CANVAS)
                draw.arc([x - 30, CANVAS - 40, x + 30, CANVAS + 10], 0, 180, fill=color, width=2)
            elif edge == "left":
                y = random.randint(0, CANVAS)
                draw.arc([-10, y - 30, 40, y + 30], 90, 270, fill=color, width=2)
            else:
                y = random.randint(0, CANVAS)
                draw.arc([CANVAS - 40, y - 30, CANVAS + 10, y + 30], 270, 90, fill=color, width=2)

    elif "tape" in name:
        cx = random.randint(150, CANVAS - 150)
        cy = random.randint(100, CANVAS - 100)
        tw = random.randint(60, 150)
        th = random.randint(20, 50)
        tape_color = (220, 210, 180, random.randint(60, 100))
        draw.rounded_rectangle(
            [cx - tw // 2, cy - th // 2, cx + tw // 2, cy + th // 2],
            radius=3, fill=tape_color, outline=(200, 190, 160, 60), width=1
        )

    elif "water_stain" in name:
        cx = random.randint(200, 800)
        cy = random.randint(200, 800)
        for _ in range(random.randint(3, 7)):
            r = random.randint(40, 120)
            ox = random.randint(-30, 30)
            oy = random.randint(-30, 30)
            color = (180, 175, 160, random.randint(15, 40))
            draw.ellipse(
                [cx - r + ox, cy - r + oy, cx + r + ox, cy + r + oy],
                fill=color
            )

    elif "thermal_fade" in name:
        for y in range(0, CANVAS, random.randint(3, 8)):
            alpha = random.randint(5, 25)
            draw.line([(0, y), (CANVAS, y + random.randint(0, 2))],
                      fill=(200, 195, 180, alpha), width=1)

    elif "dust_specks" in name:
        for _ in range(random.randint(100, 300)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 3)
            alpha = random.randint(10, 40)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(80, 75, 70, alpha))

    elif "corner_curl" in name:
        corner = random.choice(["tl", "tr", "bl", "br"])
        s = random.randint(60, 120)
        color = (200, 195, 185, random.randint(30, 60))
        if corner == "tl":
            draw.polygon([(0, 0), (s, 0), (0, s)], fill=color)
        elif corner == "tr":
            draw.polygon([(CANVAS, 0), (CANVAS - s, 0), (CANVAS, s)], fill=color)
        elif corner == "bl":
            draw.polygon([(0, CANVAS), (s, CANVAS), (0, CANVAS - s)], fill=color)
        else:
            draw.polygon([(CANVAS, CANVAS), (CANVAS - s, CANVAS), (CANVAS, CANVAS - s)], fill=color)

    elif "scan_noise" in name:
        for y in range(0, CANVAS, random.randint(4, 10)):
            alpha = random.randint(5, 20)
            draw.line([(0, y), (CANVAS, y)], fill=(0, 0, 0, alpha), width=1)

    elif "small_tear" in name:
        edge = random.choice(["top", "bottom", "left", "right"])
        cx_tear = random.randint(CANVAS // 4, 3 * CANVAS // 4)
        color = (40, 35, 30, random.randint(40, 80))
        if edge in ("top", "bottom"):
            y = 0 if edge == "top" else CANVAS
            pts = [(cx_tear - 20, y)]
            for i in range(5):
                pts.append((cx_tear - 10 + i * 5, y + random.randint(-15, 15)))
            pts.append((cx_tear + 20, y))
            draw.polygon(pts, fill=color)
        else:
            x = 0 if edge == "left" else CANVAS
            pts = [(x, cx_tear - 20)]
            for i in range(5):
                pts.append((x + random.randint(-15, 15), cx_tear - 10 + i * 5))
            pts.append((x, cx_tear + 20))
            draw.polygon(pts, fill=color)

    path = os.path.join(ASSETS_DIR, "damage", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ damage: {filename}")


# ══════════════════════════════════════════════════════════════
# OVERLAY GENERATOR (STANDARD)
# ══════════════════════════════════════════════════════════════

def generate_overlay(overlay_id, filename):
    """Generate a full-screen overlay/filter."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pixels = img.load()

    name = overlay_id.lower()

    if "film_grain" in name:
        for x in range(0, CANVAS, random.randint(1, 3)):
            for y in range(0, CANVAS, random.randint(1, 3)):
                noise = random.randint(0, 25)
                pixels[x, y] = (noise, noise, noise, random.randint(5, 15))

    elif "scan_noise" in name:
        for y in range(0, CANVAS, random.randint(2, 6)):
            alpha = random.randint(3, 12)
            for x in range(CANVAS):
                if random.random() < 0.3:
                    pixels[x, y] = (0, 0, 0, alpha)

    elif "dust" in name:
        for _ in range(random.randint(30, 80)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 4)
            alpha = random.randint(10, 40)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(200, 190, 170, alpha))

    elif "crt_grain" in name:
        for y in range(0, CANVAS, 3):
            alpha = random.randint(2, 8)
            for x in range(CANVAS):
                if random.random() < 0.15:
                    pixels[x, y] = (random.randint(0, 30), random.randint(0, 40), random.randint(0, 30), alpha)

    elif "rain_glow" in name:
        for _ in range(random.randint(200, 500)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(2, 10)
            alpha = random.randint(2, 10)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(30, 50, 80, alpha))

    elif "glass_glare" in name:
        for y in range(0, CANVAS):
            alpha = random.randint(1, 8)
            x0 = y
            for x in range(max(0, x0 - 30), min(CANVAS, x0 + 30)):
                pixels[x, y] = (255, 255, 255, alpha)

    elif "archive_yellowing" in name:
        for x in range(0, CANVAS, 2):
            for y in range(0, CANVAS, 2):
                alpha = random.randint(3, 12)
                pixels[x, y] = (200, 180, 120, alpha)

    elif "soft_vignette" in name:
        cx, cy = CANVAS // 2, CANVAS // 2
        max_dist = math.sqrt(cx ** 2 + cy ** 2)
        for x in range(0, CANVAS, 4):
            for y in range(0, CANVAS, 4):
                dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                alpha = int(max(0, min(30, (dist / max_dist) * 40)))
                if alpha > 0:
                    for dx in range(4):
                        for dy in range(4):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < CANVAS and 0 <= ny < CANVAS:
                                pixels[nx, ny] = (0, 0, 0, alpha)

    elif "faded_ink" in name:
        for y in range(0, CANVAS, random.randint(3, 8)):
            alpha = random.randint(2, 10)
            for x in range(0, CANVAS, random.randint(2, 5)):
                pixels[x, y] = (230, 225, 210, alpha)

    path = os.path.join(ASSETS_DIR, "overlays", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ overlay: {filename}")


# ══════════════════════════════════════════════════════════════
# MAIN: Generate all assets
# ══════════════════════════════════════════════════════════════

# ── STAMPS (target: 26 = 18 regular + 8 legendary) ──
STAMPS_TO_GENERATE = [
    # 11 standard stamps
    ("STAMP_LAST_ORDER",     "stamp_last_order_red.png",     "ellipse",  (200, 30, 30, 200)),
    ("STAMP_OVERDUE",        "stamp_overdue_red.png",        "hexagon",  (220, 80, 20, 210)),
    ("STAMP_NO_VACANCY",     "stamp_no_vacancy_red.png",     "circle",   (180, 20, 100, 200)),
    ("STAMP_FINAL_SALE",     "stamp_final_sale_red.png",     "rect",     (30, 30, 200, 210)),
    ("STAMP_PAWN_HOLD",      "stamp_pawn_hold_red.png",      "hexagon",  (160, 100, 20, 200)),
    ("STAMP_UNCLAIMED",      "stamp_unclaimed_red.png",      "ellipse",  (20, 140, 80, 200)),
    ("STAMP_DO_NOT_OPEN",    "stamp_do_not_open_red.png",    "circle",   (180, 20, 20, 220)),
    ("STAMP_STORE_CREDIT",   "stamp_store_credit_red.png",   "rect",     (100, 30, 180, 210)),
    ("STAMP_PAID_CASH",      "stamp_paid_cash_red.png",      "ellipse",  (20, 100, 20, 200)),
    ("STAMP_DUE_FRIDAY",     "stamp_due_friday_red.png",     "hexagon",  (140, 20, 140, 200)),
    ("STAMP_RETURNED_EMPTY", "stamp_returned_empty_red.png", "circle",   (60, 60, 60, 210)),
    # 8 legendary stamps (gold/rare color schemes)
    ("STAMP_GENESIS",          "stamp_genesis_gold.png",          "circle",   (200, 160, 20, 220)),
    ("STAMP_1_OF_1",           "stamp_1_of_1_gold.png",           "hexagon",  (200, 160, 20, 230)),
    ("STAMP_ARCHIVED_FOREVER", "stamp_archived_forever_gold.png", "rect",     (180, 140, 30, 210)),
    ("STAMP_ULTRA_RARE",       "stamp_ultra_rare_gold.png",       "ellipse",  (200, 150, 40, 220)),
    ("STAMP_VAULTED",          "stamp_vaulted_gold.png",          "circle",   (180, 140, 30, 210)),
    ("STAMP_REDEEMED",         "stamp_redeemed_gold.png",         "hexagon",  (190, 150, 20, 220)),
    ("STAMP_ZERO_SUPPLY",      "stamp_zero_supply_gold.png",      "rect",     (200, 160, 20, 210)),
    ("STAMP_GOLD_SEAL",        "stamp_gold_seal_gold.png",        "ellipse",  (210, 170, 30, 230)),
]

# ── HANDWRITTEN (target: 30) ──
HANDWRITTEN_TO_GENERATE = [
    # Existing 21
    ("NOTE_LAST_ORDER", "note_last_order.png", "top_left"),
    ("NOTE_LATE_FEE", "note_late_fee.png", "top_right"),
    ("NOTE_RETURNED_EMPTY", "note_returned_empty.png", "bottom_left"),
    ("NOTE_DUE_FRIDAY", "note_due_friday.png", "bottom_right"),
    ("NOTE_TAPE_12", "note_tape_12.png", "center"),
    ("NOTE_ROOM_8", "note_room_8.png", "random"),
    ("NOTE_EXIT_22", "note_exit_22.png", "top_left"),
    ("NOTE_PAID_CASH", "note_paid_cash.png", "top_right"),
    ("NOTE_LAST_COPY", "note_last_copy.png", "bottom_left"),
    ("NOTE_A_SIDE_GONE", "note_a_side_gone.png", "bottom_right"),
    ("NOTE_TRACK_07", "note_track_07.png", "center"),
    ("NOTE_STORE_CREDIT", "note_store_credit.png", "top_left"),
    ("NOTE_LAST_SHIFT", "note_last_shift.png", "top_right"),
    ("NOTE_AISLE_3", "note_aisle_3.png", "bottom_left"),
    ("NOTE_512PM", "note_512pm.png", "bottom_right"),
    ("NOTE_FINAL_SALE", "note_final_sale.png", "center"),
    ("NOTE_REGISTER_2", "note_register_2.png", "top_left"),
    ("NOTE_30_DAYS", "note_30_days.png", "top_right"),
    ("NOTE_UNCLAIMED", "note_unclaimed.png", "bottom_left"),
    ("NOTE_HOLD_TAG", "note_hold_tag.png", "bottom_right"),
    ("NOTE_CLAIM_BY_5", "note_claim_by_5.png", "center"),
    # 9 new handwritten notes for series expansion
    ("NOTE_REWIND", "note_rewind.png", "top_left"),
    ("NOTE_SIDE_B", "note_side_b.png", "top_right"),
    ("NOTE_TABLE_6", "note_table_6.png", "bottom_left"),
    ("NOTE_SERVER_M", "note_server_m.png", "bottom_right"),
    ("NOTE_BOOTH_4", "note_booth_4.png", "center"),
    ("NOTE_CASE_14", "note_case_14.png", "random"),
    ("NOTE_LAST_NIGHT", "note_last_night.png", "top_left"),
    ("NOTE_NO_VACANCY", "note_no_vacancy.png", "top_right"),
    ("NOTE_1138PM", "note_1138pm.png", "bottom_left"),
]

# ── PROPS (target: 60+ — DIVERSE retro objects, minimal paper slips) ──
PROPS_TO_GENERATE = [
    # === Paper items (MINIMAL — only 5 distinctly different types) ===
    "PROP_DINER_CHECK_01",          # paper receipt — distinct jagged top + lines
    "PROP_NEWSPAPER_CLIP_01",       # torn newspaper clipping — text columns
    "PROP_MATCHBOOK_01",            # matchbook — iconic, recognizable
    "PROP_MATCHBOOK_MOTEL_01",
    "PROP_POSTAGE_STAMP_01",        # postage stamp — perforated edge
    # === Keys & Hardware ===
    "PROP_OLD_KEY_01", "PROP_OLD_KEY_02", "PROP_OLD_KEY_03",
    "PROP_KEYCHAIN_01",
    "PROP_PADLOCK_01",
    # === Coins & Currency ===
    "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_GAS_STATION_TOKEN_01",
    "PROP_VINTAGE_COIN_03",
    # === Jewelry & Accessories ===
    "PROP_VINTAGE_RING_01", "PROP_VINTAGE_RING_02",
    "PROP_VINTAGE_BUTTON_01", "PROP_VINTAGE_BUTTON_02",
    "PROP_BROOCH_01",
    "PROP_VINTAGE_GLASSES_01",
    "PROP_POCKET_WATCH_01",
    # === Stationery ===
    "PROP_VINTAGE_PEN_01", "PROP_VINTAGE_PEN_02", "PROP_FOUNTAIN_PEN_01",
    "PROP_VINTAGE_SCISSORS_01",
    "PROP_SAFETY_RAZOR_01",
    "PROP_VINTAGE_COMB_01", "PROP_HAIR_CLIP_01",
    "PROP_ENVELOPE_CORNER_01",
    # === Smoking ===
    "PROP_CIGARETTE_01", "PROP_CIGARETTE_02",
    "PROP_VINTAGE_LIGHTER_01", "PROP_ZIPPO_LIGHTER_01",
    "PROP_ASHTRAY_01",
    # === Bar & Kitchen ===
    "PROP_CORKSCREW_01", "PROP_BOTTLE_OPENER_01",
    "PROP_SPOON_01", "PROP_FORK_01",
    "PROP_COFFEE_STIRRER_01",
    "PROP_BOTTLE_CAP_01", "PROP_SMALL_BOTTLE_01", "PROP_WHISKEY_BOTTLE_01",
    "PROP_PLASTIC_STRAW_01",
    "PROP_SHOT_GLASS_01",
    # === Medals & Tokens ===
    "PROP_VINTAGE_MEDAL_01", "PROP_VINTAGE_BADGE_01",
    "PROP_CHAIN_FRAGMENT_01",
    # === Misc Objects ===
    "PROP_SMALL_JEWELRY_BAG_01",
    "PROP_SUGAR_PACKET_01",
    "PROP_CANDY_WRAPPER_01",
    "PROP_CLOTH_NAPKIN_01",
    "PROP_MAGNIFYING_GLASS_01",
    "PROP_POCKET_KNIFE_01",
    "PROP_COMPASS_01",
    "PROP_DICE_01",
    "PROP_PHOTOGRAPH_CORNER_01",
    # === Stickers & Labels (vibrant, distinct shapes) ===
    "PROP_PRICE_STICKER_01",
    "PROP_BARCODE_STICKER_01",
    "PROP_REWIND_STICKER_01",
    "PROP_RECORD_SLEEVE_CORNER_01",
    "PROP_VINYL_LABEL_01",
    # === Hardware Bits (nuts, bolts, washers) ===
    "PROP_SMALL_BOLT_01", "PROP_WASHER_01",
    "PROP_SCREW_01", "PROP_NAIL_01",
    # === Notions & Findings ===
    "PROP_FISHING_HOOK_01", "PROP_SAFETY_PIN_01",
    "PROP_THIMBLE_01", "PROP_PAPERCLIP_01",
    # === Sharp Things ===
    "PROP_RAZOR_BLADE_01", "PROP_MATCHSTICK_01",
]

# ── LEGENDARY PROPS (target: 10) ──
LEGENDARY_PROPS_TO_GENERATE = [
    "PROP_CROWN_GOLD_01", "PROP_CROWN_CHROME_01",
    "PROP_CRYSTAL_SHARD_01", "PROP_HOLO_SEAL_01",
    "PROP_DIAMOND_CLIP_01", "PROP_CHAIN_LUXE_01",
    "PROP_PEARL_TAG_01", "PROP_LASER_STICKER_01",
    "PROP_GEM_BADGE_01", "PROP_ACRYLIC_TOKEN_01",
]

# ── MATERIAL / PATTERN (target: 14) ──
MATERIALS_TO_GENERATE = [
    "MAT_TRANSPARENT_RECEIPT_01", "MAT_FROSTED_RECEIPT_01",
    "MAT_HOLOGRAPHIC_RECEIPT_01", "MAT_BLACK_GOLD_RECEIPT_01",
    "MAT_SILVER_FOIL_RECEIPT_01", "MAT_GLOW_INK_01",
    "MAT_CHROME_EDGE_01", "MAT_GLASS_ARCHIVE_01",
    "PAT_LEOPARD_01", "PAT_SNAKESKIN_01",
    "PAT_HOLO_GRID_01", "PAT_GOLD_FLECK_01",
    "PAT_IRIDESCENT_WAVE_01", "PAT_SECURITY_PRINT_01",
]

# ── DAMAGE (target: 20) ──
DAMAGES_TO_GENERATE = [
    ("DMG_COFFEE_RING_01", "damage_coffee_ring_01.png"),
    ("DMG_COFFEE_RING_02", "damage_coffee_ring_02.png"),
    ("DMG_COFFEE_RING_03", "damage_coffee_ring_03.png"),
    ("DMG_FOLD_01", "damage_fold_01.png"),
    ("DMG_FOLD_02", "damage_fold_02.png"),
    ("DMG_FOLD_03", "damage_fold_03.png"),
    ("DMG_EDGE_WEAR_01", "damage_edge_wear_01.png"),
    ("DMG_EDGE_WEAR_02", "damage_edge_wear_02.png"),
    ("DMG_TAPE_01", "damage_tape_01.png"),
    ("DMG_TAPE_02", "damage_tape_02.png"),
    ("DMG_WATER_STAIN_01", "damage_water_stain_01.png"),
    ("DMG_WATER_STAIN_02", "damage_water_stain_02.png"),
    ("DMG_WATER_STAIN_03", "damage_water_stain_03.png"),
    ("DMG_DUST_SPECKS_01", "damage_dust_specks_01.png"),
    ("DMG_DUST_SPECKS_02", "damage_dust_specks_02.png"),
    ("DMG_SCAN_NOISE_01", "damage_scan_noise_01.png"),
    ("DMG_SCAN_NOISE_02", "damage_scan_noise_02.png"),
    ("DMG_THERMAL_FADE_01", "damage_thermal_fade_01.png"),
    ("DMG_CORNER_CURL_01", "damage_corner_curl_01.png"),
    ("DMG_SMALL_TEAR_01", "damage_small_tear_01.png"),
]

# ── OVERLAYS (target: 17 = 9 standard + 8 legendary) ──
OVERLAYS_TO_GENERATE = [
    ("OVERLAY_FILM_GRAIN_01", "overlay_film_grain_01.png"),
    ("OVERLAY_FILM_GRAIN_02", "overlay_film_grain_02.png"),
    ("OVERLAY_SCAN_NOISE_01", "overlay_scan_noise_01.png"),
    ("OVERLAY_SCAN_NOISE_02", "overlay_scan_noise_02.png"),
    ("OVERLAY_DUST_01", "overlay_dust_01.png"),
    ("OVERLAY_DUST_02", "overlay_dust_02.png"),
    ("OVERLAY_ARCHIVE_YELLOWING_01", "overlay_archive_yellowing_01.png"),
    ("OVERLAY_SOFT_VIGNETTE_01", "overlay_soft_vignette_01.png"),
    ("OVERLAY_FADED_INK_01", "overlay_faded_ink_01.png"),
]

# ── LEGENDARY OVERLAYS (target: 8) ──
LEGENDARY_OVERLAYS_TO_GENERATE = [
    ("OVERLAY_HOLO_PRISM_01", "overlay_holo_prism_01.png"),
    ("OVERLAY_GOLD_DUST_01", "overlay_gold_dust_01.png"),
    ("OVERLAY_IRIDESCENT_GLOW_01", "overlay_iridescent_glow_01.png"),
    ("OVERLAY_LUXE_VIGNETTE_01", "overlay_luxe_vignette_01.png"),
    ("OVERLAY_CRYSTAL_SPARK_01", "overlay_crystal_spark_01.png"),
    ("OVERLAY_NEON_ARCHIVE_01", "overlay_neon_archive_01.png"),
    ("OVERLAY_RAINBOW_FOIL_01", "overlay_rainbow_foil_01.png"),
    ("OVERLAY_ULTRA_RARE_SHIMMER_01", "overlay_ultra_rare_shimmer_01.png"),
]


def main():
    print("=" * 60)
    print("  NO REFUNDS ARCHIVE - Trait Asset Generator v3.0")
    print("=" * 60)

    total = 0
    counts = {}

    # ── Generate Stamps ──
    print("\n🔴 Generating STAMPS...")
    stamp_dir = os.path.join(ASSETS_DIR, "stamps")
    os.makedirs(stamp_dir, exist_ok=True)
    cat_count = 0
    for item in STAMPS_TO_GENERATE:
        stamp_id, filename = item[0], item[1]
        style = item[2]
        color = item[3] if len(item) > 3 else (200, 30, 30, 200)
        if not os.path.exists(os.path.join(stamp_dir, filename)):
            generate_stamp(stamp_id, filename, color=color, style=style)
            total += 1
            cat_count += 1
        else:
            print(f"  · stamp exists: {filename}")
    counts["stamps"] = cat_count

    # ── Generate Handwritten ──
    print("\n✍️ Generating HANDWRITTEN notes...")
    hw_dir = os.path.join(ASSETS_DIR, "handwritten")
    os.makedirs(hw_dir, exist_ok=True)
    cat_count = 0
    for note_id, filename, placement in HANDWRITTEN_TO_GENERATE:
        if not os.path.exists(os.path.join(hw_dir, filename)):
            generate_handwritten(note_id, filename, placement=placement)
            total += 1
            cat_count += 1
        else:
            print(f"  · handwritten exists: {filename}")
    counts["handwritten"] = cat_count

    # ── Generate Standard Props ──
    print("\n📦 Generating STANDARD PROPS...")
    prop_dir = os.path.join(ASSETS_DIR, "props")
    os.makedirs(prop_dir, exist_ok=True)
    cat_count = 0
    for prop_id in PROPS_TO_GENERATE:
        filename = prop_id.lower() + ".png"
        if not os.path.exists(os.path.join(prop_dir, filename)):
            generate_prop(prop_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · prop exists: {filename}")
    counts["props"] = cat_count

    # ── Generate Legendary Accent Stickers ──
    print("\n🏷️ Generating LEGENDARY ACCENT STICKERS (vintage sticker style)...")
    cat_count = 0
    for prop_id in LEGENDARY_PROPS_TO_GENERATE:
        filename = prop_id.lower() + ".png"
        out_dir = os.path.join(ASSETS_DIR, "legendary_accent")
        os.makedirs(out_dir, exist_ok=True)
        if not os.path.exists(os.path.join(out_dir, filename)):
            generate_legendary_accent_sticker(prop_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · legendary sticker exists: {filename}")
    counts["legendary_props"] = cat_count

    # ── Generate Material / Pattern ──
    print("\n🎨 Generating MATERIAL / PATTERN layers...")
    mat_dir = os.path.join(ASSETS_DIR, "material_pattern")
    os.makedirs(mat_dir, exist_ok=True)
    cat_count = 0
    for mat_id in MATERIALS_TO_GENERATE:
        filename = mat_id.lower() + ".png"
        if not os.path.exists(os.path.join(mat_dir, filename)):
            generate_material_pattern(mat_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · material/pattern exists: {filename}")
    counts["material_pattern"] = cat_count

    # ── Generate Damages ──
    print("\n🩹 Generating DAMAGE textures...")
    dmg_dir = os.path.join(ASSETS_DIR, "damage")
    os.makedirs(dmg_dir, exist_ok=True)
    cat_count = 0
    for dmg_id, filename in DAMAGES_TO_GENERATE:
        if not os.path.exists(os.path.join(dmg_dir, filename)):
            generate_damage(dmg_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · damage exists: {filename}")
    counts["damage"] = cat_count

    # ── Generate Standard Overlays ──
    print("\n🎞️ Generating STANDARD OVERLAYS...")
    ovl_dir = os.path.join(ASSETS_DIR, "overlays")
    os.makedirs(ovl_dir, exist_ok=True)
    cat_count = 0
    for ovl_id, filename in OVERLAYS_TO_GENERATE:
        if not os.path.exists(os.path.join(ovl_dir, filename)):
            generate_overlay(ovl_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · overlay exists: {filename}")
    counts["overlays"] = cat_count

    # ── Generate Legendary Overlays ──
    print("\n✨ Generating LEGENDARY OVERLAYS...")
    cat_count = 0
    for ovl_id, filename in LEGENDARY_OVERLAYS_TO_GENERATE:
        out_dir = os.path.join(ASSETS_DIR, "legendary_accent")
        os.makedirs(out_dir, exist_ok=True)
        if not os.path.exists(os.path.join(out_dir, filename)):
            generate_legendary_overlay(ovl_id, filename)
            total += 1
            cat_count += 1
        else:
            print(f"  · legendary overlay exists: {filename}")
    counts["legendary_overlays"] = cat_count

    print(f"\n{'=' * 60}")
    print(f"  ✓ Generated {total} new asset file(s)")
    print(f"{'=' * 60}")

    # ── Print final counts ──
    for cat in ["stamps", "handwritten", "props", "damage", "overlays", "material_pattern", "legendary_accent"]:
        d = os.path.join(ASSETS_DIR, cat)
        if os.path.exists(d):
            cnt = len([f for f in os.listdir(d) if f.endswith(".png")])
            print(f"  {cat}: {cnt} files")
        else:
            print(f"  {cat}: (directory not found)")

    print(f"\n  Summary of NEW files generated:")
    for k, v in counts.items():
        print(f"    {k}: {v} new")


if __name__ == "__main__":
    main()
