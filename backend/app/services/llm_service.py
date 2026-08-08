import json

from app.core.config import settings
from app.integrations.connectors.openai_connector import OpenAIConnector
from app.integrations.gateway.factory import get_connector_gateway

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
        self.gateway = get_connector_gateway()
        self.model = settings.OPENAI_MODEL

        if settings.OPENAI_API_KEY:
            try:
                self.gateway.integration_registry.get("openai")
            except KeyError:
                self.gateway.register(OpenAIConnector(api_key=settings.OPENAI_API_KEY))

    async def reply(self, messages: list[dict]) -> str:
        response = await self.gateway.execute_async(
            "openai",
            OpenAIConnector.CHAT_COMPLETIONS_CAPABILITY,
            payload={
                "model": self.model,
                "messages": messages,
            },
        )
        return response.choices[0].message.content

    async def classify(self, messages: list[dict]) -> dict:
        response = await self.gateway.execute_async(
            "openai",
            OpenAIConnector.CHAT_COMPLETIONS_CAPABILITY,
            payload={
                "model": self.model,
                "messages": [{"role": "system", "content": CLASSIFY_PROMPT}] + messages,
                "response_format": {"type": "json_object"},
            },
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
