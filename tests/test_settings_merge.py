import unittest
from pathlib import Path

import support
from model_routing.settings import load_merged, load_yaml, merge_layers, normalize, write_prefs
from model_routing.yamlio import loads


class MergeOrderTest(unittest.TestCase):
    def test_per_job_beats_repo_beats_user_beats_defaults(self):
        defaults = load_yaml(support.ROOT / "data" / "prefs-defaults.yaml")
        user = {
            "routing": {
                "frontier": "flagged",
                "stall_timeout_min": 60,
                "first_tool": "codex",
                "tools": {"claude": {"enabled": True}},
            }
        }
        repo = {
            "routing": {
                "first_tool": "claude",
                "tools": {"codex": {"enabled": True}},
            }
        }
        job = {"routing": {"frontier": "auto"}}
        merged = normalize(merge_layers(defaults, user, repo, job))
        routing = merged["routing"]
        self.assertEqual(routing["frontier"], "auto")
        self.assertEqual(routing["first_tool"], "claude")
        self.assertEqual(routing["stall_timeout_min"], 60)
        self.assertTrue(routing["tools"]["claude"]["enabled"])
        self.assertTrue(routing["tools"]["codex"]["enabled"])
        self.assertFalse(routing["tools"]["cursor"]["enabled"])
        self.assertEqual(merged["models"]["policy"], "newest")
        self.assertEqual(merged["preferences"]["order"], [])

    def test_repo_file_does_not_hide_user_file(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            repo = Path(tmp) / "repo"
            user_path = home / ".config" / "coding-delegation" / "prefs.yaml"
            write_prefs(
                user_path,
                {
                    "routing": {
                        "frontier": "flagged",
                        "stall_timeout_min": 60,
                        "first_tool": "codex",
                    }
                },
            )
            write_prefs(repo / "coding-delegation.prefs.yaml", {"routing": {"first_tool": "claude"}})
            merged = load_merged(repo_root=repo, user_path=user_path, job={"routing": {"frontier": "automatically"}})
        self.assertEqual(merged["routing"]["frontier"], "auto")
        self.assertEqual(merged["routing"]["first_tool"], "claude")
        self.assertEqual(merged["routing"]["stall_timeout_min"], 60)
        self.assertEqual(merged["routing"]["extra_spend"], "deny")

    def test_defaults_are_generic(self):
        text = (support.ROOT / "data" / "prefs-defaults.yaml").read_text(encoding="utf-8").lower()
        catalog = (support.ROOT / "data" / "tiers.yaml").read_text(encoding="utf-8").lower()
        for blob in (text, catalog):
            self.assertNotIn("eitav", blob)
            self.assertNotIn("@", blob)
            self.assertNotIn("gmail", blob)
        data = loads((support.ROOT / "data" / "prefs-defaults.yaml").read_text(encoding="utf-8"))
        self.assertEqual(data["routing"]["frontier"], "never")
        self.assertEqual(data["preferences"]["order"], [])
        self.assertEqual(data["routing"]["first_tool"], None)
        self.assertFalse(data["routing"]["tools"]["claude"]["enabled"])
        self.assertFalse(data["routing"]["tools"]["codex"]["enabled"])
        self.assertFalse(data["routing"]["tools"]["cursor"]["enabled"])
        parsed_catalog = loads((support.ROOT / "data" / "tiers.yaml").read_text(encoding="utf-8"))
        self.assertNotIn("preferences", parsed_catalog)
        self.assertNotIn("order", parsed_catalog)

    def test_inline_comments_do_not_become_part_of_the_value(self):
        from model_routing.yamlio import loads

        parsed = loads("routing:\n  frontier: never  # stay off\n  cost_order: []  # user only\n")
        self.assertEqual(parsed["routing"]["frontier"], "never")
        self.assertEqual(parsed["routing"]["cost_order"], [])

    def test_stall_outside_the_choices_falls_back(self):
        merged = normalize({"routing": {"stall_timeout_min": 45}})
        self.assertEqual(merged["routing"]["stall_timeout_min"], 30)


if __name__ == "__main__":
    unittest.main()
