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


if __name__ == "__main__":
    unittest.main()
