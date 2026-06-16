from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PRODUCT_STORE = Path("data/products.json")
ALLOWED_PRODUCT_STATUSES = {
    "draft",
    "active",
    "watching",
    "paused",
    "rejected",
    "validated",
}


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    affiliate_url: str
    price: str | None = None
    niche: str | None = None
    status: str = "draft"
    notes: str | None = None
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "affiliate_url": self.affiliate_url,
            "price": self.price,
            "niche": self.niche,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Product":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            category=str(data["category"]),
            affiliate_url=str(data["affiliate_url"]),
            price=_optional_str(data.get("price")),
            niche=_optional_str(data.get("niche")),
            status=str(data.get("status") or "draft"),
            notes=_optional_str(data.get("notes")),
            created_at=str(data.get("created_at") or _utc_now()),
            updated_at=str(data.get("updated_at") or _utc_now()),
        )


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_product_id(name: str, affiliate_url: str) -> str:
    seed = f"{name.strip().lower()}|{affiliate_url.strip().lower()}".encode("utf-8")
    return hashlib.sha256(seed).hexdigest()[:12]


def normalize_price(value: str | None) -> str | None:
    if value is None or value.strip() == "":
        return None
    normalized = value.strip().replace(",", ".")
    try:
        price = Decimal(normalized)
    except InvalidOperation as exc:
        raise ValueError("price precisa ser numerico") from exc
    if price < 0:
        raise ValueError("price nao pode ser negativo")
    return format(price.quantize(Decimal("0.01")), "f")


def validate_product(product: Product) -> list[str]:
    issues: list[str] = []
    if not product.name.strip():
        issues.append("name e obrigatorio")
    if not product.category.strip():
        issues.append("category e obrigatoria")
    if not product.affiliate_url.startswith(("http://", "https://")):
        issues.append("affiliate_url precisa comecar com http:// ou https://")
    if product.status not in ALLOWED_PRODUCT_STATUSES:
        issues.append(f"status invalido: {product.status}")
    return issues


class ProductRepository:
    def __init__(self, path: Path | str = DEFAULT_PRODUCT_STORE) -> None:
        self.path = Path(path)

    def list(self) -> list[Product]:
        if not self.path.exists():
            return []
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return [Product.from_dict(item) for item in raw]

    def get(self, product_id: str) -> Product:
        for product in self.list():
            if product.id == product_id:
                return product
        raise KeyError(f"produto nao encontrado: {product_id}")

    def add(self, product: Product) -> Product:
        issues = validate_product(product)
        if issues:
            raise ValueError("; ".join(issues))
        products = self.list()
        if any(item.id == product.id for item in products):
            raise ValueError(f"produto ja existe: {product.id}")
        products.append(product)
        self._write(products)
        return product

    def mark(self, product_id: str, status: str, notes: str | None = None) -> Product:
        if status not in ALLOWED_PRODUCT_STATUSES:
            raise ValueError(f"status invalido: {status}")
        products = self.list()
        updated: Product | None = None
        next_products: list[Product] = []
        for product in products:
            if product.id == product_id:
                updated = Product(
                    id=product.id,
                    name=product.name,
                    category=product.category,
                    affiliate_url=product.affiliate_url,
                    price=product.price,
                    niche=product.niche,
                    status=status,
                    notes=notes if notes is not None else product.notes,
                    created_at=product.created_at,
                    updated_at=_utc_now(),
                )
                next_products.append(updated)
            else:
                next_products.append(product)
        if updated is None:
            raise KeyError(f"produto nao encontrado: {product_id}")
        self._write(next_products)
        return updated

    def _write(self, products: Iterable[Product]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = [product.to_dict() for product in sorted(products, key=lambda item: item.id)]
        self.path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def create_product(
    *,
    name: str,
    category: str,
    affiliate_url: str,
    price: str | None = None,
    niche: str | None = None,
    status: str = "draft",
    notes: str | None = None,
) -> Product:
    clean_name = name.strip()
    clean_url = affiliate_url.strip()
    now = _utc_now()
    product = Product(
        id=build_product_id(clean_name, clean_url),
        name=clean_name,
        category=category.strip(),
        affiliate_url=clean_url,
        price=normalize_price(price),
        niche=_optional_str(niche),
        status=status.strip() or "draft",
        notes=_optional_str(notes),
        created_at=now,
        updated_at=now,
    )
    issues = validate_product(product)
    if issues:
        raise ValueError("; ".join(issues))
    return product
