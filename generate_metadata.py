#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
根据CSV生成NFT metadata JSON。
输出到 metadata/0001.json 等。
"""

import csv
import json
from pathlib import Path


def main():
    csv_path = Path("data/nra_batch_0001_0100.csv")
    out_dir = Path("metadata")
    out_dir.mkdir(exist_ok=True)

    if not csv_path.exists():
        raise FileNotFoundError(f"找不到CSV：{csv_path}")

    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        number = row["id"].split("-")[-1]
        image_name = row["filename"]
        data = {
            "name": f"NO REFUNDS ARCHIVE #{number}",
            "description": "A fictional vintage receipt artifact from the NO REFUNDS ARCHIVE collection.",
            "image": image_name,
            "attributes": [
                {"trait_type": "Series", "value": row["series"]},
                {"trait_type": "Base Model", "value": row["base_model"]},
                {"trait_type": "Stamp", "value": row["stamp"]},
                {"trait_type": "Handwritten Mark", "value": row["handwritten_mark"]},
                {"trait_type": "Paper Condition", "value": row["paper_condition"]},
                {"trait_type": "Props", "value": row["props"]},
                {"trait_type": "Mood", "value": row["mood"]},
                {"trait_type": "Rarity", "value": row["rarity"]},
            ],
        }
        (out_dir / f"{number}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print(f"已生成 metadata：{len(rows)} 个，位置：{out_dir}")


if __name__ == "__main__":
    main()
