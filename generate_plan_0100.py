#!/usr/bin/env python3
"""
generate_plan_0100.py
生成100张小批量拼装计划 CSV

规则：
- 6个系列均匀分配
- 61张底图尽量均匀使用
- 素材按系列规则匹配（基于实际存在的文件）
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

# ── 实际存在的素材文件（基于扫描结果） ──
# stamps: 7个
STAMPS = [
    "stamp_after_hours_red.png",
    "stamp_checked_out_red.png",
    "stamp_claim_closed_red.png",
    "stamp_closed_red.png",
    "stamp_last_copy_red.png",
    "stamp_no_refunds_red.png",
    "stamp_room_paid_red.png",
]
# handwritten: 9个
HANDWRITTEN = [
    "note_1138pm.png",
    "note_booth_4.png",
    "note_case_14.png",
    "note_last_night.png",
    "note_no_vacancy.png",
    "note_rewind.png",
    "note_server_m.png",
    "note_side_b.png",
    "note_table_6.png",
]
# props: 12个
PROPS = [
    "prop_broken_watch_01.png",
    "prop_cassette_01.png",
    "prop_catalog_card_01.png",
    "prop_coin_01.png",
    "prop_coin_02.png",
    "prop_map_scrap_01.png",
    "prop_motel_key_01.png",
    "prop_napkin_01.png",
    "prop_receipt_clip_01.png",
    "prop_rental_card_01.png",
    "prop_ring_box_01.png",
    "prop_vhs_label_01.png",
]
# damage: 6个
DAMAGES = [
    "damage_coffee_ring_01.png",
    "damage_edge_wear_01.png",
    "damage_fold_01.png",
    "damage_tape_01.png",
    "damage_tape_02.png",
    "damage_water_stain_01.png",
]
# overlays: 6个
OVERLAYS = [
    "overlay_crt_grain_01.png",
    "overlay_dust_01.png",
    "overlay_film_grain_01.png",
    "overlay_glass_glare_01.png",
    "overlay_rain_glow_01.png",
    "overlay_scan_noise_01.png",
]

# ── CSV ID → 实际文件名映射 ──
STAMP_ID_TO_FILE = {
    "STAMP_AFTER_HOURS":   "stamp_after_hours_red.png",
    "STAMP_NO_REFUNDS":    "stamp_no_refunds_red.png",
    "STAMP_CLOSED":        "stamp_closed_red.png",
    "STAMP_ROOM_PAID":     "stamp_room_paid_red.png",
    "STAMP_LAST_COPY":     "stamp_last_copy_red.png",
    "STAMP_CLAIM_CLOSED":  "stamp_claim_closed_red.png",
    "STAMP_CHECKED_OUT":   "stamp_checked_out_red.png",
    # 以下ID无实际文件，用相近的替代
    "STAMP_OVERDUE":       "stamp_checked_out_red.png",       # 最接近
    "STAMP_NO_VACANCY":    "stamp_closed_red.png",            # 替代
    "STAMP_FINAL_SALE":    "stamp_no_refunds_red.png",        # 替代
    "STAMP_PAWN_HOLD":     "stamp_claim_closed_red.png",      # 替代
    "STAMP_UNCLAIMED":     "stamp_claim_closed_red.png",      # 替代
}

HANDWRITTEN_ID_TO_FILE = {
    "NOTE_LAST_NIGHT":  "note_last_night.png",
    "NOTE_TABLE_6":     "note_table_6.png",
    "NOTE_1138PM":      "note_1138pm.png",
    "NOTE_BOOTH_4":     "note_booth_4.png",
    "NOTE_SERVER_M":    "note_server_m.png",
    "NOTE_REWIND":      "note_rewind.png",
    "NOTE_NO_VACANCY":  "note_no_vacancy.png",
    "NOTE_SIDE_B":      "note_side_b.png",
    "NOTE_CASE_14":     "note_case_14.png",
}

PROP_ID_TO_FILE = {
    "PROP_COIN_01":          "prop_coin_01.png",
    "PROP_COIN_02":          "prop_coin_02.png",
    "PROP_NAPKIN_01":        "prop_napkin_01.png",
    "PROP_RECEIPT_CLIP_01":  "prop_receipt_clip_01.png",
    "PROP_VHS_LABEL_01":     "prop_vhs_label_01.png",
    "PROP_RENTAL_CARD_01":   "prop_rental_card_01.png",
    "PROP_MOTEL_KEY_01":     "prop_motel_key_01.png",
    "PROP_MAP_SCRAP_01":     "prop_map_scrap_01.png",
    "PROP_CASSETTE_01":      "prop_cassette_01.png",
    "PROP_CATALOG_CARD_01":  "prop_catalog_card_01.png",
    "PROP_RING_BOX_01":      "prop_ring_box_01.png",
    "PROP_BROKEN_WATCH_01":  "prop_broken_watch_01.png",
}

DAMAGE_ID_TO_FILE = {
    "DMG_COFFEE_RING_01":  "damage_coffee_ring_01.png",
    "DMG_FOLD_01":         "damage_fold_01.png",
    "DMG_TAPE_01":         "damage_tape_01.png",
    "DMG_TAPE_02":         "damage_tape_02.png",
    "DMG_WATER_STAIN_01":  "damage_water_stain_01.png",
    "DMG_EDGE_WEAR_01":    "damage_edge_wear_01.png",
}

OVERLAY_ID_TO_FILE = {
    "OVERLAY_FILM_GRAIN_01":  "overlay_film_grain_01.png",
    "OVERLAY_SCAN_NOISE_01":  "overlay_scan_noise_01.png",
    "OVERLAY_DUST_01":        "overlay_dust_01.png",
    "OVERLAY_CRT_GRAIN_01":   "overlay_crt_grain_01.png",
    "OVERLAY_RAIN_GLOW_01":   "overlay_rain_glow_01.png",
    "OVERLAY_GLASS_GLARE_01": "overlay_glass_glare_01.png",
}

# ── 系列规则定义 ──
# 每个系列的: stamps, props, handwritten, damages, overlays (偏好列表)
SERIES_RULES = {
    "Midnight Diner": {
        "stamps":       ["STAMP_AFTER_HOURS", "STAMP_CLOSED", "STAMP_NO_REFUNDS"],
        "handwritten":  ["NOTE_LAST_NIGHT", "NOTE_TABLE_6", "NOTE_1138PM", "NOTE_BOOTH_4", "NOTE_SERVER_M"],
        "props":        ["PROP_COIN_01", "PROP_COIN_02", "PROP_NAPKIN_01", "PROP_RECEIPT_CLIP_01"],
        "damages":      ["DMG_COFFEE_RING_01", "DMG_FOLD_01", "DMG_EDGE_WEAR_01"],
        "overlays":     ["OVERLAY_FILM_GRAIN_01", "OVERLAY_DUST_01", "OVERLAY_SCAN_NOISE_01"],
    },
    "Night Owl Video": {
        "stamps":       ["STAMP_CHECKED_OUT", "STAMP_OVERDUE", "STAMP_NO_REFUNDS"],
        "handwritten":  ["NOTE_REWIND", "NOTE_CASE_14", "NOTE_SIDE_B", "NOTE_TABLE_6"],
        "props":        ["PROP_VHS_LABEL_01", "PROP_RENTAL_CARD_01"],
        "damages":      ["DMG_TAPE_01", "DMG_TAPE_02", "DMG_FOLD_01"],
        "overlays":     ["OVERLAY_CRT_GRAIN_01", "OVERLAY_SCAN_NOISE_01", "OVERLAY_DUST_01"],
    },
    "Lucky 8 Gas & Motel": {
        "stamps":       ["STAMP_ROOM_PAID", "STAMP_CLOSED", "STAMP_NO_VACANCY"],
        "handwritten":  ["NOTE_NO_VACANCY", "NOTE_1138PM", "NOTE_TABLE_6", "NOTE_BOOTH_4"],
        "props":        ["PROP_MOTEL_KEY_01", "PROP_MAP_SCRAP_01", "PROP_COIN_01"],
        "damages":      ["DMG_WATER_STAIN_01", "DMG_FOLD_01", "DMG_EDGE_WEAR_01"],
        "overlays":     ["OVERLAY_RAIN_GLOW_01", "OVERLAY_FILM_GRAIN_01", "OVERLAY_SCAN_NOISE_01"],
    },
    "Side B Records": {
        "stamps":       ["STAMP_LAST_COPY", "STAMP_FINAL_SALE"],
        "handwritten":  ["NOTE_SIDE_B", "NOTE_REWIND", "NOTE_CASE_14", "NOTE_TABLE_6"],
        "props":        ["PROP_CASSETTE_01", "PROP_CATALOG_CARD_01"],
        "damages":      ["DMG_TAPE_01", "DMG_TAPE_02", "DMG_DUST_01", "DMG_FOLD_01"],
        "overlays":     ["OVERLAY_DUST_01", "OVERLAY_SCAN_NOISE_01", "OVERLAY_CRT_GRAIN_01"],
    },
    "Sunset Mart": {
        "stamps":       ["STAMP_FINAL_SALE", "STAMP_NO_REFUNDS", "STAMP_CLOSED"],
        "handwritten":  ["NOTE_TABLE_6", "NOTE_1138PM", "NOTE_BOOTH_4", "NOTE_SERVER_M"],
        "props":        ["PROP_COIN_01", "PROP_COIN_02", "PROP_RECEIPT_CLIP_01", "PROP_NAPKIN_01"],
        "damages":      ["DMG_COFFEE_RING_01", "DMG_FOLD_01", "DMG_EDGE_WEAR_01"],
        "overlays":     ["OVERLAY_FILM_GRAIN_01", "OVERLAY_DUST_01", "OVERLAY_SCAN_NOISE_01"],
    },
    "Token Pawn": {
        "stamps":       ["STAMP_CLAIM_CLOSED", "STAMP_PAWN_HOLD", "STAMP_UNCLAIMED"],
        "handwritten":  ["NOTE_CASE_14", "NOTE_BOOTH_4", "NOTE_TABLE_6", "NOTE_1138PM"],
        "props":        ["PROP_RING_BOX_01", "PROP_BROKEN_WATCH_01", "PROP_COIN_01"],
        "damages":      ["DMG_EDGE_WEAR_01", "DMG_FOLD_01", "DMG_TAPE_01"],
        "overlays":     ["OVERLAY_GLASS_GLARE_01", "OVERLAY_DUST_01", "OVERLAY_SCAN_NOISE_01"],
    },
}

# Fix Side B Records: DMG_DUST_01 doesn't exist, use DMG_EDGE_WEAR_01
SERIES_RULES["Side B Records"]["damages"] = ["DMG_TAPE_01", "DMG_TAPE_02", "DMG_EDGE_WEAR_01", "DMG_FOLD_01"]


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
    """生成 n 张拼装计划"""
    random.seed(seed)
    
    templates = get_base_templates()
    series_list = list(SERIES_RULES.keys())
    rarity_pool = get_rarity_pool()
    
    # 6个系列各分配：Midnight Diner 17, Night Owl Video 17, Lucky 8 17, Side B 17, Sunset Mart 16, Token Pawn 16
    series_dist = {
        "Midnight Diner": 17,
        "Night Owl Video": 17,
        "Lucky 8 Gas & Motel": 17,
        "Side B Records": 17,
        "Sunset Mart": 16,
        "Token Pawn": 16,
    }
    
    # 打散模板使用顺序，确保61个底图尽量均匀
    shuffled_templates = templates[:]
    random.shuffle(shuffled_templates)
    
    # 生成每个系列的底图分配
    series_base_assignments = {}
    for series in series_list:
        series_base_assignments[series] = []
    
    # 轮询分配底图给每个系列
    series_queue = []
    for series, count in series_dist.items():
        series_queue.extend([series] * count)
    random.shuffle(series_queue)
    
    for i, series in enumerate(series_queue):
        tmpl = shuffled_templates[i % len(shuffled_templates)]
        series_base_assignments[series].append(tmpl)
    
    # 为每个系列再次打乱底图顺序
    for series in series_list:
        random.shuffle(series_base_assignments[series])
    
    rows = []
    series_counters = {s: 0 for s in series_list}
    
    # 交错分配，避免连续出现同一系列
    build_order = series_queue[:]
    
    for i in range(n):
        series = build_order[i]
        rules = SERIES_RULES[series]
        series_counters[series] += 1
        seq = series_counters[series]
        
        # 选底图
        tmpl_idx = seq - 1
        if tmpl_idx < len(series_base_assignments[series]):
            base_id = series_base_assignments[series][tmpl_idx]
        else:
            base_id = random.choice(shuffled_templates)
        
        # 选印章
        stamp = random.choice(rules["stamps"])
        
        # 选手写字
        handwritten = random.choice(rules["handwritten"])
        
        # 选小物件（2个不重复）
        prop_pool = rules["props"][:]
        if len(prop_pool) >= 2:
            prop1, prop2 = random.sample(prop_pool, 2)
        else:
            prop1 = prop_pool[0]
            prop2 = prop_pool[0] if prop_pool else ""
        
        # 选纸张痕迹
        damage = random.choice(rules["damages"])
        
        # 选滤镜
        overlay = random.choice(rules["overlays"])
        
        # 稀有度
        rarity = rarity_pool[i % len(rarity_pool)]
        
        # 编号
        nft_num = i + 1
        nft_id = f"NRA-{nft_num:04d}"
        
        # 文件名
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
            "备注": f"Batch 0100 - {series} #{seq}",
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
    print("  100张拼装计划统计")
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
    for b, c in sorted(base_counts.items()):
        print(f"  {b}: {c}次")
    
    print(f"\n📊 印章使用:")
    for st, c in sorted(stamp_counts.items()):
        print(f"  {st}: {c}次")
    
    print(f"\n📊 稀有度分布:")
    for r, c in sorted(rarity_counts.items()):
        print(f"  {r}: {c}张")
    
    print(f"\n{'='*60}")


def main():
    output_path = os.path.join(SCRIPT_DIR, "data", "auto_compose_plan_0100.csv")
    
    print("Generating 100-image composition plan...")
    rows = generate_plan(n=100, seed=42)
    
    write_csv(rows, output_path)
    print_summary(rows)


if __name__ == "__main__":
    main()
