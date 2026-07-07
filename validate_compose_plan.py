#!/usr/bin/env python3
"""
validate_compose_plan.py
NO REFUNDS ARCHIVE - Compose Plan Validator

Validates a compose plan CSV against strict series matching rules.
Checks:
  1. Series-stamp match
  2. Series-handwritten match
  3. Series-prop1 match
  4. Series-prop2 match
  5. Series-damage match
  6. Series-overlay match
  7. Image file existence
  8. Metadata file existence
  9. Metadata trait consistency with CSV
  10. Base template suitability (optional)

Output: data/compose_plan_validation_report.csv
"""

import csv
import json
import os
import sys
import io
import argparse

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ══════════════════════════════════════════════════════════════
# 系列严格匹配规则 (与 generate_plan_0100.py 保持一致)
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
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
            "PROP_NAPKIN_01", "PROP_RECEIPT_CLIP_01",
            "PROP_SPOON_01", "PROP_SUGAR_PACKET_01", "PROP_COFFEE_STIRRER_01",
            "PROP_MATCHBOOK_01", "PROP_DINER_MENU_SCRAP_01",
            "PROP_TABLE_TICKET_01", "PROP_TABLE_TICKET_02",
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
            "OVERLAY_ARCHIVE_YELLOWING_01", "OVERLAY_SOFT_VIGNETTE_01", "OVERLAY_FADED_INK_01",
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
            "PROP_VHS_LABEL_01", "PROP_RENTAL_CARD_01",
            "PROP_REWIND_STICKER_01", "PROP_LATE_FEE_SLIP_01", "PROP_MEMBERSHIP_CARD_01",
            "PROP_VIDEO_CASE_CORNER_01", "PROP_RETURN_SLOT_TAG_01",
            "PROP_TAPE_SPINE_LABEL_01", "PROP_STORE_TAG_01", "PROP_PLASTIC_TAB_01",
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
            "STAMP_ROOM_PAID", "STAMP_CLOSED", "STAMP_NO_VACANCY", "STAMP_PAID_CASH",
        ],
        "handwritten": [
            "NOTE_NO_VACANCY", "NOTE_ROOM_8", "NOTE_1138PM", "NOTE_EXIT_22", "NOTE_PAID_CASH",
        ],
        "props": [
            "PROP_MOTEL_KEY_01", "PROP_MAP_SCRAP_01",
            "PROP_ROOM_TAG_01", "PROP_GAS_STATION_TOKEN_01", "PROP_PARKING_STUB_01",
            "PROP_MATCHBOOK_MOTEL_01", "PROP_POSTCARD_CORNER_01", "PROP_ROAD_EXIT_NOTE_01",
            "PROP_KEYCHAIN_01", "PROP_PAYPHONE_CARD_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
        ],
        "damages": [
            "DMG_WATER_STAIN_01", "DMG_WATER_STAIN_02", "DMG_WATER_STAIN_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_SMALL_TEAR_01", "DMG_CORNER_CURL_01",
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
            "STAMP_LAST_COPY", "STAMP_FINAL_SALE", "STAMP_STORE_CREDIT",
        ],
        "handwritten": [
            "NOTE_SIDE_B", "NOTE_LAST_COPY", "NOTE_A_SIDE_GONE", "NOTE_TRACK_07", "NOTE_STORE_CREDIT",
        ],
        "props": [
            "PROP_CASSETTE_01", "PROP_CATALOG_CARD_01",
            "PROP_VINYL_LABEL_01", "PROP_PRICE_STICKER_01", "PROP_USED_TAPE_TAG_01",
            "PROP_TRACKLIST_SCRAP_01", "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_STORE_CREDIT_SLIP_01", "PROP_B_SIDE_NOTE_01", "PROP_PLASTIC_SLEEVE_01",
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
            "STAMP_FINAL_SALE", "STAMP_NO_REFUNDS", "STAMP_CLOSED",
        ],
        "handwritten": [
            "NOTE_LAST_SHIFT", "NOTE_AISLE_3", "NOTE_512PM", "NOTE_FINAL_SALE", "NOTE_REGISTER_2",
        ],
        "props": [
            "PROP_PRICE_TAG_01", "PROP_CANDY_WRAPPER_01", "PROP_BOTTLE_CAP_01",
            "PROP_LOTTERY_STUB_01",
            "PROP_COUPON_SCRAP_01", "PROP_COUPON_SCRAP_02",
            "PROP_PLASTIC_STRAW_WRAPPER_01", "PROP_AISLE_TAG_01",
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
            "OVERLAY_ARCHIVE_YELLOWING_01", "OVERLAY_FADED_INK_01",
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
            "PROP_RING_BOX_01", "PROP_BROKEN_WATCH_01",
            "PROP_CLAIM_TICKET_01", "PROP_BRASS_TAG_01", "PROP_OLD_KEY_01",
            "PROP_CHAIN_FRAGMENT_01", "PROP_SMALL_JEWELRY_BAG_01",
            "PROP_CASE_LABEL_01", "PROP_PAWN_STUB_01", "PROP_GLASS_COUNTER_TAG_01",
            "PROP_COIN_01", "PROP_COIN_02", "PROP_COIN_03",
        ],
        "damages": [
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_TAPE_01", "DMG_TAPE_02",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
            "DMG_SMALL_TEAR_01", "DMG_CORNER_CURL_01",
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


def validate_plan(csv_path, check_files=False, output_path=None):
    """Validate a compose plan CSV and generate report."""
    if not os.path.exists(csv_path):
        print(f"✗ CSV not found: {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n{'='*60}")
    print(f"  NO REFUNDS ARCHIVE - Plan Validator v1.0")
    print(f"  CSV: {csv_path}")
    print(f"  Rows: {len(rows)}")
    print(f"  File check: {'ON' if check_files else 'OFF'}")
    print(f"{'='*60}\n")

    errors = []
    warnings = []

    # Validation checks per row
    checks = [
        ("印章素材", "stamps"),
        ("手写素材", "handwritten"),
        ("小物件1", "props"),
        ("小物件2", "props"),
        ("纸张痕迹", "damages"),
        ("叠加滤镜/噪点", "overlays"),
    ]

    for i, row in enumerate(rows):
        nft_id = row.get("编号", f"ROW_{i+1}").strip()
        filename = row.get("最终文件名", "").strip()
        series = row.get("系列", "").strip()

        if series not in SERIES_RULES:
            errors.append({
                "编号": nft_id, "最终文件名": filename, "系列": series,
                "错误字段": "系列", "当前素材": series,
                "错误原因": f"未知系列: {series}",
                "建议替换素材": "检查系列名称拼写",
                "是否需要删除旧图": "是",
            })
            continue

        rules = SERIES_RULES[series]

        for csv_field, rule_key in checks:
            asset_id = row.get(csv_field, "").strip()
            if not asset_id:
                continue

            allowed = rules[rule_key]
            if asset_id not in allowed:
                errors.append({
                    "编号": nft_id,
                    "最终文件名": filename,
                    "系列": series,
                    "错误字段": csv_field,
                    "当前素材": asset_id,
                    "错误原因": f"{asset_id} 不属于 {series} 的允许{rule_key}列表",
                    "建议替换素材": f"建议使用: {', '.join(allowed[:5])}...",
                    "是否需要删除旧图": "是",
                })

        # Check base template suitability
        base_id = row.get("底图变体", "").strip()
        if base_id:
            base_dir = os.path.join(SCRIPT_DIR, "assets", "base_templates")
            base_path = os.path.join(base_dir, f"{base_id}.png")
            if not os.path.exists(base_path):
                for ext in (".jpg", ".jpeg", ".webp"):
                    alt_path = os.path.join(base_dir, f"{base_id}{ext}")
                    if os.path.exists(alt_path):
                        base_path = alt_path
                        break
                else:
                    warnings.append({
                        "编号": nft_id, "最终文件名": filename, "系列": series,
                        "错误字段": "底图变体", "当前素材": base_id,
                        "错误原因": f"底图文件不存在: {base_id}",
                        "建议替换素材": "检查 base_templates/ 目录",
                        "是否需要删除旧图": "",
                    })

        # Check image and metadata existence (only in file-check mode)
        if check_files:
            img_dir = os.path.join(SCRIPT_DIR, "output", "final_images")
            meta_dir = os.path.join(SCRIPT_DIR, "output", "metadata")

            img_path = os.path.join(img_dir, filename)
            if not os.path.exists(img_path):
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "图片文件", "当前素材": filename,
                    "错误原因": "图片文件不存在",
                    "建议替换素材": "重新执行拼装",
                    "是否需要删除旧图": "",
                })

            meta_filename = os.path.splitext(filename)[0] + ".json"
            meta_path = os.path.join(meta_dir, meta_filename)
            if not os.path.exists(meta_path):
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "metadata文件", "当前素材": meta_filename,
                    "错误原因": "metadata文件不存在",
                    "建议替换素材": "重新执行拼装",
                    "是否需要删除旧图": "",
                })
            else:
                # Check metadata trait consistency
                try:
                    with open(meta_path, "r", encoding="utf-8") as mf:
                        meta = json.load(mf)
                    attrs = {a["trait_type"]: a["value"] for a in meta.get("attributes", [])}

                    # Check series
                    csv_series = row.get("系列", "").strip()
                    meta_series = attrs.get("Series", "")
                    if csv_series and meta_series and csv_series != meta_series:
                        errors.append({
                            "编号": nft_id, "最终文件名": filename, "系列": series,
                            "错误字段": "metadata Series", "当前素材": meta_series,
                            "错误原因": f"metadata Series='{meta_series}' 与 CSV='{csv_series}' 不一致",
                            "建议替换素材": "重新生成 metadata",
                            "是否需要删除旧图": "",
                        })

                    # Check stamp
                    csv_stamp = row.get("印章素材", "").strip()
                    meta_stamp = attrs.get("Stamp", "")
                    if csv_stamp and meta_stamp:
                        expected_stamp = csv_stamp.replace("STAMP_", "").replace("_", " ")
                        if expected_stamp != meta_stamp:
                            errors.append({
                                "编号": nft_id, "最终文件名": filename, "系列": series,
                                "错误字段": "metadata Stamp", "当前素材": meta_stamp,
                                "错误原因": f"metadata Stamp='{meta_stamp}' 与 CSV='{csv_stamp}' 不一致",
                                "建议替换素材": "重新生成 metadata",
                                "是否需要删除旧图": "",
                            })

                except Exception as e:
                    errors.append({
                        "编号": nft_id, "最终文件名": filename, "系列": series,
                        "错误字段": "metadata解析", "当前素材": meta_filename,
                        "错误原因": f"无法解析 metadata: {e}",
                        "建议替换素材": "重新生成 metadata",
                        "是否需要删除旧图": "",
                    })

    # ── Write report ──
    if output_path is None:
        output_path = os.path.join(SCRIPT_DIR, "data", "compose_plan_validation_report.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fieldnames = [
        "编号", "最终文件名", "系列", "错误字段", "当前素材",
        "错误原因", "建议替换素材", "是否需要删除旧图",
    ]

    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if errors:
            writer.writerows(errors)
        else:
            writer.writerow({
                "编号": "(无错误)",
                "最终文件名": "",
                "系列": "",
                "错误字段": "",
                "当前素材": "",
                "错误原因": "所有校验通过，无跨系列错误",
                "建议替换素材": "",
                "是否需要删除旧图": "",
            })

    # ── Print summary ──
    print(f"{'─'*60}")
    print(f"  VALIDATION RESULTS")
    print(f"{'─'*60}")
    print(f"  ✗ Errors:   {len(errors)}")
    print(f"  ⚠ Warnings: {len(warnings)}")

    if errors:
        print(f"\n  ❌ CROSS-SERIES ERRORS FOUND:")
        # Group by error type
        from collections import Counter
        error_types = Counter(e["错误字段"] for e in errors)
        for field, count in error_types.most_common():
            print(f"     {field}: {count} errors")
        print(f"\n  Full report: {output_path}")
    else:
        print(f"\n  ✅ ALL CHECKS PASSED - No cross-series violations")
        print(f"  Report: {output_path}")

    if warnings:
        print(f"\n  Warnings:")
        for w in warnings[:5]:
            print(f"     {w['编号']}: {w['错误原因']}")

    print(f"\n{'='*60}")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="NO REFUNDS ARCHIVE - Plan Validator")
    parser.add_argument("--csv", default="data/auto_compose_plan_0100.csv",
                        help="Path to compose plan CSV")
    parser.add_argument("--files", action="store_true",
                        help="Also check image/metadata file existence and metadata consistency")
    parser.add_argument("--output", default=None,
                        help="Output path for validation report CSV")
    args = parser.parse_args()

    csv_path = os.path.join(SCRIPT_DIR, args.csv) if not os.path.isabs(args.csv) else args.csv
    output_path = None
    if args.output:
        output_path = os.path.join(SCRIPT_DIR, args.output) if not os.path.isabs(args.output) else args.output

    ok = validate_plan(csv_path, check_files=args.files, output_path=output_path)

    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
