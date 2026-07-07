#!/usr/bin/env python3
"""
generate_plan_0100.py
NO REFUNDS ARCHIVE - 100张拼装计划生成器 v3.0

v3.0 更新:
- 严格系列匹配规则：每个系列的stamps/handwritten/props/damage/overlays
  只能从各自允许的素材池中选择
- 素材ID直接对应assets目录中的实际文件名
- 61张底图尽量均匀使用
- 6个系列均匀分配
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
# 系列严格匹配规则 — 基于用户规范
# 每个trait_id必须对应assets目录中实际存在的PNG文件
# ══════════════════════════════════════════════════════════════

SERIES_RULES = {

    "Midnight Diner": {
        "stamps": [
            "STAMP_AFTER_HOURS",
            "STAMP_CLOSED",
            "STAMP_NO_REFUNDS",
            "STAMP_LAST_ORDER",
        ],
        "handwritten": [
            "NOTE_LAST_NIGHT",
            "NOTE_TABLE_6",
            "NOTE_1138PM",
            "NOTE_LAST_ORDER",
            "NOTE_BOOTH_4",
        ],
        "props": [
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
            "PROP_NAPKIN_01",
            "PROP_RECEIPT_CLIP_01",
            "PROP_SPOON_01",
            "PROP_SUGAR_PACKET_01",
            "PROP_COFFEE_STIRRER_01",
            "PROP_MATCHBOOK_01",
            "PROP_DINER_MENU_SCRAP_01",
            "PROP_TABLE_TICKET_01",
            "PROP_TABLE_TICKET_02",
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
            "STAMP_CHECKED_OUT",
            "STAMP_OVERDUE",
            "STAMP_NO_REFUNDS",
            "STAMP_DO_NOT_OPEN",
        ],
        "handwritten": [
            "NOTE_REWIND",
            "NOTE_LATE_FEE",
            "NOTE_RETURNED_EMPTY",
            "NOTE_DUE_FRIDAY",
            "NOTE_TAPE_12",
        ],
        "props": [
            "PROP_VHS_LABEL_01",
            "PROP_RENTAL_CARD_01",
            "PROP_REWIND_STICKER_01",
            "PROP_LATE_FEE_SLIP_01",
            "PROP_MEMBERSHIP_CARD_01",
            "PROP_VIDEO_CASE_CORNER_01",
            "PROP_RETURN_SLOT_TAG_01",
            "PROP_TAPE_SPINE_LABEL_01",
            "PROP_STORE_TAG_01",
            "PROP_PLASTIC_TAB_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
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
            "OVERLAY_CRT_GRAIN_01", "OVERLAY_CRT_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Lucky 8 Gas & Motel": {
        "stamps": [
            "STAMP_ROOM_PAID",
            "STAMP_CLOSED",
            "STAMP_NO_VACANCY",
            "STAMP_PAID_CASH",
        ],
        "handwritten": [
            "NOTE_NO_VACANCY",
            "NOTE_ROOM_8",
            "NOTE_1138PM",
            "NOTE_EXIT_22",
            "NOTE_PAID_CASH",
        ],
        "props": [
            "PROP_MOTEL_KEY_01",
            "PROP_MAP_SCRAP_01",
            "PROP_ROOM_TAG_01",
            "PROP_GAS_STATION_TOKEN_01",
            "PROP_PARKING_STUB_01",
            "PROP_MATCHBOOK_MOTEL_01",
            "PROP_POSTCARD_CORNER_01",
            "PROP_ROAD_EXIT_NOTE_01",
            "PROP_KEYCHAIN_01",
            "PROP_PAYPHONE_CARD_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
        ],
        "damages": [
            "DMG_WATER_STAIN_01", "DMG_WATER_STAIN_02", "DMG_WATER_STAIN_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_SMALL_TEAR_01",
            "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_RAIN_GLOW_01", "OVERLAY_RAIN_GLOW_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SOFT_VIGNETTE_01",
        ],
    },

    "Side B Records": {
        "stamps": [
            "STAMP_LAST_COPY",
            "STAMP_FINAL_SALE",
            "STAMP_STORE_CREDIT",
        ],
        "handwritten": [
            "NOTE_SIDE_B",
            "NOTE_LAST_COPY",
            "NOTE_A_SIDE_GONE",
            "NOTE_TRACK_07",
            "NOTE_STORE_CREDIT",
        ],
        "props": [
            "PROP_CASSETTE_01",
            "PROP_CATALOG_CARD_01",
            "PROP_VINYL_LABEL_01",
            "PROP_PRICE_STICKER_01",
            "PROP_USED_TAPE_TAG_01",
            "PROP_TRACKLIST_SCRAP_01",
            "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_STORE_CREDIT_SLIP_01",
            "PROP_B_SIDE_NOTE_01",
            "PROP_PLASTIC_SLEEVE_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
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
            "OVERLAY_CRT_GRAIN_01", "OVERLAY_CRT_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_FADED_INK_01",
        ],
    },

    "Sunset Mart": {
        "stamps": [
            "STAMP_FINAL_SALE",
            "STAMP_NO_REFUNDS",
            "STAMP_CLOSED",
        ],
        "handwritten": [
            "NOTE_LAST_SHIFT",
            "NOTE_AISLE_3",
            "NOTE_512PM",
            "NOTE_FINAL_SALE",
            "NOTE_REGISTER_2",
        ],
        "props": [
            "PROP_PRICE_TAG_01",
            "PROP_CANDY_WRAPPER_01",
            "PROP_BOTTLE_CAP_01",
            "PROP_LOTTERY_STUB_01",
            "PROP_COUPON_SCRAP_01", "PROP_COUPON_SCRAP_02",
            "PROP_PLASTIC_STRAW_WRAPPER_01",
            "PROP_AISLE_TAG_01",
            "PROP_REGISTER_TAPE_SCRAP_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
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
            "STAMP_CLAIM_CLOSED",
            "STAMP_PAWN_HOLD",
            "STAMP_UNCLAIMED",
        ],
        "handwritten": [
            "NOTE_CASE_14",
            "NOTE_30_DAYS",
            "NOTE_UNCLAIMED",
            "NOTE_HOLD_TAG",
            "NOTE_CLAIM_BY_5",
        ],
        "props": [
            "PROP_RING_BOX_01",
            "PROP_BROKEN_WATCH_01",
            "PROP_CLAIM_TICKET_01",
            "PROP_BRASS_TAG_01",
            "PROP_OLD_KEY_01",
            "PROP_CHAIN_FRAGMENT_01",
            "PROP_SMALL_JEWELRY_BAG_01",
            "PROP_CASE_LABEL_01",
            "PROP_PAWN_STUB_01",
            "PROP_GLASS_COUNTER_TAG_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
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
            "OVERLAY_GLASS_GLARE_01", "OVERLAY_GLASS_GLARE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_ARCHIVE_YELLOWING_01",
        ],
    },
}


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


def get_rarity_pool():
    """稀有度分布：Common 60%, Uncommon 25%, Rare 15%"""
    pool = ["Common"] * 60 + ["Uncommon"] * 25 + ["Rare"] * 15
    random.shuffle(pool)
    return pool


def generate_plan(n=100, seed=42):
    """生成 n 张严格按系列匹配规则的拼装计划"""
    random.seed(seed)

    templates = get_base_templates()
    series_list = list(SERIES_RULES.keys())
    rarity_pool = get_rarity_pool()

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

    # 构建系列队列并打乱（避免连续出现同一系列）
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

        # 严格按系列规则选择素材
        stamp = random.choice(rules["stamps"])
        handwritten = random.choice(rules["handwritten"])

        # 2个不重复的prop
        prop_pool = rules["props"][:]
        if len(prop_pool) >= 2:
            prop1, prop2 = random.sample(prop_pool, 2)
        else:
            prop1 = prop_pool[0]
            prop2 = prop_pool[0]

        damage = random.choice(rules["damages"])
        overlay = random.choice(rules["overlays"])
        rarity = rarity_pool[i % len(rarity_pool)]

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
            "印章素材": stamp,
            "手写素材": handwritten,
            "小物件1": prop1,
            "小物件2": prop2,
            "纸张痕迹": damage,
            "叠加滤镜/噪点": overlay,
            "稀有度": rarity,
            "拼装状态": "待拼装",
            "metadata状态": "待生成",
            "备注": f"Batch 0100 v3 - {series} #{seq}",
        })

    return rows


def write_csv(rows, output_path):
    """写入 CSV 文件"""
    fieldnames = [
        "编号", "最终文件名", "系列", "底图变体", "印章素材", "手写素材",
        "小物件1", "小物件2", "纸张痕迹", "叠加滤镜/噪点", "稀有度",
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
    print("  100张拼装计划统计 (v3.0 严格系列规则)")
    print(f"{'='*60}")

    series_counts = {}
    base_counts = {}
    stamp_counts = {}
    rarity_counts = {}

    for row in rows:
        s = row["系列"]
        series_counts[s] = series_counts.get(s, 0) + 1
        b = row["底图变体"]
        base_counts[b] = base_counts.get(b, 0) + 1
        st = row["印章素材"]
        stamp_counts[st] = stamp_counts.get(st, 0) + 1
        r = row["稀有度"]
        rarity_counts[r] = rarity_counts.get(r, 0) + 1

    print("\n📊 系列分布:")
    for s, c in sorted(series_counts.items()):
        print(f"  {s}: {c}张")

    print(f"\n📊 底图使用: {len(base_counts)}/61 种")
    print(f"  最少: {min(base_counts.values())}次, 最多: {max(base_counts.values())}次")

    print(f"\n📊 印章使用:")
    for st, c in sorted(stamp_counts.items()):
        print(f"  {st}: {c}次")

    print(f"\n📊 稀有度分布:")
    for r, c in sorted(rarity_counts.items()):
        print(f"  {r}: {c}张")

    print(f"\n{'='*60}")


def main():
    output_path = os.path.join(SCRIPT_DIR, "data", "auto_compose_plan_0100.csv")
    print("Generating 100-image composition plan (v3.0 strict series rules)...")
    rows = generate_plan(n=100, seed=42)
    write_csv(rows, output_path)
    print_summary(rows)


if __name__ == "__main__":
    main()
