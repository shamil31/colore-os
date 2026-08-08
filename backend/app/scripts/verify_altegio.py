import os
import sys

from app.integrations.altegio import AltegioRequestError
from app.integrations.connectors.altegio_connector import AltegioConnector
from app.integrations.gateway import ConnectorGateway


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
        login = _required_env("ALTEGIO_LOGIN")
        password = _required_env("ALTEGIO_PASSWORD")
    except ValueError as exc:
        print(f"ERROR: {exc}")
        return 1

    gateway = ConnectorGateway()
    gateway.register(
        AltegioConnector(
            base_url=base_url,
            partner_token=partner_token,
            login=login,
            password=password,
            timeout=int(os.getenv("ALTEGIO_TIMEOUT", "20")),
        )
    )

    try:
        gateway.execute(
            "altegio",
            AltegioConnector.AUTHENTICATE_CAPABILITY,
        )
        print("AUTHENTICATION: WORKING")

        companies = gateway.execute(
            "altegio",
            AltegioConnector.GET_COMPANIES_CAPABILITY,
        )
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

        staff = gateway.execute(
            "altegio",
            AltegioConnector.GET_STAFF_CAPABILITY,
            payload={"company_id": company_id},
        )
        print(f"STAFF: WORKING (company_id={company_id}, count={len(staff)})")

        services = gateway.execute(
            "altegio",
            AltegioConnector.GET_SERVICES_CAPABILITY,
            payload={"company_id": company_id},
        )
        print(f"SERVICES: WORKING (company_id={company_id}, count={len(services)})")

        return 0
    except AltegioRequestError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
