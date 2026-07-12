"""Refresh static review-page data from the canonical 3333 production plan."""
from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from prepare_3333_production import ROOT, read_csv, write_csv

PLAN = ROOT / "data" / "auto_compose_plan_3333.csv"
HTML_PAGES = [
    ROOT / "release/final_review/review_all_high_rarity.html",
    ROOT / "release/final_review/review_common_uncommon_sample.html",
    ROOT / "release/rework/gallery/review_reworked.html",
    ROOT / "staging/0333/gallery/review_0333_gallery.html",
    ROOT / "staging/0333/rework_alignment_preview/review_followup_7.html",
    ROOT / "staging/0333/rework_alignment_preview/review_special_reworks.html",
    ROOT / "staging/one_of_one_preview_0006/gallery/review_one_of_one_0006.html",
    ROOT / "staging/production_sample_0050/gallery/review_production_sample_0050.html",
]
CSV_FILES = [
    ROOT / "release/final_review/reports/review_all_high_rarity.csv",
    ROOT / "release/final_review/reports/review_common_uncommon_sample.csv",
    ROOT / "release/rework/reports/review_reworked.csv",
    ROOT / "staging/one_of_one_preview_0006/reports/review_one_of_one_0006.csv",
    ROOT / "staging/one_of_one_preview_0006/reports/review_one_of_one_0006_v2.csv",
    ROOT / "staging/production_sample_0050/reports/review_production_sample_0050.csv",
]
CSV_RE = re.compile(r'(const REVIEW_CSV\s*=\s*)("(?:\\.|[^"\\])*")')


def sync_row(row: dict, plan: dict[str, dict]) -> bool:
    token = str(row.get("编号", "")).strip()
    item = plan.get(token)
    if not item:
        return False
    if "系列" in row:
        row["系列"] = item["series"]
    if "稀有度" in row:
        row["稀有度"] = item["rarity"]
    if "material_pattern" in row:
        row["material_pattern"] = item["material_pattern"]
    if "legendary_accent" in row:
        row["legendary_accent"] = item["legendary_accent"]
    if "Special Feature" in row:
        row["Special Feature"] = item["special_feature"]
    if "Feature Variant" in row:
        row["Feature Variant"] = item["feature_variant"]
    if "combination_fingerprint" in row:
        row["combination_fingerprint"] = item["combination_fingerprint"]
    return True


def refresh_csv(path: Path, plan: dict[str, dict]) -> int:
    if not path.is_file():
        return 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = list(rows[0]) if rows else []
    changed = sum(sync_row(row, plan) for row in rows)
    if rows:
        write_csv(path, fields, rows)
    return changed


def refresh_html(path: Path, plan: dict[str, dict]) -> int:
    if not path.is_file():
        return 0
    text = path.read_text(encoding="utf-8")
    match = CSV_RE.search(text)
    if not match:
        return 0
    data = json.loads(match.group(2))
    rows = list(csv.DictReader(io.StringIO(data)))
    changed = sum(sync_row(row, plan) for row in rows)
    if not rows:
        return 0
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    updated = text[:match.start(2)] + json.dumps(output.getvalue(), ensure_ascii=False) + text[match.end(2):]
    path.write_text(updated, encoding="utf-8")
    return changed


def main() -> None:
    plan = {row["token_id"]: row for row in read_csv(PLAN)}
    assert len(plan) == 3333
    csv_rows = sum(refresh_csv(path, plan) for path in CSV_FILES)
    html_rows = sum(refresh_html(path, plan) for path in HTML_PAGES)
    print(f"updated {csv_rows} CSV review rows and {html_rows} embedded HTML review rows")


if __name__ == "__main__":
    main()
