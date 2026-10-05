"""SQLite cache for external API responses and parsed papers."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any


def make_key(*parts: Any) -> str:
    """Stable key from arbitrary JSON-serialisable parts."""
    blob = json.dumps(parts, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode()).hexdigest()


class Cache:
    """Namespaced key -> JSON value store, e.g. namespaces "api" and "paper"."""

    def __init__(self, path: Path | str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path)
        self._db.execute(
            "CREATE TABLE IF NOT EXISTS kv ("
            "namespace TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, "
            "created_at REAL NOT NULL, PRIMARY KEY (namespace, key))"
        )
        self._db.commit()

    def get(self, namespace: str, key: str) -> Any | None:
        row = self._db.execute(
            "SELECT value FROM kv WHERE namespace = ? AND key = ?", (namespace, key)
        ).fetchone()
        return json.loads(row[0]) if row else None

    def set(self, namespace: str, key: str, value: Any) -> None:
        self._db.execute(
            "INSERT OR REPLACE INTO kv VALUES (?, ?, ?, ?)",
            (namespace, key, json.dumps(value), time.time()),
        )
        self._db.commit()

    def close(self) -> None:
        self._db.close()
