"""Semantic Scholar client (stub). Responses must be cached via citation_tracer.cache."""

from citation_tracer.schemas import Paper


def get_paper(paper_id: str) -> Paper:
    raise NotImplementedError


def get_references(paper_id: str) -> list[Paper]:
    raise NotImplementedError
