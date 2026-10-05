"""Run one method over a labelled example file and report detection metrics.

    uv run python eval/run_eval.py --method single_hop --examples data/sample/examples.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from metrics import detection_metrics

from citation_tracer.config import PROJECT_ROOT, load_settings
from citation_tracer.llm import LLMClient
from citation_tracer.methods import METHODS, get_method
from citation_tracer.retrieval.sample import load_examples
from citation_tracer.runlog import RunLogger


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--method", choices=sorted(METHODS), required=True)
    ap.add_argument("--examples", type=Path, default=PROJECT_ROOT / "data/sample/examples.json")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--config", type=Path)
    args = ap.parse_args()

    settings = load_settings(args.config)
    examples = [e for e in load_examples(args.examples) if e.gold][: args.limit]
    log = RunLogger(settings.logging.dir, settings, name=f"eval-{args.method}")
    llm, method = LLMClient(settings.llm), get_method(args.method)

    preds, golds = [], []
    for ex in examples:
        result = method(ex, llm, log)
        log.log("result", **result.model_dump())
        preds.append(result.distorted)
        golds.append(ex.gold.distorted)

    metrics = detection_metrics(preds, golds)
    log.log("metrics", **metrics)
    out = log.path.with_suffix(".metrics.json")
    out.write_text(json.dumps({"method": args.method, "examples": str(args.examples), **metrics}))
    print(json.dumps(metrics, indent=2))
    print(f"log: {log.path}\nmetrics: {out}")


if __name__ == "__main__":
    main()
