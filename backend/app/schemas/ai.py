from pydantic import BaseModel


class AIReplyRequest(BaseModel):
    conversation_id: int


class AIReplyResponse(BaseModel):
    reply: str
