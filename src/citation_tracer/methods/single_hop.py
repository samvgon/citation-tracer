"""Baseline 1: single-hop citation checking.

Compares the claim as written against the text of the paper it cites, one hop only.
"""

from __future__ import annotations

from citation_tracer.llm import LLMClient, parse_json
from citation_tracer.runlog import RunLogger
from citation_tracer.schemas import Distortion, Example, TraceResult

SYSTEM = (
    "You check whether a citing sentence faithfully represents the paper it cites. "
    "Flag distortions such as a hedged or tentative finding restated as established fact, "
    "overgeneralisation, or an association restated as causation. "
    'Reply with JSON only: {"distorted": bool, "type": str|null, "explanation": str}.'
)


def trace(example: Example, llm: LLMClient, log: RunLogger) -> TraceResult:
    cited = example.cited_papers[0]
    messages = [
        {"role": "system", "content": SYSTEM},
        {
            "role": "user",
            "content": (
                f"Citing sentence:\n{example.claim.text}\n\n"
                f"Cited paper: {cited.title}\n{cited.text}"
            ),
        },
    ]
    resp = llm.chat(messages)
    verdict = parse_json(resp.text)
    log.log(
        "step",
        example_id=example.id,
        method="single_hop",
        retrieved=[cited.id],
        messages=messages,
        response=resp.text,
        usage=resp.usage,
        latency_s=resp.latency_s,
    )
    distorted = bool(verdict.get("distorted"))
    return TraceResult(
        example_id=example.id,
        method="single_hop",
        distorted=distorted,
        distortion=(
            Distortion(
                type=verdict.get("type") or "other",
                explanation=verdict.get("explanation", ""),
                paper_id=cited.id,
            )
            if distorted
            else None
        ),
        chain=[example.claim.citing_paper_id, cited.id],
        n_llm_calls=1,
    )
