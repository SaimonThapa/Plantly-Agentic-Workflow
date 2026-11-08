# D-010: curated YAML and JSON audit

Repository inspection: 2026-11-08. This is an inventory and proposed mapping,
not scientific approval, publication verification, legal clearance or ingestion.
Scope: all 15 YAML/JSON files under `data/curated/`; originals unchanged.
No task dependencies or human gates are listed for D-010.

## Reproducible inventory

[`curated_inventory.json`](../curated_inventory.json) records each actual path,
SHA-256 of original bytes (including comments), record count, nested field paths
and observed Python scalar/container types, IDs and row-to-source references.
These are observed shapes, not an approved validation schema; absent fields are
not automatically optional. Empty arrays/maps provide no evidence of item types.
`missing_source` means no row-level `source` key, including publication identities
which naturally have no parent source.

All YAML roots are lists of mappings with string IDs and boolean `verified`.
The four JSON roots are grower objects, with 1, 3, 5 and 2 plots respectively
(beginner, demo, diverse, high-input). Plot IDs repeat across fixtures and are
only unique within each fixture. They cannot become global database IDs.

| Actual path under data/curated | Rows | Schema and units observed | Proposed destination |
|---|---:|---|---|
| datasets/credits.yaml | 2 | Discriminated by `kind`; available N/P2O5/K2O lb/cu yd, compost cap cu yd/1000 sqft, previous-legume N lb/1000 sqft | Inactive versioned credit-rule payloads |
| datasets/crops.yaml | 21 | name, family, demand; target pH; N lb/1000 sqft | Stable crop codes; separate pending target/rate rules |
| datasets/lime_table.yaml | 15 | texture, pH min/max/target; lime lb/1000 sqft | Disabled placeholder archive only |
| datasets/nutrient_recs.yaml | 8 | P2O5/K2O, demand, five-category rate map in lb/1000 sqft | Pending nutrient-rule versions |
| datasets/practices.yaml | 13 | crop/problem ID arrays, prose text | Pending practice rules with join references |
| datasets/problems.yaml | 13 | name, kind, family array, rotation_helps boolean | Problem catalog plus pending applicability |
| datasets/products.yaml | 5 | type, nullable role, N/P2O5/K2O percentages, bag lb, USD/bag | Catalog staging; exclude prices from live offers |
| datasets/rotation_rules.yaml | 3 | kind-specific years_back or demand fields; severity and message | Pending versioned rule payloads |
| datasets/soil_test_levels.yaml | 2 | P/K, extraction_method text, four upper bounds in ppm | Pending method-scoped interpretation rules |
| research/source_notes.yaml | 122 | source, page/section string, topics array, note text | Inactive candidate research_chunks |
| rule_reviews/sources.yaml | 40 | title, publisher, nullable year, URL, verified | research_sources and immutable research_source_versions |
| fixtures/beginner_grower.json | 1 | Grower object with 1 plot | Synthetic test input only |
| fixtures/demo_grower.json | 1 | Grower object with 3 plots | Synthetic test input only |
| fixtures/diverse_farm.json | 1 | Grower object with 5 plots | Synthetic test input only |
| fixtures/high_input_grower.json | 1 | Grower object with 2 plots | Synthetic test input only |

Fixture fields include crops_needed, compost cu yd and USD/cu yd, empty
price_overrides, plot area sqft, texture, pH, P/K ppm, organic matter percent,
nullable crop history, planned crop, problem IDs, baseline product lb and
pesticide application counts. They contain no lab method, report, sampling date,
depth, location or season dates. Zero fixture prices are synthetic input values,
not evidence that real materials are free. Do not label these measurements lab verified.

## References, placeholders and review gaps

The checks resolve all explicit `source` keys to the 40-entry source catalog,
all practice crop/problem references and all fixture crop/problem/product
references. IDs are unique within each YAML file. A resolving ID proves neither
publication validity nor support for a claim. Topics are mixed free-text topic,
family, problem and crop tags; they are not uniformly crop foreign keys.

- Actual catalog location is `rule_reviews/sources.yaml`, not the previously
  documented root `sources.yaml`. It contains publication metadata, not rule
  approvals. There are no other files in that directory in this inventory.
- All 82 dataset rows and 122 notes have `verified: false`; 39 source rows are
  false. `SRC-GROWER-LAB-REPORT` alone is true, with empty URL and null year.
  Its comment assumes intake confirmation; no actual lab report or reviewer
  evidence accompanies this generic row. Preserve the legacy flag as provenance;
  never map it to approved status.
- `SRC-PLACEHOLDER` has empty publisher/URL and null year. All 15 lime rows cite
  it and explicitly contain placeholder quantities. The file's suggested fallback
  conflicts with PRODUCT 8.2: no real-user fallback from these rates.
- `bush_bean`, `southern_pea`, `snap_pea` cite SRC-PLACEHOLDER. Their zero N rates
  are explicitly described as planner assumptions in crops.yaml, not sourced rates.
