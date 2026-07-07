#!/usr/bin/env python3
"""
compose_nra_assets.py
NO REFUNDS ARCHIVE - 分层自动拼装系统 v2.0

读取 CSV 拼装计划，按顺序叠加 trait PNG 图层，输出最终 NFT 图片和 metadata JSON。

新功能 (v2.0):
- 素材存在性预检查 (--check)
- 缺失素材报告 (output/missing_assets_report.csv)
- 预览检查表生成 (output/preview_check_0100.csv)
- 批量拼装完成统计

用法:
  python compose_nra_assets.py --csv data/auto_compose_plan_0100.csv --limit 100
  python compose_nra_assets.py --csv data/auto_compose_plan_0100.csv --check  (仅检查)
  python compose_nra_assets.py --csv data/auto_compose_plan_0100.csv            (全部)

拼装顺序:
  1. base_template  底图 (不透明)
  2. paper_damage   纸张痕迹 (透明 PNG)
  3. props          小物件 (透明 PNG)
  4. stamp          印章 (透明 PNG)
  5. handwritten    手写字 (透明 PNG)
  6. overlay        滤镜/噪点 (透明 PNG)
  → 最终导出 PNG
"""

import os
import sys
import csv
import json
import argparse
import io
from typing import Optional

from PIL import Image

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ── 路径配置 ───────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
OUTPUT_IMG_DIR  = os.path.join(SCRIPT_DIR, "output", "final_images")
OUTPUT_META_DIR = os.path.join(SCRIPT_DIR, "output", "metadata")

CANVAS_SIZE = 1024

# ── 素材文件名映射 ─────────────────────────────────────────

STAMP_MAP = {
    "STAMP_AFTER_HOURS":   "stamp_after_hours_red.png",
    "STAMP_CHECKED_OUT":   "stamp_checked_out_red.png",
    "STAMP_CLAIM_CLOSED":  "stamp_claim_closed_red.png",
    "STAMP_CLOSED":        "stamp_closed_red.png",
    "STAMP_DO_NOT_OPEN":   "stamp_do_not_open_red.png",
    "STAMP_DUE_FRIDAY":    "stamp_due_friday_red.png",
    "STAMP_FINAL_SALE":    "stamp_final_sale_red.png",
    "STAMP_LAST_COPY":     "stamp_last_copy_red.png",
    "STAMP_LAST_ORDER":    "stamp_last_order_red.png",
    "STAMP_NO_REFUNDS":    "stamp_no_refunds_red.png",
    "STAMP_NO_VACANCY":    "stamp_no_vacancy_red.png",
    "STAMP_OVERDUE":       "stamp_overdue_red.png",
    "STAMP_PAID_CASH":     "stamp_paid_cash_red.png",
    "STAMP_PAWN_HOLD":     "stamp_pawn_hold_red.png",
    "STAMP_RETURNED_EMPTY":"stamp_returned_empty_red.png",
    "STAMP_ROOM_PAID":     "stamp_room_paid_red.png",
    "STAMP_STORE_CREDIT":  "stamp_store_credit_red.png",
    "STAMP_UNCLAIMED":     "stamp_unclaimed_red.png",
}

