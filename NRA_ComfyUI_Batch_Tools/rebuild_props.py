#!/usr/bin/env python3
"""
rebuild_props.py
v4 — Realistic vintage cast-metal / aged object props.

Design target (user reference):
- Antique brass / bronze with patina and oxidation spots
- 3D casting look: soft highlights, deep shadows, no black outlines
- Worn, scratched, dusty surfaces
- Each of the 71 props visually distinct
- Small, isolated on transparent 1024 canvas, no composition yet
"""

import os
import sys
import io
import random
import math
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
CANVAS = 1024

random.seed(42)

# ══════════════════════════════════════════════════════════════
# PALETTE — muted antique metals, paper, glass, wood
# ══════════════════════════════════════════════════════════════
BRASS_LIGHT = (185, 155, 85)
BRASS_MID   = (145, 115, 60)
BRASS_DARK  = (95,  72,  35)
BRASS_SHADOW = (55, 42, 22)

COPPER_LIGHT = (175, 120, 75)
COPPER_MID   = (130, 80,  50)
COPPER_DARK  = (80,  45,  30)

STEEL_LIGHT = (170, 170, 175)
STEEL_MID   = (120, 120, 125)
STEEL_DARK  = (70,  70,  75)

PEWTER_LIGHT = (160, 165, 165)
PEWTER_MID   = (115, 120, 120)
PEWTER_DARK  = (65,  70,  70)

GOLD_LIGHT = (195, 160, 80)
GOLD_MID   = (150, 115, 55)
GOLD_DARK  = (95,  70,  30)

SILVER_LIGHT = (190, 190, 195)
SILVER_MID   = (140, 140, 145)
SILVER_DARK  = (85,  85,  90)

RUST_LIGHT = (165, 95,  45)
RUST_MID   = (125, 65,  30)
RUST_DARK  = (75,  35,  18)

PAPER_LIGHT = (240, 230, 210)
PAPER_MID   = (225, 210, 175)
PAPER_DARK  = (190, 175, 140)
INK_BLACK   = (55, 50, 45)
INK_RED     = (130, 45, 38)
INK_BLUE    = (55, 60, 100)

WOOD_LIGHT = (170, 135, 90)
WOOD_MID   = (130, 95,  60)
WOOD_DARK  = (85,  60,  35)

GLASS_GREEN = (125, 150, 120)
GLASS_BROWN = (145, 120, 80)
GLASS_CLEAR = (185, 190, 185)

PLASTIC_BAKELITE = (115, 75, 45)
PLASTIC_CREAM   = (215, 200, 170)
PLASTIC_BLACK   = (45, 42, 38)

CLOTH_CREAM = (225, 215, 190)

# ══════════════════════════════════════════════════════════════
# LOW-LEVEL RENDER HELPERS
# ══════════════════════════════════════════════════════════════

def _make_canvas(size):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img), img.load()

def _radial_gradient(size, cx, cy, inner_color, outer_color, radius, shape_mask=None):
    """Draw a radial gradient inside a mask."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    ir, ig, ib = inner_color
    or_, og, ob = outer_color
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy) / radius
            d = min(1.0, d)
            r = int(ir + (or_ - ir) * d)
            g = int(ig + (og - ig) * d)
            b = int(ib + (ob - ib) * d)
            a = 255
            if shape_mask is not None and shape_mask.getpixel((x, y)) < 20:
                a = 0
            px[x, y] = (r, g, b, a)
    return img

def _linear_gradient(size, angle, color1, color2, shape_mask=None):
    """Draw a linear gradient at angle (radians)."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    c = math.cos(angle)
    s = math.sin(angle)
    for y in range(size):
        for x in range(size):
            t = ((x - size/2) * c + (y - size/2) * s) / (size * 0.6) + 0.5
            t = max(0, min(1, t))
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            a = 255
            if shape_mask is not None and shape_mask.getpixel((x, y)) < 20:
                a = 0
            px[x, y] = (r, g, b, a)
    return img

def _draw_shadow(img, ox, oy, blur=4, alpha=70):
    """Add a soft drop shadow beneath the object."""
    size = img.size[0]
    # Extract alpha
    alpha_ch = img.split()[-1]
    # Shadow offset
    shadow = Image.new("RGBA", (size + abs(ox) + blur*4, size + abs(oy) + blur*4), (0,0,0,0))
    spx = shadow.load()
    apx = alpha_ch.load()
    off_x, off_y = blur*2 + max(0, ox), blur*2 + max(0, oy)
    for y in range(size):
        for x in range(size):
            a = apx[x, y]
            if a > 20:
                spx[x + off_x, y + off_y] = (20, 15, 10, min(255, alpha * a // 255))
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur))
    # Composite shadow under original
    result = Image.new("RGBA", (size, size), (0,0,0,0))
    result.paste(shadow, (-blur*2 - max(0,ox), -blur*2 - max(0,oy)), shadow)
    result.paste(img, (0,0), img)
    return result

def _make_mask_from_shape(size, draw_shape_fn):
    """Create a mask image by calling draw_shape_fn on a mask canvas."""
    img = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(img)
    draw_shape_fn(draw, size)
    return img

def _apply_shape_mask(source, mask):
    """Crop source to mask alpha."""
    result = Image.new("RGBA", source.size, (0,0,0,0))
    result.paste(source, (0,0), mask.convert("RGBA"))
    return result

def _add_patina(img, base, density=0.12, strength=0.45):
    """Dark oxidation / patina spots."""
    px = img.load()
    w, h = img.size
    base_r, base_g, base_b = base
    for _ in range(int(w * h * density)):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        r, g, b, a = px[x, y]
        if a < 25: continue
        s = random.randint(1, 5)
        for dy in range(-s, s+1):
            for dx in range(-s, s+1):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h:
                    d = math.hypot(dx, dy)
                    if d <= s:
                        blend = max(0, 1 - d/s) * strength
                        nr, ng, nb, na = px[nx, ny]
                        if na > 25:
                            px[nx, ny] = (
                                int(nr*(1-blend) + base_r*blend),
                                int(ng*(1-blend) + base_g*blend),
                                int(nb*(1-blend) + base_b*blend),
                                na
                            )

def _add_rust_spots(img, density=0.08, strength=0.55):
    """Orange-brown rust speckles."""
    px = img.load()
    w, h = img.size
    for _ in range(int(w * h * density)):
        x = random.randint(0, w-1)
        y = random.randint(0, h-1)
        r, g, b, a = px[x, y]
        if a < 25: continue
        s = random.randint(1, 4)
        rr, rg, rb = random.choice([RUST_LIGHT, RUST_MID, RUST_DARK])
        for dy in range(-s, s+1):
            for dx in range(-s, s+1):
                nx, ny = x+dx, y+dy
                if 0 <= nx < w and 0 <= ny < h:
                    d = math.hypot(dx, dy)
                    if d <= s:
                        blend = max(0, 1 - d/s) * strength
                        nr, ng, nb, na = px[nx, ny]
                        if na > 25:
                            px[nx, ny] = (
                                int(nr*(1-blend) + rr*blend),
                                int(ng*(1-blend) + rg*blend),
                                int(nb*(1-blend) + rb*blend),
                                na
                            )

def _add_surface_noise(img, amount=15):
    """Fine grain noise."""
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a > 25:
                n = random.randint(-amount, amount)
                px[x, y] = (max(0,min(255,r+n)), max(0,min(255,g+n)), max(0,min(255,b+n)), a)

def _add_scratches(img, count=4):
    """Fine scratches."""
    px = img.load()
    w, h = img.size
    for _ in range(count):
        x1 = random.randint(0, w-1)
        y1 = random.randint(0, h-1)
        ang = random.uniform(0, math.pi*2)
        ln = random.randint(4, 18)
        for t in range(ln):
            x = int(x1 + t * math.cos(ang))
            y = int(y1 + t * math.sin(ang))
            if 0 <= x < w and 0 <= y < h:
                r, g, b, a = px[x, y]
                if a > 30:
                    hi = random.randint(15, 40)
                    px[x, y] = (min(255,r+hi), min(255,g+hi), min(255,b+hi), a)

def _add_edge_wear(img, amount=0.18):
    """Fade and roughen edges."""
    px = img.load()
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 10: continue
            dx = min(x, w-1-x) / (w*0.5)
            dy = min(y, h-1-y) / (h*0.5)
            ed = min(dx, dy)
            if ed < amount * 2:
                fade = ed / (amount * 2)
                if random.random() < 0.3:
                    fade *= random.uniform(0.3, 1.0)
                px[x, y] = (r, g, b, int(a * max(0.25, fade)))

def _add_top_highlight(img, amount=0.35):
    """Brighten top-left area for 3D lighting."""
    px = img.load(); w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 25: continue
            # Distance from top-left light source
            d = (x + y) / (w + h)
            boost = (1 - d) * amount * 80
            px[x, y] = (min(255, int(r + boost)), min(255, int(g + boost)), min(255, int(b + boost*0.8)), a)

def _add_bottom_shadow(img, amount=0.25):
    """Darken bottom-right area for depth."""
    px = img.load(); w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 25: continue
            d = ((w - x) + (h - y)) / (w + h)
            drop = (1 - d) * amount * 60
            px[x, y] = (max(0, int(r - drop)), max(0, int(g - drop)), max(0, int(b - drop*0.9)), a)

def _render_metal(img, base, patina_density=0.08, rust_density=0.06, scratch_count=3, shadow=True):
    """Standard antique metal finish with strong light/shadow contrast."""
    _add_surface_noise(img, 18)
    _add_top_highlight(img, 0.35)
    _add_bottom_shadow(img, 0.25)
    _add_patina(img, base, patina_density, 0.55)
    _add_rust_spots(img, rust_density, 0.55)
    _add_edge_wear(img, 0.14)
    _add_scratches(img, scratch_count)
    if shadow:
        img = _draw_shadow(img, random.randint(4, 7), random.randint(6, 10), blur=6, alpha=75)
    return img

def _draw_pearl(r, color=(245, 235, 220)):
    """Return a small RGBA pearl image with soft luster."""
    size = r * 2 + 1
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    cx, cy = r, r
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                t = d / r
                base_r = int(color[0] * (1 - t * 0.35))
                base_g = int(color[1] * (1 - t * 0.30))
                base_b = int(color[2] * (1 - t * 0.25))
                # top-left highlight
                hl = max(0, 1 - math.hypot(x - (cx - r * 0.3), y - (cy - r * 0.3)) / (r * 0.55))
                hl = max(0, hl - 0.25) * 90
                base_r = min(255, base_r + int(hl))
                base_g = min(255, base_g + int(hl))
                base_b = min(255, base_b + int(hl))
                # bottom-right shadow
                sh = max(0, 1 - math.hypot(x - (cx + r * 0.4), y - (cy + r * 0.4)) / (r * 0.7))
                sh = max(0, sh - 0.4) * 45
                base_r = max(0, base_r - int(sh))
                base_g = max(0, base_g - int(sh))
                base_b = max(0, base_b - int(sh))
                px[x, y] = (base_r, base_g, base_b, 255)
    return img


