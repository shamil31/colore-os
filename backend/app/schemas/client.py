from pydantic import BaseModel


class ClientCreate(BaseModel):
    first_name: str
    last_name: str
    phone: str


class ClientUpdate(BaseModel):
    first_name: str
    last_name: str
    phone: str


class ClientResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    phone: str

    model_config = {
        "from_attributes": True
    }