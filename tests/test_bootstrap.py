import unittest

from hermes_amazon.bootstrap import build_boot_report
from hermes_amazon.config import RuntimeSettings


class BootstrapTests(unittest.TestCase):
    def test_boot_report_is_healthy_with_mock_credentials(self) -> None:
        report = build_boot_report(RuntimeSettings(), env={})
        self.assertTrue(report.healthy)
        self.assertEqual(report.module_statuses["credentials"], "mock")
        self.assertEqual(report.module_statuses["messaging"], "local-memory")

    def test_boot_report_reports_missing_env_credentials(self) -> None:
        report = build_boot_report(
            RuntimeSettings(),
            env={
                "HERMES_CREDENTIALS_MODE": "env",
            },
        )
        self.assertFalse(report.healthy)
        self.assertIn("HERMES_AWS_ACCESS_KEY_ID ausente para modo env", report.issues)


if __name__ == "__main__":
    unittest.main()
