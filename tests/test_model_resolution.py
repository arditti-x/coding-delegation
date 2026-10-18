import json
import unittest

import support
from model_routing.catalog import load_catalog, resolve_codex_family

MODELS = json.loads((support.FIXTURES / "codex" / "debug_models.json").read_text(encoding="utf-8"))


class CodexResolutionTest(unittest.TestCase):
    def setUp(self):
        self.catalog = load_catalog()

    def resolve(self, family):
        return resolve_codex_family(self.catalog, MODELS, family)

    def test_visible_families_resolve_to_newest_listed(self):
        self.assertEqual(self.resolve("astra").model, "gpt-6-astra")
        self.assertEqual(self.resolve("sol").model, "gpt-6.1-sol")
        terra = self.resolve("terra")
        self.assertEqual(terra.model, "gpt-5.6-terra")
        self.assertTrue(any("lags newest generation" in warning for warning in terra.warnings))
        self.assertEqual(self.resolve("luna").model, "gpt-6-luna")
        for family in ("astra", "sol", "luna"):
            self.assertEqual(self.resolve(family).warnings, [])

    def test_hidden_models_are_ignored(self):
        hidden = [row["slug"] for row in MODELS["models"] if row.get("visibility") != "list"]
        self.assertIn("gpt-reserve", hidden)
        self.assertIn("codex-auto-review", hidden)
        chosen = {self.resolve(family).model for family in ("astra", "sol", "terra", "luna")}
        self.assertTrue(chosen.isdisjoint(hidden))

    def test_hidden_newer_slug_does_not_win(self):
        payload = json.loads(json.dumps(MODELS))
        payload["models"].append(
            {
                "slug": "gpt-9-astra",
                "visibility": "hide",
                "context_window": 1,
                "effective_context_window_percent": 95,
            }
        )
        resolved = resolve_codex_family(self.catalog, payload, "astra")
        self.assertEqual(resolved.model, "gpt-6-astra")

    def test_pin_overrides_newest(self):
        resolved = resolve_codex_family(self.catalog, MODELS, "sol", pin="gpt-6-sol")
        self.assertEqual(resolved.model, "gpt-6-sol")
        self.assertEqual(resolved.warnings, [])

    def test_missing_visibility_is_not_treated_as_listed(self):
        payload = {"models": [{"slug": "gpt-9-luna", "context_window": 1}]}
        resolved = resolve_codex_family(self.catalog, payload, "luna")
        self.assertIsNone(resolved.model)


if __name__ == "__main__":
    unittest.main()
