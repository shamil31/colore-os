from sqlalchemy.orm import Session

from app.models.client import Client


def get_all_clients(db: Session):
    return db.query(Client).all()


def get_client_by_id(db: Session, client_id: int):
    return db.query(Client).filter(Client.id == client_id).first()


def create_client(
    db: Session,
    first_name: str,
    last_name: str,
    phone: str,
):
    client = Client(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
    )

    db.add(client)
    db.commit()
    db.refresh(client)

    return client


def update_client(
    db: Session,
    client: Client,
    first_name: str,
    last_name: str,
    phone: str,
):
    client.first_name = first_name
    client.last_name = last_name
    client.phone = phone

    db.commit()
    db.refresh(client)

    return client


def delete_client(
    db: Session,
    client: Client,
):
    db.delete(client)
    db.commit()