HANDWRITTEN_MAP = {
    "NOTE_1138PM":          "note_1138pm.png",
    "NOTE_30_DAYS":         "note_30_days.png",
    "NOTE_512PM":           "note_512pm.png",
    "NOTE_AISLE_3":         "note_aisle_3.png",
    "NOTE_A_SIDE_GONE":     "note_a_side_gone.png",
    "NOTE_BOOTH_4":         "note_booth_4.png",
    "NOTE_CASE_14":         "note_case_14.png",
    "NOTE_CLAIM_BY_5":      "note_claim_by_5.png",
    "NOTE_DUE_FRIDAY":      "note_due_friday.png",
    "NOTE_EXIT_22":         "note_exit_22.png",
    "NOTE_FINAL_SALE":      "note_final_sale.png",
    "NOTE_HOLD_TAG":        "note_hold_tag.png",
    "NOTE_LAST_COPY":       "note_last_copy.png",
    "NOTE_LAST_NIGHT":      "note_last_night.png",
    "NOTE_LAST_ORDER":      "note_last_order.png",
    "NOTE_LAST_SHIFT":      "note_last_shift.png",
    "NOTE_LATE_FEE":        "note_late_fee.png",
    "NOTE_NO_VACANCY":      "note_no_vacancy.png",
    "NOTE_PAID_CASH":       "note_paid_cash.png",
    "NOTE_REGISTER_2":      "note_register_2.png",
    "NOTE_RETURNED_EMPTY":  "note_returned_empty.png",
    "NOTE_REWIND":          "note_rewind.png",
    "NOTE_ROOM_8":          "note_room_8.png",
    "NOTE_SERVER_M":        "note_server_m.png",
    "NOTE_SIDE_B":          "note_side_b.png",
    "NOTE_STORE_CREDIT":    "note_store_credit.png",
    "NOTE_TABLE_6":         "note_table_6.png",
    "NOTE_TAPE_12":         "note_tape_12.png",
    "NOTE_TRACK_07":        "note_track_07.png",
    "NOTE_UNCLAIMED":       "note_unclaimed.png",
}

PROP_MAP = {
    "PROP_AISLE_TAG_01":           "prop_aisle_tag_01.png",
    "PROP_BOTTLE_CAP_01":          "prop_bottle_cap_01.png",
    "PROP_BRASS_TAG_01":           "prop_brass_tag_01.png",
    "PROP_BROKEN_WATCH_01":        "prop_broken_watch_01.png",
    "PROP_B_SIDE_NOTE_01":         "prop_b_side_note_01.png",
    "PROP_CANDY_WRAPPER_01":       "prop_candy_wrapper_01.png",
    "PROP_CASE_LABEL_01":          "prop_case_label_01.png",
    "PROP_CASSETTE_01":            "prop_cassette_01.png",
    "PROP_CATALOG_CARD_01":        "prop_catalog_card_01.png",
    "PROP_CHAIN_FRAGMENT_01":      "prop_chain_fragment_01.png",
    "PROP_CLAIM_TICKET_01":        "prop_claim_ticket_01.png",
    "PROP_COFFEE_STIRRER_01":      "prop_coffee_stirrer_01.png",
    "PROP_COIN_01":                "prop_coin_01.png",
    "PROP_COIN_02":                "prop_coin_02.png",
    "PROP_COIN_03":                "prop_coin_03.png",
    "PROP_COUPON_SCRAP_01":        "prop_coupon_scrap_01.png",
    "PROP_COUPON_SCRAP_02":        "prop_coupon_scrap_02.png",
    "PROP_DINER_MENU_SCRAP_01":    "prop_diner_menu_scrap_01.png",
    "PROP_GAS_STATION_TOKEN_01":   "prop_gas_station_token_01.png",
    "PROP_GLASS_COUNTER_TAG_01":   "prop_glass_counter_tag_01.png",
    "PROP_KEYCHAIN_01":            "prop_keychain_01.png",
    "PROP_LATE_FEE_SLIP_01":       "prop_late_fee_slip_01.png",
    "PROP_LOTTERY_STUB_01":        "prop_lottery_stub_01.png",
    "PROP_MAP_SCRAP_01":           "prop_map_scrap_01.png",
    "PROP_MATCHBOOK_01":           "prop_matchbook_01.png",
    "PROP_MATCHBOOK_MOTEL_01":     "prop_matchbook_motel_01.png",
    "PROP_MEMBERSHIP_CARD_01":     "prop_membership_card_01.png",
    "PROP_MOTEL_KEY_01":           "prop_motel_key_01.png",
    "PROP_NAPKIN_01":              "prop_napkin_01.png",
    "PROP_OLD_KEY_01":             "prop_old_key_01.png",
    "PROP_PARKING_STUB_01":        "prop_parking_stub_01.png",
    "PROP_PAWN_STUB_01":           "prop_pawn_stub_01.png",
    "PROP_PAYPHONE_CARD_01":       "prop_payphone_card_01.png",
    "PROP_PLASTIC_SLEEVE_01":      "prop_plastic_sleeve_01.png",
    "PROP_PLASTIC_STRAW_WRAPPER_01":"prop_plastic_straw_wrapper_01.png",
    "PROP_PLASTIC_TAB_01":         "prop_plastic_tab_01.png",
    "PROP_POSTCARD_CORNER_01":     "prop_postcard_corner_01.png",
    "PROP_PRICE_STICKER_01":       "prop_price_sticker_01.png",
    "PROP_PRICE_TAG_01":           "prop_price_tag_01.png",
    "PROP_RECEIPT_CLIP_01":        "prop_receipt_clip_01.png",
    "PROP_RECORD_SLEEVE_CORNER_01":"prop_record_sleeve_corner_01.png",
    "PROP_REGISTER_TAPE_SCRAP_01": "prop_register_tape_scrap_01.png",
    "PROP_RENTAL_CARD_01":         "prop_rental_card_01.png",
    "PROP_RETURN_SLOT_TAG_01":     "prop_return_slot_tag_01.png",
    "PROP_REWIND_STICKER_01":      "prop_rewind_sticker_01.png",
    "PROP_RING_BOX_01":            "prop_ring_box_01.png",
    "PROP_ROAD_EXIT_NOTE_01":      "prop_road_exit_note_01.png",
    "PROP_ROOM_TAG_01":            "prop_room_tag_01.png",
    "PROP_SMALL_JEWELRY_BAG_01":   "prop_small_jewelry_bag_01.png",
    "PROP_SPOON_01":               "prop_spoon_01.png",
    "PROP_STORE_CREDIT_SLIP_01":   "prop_store_credit_slip_01.png",
    "PROP_STORE_TAG_01":           "prop_store_tag_01.png",
    "PROP_SUGAR_PACKET_01":        "prop_sugar_packet_01.png",
    "PROP_TABLE_TICKET_01":        "prop_table_ticket_01.png",
    "PROP_TABLE_TICKET_02":        "prop_table_ticket_02.png",
    "PROP_TAPE_SPINE_LABEL_01":    "prop_tape_spine_label_01.png",
    "PROP_TRACKLIST_SCRAP_01":     "prop_tracklist_scrap_01.png",
    "PROP_USED_TAPE_TAG_01":       "prop_used_tape_tag_01.png",
    "PROP_VHS_LABEL_01":           "prop_vhs_label_01.png",
    "PROP_VIDEO_CASE_CORNER_01":   "prop_video_case_corner_01.png",
    "PROP_VINYL_LABEL_01":         "prop_vinyl_label_01.png",
}

