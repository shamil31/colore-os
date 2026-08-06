from datetime import datetime
from pydantic import BaseModel


class MessageCreate(BaseModel):
    channel: str
    direction: str
    content: str


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    channel: str
    direction: str
    content: str
    created_at: datetime


class ConversationReplyResponse(BaseModel):
    reply: str
    message_id: int


class ConversationCreate(BaseModel):
    customer_id: int
    primary_channel: str
    current_channel: str
    status: str


class ConversationResponse(BaseModel):
    id: int
    customer_id: int
    primary_channel: str
    current_channel: str
    status: str
    created_at: datetime
    updated_at: datetime
