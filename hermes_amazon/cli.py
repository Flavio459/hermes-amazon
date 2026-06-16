from __future__ import annotations

import json
import argparse
from pprint import pformat
from pathlib import Path
from typing import Sequence

from .bootstrap import build_boot_report
from .config import load_runtime_settings
from .contracts import EventKind, HermesEvent
from .messaging import LocalMessagingAdapter
from .processing import LocalProcessingEngine
from .products import ALLOWED_PRODUCT_STATUSES, DEFAULT_PRODUCT_STORE, ProductRepository, create_product


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

    product_parser = subparsers.add_parser("product", help="Manage local product catalog")
    product_parser.add_argument("--store", default=str(DEFAULT_PRODUCT_STORE), help="Product store JSON path")
    product_subparsers = product_parser.add_subparsers(dest="product_command", required=True)

    add_parser = product_subparsers.add_parser("add", help="Add a product")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--category", required=True)
    add_parser.add_argument("--link", required=True)
    add_parser.add_argument("--price", default=None)
    add_parser.add_argument("--niche", default=None)
    add_parser.add_argument("--status", default="draft", choices=sorted(ALLOWED_PRODUCT_STATUSES))
    add_parser.add_argument("--notes", default=None)

    product_subparsers.add_parser("list", help="List products")

    inspect_parser = product_subparsers.add_parser("inspect", help="Inspect a product")
    inspect_parser.add_argument("product_id")

    mark_parser = product_subparsers.add_parser("mark", help="Update product status")
    mark_parser.add_argument("product_id")
    mark_parser.add_argument("--status", required=True, choices=sorted(ALLOWED_PRODUCT_STATUSES))
    mark_parser.add_argument("--notes", default=None)
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

    if args.command == "product":
        repository = ProductRepository(Path(args.store))
        if args.product_command == "add":
            product = create_product(
                name=args.name,
                category=args.category,
                affiliate_url=args.link,
                price=args.price,
                niche=args.niche,
                status=args.status,
                notes=args.notes,
            )
            repository.add(product)
            print(pformat(product.to_dict()))
            return 0

        if args.product_command == "list":
            print(pformat([product.to_dict() for product in repository.list()]))
            return 0

        if args.product_command == "inspect":
            print(pformat(repository.get(args.product_id).to_dict()))
            return 0

        if args.product_command == "mark":
            product = repository.mark(args.product_id, args.status, notes=args.notes)
            print(pformat(product.to_dict()))
            return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