DAMAGE_MAP = {
    "DMG_COFFEE_RING_01":  "damage_coffee_ring_01.png",
    "DMG_COFFEE_RING_02":  "damage_coffee_ring_02.png",
    "DMG_COFFEE_RING_03":  "damage_coffee_ring_03.png",
    "DMG_CORNER_CURL_01":  "damage_corner_curl_01.png",
    "DMG_DUST_SPECKS_01":  "damage_dust_specks_01.png",
    "DMG_DUST_SPECKS_02":  "damage_dust_specks_02.png",
    "DMG_EDGE_WEAR_01":    "damage_edge_wear_01.png",
    "DMG_EDGE_WEAR_02":    "damage_edge_wear_02.png",
    "DMG_FOLD_01":         "damage_fold_01.png",
    "DMG_FOLD_02":         "damage_fold_02.png",
    "DMG_FOLD_03":         "damage_fold_03.png",
    "DMG_SCAN_NOISE_01":   "damage_scan_noise_01.png",
    "DMG_SCAN_NOISE_02":   "damage_scan_noise_02.png",
    "DMG_SMALL_TEAR_01":   "damage_small_tear_01.png",
    "DMG_TAPE_01":         "damage_tape_01.png",
    "DMG_TAPE_02":         "damage_tape_02.png",
    "DMG_THERMAL_FADE_01": "damage_thermal_fade_01.png",
    "DMG_WATER_STAIN_01":  "damage_water_stain_01.png",
    "DMG_WATER_STAIN_02":  "damage_water_stain_02.png",
    "DMG_WATER_STAIN_03":  "damage_water_stain_03.png",
}

