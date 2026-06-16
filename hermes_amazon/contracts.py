from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Protocol, Sequence


class ModuleName(str, Enum):
    CREDENTIALS = "credentials"
    MESSAGING = "messaging"
    PROCESSING = "processing"
    STORAGE = "storage"
    INTEGRATION = "integration"


class EventKind(str, Enum):
    SNS_NOTIFICATION = "sns_notification"
    SQS_MESSAGE = "sqs_message"
    LAMBDA_RESULT = "lambda_result"
    WEBHOOK_RECEIVED = "webhook_received"
    STORAGE_REQUEST = "storage_request"


@dataclass(frozen=True)
class HermesEvent:
    kind: EventKind
    source: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None


@dataclass(frozen=True)
class RouteDecision:
    event_kind: EventKind
    module: ModuleName
    action: str
    rationale: str


@dataclass(frozen=True)
class CredentialSnapshot:
    provider: str
    scope: str
    temporary: bool = True
    expires_in_seconds: int | None = None


@dataclass(frozen=True)
class BootReport:
    healthy: bool
    route_profile: str
    issues: Sequence[str]
    module_statuses: Mapping[str, str] = field(default_factory=dict)


class CredentialProvider(Protocol):
    def resolve(self) -> CredentialSnapshot:
        raise NotImplementedError


class MessagingAdapter(Protocol):
    def publish(self, channel: str, message: Mapping[str, Any]) -> None:
        raise NotImplementedError


class ProcessingEngine(Protocol):
    def process(self, event: HermesEvent) -> RouteDecision:
        raise NotImplementedError


class StorageRepository(Protocol):
    def save(self, collection: str, item: Mapping[str, Any]) -> None:
        raise NotImplementedError


class IntegrationEndpoint(Protocol):
    def send(self, target: str, payload: Mapping[str, Any]) -> None:
        raise NotImplementedError