def _draw_gem(r, color=(190, 80, 90)):
    """Return a small RGBA faceted gem image."""
    size = r * 2 + 1
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    px = img.load()
    cx, cy = r, r
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                t = d / r
                base_r = int(color[0] * (1 - t * 0.35))
                base_g = int(color[1] * (1 - t * 0.25))
                base_b = int(color[2] * (1 - t * 0.15))
                a = math.atan2(y - cy, x - cx)
                facet = (math.sin(a * 8) + 1) / 2
                if facet > 0.65:
                    base_r = min(255, base_r + 50)
                    base_g = min(255, base_g + 50)
                    base_b = min(255, base_b + 50)
                hl = max(0, 1 - math.hypot(x - (cx - r * 0.35), y - (cy - r * 0.35)) / (r * 0.5))
                hl = max(0, hl - 0.2) * 110
                base_r = min(255, base_r + int(hl))
                base_g = min(255, base_g + int(hl))
                base_b = min(255, base_b + int(hl))
                px[x, y] = (base_r, base_g, base_b, 255)
    return img


# ══════════════════════════════════════════════════════════════
# 71 DISTINCT PROP DRAWERS
# Each returns a small RGBA image centered on its own canvas
# ══════════════════════════════════════════════════════════════

def _draw_prop_old_key_01(size):
    """Ornate skeleton key, round bow."""
    s = size
    cx, cy = s//2, s//2
    def shape(draw, s):
        # bow
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        draw.ellipse([cx-s//6, cy-s//6, cx+s//6, cy+s//6], fill=0)
        # shaft
        draw.rectangle([cx, cy-s//14, cx+s//3, cy+s//14], fill=255)
        # teeth
        draw.rectangle([cx+s//3-s//12, cy+s//14, cx+s//3, cy+s//5], fill=255)
        draw.rectangle([cx+s//3-s//6, cy+s//14, cx+s//3-s//6+s//15, cy+s//5], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, BRASS_DARK, BRASS_LIGHT, mask)
    return _render_metal(grad, BRASS_MID, 0.08, 0.05, 3)

def _draw_prop_old_key_02(size):
    """Long barrel key, diamond bow."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # diamond bow
        pts = [(cx, cy-s//3), (cx+s//8, cy-s//8), (cx, cy), (cx-s//8, cy-s//8)]
        draw.polygon(pts, fill=255)
        # shaft long
        draw.rounded_rectangle([cx-s//16, cy-s//14, cx+s//16, cy+s//2], radius=2, fill=255)
        # bit
        draw.rectangle([cx, cy+s//3, cx+s//8, cy+s//2], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, BRASS_SHADOW, BRASS_LIGHT, mask)
    return _render_metal(grad, BRASS_DARK, 0.10, 0.07, 4)

def _draw_prop_old_key_03(size):
    """Small warded key, heart-shaped bow."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # heart bow
        draw.ellipse([cx-s//5, cy-s//3, cx, cy-s//8], fill=255)
        draw.ellipse([cx, cy-s//3, cx+s//5, cy-s//8], fill=255)
        draw.polygon([(cx-s//5, cy-s//8), (cx+s//5, cy-s//8), (cx, cy)], fill=255)
        # shaft
        draw.rectangle([cx-s//18, cy, cx+s//18, cy+s//3], fill=255)
        # teeth
        draw.rectangle([cx, cy+s//3, cx+s//7, cy+s//3+s//12], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, COPPER_LIGHT, COPPER_DARK, s//2, mask)
    return _render_metal(grad, COPPER_MID, 0.09, 0.08, 3)

def _draw_prop_keychain_01(size):
    """Split ring keychain with fob."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # split ring
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=0)
        # fob tag
        draw.rounded_rectangle([cx-s//8, cy+s//6, cx+s//8, cy+s//2], radius=3, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_padlock_01(size):
    """Small brass padlock with shackle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # body
        draw.rounded_rectangle([cx-s//4, cy-s//6, cx+s//4, cy+s//4], radius=4, fill=255)
        # shackle
        draw.arc([cx-s//5, cy-s//3, cx+s//5, cy], 0, 180, fill=255, width=s//10)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/5, BRASS_LIGHT, BRASS_SHADOW, mask)
    return _render_metal(grad, BRASS_MID, 0.07, 0.05, 3)

def _draw_prop_vintage_coin_01(size):
    """Large copper coin with raised rim."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, COPPER_LIGHT, COPPER_DARK, s//3, mask)
    # rim line
    draw = ImageDraw.Draw(grad)
    draw.ellipse([cx-s//3+4, cy-s//3+4, cx+s//3-4, cy+s//3-4], outline=BRASS_DARK, width=2)
    return _render_metal(grad, COPPER_MID, 0.05, 0.04, 2)

def _draw_prop_vintage_coin_02(size):
    """Small silver coin, worn."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, SILVER_DARK, s//4, mask)
    draw = ImageDraw.Draw(grad)
    draw.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], outline=PEWTER_DARK, width=1)
    return _render_metal(grad, SILVER_MID, 0.07, 0.06, 4)

def _draw_prop_gas_station_token_01(size):
    """Hexagonal metal token."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        pts = []
        for i in range(6):
            a = math.pi/6 + i*math.pi/3
            pts.append((cx + s//3*math.cos(a), cy + s//3*math.sin(a)))
        draw.polygon(pts, fill=255)
        # hole
        draw.ellipse([cx-s//12, cy-s//12, cx+s//12, cy+s//12], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/6, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.08, 0.07, 3)

def _draw_prop_vintage_coin_03(size):
    """Square token with clipped corners."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        m = s//6
        draw.rounded_rectangle([cx-s//3+m, cy-s//3+m, cx+s//3-m, cy+s//3-m], radius=6, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PEWTER_LIGHT, PEWTER_DARK, mask)
    return _render_metal(grad, PEWTER_MID, 0.06, 0.08, 3)

def _draw_prop_vintage_ring_01(size):
    """Signet ring with flat top."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # band
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//4, cy-s//7, cx+s//4, cy+s//7], fill=0)
        # signet top
        draw.rounded_rectangle([cx-s//7, cy-s//2, cx+s//7, cy-s//4], radius=3, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 2)

def _draw_prop_vintage_ring_02(size):
    """Stone ring with gem setting."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # band
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//8], fill=0)
        # setting
        draw.ellipse([cx-s//8, cy-s//2, cx+s//8, cy-s//6], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, BRASS_LIGHT, BRASS_SHADOW, mask)
    img = _render_metal(grad, BRASS_MID, 0.07, 0.05, 3)
    # add dark gem
    px = img.load(); r = s//10
    for y in range(cy-s//2, cy-s//6):
        for x in range(cx-s//8, cx+s//8):
            if math.hypot(x-cx, y-(cy-s//3)) < r:
                px[x, y] = (40, 35, 30, 200)
    return img

def _draw_prop_vintage_button_01(size):
    """Four-hole brass button."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    draw = ImageDraw.Draw(grad)
    for dx in [-s//10, s//10]:
        for dy in [-s//10, s//10]:
            draw.ellipse([cx+dx-2, cy+dy-2, cx+dx+2, cy+dy+2], fill=BRASS_SHADOW)
    return _render_metal(grad, BRASS_MID, 0.05, 0.04, 2)

def _draw_prop_vintage_button_02(size):
    """Two-hole mother-of-pearl style button."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, PEWTER_DARK, s//3, mask)
    draw = ImageDraw.Draw(grad)
    draw.ellipse([cx-3, cy-s//8, cx+3, cy-s//8+4], fill=PEWTER_DARK)
    draw.ellipse([cx-3, cy+s//8-4, cx+3, cy+s//8], fill=PEWTER_DARK)
    return _render_metal(grad, SILVER_MID, 0.05, 0.03, 2)

def _draw_prop_brooch_01(size):
    """Filigree leaf brooch."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # leaf body
        draw.polygon([(cx, cy-s//2), (cx+s//4, cy), (cx, cy+s//2), (cx-s//4, cy)], fill=255)
        # stem line
        draw.line([(cx, cy+s//2), (cx, cy-s//3)], fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.05, 3)

def _draw_prop_vintage_glasses_01(size):
    """Wire-rim spectacles."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        r = s//5
        br = s//8
        draw.ellipse([cx-br-r, cy-r, cx-br+r, cy+r], outline=255, width=3)
        draw.ellipse([cx+br-r, cy-r, cx+br+r, cy+r], outline=255, width=3)
        draw.line([(cx-br, cy), (cx+br, cy)], fill=255, width=2)
        draw.line([(cx-br-r, cy), (cx-br-r-s//3, cy)], fill=255, width=2)
        draw.line([(cx+br+r, cy), (cx+br+r+s//3, cy)], fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.06, 4)

def _draw_prop_pocket_watch_01(size):
    """Closed pocket watch."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        # bow
        draw.ellipse([cx-s//12, cy-s//2-s//10, cx+s//12, cy-s//2+s//10], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)

def _draw_prop_vintage_perfume_01(size):
    """Art deco perfume bottle with glass stopper."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # body - faceted bottle
        draw.polygon([(cx-s//4, cy+s//4), (cx+s//4, cy+s//4), (cx+s//3, cy-s//6), (cx-s//3, cy-s//6)], fill=255)
        # neck
        draw.rectangle([cx-s//12, cy-s//3, cx+s//12, cy-s//6], fill=255)
        # stopper
        draw.polygon([(cx-s//8, cy-s//3), (cx+s//8, cy-s//3), (cx+s//6, cy-s//2), (cx-s//6, cy-s//2)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GLASS_GREEN, GLASS_CLEAR, mask)
    img = _render_metal(grad, GLASS_GREEN, 0.04, 0.02, 2)
    # gold cap band
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([cx-s//10, cy-s//3, cx+s//10, cy-s//4], fill=GOLD_LIGHT+(180,))
    return img

def _draw_prop_pearl_necklace_01(size):
    """Strand of pearls draped in a curve."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # draped necklace shape
        for i in range(12):
            a = i * 0.28
            px_ = cx - s//3 + int(i * s//6 * 0.9)
            py_ = cy + int(s//4 * math.sin(a))
            r_ = s//14
            draw.ellipse([px_-r_, py_-r_, px_+r_, py_+r_], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, SILVER_LIGHT, PEWTER_DARK, mask)
    return _render_metal(grad, SILVER_MID, 0.05, 0.04, 2)

def _draw_prop_vintage_bracelet_01(size):
    """Engraved bangle bracelet."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//4, cy-s//8, cx+s//4, cy+s//8], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 2)

def _draw_prop_vintage_scissors_01(size):
    """Small scissors open."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # blades
        draw.line([(cx, cy), (cx-s//3, cy-s//4)], fill=255, width=4)
        draw.line([(cx, cy), (cx+s//3, cy-s//4)], fill=255, width=4)
        # finger loops
        draw.ellipse([cx-s//5, cy+s//6, cx-s//10, cy+s//3], outline=255, width=3)
        draw.ellipse([cx+s//10, cy+s//6, cx+s//5, cy+s//3], outline=255, width=3)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/5, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.07, 4)

def _draw_prop_safety_razor_01(size):
    """Safety razor handle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//10, cy-s//2, cx+s//10, cy+s//2], radius=4, fill=255)
        # head
        draw.rounded_rectangle([cx-s//6, cy-s//2, cx+s//6, cy-s//3], radius=4, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.05, 0.08, 3)

def _draw_prop_vintage_comb_01(size):
    """Pocket comb."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//5, cy-s//3, cx+s//5, cy+s//3], radius=4, fill=255)
        # teeth
        for dx in range(-s//5+4, s//5-2, 4):
            draw.line([(cx+dx, cy+s//8), (cx+dx, cy+s//3)], fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.05, 0.04, 3)

def _draw_prop_hair_clip_01(size):
    """Metal hair clip."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//6), (cx+s//3, cy-s//8), (cx+s//3, cy+s//8), (cx-s//3, cy+s//6)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.05, 3)

def _draw_prop_envelope_corner_01(size):
    """Triangular envelope corner."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx, cy-s//2), (cx+s//3, cy+s//3), (cx-s//3, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    # address lines
    draw = ImageDraw.Draw(img)
    draw.line([(cx-s//6, cy), (cx+s//8, cy)], fill=INK_BLACK, width=1)
    draw.line([(cx-s//6, cy+s//8), (cx+s//6, cy+s//8)], fill=INK_BLACK, width=1)
    return img

def _draw_prop_cameo_brooch_01(size):
    """Oval cameo brooch with profile."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    # inner cameo
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//5, cy-s//6, cx+s//5, cy+s//6], fill=PAPER_LIGHT+(200,))
    draw2.ellipse([cx-4, cy-8, cx+4, cy], fill=INK_BLACK+(120,))
    return img

def _draw_prop_vintage_earring_01(size):
    """Chandelier-style drop earring."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # hook
        draw.arc([cx-4, cy-s//2-4, cx+4, cy-s//2+4], 0, 180, fill=255, width=2)
        # teardrop
        draw.polygon([(cx, cy+s//3), (cx-s//5, cy-s//6), (cx+s//5, cy-s//6)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.04, 3)

def _draw_prop_gemstone_pendant_01(size):
    """Oval gemstone in a claw setting."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], fill=255)
        # bail
        draw.ellipse([cx-3, cy-s//5-8, cx+3, cy-s//5], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, (180,40,50), (80,15,20), s//5, mask)
    img = _render_metal(grad, (130,25,30), 0.04, 0.03, 2)
    # claw prongs
    draw2 = ImageDraw.Draw(img)
    for a in [math.pi/4, 3*math.pi/4, 5*math.pi/4, 7*math.pi/4]:
        draw2.ellipse([cx+s//6*math.cos(a)-2, cy+s//6*math.sin(a)-2, cx+s//6*math.cos(a)+2, cy+s//6*math.sin(a)+2], fill=GOLD_LIGHT+(200,))
    return img

def _draw_prop_vintage_locket_01(size):
    """Heart-shaped locket with hinge."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # heart shape
        draw.ellipse([cx-s//4, cy-s//3, cx, cy-s//12], fill=255)
        draw.ellipse([cx, cy-s//3, cx+s//4, cy-s//12], fill=255)
        draw.polygon([(cx-s//4, cy-s//12), (cx+s//4, cy-s//12), (cx, cy+s//3)], fill=255)
        # bail
        draw.ellipse([cx-3, cy-s//3-6, cx+3, cy-s//3], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)

def _draw_prop_jeweled_compact_01(size):
    """Round jeweled compact mirror."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, SILVER_DARK, s//3, mask)
    img = _render_metal(grad, SILVER_MID, 0.05, 0.04, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=GLASS_CLEAR+(100,))
    for i in range(8):
        a = i * math.pi/4
        draw2.ellipse([cx+s//4*math.cos(a)-2, cy+s//4*math.sin(a)-2, cx+s//4*math.cos(a)+2, cy+s//4*math.sin(a)+2], fill=GOLD_LIGHT+(180,))
    return img

def _draw_prop_pocket_mirror_01(size):
    """Small rectangular folding mirror."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//3, cx+s//4, cy+s//3], radius=5, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, BRASS_LIGHT, BRASS_DARK, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.rounded_rectangle([cx-s//4+4, cy-s//3+4, cx+s//4-4, cy+s//3-4], radius=3, fill=GLASS_CLEAR+(80,))
    return img

def _draw_prop_vintage_cufflink_01(size):
    """Round cufflink with monogram."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        # link bar
        draw.rectangle([cx-2, cy+s//4, cx+2, cy+s//4+8], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//4, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.04, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.line([(cx-6, cy-4), (cx+6, cy+4)], fill=GOLD_DARK, width=1)
    draw2.line([(cx-6, cy+4), (cx+6, cy-4)], fill=GOLD_DARK, width=1)
    return img

def _draw_prop_vintage_tie_pin_01(size):
    """Decorative tie pin with pearl head."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # pin shaft (short, decorative)
        draw.rectangle([cx-2, cy, cx+2, cy+s//3], fill=255)
        # decorative head
        draw.ellipse([cx-s//8, cy-s//8, cx+s//8, cy+s//8], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.04, 2)

def _draw_prop_wax_seal_01(size):
    """Wax seal stamp with handle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # handle
        draw.rounded_rectangle([cx-s//8, cy-s//3, cx+s//8, cy-s//10], radius=2, fill=255)
        # seal disk
        draw.ellipse([cx-s//5, cy-s//10, cx+s//5, cy+s//5], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, BRASS_LIGHT, BRASS_DARK, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    # red wax on seal face
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//6, cy-2, cx+s//6, cy+s//4], fill=(160,40,35,200))
    return img

def _draw_prop_snuff_box_01(size):
    """Small oval snuff box."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, SILVER_DARK, s//3, mask)
    img = _render_metal(grad, SILVER_MID, 0.05, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//6, cx+s//4, cy+s//6], outline=GOLD_DARK, width=1)
    return img

def _draw_prop_monocle_01(size):
    """Monocle with chain fragment."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], outline=255, width=4)
        # chain
        draw.line([(cx+s//3, cy), (cx+s//3+s//6, cy)], fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.06, 3)

def _draw_prop_amber_stone_01(size):
    """Raw amber stone with inclusions."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        pts = []
        for i in range(8):
            a = i * math.pi/4 + random.uniform(-0.15, 0.15)
            r = s//3 + random.randint(-8, 8)
            pts.append((cx+r*math.cos(a), cy+r*math.sin(a)))
        draw.polygon(pts, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, (200,140,50), (120,75,25), s//3, mask)
    img = _render_metal(grad, (160,105,35), 0.04, 0.03, 2)
    # dark inclusion
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx+4, cy-2, cx+8, cy+4], fill=(50,35,20,180))
    return img

def _draw_prop_crystal_ball_01(size):
    """Small fortune teller crystal ball."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        # base
        draw.rounded_rectangle([cx-s//6, cy+s//3-4, cx+s//6, cy+s//3+s//10], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GLASS_CLEAR, (100,110,120), s//3, mask)
    img = _render_metal(grad, GLASS_CLEAR, 0.03, 0.02, 1)
    # highlight
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//8, cy-s//8, cx-s//12, cy-s//12], fill=(255,255,255,120))
    return img

def _draw_prop_rosary_beads_01(size):
    """Loop of rosary beads with cross."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        for i in range(14):
            a = i * math.pi*2/14
            bx = cx + int(s//3*math.cos(a))
            by = cy + int(s//4*math.sin(a))
            draw.ellipse([bx-3, by-3, bx+3, by+3], fill=255)
        # cross
        draw.rectangle([cx-2, cy+s//4, cx+2, cy+s//2], fill=255)
        draw.rectangle([cx-s//8, cy+s//3, cx+s//8, cy+s//3+4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.04, 3)

def _draw_prop_signet_ring_01(size):
    """Heavy signet ring with engraved face."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # band
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
        draw.ellipse([cx-s//4, cy-s//8, cx+s//4, cy+s//8], fill=0)
        # signet face
        draw.rounded_rectangle([cx-s//6, cy-s//2, cx+s//6, cy-s//5], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, BRASS_LIGHT, BRASS_SHADOW, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-3, cy-s//2+4, cx+3, cy-s//2+10], outline=BRASS_SHADOW, width=1)
    return img

def _draw_prop_cigar_cutter_01(size):
    """Guillotine-style cigar cutter."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//6, cy-s//4, cx+s//6, cy+s//4], radius=3, fill=255)
        # hole
        draw.ellipse([cx-s//8, cy-s//10, cx+s//8, cy+s//10], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.07, 3)

def _draw_prop_vintage_hat_pin_01(size):
    """Long decorative hat pin with ornate head."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # ornate head
        draw.ellipse([cx-s//5, cy-s//4, cx+s//5, cy-s//6], fill=255)
        # pin shaft
        draw.rectangle([cx-1, cy-s//6, cx+1, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.05, 0.04, 2)

def _draw_prop_opera_glasses_01(size):
    """Small opera glasses / binoculars."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx-s//12, cy+s//4], fill=255)
        draw.ellipse([cx+s//12, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.rectangle([cx-s//12, cy-s//6, cx+s//12, cy+s//6], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)

def _draw_prop_pocket_sundial_01(size):
    """Brass pocket sundial."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    # gnomon shadow
    draw2.polygon([(cx, cy), (cx+s//4, cy-s//8), (cx+s//4, cy+s//8)], fill=BRASS_SHADOW+(120,))
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=BRASS_DARK, width=1)
    return img

def _draw_prop_pocket_abacus_01(size):
    """Mini brass abacus."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//3, cy-s//3, cx+s//3, cy+s//3], radius=3, fill=255)
        # beads
        for dy in range(-s//5, s//5+1, s//5):
            for dx in range(-s//5, s//5+1, s//5):
                draw.ellipse([cx+dx-3, cy+dy-3, cx+dx+3, cy+dy+3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)

def _draw_prop_vintage_thimble_02(size):
    """Decorated sewing thimble with dimple pattern."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy+s//4), (cx+s//4, cy+s//4), (cx+s//5, cy-s//4), (cx-s//5, cy-s//4)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    img = _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    for dy in range(-s//6, s//6, 4):
        for dx in range(-s//6, s//6, 4):
            draw2.ellipse([cx+dx-1, cy+dy-1, cx+dx+1, cy+dy+1], fill=BRASS_SHADOW+(80,))
    return img

def _draw_prop_vintage_comb_02(size):
    """Small tortoiseshell folding comb."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//3, cx+s//4, cy+s//3], radius=6, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, WOOD_DARK, WOOD_LIGHT, mask)
    img = _render_metal(grad, WOOD_MID, 0.04, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    for i in range(5):
        draw2.line([(cx-s//5+i*8, cy-s//3+4), (cx-s//5+i*8, cy+s//3-4)], fill=WOOD_DARK+(100,), width=1)
    return img

def _draw_prop_pearl_earring_01(size):
    """Single pearl drop earring."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.arc([cx-4, cy-s//2-4, cx+4, cy-s//2+4], 0, 180, fill=255, width=2)
        draw.ellipse([cx-s//10, cy-s//6, cx+s//10, cy+s//10], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, PEWTER_DARK, s//3, mask)
    return _render_metal(grad, SILVER_MID, 0.04, 0.03, 2)

def _draw_prop_vintage_bracelet_02(size):
    """Charm bracelet with dangling charms."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
        draw.ellipse([cx-s//4, cy-s//8, cx+s//4, cy+s//8], fill=0)
        # charms
        draw.ellipse([cx-s//3, cy+s//6, cx-s//3+6, cy+s//6+6], fill=255)
        draw.ellipse([cx+s//3-6, cy+s//6, cx+s//3, cy+s//6+6], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)

def _draw_prop_vintage_ring_03(size):
    """Twisted wire ring with small gem."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//8], fill=0)
        # gem setting
        draw.ellipse([cx-4, cy-s//2, cx+4, cy-s//2+8], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, SILVER_LIGHT, SILVER_DARK, mask)
    img = _render_metal(grad, SILVER_MID, 0.05, 0.04, 2)
    # small blue gem
    px = img.load()
    for y in range(cy-s//2+2, cy-s//2+6):
        for x in range(cx-3, cx+3):
            px[x, y] = (60, 80, 140, 200)
    return img

def _draw_prop_vintage_perfume_02(size):
    """Round atomizer perfume bottle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        # neck
        draw.rectangle([cx-s//10, cy-s//3, cx+s//10, cy-s//4], fill=255)
        # bulb
        draw.ellipse([cx-s//8, cy-s//2, cx+s//8, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GLASS_BROWN, GLASS_CLEAR, s//4, mask)
    return _render_metal(grad, GLASS_BROWN, 0.04, 0.03, 2)

def _draw_prop_vintage_brooch_02(size):
    """Floral filigree brooch."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # flower shape
        for i in range(6):
            a = i * math.pi/3
            px_ = cx + int(s//5*math.cos(a))
            py_ = cy + int(s//5*math.sin(a))
            draw.ellipse([px_-6, py_-6, px_+6, py_+6], fill=255)
        draw.ellipse([cx-5, cy-5, cx+5, cy+5], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 2)

def _draw_prop_vintage_lighter_01(size):
    """Old rectangular flip lighter."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//3, cx+s//4, cy+s//3], radius=4, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/2, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.07, 0.06, 3)

def _draw_prop_zippo_lighter_01(size):
    """Zippo-style hinged lighter."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//5, cy-s//3, cx+s//5, cy+s//3], radius=2, fill=255)
        # hinge
        draw.rectangle([cx+s//5-2, cy-s//4, cx+s//5+2, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.07, 4)

def _draw_prop_ashtray_01(size):
    """Round metal ashtray."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, PEWTER_LIGHT, PEWTER_DARK, s//3, mask)
    return _render_metal(grad, PEWTER_MID, 0.08, 0.05, 3)

def _draw_prop_corkscrew_01(size):
    """Corkscrew with spiral."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # handle
        draw.rounded_rectangle([cx-s//8, cy-s//2, cx+s//8, cy-s//6], radius=3, fill=255)
        # shaft
        draw.rectangle([cx-2, cy-s//6, cx+2, cy+s//3], fill=255)
        # spiral approx
        for i in range(6):
            y = cy + s//6 + i*s//14
            r = s//12 - i
            draw.ellipse([cx-r, y-r, cx+r, y+r], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.06, 0.07, 4)

def _draw_prop_bottle_opener_01(size):
    """Church key bottle opener."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # handle
        draw.rounded_rectangle([cx-4, cy-s//2, cx+4, cy], radius=2, fill=255)
        # head
        draw.polygon([(cx-4, cy), (cx+4, cy), (cx+s//4, cy+s//8), (cx+s//4, cy-s//8)], fill=255)
        # keyhole
        draw.ellipse([cx+s//5-2, cy-2, cx+s//5+2, cy+2], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_spoon_01(size):
    """Small teaspoon."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # bowl
        draw.ellipse([cx-s//6, cy-s//2, cx+s//6, cy-s//8], fill=255)
        # handle
        draw.rectangle([cx-3, cy-s//8, cx+3, cy+s//2], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, SILVER_LIGHT, SILVER_DARK, mask)
    return _render_metal(grad, SILVER_MID, 0.05, 0.06, 3)

def _draw_prop_fork_01(size):
    """Dinner fork."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # tines
        for dx in [-s//10, -s//20, s//20, s//10]:
            draw.line([(cx+dx, cy-s//2), (cx+dx, cy-s//8)], fill=255, width=3)
        # handle
        draw.rectangle([cx-3, cy-s//8, cx+3, cy+s//2], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, SILVER_LIGHT, SILVER_DARK, mask)
    return _render_metal(grad, SILVER_MID, 0.05, 0.06, 4)

def _draw_prop_coffee_stirrer_01(size):
    """Wooden coffee stirrer."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-4, cy-s//2, cx+4, cy+s//3], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/5, WOOD_LIGHT, WOOD_DARK, mask)
    return _render_metal(grad, WOOD_MID, 0.04, 0.02, 2)

def _draw_prop_bottle_cap_01(size):
    """Crown bottle cap."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    draw = ImageDraw.Draw(grad)
    for i in range(16):
        a = i * math.pi/8
        x1, y1 = cx + s//4*math.cos(a), cy + s//4*math.sin(a)
        x2, y2 = cx + s//3*math.cos(a), cy + s//3*math.sin(a)
        draw.line([(x1,y1),(x2,y2)], fill=BRASS_SHADOW, width=1)
    return _render_metal(grad, BRASS_MID, 0.07, 0.06, 3)

def _draw_prop_small_bottle_01(size):
    """Small medicine bottle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//6, cy-s//3, cx+s//6, cy+s//4], radius=4, fill=255)
        draw.rectangle([cx-s//8, cy-s//3-s//8, cx+s//8, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GLASS_BROWN, GLASS_CLEAR, mask)
    return _render_metal(grad, GLASS_BROWN, 0.04, 0.02, 2)

def _draw_prop_whiskey_bottle_01(size):
    """Whiskey bottle silhouette."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//5, cy+s//3), (cx+s//5, cy+s//3), (cx+s//5, cy), (cx+s//8, cy-s//3), (cx-s//8, cy-s//3), (cx-s//5, cy)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GLASS_BROWN, (70,45,25), mask)
    return _render_metal(grad, GLASS_BROWN, 0.04, 0.02, 2)

def _draw_prop_plastic_straw_01(size):
    """Bent plastic straw."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.line([(cx-s//3, cy+s//3), (cx, cy), (cx, cy-s//2)], fill=255, width=5)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PLASTIC_CREAM, PAPER_DARK, mask)
    return _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)

def _draw_prop_shot_glass_01(size):
    """Shot glass."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//5, cy-s//3), (cx+s//5, cy-s//3), (cx+s//7, cy+s//3), (cx-s//7, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/5, GLASS_CLEAR, GLASS_GREEN, mask)
    return _render_metal(grad, GLASS_CLEAR, 0.03, 0.02, 1)

def _draw_prop_vintage_medal_01(size):
    """Military-style medal with ribbon stub."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # ribbon
        draw.rectangle([cx-s//8, cy-s//2, cx+s//8, cy-s//4], fill=255)
        # medallion
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy+s//12, GOLD_LIGHT, GOLD_DARK, s//4, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 2)

def _draw_prop_vintage_badge_01(size):
    """Star badge."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        pts = []
        for i in range(10):
            a = i * math.pi/5 - math.pi/2
            r = s//3 if i % 2 == 0 else s//6
            pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
        draw.polygon(pts, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.05, 3)

def _draw_prop_chain_fragment_01(size):
    """Chunk of chain."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        for i in range(3):
            x = cx - s//4 + i*s//4
            draw.ellipse([x-6, cy-8, x+6, cy+8], outline=255, width=3)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_small_jewelry_bag_01(size):
    """Drawstring pouch."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy-s//3), (cx+s//4, cy-s//3), (cx+s//5, cy+s//3), (cx-s//5, cy+s//3)], fill=255)
        # drawstring
        draw.arc([cx-s//5, cy-s//3-4, cx+s//5, cy-s//3+4], 0, 180, fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, CLOTH_CREAM, PAPER_DARK, mask)
    return _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)

def _draw_prop_sugar_packet_01(size):
    """Sugar packet."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy-s//6), (cx+s//4, cy-s//8), (cx+s//4, cy+s//8), (cx-s//4, cy+s//6)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.line([(cx-s//8, cy), (cx+s//8, cy)], fill=INK_BLUE, width=1)
    return img

def _draw_prop_candy_wrapper_01(size):
    """Twisted candy wrapper."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy-s//8), (cx+s//4, cy-s//10), (cx+s//3, cy+s//10), (cx-s//3, cy+s//8)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, (220,180,160), (180,140,120), mask)
    return _render_metal(grad, (180,140,120), 0.03, 0.02, 1)

def _draw_prop_cloth_napkin_01(size):
    """Folded cloth napkin corner."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//3), (cx+s//3, cy-s//3), (cx+s//3, cy+s//3), (cx-s//3, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, CLOTH_CREAM, PAPER_DARK, mask)
    return _render_metal(grad, PAPER_DARK, 0.02, 0.01, 1)

def _draw_prop_magnifying_glass_01(size):
    """Magnifying glass."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], outline=255, width=4)
        draw.rectangle([cx-3, cy+s//3, cx+3, cy+s//2], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, BRASS_LIGHT, BRASS_DARK, mask)
    return _render_metal(grad, BRASS_MID, 0.05, 0.06, 3)

def _draw_prop_pocket_knife_01(size):
    """Closed pocket knife."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//10, cx+s//4, cy+s//10], radius=4, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_DARK, STEEL_LIGHT, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.07, 3)

def _draw_prop_compass_01(size):
    """Compass with needle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, BRASS_LIGHT, BRASS_DARK, s//3, mask)
    draw = ImageDraw.Draw(grad)
    draw.line([(cx, cy-s//4), (cx, cy+s//4)], fill=BRASS_SHADOW, width=2)
    draw.line([(cx-s//4, cy), (cx+s//4, cy)], fill=BRASS_LIGHT, width=1)
    return _render_metal(grad, BRASS_MID, 0.06, 0.05, 3)

def _draw_prop_dice_01(size):
    """Dice cube."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//3, cy-s//3, cx+s//3, cy+s//3], radius=5, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, COPPER_LIGHT, COPPER_DARK, s//3, mask)
    # pips
    draw = ImageDraw.Draw(grad)
    draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=BRASS_SHADOW)
    return _render_metal(grad, COPPER_MID, 0.05, 0.04, 2)

def _draw_prop_photograph_corner_01(size):
    """Torn photo corner."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//3), (cx+s//3, cy-s//3), (cx+s//3, cy+s//4), (cx-s//4, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    return _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)

def _draw_prop_price_sticker_01(size):
    """Round price sticker."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.line([(cx-s//6, cy), (cx+s//6, cy)], fill=INK_BLACK, width=1)
    return img

def _draw_prop_barcode_sticker_01(size):
    """Rectangular barcode label."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//3, cy-s//5, cx+s//3, cy+s//5], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    for bx in range(cx-s//3+4, cx+s//3-4, 3):
        draw.line([(bx, cy-s//8), (bx, cy+s//8)], fill=INK_BLACK, width=random.choice([1,2]))
    return img

def _draw_prop_rewind_sticker_01(size):
    """Small circular rewind sticker."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, PAPER_LIGHT, PAPER_DARK, s//4, mask)
    return _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)

def _draw_prop_record_sleeve_corner_01(size):
    """Record sleeve corner."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//3), (cx+s//3, cy-s//3), (cx+s//3, cy+s//3), (cx-s//3, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.polygon([(cx-s//6, cy-s//6), (cx+s//6, cy-s//6), (cx, cy+s//6)], fill=INK_BLACK+(60,))
    return img

def _draw_prop_vinyl_label_01(size):
    """Vinyl record label."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, (70,40,30), (40,25,20), s//3, mask)
    return _render_metal(grad, (70,40,30), 0.04, 0.03, 2)

def _draw_prop_small_bolt_01(size):
    """Hex bolt with threads."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx, cy-s//3), (cx+s//4, cy-s//6), (cx+s//4, cy+s//6), (cx, cy+s//3), (cx-s//4, cy+s//6), (cx-s//4, cy-s//6)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_washer_01(size):
    """Flat washer."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-s//6, cy-s//6, cx+s//6, cy+s//6], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, STEEL_LIGHT, STEEL_DARK, s//3, mask)
    return _render_metal(grad, STEEL_MID, 0.05, 0.07, 3)

def _draw_prop_screw_01(size):
    """Wood screw with flat head."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], fill=255)
        draw.rectangle([cx-2, cy, cx+2, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_nail_01(size):
    """Iron nail."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-3, cy-s//2), (cx+3, cy-s//2), (cx+2, cy+s//3), (cx-2, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, RUST_LIGHT, RUST_DARK, mask)
    return _render_metal(grad, RUST_MID, 0.08, 0.10, 4)

def _draw_prop_fishing_hook_01(size):
    """Fishing hook."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.arc([cx-s//4, cy-s//4, cx+s//4, cy+s//4], 90, 270, fill=255, width=3)
        draw.line([(cx, cy-s//4), (cx, cy+s//3)], fill=255, width=3)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.06, 0.08, 4)

def _draw_prop_safety_pin_01(size):
    """Closed safety pin."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.arc([cx-s//4, cy-s//3, cx+s//4, cy+s//3], 180, 360, fill=255, width=3)
        draw.line([(cx+s//4, cy), (cx+s//4, cy+s//3)], fill=255, width=3)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.05, 0.07, 4)

def _draw_prop_thimble_01(size):
    """Sewing thimble."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy+s//4), (cx+s//4, cy+s//4), (cx+s//5, cy-s//4), (cx-s//5, cy-s//4)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, SILVER_LIGHT, SILVER_DARK, s//3, mask)
    return _render_metal(grad, SILVER_MID, 0.06, 0.05, 3)

def _draw_prop_paperclip_01(size):
    """Bent paperclip."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.line([(cx-s//3, cy-s//4), (cx-s//4, cy+s//3), (cx+s//4, cy+s//3), (cx+s//3, cy-s//4)], fill=255, width=3)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.05, 0.07, 4)

def _draw_prop_razor_blade_01(size):
    """Single razor blade."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy-s//3), (cx+s//4, cy-s//3), (cx+s//3, cy+s//3), (cx-s//3, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, STEEL_LIGHT, STEEL_DARK, mask)
    return _render_metal(grad, STEEL_MID, 0.05, 0.08, 5)

def _draw_prop_matchstick_01(size):
    """Burnt matchstick."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-2, cy-s//2, cx+2, cy+s//3], radius=1, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, WOOD_LIGHT, WOOD_DARK, mask)
    img = _render_metal(grad, WOOD_MID, 0.04, 0.02, 2)
    draw = ImageDraw.Draw(img)
    draw.ellipse([cx-4, cy+s//3-6, cx+4, cy+s//3], fill=(40,35,30,200))
    return img

def _draw_prop_diner_check_01(size):
    """Diner check slip."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//3), (cx+s//4, cy-s//3), (cx+s//3, cy+s//3), (cx-s//4, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    for ly in [cy-s//8, cy, cy+s//8]:
        draw.line([(cx-s//5, ly), (cx+s//5, ly)], fill=INK_BLACK, width=1)
    return img

def _draw_prop_newspaper_clip_01(size):
    """Folded newspaper corner."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//3), (cx+s//3, cy-s//3), (cx+s//3, cy+s//4), (cx-s//3, cy+s//3)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    for i in range(5):
        draw.line([(cx-s//3+4, cy-s//5+i*s//12), (cx+s//3-4, cy-s//5+i*s//12)], fill=INK_BLACK, width=1)
    return img

def _draw_prop_matchbook_01(size):
    """Standard matchbook."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//5, cx+s//4, cy+s//4], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.rectangle([cx-s//4+4, cy+s//8, cx+s//4-4, cy+s//4-2], fill=(45,40,35,180))
    return img

def _draw_prop_matchbook_motel_01(size):
    """Motel matchbook with arrow."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//4, cy-s//5, cx+s//4, cy+s//4], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.polygon([(cx-s//8, cy), (cx+s//8, cy-s//10), (cx+s//8, cy+s//10)], fill=INK_RED+(140,))
    return img

def _draw_prop_postage_stamp_01(size):
    """Postage stamp with perforations."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rectangle([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, PAPER_LIGHT, PAPER_DARK, mask)
    img = _render_metal(grad, PAPER_DARK, 0.03, 0.02, 1)
    draw = ImageDraw.Draw(img)
    draw.rectangle([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=INK_BLUE, width=1)
    return img

# ══════════════════════════════════════════════════════════════
# ADDITIONAL VINTAGE JEWELRY / PERFUME / MIRROR REPLACEMENTS
# (replacing sticks, bars, and paper props)
# ══════════════════════════════════════════════════════════════

def _draw_prop_vintage_perfume_03(size):
    """Tall art-deco perfume bottle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//5, cy+s//4), (cx+s//5, cy+s//4), (cx+s//8, cy-s//3), (cx-s//8, cy-s//3)], fill=255)
        draw.ellipse([cx-s//10, cy-s//3-s//8, cx+s//10, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GLASS_BROWN, (90,70,50), mask)
    img = _render_metal(grad, GLASS_BROWN, 0.04, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([cx-s//8, cy-s//3, cx+s//8, cy-s//4], fill=GOLD_LIGHT+(180,))
    return img

def _draw_prop_vintage_perfume_04(size):
    """Crystal perfume atomizer with bulb."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//5, cy-s//5, cx+s//5, cy+s//5], radius=6, fill=255)
        draw.rectangle([cx-s//12, cy-s//3, cx+s//12, cy-s//5], fill=255)
        draw.ellipse([cx-s//8, cy-s//2-s//10, cx+s//8, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GLASS_CLEAR, (110,120,130), s//4, mask)
    img = _render_metal(grad, GLASS_CLEAR, 0.03, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([cx-s//10, cy-s//3, cx+s//10, cy-s//4], fill=GOLD_LIGHT+(160,))
    return img

def _draw_prop_vintage_potion_bottle_01(size):
    """Small round apothecary potion bottle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        draw.rectangle([cx-s//12, cy-s//3, cx+s//12, cy-s//4], fill=255)
        draw.rectangle([cx-s//10, cy-s//3-s//6, cx+s//10, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GLASS_GREEN, (70,85,70), s//4, mask)
    return _render_metal(grad, GLASS_GREEN, 0.04, 0.03, 2)

def _draw_prop_vintage_glass_vial_01(size):
    """Tiny glass vial with stopper."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//8, cy-s//4, cx+s//8, cy+s//4], radius=4, fill=255)
        draw.rounded_rectangle([cx-s//10, cy-s//4-s//8, cx+s//10, cy-s//4], radius=2, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, (180,170,160), (90,85,80), mask)
    img = _render_metal(grad, (130,120,115), 0.04, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//10, cy-s//6, cx+s//10, cy+s//6], fill=(60,50,45,120))
    return img

def _draw_prop_vintage_chatelaine_01(size):
    """Victorian chatelaine with dangling charms."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # belt clip
        draw.ellipse([cx-s//6, cy-s//2, cx+s//6, cy-s//3], fill=255)
        # chain
        draw.line([(cx, cy-s//3), (cx, cy+s//4)], fill=255, width=2)
        # charms
        draw.ellipse([cx-s//8, cy+s//4, cx+s//8, cy+s//2], fill=255)
        draw.ellipse([cx-s//4, cy+s//3, cx-s//12, cy+s//2], fill=255)
        draw.ellipse([cx+s//12, cy+s//3, cx+s//4, cy+s//2], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, SILVER_LIGHT, SILVER_DARK, mask)
    return _render_metal(grad, SILVER_MID, 0.06, 0.05, 3)

def _draw_prop_vintage_hand_mirror_01(size):
    """Ornate hand mirror with handle."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # mirror face
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        # handle
        draw.polygon([(cx-3, cy+s//4), (cx+3, cy+s//4), (cx+s//8, cy+s//2), (cx-s//8, cy+s//2)], fill=255)
        # decorative top
        draw.ellipse([cx-s//6, cy-s//2, cx+s//6, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    img = _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], fill=GLASS_CLEAR+(90,))
    return img

def _draw_prop_vintage_tiara_01(size):
    """Small jeweled tiara."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # base band
        draw.ellipse([cx-s//3, cy-s//8, cx+s//3, cy+s//8], fill=255)
        # peaks
        pts = [(cx-s//3, cy), (cx-s//4, cy-s//2), (cx-s//8, cy), (cx, cy-s//2), (cx+s//8, cy), (cx+s//4, cy-s//2), (cx+s//3, cy)]
        draw.polygon(pts, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, SILVER_LIGHT, SILVER_DARK, mask)
    img = _render_metal(grad, SILVER_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    for i in range(7):
        px_ = cx - s//3 + i * s//10
        draw2.ellipse([px_-2, cy-s//2-2, px_+2, cy-s//2+2], fill=(60,80,120,180))
    return img

def _draw_prop_vintage_powder_box_01(size):
    """Round powder compact with lid."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=GOLD_DARK, width=2)
    draw2.ellipse([cx-3, cy-3, cx+3, cy+3], fill=(60,40,80,160))
    return img

def _draw_prop_vintage_coin_04(size):
    """Worn roman-style coin with hole."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        draw.ellipse([cx-s//10, cy-s//10, cx+s//10, cy+s//10], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, COPPER_LIGHT, COPPER_DARK, s//3, mask)
    img = _render_metal(grad, COPPER_MID, 0.07, 0.06, 3)
    draw2 = ImageDraw.Draw(img)
    draw2.line([(cx, cy-s//3+s//8), (cx, cy+s//3-s//8)], fill=BRASS_DARK, width=1)
    return img

def _draw_prop_vintage_filigree_bracelet_01(size):
    """Wide filigree cuff bracelet."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//5, cy-s//7, cx+s//5, cy+s//7], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)
    draw2 = ImageDraw.Draw(img)
    for i in range(8):
        a = i * math.pi/4
        draw2.ellipse([cx+s//3*math.cos(a)-2, cy+s//4*math.sin(a)-2, cx+s//3*math.cos(a)+2, cy+s//4*math.sin(a)+2], fill=GOLD_DARK+(120,))
    return img

def _draw_prop_vintage_hair_comb_01(size):
    """Ornate decorative hair comb."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # arch top
        draw.arc([cx-s//3, cy-s//3, cx+s//3, cy], 0, 180, fill=255, width=5)
        # teeth
        for dx in range(-s//3+4, s//3-2, 5):
            draw.line([(cx+dx, cy-s//8), (cx+dx, cy+s//3)], fill=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/3, GOLD_LIGHT, GOLD_DARK, mask)
    return _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)

def _draw_prop_vintage_barrette_01(size):
    """Jeweled hair barrette."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//3, cy-s//8), (cx+s//3, cy-s//10), (cx+s//3, cy+s//10), (cx-s//3, cy+s//8)], fill=255)
        # center gem
        draw.ellipse([cx-s//10, cy-s//10, cx+s//10, cy+s//10], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GOLD_LIGHT, GOLD_DARK, mask)
    img = _render_metal(grad, GOLD_MID, 0.06, 0.04, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//10, cy-s//10, cx+s//10, cy+s//10], fill=(120,40,60,180))
    return img

def _draw_prop_vintage_pocket_watch_02(size):
    """Open pocket watch with visible face."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
        # bow
        draw.ellipse([cx-s//10, cy-s//2-s//10, cx+s//10, cy-s//2+s//10], outline=255, width=2)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.06, 0.04, 3)
    draw2 = ImageDraw.Draw(img)
    # watch face
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=PAPER_LIGHT+(160,))
    draw2.line([(cx, cy-s//4), (cx, cy)], fill=INK_BLACK, width=1)
    draw2.line([(cx, cy), (cx+s//8, cy+s//12)], fill=INK_BLACK, width=1)
    return img

def _draw_prop_vintage_filigree_collar_01(size):
    """Ornate filigree collar brooch."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # crescent collar shape
        pts = [(cx-s//3, cy+s//6), (cx-s//4, cy-s//3), (cx, cy-s//2), (cx+s//4, cy-s//3), (cx+s//3, cy+s//6)]
        draw.polygon(pts, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, SILVER_LIGHT, SILVER_DARK, mask)
    img = _render_metal(grad, SILVER_MID, 0.06, 0.05, 3)
    draw2 = ImageDraw.Draw(img)
    for i in range(5):
        px_ = cx - s//3 + i * s//6
        draw2.ellipse([px_-2, cy-s//4-2, px_+2, cy-s//4+2], fill=(60,80,120,160))
    return img

def _draw_prop_jewelry_dish_01(size):
    """Round ornate jewelry dish with a central pearl."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=GOLD_DARK, width=2)
    pearl = _draw_pearl(s//10, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx - pw//2, cy - ph//2), pearl)
    return img

def _draw_prop_perfume_bottle_05(size):
    """Round art-deco perfume bottle with pearl cap."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        draw.rectangle([cx-s//12, cy-s//3, cx+s//12, cy-s//4], fill=255)
        draw.ellipse([cx-s//8, cy-s//2-s//10, cx+s//8, cy-s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, (225, 205, 185), (115, 95, 75), s//4, mask)
    img = _render_metal(grad, (150, 130, 110), 0.03, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([cx-s//10, cy-s//3, cx+s//10, cy-s//4], fill=GOLD_LIGHT+(180,))
    pearl = _draw_pearl(s//10, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx - pw//2, cy - s//2 - s//12 - ph//2), pearl)
    return img

def _draw_prop_pearl_strand_bracelet_01(size):
    """Pearl strand bracelet with gold clasp."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rx, ry = s//3, s//5
    n = 18
    for i in range(n):
        a = i * 2 * math.pi / n
        px_ = cx + int(rx * math.cos(a))
        py_ = cy + int(ry * math.sin(a))
        pr = s//13
        pearl = _draw_pearl(pr, (245, 235, 220))
        img.paste(pearl, (px_ - pr, py_ - pr), pearl)
    draw.rectangle([cx-s//10, cy-ry-s//10, cx+s//10, cy-ry+s//10], fill=GOLD_LIGHT+(200,))
    img = _draw_shadow(img, 5, 8, blur=5, alpha=60)
    return img

def _draw_prop_gem_drop_earring_01(size):
    """Gold drop earring with a large gem and small pearl."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # hook
    draw.arc([cx-s//10, cy-s//2-s//10, cx+s//10, cy-s//2+s//10], 0, 180, fill=GOLD_LIGHT+(255,), width=3)
    # gold frame drop
    draw.polygon([(cx-s//6, cy-s//4), (cx+s//6, cy-s//4), (cx+s//10, cy+s//4), (cx-s//10, cy+s//4)], fill=GOLD_LIGHT+(255,))
    # gem
    gem = _draw_gem(s//8, (170, 70, 90))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-s//8), gem)
    # pearl top
    pearl = _draw_pearl(s//14, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-s//4-ph//2), pearl)
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_lipstick_01(size):
    """Vintage gold lipstick tube with pink bullet."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # case
    draw.rounded_rectangle([cx-s//7, cy, cx+s//7, cy+s//3], radius=4, fill=GOLD_LIGHT+(255,))
    # bullet
    draw.polygon([(cx-s//9, cy), (cx+s//9, cy), (cx+s//10, cy-s//4), (cx-s//10, cy-s//4)], fill=(230, 150, 150, 255))
    # decorative band
    draw.rectangle([cx-s//7, cy+s//6, cx+s//7, cy+s//5], fill=GOLD_DARK+(255,))
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_jewelry_box_01(size):
    """Small ornate jewelry box with gem clasp."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.rounded_rectangle([cx-s//3, cy-s//4, cx+s//3, cy+s//4], radius=5, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, GOLD_LIGHT, GOLD_DARK, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.line([(cx-s//3+5, cy), (cx+s//3-5, cy)], fill=GOLD_DARK, width=2)
    gem = _draw_gem(s//12, (140, 50, 70))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//2), gem)
    return img

def _draw_prop_powder_compact_02(size):
    """Round powder compact with central gem."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=GOLD_DARK, width=2)
    gem = _draw_gem(s//12, (90, 60, 110))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//2), gem)
    return img

def _draw_prop_pearl_cuff_bracelet_01(size):
    """Gold cuff bracelet with two large pearl settings."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//8], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    for dx in [-s//4, s//4]:
        pearl = _draw_pearl(s//11, (245, 235, 220))
        pw, ph = pearl.size
        img.paste(pearl, (cx+dx-pw//2, cy-ph//2), pearl)
    return img

def _draw_prop_gold_cuff_bracelet_01(size):
    """Wide engraved gold bangle cuff."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//5, cy-s//7, cx+s//5, cy+s//7], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    for i in range(6):
        a = i * math.pi / 3
        x1 = cx + int(s//3 * math.cos(a))
        y1 = cy + int(s//4 * math.sin(a))
        x2 = cx + int(s//5 * math.cos(a))
        y2 = cy + int(s//7 * math.sin(a))
        draw2.line([(x1, y1), (x2, y2)], fill=GOLD_DARK, width=2)
    return img

def _draw_prop_gem_brooch_01(size):
    """Oval gold brooch with a large central gem and pearl accents."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    gem = _draw_gem(s//7, (210, 160, 110))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//2), gem)
    for i in range(6):
        a = i * math.pi / 3
        px_ = cx + int(s//3 * math.cos(a))
        py_ = cy + int(s//4 * math.sin(a))
        pearl = _draw_pearl(s//18, (245, 235, 220))
        pw, ph = pearl.size
        img.paste(pearl, (px_-pw//2, py_-ph//2), pearl)
    return img

def _draw_prop_makeup_brush_01(size):
    """Vintage makeup brush with gold handle."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # bristles
    draw.polygon([(cx-s//6, cy-s//3), (cx+s//6, cy-s//3), (cx+s//9, cy), (cx-s//9, cy)], fill=(205, 170, 140, 255))
    # ferrule
    draw.rectangle([cx-s//10, cy, cx+s//10, cy+s//8], fill=GOLD_LIGHT+(255,))
    # handle
    draw.polygon([(cx-s//10, cy+s//8), (cx+s//10, cy+s//8), (cx+s//12, cy+s//2), (cx-s//12, cy+s//2)], fill=GOLD_DARK+(255,))
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_crystal_perfume_01(size):
    """Tall crystal perfume bottle with gem stopper."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//5, cy+s//3), (cx+s//5, cy+s//3), (cx+s//7, cy-s//4), (cx-s//7, cy-s//4)], fill=255)
        draw.rectangle([cx-s//10, cy-s//2, cx+s//10, cy-s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, (210, 210, 215), (120, 120, 130), mask)
    img = _render_metal(grad, (150, 150, 160), 0.03, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    gem = _draw_gem(s//14, (140, 70, 90))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-s//2-s//12), gem)
    return img

def _draw_prop_pearl_choker_01(size):
    """Pearl choker necklace with gold clasp."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    rx, ry = s//3, s//6
    n = 22
    for i in range(n):
        a = i * 2 * math.pi / n
        px_ = cx + int(rx * math.cos(a))
        py_ = cy + int(ry * math.sin(a))
        pr = s//16
        pearl = _draw_pearl(pr, (245, 235, 220))
        img.paste(pearl, (px_ - pr, py_ - pr), pearl)
    draw = ImageDraw.Draw(img)
    draw.rectangle([cx-s//10, cy-ry-s//10, cx+s//10, cy-ry+s//10], fill=GOLD_LIGHT+(200,))
    img = _draw_shadow(img, 5, 8, blur=5, alpha=60)
    return img

def _draw_prop_opal_pendant_01(size):
    """Gold pendant with an opal-like gem and pearl."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # bail
    draw.ellipse([cx-s//12, cy-s//2-s//10, cx+s//12, cy-s//2+s//10], outline=GOLD_LIGHT+(255,), width=3)
    # ornate frame
    draw.polygon([(cx-s//6, cy-s//4), (cx+s//6, cy-s//4), (cx+s//8, cy+s//3), (cx-s//8, cy+s//3)], fill=GOLD_LIGHT+(255,))
    gem = _draw_gem(s//7, (180, 200, 210))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//4), gem)
    pearl = _draw_pearl(s//16, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-s//4-ph), pearl)
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_art_nouveau_brooch_01(size):
    """Art-nouveau gold brooch with flowing lines and a central gem."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        pts = [(cx-s//3, cy), (cx-s//5, cy-s//3), (cx, cy-s//4), (cx+s//5, cy-s//3), (cx+s//3, cy), (cx+s//5, cy+s//3), (cx, cy+s//4), (cx-s//5, cy+s//3)]
        draw.polygon(pts, fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    gem = _draw_gem(s//9, (120, 150, 120))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//2), gem)
    return img

def _draw_prop_enamel_cufflink_01(size):
    """Round gold cufflink with enamel center and pearl."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
        draw.ellipse([cx-s//6, cy-s//6, cx+s//6, cy+s//6], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//4, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//6, cy-s//6, cx+s//6, cy+s//6], fill=(120, 60, 60, 180))
    pearl = _draw_pearl(s//16, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-ph//2), pearl)
    return img

def _draw_prop_pearl_hair_comb_01(size):
    """Ornate gold hair comb with pearl-studded arch."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # arch
    draw.arc([cx-s//3, cy-s//3, cx+s//3, cy], 0, 180, fill=GOLD_LIGHT+(255,), width=5)
    # teeth
    for dx in range(-s//3+4, s//3-2, 6):
        draw.line([(cx+dx, cy-s//10), (cx+dx, cy+s//3)], fill=GOLD_LIGHT+(255,), width=2)
    # pearls along arch
    for i in range(7):
        a = i * math.pi / 6
        px_ = cx + int(s//3 * math.cos(a))
        py_ = cy - int(s//3 * math.sin(a))
        pearl = _draw_pearl(s//18, (245, 235, 220))
        pw, ph = pearl.size
        img.paste(pearl, (px_-pw//2, py_-ph//2), pearl)
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_lip_balm_01(size):
    """Small vintage lip balm pot with gold lid."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//4, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//5, cy-s//5, cx+s//5, cy+s//5], fill=(205, 140, 130, 180))
    return img

def _draw_prop_cameo_pendant_01(size):
    """Oval gold cameo pendant with a pearl profile."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//4, cy-s//3, cx+s//4, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//5, cy-s//4, cx+s//5, cy+s//4], fill=(230, 210, 185, 200))
    # profile silhouette
    draw2.ellipse([cx-s//12, cy-s//6, cx+s//12, cy+s//12], fill=(120, 90, 80, 160))
    return img

def _draw_prop_pearl_signet_ring_01(size):
    """Gold signet ring with a pearl face."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//8], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    pearl = _draw_pearl(s//10, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-ph//2), pearl)
    return img

def _draw_prop_gold_bangle_01(size):
    """Smooth polished gold bangle bracelet."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.ellipse([cx-s//5, cy-s//7, cx+s//5, cy+s//7], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.04, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    # hinge
    draw2.rectangle([cx-s//12, cy-s//5, cx+s//12, cy-s//7], fill=GOLD_DARK+(200,))
    return img

def _draw_prop_seal_ring_01(size):
    """Ornate signet ring with an engraved face."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//5, cx+s//3, cy+s//5], fill=255)
        draw.ellipse([cx-s//5, cy-s//8, cx+s//5, cy+s//8], fill=0)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//6, cy-s//8, cx+s//6, cy+s//8], fill=(120, 70, 50, 180))
    draw2.line([(cx-s//8, cy), (cx+s//8, cy)], fill=GOLD_DARK, width=2)
    return img

def _draw_prop_parfum_bottle_01(size):
    """Small flacon perfume bottle with a gold bow stopper."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.polygon([(cx-s//4, cy+s//4), (cx+s//4, cy+s//4), (cx+s//6, cy-s//4), (cx-s//6, cy-s//4)], fill=255)
        draw.ellipse([cx-s//8, cy-s//2, cx+s//8, cy-s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _linear_gradient(s, math.pi/4, (180, 160, 140), (90, 75, 60), mask)
    img = _render_metal(grad, (130, 110, 95), 0.03, 0.02, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.rectangle([cx-s//8, cy-s//3, cx+s//8, cy-s//4], fill=GOLD_LIGHT+(180,))
    return img

def _draw_prop_rouge_compact_01(size):
    """Round rouge compact with gold case and pink center."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=(200, 120, 130, 180))
    return img

def _draw_prop_sapphire_pendant_01(size):
    """Gold pendant with a deep blue sapphire and pearl accent."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # bail
    draw.ellipse([cx-s//12, cy-s//2-s//10, cx+s//12, cy-s//2+s//10], outline=GOLD_LIGHT+(255,), width=3)
    # ornate frame
    draw.polygon([(cx-s//5, cy-s//4), (cx+s//5, cy-s//4), (cx+s//7, cy+s//3), (cx-s//7, cy+s//3)], fill=GOLD_LIGHT+(255,))
    gem = _draw_gem(s//7, (60, 90, 150))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//4), gem)
    pearl = _draw_pearl(s//16, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-s//4-ph), pearl)
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_emerald_drop_earring_01(size):
    """Gold drop earring with emerald and tiny pearls."""
    s = size; cx, cy = s//2, s//2
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.arc([cx-s//10, cy-s//2-s//10, cx+s//10, cy-s//2+s//10], 0, 180, fill=GOLD_LIGHT+(255,), width=3)
    draw.polygon([(cx-s//7, cy-s//4), (cx+s//7, cy-s//4), (cx+s//10, cy+s//4), (cx-s//10, cy+s//4)], fill=GOLD_LIGHT+(255,))
    gem = _draw_gem(s//8, (70, 140, 100))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-s//8), gem)
    for dy in [-s//3, -s//4]:
        pearl = _draw_pearl(s//20, (245, 235, 220))
        pw, ph = pearl.size
        img.paste(pearl, (cx-pw//2, cy+dy-ph//2), pearl)
    img = _draw_shadow(img, 4, 6, blur=5, alpha=55)
    return img

def _draw_prop_compact_mirror_01(size):
    """Round gold compact mirror with engraved rim."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//3, cx+s//3, cy+s//3], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], fill=GLASS_CLEAR+(120,))
    draw2.ellipse([cx-s//4, cy-s//4, cx+s//4, cy+s//4], outline=GOLD_DARK, width=2)
    return img

def _draw_prop_heart_locket_01(size):
    """Gold heart-shaped locket with a pearl."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        # heart shape
        draw.ellipse([cx-s//3, cy-s//4, cx, cy+s//4], fill=255)
        draw.ellipse([cx, cy-s//4, cx+s//3, cy+s//4], fill=255)
        draw.polygon([(cx-s//3, cy), (cx, cy+s//3), (cx+s//3, cy)], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    pearl = _draw_pearl(s//12, (245, 235, 220))
    pw, ph = pearl.size
    img.paste(pearl, (cx-pw//2, cy-ph//3), pearl)
    return img

def _draw_prop_amber_brooch_01(size):
    """Gold brooch with an amber cabochon center."""
    s = size; cx, cy = s//2, s//2
    def shape(draw, s):
        draw.ellipse([cx-s//3, cy-s//4, cx+s//3, cy+s//4], fill=255)
    mask = _make_mask_from_shape(s, shape)
    grad = _radial_gradient(s, cx, cy, GOLD_LIGHT, GOLD_DARK, s//3, mask)
    img = _render_metal(grad, GOLD_MID, 0.05, 0.03, 2)
    draw2 = ImageDraw.Draw(img)
    gem = _draw_gem(s//7, (200, 130, 60))
    gw, gh = gem.size
    img.paste(gem, (cx-gw//2, cy-gh//2), gem)
    return img

# ══════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════


DRAWERS = {
    # === Keys & Locks ===
    "PROP_OLD_KEY_01": _draw_prop_old_key_01,
    "PROP_OLD_KEY_02": _draw_prop_old_key_02,
    "PROP_OLD_KEY_03": _draw_prop_old_key_03,
    "PROP_KEYCHAIN_01": _draw_prop_keychain_01,
    "PROP_PADLOCK_01": _draw_prop_heart_locket_01,
    # === Coins & Tokens ===
    "PROP_VINTAGE_COIN_01": _draw_prop_pearl_choker_01,
    "PROP_VINTAGE_COIN_02": _draw_prop_opal_pendant_01,
    "PROP_GAS_STATION_TOKEN_01": _draw_prop_gem_drop_earring_01,
    "PROP_VINTAGE_COIN_03": _draw_prop_art_nouveau_brooch_01,
    "PROP_VINTAGE_COIN_04": _draw_prop_enamel_cufflink_01,
    # === Rings ===
    "PROP_VINTAGE_RING_01": _draw_prop_vintage_ring_01,
    "PROP_VINTAGE_RING_02": _draw_prop_vintage_ring_02,
    "PROP_SIGNET_RING_01": _draw_prop_signet_ring_01,
    "PROP_VINTAGE_RING_03": _draw_prop_vintage_ring_03,
    # === Buttons & Brooches ===
    "PROP_VINTAGE_BUTTON_01": _draw_prop_makeup_brush_01,
    "PROP_VINTAGE_BUTTON_02": _draw_prop_crystal_perfume_01,
    "PROP_BROOCH_01": _draw_prop_brooch_01,
    "PROP_CAMEO_BROOCH_01": _draw_prop_cameo_brooch_01,
    "PROP_VINTAGE_BROOCH_02": _draw_prop_vintage_brooch_02,
    "PROP_FILIGREE_COLLAR_01": _draw_prop_vintage_filigree_collar_01,
    # === Glasses & Watches ===
    "PROP_VINTAGE_GLASSES_01": _draw_prop_vintage_glasses_01,
    "PROP_POCKET_WATCH_01": _draw_prop_pocket_watch_01,
    "PROP_POCKET_WATCH_02": _draw_prop_vintage_pocket_watch_02,
    "PROP_MONOCLE_01": _draw_prop_monocle_01,
    "PROP_OPERA_GLASSES_01": _draw_prop_opera_glasses_01,
    # === Perfume & Bottles ===
    "PROP_VINTAGE_PERFUME_01": _draw_prop_vintage_perfume_01,
    "PROP_VINTAGE_PERFUME_02": _draw_prop_vintage_perfume_02,
    "PROP_VINTAGE_PERFUME_03": _draw_prop_vintage_perfume_03,
    "PROP_VINTAGE_PERFUME_04": _draw_prop_vintage_perfume_04,
    "PROP_VINTAGE_POTION_BOTTLE_01": _draw_prop_vintage_potion_bottle_01,
    "PROP_VINTAGE_GLASS_VIAL_01": _draw_prop_vintage_glass_vial_01,
    "PROP_SHOT_GLASS_01": _draw_prop_shot_glass_01,
    "PROP_BOTTLE_CAP_01": _draw_prop_perfume_bottle_05,
    # === Jewelry ===
    "PROP_PEARL_NECKLACE_01": _draw_prop_pearl_necklace_01,
    "PROP_PEARL_EARRING_01": _draw_prop_pearl_earring_01,
    "PROP_VINTAGE_EARRING_01": _draw_prop_vintage_earring_01,
    "PROP_GEMSTONE_PENDANT_01": _draw_prop_gemstone_pendant_01,
    "PROP_VINTAGE_LOCKET_01": _draw_prop_vintage_locket_01,
    "PROP_VINTAGE_BRACELET_01": _draw_prop_vintage_bracelet_01,
    "PROP_VINTAGE_BRACELET_02": _draw_prop_vintage_bracelet_02,
    "PROP_VINTAGE_FILIGREE_BRACELET_01": _draw_prop_vintage_filigree_bracelet_01,
    "PROP_VINTAGE_CUFFLINK_01": _draw_prop_pearl_hair_comb_01,
    "PROP_VINTAGE_TIE_PIN_01": _draw_prop_gold_bangle_01,
    "PROP_VINTAGE_HAT_PIN_01": _draw_prop_lip_balm_01,
    "PROP_JEWELED_COMPACT_01": _draw_prop_jeweled_compact_01,
    "PROP_POCKET_MIRROR_01": _draw_prop_pocket_mirror_01,
    "PROP_HAND_MIRROR_01": _draw_prop_vintage_hand_mirror_01,
    "PROP_VINTAGE_TIARA_01": _draw_prop_vintage_tiara_01,
    "PROP_POWDER_BOX_01": _draw_prop_vintage_powder_box_01,
    "PROP_CHATELAINE_01": _draw_prop_vintage_chatelaine_01,
    "PROP_VINTAGE_HAIR_COMB_01": _draw_prop_vintage_hair_comb_01,
    "PROP_VINTAGE_BARRETTE_01": _draw_prop_vintage_barrette_01,
    # === Lighters & Smoking Accessories ===
    "PROP_VINTAGE_LIGHTER_01": _draw_prop_cameo_pendant_01,
    "PROP_ZIPPO_LIGHTER_01": _draw_prop_parfum_bottle_01,
    "PROP_ASHTRAY_01": _draw_prop_jewelry_dish_01,
    "PROP_CIGAR_CUTTER_01": _draw_prop_rouge_compact_01,
    "PROP_SNUFF_BOX_01": _draw_prop_powder_compact_02,
    # === Small Tools ===
    "PROP_MAGNIFYING_GLASS_01": _draw_prop_compact_mirror_01,
    "PROP_POCKET_KNIFE_01": _draw_prop_lipstick_01,
    # === Medals, Badges, Religious ===
    "PROP_VINTAGE_MEDAL_01": _draw_prop_pearl_signet_ring_01,
    "PROP_VINTAGE_BADGE_01": _draw_prop_gem_brooch_01,
    "PROP_ROSARY_BEADS_01": _draw_prop_rosary_beads_01,
    "PROP_WAX_SEAL_01": _draw_prop_seal_ring_01,
    # === Compass & Sundial ===
    "PROP_COMPASS_01": _draw_prop_sapphire_pendant_01,
    "PROP_POCKET_SUNDIAL_01": _draw_prop_emerald_drop_earring_01,
    # === Sewing ===
    "PROP_THIMBLE_01": _draw_prop_pearl_cuff_bracelet_01,
    "PROP_VINTAGE_THIMBLE_02": _draw_prop_gold_cuff_bracelet_01,
    # === Stones & Curios ===
    "PROP_AMBER_STONE_01": _draw_prop_amber_brooch_01,
    "PROP_CRYSTAL_BALL_01": _draw_prop_crystal_ball_01,
    "PROP_CHAIN_FRAGMENT_01": _draw_prop_pearl_strand_bracelet_01,
    "PROP_SMALL_JEWELRY_BAG_01": _draw_prop_jewelry_box_01,
}

def generate_prop(prop_id, filename):
    """Generate one realistic vintage prop and place it centered on a 1024 canvas."""
    drawer = DRAWERS.get(prop_id, _draw_prop_old_key_01)
    prop_size = random.randint(80, 160)
    prop_img = drawer(prop_size)
    
    # Crop to content to reduce oversized canvas
    bbox = prop_img.getbbox()
    if bbox:
        pad = 12
        bbox = (max(0,bbox[0]-pad), max(0,bbox[1]-pad), min(prop_img.width,bbox[2]+pad), min(prop_img.height,bbox[3]+pad))
        prop_img = prop_img.crop(bbox)
    
    # Place in the center region of 1024 canvas (not too close to edges)
    # Center area: between 200 and CANVAS-200
    cx = random.randint(300, CANVAS - 300)
    cy = random.randint(280, CANVAS - 280)
    
    canvas = Image.new("RGBA", (CANVAS, CANVAS), (0,0,0,0))
    pw, ph = prop_img.size
    canvas.paste(prop_img, (cx - pw//2, cy - ph//2), prop_img)
    
    # slight rotation
    angle = random.uniform(-8, 8)
    canvas = canvas.rotate(angle, resample=Image.BICUBIC, center=(cx, cy), expand=False)
    
    # global alpha — keep props fairly solid since they are viewed as standalone objects now
    alpha = random.uniform(0.80, 0.98)
    px = canvas.load()
    for y in range(CANVAS):
        for x in range(CANVAS):
            r, g, b, a = px[x, y]
            if a > 0:
                px[x, y] = (r, g, b, int(a * alpha))
    
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else os.path.join(ASSETS_DIR, "props"), exist_ok=True)
    filepath = filename if os.path.isabs(filename) else os.path.join(ASSETS_DIR, "props", filename)
    canvas.save(filepath)
    return filepath

# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def generate_preview_grid(prop_dir, output_path, cols=8, cell=150, margin=22):
    """Generate a contact sheet preview of all generated props."""
    files = sorted([f for f in os.listdir(prop_dir) if f.endswith('.png')])
    rows = (len(files) + cols - 1) // cols
    bg = Image.new('RGBA', (cols * cell + (cols + 1) * margin, rows * cell + (rows + 1) * margin + 40), (248, 245, 238, 255))
    draw = ImageDraw.Draw(bg)
    for i, fn in enumerate(files):
        img = Image.open(os.path.join(prop_dir, fn)).convert('RGBA')
        # scale to fit cell while preserving aspect ratio
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        img.thumbnail((cell - 20, cell - 40), Image.LANCZOS)
        x = (i % cols) * (cell + margin) + margin + (cell - img.width) // 2
        y = (i // cols) * (cell + margin) + margin + 20 + (cell - 40 - img.height) // 2
        bg.paste(img, (x, y), img)
        # label
        name = os.path.splitext(fn)[0].replace('prop_', '')
        draw.text((x + img.width // 2 - 20, y + img.height + 4), name[:14], fill=(80, 75, 70), font=None)
    draw.text((margin, 12), f"{len(files)} Vintage Props v7 — jewelry, perfume & cosmetics", fill=(80, 75, 70), font=None)
    bg.save(output_path)
    print(f"Preview saved: {output_path}")

if __name__ == "__main__":
    PROPS_TO_GENERATE = list(DRAWERS.keys())
    prop_dir = os.path.join(ASSETS_DIR, "props")
    if os.path.exists(prop_dir):
        for f in os.listdir(prop_dir):
            if f.endswith(".png"):
                os.remove(os.path.join(prop_dir, f))
        print(f"Deleted old props in {prop_dir}")
    else:
        os.makedirs(prop_dir, exist_ok=True)
    
    print(f"\nGenerating {len(PROPS_TO_GENERATE)} props...")
    for i, prop_id in enumerate(PROPS_TO_GENERATE, 1):
        filename = prop_id.lower() + ".png"
        generate_prop(prop_id, filename)
        print(f"  {i:2d}/{len(PROPS_TO_GENERATE)} {filename}")
    print(f"\nDone: {len(PROPS_TO_GENERATE)} props generated in {prop_dir}")
    
    preview_path = os.path.join(os.path.dirname(__file__), "props_preview_grid_v7.png")
    generate_preview_grid(prop_dir, preview_path)
