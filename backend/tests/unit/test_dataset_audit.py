"""D-010 inventory checks, not scientific acceptance tests. Requires PyYAML."""

import hashlib
import json
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
CURATED = ROOT / "data/curated"


def load_files():
    return {
        p.relative_to(CURATED).as_posix(): (
            json.loads(p.read_text(encoding="utf-8"))
            if p.suffix == ".json"
            else yaml.safe_load(p.read_text(encoding="utf-8"))
        )
        for p in sorted(CURATED.rglob("*"))
        if p.suffix in {".yaml", ".yml", ".json"}
    }


def inventory():
    result = {}
    for name, data in load_files().items():
        fields = {}

        def walk(value, path):
            fields.setdefault(path, set()).add(type(value).__name__)
            if isinstance(value, dict):
                for key, item in value.items():
                    walk(item, f"{path}.{key}")
            elif isinstance(value, list):
                for item in value:
                    walk(item, path + "[]")

        walk(data, "$")
        rows = data if isinstance(data, list) else [data]
        result[name] = {
            "sha256": hashlib.sha256((CURATED / name).read_bytes()).hexdigest(),
            "records": len(rows),
            "fields": {key: sorted(types) for key, types in sorted(fields.items())},
            "ids": [row["id"] for row in rows if "id" in row],
            "source_refs": {
                row["id"]: row["source"] for row in rows if "source" in row
            },
            "missing_source": [
                row["id"] for row in rows if "id" in row and "source" not in row
            ],
        }
    return result


class CuratedAuditTests(unittest.TestCase):
    def test_required_audit_documents_every_input(self):
        audit_path = ROOT / "docs/agent/DATASET_AUDIT.md"
        audit = audit_path.read_text(encoding="utf-8")
        for name in load_files():
            with self.subTest(file=name):
                self.assertIn(name, audit)
        self.assertIn("(../curated_inventory.json)", audit)
        self.assertTrue((audit_path.parent / "../curated_inventory.json").is_file())

    def test_inventory_matches_audited_snapshot(self):
        expected = json.loads(
            (ROOT / "docs/curated_inventory.json").read_text(encoding="utf-8")
        )
        self.assertEqual(inventory(), expected)

    def test_ids_sources_and_inactive_legacy_flags(self):
        files = load_files()
        sources = {row["id"] for row in files["rule_reviews/sources.yaml"]}
        for name, rows in files.items():
            if not isinstance(rows, list):
                continue
            with self.subTest(file=name):
                ids = [row["id"] for row in rows]
                self.assertEqual(len(ids), len(set(ids)))
                for row in rows:
                    self.assertIs(
                        row["verified"], row["id"] == "SRC-GROWER-LAB-REPORT"
                    )
                    if "source" in row:
                        self.assertIn(row["source"], sources)

    def test_catalog_and_fixture_references(self):
        files = load_files()
        crops = {r["id"] for r in files["datasets/crops.yaml"]}
        problems = {r["id"] for r in files["datasets/problems.yaml"]}
        products = {r["id"] for r in files["datasets/products.yaml"]}
        for row in files["datasets/practices.yaml"]:
            self.assertLessEqual(set(row["crops"]), crops)
            self.assertLessEqual(set(row["problems"]), problems)
        for name, grower in files.items():
            if not name.startswith("fixtures/"):
                continue
            with self.subTest(file=name):
                self.assertLessEqual(set(grower["crops_needed"]), crops)
                self.assertLessEqual(set(grower["price_overrides"]), products)
                ids = [p["id"] for p in grower["plots"]]
                self.assertEqual(len(ids), len(set(ids)))
                for plot in grower["plots"]:
                    for key in ("crop_planned", "crop_last_year", "crop_two_years_ago"):
                        self.assertIn(plot[key], crops | {None})
                    self.assertLessEqual(set(plot["problems"]), problems)
                    for item in plot["baseline"]["inputs"]:
                        self.assertIn(item["product_id"], products)

    def test_documented_placeholders_and_provenance_gaps(self):
        files = load_files()
        lime = files["datasets/lime_table.yaml"]
        self.assertEqual(len(lime), 15)
        self.assertEqual({row["source"] for row in lime}, {"SRC-PLACEHOLDER"})
        self.assertEqual(
            {
                row["id"] for row in files["datasets/crops.yaml"]
                if row["source"] == "SRC-PLACEHOLDER"
            },
            {"bush_bean", "southern_pea", "snap_pea"},
        )
        products = files["datasets/products.yaml"]
        self.assertEqual(len(products), 5)
        self.assertTrue(all("source" not in row for row in products))
        sources = {row["id"]: row for row in files["rule_reviews/sources.yaml"]}
        self.assertEqual(len(sources), 40)
        # These observed fields supply neither licensing nor reviewer evidence.
        for source in sources.values():
            self.assertEqual(
                set(source), {"id", "title", "publisher", "year", "url", "verified"}
            )
        for source_id in ("SRC-PLACEHOLDER", "SRC-GROWER-LAB-REPORT"):
            self.assertEqual(sources[source_id]["url"], "")
            self.assertIsNone(sources[source_id]["year"])

    def test_documented_units_and_fixture_counts(self):
        files = load_files()
        levels = files["datasets/soil_test_levels.yaml"]
        rates = files["datasets/nutrient_recs.yaml"]
        # Record elemental measurements versus oxide rates, without conversions.
        self.assertEqual({row["nutrient"] for row in levels}, {"P", "K"})
        self.assertEqual({row["nutrient"] for row in rates}, {"P2O5", "K2O"})
        for row in levels:
            self.assertIn("Mehlich-1", row["extraction_method"])
            self.assertEqual(
                set(row["upper_bounds_ppm"]), {"very_low", "low", "medium", "high"}
            )
        for row in rates:
            self.assertEqual(
                set(row["lb_per_1000sqft"]),
                {"very_low", "low", "medium", "high", "very_high"},
            )
        self.assertEqual(
            {
                name: len(data["plots"]) for name, data in files.items()
                if name.startswith("fixtures/")
            },
            {
                "fixtures/beginner_grower.json": 1,
                "fixtures/demo_grower.json": 3,
                "fixtures/diverse_farm.json": 5,
                "fixtures/high_input_grower.json": 2,
            },
        )


if __name__ == "__main__":
    unittest.main()
