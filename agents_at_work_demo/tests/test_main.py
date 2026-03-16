from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from agents_at_work_demo import main


class ParseArgsTests(unittest.TestCase):
    def test_parse_args_uses_expected_defaults(self) -> None:
        args = main.parse_args([])
        self.assertEqual(args.scenario, main.DEFAULT_SCENARIO)
        self.assertEqual(args.product, main.DEFAULT_PRODUCT)
        self.assertEqual(args.market, main.DEFAULT_MARKET)
        self.assertEqual(args.web_search, "auto")
        self.assertFalse(args.skip_preflight)

    def test_parse_args_accepts_live_demo_overrides(self) -> None:
        args = main.parse_args(
            [
                "--scenario",
                "healthcare_ops",
                "--product",
                "NovaOps",
                "--market",
                "healthcare operations teams",
                "--web-search",
                "off",
                "--skip-preflight",
            ]
        )
        self.assertEqual(args.scenario, "healthcare_ops")
        self.assertEqual(args.product, "NovaOps")
        self.assertEqual(args.market, "healthcare operations teams")
        self.assertEqual(args.web_search, "off")
        self.assertTrue(args.skip_preflight)


class ScenarioResolutionTests(unittest.TestCase):
    def test_available_scenarios_includes_default_demo_set(self) -> None:
        scenarios = main.available_scenarios()
        self.assertIn("saas_ops", scenarios)
        self.assertIn("healthcare_ops", scenarios)

    def test_resolve_knowledge_path_points_to_scenario_file(self) -> None:
        path = main.resolve_knowledge_path("nonprofit")
        self.assertEqual(path.name, "nonprofit.txt")
        self.assertTrue(path.exists())


class PreflightTests(unittest.TestCase):
    @patch("agents_at_work_demo.main.KNOWLEDGE_BASE_PATH.exists", return_value=True)
    @patch("agents_at_work_demo.main.requests.get")
    def test_preflight_passes_when_required_models_exist(
        self,
        mock_get: Mock,
        _mock_exists: Mock,
    ) -> None:
        response = Mock()
        response.json.return_value = {
            "models": [
                {"name": main.OLLAMA_LLM_MODEL},
                {"name": main.OLLAMA_EMBED_MODEL},
            ]
        }
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        main.run_preflight_checks()

    @patch("agents_at_work_demo.main.KNOWLEDGE_BASE_PATH.exists", return_value=True)
    @patch("agents_at_work_demo.main.requests.get")
    def test_preflight_fails_when_model_is_missing(
        self,
        mock_get: Mock,
        _mock_exists: Mock,
    ) -> None:
        response = Mock()
        response.json.return_value = {"models": [{"name": main.OLLAMA_LLM_MODEL}]}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        with self.assertRaisesRegex(RuntimeError, main.OLLAMA_EMBED_MODEL):
            main.run_preflight_checks()

    @patch("agents_at_work_demo.main.KNOWLEDGE_BASE_PATH.exists", return_value=False)
    def test_preflight_fails_when_knowledge_file_is_missing(self, _mock_exists: Mock) -> None:
        with self.assertRaisesRegex(RuntimeError, "Knowledge file is missing"):
            main.run_preflight_checks()


if __name__ == "__main__":
    unittest.main()
