#!/usr/bin/env python3
"""
generate_trait_assets.py
NO REFUNDS ARCHIVE - Trait Asset Generator

Generates placeholder PNG assets for all trait categories
based on series matching rules. All outputs are 1024x1024 RGBA PNGs
with semi-transparent design elements.

Categories:
  - stamps: Red ink stamp effects (circle/rectangle)
  - handwritten: Handwritten-style text notes
  - props: Small object silhouettes
  - damage: Paper damage textures (coffee rings, folds, tears, etc.)
  - overlays: Full-screen filter effects (grain, noise, vignette, etc.)
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
    """Try to find available fonts on the system."""
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
    """Get a font with fallback."""
    fonts = get_font_paths()
    if fonts:
        return ImageFont.truetype(fonts[0], size)
    return ImageFont.load_default()


def get_bold_font(size=48):
    """Get a bold font."""
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


# ══════════════════════════════════════════════════════════════
# STAMP GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_stamp(text, filename, color=(200, 30, 30, 200), style="circle"):
    """Generate a red stamp effect."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = CANVAS // 2, CANVAS // 2
    stamp_size = random.randint(280, 380)

    # Rotation
    angle = random.uniform(-15, 15)
    stamp_layer = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    stamp_draw = ImageDraw.Draw(stamp_layer)

    r, g, b, a = color
    outline_color = (r, g, b, min(255, a + 30))
    fill_color = (r, g, b, min(255, a - 40))

    if style == "circle":
        # Double circle stamp
        stamp_draw.ellipse(
            [cx - stamp_size, cy - stamp_size, cx + stamp_size, cy + stamp_size],
            outline=outline_color, width=random.randint(5, 9)
        )
        inner = stamp_size - 25
        stamp_draw.ellipse(
            [cx - inner, cy - inner, cx + inner, cy + inner],
            outline=outline_color, width=random.randint(3, 6)
        )
        # Text inside
        words = text.replace("STAMP_", "").replace("_", " ").upper()
        font_size = max(24, min(72, int(stamp_size * 0.18)))
        font = get_bold_font(font_size)
        # Try to center text
        bbox = stamp_draw.textbbox((0, 0), words, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if tw > inner * 1.8:
            # Try two lines
            parts = words.split()
            mid = len(parts) // 2
            line1 = " ".join(parts[:mid])
            line2 = " ".join(parts[mid:])
            b1 = stamp_draw.textbbox((0, 0), line1, font=font)
            b2 = stamp_draw.textbbox((0, 0), line2, font=font)
            stamp_draw.text((cx - (b1[2] - b1[0]) // 2, cy - font_size - 5), line1, fill=outline_color, font=font)
            stamp_draw.text((cx - (b2[2] - b2[0]) // 2, cy + 5), line2, fill=outline_color, font=font)
        else:
            stamp_draw.text((cx - tw // 2, cy - th // 2), words, fill=outline_color, font=font)
    else:
        # Rectangle stamp
        w = int(stamp_size * 1.4)
        h = stamp_size
        stamp_draw.rectangle(
            [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
            outline=outline_color, width=random.randint(4, 7)
        )
        words = text.replace("STAMP_", "").replace("_", " ").upper()
        font_size = max(20, min(60, int(stamp_size * 0.16)))
        font = get_bold_font(font_size)
        bbox = stamp_draw.textbbox((0, 0), words, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        stamp_draw.text((cx - tw // 2, cy - th // 2), words, fill=outline_color, font=font)

    # Apply rotation
    stamp_layer = stamp_layer.rotate(angle, expand=False, resample=Image.BICUBIC, center=(cx, cy))
    img = Image.alpha_composite(img, stamp_layer)

    # Add slight noise/grit to stamp
    pixels = img.load()
    for _ in range(random.randint(200, 600)):
        x = random.randint(max(0, cx - stamp_size), min(CANVAS - 1, cx + stamp_size))
        y = random.randint(max(0, cy - stamp_size), min(CANVAS - 1, cy + stamp_size))
        px = pixels[x, y]
        if px[3] > 30:
            noise = random.randint(-40, 20)
            pixels[x, y] = (
                max(0, min(255, px[0] + noise)),
                max(0, min(255, px[1] + noise)),
                max(0, min(255, px[2] + noise)),
                max(0, min(255, px[3] + noise)),
            )

    path = os.path.join(ASSETS_DIR, "stamps", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ stamp: {filename}")


# ══════════════════════════════════════════════════════════════
# HANDWRITTEN NOTE GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_handwritten(text_id, filename, placement="random"):
    """Generate a handwritten-style note."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    text = text_id.replace("NOTE_", "").replace("_", " ")
    ink_color = (random.randint(20, 60), random.randint(20, 60), random.randint(60, 140), random.randint(160, 220))

    font_size = random.randint(36, 64)
    font = get_font(font_size)

    # Position: random but within reasonable bounds
    margin = 100
    max_w = CANVAS - 2 * margin
    max_h = CANVAS - 2 * margin

    # Try to fit text
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

    line_height = font_size + random.randint(4, 12)
    total_h = len(lines) * line_height

    if placement == "top_left":
        x0, y0 = margin, margin + random.randint(0, 50)
    elif placement == "top_right":
        x0, y0 = CANVAS - margin - max_w, margin + random.randint(0, 50)
    elif placement == "bottom_left":
        x0, y0 = margin, CANVAS - margin - total_h - random.randint(0, 50)
    elif placement == "bottom_right":
        x0, y0 = CANVAS - margin - max_w, CANVAS - margin - total_h - random.randint(0, 50)
    elif placement == "center":
        x0, y0 = margin, (CANVAS - total_h) // 2
    else:
        x0 = margin + random.randint(0, CANVAS - margin - max_w)
        y0 = margin + random.randint(0, CANVAS - margin - total_h)

    # Draw lines with slight jitter for handwritten effect
    for i, line in enumerate(lines):
        lx = x0
        ly = y0 + i * line_height
        for ch in line:
            bbox = draw.textbbox((0, 0), ch, font=font)
            cw = bbox[2] - bbox[0]
            # Jitter each character
            jx = lx + random.randint(-2, 2)
            jy = ly + random.randint(-3, 3)
            draw.text((jx, jy), ch, fill=ink_color, font=font)
            lx += cw + random.randint(-1, 2)

    # Add slight rotation to the whole note
    angle = random.uniform(-5, 5)
    img = img.rotate(angle, expand=False, resample=Image.BICUBIC, center=(CANVAS // 2, CANVAS // 2))

    path = os.path.join(ASSETS_DIR, "handwritten", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ handwritten: {filename}")


# ══════════════════════════════════════════════════════════════
# PROP GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_prop(prop_id, filename):
    """Generate a small object silhouette on transparent background."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Random position (off-center, simulating a placed object)
    cx = random.randint(200, CANVAS - 200)
    cy = random.randint(150, CANVAS - 150)
    prop_size = random.randint(60, 180)

    # Color based on prop type name
    name = prop_id.lower()
    if "coin" in name:
        base_color = (180, 150, 80, random.randint(180, 230))
    elif "receipt" in name or "slip" in name or "ticket" in name or "stub" in name or "tag" in name or "label" in name or "card" in name:
        base_color = (220, 215, 200, random.randint(180, 230))
    elif "napkin" in name or "spoon" in name or "stirrer" in name or "straw" in name or "bottle" in name:
        base_color = (200, 200, 210, random.randint(180, 220))
    elif "cassette" in name or "tape" in name or "vhs" in name or "vinyl" in name:
        base_color = (40, 40, 50, random.randint(200, 240))
    elif "key" in name or "chain" in name or "ring" in name or "watch" in name:
        base_color = (120, 110, 90, random.randint(200, 240))
    elif "candy" in name or "wrapper" in name or "packet" in name or "sugar" in name:
        base_color = (200, 80, 60, random.randint(180, 220))
    elif "box" in name or "case" in name or "bag" in name:
        base_color = (100, 80, 60, random.randint(190, 230))
    elif "glass" in name or "plastic" in name:
        base_color = (180, 200, 220, random.randint(120, 180))
    else:
        base_color = (150, 140, 130, random.randint(180, 230))

    # Draw shape
    shape_type = random.choice(["rect", "round_rect", "ellipse", "polygon"])
    if shape_type == "rect":
        draw.rectangle(
            [cx - prop_size // 2, cy - prop_size // 3, cx + prop_size // 2, cy + prop_size // 3],
            fill=base_color, outline=(0, 0, 0, 80), width=1
        )
    elif shape_type == "round_rect":
        r = prop_size // 6
        draw.rounded_rectangle(
            [cx - prop_size // 2, cy - prop_size // 3, cx + prop_size // 2, cy + prop_size // 3],
            radius=r, fill=base_color, outline=(0, 0, 0, 80), width=1
        )
    elif shape_type == "ellipse":
        draw.ellipse(
            [cx - prop_size // 2, cy - prop_size // 2, cx + prop_size // 2, cy + prop_size // 2],
            fill=base_color
        )
    else:
        pts = []
        n_pts = random.randint(5, 8)
        for i in range(n_pts):
            angle = 2 * math.pi * i / n_pts + random.uniform(-0.3, 0.3)
            r = prop_size // 2 + random.randint(-20, 20)
            pts.append((cx + int(r * math.cos(angle)), cy + int(r * math.sin(angle))))
        draw.polygon(pts, fill=base_color)

    # Add label text
    short_name = prop_id.replace("PROP_", "").replace("_", " ")
    font_size = max(10, min(20, prop_size // 5))
    font = get_font(font_size)
    bbox = draw.textbbox((0, 0), short_name[:12], font=font)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, cy - 8), short_name[:12], fill=(0, 0, 0, 100), font=font)

    # Rotation
    angle = random.uniform(-10, 10)
    img = img.rotate(angle, expand=False, resample=Image.BICUBIC, center=(cx, cy))

    path = os.path.join(ASSETS_DIR, "props", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ prop: {filename}")


# ══════════════════════════════════════════════════════════════
# DAMAGE GENERATOR
# ══════════════════════════════════════════════════════════════

def generate_damage(dmg_id, filename):
    """Generate a paper damage texture."""
    img = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    name = dmg_id.lower()

    if "coffee_ring" in name:
        # Coffee ring stain
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
        # Fold line
        if "02" in name:
            x = random.randint(CANVAS // 3, 2 * CANVAS // 3)
            draw.line([(x, 0), (x + random.randint(-10, 10), CANVAS)],
                      fill=(80, 75, 70, random.randint(30, 60)), width=random.randint(1, 3))
        else:
            y = random.randint(CANVAS // 3, 2 * CANVAS // 3)
            draw.line([(0, y + random.randint(-10, 10)), (CANVAS, y)],
                      fill=(80, 75, 70, random.randint(30, 60)), width=random.randint(1, 3))

    elif "edge_wear" in name:
        # Worn edges
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
        # Tape piece
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
        # Water stain blotch
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
        # Fading effect (horizontal bands)
        for y in range(0, CANVAS, random.randint(3, 8)):
            alpha = random.randint(5, 25)
            draw.line([(0, y), (CANVAS, y + random.randint(0, 2))],
                      fill=(200, 195, 180, alpha), width=1)

    elif "dust_specks" in name:
        # Random dust specks
        for _ in range(random.randint(100, 300)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(1, 3)
            alpha = random.randint(10, 40)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(80, 75, 70, alpha))

    elif "corner_curl" in name:
        # Curled corner
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
        # Horizontal scan lines
        for y in range(0, CANVAS, random.randint(4, 10)):
            alpha = random.randint(5, 20)
            draw.line([(0, y), (CANVAS, y)], fill=(0, 0, 0, alpha), width=1)

    elif "small_tear" in name:
        # Small tear at edge
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
# OVERLAY GENERATOR
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
        # Blue-ish rain glow overlay
        for _ in range(random.randint(200, 500)):
            x = random.randint(0, CANVAS - 1)
            y = random.randint(0, CANVAS - 1)
            r = random.randint(2, 10)
            alpha = random.randint(2, 10)
            draw.ellipse([x - r, y - r, x + r, y + r],
                         fill=(30, 50, 80, alpha))

    elif "glass_glare" in name:
        # Diagonal glare
        for y in range(0, CANVAS):
            alpha = random.randint(1, 8)
            x0 = y
            for x in range(max(0, x0 - 30), min(CANVAS, x0 + 30)):
                pixels[x, y] = (255, 255, 255, alpha)

    elif "archive_yellowing" in name:
        # Yellow/brown aging
        for x in range(0, CANVAS, 2):
            for y in range(0, CANVAS, 2):
                alpha = random.randint(3, 12)
                pixels[x, y] = (200, 180, 120, alpha)

    elif "soft_vignette" in name:
        # Dark vignette
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
        # Ink fade effect
        for y in range(0, CANVAS, random.randint(3, 8)):
            alpha = random.randint(2, 10)
            for x in range(0, CANVAS, random.randint(2, 5)):
                pixels[x, y] = (230, 225, 210, alpha)

    path = os.path.join(ASSETS_DIR, "overlays", filename)
    img.save(path, "PNG", optimize=True)
    print(f"  ✓ overlay: {filename}")


# ══════════════════════════════════════════════════════════════
# MAIN: Generate all needed assets
# ══════════════════════════════════════════════════════════════

# Define all assets needed based on series matching rules
# Format: (trait_id, filename, category)

STAMPS_TO_GENERATE = [
    ("STAMP_LAST_ORDER", "stamp_last_order_red.png", "circle"),
    ("STAMP_OVERDUE", "stamp_overdue_red.png", "rect"),
    ("STAMP_NO_VACANCY", "stamp_no_vacancy_red.png", "circle"),
    ("STAMP_FINAL_SALE", "stamp_final_sale_red.png", "rect"),
    ("STAMP_PAWN_HOLD", "stamp_pawn_hold_red.png", "circle"),
    ("STAMP_UNCLAIMED", "stamp_unclaimed_red.png", "rect"),
    ("STAMP_DO_NOT_OPEN", "stamp_do_not_open_red.png", "circle"),
    ("STAMP_STORE_CREDIT", "stamp_store_credit_red.png", "rect"),
    ("STAMP_PAID_CASH", "stamp_paid_cash_red.png", "circle"),
    ("STAMP_DUE_FRIDAY", "stamp_due_friday_red.png", "rect"),
    ("STAMP_RETURNED_EMPTY", "stamp_returned_empty_red.png", "circle"),
]

HANDWRITTEN_TO_GENERATE = [
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
]

PROPS_TO_GENERATE = [
    "PROP_SPOON_01", "PROP_SUGAR_PACKET_01", "PROP_COFFEE_STIRRER_01",
    "PROP_MATCHBOOK_01", "PROP_DINER_MENU_SCRAP_01", "PROP_TABLE_TICKET_01",
    "PROP_REWIND_STICKER_01", "PROP_LATE_FEE_SLIP_01", "PROP_MEMBERSHIP_CARD_01",
    "PROP_VIDEO_CASE_CORNER_01", "PROP_RETURN_SLOT_TAG_01", "PROP_TAPE_SPINE_LABEL_01",
    "PROP_STORE_TAG_01", "PROP_PLASTIC_TAB_01",
    "PROP_ROOM_TAG_01", "PROP_GAS_STATION_TOKEN_01", "PROP_PARKING_STUB_01",
    "PROP_MATCHBOOK_MOTEL_01", "PROP_POSTCARD_CORNER_01", "PROP_ROAD_EXIT_NOTE_01",
    "PROP_KEYCHAIN_01", "PROP_PAYPHONE_CARD_01",
    "PROP_VINYL_LABEL_01", "PROP_PRICE_STICKER_01", "PROP_USED_TAPE_TAG_01",
    "PROP_TRACKLIST_SCRAP_01", "PROP_RECORD_SLEEVE_CORNER_01", "PROP_STORE_CREDIT_SLIP_01",
    "PROP_B_SIDE_NOTE_01", "PROP_PLASTIC_SLEEVE_01",
    "PROP_PRICE_TAG_01", "PROP_CANDY_WRAPPER_01", "PROP_BOTTLE_CAP_01",
    "PROP_LOTTERY_STUB_01", "PROP_COUPON_SCRAP_01", "PROP_PLASTIC_STRAW_WRAPPER_01",
    "PROP_AISLE_TAG_01", "PROP_REGISTER_TAPE_SCRAP_01",
    "PROP_CLAIM_TICKET_01", "PROP_BRASS_TAG_01", "PROP_OLD_KEY_01",
    "PROP_CHAIN_FRAGMENT_01", "PROP_SMALL_JEWELRY_BAG_01", "PROP_CASE_LABEL_01",
    "PROP_PAWN_STUB_01", "PROP_GLASS_COUNTER_TAG_01",
]

DAMAGES_TO_GENERATE = [
    ("DMG_COFFEE_RING_02", "damage_coffee_ring_02.png"),
    ("DMG_FOLD_02", "damage_fold_02.png"),
    ("DMG_EDGE_WEAR_02", "damage_edge_wear_02.png"),
    ("DMG_THERMAL_FADE_01", "damage_thermal_fade_01.png"),
    ("DMG_DUST_SPECKS_01", "damage_dust_specks_01.png"),
    ("DMG_CORNER_CURL_01", "damage_corner_curl_01.png"),
    ("DMG_SCAN_NOISE_01", "damage_scan_noise_01.png"),
    ("DMG_SCAN_NOISE_02", "damage_scan_noise_02.png"),
    ("DMG_WATER_STAIN_02", "damage_water_stain_02.png"),
    ("DMG_SMALL_TEAR_01", "damage_small_tear_01.png"),
    ("DMG_DUST_SPECKS_02", "damage_dust_specks_02.png"),
]

OVERLAYS_TO_GENERATE = [
    ("OVERLAY_FILM_GRAIN_02", "overlay_film_grain_02.png"),
    ("OVERLAY_SCAN_NOISE_02", "overlay_scan_noise_02.png"),
    ("OVERLAY_DUST_02", "overlay_dust_02.png"),
    ("OVERLAY_ARCHIVE_YELLOWING_01", "overlay_archive_yellowing_01.png"),
    ("OVERLAY_SOFT_VIGNETTE_01", "overlay_soft_vignette_01.png"),
    ("OVERLAY_FADED_INK_01", "overlay_faded_ink_01.png"),
    ("OVERLAY_CRT_GRAIN_02", "overlay_crt_grain_02.png"),
    ("OVERLAY_RAIN_GLOW_02", "overlay_rain_glow_02.png"),
    ("OVERLAY_GLASS_GLARE_02", "overlay_glass_glare_02.png"),
]


def main():
    print("=" * 60)
    print("  NO REFUNDS ARCHIVE - Trait Asset Generator")
    print("=" * 60)

    total = 0

    # ── Generate Stamps ──
    print("\n🔴 Generating STAMPS...")
    stamp_dir = os.path.join(ASSETS_DIR, "stamps")
    os.makedirs(stamp_dir, exist_ok=True)
    for stamp_id, filename, style in STAMPS_TO_GENERATE:
        if not os.path.exists(os.path.join(stamp_dir, filename)):
            generate_stamp(stamp_id, filename, style=style)
            total += 1
        else:
            print(f"  · stamp exists: {filename}")

    # ── Generate Handwritten ──
    print("\n✍️ Generating HANDWRITTEN notes...")
    hw_dir = os.path.join(ASSETS_DIR, "handwritten")
    os.makedirs(hw_dir, exist_ok=True)
    for note_id, filename, placement in HANDWRITTEN_TO_GENERATE:
        if not os.path.exists(os.path.join(hw_dir, filename)):
            generate_handwritten(note_id, filename, placement=placement)
            total += 1
        else:
            print(f"  · handwritten exists: {filename}")

    # ── Generate Props ──
    print("\n📦 Generating PROPS...")
    prop_dir = os.path.join(ASSETS_DIR, "props")
    os.makedirs(prop_dir, exist_ok=True)
    for prop_id in PROPS_TO_GENERATE:
        filename = prop_id.lower().replace("_", "_", 1).replace("prop_", "prop_", 1) + ".png"
        # Fix: convert PROP_SPOON_01 -> prop_spoon_01.png
        filename = prop_id.lower() + ".png"
        if not os.path.exists(os.path.join(prop_dir, filename)):
            generate_prop(prop_id, filename)
            total += 1
        else:
            print(f"  · prop exists: {filename}")

    # ── Generate Damages ──
    print("\n🩹 Generating DAMAGE textures...")
    dmg_dir = os.path.join(ASSETS_DIR, "damage")
    os.makedirs(dmg_dir, exist_ok=True)
    for dmg_id, filename in DAMAGES_TO_GENERATE:
        if not os.path.exists(os.path.join(dmg_dir, filename)):
            generate_damage(dmg_id, filename)
            total += 1
        else:
            print(f"  · damage exists: {filename}")

    # ── Generate Overlays ──
    print("\n🎞️ Generating OVERLAYS...")
    ovl_dir = os.path.join(ASSETS_DIR, "overlays")
    os.makedirs(ovl_dir, exist_ok=True)
    for ovl_id, filename in OVERLAYS_TO_GENERATE:
        if not os.path.exists(os.path.join(ovl_dir, filename)):
            generate_overlay(ovl_id, filename)
            total += 1
        else:
            print(f"  · overlay exists: {filename}")

    print(f"\n{'=' * 60}")
    print(f"  ✓ Generated {total} new asset file(s)")
    print(f"{'=' * 60}")

    # ── Print final counts ──
    for cat in ["stamps", "handwritten", "props", "damage", "overlays"]:
        d = os.path.join(ASSETS_DIR, cat)
        count = len([f for f in os.listdir(d) if f.endswith(".png")])
        print(f"  {cat}: {count} files")


if __name__ == "__main__":
    main()
