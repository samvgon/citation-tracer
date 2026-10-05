"""Settings: config/default.yaml, overridden by environment variables / .env."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from pydantic import BaseModel, SecretStr, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "default.yaml"
CONFIG_PATH_ENV = "CITATION_TRACER_CONFIG"

# Flat environment variable -> (section, field) in Settings.
ENV_MAP: dict[str, tuple[str, str]] = {
    "LLM_BASE_URL": ("llm", "base_url"),
    "LLM_MODEL": ("llm", "model"),
    "LLM_TEMPERATURE": ("llm", "temperature"),
    "LLM_MAX_TOKENS": ("llm", "max_tokens"),
    "LLM_API_KEY": ("llm", "api_key"),
    "GROBID_URL": ("grobid", "url"),
    "CACHE_PATH": ("cache", "path"),
    "LOG_DIR": ("logging", "dir"),
    "SEMANTIC_SCHOLAR_API_KEY": ("keys", "semantic_scholar"),
    "OPENALEX_EMAIL": ("keys", "openalex_email"),
    "NCBI_API_KEY": ("keys", "ncbi"),
}


class LLMConfig(BaseModel):
    base_url: str
    model: str
    temperature: float
    max_tokens: int
    timeout: float = 120.0
    api_key: SecretStr = SecretStr("sk-local")  # llama.cpp ignores the value


class GrobidConfig(BaseModel):
    url: str


class CacheConfig(BaseModel):
    path: Path


class LoggingConfig(BaseModel):
    dir: Path


class KeysConfig(BaseModel):
    semantic_scholar: SecretStr | None = None
    openalex_email: str | None = None
    ncbi: SecretStr | None = None


class FlatEnvSource(PydanticBaseSettingsSource):
    """Reads LLM_BASE_URL-style variables from the process env and a .env file."""

    def __init__(self, settings_cls: type[BaseSettings], env_file: Path | None) -> None:
        super().__init__(settings_cls)
        self._env_file = env_file

    def get_field_value(self, field: Any, field_name: str) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        values: dict[str, str | None] = {}
        if self._env_file and Path(self._env_file).is_file():
            values.update(dotenv_values(self._env_file))
        values.update(os.environ)  # real environment beats .env
        out: dict[str, dict[str, Any]] = {}
        for var, (section, field) in ENV_MAP.items():
            if values.get(var):  # blank entries (as in .env.example) don't override
                out.setdefault(section, {})[field] = values[var]
        return out


class Settings(BaseSettings):
    llm: LLMConfig
    grobid: GrobidConfig
    cache: CacheConfig
    logging: LoggingConfig
    keys: KeysConfig = KeysConfig()

    @model_validator(mode="after")
    def _resolve_paths(self) -> Settings:
        for p in (self.cache, self.logging):
            for name, value in p:
                if isinstance(value, Path) and not value.is_absolute():
                    setattr(p, name, PROJECT_ROOT / value)
        return self


def load_settings(config_path: Path | str | None = None, env_file: Path | None = None) -> Settings:
    """Load YAML config, then apply env/.env overrides (env wins)."""
    path = Path(config_path or os.environ.get(CONFIG_PATH_ENV) or DEFAULT_CONFIG_PATH)
    env_path = PROJECT_ROOT / ".env" if env_file is None else env_file

    class _Loaded(Settings):
        @classmethod
        def settings_customise_sources(cls, settings_cls, init_settings, *_args, **_kwargs):
            return (
                init_settings,
                FlatEnvSource(settings_cls, env_path),
                YamlConfigSettingsSource(settings_cls, yaml_file=path),
            )

    return _Loaded()
