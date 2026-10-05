"""GROBID PDF parsing (stub). Parsed papers must be cached via citation_tracer.cache."""

from pathlib import Path

from citation_tracer.schemas import Paper


def parse_pdf(pdf_path: Path) -> Paper:
    raise NotImplementedError
