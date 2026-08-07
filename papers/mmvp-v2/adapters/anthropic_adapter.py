"""Anthropic Claude backend adapter."""
from __future__ import annotations
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class AnthropicAdapter:
    def __init__(self, model: str = "claude-3-5-haiku-20241022", api_key: Optional[str] = None) -> None:
        self.model = model
        self.client = HttpClient("anthropic", api_key, env_var="ANTHROPIC_API_KEY")
        self.base = "https://api.anthropic.com/v1/messages"

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", 1024),
            "messages": [{"role": "user", "content": prompt}],
        }
        headers = {
            "x-api-key": self.client.api_key,
            "anthropic-version": "2023-06-01",
        }
        raw = self.client.post_json(self.base, payload, headers=headers)
        content_blocks = raw.get("content", [])
        text = "".join(block.get("text", "") for block in content_blocks if block.get("type") == "text")
        return Response(
            model=self.model,
            text=text,
            metadata={
                "provider": "anthropic",
                "stop_reason": raw.get("stop_reason"),
                "usage": raw.get("usage", {}),
                "raw_response": raw,
            },
        )
