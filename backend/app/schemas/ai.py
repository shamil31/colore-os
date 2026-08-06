from pydantic import BaseModel


class AIReplyRequest(BaseModel):
    conversation_id: int


class AIReplyResponse(BaseModel):
    reply: str


class AIAnalyzeRequest(BaseModel):
    conversation_id: int


class AIAnalyzeResponse(BaseModel):
    intent: str
    confidence: float
