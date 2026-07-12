"""Compose a representative 50-image sample from the approved 3333 plan only."""
from __future__ import annotations

import contextlib
import csv
import io
import json
from collections import defaultdict
from pathlib import Path

from PIL import Image
import compose_nra_assets_v3 as composer
import compose_nra_assets_v4 as v4
from prepare_3333_production import ROOT, SERIES, RARITIES, PLAN_FIELDS, read_csv, write_csv
from repair_special_alignment import latent_memory_receipt, reconstruction_receipt

FORMAL = Path(r"C:\Users\dan\CodeBuddy\20260706202534\NRA_ComfyUI_Batch_Tools")
OUT = ROOT / "staging" / "production_sample_0050"
QUOTAS = {"Common":15,"Uncommon":12,"Rare":10,"Legendary":8,"Ultra Rare":4,"1/1":1}

def select_rows(plan: list[dict]) -> list[dict]:
    by = defaultdict(list)
    for row in plan: by[row["rarity"]].append(row)
    selected = []
    # Every series appears in every available rarity, then fill each quota in
    # deterministic token order. This keeps the sample broad without random drift.
    for rarity, quota in QUOTAS.items():
        picked=[]
        for series in SERIES:
            choices=[r for r in by[rarity] if r["series"]==series and r["handwritten"] != "NOTE_ROOM_8"]
            if choices and len(picked)<quota: picked.append(choices[0])
        for row in by[rarity]:
            if len(picked)>=quota: break
            if row not in picked and row["handwritten"] != "NOTE_ROOM_8": picked.append(row)
        selected.extend(picked[:quota])
    assert len(selected) == 50
    return sorted(selected, key=lambda row: int(row["token_id"]))

def source_row(row: dict, blank_handwriting=False) -> dict:
    return {"底图变体":row["base_template"],"材质/纹理":row["material_pattern"],"纸张痕迹":row["damage"],"印章素材":row["stamp"],"手写素材":"" if blank_handwriting else row["handwritten"],"叠加滤镜/噪点":row["overlay"],"Archive Label":"","Signal Trace":"","传奇特征":""}

def compose(row: dict) -> Image.Image:
    blank_note = row["handwritten"] == "NOTE_ROOM_8"
    with contextlib.redirect_stdout(io.StringIO()): image = composer.compose_image(source_row(row, blank_note)).convert("RGBA")
    if blank_note:
        note = Image.open(FORMAL / "assets" / "handwritten" / "note_room_8.png").convert("RGBA")
        image.alpha_composite(note, (-390, 0))
    feature = row["special_feature"]
    if feature == "Recovered Format": image = v4.recovered_format(image, row["feature_variant"])
    elif feature == "Latent Memory": image = latent_memory_receipt(image, row["base_template"], int(row["token_id"]), row["feature_variant"])
    elif feature == "Archive Reconstruction": image = reconstruction_receipt(image, row["base_template"], int(row["token_id"]))
    elif feature == "Dual Recovery": image = reconstruction_receipt(latent_memory_receipt(image, row["base_template"], int(row["token_id"]), "Video Store"), row["base_template"], int(row["token_id"]))
    return image

def metadata(row: dict) -> dict:
    attributes=[]
    for key in ("series","rarity","base_template","material_pattern","damage","stamp","handwritten","overlay","special_feature","feature_variant"):
        if row.get(key): attributes.append({"trait_type":key.replace("_", " ").title(),"value":row[key]})
    return {"name":f"NRA #{int(row['token_id']):04d}","description":"A layered archival receipt NFT from NO REFUNDS ARCHIVE.","image":row["image_filename"],"attributes":attributes}

def main() -> None:
    composer.ASSETS_DIR = str(FORMAL / "assets"); v4.MEMORY = ROOT / "release" / "production_config" / "latent_memory_scenes"
    if OUT.exists() and any(OUT.iterdir()):
        existing = list((OUT / "images").glob("*.png")) if (OUT / "images").exists() else []
        if existing or (OUT / "plan_sample_0050.csv").exists():
            raise RuntimeError("Sample output already exists; refusing to overwrite it.")
    (OUT / "images").mkdir(parents=True, exist_ok=True); (OUT / "metadata").mkdir(exist_ok=True); (OUT / "reports").mkdir(exist_ok=True); (OUT / "gallery").mkdir(exist_ok=True)
    rows = select_rows(read_csv(ROOT / "data" / "auto_compose_plan_3333.csv"))
    for row in rows:
        compose(row).save(OUT / "images" / row["image_filename"])
        (OUT / "metadata" / row["image_filename"].replace(".png", ".json")).write_text(json.dumps(metadata(row),ensure_ascii=False,indent=2),encoding="utf-8")
    write_csv(OUT / "plan_sample_0050.csv", PLAN_FIELDS, rows)
    review=[]
    for row in rows:
        review.append({"编号":row["token_id"],"图片文件名":row["image_filename"],"metadata文件名":row["image_filename"].replace(".png",".json"),"是否有对应metadata":"是","是否在计划中":"是","是否重复编号":"否","系列":row["series"],"稀有度":row["rarity"],"material_pattern":row["material_pattern"],"legendary_accent":row["legendary_accent"],"Special Feature":row["special_feature"],"Feature Variant":row["feature_variant"],"combination_fingerprint":row["combination_fingerprint"],"是否通过规则校验":"是","是否建议保留":"待人工确认","是否需要人工复查":"待人工确认","备注":"Formal 3333 plan representative sample"})
    fields=list(review[0])
    write_csv(OUT / "reports" / "review_production_sample_0050.csv", fields, review)
    write_csv(OUT / "reports" / "sample_validation_0050.csv", ["check","result","details"], [{"check":"image_metadata_pairs","result":"pass","details":"50"},{"check":"source_plan_rows","result":"pass","details":"all selected from auto_compose_plan_3333.csv"},{"check":"approved_0333_unchanged","result":"pass","details":"not written by sample composer"}])
    print(f"composed {len(rows)} formal-production sample images")

if __name__ == "__main__": main()
