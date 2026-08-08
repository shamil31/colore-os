from __future__ import annotations

from typing import Any

from openai import AsyncOpenAI

from app.integrations.gateway.base_connector import BaseConnector


class OpenAIConnector(BaseConnector):
    integration_name = "openai"
    CHAT_COMPLETIONS_CAPABILITY = "openai.chat.completions.create"

    def __init__(self, api_key: str) -> None:
        self.client = AsyncOpenAI(api_key=api_key)

    @property
    def capabilities(self) -> set[str]:
        return {self.CHAT_COMPLETIONS_CAPABILITY}

    def execute(self, capability: str, *, payload: dict[str, Any] | None = None) -> Any:
        if capability != self.CHAT_COMPLETIONS_CAPABILITY:
            raise ValueError(f"Unsupported capability for OpenAI connector: {capability}")

        body = payload or {}
        if "model" not in body:
            raise ValueError("Missing required payload field 'model'")
        if "messages" not in body:
            raise ValueError("Missing required payload field 'messages'")

        request: dict[str, Any] = {
            "model": body["model"],
            "messages": body["messages"],
        }
        if "response_format" in body and body["response_format"] is not None:
            request["response_format"] = body["response_format"]

        return self.client.chat.completions.create(**request)
