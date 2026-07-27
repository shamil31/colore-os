from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.client import (
    ClientCreate,
    ClientResponse,
    ClientUpdate,
)
from app.services.client_service import (
    create_client,
    delete_client,
    get_all_clients,
    get_client_by_id,
    update_client,
)

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
)


@router.post("", response_model=ClientResponse)
def create_client_endpoint(
    client: ClientCreate,
    db: Session = Depends(get_db),
):
    return create_client(
        db=db,
        first_name=client.first_name,
        last_name=client.last_name,
        phone=client.phone,
    )


@router.get("", response_model=List[ClientResponse])
def get_clients(
    db: Session = Depends(get_db),
):
    return get_all_clients(db)


@router.get("/{client_id}", response_model=ClientResponse)
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
):
    client = get_client_by_id(db, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    return client


@router.put("/{client_id}", response_model=ClientResponse)
def update_client_endpoint(
    client_id: int,
    client_data: ClientUpdate,
    db: Session = Depends(get_db),
):
    client = get_client_by_id(db, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    return update_client(
        db=db,
        client=client,
        first_name=client_data.first_name,
        last_name=client_data.last_name,
        phone=client_data.phone,
    )


@router.delete("/{client_id}")
def delete_client_endpoint(
    client_id: int,
    db: Session = Depends(get_db),
):
    client = get_client_by_id(db, client_id)

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    delete_client(db, client)

    return {
        "message": "Client deleted successfully"
    }