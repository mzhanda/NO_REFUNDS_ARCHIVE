#!/usr/bin/env python3
"""
generate_plan_0100.py
NO REFUNDS ARCHIVE - 100张拼装计划生成器 v4.0

v4.0 更新:
- 新增 material_pattern 和 legendary_accent 字段
- 严格稀有度规则: Common 60, Uncommon 25, Rare 10, Legendary 4, Ultra Rare 1
- Common 不使用 legendary_accent
- Uncommon 可少量使用轻微 material_pattern
- Rare 必须有至少1个高级 trait (material_pattern 或 legendary_accent)
- Legendary 必须有至少2个高级 trait
- Ultra Rare 必须有2-3个高级 trait
- 高稀有度必须使用 gold stamps / holo overlays / legendary accents
- 严格系列匹配规则保持不变
"""

import csv
import os
import random
import sys
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════
# 系列严格匹配规则
# ══════════════════════════════════════════════════════════════

SERIES_RULES = {

    "Midnight Diner": {
        "stamps": [
            "STAMP_AFTER_HOURS", "STAMP_CLOSED", "STAMP_NO_REFUNDS", "STAMP_LAST_ORDER",
        ],
        "handwritten": [
            "NOTE_LAST_NIGHT", "NOTE_TABLE_6", "NOTE_1138PM", "NOTE_LAST_ORDER", "NOTE_BOOTH_4",
        ],
        "props": [
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
            "PROP_CLOTH_NAPKIN_01",
            "PROP_SPOON_01",
            "PROP_SUGAR_PACKET_01",
            "PROP_COFFEE_STIRRER_01",
            "PROP_MATCHBOOK_01",
            "PROP_DINER_CHECK_01",
            "PROP_CORKSCREW_01",
            "PROP_BOTTLE_OPENER_01",
            "PROP_FORK_01",
            "PROP_SHOT_GLASS_01",
            "PROP_WHISKEY_BOTTLE_01",
        ],
        "damages": [
            "DMG_COFFEE_RING_01", "DMG_COFFEE_RING_02", "DMG_COFFEE_RING_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_THERMAL_FADE_01",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
            "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_ARCHIVE_YELLOWING_01",
            "OVERLAY_SOFT_VIGNETTE_01",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Night Owl Video": {
        "stamps": [
            "STAMP_CHECKED_OUT", "STAMP_OVERDUE", "STAMP_NO_REFUNDS", "STAMP_DO_NOT_OPEN",
        ],
        "handwritten": [
            "NOTE_REWIND", "NOTE_LATE_FEE", "NOTE_RETURNED_EMPTY", "NOTE_DUE_FRIDAY", "NOTE_TAPE_12",
        ],
        "props": [
            "PROP_REWIND_STICKER_01",
            "PROP_BARCODE_STICKER_01",
            "PROP_PRICE_STICKER_01",
            "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_VINYL_LABEL_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
            "PROP_POCKET_KNIFE_01",
            "PROP_VINTAGE_GLASSES_01",
            "PROP_VINTAGE_LIGHTER_01",
            "PROP_ZIPPO_LIGHTER_01",
            "PROP_VINTAGE_BADGE_01",
            "PROP_MAGNIFYING_GLASS_01",
        ],
        "damages": [
            "DMG_TAPE_01", "DMG_TAPE_02",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_SCAN_NOISE_01", "DMG_SCAN_NOISE_02",
            "DMG_THERMAL_FADE_01",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
        ],
        "overlays": [
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Lucky 8 Gas & Motel": {
        "stamps": [
            "STAMP_ROOM_PAID", "STAMP_CLOSED", "STAMP_NO_VACANCY", "STAMP_PAID_CASH",
        ],
        "handwritten": [
            "NOTE_NO_VACANCY", "NOTE_ROOM_8", "NOTE_1138PM", "NOTE_EXIT_22", "NOTE_PAID_CASH",
        ],
        "props": [
            "PROP_OLD_KEY_01", "PROP_OLD_KEY_02", "PROP_OLD_KEY_03",
            "PROP_KEYCHAIN_01",
            "PROP_GAS_STATION_TOKEN_01",
            "PROP_MATCHBOOK_MOTEL_01",
            "PROP_POSTAGE_STAMP_01",
            "PROP_NEWSPAPER_CLIP_01",
            "PROP_CIGARETTE_01", "PROP_CIGARETTE_02",
            "PROP_ASHTRAY_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_WATER_STAIN_01", "DMG_WATER_STAIN_02", "DMG_WATER_STAIN_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_SMALL_TEAR_01",
            "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SOFT_VIGNETTE_01",
        ],
    },

    "Side B Records": {
        "stamps": [
            "STAMP_LAST_COPY", "STAMP_FINAL_SALE", "STAMP_STORE_CREDIT",
        ],
        "handwritten": [
            "NOTE_SIDE_B", "NOTE_LAST_COPY", "NOTE_A_SIDE_GONE", "NOTE_TRACK_07", "NOTE_STORE_CREDIT",
        ],
        "props": [
            "PROP_VINYL_LABEL_01",
            "PROP_PRICE_STICKER_01",
            "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_COMPASS_01",
            "PROP_DICE_01",
            "PROP_PHOTOGRAPH_CORNER_01",
            "PROP_VINTAGE_PEN_01", "PROP_VINTAGE_PEN_02",
            "PROP_FOUNTAIN_PEN_01",
            "PROP_VINTAGE_SCISSORS_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_TAPE_01", "DMG_TAPE_02",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
            "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Sunset Mart": {
        "stamps": [
            "STAMP_FINAL_SALE", "STAMP_NO_REFUNDS", "STAMP_CLOSED",
        ],
        "handwritten": [
            "NOTE_LAST_SHIFT", "NOTE_AISLE_3", "NOTE_512PM", "NOTE_FINAL_SALE", "NOTE_REGISTER_2",
        ],
        "props": [
            "PROP_CANDY_WRAPPER_01",
            "PROP_BOTTLE_CAP_01",
            "PROP_SMALL_BOTTLE_01",
            "PROP_PLASTIC_STRAW_01",
            "PROP_SUGAR_PACKET_01",
            "PROP_SAFETY_RAZOR_01",
            "PROP_VINTAGE_COMB_01",
            "PROP_HAIR_CLIP_01",
            "PROP_ENVELOPE_CORNER_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_COFFEE_RING_01", "DMG_COFFEE_RING_02", "DMG_COFFEE_RING_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_WATER_STAIN_01", "DMG_WATER_STAIN_02", "DMG_WATER_STAIN_03",
            "DMG_THERMAL_FADE_01",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
        ],
        "overlays": [
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_ARCHIVE_YELLOWING_01",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Token Pawn": {
        "stamps": [
            "STAMP_CLAIM_CLOSED", "STAMP_PAWN_HOLD", "STAMP_UNCLAIMED",
        ],
        "handwritten": [
            "NOTE_CASE_14", "NOTE_30_DAYS", "NOTE_UNCLAIMED", "NOTE_HOLD_TAG", "NOTE_CLAIM_BY_5",
        ],
        "props": [
            "PROP_OLD_KEY_01", "PROP_OLD_KEY_02", "PROP_OLD_KEY_03",
            "PROP_CHAIN_FRAGMENT_01",
            "PROP_SMALL_JEWELRY_BAG_01",
            "PROP_POCKET_WATCH_01",
            "PROP_VINTAGE_RING_01", "PROP_VINTAGE_RING_02",
            "PROP_VINTAGE_BUTTON_01", "PROP_VINTAGE_BUTTON_02",
            "PROP_BROOCH_01",
            "PROP_VINTAGE_MEDAL_01",
            "PROP_PADLOCK_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_TAPE_01", "DMG_TAPE_02",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
            "DMG_SMALL_TEAR_01",
            "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_ARCHIVE_YELLOWING_01",
        ],
    },
}

# ══════════════════════════════════════════════════════════════
# Legendary / Gold Stamps (跨系列可用，仅高稀有度)
# ══════════════════════════════════════════════════════════════
GOLD_STAMPS = [
    "STAMP_GENESIS_GOLD",
    "STAMP_1_OF_1_GOLD",
    "STAMP_ARCHIVED_FOREVER_GOLD",
    "STAMP_ULTRA_RARE_GOLD",
    "STAMP_VAULTED_GOLD",
    "STAMP_REDEEMED_GOLD",
    "STAMP_ZERO_SUPPLY_GOLD",
    "STAMP_GOLD_SEAL_GOLD",
]

# ══════════════════════════════════════════════════════════════
# Legendary Accents (高级特征)
# ══════════════════════════════════════════════════════════════
LEGENDARY_STICKERS = [
    "PROP_CROWN_GOLD_01", "PROP_CROWN_CHROME_01",
    "PROP_HOLO_SEAL_01", "PROP_DIAMOND_CLIP_01",
    "PROP_CHAIN_LUXE_01", "PROP_PEARL_TAG_01",
    "PROP_LASER_STICKER_01", "PROP_GEM_BADGE_01",
    "PROP_ACRYLIC_TOKEN_01", "PROP_CRYSTAL_SHARD_01",
]

LEGENDARY_OVERLAYS = [
    "OVERLAY_HOLO_PRISM_01",
    "OVERLAY_GOLD_DUST_01",
    "OVERLAY_IRIDESCENT_GLOW_01",
    "OVERLAY_LUXE_VIGNETTE_01",
    "OVERLAY_CRYSTAL_SPARK_01",
    "OVERLAY_NEON_ARCHIVE_01",
    "OVERLAY_RAINBOW_FOIL_01",
    "OVERLAY_ULTRA_RARE_SHIMMER_01",
]

# ══════════════════════════════════════════════════════════════
# Material / Pattern (材质纹理)
# ══════════════════════════════════════════════════════════════
LIGHT_MATERIALS = [
    "MAT_FROSTED_RECEIPT_01",
    "MAT_TRANSPARENT_RECEIPT_01",
    "MAT_GLOW_INK_01",
    "PAT_HOLO_GRID_01",
    "PAT_GOLD_FLECK_01",
]

HEAVY_MATERIALS = [
    "MAT_HOLOGRAPHIC_RECEIPT_01",
    "MAT_BLACK_GOLD_RECEIPT_01",
    "MAT_SILVER_FOIL_RECEIPT_01",
    "MAT_CHROME_EDGE_01",
    "MAT_GLASS_ARCHIVE_01",
    "PAT_LEOPARD_01",
    "PAT_SNAKESKIN_01",
    "PAT_IRIDESCENT_WAVE_01",
    "PAT_SECURITY_PRINT_01",
]


# ══════════════════════════════════════════════════════════════
# 辅助函数
# ══════════════════════════════════════════════════════════════

def get_base_templates():
    """返回61个底图变体列表"""
    templates = []
    base_counts = {
        "B01": 8, "B02": 12, "B03": 8, "B04": 8,
        "B05": 6, "B06": 10, "B07": 5, "B08": 4,
    }
    for btype, count in base_counts.items():
        for i in range(1, count + 1):
            templates.append(f"{btype}_VAR_{i:02d}")
    return templates


def pick_for_rarity(rules, rarity):
    """根据稀有度选择高级 trait。

    Common:     无 material_pattern, 无 legendary_accent, 普通 stamp/overlay
    Uncommon:   可选轻量 material_pattern, 无 legendary_accent
    Rare:       必须有 1 个高级 trait (material_pattern 或 legendary_accent)
    Legendary:  必须有 2 个高级 trait + gold stamp
    Ultra Rare: 必须有 2-3 个高级 trait + gold stamp + legendary overlay
    """
    mat = ""
    legend = ""
    stamp = random.choice(rules["stamps"])
    overlay = random.choice(rules["overlays"])

    if rarity == "Common":
        # No legendary traits at all
        pass

    elif rarity == "Uncommon":
        # 30% chance of a light material pattern
        if random.random() < 0.3:
            mat = random.choice(LIGHT_MATERIALS)

    elif rarity == "Rare":
        # Must have at least 1 advanced trait
        if random.random() < 0.5:
            # Use material
            if random.random() < 0.5:
                mat = random.choice(LIGHT_MATERIALS)
            else:
                mat = random.choice(HEAVY_MATERIALS)
        else:
            # Use legendary accent sticker
            legend = random.choice(LEGENDARY_STICKERS[:6])

    elif rarity == "Legendary":
        # Must have at least 2 advanced traits
        # Gold stamp
        stamp = random.choice(GOLD_STAMPS)
        # Material
        mat = random.choice(HEAVY_MATERIALS)
        # Legendary accent: always use a legendary overlay as accent
        legend = random.choice(LEGENDARY_OVERLAYS)
        # Sometimes also add a legendary sticker
        if random.random() < 0.5:
            legend = legend + ";" + random.choice(LEGENDARY_STICKERS[:4])

    elif rarity == "Ultra Rare":
        # Must have 2-3 advanced traits, most special
        stamp = random.choice(GOLD_STAMPS[4:])  # Most exclusive gold stamps
        mat = random.choice(HEAVY_MATERIALS[-4:])  # Most special materials
        # Always legendary overlay as accent
        legend = random.choice(LEGENDARY_OVERLAYS[-3:])
        # Legendary sticker too (combo)
        legend = legend + ";" + random.choice(LEGENDARY_STICKERS[:4])

    return stamp, overlay, mat, legend


def generate_plan(n=100, seed=42):
    """生成 n 张严格按系列匹配规则和稀有度规则的拼装计划"""
    random.seed(seed)

    templates = get_base_templates()
    series_list = list(SERIES_RULES.keys())

    # ── 稀有度分布 ──
    # Common: 60, Uncommon: 25, Rare: 10, Legendary: 4, Ultra Rare: 1
    rarity_pool = (
        ["Common"] * 60 +
        ["Uncommon"] * 25 +
        ["Rare"] * 10 +
        ["Legendary"] * 4 +
        ["Ultra Rare"] * 1
    )
    random.shuffle(rarity_pool)

    # 系列分配：17+17+17+17+16+16 = 100
    series_dist = {
        "Midnight Diner": 17,
        "Night Owl Video": 17,
        "Lucky 8 Gas & Motel": 17,
        "Side B Records": 17,
        "Sunset Mart": 16,
        "Token Pawn": 16,
    }

    # 打散模板顺序
    shuffled_templates = templates[:]
    random.shuffle(shuffled_templates)

    # 构建系列队列并打乱
    series_queue = []
    for series, count in series_dist.items():
        series_queue.extend([series] * count)
    random.shuffle(series_queue)

    # 轮询分配底图
    template_idx = 0
    series_base_assignments = {s: [] for s in series_list}
    for series in series_queue:
        tmpl = shuffled_templates[template_idx % len(shuffled_templates)]
        series_base_assignments[series].append(tmpl)
        template_idx += 1

    # 再打乱每个系列内部的底图顺序
    for s in series_list:
        random.shuffle(series_base_assignments[s])

    rows = []
    series_counters = {s: 0 for s in series_list}

    for i in range(n):
        series = series_queue[i]
        rules = SERIES_RULES[series]
        series_counters[series] += 1
        seq = series_counters[series]

        # 选底图
        tmpl_idx = seq - 1
        base_id = series_base_assignments[series][tmpl_idx]

        # 严格按系列规则选择普通素材
        handwritten = random.choice(rules["handwritten"])
        damage = random.choice(rules["damages"])

        # 0-1个prop (随机决定是否放小物件，不再固定2个)
        prop1 = ""
        prop2 = ""
        prop_pool = rules["props"][:]
        if len(prop_pool) >= 1 and random.random() < 0.7:
            # 70% chance of having one prop
            prop1 = random.choice(prop_pool)
            # 30% of those also get a second prop (so ~21% of all images have 2)
            if len(prop_pool) >= 2 and random.random() < 0.3:
                remaining = [p for p in prop_pool if p != prop1]
                if remaining:
                    prop2 = random.choice(remaining)

        # 稀有度相关的高级 trait 选择
        rarity = rarity_pool[i % len(rarity_pool)]
        stamp, overlay, mat, legend = pick_for_rarity(rules, rarity)

        # 编号和文件名
        nft_num = i + 1
        nft_id = f"NRA-{nft_num:04d}"
        series_abbr = series.replace(" & ", "").replace(" ", "")
        stamp_short = stamp.replace("STAMP_", "")
        filename = f"NRA_{nft_num:04d}_{series_abbr}_{base_id}_{stamp_short}.png"

        rows.append({
            "编号": nft_id,
            "最终文件名": filename,
            "系列": series,
            "底图变体": base_id,
            "材质/纹理": mat,
            "印章素材": stamp,
            "手写素材": handwritten,
            "小物件1": prop1,
            "小物件2": prop2,
            "纸张痕迹": damage,
            "叠加滤镜/噪点": overlay,
            "传奇特征": legend,
            "稀有度": rarity,
            "拼装状态": "待拼装",
            "metadata状态": "待生成",
            "备注": f"Batch 0100 v2 - {series} #{seq} [{rarity}]",
        })

    return rows


def write_csv(rows, output_path):
    """写入 CSV 文件"""
    fieldnames = [
        "编号", "最终文件名", "系列", "底图变体", "材质/纹理", "印章素材", "手写素材",
        "小物件1", "小物件2", "纸张痕迹", "叠加滤镜/噪点", "传奇特征", "稀有度",
        "拼装状态", "metadata状态", "备注",
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✓ CSV saved: {output_path}")
    print(f"  Total rows: {len(rows)}")


def print_summary(rows):
    """打印统计摘要"""
    print(f"\n{'='*60}")
    print("  100张拼装计划统计 (v4.0 稀有度规则)")
    print(f"{'='*60}")

    series_counts = {}
    base_counts = {}
    stamp_counts = {}
    rarity_counts = {}
    mat_counts = {}
    legend_counts = {}

    for row in rows:
        s = row["系列"]
        series_counts[s] = series_counts.get(s, 0) + 1
        b = row["底图变体"]
        base_counts[b] = base_counts.get(b, 0) + 1
        st = row["印章素材"]
        stamp_counts[st] = stamp_counts.get(st, 0) + 1
        r = row["稀有度"]
        rarity_counts[r] = rarity_counts.get(r, 0) + 1
        m = row.get("材质/纹理", "").strip()
        if m:
            mat_counts[m] = mat_counts.get(m, 0) + 1
        l = row.get("传奇特征", "").strip()
        if l:
            legend_counts[l] = legend_counts.get(l, 0) + 1

    print("\n📊 系列分布:")
    for s, c in sorted(series_counts.items()):
        print(f"  {s}: {c}张")

    print(f"\n📊 稀有度分布:")
    for r, c in sorted(rarity_counts.items()):
        print(f"  {r}: {c}张")

    print(f"\n📊 底图使用: {len(base_counts)}/61 种")
    print(f"  最少: {min(base_counts.values())}次, 最多: {max(base_counts.values())}次")

    print(f"\n📊 印章使用:")
    for st, c in sorted(stamp_counts.items()):
        print(f"  {st}: {c}次")

    if mat_counts:
        print(f"\n📊 材质/纹理使用:")
        for m, c in sorted(mat_counts.items()):
            print(f"  {m}: {c}次")

    if legend_counts:
        print(f"\n📊 传奇特征使用:")
        for l, c in sorted(legend_counts.items()):
            print(f"  {l}: {c}次")

    print(f"\n{'='*60}")


def main():
    output_path = os.path.join(SCRIPT_DIR, "data", "auto_compose_plan_0100_v2.csv")
    print("Generating 100-image composition plan (v4.0 rarity rules)...")
    rows = generate_plan(n=100, seed=42)
    write_csv(rows, output_path)
    print_summary(rows)


if __name__ == "__main__":
    main()