- All five products omit `source`. Prices for `fert-10-10-10`, `tsp-0-46-0`,
  and `ag-lime` are marked placeholders in comments. Urea and potash comments
  describe conversion from October 2026 DTN farm averages; SRC-DTN-PRICES exists
  but there is no row-level link, retailer offer or observation timestamp.
  Preserve this distinction; none is a verified current local price.
- Products include type `mineral` and null role; import validation must not assume
  only organic/synthetic or a mandatory role. Problem `rotation_helps: false`
  must survive import. Rotation message braces are formatting tokens, not missing data.
- Important restrictions live in comments: soil thresholds use Clemson
  Mehlich-1, a stated lb/acre-to-ppm assumption and particular soil textures;
  nutrient recommendations describe a home-garden program. These do not authorize
  other extractants, regions or commercial crops. Four upper bounds yield five
  categories; the top category has no finite ceiling in the file.
- Compost credits derive from one worked example and density assumptions;
  previous-legume credit comments distinguish vegetable legumes from cover crops.
  Crop target/rate comments include exceptions and assumptions. Preserve comments
  with the source revision and have a reviewer formalize applicability before use.
- No structured rule version, reviewer, review timestamp, allowed region/depth,
  acceptance examples or approval manifest is present. Notes' page strings are
  supplied locators, not independently verified page numbers.

## Licensing and publication provenance

None of the 40 source records provides a license, permitted-use status or
redistribution permission. No license fields or permission artifacts accompany
these 15 inputs. Public URLs and publisher names do not establish permission.
The notes header describes paraphrases, but that claim does not settle reuse
rights. Licensing is **unknown** for every source and derived dataset/note;
do not manufacture a license or infer one from a publisher. Retain citation
metadata, request permitted-use evidence before extraction/embedding or
redistribution, and retain original version/hash and supplied locators.

This audit did not fetch linked publications or verify their scientific claims,
dates, availability or licenses. No publication contents are asserted here.

## Proposed import mapping and order (F-040 work, not implemented)

1. Record actual relative paths and raw hashes in an import manifest; parse and
   validate known shapes, duplicate IDs and references before a transaction.
   Keep comments/original bytes for restrictions not represented in YAML fields.
2. Stage source identities: id -> stable source ID, publisher -> organization,
   title/url/year -> supplied bibliographic metadata. Missing license remains
   unknown. Create immutable source revisions with content hash, pending_review
   status and absent reviewer evidence. Do not convert legacy verified to approval.
3. Stage crops, problems and products by existing IDs, then practices and
   rule payloads referencing these catalogs and exact source versions. Proposed
   scientific_rule_versions storage follows ARCHITECTURE 6.4; it is not an existing
   schema claim. Keep rules inactive; explicitly disable placeholder lime rows.
   Preserve N versus P2O5/K2O, percentages versus fractions, and original units;
   do not silently convert oxide nutrients into elemental P/K.
4. Stage notes as candidate chunks: id -> stable note identity, source -> source
   version FK, note -> text, page -> original locator, topics -> tags. Include
   text hash/version. No claim-authorizing retrieval or embedding until review,
   permitted use and embedding decisions are available.
5. Keep fixtures outside production ingestion. A future test adapter could map
   plots to owned plots, sqft to canonical area_m2, crop history to explicitly
   supplied seasons, and observations to soil_measurements preserving original
   units/source type. Missing owner, dates, method and provenance must not be
   invented to fill relational constraints. Preserve baseline inputs as synthetic
   plot-season input snapshots; do not turn them into savings claims.
6. Future importer tests must cover repeated imports, changed/unchanged hashes,
   immutable prior versions, bad references and rollback on disposable PostgreSQL.
   This audit creates no importer, migrations, approvals or runtime data.

## Checks and remaining gates

From the repository root, run
`python -m pytest backend/tests/unit/test_dataset_audit.py -q`.
The tests also run with unittest:
`python -m unittest discover -s backend/tests/unit -p test_dataset_audit.py -v`.
Requires Python and PyYAML (declared in the backend dev dependencies; observed
installed version 6.0.3); no dependency was installed for this audit. Tests parse
JSON with the JSON parser and YAML with the safe YAML loader, compare the full
file inventory/hash/schema snapshot, check references, preserve the exact legacy
flag exception, and check documented placeholders, provenance gaps, unit labels
and fixture counts. Snapshot changes require
re-auditing; do not regenerate it merely to silence a failure. These checks prove
repository structure and drift detection, not agronomic correctness.

D-010 has no blocking human gate. Subsequent live scientific activation is
BLOCKED_BY_SCIENCE until exact source/rule applicability and acceptance examples
receive real review. Licensing/allowed use also needs human evidence. This does
not prevent completing the requested inventory and proposed mapping. Runner task
status and verification configuration remain untouched.
