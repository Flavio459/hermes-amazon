from __future__ import annotations

import json
import argparse
from pprint import pformat
from typing import Sequence

from .bootstrap import build_boot_report
from .config import load_runtime_settings
from .contracts import EventKind, HermesEvent
from .messaging import LocalMessagingAdapter
from .processing import LocalProcessingEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hermes-amazon")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect", help="Show current runtime settings")
    subparsers.add_parser("validate", help="Validate runtime settings")

    process_parser = subparsers.add_parser("process", help="Simulate event routing")
    process_parser.add_argument("--kind", required=True, choices=[kind.value for kind in EventKind])
    process_parser.add_argument("--source", required=True)
    process_parser.add_argument("--payload", default="{}", help="JSON payload")
    process_parser.add_argument("--correlation-id", default=None)
    process_parser.add_argument("--emit", action="store_true", help="Emit a local message summary")
    process_parser.add_argument("--channel", default="hermes.local.processing")
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

    if args.command == "process":
        payload = json.loads(args.payload)
        event = HermesEvent(
            kind=EventKind(args.kind),
            source=args.source,
            payload=payload,
            correlation_id=args.correlation_id,
        )
        engine = LocalProcessingEngine(messaging=LocalMessagingAdapter())
        outcome = engine.run(event, emit=args.emit, channel=args.channel)
        print(
            pformat(
                {
                    "decision": {
                        "event_kind": outcome.decision.event_kind.value,
                        "module": outcome.decision.module.value,
                        "action": outcome.decision.action,
                        "rationale": outcome.decision.rationale,
                    },
                    "emitted": outcome.emitted,
                    "receipt": None
                    if outcome.receipt is None
                    else {
                        "channel": outcome.receipt.channel,
                        "accepted": outcome.receipt.accepted,
                        "stored_messages": outcome.receipt.stored_messages,
                    },
                }
            )
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
