from pydantic import BaseModel, ConfigDict, Field


class AltegioCredentials(BaseModel):
    login: str
    password: str


class AltegioCompany(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    company_id: int | None = None
    salon_id: int | None = None
    title: str | None = None
    name: str | None = None

    @property
    def location_id(self) -> int:
        for value in (self.company_id, self.salon_id, self.id):
            if isinstance(value, int):
                return value
        return self.id


class AltegioStaff(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str | None = None
    fullname: str | None = None


class AltegioService(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    title: str | None = None
    name: str | None = None
    cost: float | None = None


class AltegioAuthData(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_token: str = Field(min_length=1)


class AltegioClient(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    name: str | None = None
    fullname: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    mobile: str | None = None
    mobile_phone: str | None = None
    phone_number: str | None = None
    last_visit_date: str | None = None
    last_visit: str | None = None
    category: str | None = None
    service: str | None = None
    visits_count: int | None = None
