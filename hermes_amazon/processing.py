from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Mapping

from .contracts import EventKind, HermesEvent, ModuleName, RouteDecision
from .messaging import LocalMessagingAdapter, MessageValidationError, PublishReceipt

DEFAULT_PROCESSING_CHANNEL = "hermes.local.processing"


@dataclass(frozen=True)
class ProcessingOutcome:
    decision: RouteDecision
    emitted: bool
    receipt: PublishReceipt | None = None


def validate_processing_event(event: HermesEvent) -> list[str]:
    issues: list[str] = []
    if not event.source.strip():
        issues.append("source do evento nao pode ser vazio")
    try:
        json.dumps(event.payload)
    except TypeError as exc:
        raise ValueError("payload do evento precisa ser serializavel em JSON") from exc
    return issues


def decide_route(event: HermesEvent) -> RouteDecision:
    route_map = {
        EventKind.SNS_NOTIFICATION: (
            ModuleName.MESSAGING,
            "fanout_message",
            "SNS alimenta distribuicao de mensagens e orquestracao assíncrona",
        ),
        EventKind.SQS_MESSAGE: (
            ModuleName.PROCESSING,
            "consume_queue_message",
            "SQS entra como fila de trabalho para processamento local",
        ),
        EventKind.LAMBDA_RESULT: (
            ModuleName.STORAGE,
            "persist_lambda_result",
            "resultado de Lambda deve seguir para persistencia e auditoria",
        ),
        EventKind.WEBHOOK_RECEIVED: (
            ModuleName.INTEGRATION,
            "handle_webhook",
            "webhook pertence a integracao externa e adaptadores de entrada",
        ),
        EventKind.STORAGE_REQUEST: (
            ModuleName.STORAGE,
            "apply_storage_request",
            "pedido de armazenamento precisa cair no repositorio persistente",
        ),
    }
    module, action, rationale = route_map[event.kind]
    return RouteDecision(
        event_kind=event.kind,
        module=module,
        action=action,
        rationale=rationale,
    )


class LocalProcessingEngine:
    def __init__(self, messaging: LocalMessagingAdapter | None = None) -> None:
        self._messaging = messaging

    def process(self, event: HermesEvent) -> RouteDecision:
        issues = validate_processing_event(event)
        if issues:
            raise ValueError("; ".join(issues))
        return decide_route(event)

    def run(
        self,
        event: HermesEvent,
        *,
        emit: bool = False,
        channel: str = DEFAULT_PROCESSING_CHANNEL,
    ) -> ProcessingOutcome:
        decision = self.process(event)
        if not emit or self._messaging is None:
            return ProcessingOutcome(decision=decision, emitted=False)

        payload: Mapping[str, Any] = {
            "event_kind": event.kind.value,
            "source": event.source,
            "correlation_id": event.correlation_id,
            "decision": {
                "module": decision.module.value,
                "action": decision.action,
                "rationale": decision.rationale,
            },
        }
        try:
            receipt = self._messaging.publish(payload, channel=channel)
        except MessageValidationError as exc:
            raise ValueError(str(exc)) from exc
        return ProcessingOutcome(decision=decision, emitted=True, receipt=receipt)
