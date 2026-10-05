"""Load examples from committed JSON files (e.g. data/sample/examples.json)."""

from __future__ import annotations

import json
from pathlib import Path

from citation_tracer.schemas import Example


def load_examples(path: Path | str) -> list[Example]:
    return [Example.model_validate(e) for e in json.loads(Path(path).read_text())]
