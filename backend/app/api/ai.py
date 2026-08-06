from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.schemas.ai import (
    AIAnalyzeRequest,
    AIAnalyzeResponse,
    AIReplyRequest,
    AIReplyResponse,
)
from app.services.conversation_service import (
    get_conversation_by_id,
    get_messages_by_conversation_id,
)
from app.services.llm_service import LLMService

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/reply", response_model=AIReplyResponse)
async def ai_reply_endpoint(
    request: AIReplyRequest,
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
    reply = await llm_service.reply(messages)

    return AIReplyResponse(reply=reply)


@router.post("/analyze", response_model=AIAnalyzeResponse)
async def ai_analyze_endpoint(
    request: AIAnalyzeRequest,
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

    return AIAnalyzeResponse(
        intent=result["intent"],
        confidence=result["confidence"],
    )
