from pydantic import BaseModel


class BookingProposalRequest(BaseModel):
    conversation_id: int
