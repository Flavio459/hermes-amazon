from __future__ import annotations

from .config import RuntimeSettings
from .contracts import BootReport
from .plan import route_profile


def build_boot_report(settings: RuntimeSettings) -> BootReport:
    issues = settings.validate()
    profile = route_profile(settings)
    return BootReport(
        healthy=not issues,
        route_profile=profile.name,
        issues=issues,
    )
