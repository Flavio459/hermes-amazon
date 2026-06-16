import unittest

from hermes_amazon.credentials import CredentialMode, resolve_credentials, validate_credential_settings


class CredentialTests(unittest.TestCase):
    def test_defaults_to_mock_mode_when_unset(self) -> None:
        bundle = resolve_credentials({})
        self.assertEqual(bundle.mode, CredentialMode.MOCK)
        self.assertEqual(bundle.provider, "local-mock")

    def test_env_mode_requires_aws_keys(self) -> None:
        issues = validate_credential_settings({"HERMES_CREDENTIALS_MODE": "env"})
        self.assertIn("HERMES_AWS_ACCESS_KEY_ID ausente para modo env", issues)
        self.assertIn("HERMES_AWS_SECRET_ACCESS_KEY ausente para modo env", issues)

    def test_env_mode_resolves_when_keys_exist(self) -> None:
        bundle = resolve_credentials(
            {
                "HERMES_CREDENTIALS_MODE": "env",
                "HERMES_AWS_ACCESS_KEY_ID": "AKIAEXAMPLE",
                "HERMES_AWS_SECRET_ACCESS_KEY": "secret",
            }
        )
        self.assertEqual(bundle.mode, CredentialMode.ENV)
        self.assertTrue(bundle.access_key_present)
        self.assertTrue(bundle.secret_key_present)


if __name__ == "__main__":
    unittest.main()
