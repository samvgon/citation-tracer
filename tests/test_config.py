import json

import pytest

from citation_tracer.cache import Cache
from citation_tracer.config import ENV_MAP, PROJECT_ROOT, load_settings
from citation_tracer.runlog import RunLogger


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for var in ENV_MAP:
        monkeypatch.delenv(var, raising=False)


def test_defaults_from_yaml(tmp_path):
    s = load_settings(env_file=tmp_path / "missing.env")
    assert s.llm.base_url == "http://localhost:8080/v1"
    assert s.cache.path == PROJECT_ROOT / "data/cache/cache.sqlite"


def test_env_and_dotenv_override(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("LLM_MODEL=from-dotenv\nLLM_BASE_URL=http://dotenv/v1\nLLM_API_KEY=\n")
    monkeypatch.setenv("LLM_MODEL", "from-env")
    s = load_settings(env_file=env_file)
    assert s.llm.model == "from-env"  # real env beats .env
    assert s.llm.base_url == "http://dotenv/v1"
    assert s.llm.api_key.get_secret_value() == "sk-local"  # blank value ignored


def test_runlog_header_masks_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "sk-secret")
    s = load_settings(env_file=tmp_path / "missing.env")
    log = RunLogger(tmp_path, s, name="t")
    log.log("step", note="hi")
    header, step = (json.loads(line) for line in log.path.read_text().splitlines())
    assert header["type"] == "header" and header["git_commit"]
    assert header["config"]["llm"]["model"] == s.llm.model
    assert "sk-secret" not in log.path.read_text()
    assert step["seq"] == 1


def test_cache_roundtrip(tmp_path):
    c = Cache(tmp_path / "sub" / "c.sqlite")
    assert c.get("api", "k") is None
    c.set("api", "k", {"a": [1]})
    assert c.get("api", "k") == {"a": [1]}
