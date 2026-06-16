from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .products import Product, ProductRepository


DEFAULT_WATCH_STORE = Path("data/watch_targets.json")
ALLOWED_WATCH_STATUSES = {"active", "paused"}
ALLOWED_WATCH_EVENT_TYPES = {"price_drop", "price_change", "availability_change", "content_change"}


@dataclass(frozen=True)
class WatchTarget:
    id: str
    product_id: str
    url: str
    selector: str | None = None
    status: str = "active"
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "product_id": self.product_id,
            "url": self.url,
            "selector": self.selector,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "WatchTarget":
        return cls(
            id=str(data["id"]),
            product_id=str(data["product_id"]),
            url=str(data["url"]),
            selector=_optional_str(data.get("selector")),
            status=str(data.get("status") or "active"),
            created_at=str(data.get("created_at") or _utc_now()),
            updated_at=str(data.get("updated_at") or _utc_now()),
        )


@dataclass(frozen=True)
class WatchEvent:
    target_id: str
    product_id: str
    event_type: str
    old_value: str | None = None
    new_value: str | None = None
    severity: str = "info"
    observed_at: str = field(default_factory=lambda: _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "product_id": self.product_id,
            "event_type": self.event_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "severity": self.severity,
            "observed_at": self.observed_at,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def build_watch_id(product_id: str, url: str, selector: str | None = None) -> str:
    seed = f"{product_id.strip()}|{url.strip().lower()}|{selector or ''}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:12]


def validate_watch_target(target: WatchTarget) -> list[str]:
    issues: list[str] = []
    if not target.product_id.strip():
        issues.append("product_id e obrigatorio")
    if not target.url.startswith(("http://", "https://")):
        issues.append("url precisa comecar com http:// ou https://")
    if target.status not in ALLOWED_WATCH_STATUSES:
        issues.append(f"status invalido: {target.status}")
    return issues


def create_watch_target(product: Product, selector: str | None = None, status: str = "active") -> WatchTarget:
    clean_selector = _optional_str(selector)
    now = _utc_now()
    target = WatchTarget(
        id=build_watch_id(product.id, product.affiliate_url, clean_selector),
        product_id=product.id,
        url=product.affiliate_url,
        selector=clean_selector,
        status=status.strip() or "active",
        created_at=now,
        updated_at=now,
    )
    issues = validate_watch_target(target)
    if issues:
        raise ValueError("; ".join(issues))
    return target


class WatchRepository:
    def __init__(self, path: Path | str = DEFAULT_WATCH_STORE) -> None:
        self.path = Path(path)

    def list(self) -> list[WatchTarget]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [WatchTarget.from_dict(item) for item in raw]

    def get(self, target_id: str) -> WatchTarget:
        for target in self.list():
            if target.id == target_id:
                return target
        raise KeyError(f"watch nao encontrado: {target_id}")

    def add(self, target: WatchTarget) -> WatchTarget:
        issues = validate_watch_target(target)
        if issues:
            raise ValueError("; ".join(issues))
        targets = self.list()
        if any(item.id == target.id for item in targets):
            raise ValueError(f"watch ja existe: {target.id}")
        targets.append(target)
        self._write(targets)
        return target

    def add_from_product(self, product_id: str, products: ProductRepository, selector: str | None = None) -> WatchTarget:
        product = products.get(product_id)
        return self.add(create_watch_target(product, selector=selector))

    def _write(self, targets: list[WatchTarget]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [target.to_dict() for target in sorted(targets, key=lambda item: item.created_at)]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def simulate_watch_event(
    target: WatchTarget,
    event_type: str,
    old_value: str | None = None,
    new_value: str | None = None,
    severity: str = "info",
) -> WatchEvent:
    clean_type = event_type.strip()
    if clean_type not in ALLOWED_WATCH_EVENT_TYPES:
        raise ValueError(f"event_type invalido: {clean_type}")
    if not severity.strip():
        raise ValueError("severity nao pode ser vazio")
    return WatchEvent(
        target_id=target.id,
        product_id=target.product_id,
        event_type=clean_type,
        old_value=_optional_str(old_value),
        new_value=_optional_str(new_value),
        severity=severity.strip(),
    )
