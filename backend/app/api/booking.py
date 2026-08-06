from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.booking import BookingProposalRequest
from app.services.conversation_service import (
    get_conversation_by_id,
    get_messages_by_conversation_id,
)
from app.services.llm_service import LLMService

router = APIRouter(
    prefix="/booking",
    tags=["Booking"],
)

PROPOSAL_SLOTS = [
    "Завтра 14:00",
    "Завтра 16:00",
    "Пятница 11:00",
]


@router.post("/proposal", response_model=List[str])
async def booking_proposal_endpoint(
    request: BookingProposalRequest,
    db: Session = Depends(get_db),
):
    if not settings.OPENAI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="LLM is not configured",
        )

    conversation = get_conversation_by_id(db, request.conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found",
        )

    db_messages = get_messages_by_conversation_id(db, request.conversation_id)

    messages = [
        {
            "role": "user" if message.direction == "inbound" else "assistant",
            "content": message.content,
        }
        for message in db_messages
    ]

    llm_service = LLMService()
    result = await llm_service.classify(messages)

    if result["intent"] != "BOOKING":
        raise HTTPException(
            status_code=409,
            detail="Intent is not BOOKING",
        )

    return PROPOSAL_SLOTS
