from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_all_conversations,
    get_conversation_by_id,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.post("", response_model=ConversationResponse)
def create_conversation_endpoint(
    conversation: ConversationCreate,
    db: Session = Depends(get_db),
):
    return create_conversation(
        db=db,
        customer_id=conversation.customer_id,
        primary_channel=conversation.primary_channel,
        current_channel=conversation.current_channel,
        status=conversation.status,
    )


@router.get("", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
):
    return get_all_conversations(db)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return conversation


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
def create_message_endpoint(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return create_message(
        db=db,
        conversation_id=conversation_id,
        channel=message.channel,
        direction=message.direction,
        content=message.content,
    )
