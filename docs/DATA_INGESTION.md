# Curated data: audit before schema or import

Canonical input location: `data/curated/`. The user supplies their existing YAML datasets and JSON fixtures **manually**; this starter does not contain or synthesize them.

- `datasets/`: `credits.yaml`, `crops.yaml`, `lime_table.yaml`, `nutrient_recs.yaml`, `practices.yaml`, `problems.yaml`, `products.yaml`, `rotation_rules.yaml`, `soil_test_levels.yaml`.
- `sources.yaml`: source catalog; retain its actual schema/IDs.
- `research/`: notes, permitted papers, excerpts and explicit source provenance. `source_notes.yaml` can be placed here after reference paths are audited.
- `fixtures/`: `beginner_grower.json`, `demo_grower.json`, `diverse_farm.json`, `high_input_grower.json` — synthetic examples only, never production grower records.
- `rule_reviews/`: only real documented human approvals; no automated approvals, and no fictional records.

**D-010 dataset audit:** examine actual schemas, source IDs, references, method/region/crop restrictions, licensing, units, placeholder flags and import order; do not rewrite original source files just to make an import pass.

**F-040 ingestion:** Alembic handles schema migrations. A separate, validated, idempotent script imports versioned source/catalog data and preserves provenance. Test repeated runs, failures, rollback and bad references on disposable PostgreSQL. Research in a database is not automatically eligible for scientific use. Existing legacy `verified` fields are not a substitute for source-version/rule review.

Do not enable placeholder lime quantities, unreviewed nutrient numbers, or unsupported agronomy. Do not select embedding provider, dimension or vector column size without a documented decision. No production ingestion occurs solely because this instruction exists.
