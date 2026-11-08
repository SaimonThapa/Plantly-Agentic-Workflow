# Image and artwork handoff (never invent final assets)

Approved behavior: before building each UI surface, ask whether required images/logo are available. If not, keep a **labeled responsive placeholder** in the intended location describing what to supply, its subject and design-established crop/size; do not invent pixel dimensions. This is not a reason to block layout implementation.

| Asset or slot | Source requirement | Status / provided path |
|---|---|---|
| Brand mark | Plantly spherical plant emblem | Awaiting user |
| Landing hero | Large white/cream tractor at field boundary; open sky, lower horizon (see LANDING_DESIGN) | Awaiting user |
| Feature card backgrounds (3) | Field intelligence, observations, weather (separate images) | Awaiting user |
| Benefits cards (9) | 3 sets × 3 agricultural images for growth, irrigation, soil improvement | Awaiting user |
| Optional light footer mark | Only if needed for contrast | Deferred |
| Layout reference screenshots (4) | IMG_4368, IMG_4362, IMG_4365, IMG_4369 | Awaiting user for exact visual matching |

During frontend implementation, prefer a single accessible `MissingAsset` component reused across slots. Keep placeholders visibly labeled `AWAITING USER ASSET`. Mark an asset final only after the real file, integration and responsive review exist. Do not silently use random stock photography or generated logos.
