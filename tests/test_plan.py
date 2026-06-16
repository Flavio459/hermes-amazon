import unittest

from hermes_amazon.config import RuntimeSettings
from hermes_amazon.plan import route_profile


class PlanTests(unittest.TestCase):
    def test_custom_mode_routes_to_manifest_private(self) -> None:
        profile = route_profile(RuntimeSettings())
        self.assertEqual(profile.name, "manifest-private")
        self.assertTrue(profile.manifest_enabled)

    def test_auto_mode_routes_to_openrouter(self) -> None:
        profile = route_profile(
            RuntimeSettings(
                provider_mode="auto",
                base_url="https://openrouter.ai/api/v1",
            )
        )
        self.assertEqual(profile.name, "openrouter")
        self.assertFalse(profile.manifest_enabled)


if __name__ == "__main__":
    unittest.main()
