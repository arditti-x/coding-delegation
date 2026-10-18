import json
import unittest

import support
from model_routing.catalog import codex_usable_window, load_catalog
from model_routing.context import context_need, skips_for_context

MODELS = json.loads((support.FIXTURES / "codex" / "debug_models.json").read_text(encoding="utf-8"))


class ContextMathTest(unittest.TestCase):
    def test_formula_and_strict_boundary(self):
        need = context_need(bytes_in_scope=3000, roundtrip_tokens=1000, output_reserve=16_000)
        self.assertEqual(need, 3000 / 3 + 40_000 + 2 * 1000 + 16_000)
        usable = 100_000
        self.assertFalse(skips_for_context(0.6 * usable, usable))
        self.assertTrue(skips_for_context(0.6 * usable + 1, usable))
        self.assertFalse(skips_for_context(need, None))

    def test_reserve_must_stay_in_range(self):
        with self.assertRaises(ValueError):
            context_need(0, 0, output_reserve=15_999)
        with self.assertRaises(ValueError):
            context_need(0, 0, output_reserve=32_001)
        self.assertEqual(context_need(0, 0), 40_000 + 32_000)

    def test_codex_usable_window_uses_runtime_percent(self):
        catalog = load_catalog()
        usable = codex_usable_window(catalog, MODELS, "gpt-6-astra")
        self.assertEqual(usable, int(272_000 * 95 / 100))
        need = context_need(0, 0, output_reserve=32_000)
        self.assertFalse(skips_for_context(need, usable))
        huge = context_need(3_000_000, 0, output_reserve=32_000)
        self.assertTrue(skips_for_context(huge, usable))


if __name__ == "__main__":
    unittest.main()
