# NO REFUNDS ARCHIVE - Final Production Status

Updated: 2026-07-13

## Production Status

- Final production output: 3,333 PNG images and 3,333 ERC-721-compatible metadata JSON files.
- Image size: 1024x1024 PNG.
- Final production route: deterministic Python/Pillow layered composition.
- ComfyUI is retained only for source-asset generation, not final full-image generation.
- The approved 100-image and 333-image batches remain frozen and were not modified.
- Four previously corrupted production PNGs (`NRA_0418`, `NRA_0814`, `NRA_1566`, `NRA_3177`) were replaced with their approved reworks on 2026-07-13.
- Final image readability check: 3,333 checked, 0 broken PNG files.
- Metadata pairing check: 3,333 images / 3,333 metadata files.
- Combination-fingerprint check: 0 duplicates.

## Collection Distribution

| Rarity | Count |
| --- | ---: |
| Common | 1994 |
| Uncommon | 833 |
| Rare | 350 |
| Legendary | 120 |
| Ultra Rare | 30 |
| 1/1 | 6 |
| Total | 3333 |

Series identity follows the store visibly printed on the base receipt.

| Visual Store Series | Count |
| --- | ---: |
| Lucky 8 Gas & Motel | 263 |
| Midnight Diner | 552 |
| Night Owl Video | 369 |
| Pine Hollow General Store | 511 |
| Side B Records | 750 |
| Sunset Mart | 298 |
| Token Pawn | 590 |

## Review And Records

- Review directory: `release/final_review/review_index.html`.
- Production plan: `data/auto_compose_plan_3333.csv`.
- Production images: `release/production_3333/images/`.
- Production metadata: `release/production_3333/metadata/`.
- Production provenance: `release/production_3333/reports/production_provenance_3333.csv`.
- Final validation: `release/production_3333/reports/final_production_validation_3333.csv`.
- Final image integrity result: `release/production_3333/reports/rework_promotion_0418_0814_1566_3177.csv`.

## Website Content Status

- The public website content is complete and aligned with the final production vocabulary.
- The archive contains seven visual store series: Lucky 8 Gas & Motel, Midnight Diner, Night Owl Video, Pine Hollow General Store, Side B Records, Sunset Mart, and Token Pawn.
- The formal trait system contains ten categories: Material Pattern, Damage, Stamp, Handwritten, Overlay, Latent Memory, Recovered Format, Archive Reconstruction, Dual Recovery, and One of One Archive.
- Website galleries show archive samples only; they do not reveal a token's final trait combination before reveal.
- Final token traits will be revealed within three days after the collection is fully minted.
- Props are retired from both the production vocabulary and public website copy. 1997 is not a fixed setting for the project.

## OpenSea Release State

The collection will use OpenSea's mint/deployment workflow. No separate custom smart-contract deployment is currently required from this production repository.

Before mint is opened:

1. Upload final images and metadata through the chosen OpenSea workflow.
2. Confirm the platform's metadata URI and reveal configuration requirements.
3. Confirm collection settings: total supply 3333, public price 0.0006 ETH, whitelist allocation, royalties, treasury wallet, and mint dates.
4. Keep the final images and metadata unchanged after upload.
