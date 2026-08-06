import json

from openai import AsyncOpenAI

from app.core.config import settings

INTENTS = [
    "BOOKING",
    "PRICE",
    "CONSULTATION",
    "RESCHEDULE",
    "CANCEL",
    "COMPLAINT",
    "OTHER",
]

CLASSIFY_PROMPT = (
    "You classify the client's intent in a beauty salon conversation. "
    f"Allowed intents: {', '.join(INTENTS)}. "
    "Use OTHER when nothing else applies. "
    'Answer with JSON only: {"intent": "<INTENT>", "confidence": <float between 0 and 1>}.'
)


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def reply(self, messages: list[dict]) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content

    async def classify(self, messages: list[dict]) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": CLASSIFY_PROMPT}] + messages,
            response_format={"type": "json_object"},
        )

        data = json.loads(response.choices[0].message.content)

        intent = data.get("intent")
        if intent not in INTENTS:
            intent = "OTHER"

        try:
            confidence = float(data.get("confidence"))
        except (TypeError, ValueError):
            confidence = 0.0

        return {"intent": intent, "confidence": confidence}
