from typing import Any

from app.integrations.altegio.client import AltegioHttpClient, AltegioRequestError
from app.integrations.altegio.endpoints import AltegioEndpoints
from app.integrations.altegio.models import AltegioAuthData, AltegioCredentials


class AltegioAuthClient:
    def __init__(
        self,
        endpoints: AltegioEndpoints,
        partner_token: str,
        credentials: AltegioCredentials,
        http_client: AltegioHttpClient,
    ) -> None:
        self.endpoints = endpoints
        self.partner_token = partner_token
        self.credentials = credentials
        self.http_client = http_client

    def authenticate(self) -> str:
        method = "POST"
        headers = {
            "Authorization": f"Bearer {self.partner_token}",
            "Accept": "application/vnd.api.v2+json",
            "Content-Type": "application/json",
        }
        payload = {
            "login": self.credentials.login,
            "password": self.credentials.password,
        }

        print(f"ALTEGIO_AUTH_REQUEST_URL: {self.endpoints.auth}")
        print(f"ALTEGIO_AUTH_REQUEST_METHOD: {method}")
        print(f"ALTEGIO_AUTH_REQUEST_HEADERS: {headers}")
        print(
            "ALTEGIO_AUTH_REQUEST_BODY: "
            f"{{'login': '<provided>', 'password': '<hidden>'}}"
        )
        print(
            "ALTEGIO_AUTH_REQUEST_BODY_KEYS: "
            f"{sorted(list(payload.keys()))}"
        )

        response = self.http_client.post(self.endpoints.auth, payload=payload, headers=headers)
        data = _extract_auth_data(response)
        return data.user_token


def _extract_auth_data(response: dict[str, Any]) -> AltegioAuthData:
    payload = response.get("data")
    if not isinstance(payload, dict):
        raise AltegioRequestError("Auth response missing data object")

    try:
        return AltegioAuthData.model_validate(payload)
    except Exception as exc:  # noqa: BLE001
        raise AltegioRequestError("Auth response missing user_token") from exc
