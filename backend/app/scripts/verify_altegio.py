import os
import sys

from app.integrations.altegio import (
    AltegioAuthClient,
    AltegioCredentials,
    AltegioDataClient,
    AltegioEndpoints,
    AltegioHttpClient,
    AltegioRequestError,
)


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required env var: {name}")
    return value


def main() -> int:
    base_url = os.getenv("ALTEGIO_BASE_URL", "https://api.alteg.io/api")
    partner_token = os.getenv("ALTEGIO_PARTNER_TOKEN")

    if not partner_token:
        print("ERROR: Missing required env var: ALTEGIO_PARTNER_TOKEN")
        return 1

    try:
        credentials = AltegioCredentials(
            login=_required_env("ALTEGIO_LOGIN"),
            password=_required_env("ALTEGIO_PASSWORD"),
        )
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    endpoints = AltegioEndpoints(base_url=base_url)
    http_client = AltegioHttpClient(timeout=int(os.getenv("ALTEGIO_TIMEOUT", "20")))

    try:
        auth_client = AltegioAuthClient(
            endpoints=endpoints,
            partner_token=partner_token,
            credentials=credentials,
            http_client=http_client,
        )
        token = auth_client.authenticate()
        print("AUTHENTICATION: WORKING")

        data_client = AltegioDataClient(
            endpoints=endpoints,
            partner_token=partner_token,
            token=token,
            http_client=http_client,
        )

        companies = data_client.get_companies()
        print(f"COMPANIES: WORKING (count={len(companies)})")

        if not companies:
            print("STAFF: UNKNOWN (no companies returned)")
            print("SERVICES: UNKNOWN (no companies returned)")
            return 0

        location_ids = {company.location_id for company in companies}
        company_id_env = os.getenv("ALTEGIO_COMPANY_ID")
        if company_id_env and int(company_id_env) in location_ids:
            company_id = int(company_id_env)
        else:
            company_id = companies[0].location_id

        staff = data_client.get_staff(company_id)
        print(f"STAFF: WORKING (company_id={company_id}, count={len(staff)})")

        services = data_client.get_services(company_id)
        print(f"SERVICES: WORKING (company_id={company_id}, count={len(services)})")

        return 0
    except AltegioRequestError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
