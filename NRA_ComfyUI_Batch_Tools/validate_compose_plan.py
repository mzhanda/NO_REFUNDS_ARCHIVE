#!/usr/bin/env python3
"""
validate_compose_plan.py
NO REFUNDS ARCHIVE - Compose Plan Validator v2.0

Validates a compose plan CSV against strict series matching rules and rarity rules.

v2.0 更新:
- 新增 material_pattern 和 legendary_accent 字段校验
- 稀有度与高级 trait 匹配校验
- Common 不应出现 legendary_accent
- Legendary / Ultra Rare 必须有高级 trait
- 图片文件 + metadata 文件存在性检查
- metadata 内容一致性检查

Checks:
  1. Series-stamp match
  2. Series-handwritten match
  3. Series-prop1 match
  4. Series-prop2 match
  5. Series-damage match
  6. Series-overlay match
  7. Series-material_pattern match
  8. Series-legendary_accent match
  9. Rarity vs advanced trait match
  10. Common should NOT have legendary_accent
  11. Legendary/Ultra Rare MUST have advanced traits
  12. Image file existence
  13. Metadata file existence
  14. Metadata trait consistency with CSV

Output: data/compose_plan_validation_report_v2.csv
"""

import csv
import json
import os
import sys
import io
import argparse
from collections import Counter

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
            # Gold stamps also allowed for high rarity
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
        ],
        "handwritten": [
            "NOTE_LAST_NIGHT", "NOTE_TABLE_6", "NOTE_1138PM", "NOTE_LAST_ORDER", "NOTE_BOOTH_4",
        ],
        "props": [
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
            "PROP_CLOTH_NAPKIN_01", "PROP_SPOON_01",
            "PROP_SUGAR_PACKET_01", "PROP_COFFEE_STIRRER_01",
            "PROP_MATCHBOOK_01", "PROP_DINER_CHECK_01",
            "PROP_CORKSCREW_01", "PROP_BOTTLE_OPENER_01",
            "PROP_FORK_01", "PROP_SHOT_GLASS_01", "PROP_WHISKEY_BOTTLE_01",
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
            "OVERLAY_ARCHIVE_YELLOWING_01", "OVERLAY_SOFT_VIGNETTE_01",
            "OVERLAY_FADED_INK_01",
            # Legendary overlays (allowed for high rarity)
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },

    "Night Owl Video": {
        "stamps": [
            "STAMP_CHECKED_OUT", "STAMP_OVERDUE", "STAMP_NO_REFUNDS", "STAMP_DO_NOT_OPEN",
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
        ],
        "handwritten": [
            "NOTE_REWIND", "NOTE_LATE_FEE", "NOTE_RETURNED_EMPTY", "NOTE_DUE_FRIDAY", "NOTE_TAPE_12",
        ],
        "props": [
            "PROP_REWIND_STICKER_01", "PROP_BARCODE_STICKER_01",
            "PROP_PRICE_STICKER_01", "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_VINYL_LABEL_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
            "PROP_POCKET_KNIFE_01", "PROP_VINTAGE_GLASSES_01",
            "PROP_VINTAGE_LIGHTER_01", "PROP_ZIPPO_LIGHTER_01",
            "PROP_VINTAGE_BADGE_01", "PROP_MAGNIFYING_GLASS_01",
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
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },

    "Lucky 8 Gas & Motel": {
        "stamps": [
            "STAMP_ROOM_PAID", "STAMP_CLOSED", "STAMP_NO_VACANCY", "STAMP_PAID_CASH",
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
        ],
        "handwritten": [
            "NOTE_NO_VACANCY", "NOTE_ROOM_8", "NOTE_1138PM", "NOTE_EXIT_22", "NOTE_PAID_CASH",
        ],
        "props": [
            "PROP_OLD_KEY_01", "PROP_OLD_KEY_02", "PROP_OLD_KEY_03",
            "PROP_KEYCHAIN_01", "PROP_GAS_STATION_TOKEN_01",
            "PROP_MATCHBOOK_MOTEL_01", "PROP_POSTAGE_STAMP_01",
            "PROP_NEWSPAPER_CLIP_01",
            "PROP_CIGARETTE_01", "PROP_CIGARETTE_02",
            "PROP_ASHTRAY_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_WATER_STAIN_01", "DMG_WATER_STAIN_02", "DMG_WATER_STAIN_03",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_SMALL_TEAR_01", "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SOFT_VIGNETTE_01",
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },

    "Side B Records": {
        "stamps": [
            "STAMP_LAST_COPY", "STAMP_FINAL_SALE", "STAMP_STORE_CREDIT",
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
        ],
        "handwritten": [
            "NOTE_SIDE_B", "NOTE_LAST_COPY", "NOTE_A_SIDE_GONE", "NOTE_TRACK_07", "NOTE_STORE_CREDIT",
        ],
        "props": [
            "PROP_VINYL_LABEL_01", "PROP_PRICE_STICKER_01",
            "PROP_RECORD_SLEEVE_CORNER_01",
            "PROP_COMPASS_01", "PROP_DICE_01",
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
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },

    "Sunset Mart": {
        "stamps": [
            "STAMP_FINAL_SALE", "STAMP_NO_REFUNDS", "STAMP_CLOSED",
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
        ],
        "handwritten": [
            "NOTE_LAST_SHIFT", "NOTE_AISLE_3", "NOTE_512PM", "NOTE_FINAL_SALE", "NOTE_REGISTER_2",
        ],
        "props": [
            "PROP_CANDY_WRAPPER_01", "PROP_BOTTLE_CAP_01",
            "PROP_SMALL_BOTTLE_01", "PROP_PLASTIC_STRAW_01",
            "PROP_SUGAR_PACKET_01",
            "PROP_SAFETY_RAZOR_01",
            "PROP_VINTAGE_COMB_01", "PROP_HAIR_CLIP_01",
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
            "OVERLAY_ARCHIVE_YELLOWING_01", "OVERLAY_FADED_INK_01",
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },

    "Token Pawn": {
        "stamps": [
            "STAMP_CLAIM_CLOSED", "STAMP_PAWN_HOLD", "STAMP_UNCLAIMED",
            "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD", "STAMP_ARCHIVED_FOREVER_GOLD",
            "STAMP_ULTRA_RARE_GOLD", "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
            "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
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
            "PROP_BROOCH_01", "PROP_VINTAGE_MEDAL_01",
            "PROP_PADLOCK_01",
            "PROP_VINTAGE_COIN_01", "PROP_VINTAGE_COIN_02", "PROP_VINTAGE_COIN_03",
        ],
        "damages": [
            "DMG_EDGE_WEAR_01", "DMG_EDGE_WEAR_02",
            "DMG_TAPE_01", "DMG_TAPE_02",
            "DMG_FOLD_01", "DMG_FOLD_02", "DMG_FOLD_03",
            "DMG_DUST_SPECKS_01", "DMG_DUST_SPECKS_02",
            "DMG_SMALL_TEAR_01", "DMG_CORNER_CURL_01",
        ],
        "overlays": [
            "OVERLAY_DUST_01", "OVERLAY_DUST_02",
            "OVERLAY_SCAN_NOISE_01", "OVERLAY_SCAN_NOISE_02",
            "OVERLAY_FILM_GRAIN_01", "OVERLAY_FILM_GRAIN_02",
            "OVERLAY_ARCHIVE_YELLOWING_01",
            "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
            "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
            "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
            "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
        ],
    },
}

# Global pools for cross-series validation
ALL_MATERIALS = [
    "MAT_TRANSPARENT_RECEIPT_01", "MAT_FROSTED_RECEIPT_01",
    "MAT_HOLOGRAPHIC_RECEIPT_01", "MAT_BLACK_GOLD_RECEIPT_01",
    "MAT_SILVER_FOIL_RECEIPT_01", "MAT_GLOW_INK_01",
    "MAT_CHROME_EDGE_01", "MAT_GLASS_ARCHIVE_01",
    "PAT_LEOPARD_01", "PAT_SNAKESKIN_01",
    "PAT_HOLO_GRID_01", "PAT_GOLD_FLECK_01",
    "PAT_IRIDESCENT_WAVE_01", "PAT_SECURITY_PRINT_01",
]

ALL_LEGENDARY_ACCENTS = [
    "PROP_CROWN_GOLD_01", "PROP_CROWN_CHROME_01",
    "PROP_CRYSTAL_SHARD_01", "PROP_HOLO_SEAL_01",
    "PROP_DIAMOND_CLIP_01", "PROP_CHAIN_LUXE_01",
    "PROP_PEARL_TAG_01", "PROP_LASER_STICKER_01",
    "PROP_GEM_BADGE_01", "PROP_ACRYLIC_TOKEN_01",
    "OVERLAY_HOLO_PRISM_01", "OVERLAY_GOLD_DUST_01",
    "OVERLAY_IRIDESCENT_GLOW_01", "OVERLAY_LUXE_VIGNETTE_01",
    "OVERLAY_CRYSTAL_SPARK_01", "OVERLAY_NEON_ARCHIVE_01",
    "OVERLAY_RAINBOW_FOIL_01", "OVERLAY_ULTRA_RARE_SHIMMER_01",
]

GOLD_STAMPS = [
    "STAMP_GENESIS_GOLD", "STAMP_1_OF_1_GOLD",
    "STAMP_ARCHIVED_FOREVER_GOLD", "STAMP_ULTRA_RARE_GOLD",
    "STAMP_VAULTED_GOLD", "STAMP_REDEEMED_GOLD",
    "STAMP_ZERO_SUPPLY_GOLD", "STAMP_GOLD_SEAL_GOLD",
]


def validate_plan(csv_path, check_files=False, output_path=None):
    """Validate a compose plan CSV and generate report."""
    if not os.path.exists(csv_path):
        print(f"✗ CSV not found: {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\n{'='*60}")
    print(f"  NO REFUNDS ARCHIVE - Plan Validator v2.0")
    print(f"  CSV: {csv_path}")
    print(f"  Rows: {len(rows)}")
    print(f"  File check: {'ON' if check_files else 'OFF'}")
    print(f"{'='*60}\n")

    errors = []
    warnings = []

    # Validation checks per row (series-specific checks)
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
        rarity = row.get("稀有度", "").strip()

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

        # ── Series-specific checks ──
        for csv_field, rule_key in checks:
            asset_id = row.get(csv_field, "").strip()
            if not asset_id:
                continue
            allowed = rules[rule_key]
            if asset_id not in allowed:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": csv_field, "当前素材": asset_id,
                    "错误原因": f"{asset_id} 不属于 {series} 的允许{rule_key}列表",
                    "建议替换素材": f"建议使用: {', '.join(allowed[:5])}...",
                    "是否需要删除旧图": "是",
                })

        # ── Material/Pattern check (cross-series, must be valid ID) ──
        mat_id = row.get("材质/纹理", "").strip()
        if mat_id:
            if mat_id not in ALL_MATERIALS:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "材质/纹理", "当前素材": mat_id,
                    "错误原因": f"未知 material_pattern ID: {mat_id}",
                    "建议替换素材": f"使用: {', '.join(ALL_MATERIALS[:4])}...",
                    "是否需要删除旧图": "是",
                })

        # ── Legendary Accent check (cross-series, must be valid ID, supports semicolon-separated) ──
        legend_id = row.get("传奇特征", "").strip()
        if legend_id:
            legend_ids = [a.strip() for a in legend_id.split(";") if a.strip()]
            for lid in legend_ids:
                if lid not in ALL_LEGENDARY_ACCENTS:
                    errors.append({
                        "编号": nft_id, "最终文件名": filename, "系列": series,
                        "错误字段": "传奇特征", "当前素材": lid,
                        "错误原因": f"未知 legendary_accent ID: {lid}",
                        "建议替换素材": f"使用: {', '.join(ALL_LEGENDARY_ACCENTS[:4])}...",
                        "是否需要删除旧图": "是",
                    })

        # ── Rarity rules ──
        has_mat = bool(mat_id)
        has_legend = bool(legend_id)
        # Count semicolon-separated legendary accents as multiple traits
        legend_count = len([a.strip() for a in legend_id.split(";") if a.strip()]) if legend_id else 0
        has_gold_stamp = row.get("印章素材", "").strip() in GOLD_STAMPS
        advanced_trait_count = sum([1 if has_mat else 0, legend_count, 1 if has_gold_stamp else 0])

        if rarity == "Common":
            if has_legend:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "稀有度规则", "当前素材": legend_id,
                    "错误原因": "Common 不应使用 legendary_accent",
                    "建议替换素材": "移除传奇特征",
                    "是否需要删除旧图": "是",
                })

        elif rarity == "Legendary":
            if advanced_trait_count < 2:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "稀有度规则", "当前素材": f"高级trait数={advanced_trait_count}",
                    "错误原因": f"Legendary 必须至少有2个高级 trait (material/legendary/gold stamp), 当前只有{advanced_trait_count}个",
                    "建议替换素材": "增加 material_pattern 或 legendary_accent",
                    "是否需要删除旧图": "是",
                })

        elif rarity == "Ultra Rare":
            if advanced_trait_count < 2:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "稀有度规则", "当前素材": f"高级trait数={advanced_trait_count}",
                    "错误原因": f"Ultra Rare 必须至少有2个高级 trait, 当前只有{advanced_trait_count}个",
                    "建议替换素材": "增加 material_pattern + legendary_accent + gold stamp",
                    "是否需要删除旧图": "是",
                })

        elif rarity == "Rare":
            if advanced_trait_count < 1:
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "稀有度规则", "当前素材": f"高级trait数={advanced_trait_count}",
                    "错误原因": f"Rare 必须至少有1个高级 trait, 当前有{advanced_trait_count}个",
                    "建议替换素材": "增加 material_pattern 或 legendary_accent",
                    "是否需要删除旧图": "是",
                })

        # ── Base template check ──
        base_id = row.get("底图变体", "").strip()
        if base_id:
            base_dir = os.path.join(SCRIPT_DIR, "assets", "base_templates")
            base_path = os.path.join(base_dir, f"{base_id}.png")
            if not os.path.exists(base_path):
                found = False
                for ext in (".jpg", ".jpeg", ".webp"):
                    alt_path = os.path.join(base_dir, f"{base_id}{ext}")
                    if os.path.exists(alt_path):
                        found = True
                        break
                if not found:
                    warnings.append({
                        "编号": nft_id, "最终文件名": filename, "系列": series,
                        "错误字段": "底图变体", "当前素材": base_id,
                        "错误原因": f"底图文件不存在: {base_id}",
                        "建议替换素材": "检查 base_templates/ 目录",
                        "是否需要删除旧图": "",
                    })

        # ── File existence checks ──
        if check_files:
            img_dir = os.path.join(SCRIPT_DIR, "output", "final_images_v2")
            meta_dir = os.path.join(SCRIPT_DIR, "output", "metadata_v2")

            img_path = os.path.join(img_dir, filename)
            if not os.path.exists(img_path):
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "图片文件", "当前素材": filename,
                    "错误原因": "图片文件不存在 (final_images_v2/)",
                    "建议替换素材": "重新执行拼装",
                    "是否需要删除旧图": "",
                })

            meta_filename = os.path.splitext(filename)[0] + ".json"
            meta_path = os.path.join(meta_dir, meta_filename)
            if not os.path.exists(meta_path):
                errors.append({
                    "编号": nft_id, "最终文件名": filename, "系列": series,
                    "错误字段": "metadata文件", "当前素材": meta_filename,
                    "错误原因": "metadata文件不存在 (metadata_v2/)",
                    "建议替换素材": "重新执行拼装",
                    "是否需要删除旧图": "",
                })
            else:
                # ── Metadata consistency check ──
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

                    # Check Material/Pattern
                    csv_mat = row.get("材质/纹理", "").strip()
                    meta_mat = attrs.get("Material / Pattern", "")
                    if csv_mat:
                        expected_mat = csv_mat.replace("MAT_", "").replace("PAT_", "").replace("_", " ")
                        if expected_mat != meta_mat:
                            errors.append({
                                "编号": nft_id, "最终文件名": filename, "系列": series,
                                "错误字段": "metadata Material/Pattern", "当前素材": meta_mat,
                                "错误原因": f"metadata Material/Pattern='{meta_mat}' 与 CSV='{csv_mat}' 不一致",
                                "建议替换素材": "重新生成 metadata",
                                "是否需要删除旧图": "",
                            })

                    # Check Legendary Accent (supports multiple values)
                    csv_legend = row.get("传奇特征", "").strip()
                    meta_legend_values = [a["value"] for a in meta.get("attributes", []) if a["trait_type"] == "Legendary Accent"]
                    if csv_legend:
                        csv_legend_ids = [a.strip() for a in csv_legend.split(";") if a.strip()]
                        csv_expected = [lid.replace("PROP_", "").replace("OVERLAY_", "").replace("_", " ") for lid in csv_legend_ids]
                        if sorted(csv_expected) != sorted(meta_legend_values):
                            errors.append({
                                "编号": nft_id, "最终文件名": filename, "系列": series,
                                "错误字段": "metadata Legendary Accent", "当前素材": str(meta_legend_values),
                                "错误原因": f"metadata Legendary={meta_legend_values} 与 CSV={csv_expected} 不一致",
                                "建议替换素材": "重新生成 metadata",
                                "是否需要删除旧图": "",
                            })

                    # Check Rarity
                    csv_rarity = row.get("稀有度", "").strip()
                    meta_rarity = attrs.get("Rarity", "")
                    if csv_rarity and meta_rarity and csv_rarity != meta_rarity:
                        errors.append({
                            "编号": nft_id, "最终文件名": filename, "系列": series,
                            "错误字段": "metadata Rarity", "当前素材": meta_rarity,
                            "错误原因": f"metadata Rarity='{meta_rarity}' 与 CSV='{csv_rarity}' 不一致",
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
        output_path = os.path.join(SCRIPT_DIR, "data", "compose_plan_validation_report_v2.csv")

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
        print(f"\n  ❌ ERRORS FOUND:")
        error_types = Counter(e["错误字段"] for e in errors)
        for field, count in error_types.most_common():
            print(f"     {field}: {count} errors")
        print(f"\n  Full report: {output_path}")
    else:
        print(f"\n  ✅ ALL CHECKS PASSED - No violations")
        print(f"  Report: {output_path}")

    if warnings:
        print(f"\n  Warnings:")
        for w in warnings[:5]:
            print(f"     {w['编号']}: {w['错误原因']}")

    print(f"\n{'='*60}")

    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="NO REFUNDS ARCHIVE - Plan Validator v2.0")
    parser.add_argument("--csv", default="data/auto_compose_plan_0100_v2.csv",
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
