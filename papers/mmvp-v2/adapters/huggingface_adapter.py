"""HuggingFace Inference API backend adapter."""
from __future__ import annotations
from typing import Any, Dict, Optional
from ..adapters.protocol import Response
from .http_client import HttpClient


class HuggingFaceAdapter:
    def __init__(self, model: str = "mistralai/Mistral-7B-Instruct-v0.2", api_key: Optional[str] = None) -> None:
        self.model = model
        self.client = HttpClient("huggingface", api_key, env_var="HF_API_TOKEN")
        self.base = f"https://api-inference.huggingface.co/models/{model}"

    def complete(self, prompt: str, **kwargs: Any) -> Response:
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": kwargs.get("max_tokens", 1024)},
        }
        raw = self.client.post_json(self.base, payload)
        if isinstance(raw, list) and raw:
            text = raw[0].get("generated_text", "")
        elif isinstance(raw, dict):
            text = raw.get("generated_text", "") or raw.get("choices", [{}])[0].get("text", "")
        else:
            text = str(raw)
        return Response(
            model=self.model,
            text=text,
            metadata={
                "provider": "huggingface",
                "raw_response": raw,
            },
        )
