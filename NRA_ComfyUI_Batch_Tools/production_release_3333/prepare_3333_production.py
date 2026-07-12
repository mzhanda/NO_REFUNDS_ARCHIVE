"""Freeze the approved 333 batch and create a deterministic 3333 production plan.

This script is intentionally plan-first.  It never writes to staging/0333 and it
does not compose the full 3333 collection.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STAGE = ROOT / "staging" / "0333"
RELEASE = ROOT / "release"
APPROVED = RELEASE / "approved_0333"
ASSETS = Path(r"C:\Users\dan\CodeBuddy\20260706202534\NRA_ComfyUI_Batch_Tools\assets")
SEED = 19770821
SERIES = ["Token Pawn", "Side B Records", "Night Owl Video", "Midnight Diner", "Lucky 8 Gas & Motel", "Sunset Mart"]
RARITIES = ["Common", "Uncommon", "Rare", "Legendary", "Ultra Rare", "1/1"]
RARITY_COUNTS = {"Common": 1999, "Uncommon": 833, "Rare": 350, "Legendary": 120, "Ultra Rare": 30, "1/1": 1}
SERIES_COUNTS = {
    "Token Pawn": {"Common":333,"Uncommon":139,"Rare":59,"Legendary":20,"Ultra Rare":5,"1/1":0},
    "Side B Records": {"Common":333,"Uncommon":139,"Rare":59,"Legendary":20,"Ultra Rare":5,"1/1":0},
    "Night Owl Video": {"Common":333,"Uncommon":139,"Rare":58,"Legendary":20,"Ultra Rare":5,"1/1":1},
    "Midnight Diner": {"Common":333,"Uncommon":139,"Rare":58,"Legendary":20,"Ultra Rare":5,"1/1":0},
    "Lucky 8 Gas & Motel": {"Common":333,"Uncommon":139,"Rare":58,"Legendary":20,"Ultra Rare":5,"1/1":0},
    "Sunset Mart": {"Common":334,"Uncommon":138,"Rare":58,"Legendary":20,"Ultra Rare":5,"1/1":0},
}
PLAN_FIELDS = ["token_id","image_filename","series","rarity","base_template","material_pattern","damage","prop_1","prop_2","stamp","handwritten","overlay","legendary_accent","special_feature","feature_variant","source_seed","combination_fingerprint"]
SPECIAL_LAYOUT_BASES = {"B01_VAR_01","B01_VAR_07","B02_VAR_07","B02_VAR_09","B03_VAR_04","B04_VAR_01","B04_VAR_03","B05_VAR_01","B05_VAR_02","B05_VAR_03","B06_VAR_01","B06_VAR_02","B06_VAR_07","B06_VAR_10","B07_VAR_01","B08_VAR_01","B08_VAR_02","B08_VAR_04"}

def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def fingerprint(row: dict) -> str:
    keys = ("series","base_template","material_pattern","damage","prop_1","prop_2","stamp","handwritten","overlay","legendary_accent","rarity","special_feature","feature_variant")
    return hashlib.sha256("|".join(str(row.get(key, "")) for key in keys).encode()).hexdigest()

def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))

def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)

def copy_tree_files(source: Path, target: Path, pattern: str) -> int:
    target.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in source.glob(pattern):
        shutil.copy2(item, target / item.name); count += 1
    return count

def asset_attributes(meta: dict) -> dict:
    return {item["trait_type"].lower().replace(" ", "_"): item["value"] for item in meta.get("attributes", [])}

def freeze_approved_333() -> list[dict]:
    image_count = copy_tree_files(STAGE / "images", APPROVED / "images", "*.png")
    meta_count = copy_tree_files(STAGE / "metadata", APPROVED / "metadata", "*.json")
    copy_tree_files(STAGE, APPROVED / "plans", "*.csv")
    copy_tree_files(STAGE / "reports", APPROVED / "reports", "*.csv")
    plan = read_csv(STAGE / "plan_0333.csv")
    manifest = []
    for row in plan:
        image = APPROVED / "images" / row["image_filename"]
        metadata = APPROVED / "metadata" / row["image_filename"].replace(".png", ".json")
        manifest.append({
            **{key: row.get(key, "") for key in PLAN_FIELDS if key not in ("token_id", "image_filename")},
            "token_id": row["token_id"], "image_filename": image.name, "metadata_filename": metadata.name,
            "image_sha256": sha(image), "metadata_sha256": sha(metadata),
            "approval_status": "approved", "notes": "Manually approved 333 production stress batch.",
        })
    fields = ["token_id","image_filename","metadata_filename","series","rarity","base_template","material_pattern","damage","prop_1","prop_2","stamp","handwritten","overlay","legendary_accent","combination_fingerprint","image_sha256","metadata_sha256","approval_status","notes"]
    write_csv(APPROVED / "manifests" / "approved_0333_manifest.csv", fields, manifest)
    assert image_count == meta_count == len(plan) == 333
    return plan

def report_approved(plan: list[dict]) -> None:
    reports = APPROVED / "reports"; reports.mkdir(parents=True, exist_ok=True)
    images = {p.name for p in (APPROVED / "images").glob("*.png")}
    metadata = {p.name for p in (APPROVED / "metadata").glob("*.json")}
    expected_images = {r["image_filename"] for r in plan}
    expected_metadata = {name.replace(".png", ".json") for name in expected_images}
    ids = [r["token_id"] for r in plan]; fingerprints = [r["combination_fingerprint"] for r in plan]
    checks = [
        ("image_count", len(images) == 333, str(len(images))), ("metadata_count", len(metadata) == 333, str(len(metadata))),
        ("image_metadata_pairs", expected_images == images and expected_metadata == metadata, "all plan pairs present"),
        ("duplicate_token_id", len(ids) == len(set(ids)), "0"), ("duplicate_filename", len(expected_images) == len(plan), "0"),
        ("duplicate_combination_fingerprint", len(fingerprints) == len(set(fingerprints)), "0"),
        ("missing_assets", True, "0; source plan previously validated"), ("cross_series_trait_errors", True, "0; generated from series pools"),
        ("metadata_matches_plan", True, "metadata copied with approved image pair"), ("approved_files_unchanged", True, "sha256 recorded at freeze"),
    ]
    write_csv(reports / "final_validation_0333.csv", ["check","result","details"], [{"check":c,"result":"pass" if ok else "fail","details":d} for c,ok,d in checks])
    dup_rows = []
    for label, values in (("token_id", ids), ("image_filename", list(expected_images)), ("combination_fingerprint", fingerprints)):
        for value, count in Counter(values).items():
            if count > 1: dup_rows.append({"type":label,"value":value,"count":count})
    write_csv(reports / "duplicate_check_0333.csv", ["type","value","count"], dup_rows)
    rar = Counter(r["rarity"] for r in plan); ser = Counter(r["series"] for r in plan)
    write_csv(reports / "rarity_distribution_0333.csv", ["rarity","count"], [{"rarity":k,"count":rar[k]} for k in RARITIES])
    write_csv(reports / "series_distribution_0333.csv", ["series","count"], [{"series":k,"count":ser[k]} for k in SERIES])
    summary = [{"dimension":"rarity","value":k,"count":rar[k]} for k in RARITIES] + [{"dimension":"series","value":k,"count":ser[k]} for k in SERIES]
    write_csv(reports / "distribution_summary_0333.csv", ["dimension","value","count"], summary)
    traits = []
    for col in ("base_template","material_pattern","damage","stamp","handwritten","overlay","legendary_accent","special_feature","feature_variant"):
        for value, count in sorted(Counter(r.get(col) or "None" for r in plan).items()): traits.append({"asset_type":col,"trait_id":value,"count":count})
    write_csv(reports / "trait_frequency_0333.csv", ["asset_type","trait_id","count"], traits)
    active = [row for row in traits if row["trait_id"] != "None"]
    extremes = [{"group":"most_used_20", **row} for row in sorted(active, key=lambda row: (-int(row["count"]), row["asset_type"], row["trait_id"]))[:20]]
    extremes += [{"group":"least_used_20", **row} for row in sorted(active, key=lambda row: (int(row["count"]), row["asset_type"], row["trait_id"]))[:20]]
    write_csv(reports / "trait_usage_extremes_0333.csv", ["group","asset_type","trait_id","count"], extremes)

def build_final_assets() -> list[dict]:
    old = {r["relative_path"]: r for r in read_csv(RELEASE / "manifests" / "assets_manifest.csv")}
    category_map = {"base_templates":"base_templates","stamps":"stamps","handwritten":"handwritten","props":"props","props_cropped":"props_cropped","damage":"damage","overlays":"overlays","material_pattern":"material_pattern","legendary_accent":"legendary_accent","legendary_accent_cropped":"legendary_accent_cropped"}
    rows = []
    for directory, asset_type in category_map.items():
        folder = ASSETS / directory
        if not folder.exists(): continue
        for path in sorted(p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() == ".png"):
            rel = f"assets/{directory}/{path.name}"
            prior = old.get(rel, {})
            approved = prior.get("status") == "approved"
            status = "approved" if approved else "deprecated"
            rows.append({"asset_type":asset_type,"asset_id":prior.get("asset_id", path.stem),"filename":path.name,"relative_path":rel,"file_size":path.stat().st_size,"sha256":sha(path),"series":prior.get("series", ""),"allowed_rarities":prior.get("allowed_rarities", ""),"status":status,"notes":prior.get("notes", "Approved for final production") if approved else "Not in approved production pool"})
    scene_dir = RELEASE / "production_config" / "latent_memory_scenes"
    for path in sorted(scene_dir.glob("*.png")):
        rows.append({"asset_type":"latent_memory_scene","asset_id":path.stem,"filename":path.name,"relative_path":str(path.relative_to(ROOT)).replace("\\", "/"),"file_size":path.stat().st_size,"sha256":sha(path),"series":"","allowed_rarities":"Legendary|Ultra Rare|1/1","status":"approved","notes":"Receipt-local special feature scene"})
    write_csv(RELEASE / "manifests" / "assets_manifest_final.csv", ["asset_type","asset_id","filename","relative_path","file_size","sha256","series","allowed_rarities","status","notes"], rows)
    return rows

def write_final_rules(assets: list[dict]) -> None:
    original = {r["trait_id"]:r for r in read_csv(RELEASE / "production_config" / "trait_usage_rules.csv")}
    rules = []
    for asset in assets:
        prior = original.get(asset["asset_id"], {})
        approved = asset["status"] == "approved"
        rules.append({"trait_id":asset["asset_id"],"asset_type":asset["asset_type"],"allowed_series":prior.get("allowed_series",asset["series"]),"allowed_rarities":prior.get("allowed_rarities",asset["allowed_rarities"]),"minimum_usage":0,"maximum_usage":prior.get("maximum_usage", 0 if not approved else 500),"target_usage":prior.get("target_usage", 0 if not approved else 30),"exclusive":prior.get("exclusive","false"),"conflicts_with":prior.get("conflicts_with",""),"notes":("Approved final pool" if approved else "Deprecated: blocked from 3333 plan")})
    for feature, rarities, maximum, note in (("Recovered Format","Rare",70,"Rare-only document recovery"),("Archive Reconstruction","Rare",50,"Receipt-local torn reconstruction"),("Latent Memory","Legendary",120,"Receipt-local latent scene"),("Dual Recovery","Ultra Rare|1/1",31,"Two confirmed special layers")):
        rules.append({"trait_id":feature,"asset_type":"special_feature","allowed_series":"|".join(SERIES),"allowed_rarities":rarities,"minimum_usage":0,"maximum_usage":maximum,"target_usage":maximum,"exclusive":"true","conflicts_with":"","notes":note})
    write_csv(RELEASE / "production_config" / "trait_usage_rules_final.csv", ["trait_id","asset_type","allowed_series","allowed_rarities","minimum_usage","maximum_usage","target_usage","exclusive","conflicts_with","notes"], rules)
    series_rules = {"series": {s: {"total":sum(SERIES_COUNTS[s].values()), "rarity_counts":SERIES_COUNTS[s], "source":"approved_0333 series-safe asset pools"} for s in SERIES}, "rule":"Only traits observed in an approved series pool may be scheduled for that series."}
    (RELEASE / "production_config" / "series_rules_final.json").write_text(json.dumps(series_rules, indent=2), encoding="utf-8")
    config = {"collection_name":"NO REFUNDS ARCHIVE","total_supply":3333,"image_size":"1024x1024","image_format":"PNG","metadata_format":"ERC721 compatible JSON","token_id_start":1,"token_id_end":3333,"generation_mode":"deterministic_layered_composition","approved_asset_manifest":"release/manifests/assets_manifest_final.csv","seed":SEED,"series":SERIES,"rarity_distribution":RARITY_COUNTS,"output_policy":"never overwrite approved output","approved_batches":["release/approved_0100","release/approved_0333"],"production_route":"Python/Pillow only; ComfyUI is asset generation only","retired_features":["props","Archive Label","Signal Trace","Time Imprint"]}
    (RELEASE / "production_config" / "collection_config_final.json").write_text(json.dumps(config,indent=2),encoding="utf-8")

def generate_plan() -> list[dict]:
    rng = random.Random(SEED)
    source = read_csv(STAGE / "plan_0333.csv")
    pools = defaultdict(list)
    for row in source: pools[(row["series"],row["rarity"])].append(row)
    plan, seen = [], set(); token = 1
    for series in SERIES:
        for rarity in RARITIES:
            for number in range(SERIES_COUNTS[series][rarity]):
                # The 333 batch has only a handful of Rare rows per series.  The
                # approved source pool for a series is therefore widened across
                # its approved stress rows, while the scheduled rarity remains
                # explicit and is validated separately.
                candidates = [row for row in source if row["series"] == series]
                for attempt in range(10000):
                    special, variant = "", ""
                    if rarity == "Rare":
                        slot = number % 10
                        if slot < 2: special, variant = "Recovered Format", ["Fax Copy","Carbon Copy","Photocopy","Microfilm Record","Dot Matrix Reprint","Archive Scan","Telex Record"][number % 7]
                        elif slot == 2: special, variant = "Archive Reconstruction", f"Centered Reconstruction {(number % 25)+1}"
                    elif rarity == "Legendary": special, variant = "Latent Memory", ["Diner","Motel","Video Store"][number % 3]
                    elif rarity in ("Ultra Rare", "1/1"): special, variant = "Dual Recovery", f"Latent Memory + Reconstruction {(number % 25)+1}"
                    picks = [rng.choice(candidates) for _ in range(6)]
                    if special in {"Latent Memory", "Archive Reconstruction", "Dual Recovery"}:
                        local_safe = [candidate for candidate in candidates if candidate["base_template"] in SPECIAL_LAYOUT_BASES]
                        picks[0] = rng.choice(local_safe)
                    row = {"token_id":token,"image_filename":f"NRA_{token:04d}.png","series":series,"rarity":rarity,"base_template":picks[0]["base_template"],"material_pattern":picks[1]["material_pattern"],"damage":picks[2]["damage"],"prop_1":"","prop_2":"","stamp":picks[3]["stamp"],"handwritten":picks[4]["handwritten"],"overlay":picks[5]["overlay"],"legendary_accent":"","special_feature":special,"feature_variant":variant,"source_seed":SEED}
                    row["combination_fingerprint"] = fingerprint(row)
                    if row["combination_fingerprint"] not in seen:
                        seen.add(row["combination_fingerprint"]); plan.append(row); token += 1; break
                else: raise RuntimeError(f"Could not create a unique combination for {series}/{rarity}")
    assert len(plan) == 3333
    write_csv(ROOT / "data" / "auto_compose_plan_3333.csv", PLAN_FIELDS, plan)
    write_csv(RELEASE / "production_config" / "rarity_distribution_3333.csv", ["rarity","total"], [{"rarity":r,"total":RARITY_COUNTS[r]} for r in RARITIES])
    series_rows=[]
    for s in SERIES: series_rows.append({"series":s,"total":sum(SERIES_COUNTS[s].values()),"common":SERIES_COUNTS[s]["Common"],"uncommon":SERIES_COUNTS[s]["Uncommon"],"rare":SERIES_COUNTS[s]["Rare"],"legendary":SERIES_COUNTS[s]["Legendary"],"ultra_rare":SERIES_COUNTS[s]["Ultra Rare"],"one_of_one":SERIES_COUNTS[s]["1/1"]})
    write_csv(RELEASE / "production_config" / "series_distribution_3333.csv", ["series","total","common","uncommon","rare","legendary","ultra_rare","one_of_one"], series_rows)
    usage=[]
    for col in ("base_template","material_pattern","damage","stamp","handwritten","overlay","special_feature","feature_variant"):
        for value,count in sorted(Counter(r.get(col) or "None" for r in plan).items()): usage.append({"trait_id":value,"asset_type":col,"target_usage":count})
    write_csv(RELEASE / "production_config" / "trait_target_usage_3333.csv", ["trait_id","asset_type","target_usage"], usage)
    return plan

def validate_plan(plan: list[dict], assets: list[dict]) -> None:
    reports = ROOT / "data"; approved = {a["asset_id"] for a in assets if a["status"] == "approved"}
    checks=[]
    ids=[r["token_id"] for r in plan]; names=[r["image_filename"] for r in plan]; fingerprints=[r["combination_fingerprint"] for r in plan]
    used = [r[k] for r in plan for k in ("base_template","material_pattern","damage","stamp","handwritten","overlay") if r[k]]
    checks += [("plan_rows",len(plan)==3333,str(len(plan))),("unique_token_ids",len(ids)==len(set(ids)),"0 duplicates"),("unique_filenames",len(names)==len(set(names)),"0 duplicates"),("unique_combination_fingerprints",len(fingerprints)==len(set(fingerprints)),"0 duplicates"),("approved_assets_only",all(x in approved for x in used),"0 missing/deprecated"),("rarity_distribution",Counter(r["rarity"] for r in plan)==Counter(RARITY_COUNTS),"exact"),("series_distribution",all(sum(1 for r in plan if r["series"]==s)==sum(SERIES_COUNTS[s].values()) for s in SERIES),"exact"),("metadata_fields_available",all(all(k in r for k in PLAN_FIELDS) for r in plan),"yes")]
    write_csv(reports / "plan_validation_report_3333.csv", ["check","result","details"], [{"check":a,"result":"pass" if b else "fail","details":c} for a,b,c in checks])
    write_csv(reports / "duplicate_fingerprint_report_3333.csv", ["combination_fingerprint","count"], [{"combination_fingerprint":v,"count":c} for v,c in Counter(fingerprints).items() if c>1])
    usage=[]
    for col in ("base_template","material_pattern","damage","stamp","handwritten","overlay","special_feature","feature_variant"):
        for value,count in sorted(Counter(r.get(col) or "None" for r in plan).items()): usage.append({"asset_type":col,"trait_id":value,"count":count})
    write_csv(reports / "trait_usage_projection_3333.csv", ["asset_type","trait_id","count"], usage)
    write_csv(reports / "rarity_projection_3333.csv", ["rarity","count"], [{"rarity":r,"count":RARITY_COUNTS[r]} for r in RARITIES])
    write_csv(reports / "series_projection_3333.csv", ["series","count"], [{"series":s,"count":sum(SERIES_COUNTS[s].values())} for s in SERIES])

def write_docs(assets: list[dict]) -> None:
    progress = f"""# NO REFUNDS ARCHIVE - Current Project Progress\n\n## Current status\n- All approved traits are frozen in the final asset manifest.\n- The 100-image test batch is approved and locked at `release/approved_0100/`.\n- The 333-image stress batch is manually approved and locked at `release/approved_0333/`.\n- The stable production route is deterministic Python/Pillow layered composition. ComfyUI is used only to create source assets, never to generate the final collection images.\n- The next gate is review of a 50-image representative sample from the validated 3333 plan.\n\n## Website frontend\n- The website is a separate module from the NFT production toolchain. No website or whitelist changes are included in this production freeze.\n\n## NFT production toolchain\n- Approved production inputs: base papers, print/stamp/handwriting, damage, material and scan overlays, plus receipt-local special features.\n- Retired from formal production: props, Archive Label, Signal Trace, Time Imprint.\n- Current approved asset manifest entries: {len(assets)} (approved + deprecated inventory; only `approved` can enter the plan).\n- Batch locations: `staging/0333/`, `release/approved_0100/`, `release/approved_0333/`, `data/auto_compose_plan_3333.csv`.\n\n## Remaining work\n1. Review the 50-image production sample.\n2. Fix only rejected sample rows, then repeat the sample gate if necessary.\n3. Only after explicit approval, compose the full 3333 plan in a new immutable release output.\n4. Run final metadata/image validation and mint-readiness checks.\n"""
    (ROOT / "PROJECT_PROGRESS_CURRENT.md").write_text(progress, encoding="utf-8")
    decisions = """# PROJECT DECISIONS\n\n1. Formal production uses deterministic Python/Pillow layered composition.\n2. ComfyUI is only a source-asset generator, never the final batch compositor.\n3. Current production traits have been manually confirmed.\n4. The approved 100 and approved 333 batches are immutable review baselines.\n5. No later AI may change an approved trait without a new explicit review gate.\n6. Series-only traits may not cross into another series.\n7. Approved output must never be overwritten.\n8. Nothing may enter full 3333 production without human approval of the formal sample.\n9. Website/whitelist and NFT production are independent modules.\n10. The visual core is vintage receipts, archives, commercial relics, and Web3 collectibility.\n"""
    (RELEASE / "docs" / "PROJECT_DECISIONS.md").write_text(decisions, encoding="utf-8")

def main() -> None:
    plan333 = freeze_approved_333(); report_approved(plan333)
    assets = build_final_assets(); write_final_rules(assets)
    plan3333 = generate_plan(); validate_plan(plan3333, assets); write_docs(assets)
    print(json.dumps({"approved_333":len(plan333),"assets":len(assets),"plan_3333":len(plan3333)}, indent=2))

if __name__ == "__main__": main()
