from __future__ import annotations

from dataclasses import dataclass

from .config import DEFAULT_OPENROUTER_BASE_URL, DEFAULT_PRIVATE_BASE_URL, RuntimeSettings


@dataclass(frozen=True)
class RouteProfile:
    name: str
    provider_mode: str
    base_url: str
    manifest_enabled: bool


def route_profile(settings: RuntimeSettings) -> RouteProfile:
    if settings.provider_mode == "custom":
        return RouteProfile(
            name="manifest-private",
            provider_mode=settings.provider_mode,
            base_url=settings.base_url or DEFAULT_PRIVATE_BASE_URL,
            manifest_enabled=True,
        )

    return RouteProfile(
        name="openrouter",
        provider_mode=settings.provider_mode,
        base_url=settings.base_url or DEFAULT_OPENROUTER_BASE_URL,
        manifest_enabled=False,
    )
