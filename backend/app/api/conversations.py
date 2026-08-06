from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.booking import PROPOSAL_SLOTS
from app.core.config import settings
from app.db.database import get_db
from app.schemas.conversation import (
    ConversationCreate,
    ConversationProcessResponse,
    ConversationReplyResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.services.conversation_service import (
    create_conversation,
    create_message,
    get_all_conversations,
    get_conversation_by_id,
    get_messages_by_conversation_id,
)
from app.services.llm_service import LLMService

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


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
def get_messages_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    conversation = get_conversation_by_id(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    return get_messages_by_conversation_id(db, conversation_id)


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


@router.post("/{conversation_id}/reply", response_model=ConversationReplyResponse)
async def reply_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="LLM is not configured",
        )

    conversation = get_conversation_by_id(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db_messages = get_messages_by_conversation_id(db, conversation_id)

    messages = [
        {
            "role": "user" if message.direction == "inbound" else "assistant",
            "content": message.content,
        }
        for message in db_messages
    ]

    llm_service = LLMService()
    reply = await llm_service.reply(messages)

    message = create_message(
        db=db,
        conversation_id=conversation_id,
        channel=conversation.current_channel,
        direction="outbound",
        content=reply,
    )

    return ConversationReplyResponse(
        reply=reply,
        message_id=message.id,
    )


@router.post("/{conversation_id}/process", response_model=ConversationProcessResponse)
async def process_endpoint(
    conversation_id: int,
    db: Session = Depends(get_db),
):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="LLM is not configured",
        )

    conversation = get_conversation_by_id(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db_messages = get_messages_by_conversation_id(db, conversation_id)

    messages = [
        {
            "role": "user" if message.direction == "inbound" else "assistant",
            "content": message.content,
        }
        for message in db_messages
    ]

    llm_service = LLMService()
    reply = await llm_service.reply(messages)
    result = await llm_service.classify(messages)

    slots = PROPOSAL_SLOTS if result["intent"] == "BOOKING" else []

    return ConversationProcessResponse(
        reply=reply,
        intent=result["intent"],
        confidence=result["confidence"],
        slots=slots,
    )
