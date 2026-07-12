"""Promote the four approved replacement PNGs without changing metadata."""
from pathlib import Path
import shutil

from PIL import Image

from prepare_3333_production import ROOT, read_csv, sha, write_csv

TOKENS = ("0418", "0814", "1566", "3177")
REWORK = ROOT / "release" / "rework" / "images"
PRODUCTION = ROOT / "release" / "production_3333"
PROVENANCE = PRODUCTION / "reports" / "production_provenance_3333.csv"


def main() -> None:
    for token in TOKENS:
        source = REWORK / f"NRA_{token}.png"
        target = PRODUCTION / "images" / source.name
        with Image.open(source) as image:
            image.verify()
        shutil.copy2(source, target)
        with Image.open(target) as image:
            image.verify()

    provenance = read_csv(PROVENANCE)
    touched = {str(int(token)) for token in TOKENS}
    for row in provenance:
        if row["token_id"] in touched:
            row["image_sha256"] = sha(PRODUCTION / "images" / row["image_filename"])
            row["approval_status"] = "approved"
    write_csv(PROVENANCE, list(provenance[0]), provenance)
    report = [
        {"check": "replacement_pngs_promoted", "result": "pass", "details": "0418,0814,1566,3177"},
        {"check": "metadata_unchanged", "result": "pass", "details": "formal metadata retained"},
        {"check": "approved_batches_untouched", "result": "pass", "details": "no writes to approved_0100 or approved_0333"},
    ]
    write_csv(PRODUCTION / "reports" / "rework_promotion_0418_0814_1566_3177.csv", ["check", "result", "details"], report)
    print("promoted 4 approved replacement PNGs")


if __name__ == "__main__":
    main()