OVERLAY_MAP = {
    "OVERLAY_ARCHIVE_YELLOWING_01": "overlay_archive_yellowing_01.png",
    "OVERLAY_CRT_GRAIN_01":        "overlay_crt_grain_01.png",
    "OVERLAY_CRT_GRAIN_02":        "overlay_crt_grain_02.png",
    "OVERLAY_DUST_01":             "overlay_dust_01.png",
    "OVERLAY_DUST_02":             "overlay_dust_02.png",
    "OVERLAY_FADED_INK_01":        "overlay_faded_ink_01.png",
    "OVERLAY_FILM_GRAIN_01":       "overlay_film_grain_01.png",
    "OVERLAY_FILM_GRAIN_02":       "overlay_film_grain_02.png",
    "OVERLAY_GLASS_GLARE_01":      "overlay_glass_glare_01.png",
    "OVERLAY_GLASS_GLARE_02":      "overlay_glass_glare_02.png",
    "OVERLAY_RAIN_GLOW_01":        "overlay_rain_glow_01.png",
    "OVERLAY_RAIN_GLOW_02":        "overlay_rain_glow_02.png",
    "OVERLAY_SCAN_NOISE_01":       "overlay_scan_noise_01.png",
    "OVERLAY_SCAN_NOISE_02":       "overlay_scan_noise_02.png",
    "OVERLAY_SOFT_VIGNETTE_01":    "overlay_soft_vignette_01.png",
}


# ── 辅助函数 ───────────────────────────────────────────────

def load_image(path: str, size: tuple = (CANVAS_SIZE, CANVAS_SIZE)) -> Optional[Image.Image]:
    """Load an image, convert to RGBA, resize to target size. Returns None on failure."""
    if not os.path.exists(path):
        return None
    try:
        img = Image.open(path).convert("RGBA")
        if img.size != size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"  ⚠ Failed to load {path}: {e}")
        return None


def resolve_base_template(base_id: str) -> Optional[str]:
    """Resolve a base template ID to a file path."""
    base_dir = os.path.join(ASSETS_DIR, "base_templates")

    # 1. Exact match
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        var_path = os.path.join(base_dir, f"{base_id}{ext}")
        if os.path.exists(var_path):
            return var_path

    # 2. Fallback: B0X_VAR_XX -> B0X_VAR_01
    base_type = base_id.split("_")[0]
    fallback_id = f"{base_type}_VAR_01"
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        fallback_path = os.path.join(base_dir, f"{fallback_id}{ext}")
        if os.path.exists(fallback_path):
            print(f"  ⚠ {base_id} not found, using fallback: {fallback_id}")
            return fallback_path

    return None


def resolve_asset(asset_id: str, category: str) -> Optional[str]:
    """Resolve a trait asset ID to a file path."""
    map_dict = {
        "stamp":       (STAMP_MAP,       "stamps"),
        "handwritten": (HANDWRITTEN_MAP, "handwritten"),
        "prop":        (PROP_MAP,        "props"),
        "damage":      (DAMAGE_MAP,      "damage"),
        "overlay":     (OVERLAY_MAP,     "overlays"),
    }

    if category not in map_dict:
        return None

    mapping, subdir = map_dict[category]
    filename = mapping.get(asset_id.strip())
    if not filename:
        return None

    return os.path.join(ASSETS_DIR, subdir, filename)


def check_asset_exists(asset_id: str, category: str) -> tuple:
    """Check if an asset exists on disk. Returns (asset_id, filename, exists, path)."""
    if not asset_id or not asset_id.strip():
        return (asset_id, "", True, "")

    if category == "base":
        path = resolve_base_template(asset_id.strip())
        if path and os.path.exists(path):
            return (asset_id, os.path.basename(path), True, path)
        return (asset_id, f"{asset_id.strip()}.png", False, "")

    path = resolve_asset(asset_id.strip(), category)
    if path and os.path.exists(path):
        return (asset_id, os.path.basename(path), True, path)

    # Try to get expected filename from mapping
    map_dict = {
        "stamp": STAMP_MAP,
        "handwritten": HANDWRITTEN_MAP,
        "prop": PROP_MAP,
        "damage": DAMAGE_MAP,
        "overlay": OVERLAY_MAP,
    }
    expected_file = map_dict.get(category, {}).get(asset_id.strip(), f"{asset_id.strip()}.png")
    return (asset_id, expected_file, False, "")


