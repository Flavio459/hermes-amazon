from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Mapping


DEFAULT_PRIVATE_BASE_URL = "http://100.114.155.6:2099/v1"
DEFAULT_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class RuntimeSettings:
    stage: str = "development"
    provider_mode: str = "custom"
    base_url: str = DEFAULT_PRIVATE_BASE_URL
    default_model: str = "auto"
    manifest_api_key_present: bool = False

    def validate(self) -> list[str]:
        issues: list[str] = []
        if self.provider_mode not in {"custom", "auto"}:
            issues.append(f"provider_mode invalido: {self.provider_mode}")
        if self.provider_mode == "custom" and not self.base_url:
            issues.append("base_url obrigatoria quando provider_mode e custom")
        if self.provider_mode == "auto" and not self.base_url:
            issues.append("base_url obrigatoria quando provider_mode e auto")
        return issues


def load_runtime_settings(env: Mapping[str, str] | None = None) -> RuntimeSettings:
    data = env if env is not None else os.environ
    provider_mode = data.get("HERMES_MODEL_PROVIDER", "custom").strip() or "custom"
    if provider_mode == "auto":
        base_url = data.get("HERMES_MODEL_BASE_URL", DEFAULT_OPENROUTER_BASE_URL).strip()
    else:
        base_url = data.get("HERMES_MODEL_BASE_URL", DEFAULT_PRIVATE_BASE_URL).strip()

    return RuntimeSettings(
        stage=data.get("HERMES_STAGE", "development").strip() or "development",
        provider_mode=provider_mode,
        base_url=base_url,
        default_model=data.get("HERMES_MODEL_DEFAULT", "auto").strip() or "auto",
        manifest_api_key_present=bool(data.get("MANIFEST_API_KEY")),
    )
