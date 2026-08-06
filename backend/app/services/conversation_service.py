from sqlalchemy.orm import Session

from app.models.conversation import Conversation, Message


def create_conversation(
    db: Session,
    customer_id: int,
    primary_channel: str,
    current_channel: str,
    status: str,
) -> Conversation:
    conversation = Conversation(
        customer_id=customer_id,
        primary_channel=primary_channel,
        current_channel=current_channel,
        status=status,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def get_all_conversations(db: Session) -> list[Conversation]:
    return db.query(Conversation).all()


def get_conversation_by_id(db: Session, conversation_id: int) -> Conversation | None:
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def get_messages_by_conversation_id(db: Session, conversation_id: int) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )


def create_message(
    db: Session,
    conversation_id: int,
    channel: str,
    direction: str,
    content: str,
) -> Message:
    message = Message(
        conversation_id=conversation_id,
        channel=channel,
        direction=direction,
        content=content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
