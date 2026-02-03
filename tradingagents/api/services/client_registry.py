"""Client registry and credential validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from fastapi import status
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from tradingagents.api.deps.errors import ApiError
from tradingagents.api.settings import settings


_PASSWORD_HASH = PasswordHash((Argon2Hasher(),))


@dataclass(frozen=True)
class ClientRecord:
    client_id: str
    client_secret_hash: str
    account_id: str
    name: Optional[str] = None


def _load_clients() -> dict[str, ClientRecord]:
    if settings.api_clients_json:
        try:
            payload = json.loads(settings.api_clients_json)
        except json.JSONDecodeError as exc:
            raise ApiError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="AUTH_CONFIG_ERROR",
                message="API_CLIENTS_JSON is not valid JSON",
            ) from exc
        if not isinstance(payload, list):
            raise ApiError(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                code="AUTH_CONFIG_ERROR",
                message="API_CLIENTS_JSON must be a list",
            )
        clients: dict[str, ClientRecord] = {}
        for item in payload:
            if not isinstance(item, dict):
                continue
            client_id = item.get("client_id")
            secret_hash = item.get("client_secret_hash")
            account_id = item.get("account_id")
            if not client_id or not secret_hash or not account_id:
                continue
            clients[client_id] = ClientRecord(
                client_id=client_id,
                client_secret_hash=secret_hash,
                account_id=account_id,
                name=item.get("name"),
            )
        return clients

    if settings.app_env == "dev":
        client_id = settings.dev_client_id
        secret_hash = _PASSWORD_HASH.hash(settings.dev_client_secret)
        return {
            client_id: ClientRecord(
                client_id=client_id,
                client_secret_hash=secret_hash,
                account_id="demo-account",
                name="Dev Client",
            )
        }

    return {}


_CLIENTS = _load_clients()


def get_client(client_id: str) -> Optional[ClientRecord]:
    return _CLIENTS.get(client_id)


def verify_client_secret(client: ClientRecord, client_secret: str) -> bool:
    return _PASSWORD_HASH.verify(client_secret, client.client_secret_hash)