def precheck_assets(rows: list) -> list:
    """Pre-check all assets in CSV rows. Returns list of missing asset reports."""
    missing_reports = []

    layer_checks = [
        ("底图变体",       "base"),
        ("印章素材",       "stamp"),
        ("手写素材",       "handwritten"),
        ("小物件1",        "prop"),
        ("小物件2",        "prop"),
        ("纸张痕迹",       "damage"),
        ("叠加滤镜/噪点",  "overlay"),
    ]

    for row in rows:
        nft_id = row.get("编号", "").strip()
        filename = row.get("最终文件名", "").strip()

        for field, category in layer_checks:
            asset_id = row.get(field, "").strip()
            if not asset_id:
                continue

            aid, fname, exists, path = check_asset_exists(asset_id, category)
            if not exists:
                suggestion = ""
                if category == "stamp" and asset_id in STAMP_MAP:
                    suggestion = f"已映射到 {STAMP_MAP[asset_id]}，检查 stamps/ 目录"
                elif category == "base":
                    suggestion = f"检查 base_templates/ 目录是否存在变体文件"
                else:
                    suggestion = f"检查 {category}/ 目录"

                missing_reports.append({
                    "编号": nft_id,
                    "最终文件名": filename,
                    "缺失素材字段": field,
                    "缺失素材名": asset_id,
                    "建议处理方式": suggestion,
                })

    return missing_reports


def write_missing_report(missing_reports: list, output_path: str):
    """Write missing assets report CSV."""
    fieldnames = ["编号", "最终文件名", "缺失素材字段", "缺失素材名", "建议处理方式"]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if missing_reports:
            writer.writerows(missing_reports)
        else:
            writer.writerow({
                "编号": "(无缺失)",
                "最终文件名": "",
                "缺失素材字段": "",
                "缺失素材名": "",
                "建议处理方式": "所有素材文件均存在，无需处理",
            })
    print(f"\n📋 Missing assets report: {output_path}")
    print(f"   Missing entries: {len(missing_reports)}")


def compose_image(row: dict) -> Optional[Image.Image]:
    """Compose a single NFT image from a CSV row."""
    base_id = row.get("底图变体", "").strip()
    base_path = resolve_base_template(base_id)

    if not base_path:
        print(f"  ✗ Base template not found: {base_id}")
        return None

    # 1. Load base template
    base = load_image(base_path)
    if base is None:
        print(f"  ✗ Failed to load base: {base_path}")
        return None

    print(f"  ✓ Base: {base_id} ({os.path.basename(base_path)})")

    # Start composition on a fresh RGBA canvas
    canvas = Image.new("RGBA", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0, 0))
    canvas.paste(base, (0, 0), base)

    # Define layer stacking order (2-6)
    layers = [
        ("纸张痕迹",     "damage",      "Damage"),
        ("小物件1",      "prop",        "Prop 1"),
        ("小物件2",      "prop",        "Prop 2"),
        ("印章素材",     "stamp",       "Stamp"),
        ("手写素材",     "handwritten", "Handwritten"),
        ("叠加滤镜/噪点", "overlay",     "Overlay"),
    ]

    for csv_field, category, label in layers:
        asset_id = row.get(csv_field, "").strip()
        if not asset_id:
            continue

        asset_path = resolve_asset(asset_id, category)
        if not asset_path or not os.path.exists(asset_path):
            print(f"  ⚠ {label}: {asset_id} → file not found, skipping")
            continue

        layer = load_image(asset_path)
        if layer is None:
            continue

        canvas.paste(layer, (0, 0), layer)
        print(f"  ✓ {label}: {asset_id}")

    return canvas


