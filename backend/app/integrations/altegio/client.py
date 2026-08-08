from typing import Any
from urllib.parse import urlencode

import requests

from app.integrations.altegio.endpoints import AltegioEndpoints
from app.integrations.altegio.models import AltegioClient, AltegioCompany, AltegioService, AltegioStaff


class AltegioRequestError(Exception):
    pass


class AltegioHttpClient:
    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout
        self.default_headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/126.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
        }

    def get(self, url: str, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return self._request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        merged_headers = {"Content-Type": "application/json"}
        if headers:
            merged_headers.update(headers)

        return self._request("POST", url, payload=payload, headers=merged_headers)

    def _request(
        self,
        method: str,
        url: str,
        payload: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        merged_headers = dict(self.default_headers)
        if headers:
            merged_headers.update(headers)

        try:
            response = requests.request(
                method=method,
                url=url,
                json=payload,
                headers=merged_headers,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise AltegioRequestError(f"Request failed for {method} {url}: {exc}") from exc

        if response.status_code >= 400:
            raise AltegioRequestError(
                f"HTTP {response.status_code} for {method} {url}: {response.text}"
            )

        try:
            parsed = response.json()
        except ValueError as exc:
            raise AltegioRequestError(f"Non-JSON response for {method} {url}") from exc

        if not isinstance(parsed, dict):
            raise AltegioRequestError(f"Unexpected response format for {method} {url}")

        return parsed


class AltegioDataClient:
    def __init__(
        self,
        endpoints: AltegioEndpoints,
        partner_token: str,
        token: str,
        http_client: AltegioHttpClient,
    ) -> None:
        self.endpoints = endpoints
        self.partner_token = partner_token
        self.token = token
        self.http_client = http_client

    def get_companies(self) -> list[AltegioCompany]:
        payload = self.http_client.get(self.endpoints.companies, headers=self._auth_headers())
        data = _extract_data_list(payload, "companies")
        return [AltegioCompany.model_validate(item) for item in data]

    def get_staff(self, company_id: int) -> list[AltegioStaff]:
        payload = self.http_client.get(self.endpoints.staff(company_id), headers=self._auth_headers())
        data = _extract_data_list(payload, "staff")
        return [AltegioStaff.model_validate(item) for item in data]

    def get_services(self, company_id: int) -> list[AltegioService]:
        payload = self.http_client.get(self.endpoints.services(company_id), headers=self._auth_headers())
        data = _extract_data_list(payload, "services")
        return [AltegioService.model_validate(item) for item in data]

    def get_clients(self, company_id: int) -> list[AltegioClient]:
        payload = self.http_client.get(self.endpoints.clients(company_id), headers=self._auth_headers())
        data = _extract_data_list(payload, "clients")
        return [AltegioClient.model_validate(item) for item in data]

    def get_clients_page_raw(
        self,
        company_id: int,
        *,
        page: int,
        count: int,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        base_url = self.endpoints.clients(company_id)
        separator = "&" if "?" in base_url else "?"
        url = f"{base_url}{separator}count={count}&page={page}"
        payload = self.http_client.get(url, headers=self._auth_headers())
        data = _extract_data_list(payload, "clients")

        meta = payload.get("meta") if isinstance(payload, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        return data, meta

    def get_all_clients_raw(self, company_id: int, *, page_size: int = 200) -> list[dict[str, Any]]:
        page = 1
        all_clients: list[dict[str, Any]] = []

        while True:
            batch, meta = self.get_clients_page_raw(company_id, page=page, count=page_size)
            if not batch:
                break

            all_clients.extend(batch)

            next_page = _resolve_next_page(meta, page=page, page_size=page_size, batch_size=len(batch))
            if next_page is None:
                break

            page = next_page

        return all_clients

    def get_records_page_raw(
        self,
        company_id: int,
        *,
        page: int,
        count: int,
        date_from: str,
        date_to: str,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Every appointment in a date range, across all clients.

        The per-client variant below answers "what did this person book"; this
        one answers "what did the salon book", which is what any conversion or
        occupancy figure needs. Fetching it per client would be 334 requests
        against a 5 req/sec limit.
        """
        params: dict[str, Any] = {
            "start_date": date_from,
            "end_date": date_to,
            "count": count,
            "page": page,
        }

        query = urlencode(params)
        url = f"{self.endpoints.records(company_id)}?{query}"

        payload = self.http_client.get(url, headers=self._auth_headers())
        data = _extract_data_list(payload, "records")

        meta = payload.get("meta") if isinstance(payload, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        return data, meta

    def get_all_records_raw(
        self,
        company_id: int,
        *,
        date_from: str,
        date_to: str,
        page_size: int = 200,
        max_pages: int = 25,
    ) -> list[dict[str, Any]]:
        page = 1
        all_records: list[dict[str, Any]] = []

        while page <= max_pages:
            batch, meta = self.get_records_page_raw(
                company_id,
                page=page,
                count=page_size,
                date_from=date_from,
                date_to=date_to,
            )
            if not batch:
                break

            all_records.extend(batch)

            next_page = _resolve_next_page(meta, page=page, page_size=page_size, batch_size=len(batch))
            if next_page is None:
                break

            page = next_page

        return all_records

    def get_client_records_page_raw(
        self,
        company_id: int,
        *,
        client_id: int,
        page: int,
        count: int,
        date_from: str | None = None,
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        params: dict[str, Any] = {
            "client_id": client_id,
            "count": count,
            "page": page,
        }
        if date_from:
            params["start_date"] = date_from

        query = urlencode(params)
        url = f"{self.endpoints.records(company_id)}?{query}"

        payload = self.http_client.get(url, headers=self._auth_headers())
        data = _extract_data_list(payload, "records")

        meta = payload.get("meta") if isinstance(payload, dict) else None
        if not isinstance(meta, dict):
            meta = {}

        return data, meta

    def get_all_client_records_raw(
        self,
        company_id: int,
        *,
        client_id: int,
        page_size: int = 200,
        date_from: str | None = None,
    ) -> list[dict[str, Any]]:
        page = 1
        all_records: list[dict[str, Any]] = []

        while True:
            batch, meta = self.get_client_records_page_raw(
                company_id,
                client_id=client_id,
                page=page,
                count=page_size,
                date_from=date_from,
            )
            if not batch:
                break

            all_records.extend(batch)

            next_page = _resolve_next_page(meta, page=page, page_size=page_size, batch_size=len(batch))
            if next_page is None:
                break

            page = next_page

        return all_records

    def _auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.partner_token}, User {self.token}",
            "Accept": "application/vnd.api.v2+json",
            "Content-Type": "application/json",
        }


def _extract_data_list(payload: dict[str, Any], entity_name: str) -> list[dict[str, Any]]:
    data = payload.get("data")
    if not isinstance(data, list):
        raise AltegioRequestError(f"Expected list in data for {entity_name}")

    valid_items: list[dict[str, Any]] = []
    for item in data:
        if isinstance(item, dict):
            valid_items.append(item)

    return valid_items


def _resolve_next_page(
    meta: dict[str, Any],
    *,
    page: int,
    page_size: int,
    batch_size: int,
) -> int | None:
    page_total = meta.get("page_count", meta.get("pages", meta.get("last_page")))
    if isinstance(page_total, int):
        return page + 1 if page < page_total else None

    next_page = meta.get("next_page")
    if isinstance(next_page, int):
        return next_page if next_page > page else None

    total = meta.get("total_count", meta.get("total", meta.get("count_all")))
    if isinstance(total, int):
        return page + 1 if (page * page_size) < total else None

    if batch_size < page_size:
        return None

    return page + 1
