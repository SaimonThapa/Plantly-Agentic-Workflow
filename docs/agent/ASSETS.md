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

## F-010 implementation handoff — 2026-11-08

Repository inspection found the approved mark at `frontend/public/assets/images/planty_logo.svg` (real SVG paths) and the approved tractor at `frontend/public/assets/images/golden_harvest_tractor_at_sunset.png`. Both are integrated; Next Image supplies responsive optimized hero sizes. Responsive visual approval remains pending browser access.

The four layout references are also present in that directory; they are references, not published page artwork. The earlier Awaiting user entries above are superseded for these supplied files only.

Still awaiting user assets: three distinct feature backgrounds and nine distinct benefit photographs. Each slot is visibly labeled `AWAITING USER ASSET`, with its subject and tall/portrait crop described in the page. No stand-in artwork was generated. Optional light footer mark remains deferred; the original full-color mark is used.
