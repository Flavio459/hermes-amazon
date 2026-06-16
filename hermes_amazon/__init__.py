"""Hermes Amazon core package."""

from .bootstrap import build_boot_report
from .config import RuntimeSettings, load_runtime_settings
from .credentials import (
    CredentialAdapter,
    CredentialBundle,
    CredentialMode,
    EnvironmentCredentialAdapter,
    MockCredentialAdapter,
    resolve_credential_adapter,
    resolve_credentials,
    validate_credential_settings,
)
from .contracts import EventKind, HermesEvent, ModuleName
from .messaging import (
    LocalMessagingAdapter,
    MessageEnvelope,
    MessageValidationError,
    PublishReceipt,
    validate_messaging_settings,
)
from .monitoring import (
    WatchEvent,
    WatchRepository,
    WatchTarget,
    build_watch_id,
    create_watch_target,
    simulate_watch_event,
    validate_watch_target,
)
from .processing import LocalProcessingEngine, ProcessingOutcome, decide_route, validate_processing_event
from .plan import route_profile
from .products import Product, ProductRepository, build_product_id, create_product, validate_product

__all__ = [
    "CredentialAdapter",
    "CredentialBundle",
    "CredentialMode",
    "EnvironmentCredentialAdapter",
    "EventKind",
    "HermesEvent",
    "LocalMessagingAdapter",
    "MessageEnvelope",
    "MessageValidationError",
    "MockCredentialAdapter",
    "ModuleName",
    "PublishReceipt",
    "LocalProcessingEngine",
    "ProcessingOutcome",
    "Product",
    "ProductRepository",
    "RuntimeSettings",
    "WatchEvent",
    "WatchRepository",
    "WatchTarget",
    "build_product_id",
    "build_watch_id",
    "build_boot_report",
    "create_product",
    "create_watch_target",
    "load_runtime_settings",
    "decide_route",
    "resolve_credential_adapter",
    "resolve_credentials",
    "route_profile",
    "validate_credential_settings",
    "validate_messaging_settings",
    "validate_product",
    "validate_processing_event",
    "validate_watch_target",
    "simulate_watch_event",
]
