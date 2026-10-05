"""Data models shared by retrieval, methods and evaluation."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Paper(BaseModel):
    id: str
    title: str
    text: str = ""  # abstract or parsed full text


class Claim(BaseModel):
    id: str
    text: str  # the sentence as written in the citing paper
    citing_paper_id: str


class Gold(BaseModel):
    distorted: bool
    distortion_type: str | None = None


class Example(BaseModel):
    """One claim plus the paper(s) it cites; gold label is optional."""

    id: str
    claim: Claim
    cited_papers: list[Paper]
    gold: Gold | None = None


class Distortion(BaseModel):
    type: str  # e.g. "certainty_inflation"
    explanation: str
    paper_id: str | None = None  # where in the chain the distortion was introduced


class TraceResult(BaseModel):
    example_id: str
    method: str
    distorted: bool
    distortion: Distortion | None = None
    chain: list[str] = Field(default_factory=list)  # paper ids visited, in order
    n_llm_calls: int = 0