def generate_metadata(row: dict, image_filename: str) -> dict:
    """Generate metadata JSON from a CSV row."""
    attributes = []

    series = row.get("系列", "").strip()
    if series:
        attributes.append({"trait_type": "Series", "value": series})

    base = row.get("底图变体", "").strip()
    if base:
        attributes.append({"trait_type": "Base Template", "value": base})

    stamp = row.get("印章素材", "").strip()
    if stamp:
        stamp_label = stamp.replace("STAMP_", "").replace("_", " ")
        attributes.append({"trait_type": "Stamp", "value": stamp_label})

    note = row.get("手写素材", "").strip()
    if note:
        note_label = note.replace("NOTE_", "").replace("_", " ")
        attributes.append({"trait_type": "Handwritten Note", "value": note_label})

    prop1 = row.get("小物件1", "").strip()
    if prop1:
        attributes.append({"trait_type": "Prop 1", "value": prop1})

    prop2 = row.get("小物件2", "").strip()
    if prop2:
        attributes.append({"trait_type": "Prop 2", "value": prop2})

    damage = row.get("纸张痕迹", "").strip()
    if damage:
        attributes.append({"trait_type": "Paper Damage", "value": damage})

    overlay = row.get("叠加滤镜/噪点", "").strip()
    if overlay:
        attributes.append({"trait_type": "Overlay", "value": overlay})

    rarity = row.get("稀有度", "").strip()
    if rarity:
        attributes.append({"trait_type": "Rarity", "value": rarity})

    nft_number = row.get("编号", "").strip()
    name = f"NO REFUNDS ARCHIVE #{nft_number.replace('NRA-', '')}" if nft_number else "NO REFUNDS ARCHIVE"

    return {
        "name": name,
        "description": f"A layered archival receipt NFT from NO REFUNDS ARCHIVE. Series: {series}. Composed from base template + stamp + handwritten + props + damage + overlay layers.",
        "image": image_filename,
        "attributes": attributes,
        "compilation": {
            "series": series,
            "base_template": base,
            "rarity": rarity,
        }
    }


