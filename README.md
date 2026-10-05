# citation-tracer

CS329Z course project: an agent that traces a scientific claim back through its citation chain
to the original evidence and identifies where the claim was distorted (e.g. a hedged finding
restated as fact). Compares three methods: single-hop checking, fixed-depth tracing
(LAGMiD-style), and agentic tracing (ours).

**Status:** scaffold. `single_hop` works on the committed sample; `fixed_depth`, `agentic`,
and the retrieval clients (Semantic Scholar, OpenAlex, GROBID) are stubs; Greenberg (2009) /
Sarol et al. data is not yet integrated.

## Install

Requires [uv](https://docs.astral.sh/uv/) (Python 3.12 is pinned in `.python-version`).

```bash
uv sync
```

## API keys and configuration

```bash
cp .env.example .env   # then edit; .env is gitignored
```

Defaults live in `config/default.yaml`; variables in `.env` (or the real environment) override
them. All LLM calls use one OpenAI-compatible endpoint:

| Variable | Overrides |
|---|---|
| `LLM_BASE_URL`, `LLM_MODEL`, `LLM_API_KEY` | `llm.*` (any OpenAI-compatible server) |
| `LLM_TEMPERATURE`, `LLM_MAX_TOKENS` | `llm.*` |
| `GROBID_URL`, `CACHE_PATH`, `LOG_DIR` | `grobid.url`, `cache.path`, `logging.dir` |
| `SEMANTIC_SCHOLAR_API_KEY`, `OPENALEX_EMAIL`, `NCBI_API_KEY` | retrieval keys (unused so far) |

Check the resolved config with `uv run citation-tracer show-config` (secrets are masked).

## Quick-start (API model, no llama.cpp needed)

Uses the committed synthetic sample in `data/sample/`. In `.env` set, for example:

```
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=<a chat model name>
LLM_API_KEY=<your key>
```

```bash
uv run python scripts/check_llm.py     # optional: ping the endpoint
uv run python scripts/quickstart.py    # trace one example with single_hop
```

This prints the verdict and writes a JSONL log to `runs/`.

### Local model (optional)

Serve a model with llama.cpp's `llama-server` (default port 8080) and leave `LLM_BASE_URL`
unset; set `LLM_MODEL` to match the served model. GROBID setup: TODO (needed only for PDF parsing).

## Reproducing evaluation

See [eval/README.md](eval/README.md). Currently:

```bash
uv run python eval/run_eval.py --method single_hop --examples data/sample/examples.json
```

Full Greenberg/Sarol runs: TODO once the data is integrated.

## Development

```bash
uv run pytest
uv run ruff check
```

## Layout

- `src/citation_tracer/` — `config`, `llm`, `cache` (SQLite), `runlog` (JSONL), `schemas`,
  `cli`, `retrieval/`, `methods/`
- `eval/`, `scripts/`, `config/`, `tests/`
- `data/sample/` committed; `data/raw|cache|processed`, `runs/` are gitignored

Every run's log starts with a header holding the full config and git commit hash; every agent
step is logged as one JSON line. External responses and parsed papers go in the SQLite cache.
