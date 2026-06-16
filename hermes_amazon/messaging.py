from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any, Mapping


@dataclass(frozen=True)
class MessageEnvelope:
    channel: str
    payload: Mapping[str, Any]
    attributes: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PublishReceipt:
    channel: str
    accepted: bool
    stored_messages: int


class MessageValidationError(ValueError):
    pass


def _ensure_serializable(payload: Mapping[str, Any]) -> None:
    try:
        json.dumps(payload)
    except TypeError as exc:
        raise MessageValidationError("payload da mensagem precisa ser serializavel em JSON") from exc


def validate_message_envelope(envelope: MessageEnvelope) -> list[str]:
    issues: list[str] = []
    if not envelope.channel.strip():
        issues.append("channel da mensagem nao pode ser vazio")
    _ensure_serializable(envelope.payload)
    for key, value in envelope.attributes.items():
        if not key.strip():
            issues.append("atributo de mensagem nao pode ter chave vazia")
        if not isinstance(value, str):
            issues.append(f"atributo {key} precisa ser string")
    return issues


@dataclass
class LocalMessagingAdapter:
    channel: str = "hermes.local"
    _messages: list[MessageEnvelope] = field(default_factory=list)

    def publish(self, payload: Mapping[str, Any], channel: str | None = None, attributes: Mapping[str, str] | None = None) -> PublishReceipt:
        resolved_channel = (channel or self.channel).strip()
        envelope = MessageEnvelope(
            channel=resolved_channel,
            payload=payload,
            attributes=attributes or {},
        )
        issues = validate_message_envelope(envelope)
        if issues:
            raise MessageValidationError("; ".join(issues))
        self._messages.append(envelope)
        return PublishReceipt(channel=resolved_channel, accepted=True, stored_messages=len(self._messages))

    @property
    def messages(self) -> tuple[MessageEnvelope, ...]:
        return tuple(self._messages)


def validate_messaging_settings(env: Mapping[str, str]) -> list[str]:
    issues: list[str] = []
    if "HERMES_MESSAGING_DEFAULT_CHANNEL" not in env:
        return issues
    default_channel = env.get("HERMES_MESSAGING_DEFAULT_CHANNEL", "").strip()
    if not default_channel:
        issues.append("HERMES_MESSAGING_DEFAULT_CHANNEL nao pode ser vazio")
    return issues
