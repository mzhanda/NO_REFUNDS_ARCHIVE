# NO REFUNDS ARCHIVE - Production Handoff

## Locked status
- `release/approved_0100/` is the immutable approved 100-image baseline.
- `release/approved_0333/` is the immutable manually approved 333-image stress batch.
- The confirmed production method is deterministic Python/Pillow layered composition.
- ComfyUI may create raw assets only. It must not generate final collection images.
- Formal production assets are governed by `release/manifests/assets_manifest_final.csv`.

## Current Status

- Final production is complete: 3,333 PNG images and 3,333 ERC-721-compatible metadata JSON files exist in `release/production_3333/`.
- The 50-image production sample, the six 1/1 images, and the completed 3333-image batch have all passed human review.
- Final validation reports 0 broken PNG files and 0 duplicate combination fingerprints.
- The final rarity distribution is Common 1994, Uncommon 833, Rare 350, Legendary 120, Ultra Rare 30, and 1/1 6.
- Series identity follows the actual store printed on the receipt. The seven series are Lucky 8 Gas & Motel, Midnight Diner, Night Owl Video, Pine Hollow General Store, Side B Records, Sunset Mart, and Token Pawn.
- The formal trait system contains ten categories: Material Pattern, Damage, Stamp, Handwritten, Overlay, Latent Memory, Recovered Format, Archive Reconstruction, Dual Recovery, and One of One Archive.
- Website content is complete. It shows archive samples rather than final token combinations; final traits reveal within three days after the collection is fully minted.
- The project is ready for OpenSea upload, deployment, and mint configuration. Do not regenerate or alter final PNG or metadata output without a new approval gate.

## Safety rules
1. Never overwrite `release/approved_0100/` or `release/approved_0333/`.
2. Do not overwrite final production output or regenerate it without a new approved production gate.
3. Keep production metadata and final PNGs unchanged after marketplace upload is finalized.
4. Use only assets marked `approved` in `assets_manifest_final.csv`.
5. Do not revive props, Archive Label, Signal Trace, or Time Imprint without a separate approved art direction.
6. Keep special features receipt-local, with their existing alignment validation approach.
