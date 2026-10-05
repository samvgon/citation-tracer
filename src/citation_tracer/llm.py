"""Single OpenAI-compatible client wrapper: every LLM call goes through here."""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from typing import Any

import openai
from openai import OpenAI
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from citation_tracer.config import LLMConfig

_RETRYABLE = (
    openai.APIConnectionError,
    openai.APITimeoutError,
    openai.RateLimitError,
    openai.InternalServerError,
)


@dataclass
class LLMResponse:
    text: str
    model: str
    latency_s: float
    usage: dict[str, int] = field(default_factory=dict)


class LLMClient:
    def __init__(self, cfg: LLMConfig) -> None:
        self.cfg = cfg
        self._client = OpenAI(
            base_url=cfg.base_url,
            api_key=cfg.api_key.get_secret_value(),
            timeout=cfg.timeout,
            max_retries=0,  # retries are handled by tenacity below
        )

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(4),
        wait=wait_exponential(min=1, max=20),
        reraise=True,
    )
    def chat(self, messages: list[dict[str, str]], **overrides: Any) -> LLMResponse:
        params: dict[str, Any] = {
            "model": self.cfg.model,
            "temperature": self.cfg.temperature,
            "max_tokens": self.cfg.max_tokens,
            **overrides,
        }
        start = time.perf_counter()
        resp = self._client.chat.completions.create(messages=messages, **params)
        usage = resp.usage.model_dump() if resp.usage else {}
        return LLMResponse(
            text=resp.choices[0].message.content or "",
            model=resp.model,
            latency_s=time.perf_counter() - start,
            usage={k: v for k, v in usage.items() if isinstance(v, int)},
        )


def parse_json(text: str) -> Any:
    """Parse a JSON object from model output, tolerating code fences and surrounding prose."""
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))
