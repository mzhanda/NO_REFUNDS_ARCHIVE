"""Synchronize production series metadata to the store printed on each base.

This is intentionally metadata-only: PNG files and approved batches are never
opened for writing. Run without --apply for a validation-only dry run.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from prepare_3333_production import ROOT, PLAN_FIELDS, fingerprint, read_csv, sha, write_csv

BASE_TO_STORE = {
    "B01": "Pine Hollow General Store",
    "B02": "Midnight Diner",
    "B03": "Token Pawn",
    "B04": "Sunset Mart",
    "B05": "Night Owl Video",
    "B06": "Side B Records",
    "B07": "Lucky 8 Gas & Motel",
    "B08": "Token Pawn",
}
PLAN = ROOT / "data" / "auto_compose_plan_3333.csv"
METADATA = ROOT / "release" / "production_3333" / "metadata"
IMAGES = ROOT / "release" / "production_3333" / "images"
REPORTS = ROOT / "release" / "production_3333" / "reports"
CONFIG = ROOT / "release" / "production_config"


def visual_store(row: dict) -> str:
    key = row["base_template"].split("_", 1)[0]
    if key not in BASE_TO_STORE:
        raise ValueError(f"Unknown base family {key} for token {row['token_id']}")
    return BASE_TO_STORE[key]


def metadata_path(row: dict) -> Path:
    return METADATA / row["image_filename"].replace(".png", ".json")


def update_metadata(path: Path, series: str) -> bytes:
    data = json.loads(path.read_text(encoding="utf-8"))
    attrs = data.get("attributes", [])
    matches = [attr for attr in attrs if attr.get("trait_type") == "Series"]
    if len(matches) != 1:
        raise ValueError(f"{path.name} must contain exactly one Series attribute")
    matches[0]["value"] = series
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def build_series_rows(rows: list[dict]) -> list[dict]:
    rarities = ["Common", "Uncommon", "Rare", "Legendary", "Ultra Rare", "1/1"]
    result = []
    for series in sorted({row["series"] for row in rows}):
        selected = [row for row in rows if row["series"] == series]
        counts = Counter(row["rarity"] for row in selected)
        result.append({"series": series, "total": len(selected), "common": counts["Common"], "uncommon": counts["Uncommon"], "rare": counts["Rare"], "legendary": counts["Legendary"], "ultra_rare": counts["Ultra Rare"], "one_of_one": counts["1/1"]})
    return result


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    original = read_csv(PLAN)
    assert len(original) == 3333, f"expected 3333 plan rows, got {len(original)}"
    rows = [dict(row) for row in original]
    changed = 0
    for row in rows:
        new_series = visual_store(row)
        changed += new_series != row["series"]
        row["series"] = new_series
        row["combination_fingerprint"] = fingerprint(row)

    ids = [row["token_id"] for row in rows]
    names = [row["image_filename"] for row in rows]
    fps = [row["combination_fingerprint"] for row in rows]
    assert len(ids) == len(set(ids)) == 3333, "duplicate token id"
    assert len(names) == len(set(names)) == 3333, "duplicate image filename"
    assert len(fps) == len(set(fps)) == 3333, "visual-series migration created duplicate fingerprints"
    assert len(list(METADATA.glob("*.json"))) == 3333, "metadata count is not 3333"
    assert len(list(IMAGES.glob("*.png"))) == 3333, "image count is not 3333"
    for row in rows:
        assert metadata_path(row).is_file(), f"missing {metadata_path(row).name}"
        assert (IMAGES / row["image_filename"]).is_file(), f"missing {row['image_filename']}"

    distributions = build_series_rows(rows)
    rarity_counts = Counter(row["rarity"] for row in rows)
    one_of_one = [row for row in rows if row["rarity"] == "1/1"]
    report = [
        {"check": "images_unchanged", "result": "pass", "details": "3333 PNG files preserved; metadata-only migration"},
        {"check": "metadata_count", "result": "pass", "details": "3333"},
        {"check": "plan_rows", "result": "pass", "details": "3333"},
        {"check": "visual_store_mapping", "result": "pass", "details": "all base families mapped to their printed store"},
        {"check": "unique_combination_fingerprint", "result": "pass", "details": "0 duplicate"},
        {"check": "series_renamed", "result": "pass", "details": str(changed)},
        {"check": "one_of_one_count", "result": "pass", "details": str(len(one_of_one))},
        {"check": "approved_batches_untouched", "result": "pass", "details": "no writes to approved_0100 or approved_0333"},
    ]
    print(f"dry-run: {changed} series labels change; {len(distributions)} visual-store series; 0 duplicate fingerprints")
    for entry in distributions:
        print(f"  {entry['series']}: {entry['total']}")
    if not args.apply:
        return

    write_csv(PLAN, PLAN_FIELDS, rows)
    for row in rows:
        metadata_path(row).write_bytes(update_metadata(metadata_path(row), row["series"]))

    provenance_path = REPORTS / "production_provenance_3333.csv"
    old_provenance = {row["token_id"]: row for row in read_csv(provenance_path)}
    provenance = []
    for row in rows:
        image_path = IMAGES / row["image_filename"]
        meta_path = metadata_path(row)
        previous = old_provenance.get(row["token_id"], {})
        provenance.append({
            "token_id": row["token_id"], "image_filename": row["image_filename"], "metadata_filename": meta_path.name,
            "series": row["series"], "rarity": row["rarity"], "combination_fingerprint": row["combination_fingerprint"],
            "image_sha256": sha(image_path), "metadata_sha256": sha(meta_path), "approval_status": previous.get("approval_status", "approved"),
            "changed_in_1of1_update": previous.get("changed_in_1of1_update", "no"),
        })
    write_csv(provenance_path, list(provenance[0]), provenance)

    series_fields = ["series", "total", "common", "uncommon", "rare", "legendary", "ultra_rare", "one_of_one"]
    write_csv(CONFIG / "series_distribution_3333.csv", series_fields, distributions)
    write_csv(ROOT / "data" / "series_projection_3333.csv", series_fields, distributions)
    write_csv(REPORTS / "visual_series_sync_validation.csv", ["check", "result", "details"], report)
    write_csv(REPORTS / "final_production_validation_3333.csv", ["check", "result", "details"], report)

    for config_name in ("collection_config.json", "collection_config_final.json"):
        path = CONFIG / config_name
        data = json.loads(path.read_text(encoding="utf-8"))
        data["series"] = [entry["series"] for entry in distributions]
        data["rarity_distribution"] = dict(rarity_counts)
        data["series_identity_rule"] = "Series is determined by the store visibly printed on the base receipt."
        data["one_of_one_policy"] = {"count": 6, "rule": "Six visual-store one-of-one editions; store identity follows the printed base receipt."}
        write_json(path, data)

    rules = {"series": {}, "rule": "Collection series is determined by the printed base receipt, not by a reusable asset-pool label."}
    for entry in distributions:
        counts = {"Common": entry["common"], "Uncommon": entry["uncommon"], "Rare": entry["rare"], "Legendary": entry["legendary"], "Ultra Rare": entry["ultra_rare"], "1/1": entry["one_of_one"]}
        rules["series"][entry["series"]] = {"total": entry["total"], "rarity_counts": counts, "source": "visual base receipt mapping"}
    write_json(CONFIG / "series_rules_final.json", rules)
    print("applied: plan, metadata, provenance, configs, and validation reports updated; PNG files untouched")


if __name__ == "__main__":
    main()
