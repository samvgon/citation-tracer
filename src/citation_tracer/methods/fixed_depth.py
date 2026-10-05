"""Baseline 2: fixed-depth tracing (LAGMiD-style). Not implemented yet."""

from citation_tracer.llm import LLMClient
from citation_tracer.runlog import RunLogger
from citation_tracer.schemas import Example, TraceResult


def trace(example: Example, llm: LLMClient, log: RunLogger) -> TraceResult:
    raise NotImplementedError("fixed-depth tracing is not implemented yet")
