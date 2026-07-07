#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成前100张测试CSV：data/nra_batch_0001_0100.csv
用于 ComfyUI 批量脚本读取。
"""

import csv
from pathlib import Path

BASE_MODELS = [
    "B01 Standard Single Receipt",
    "B02 Tabletop Narrative",
    "B04 Archive Scan",
    "B06 Collage Evidence",
]
STAMPS = ["AFTER HOURS", "CLOSED", "NO REFUNDS", "LAST ORDER", "OPEN 24 HOURS", "VOID"]
MARKS = ["LAST NIGHT", "TABLE 6", "11:38 PM", "BOOTH 4", "CHECK 12", "SERVER M"]
PAPERS = [
    "yellowed thermal paper",
    "folded corner and small tear",
    "water stains and scan noise",
    "heavy creases and dirt marks",
    "sealed plastic sleeve glare",
    "faded ink",
]
PROPS = [
    "spoon napkin register clip",
    "menu scrap and coins",
    "sugar packet and bill holder",
    "archive label and tabletop stains",
    "plain cup ring mark",
]
MOODS = [
    "warm low light",
    "cool archive scan",
    "rainy reflection",
    "glass case shadow",
    "sealed evidence feeling",
]


def rarity(n: int) -> str:
    if n <= 33:
        return "Legendary"
    if n % 111 == 0:
        return "Ultra Rare"
    if n % 17 == 0:
        return "Rare"
    if n % 5 == 0:
        return "Uncommon"
    return "Common"


def clean_stamp(stamp: str) -> str:
    return "".join(word.capitalize() for word in stamp.replace(".", "").split())


def main():
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    csv_path = out_dir / "nra_batch_0001_0100.csv"

    fieldnames = [
        "id",
        "name_cn",
        "series",
        "base_model",
        "stamp",
        "handwritten_mark",
        "paper_condition",
        "props",
        "mood",
        "rarity",
        "filename",
        "prompt",
        "image_status",
        "metadata_status",
        "batch",
        "notes",
    ]

    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for n in range(1, 101):
            base_model = BASE_MODELS[(n - 1) % len(BASE_MODELS)]
            stamp = STAMPS[(n - 1) % len(STAMPS)]
            mark = MARKS[(n - 1) % len(MARKS)]
            paper = PAPERS[(n - 1) % len(PAPERS)]
            props = PROPS[(n - 1) % len(PROPS)]
            mood = MOODS[(n - 1) % len(MOODS)]

            filename = f"NRA_{n:04d}_MidnightDiner_{base_model[:3]}_{clean_stamp(stamp)}.png"
            prompt = (
                f"NO REFUNDS ARCHIVE square NFT; Midnight Diner; {base_model}; "
                f"stamp {stamp}; mark {mark}; {paper}; props {props}; mood {mood}; "
                "old receipt main subject; vintage archive aesthetic; no people; "
                "no real brands; no modern UI; no cyberpunk"
            )

            writer.writerow(
                {
                    "id": f"NRA-{n:04d}",
                    "name_cn": f"午夜餐馆：{stamp} / {mark}",
                    "series": "Midnight Diner",
                    "base_model": base_model,
                    "stamp": stamp,
                    "handwritten_mark": mark,
                    "paper_condition": paper,
                    "props": props,
                    "mood": mood,
                    "rarity": rarity(n),
                    "filename": filename,
                    "prompt": prompt,
                    "image_status": "待生成",
                    "metadata_status": "待生成metadata",
                    "batch": "Batch_01",
                    "notes": "GitHub前100张测试CSV",
                }
            )

    print(f"已生成：{csv_path}")


if __name__ == "__main__":
    main()
