from __future__ import annotations

import unittest
from unittest.mock import patch

from customer_support import main
from customer_support.presets import DEFAULT_PRESET, PRESETS
from customer_support.runtime import SUPPORT_KNOWLEDGE_PATH, check_llm_runtime_dependencies


class ParseArgsTests(unittest.TestCase):
    def test_parse_args_uses_expected_defaults(self) -> None:
        args = main.parse_args([])
        self.assertFalse(args.list_presets)
        self.assertEqual(args.preset, DEFAULT_PRESET)
        self.assertIsNone(args.customer_name)
        self.assertIsNone(args.customer_tier)
        self.assertIsNone(args.channel)
        self.assertIsNone(args.message)
        self.assertFalse(args.skip_preflight)

    def test_parse_args_accepts_live_demo_overrides(self) -> None:
        args = main.parse_args(
            [
                "--preset",
                "sso_failure",
                "--list-presets",
                "--customer-name",
                "Acme Corp",
                "--customer-tier",
                "strategic",
                "--channel",
                "chat",
                "--message",
                "We cannot log in after enabling SSO.",
                "--skip-preflight",
            ]
        )
        self.assertTrue(args.list_presets)
        self.assertEqual(args.preset, "sso_failure")
        self.assertEqual(args.customer_name, "Acme Corp")
        self.assertEqual(args.customer_tier, "strategic")
        self.assertEqual(args.channel, "chat")
        self.assertEqual(args.message, "We cannot log in after enabling SSO.")
        self.assertTrue(args.skip_preflight)


class PresetTests(unittest.TestCase):
    def test_default_message_matches_default_preset(self) -> None:
        self.assertEqual(main.DEFAULT_MESSAGE, PRESETS[DEFAULT_PRESET]["message"])

    def test_preset_catalog_contains_multiple_demo_cases(self) -> None:
        self.assertIn("billing_lockout", PRESETS)
        self.assertIn("sso_failure", PRESETS)
        self.assertIn("integration_outage", PRESETS)
        self.assertIn("double_charge", PRESETS)
        self.assertIn("unclear_request", PRESETS)
        self.assertIn("refund_escalation", PRESETS)
        self.assertIn("api_regression", PRESETS)

    def test_presets_include_a_demo_description(self) -> None:
        self.assertTrue(PRESETS["billing_lockout"]["description"])
        self.assertTrue(PRESETS["api_regression"]["description"])


class KnowledgeTests(unittest.TestCase):
    def test_support_playbook_exists(self) -> None:
        self.assertTrue(SUPPORT_KNOWLEDGE_PATH.exists())

    def test_llm_dependency_check_raises_clear_error_when_missing(self) -> None:
        with patch("customer_support.runtime.importlib.import_module", side_effect=ImportError):
            with self.assertRaisesRegex(RuntimeError, "LiteLLM is not installed"):
                check_llm_runtime_dependencies()


if __name__ == "__main__":
    unittest.main()
