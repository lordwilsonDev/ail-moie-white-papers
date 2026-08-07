"""DeepSeek-compatible backend adapter."""
from __future__ import annotations
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class DeepSeekAdapter:
    def __init__(self, model: str = "deepseek-chat", api_key: Optional[str] = None) -> None:
        self.model = model
        self.client = HttpClient("deepseek", api_key, env_var="DEEPSEEK_API_KEY")
        self.base = "https://api.deepseek.com/v1/chat/completions"

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": kwargs.get("max_tokens", 1024),
        }
        raw = self.client.post_json(self.base, payload)
        choice = raw["choices"][0]["message"]["content"]
        return Response(
            model=self.model,
            text=choice,
            metadata={
                "provider": "deepseek",
                "finish_reason": raw["choices"][0].get("finish_reason"),
                "raw_response": raw,
            },
        )
