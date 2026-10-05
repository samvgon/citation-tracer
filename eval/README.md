# Evaluation

Ground truth: Greenberg (2009) BMJ citation network; prior baseline: Sarol et al. (ASIS&T 2025).
The full datasets are **not yet downloaded or converted** (planned location: `data/raw/` →
`data/processed/`, both gitignored).

## Reproduce (currently on the committed synthetic sample)

```bash
cp .env.example .env        # set LLM_BASE_URL / LLM_MODEL / LLM_API_KEY
uv sync
uv run python eval/run_eval.py --method single_hop --examples data/sample/examples.json
```

Each run writes `runs/<run_id>.jsonl` (first line: full config + git commit) and
`runs/<run_id>.metrics.json`. Methods: `single_hop` (implemented), `fixed_depth`, `agentic`
(stubs). Metrics are binary distortion detection: accuracy, precision, recall, F1
(`eval/metrics.py`). Sample numbers are a smoke test, not results.
