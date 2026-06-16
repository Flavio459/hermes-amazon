from __future__ import annotations

import os
from collections.abc import Mapping

from .config import RuntimeSettings
from .contracts import BootReport
from .credentials import resolve_credentials, validate_credential_settings
from .messaging import validate_messaging_settings
from .plan import route_profile


def build_boot_report(settings: RuntimeSettings, env: Mapping[str, str] | None = None) -> BootReport:
    env_map = env if env is not None else os.environ
    issues = settings.validate()
    issues.extend(validate_credential_settings(env_map))
    issues.extend(validate_messaging_settings(env_map))
    credentials = resolve_credentials(env_map)
    profile = route_profile(settings)
    return BootReport(
        healthy=not issues,
        route_profile=profile.name,
        issues=issues,
        module_statuses={
            "credentials": credentials.mode.value,
            "messaging": "local-memory",
            "processing": "rule-based",
        },
    )
