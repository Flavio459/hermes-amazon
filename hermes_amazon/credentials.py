from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Mapping


class CredentialMode(str, Enum):
    MOCK = "mock"
    ENV = "env"


@dataclass(frozen=True)
class CredentialBundle:
    mode: CredentialMode
    provider: str
    scope: str
    temporary: bool = True
    expires_in_seconds: int | None = None
    access_key_present: bool = False
    secret_key_present: bool = False
    session_token_present: bool = False


class CredentialAdapter:
    def resolve(self) -> CredentialBundle:
        raise NotImplementedError


@dataclass(frozen=True)
class MockCredentialAdapter(CredentialAdapter):
    provider: str = "local-mock"
    scope: str = "local"

    def resolve(self) -> CredentialBundle:
        return CredentialBundle(
            mode=CredentialMode.MOCK,
            provider=self.provider,
            scope=self.scope,
            temporary=True,
            expires_in_seconds=300,
        )


@dataclass(frozen=True)
class EnvironmentCredentialAdapter(CredentialAdapter):
    provider: str = "aws"
    scope: str = "runtime"

    def resolve(self) -> CredentialBundle:
        return CredentialBundle(
            mode=CredentialMode.ENV,
            provider=self.provider,
            scope=self.scope,
            temporary=True,
            expires_in_seconds=None,
            access_key_present=True,
            secret_key_present=True,
            session_token_present=False,
        )


def _get_env(data: Mapping[str, str], key: str) -> str:
    return data.get(key, "").strip()


def resolve_credential_adapter(env: Mapping[str, str]) -> CredentialAdapter:
    mode = _get_env(env, "HERMES_CREDENTIALS_MODE") or CredentialMode.MOCK.value
    if mode == CredentialMode.ENV.value:
        if _get_env(env, "HERMES_AWS_ACCESS_KEY_ID") and _get_env(env, "HERMES_AWS_SECRET_ACCESS_KEY"):
            return EnvironmentCredentialAdapter()
        return MockCredentialAdapter()
    return MockCredentialAdapter()


def resolve_credentials(env: Mapping[str, str]) -> CredentialBundle:
    return resolve_credential_adapter(env).resolve()


def validate_credential_settings(env: Mapping[str, str]) -> list[str]:
    issues: list[str] = []
    mode = _get_env(env, "HERMES_CREDENTIALS_MODE") or CredentialMode.MOCK.value
    if mode not in {CredentialMode.MOCK.value, CredentialMode.ENV.value}:
        issues.append(f"modo de credenciais invalido: {mode}")
        return issues

    if mode == CredentialMode.ENV.value:
        if not _get_env(env, "HERMES_AWS_ACCESS_KEY_ID"):
            issues.append("HERMES_AWS_ACCESS_KEY_ID ausente para modo env")
        if not _get_env(env, "HERMES_AWS_SECRET_ACCESS_KEY"):
            issues.append("HERMES_AWS_SECRET_ACCESS_KEY ausente para modo env")

    return issues
