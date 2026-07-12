"""Generate the deterministic 3333 plan without composing any images."""
from prepare_3333_production import generate_plan

if __name__ == "__main__":
    print(f"planned {len(generate_plan())} tokens")
