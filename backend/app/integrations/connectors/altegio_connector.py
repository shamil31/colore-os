from __future__ import annotations

from typing import Any

from app.integrations.altegio import (
    AltegioAuthClient,
    AltegioCredentials,
    AltegioDataClient,
    AltegioEndpoints,
    AltegioHttpClient,
)
from app.integrations.gateway import capabilities
from app.integrations.gateway.base_connector import BaseConnector


class AltegioConnector(BaseConnector):
    integration_name = "altegio"

    # "200 requests/min or 5 requests/sec per IP." One shared limiter here, so
    # the decision layer cannot exhaust the salon's whole API quota answering a
    # single message.
    min_interval_seconds = 0.2

    AUTHENTICATE_CAPABILITY = "altegio.authenticate"
    GET_COMPANIES_CAPABILITY = "altegio.get_companies"
    GET_STAFF_CAPABILITY = "altegio.get_staff"
    GET_SERVICES_CAPABILITY = "altegio.get_services"
    GET_CLIENTS_CAPABILITY = "altegio.get_clients"
    GET_ALL_CLIENTS_RAW_CAPABILITY = "altegio.get_all_clients_raw"
    GET_ALL_CLIENT_RECORDS_RAW_CAPABILITY = "altegio.get_all_client_records_raw"
    GET_RECORDS_RANGE_CAPABILITY = "altegio.get_records_range"

    def __init__(
        self,
        *,
        base_url: str,
        partner_token: str,
        login: str,
        password: str,
        timeout: int = 20,
    ) -> None:
        self.endpoints = AltegioEndpoints(base_url=base_url)
        self.partner_token = partner_token
        self.credentials = AltegioCredentials(login=login, password=password)
        self.http_client = AltegioHttpClient(timeout=timeout)
        self._user_token: str | None = None

    @property
    def capabilities(self) -> set[str]:
        return {
            self.AUTHENTICATE_CAPABILITY,
            self.GET_COMPANIES_CAPABILITY,
            self.GET_STAFF_CAPABILITY,
            self.GET_SERVICES_CAPABILITY,
            self.GET_CLIENTS_CAPABILITY,
            self.GET_ALL_CLIENTS_RAW_CAPABILITY,
            self.GET_ALL_CLIENT_RECORDS_RAW_CAPABILITY,
            self.GET_RECORDS_RANGE_CAPABILITY,
            # Read only, deliberately. Altegio stays the system of record and
            # Coloré OS writes nothing to it (ADR-002 decision 6). Declaring a
            # write capability here would let a future caller reach for one.
            capabilities.CLIENTS_READ,
            capabilities.RECORDS_READ,
        }

    def is_configured(self) -> bool:
        return bool(self.partner_token and self.credentials.login and self.credentials.password)

    def missing_configuration(self) -> tuple[str, ...]:
        missing = []
        if not self.partner_token:
            missing.append("ALTEGIO_PARTNER_TOKEN")
        if not self.credentials.login:
            missing.append("ALTEGIO_LOGIN")
        if not self.credentials.password:
            missing.append("ALTEGIO_PASSWORD")
        return tuple(missing)

    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        params = payload or {}

        if capability == self.AUTHENTICATE_CAPABILITY:
            return self._authenticate(force=True)

        token = self._authenticate(force=False)
        data_client = AltegioDataClient(
            endpoints=self.endpoints,
            partner_token=self.partner_token,
            token=token,
            http_client=self.http_client,
        )

        if capability == self.GET_COMPANIES_CAPABILITY:
            return data_client.get_companies()
        if capability == self.GET_STAFF_CAPABILITY:
            company_id = _required_int(params, "company_id")
            return data_client.get_staff(company_id)
        if capability == self.GET_SERVICES_CAPABILITY:
            company_id = _required_int(params, "company_id")
            return data_client.get_services(company_id)
        if capability in (self.GET_CLIENTS_CAPABILITY, capabilities.CLIENTS_READ):
            company_id = _required_int(params, "company_id")
            return data_client.get_clients(company_id)
        if capability == capabilities.RECORDS_READ:
            company_id = _required_int(params, "company_id")
            client_id = _required_int(params, "client_id")
            return data_client.get_all_client_records_raw(
                company_id,
                client_id=client_id,
                page_size=_optional_int(params, "page_size", default=200),
                date_from=_optional_str(params, "date_from"),
            )
        if capability == self.GET_ALL_CLIENTS_RAW_CAPABILITY:
            company_id = _required_int(params, "company_id")
            page_size = _optional_int(params, "page_size", default=200)
            return data_client.get_all_clients_raw(company_id, page_size=page_size)
        if capability == self.GET_RECORDS_RANGE_CAPABILITY:
            company_id = _required_int(params, "company_id")
            date_from = params.get("date_from")
            date_to = params.get("date_to")
            if not isinstance(date_from, str) or not isinstance(date_to, str):
                raise ValueError("Missing or invalid 'date_from'/'date_to' (expected YYYY-MM-DD)")
            return data_client.get_all_records_raw(
                company_id,
                date_from=date_from,
                date_to=date_to,
                page_size=_optional_int(params, "page_size", default=200),
                with_deleted=bool(params.get("with_deleted")),
            )
        if capability == self.GET_ALL_CLIENT_RECORDS_RAW_CAPABILITY:
            company_id = _required_int(params, "company_id")
            client_id = _required_int(params, "client_id")
            page_size = _optional_int(params, "page_size", default=200)
            date_from = _optional_str(params, "date_from")
            return data_client.get_all_client_records_raw(
                company_id,
                client_id=client_id,
                page_size=page_size,
                date_from=date_from,
            )

        raise ValueError(f"Unsupported capability for Altegio connector: {capability}")

    def _authenticate(self, *, force: bool) -> str:
        if self._user_token and not force:
            return self._user_token

        auth_client = AltegioAuthClient(
            endpoints=self.endpoints,
            partner_token=self.partner_token,
            credentials=self.credentials,
            http_client=self.http_client,
        )
        self._user_token = auth_client.authenticate()
        return self._user_token


def _required_int(payload: dict[str, Any], key: str) -> int:
    value = payload.get(key)
    if not isinstance(value, int):
        raise ValueError(f"Missing or invalid integer payload field '{key}'")
    return value


def _optional_int(payload: dict[str, Any], key: str, *, default: int) -> int:
    value = payload.get(key, default)
    if not isinstance(value, int):
        raise ValueError(f"Invalid integer payload field '{key}'")
    return value


def _optional_str(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"Invalid string payload field '{key}'")
    return value
