class AltegioEndpoints:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    @property
    def auth(self) -> str:
        return f"{self.base_url}/v1/auth"

    @property
    def companies(self) -> str:
        return f"{self.base_url}/v1/companies?my=1"

    def staff(self, company_id: int) -> str:
        return f"{self.base_url}/v1/staff/{company_id}"

    def services(self, company_id: int) -> str:
        return f"{self.base_url}/v1/services/{company_id}"

    def clients(self, company_id: int) -> str:
        return f"{self.base_url}/v1/clients/{company_id}"

    def records(self, company_id: int) -> str:
        return f"{self.base_url}/v1/records/{company_id}"
