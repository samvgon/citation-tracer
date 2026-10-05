"""JSONL run logger. Line 1 is a header with the full config and git commit."""

from __future__ import annotations

import json
import subprocess
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from citation_tracer.config import PROJECT_ROOT


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip()


class RunLogger:
    def __init__(self, log_dir: Path | str, config: BaseModel, name: str = "run") -> None:
        now = datetime.now(UTC)
        self.run_id = f"{now:%Y%m%dT%H%M%SZ}-{name}-{uuid.uuid4().hex[:6]}"
        self.path = Path(log_dir) / f"{self.run_id}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._seq = 0
        status = _git("status", "--porcelain")
        self._write(
            {
                "type": "header",
                "run_id": self.run_id,
                "name": name,
                "timestamp": now.isoformat(),
                "git_commit": _git("rev-parse", "HEAD") or "unknown",
                "git_dirty": bool(status) if status is not None else None,
                "config": config.model_dump(mode="json"),  # SecretStr is masked in json mode
            }
        )

    def log(self, event: str, **fields: Any) -> None:
        """Append one step (retrieved docs, chosen citations, reasoning, ...)."""
        self._seq += 1
        self._write(
            {
                "type": event,
                "seq": self._seq,
                "timestamp": datetime.now(UTC).isoformat(),
                **fields,
            }
        )

    def _write(self, record: dict[str, Any]) -> None:
        with self.path.open("a") as f:
            f.write(json.dumps(record, default=str) + "\n")
