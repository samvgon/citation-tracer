# Citation-chain tracing agent (CS329Z course project)

## Goal
Build and evaluate an agent that traces a scientific claim back through its citation chain to the original evidence and identifies where the claim was distorted (e.g., a hedged finding restated as fact).

## Baselines to compare
1. Single-hop citation checking
2. Fixed-depth tracing (LAGMiD-style)
3. Agentic tracing (our contribution)

## Ground truth
Greenberg (2009) BMJ citation network; Sarol et al. (ASIS&T 2025) as prior baseline.

## Environment
Ubuntu on a GMKtec EVO-X2 (Ryzen AI Max+ 395, Radeon 8060S iGPU, 128 GB unified memory, 64 GB allocated to GPU). Local models will be served via llama.cpp with an OpenAI-compatible API.

## Engineering rules
- All LLM calls go through one OpenAI-compatible endpoint (configurable), so local and API models are swappable.
- Cache every external API response and parsed paper locally (SQLite or DuckDB).
- Log every agent step (retrieved docs, chosen citations, reasoning) as JSONL.
- Keep README.md current: install, API keys, quick-start on one example, how to reproduce evaluation. Reproducibility is graded.
- API keys live only in .env, never in code.
- Only work inside this repository.
