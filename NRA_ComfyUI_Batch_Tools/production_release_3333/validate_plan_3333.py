"""Validate the deterministic 3333 plan without composing any images."""
from prepare_3333_production import build_final_assets, read_csv, validate_plan, ROOT

if __name__ == "__main__":
    assets = build_final_assets()
    plan = read_csv(ROOT / "data" / "auto_compose_plan_3333.csv")
    validate_plan(plan, assets)
    print(f"validated {len(plan)} planned tokens")
