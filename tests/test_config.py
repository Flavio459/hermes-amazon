import unittest

from hermes_amazon.config import DEFAULT_OPENROUTER_BASE_URL, DEFAULT_PRIVATE_BASE_URL, load_runtime_settings


class ConfigTests(unittest.TestCase):
    def test_custom_endpoint_defaults_to_private_base_url(self) -> None:
        settings = load_runtime_settings({})
        self.assertEqual(settings.provider_mode, "custom")
        self.assertEqual(settings.base_url, DEFAULT_PRIVATE_BASE_URL)

    def test_openrouter_mode_uses_openrouter_default(self) -> None:
        settings = load_runtime_settings(
            {
                "HERMES_MODEL_PROVIDER": "auto",
            }
        )
        self.assertEqual(settings.provider_mode, "auto")
        self.assertEqual(settings.base_url, DEFAULT_OPENROUTER_BASE_URL)

    def test_manifest_key_presence_is_detected(self) -> None:
        settings = load_runtime_settings({"MANIFEST_API_KEY": "mnfst_example"})
        self.assertTrue(settings.manifest_api_key_present)

    def test_changedetection_config_presence_is_detected_without_exposing_key(self) -> None:
        settings = load_runtime_settings(
            {
                "HERMES_CHANGEDETECTION_BASE_URL": "https://changedetection.example",
                "HERMES_CHANGEDETECTION_API_KEY": "secret",
            }
        )
        self.assertEqual(settings.changedetection_base_url, "https://changedetection.example")
        self.assertTrue(settings.changedetection_api_key_present)

    def test_changedetection_key_requires_base_url(self) -> None:
        settings = load_runtime_settings({"HERMES_CHANGEDETECTION_API_KEY": "secret"})
        self.assertIn(
            "HERMES_CHANGEDETECTION_BASE_URL obrigatoria quando HERMES_CHANGEDETECTION_API_KEY esta presente",
            settings.validate(),
        )


if __name__ == "__main__":
    unittest.main()
