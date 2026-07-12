# NO REFUNDS ARCHIVE - Current Project Progress

## Current status
- All approved traits are frozen in the final asset manifest.
- The 100-image test batch is approved and locked at `release/approved_0100/`.
- The 333-image stress batch is manually approved and locked at `release/approved_0333/`.
- The stable production route is deterministic Python/Pillow layered composition. ComfyUI is used only to create source assets, never to generate the final collection images.
- The next gate is review of a 50-image representative sample from the validated 3333 plan.
- Current GitHub baseline before this freeze: `39488a9f46ea255c68268b826bc20ec0ab5f42f2`.

## Website frontend
- The website is a separate module from the NFT production toolchain. No website or whitelist changes are included in this production freeze.

## NFT production toolchain
- Approved production inputs: base papers, print/stamp/handwriting, damage, material and scan overlays, plus receipt-local special features.
- Retired from formal production: props, Archive Label, Signal Trace, Time Imprint.
- Confirmed production traits: 149 approved source assets plus 3 approved receipt-local latent-memory scenes. The final inventory lists 379 files, with the remaining 227 marked `deprecated` and blocked from the plan.
- Batch locations: `staging/0333/`, `release/approved_0100/`, `release/approved_0333/`, `data/auto_compose_plan_3333.csv`.

## Remaining work
1. Review the 50-image production sample.
2. Fix only rejected sample rows, then repeat the sample gate if necessary.
3. Only after explicit approval, compose the full 3333 plan in a new immutable release output.
4. Run final metadata/image validation and mint-readiness checks.
