# citation-tracer

An agent that traces a scientific claim back through its citation chain to the original 
evidence and identifies where the claim was distorted (e.g. a hedged finding
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

Tested on Ubuntu 26.04, Ryzen AI Max+ 395, Radeon 8060S (RADV) via Vulkan. Build and models
live outside the repo (`~/llama.cpp`, `~/models`).

```bash
# 1. Build llama.cpp with Vulkan (needs cmake, ninja-build, libvulkan-dev, glslc, spirv-headers, libcurl4-openssl-dev)
git clone --depth 1 https://github.com/ggml-org/llama.cpp ~/llama.cpp
cmake -S ~/llama.cpp -B ~/llama.cpp/build -G Ninja -DGGML_VULKAN=ON -DCMAKE_BUILD_TYPE=Release
cmake --build ~/llama.cpp/build -j

# 2. Download models into ~/models (~22 GiB total)
B=https://huggingface.co; mkdir -p ~/models && cd ~/models
curl -fLO $B/unsloth/Qwen3-30B-A3B-Instruct-2507-GGUF/resolve/main/Qwen3-30B-A3B-Instruct-2507-Q4_K_M.gguf  # default, 17.3 GiB
curl -fLO $B/Qwen/Qwen3-8B-GGUF/resolve/main/Qwen3-8B-Q4_K_M.gguf                                           # small, 4.7 GiB
curl -fLO $B/nomic-ai/nomic-embed-text-v1.5-GGUF/resolve/main/nomic-embed-text-v1.5.Q8_0.gguf              # embeddings, 0.14 GiB

# 3. Serve on :8080 (served model name `local-model` matches config/default.yaml)
scripts/serve_llm.sh                          # Qwen3-30B-A3B-Instruct-2507
scripts/serve_llm.sh ~/models/Qwen3-8B-Q4_K_M.gguf   # or another model; extra args pass to llama-server
uv run python scripts/check_llm.py            # expect: reply: 'OK'
```

The script pins `--device Vulkan0` (the Radeon; `vulkaninfo` also lists llvmpipe, a CPU
renderer) and prints visible devices at startup. To confirm GPU use, run with `-lv 4` and look
for `using device Vulkan0 (Radeon 8060S ...)` and `offloaded 49/49 layers to GPU`.
Overrides: `PORT`, `CTX` (default 32768), `ALIAS`, `LLAMA_DIR`, `MODEL_DIR`.

Ollama can run alongside, but models it has loaded hold GPU memory (check `ollama ps`; it
unloads after its idle timeout). The script warns if Ollama has a model loaded.

The embedding model is downloaded but not served by `serve_llm.sh` yet; serve it separately with
`llama-server -m ~/models/nomic-embed-text-v1.5.Q8_0.gguf --embeddings --port 8081` when needed.

GROBID setup: TODO (needed only for PDF parsing).

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
