"""Ping the configured LLM endpoint."""

from citation_tracer.config import load_settings
from citation_tracer.llm import LLMClient

if __name__ == "__main__":
    cfg = load_settings().llm
    print(f"endpoint: {cfg.base_url}  model: {cfg.model}")
    messages = [{"role": "user", "content": "Reply with the word OK."}]
    resp = LLMClient(cfg).chat(messages, max_tokens=16)
    print(f"reply: {resp.text.strip()!r} ({resp.latency_s:.2f}s)")
