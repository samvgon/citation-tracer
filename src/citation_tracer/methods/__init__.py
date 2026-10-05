"""Tracing methods. Each exposes trace(example, llm, log) -> TraceResult."""

from __future__ import annotations

from collections.abc import Callable

from citation_tracer.llm import LLMClient
from citation_tracer.methods import agentic, fixed_depth, single_hop
from citation_tracer.runlog import RunLogger
from citation_tracer.schemas import Example, TraceResult

Method = Callable[[Example, LLMClient, RunLogger], TraceResult]

METHODS: dict[str, Method] = {
    "single_hop": single_hop.trace,
    "fixed_depth": fixed_depth.trace,
    "agentic": agentic.trace,
}


def get_method(name: str) -> Method:
    try:
        return METHODS[name]
    except KeyError:
        raise ValueError(f"unknown method {name!r}; choose from {sorted(METHODS)}") from None
