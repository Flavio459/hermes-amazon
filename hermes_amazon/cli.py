from __future__ import annotations

import argparse
from pprint import pformat
from typing import Sequence

from .bootstrap import build_boot_report
from .config import load_runtime_settings


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hermes-amazon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect", help="Show current runtime settings")
    subparsers.add_parser("validate", help="Validate runtime settings")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = load_runtime_settings()
    report = build_boot_report(settings)

    if args.command == "inspect":
        print(
            pformat(
                {
                    "stage": settings.stage,
                    "provider_mode": settings.provider_mode,
                    "base_url": settings.base_url,
                    "default_model": settings.default_model,
                    "manifest_api_key_present": settings.manifest_api_key_present,
                    "route_profile": report.route_profile,
                    "module_statuses": dict(report.module_statuses),
                }
            )
        )
        return 0

    if args.command == "validate":
        if report.healthy:
            print("OK")
            return 0
        for issue in report.issues:
            print(issue)
        return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
