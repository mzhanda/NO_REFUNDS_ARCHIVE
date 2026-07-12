# NO REFUNDS ARCHIVE - Production Handoff

## Locked status
- `release/approved_0100/` is the immutable approved 100-image baseline.
- `release/approved_0333/` is the immutable manually approved 333-image stress batch.
- The confirmed production method is deterministic Python/Pillow layered composition.
- ComfyUI may create raw assets only. It must not generate final collection images.
- Formal production assets are governed by `release/manifests/assets_manifest_final.csv`.

## Current gate
`data/auto_compose_plan_3333.csv` has 3333 deterministic, validated planned rows. It is a plan only; the full 3333 image batch has not been composed.

The next required human gate is:
`staging/production_sample_0050/gallery/review_production_sample_0050.html`

The 50 images come from the formal 3333 plan and cover every series and rarity, including special features. Review with the standard gallery controls, export `review_decisions_0050.csv`, then regenerate only rows marked `redo`.

## Safety rules
1. Never overwrite `release/approved_0100/` or `release/approved_0333/`.
2. Never compose all 3333 before the 50-image sample is approved.
3. Use only assets marked `approved` in `assets_manifest_final.csv`.
4. Do not revive props, Archive Label, Signal Trace, or Time Imprint without a separate approved art direction.
5. Keep special features receipt-local, with their existing alignment validation approach.
