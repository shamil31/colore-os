from __future__ import annotations

from typing import Any

from app.integrations.altegio import (
    AltegioAuthClient,
    AltegioCredentials,
    AltegioDataClient,
    AltegioEndpoints,
    AltegioHttpClient,
)
from app.integrations.gateway.base_connector import BaseConnector


class AltegioConnector(BaseConnector):
    integration_name = "altegio"

    AUTHENTICATE_CAPABILITY = "altegio.authenticate"
    GET_COMPANIES_CAPABILITY = "altegio.get_companies"
    GET_STAFF_CAPABILITY = "altegio.get_staff"
    GET_SERVICES_CAPABILITY = "altegio.get_services"
    GET_CLIENTS_CAPABILITY = "altegio.get_clients"
    GET_ALL_CLIENTS_RAW_CAPABILITY = "altegio.get_all_clients_raw"
    GET_ALL_CLIENT_RECORDS_RAW_CAPABILITY = "altegio.get_all_client_records_raw"

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
        }

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
        if capability == self.GET_CLIENTS_CAPABILITY:
            company_id = _required_int(params, "company_id")
            return data_client.get_clients(company_id)
        if capability == self.GET_ALL_CLIENTS_RAW_CAPABILITY:
            company_id = _required_int(params, "company_id")
            page_size = _optional_int(params, "page_size", default=200)
            return data_client.get_all_clients_raw(company_id, page_size=page_size)
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