def generate_preview_check(rows: list, output_path: str):
    """Generate preview check CSV after composition."""
    fieldnames = [
        "编号", "最终文件名", "系列", "底图变体", "印章素材", "手写素材",
        "小物件1", "小物件2", "纸张痕迹", "滤镜", "稀有度",
        "图片是否生成", "metadata是否生成", "需要人工复查", "备注",
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            nft_id = row.get("编号", "").strip()
            filename = row.get("最终文件名", "").strip()

            img_exists = os.path.exists(os.path.join(OUTPUT_IMG_DIR, filename))
            meta_filename = os.path.splitext(filename)[0] + ".json"
            meta_exists = os.path.exists(os.path.join(OUTPUT_META_DIR, meta_filename))

            need_review = "否"
            if not img_exists or not meta_exists:
                need_review = "是"

            writer.writerow({
                "编号": nft_id,
                "最终文件名": filename,
                "系列": row.get("系列", ""),
                "底图变体": row.get("底图变体", ""),
                "印章素材": row.get("印章素材", ""),
                "手写素材": row.get("手写素材", ""),
                "小物件1": row.get("小物件1", ""),
                "小物件2": row.get("小物件2", ""),
                "纸张痕迹": row.get("纸张痕迹", ""),
                "滤镜": row.get("叠加滤镜/噪点", ""),
                "稀有度": row.get("稀有度", ""),
                "图片是否生成": "是" if img_exists else "否",
                "metadata是否生成": "是" if meta_exists else "否",
                "需要人工复查": need_review,
                "备注": row.get("备注", ""),
            })

    print(f"\n📋 Preview check: {output_path}")


def process_csv(csv_path: str, limit: int = None, check_only: bool = False, preview_csv: str = None):
    """Main processing function."""
    os.makedirs(OUTPUT_IMG_DIR, exist_ok=True)
    os.makedirs(OUTPUT_META_DIR, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"✗ CSV not found: {csv_path}")
        sys.exit(1)

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if limit:
        rows = rows[:limit]

    print(f"\n{'='*60}")
    print(f"  NO REFUNDS ARCHIVE - Asset Composer v2.0")
    print(f"  CSV: {csv_path}")
    print(f"  Processing {len(rows)} row(s)")
    print(f"{'='*60}\n")

    # ── Step 1: Pre-check assets ──
    print("🔍 Phase 1: Asset existence check...")
    missing_reports = precheck_assets(rows)

    missing_csv = os.path.join(SCRIPT_DIR, "output", "missing_assets_report.csv")
    write_missing_report(missing_reports, missing_csv)

    if missing_reports:
        print(f"\n⚠ WARNING: {len(missing_reports)} missing asset(s) found!")
        for mr in missing_reports[:10]:
            print(f"  - {mr['编号']}: {mr['缺失素材字段']} → {mr['缺失素材名']}")
        if len(missing_reports) > 10:
            print(f"  ... and {len(missing_reports) - 10} more")
        print(f"  Full report: {missing_csv}")

    if check_only:
        print("\n✓ Check-only mode. No images composed.")
        if preview_csv:
            generate_preview_check(rows, preview_csv)
        return

    # ── Step 2: Compose images ──
    print(f"\n🎨 Phase 2: Composing {len(rows)} image(s)...")
    success_count = 0
    fail_count = 0
    skipped_count = 0

    for i, row in enumerate(rows):
        nft_id = row.get("编号", f"ROW_{i+1}").strip()
        filename = row.get("最终文件名", f"NRA_unknown_{i+1:04d}.png").strip()
        status = row.get("拼装状态", "").strip()

        print(f"\n[{i+1}/{len(rows)}] {nft_id} → {filename}")

        if status in ("已完成", "已拼装"):
            print(f"  ↳ Already completed, skipping")
            skipped_count += 1
            continue

        # Compose
        image = compose_image(row)
        if image is None:
            print(f"  ✗ FAILED to compose {nft_id}")
            fail_count += 1
            continue

        # Save image
        img_path = os.path.join(OUTPUT_IMG_DIR, filename)
        final = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), (0, 0, 0))
        final.paste(image, (0, 0), image)
        final.save(img_path, "PNG", optimize=True)
        print(f"  ✓ Image saved: {img_path}")

        # Generate and save metadata
        metadata = generate_metadata(row, filename)
        meta_filename = os.path.splitext(filename)[0] + ".json"
        meta_path = os.path.join(OUTPUT_META_DIR, meta_filename)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Metadata saved: {meta_path}")

        success_count += 1

    # ── Step 3: Generate preview check ──
    print(f"\n📊 Phase 3: Generating preview check...")
    if preview_csv:
        generate_preview_check(rows, preview_csv)
    else:
        # Default preview check path based on CSV name
        base_name = os.path.splitext(os.path.basename(csv_path))[0]
        preview_path = os.path.join(SCRIPT_DIR, "output", f"preview_check_{base_name.replace('auto_compose_plan_', '')}.csv")
        generate_preview_check(rows, preview_path)

    # ── Summary ──
    print(f"\n{'='*60}")
    print(f"  COMPOSITION COMPLETE")
    print(f"  ✓ Success:  {success_count}")
    print(f"  ✗ Failed:   {fail_count}")
    print(f"  ↳ Skipped:  {skipped_count}")
    print(f"  Total:      {len(rows)}")
    print(f"  Images:     {OUTPUT_IMG_DIR}")
    print(f"  Metadata:   {OUTPUT_META_DIR}")
    print(f"  Missing rpt:{missing_csv}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="NO REFUNDS ARCHIVE - Layered Asset Composer v2.0"
    )
    parser.add_argument(
        "--csv",
        default="data/auto_compose_plan.csv",
        help="Path to composition plan CSV"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of rows to process (default: all)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only check asset existence, do not compose"
    )
    parser.add_argument(
        "--preview",
        default=None,
        help="Output path for preview check CSV"
    )

    args = parser.parse_args()
    csv_path = os.path.join(SCRIPT_DIR, args.csv) if not os.path.isabs(args.csv) else args.csv

    preview_csv = None
    if args.preview:
        preview_csv = os.path.join(SCRIPT_DIR, args.preview) if not os.path.isabs(args.preview) else args.preview

    process_csv(csv_path, args.limit, args.check, preview_csv)


if __name__ == "__main__":
    main()
