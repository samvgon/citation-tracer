"""Command line entry point: `citation-tracer {show-config,trace}`."""

from __future__ import annotations

import argparse
from pathlib import Path

from citation_tracer.config import PROJECT_ROOT, load_settings
from citation_tracer.llm import LLMClient
from citation_tracer.methods import METHODS, get_method
from citation_tracer.retrieval.sample import load_examples
from citation_tracer.runlog import RunLogger

DEFAULT_EXAMPLES = PROJECT_ROOT / "data" / "sample" / "examples.json"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="citation-tracer")
    parser.add_argument("--config", type=Path, help="YAML config (default: config/default.yaml)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("show-config", help="print the resolved config (secrets masked)")
    t = sub.add_parser("trace", help="trace one example")
    t.add_argument("--method", choices=sorted(METHODS), default="single_hop")
    t.add_argument("--examples", type=Path, default=DEFAULT_EXAMPLES)
    t.add_argument("--id", help="example id (default: first in file)")
    args = parser.parse_args(argv)

    settings = load_settings(args.config)
    if args.command == "show-config":
        print(settings.model_dump_json(indent=2))
        return

    examples = load_examples(args.examples)
    example = next((e for e in examples if e.id == args.id), None) if args.id else examples[0]
    if example is None:
        parser.error(f"no example with id {args.id!r} in {args.examples}")
    log = RunLogger(settings.logging.dir, settings, name=args.method)
    result = get_method(args.method)(example, LLMClient(settings.llm), log)
    log.log("result", **result.model_dump())
    print(f"claim: {example.claim.text}")
    print(result.model_dump_json(indent=2))
    print(f"log: {log.path}")
    if example.gold:
        print(f"gold: distorted={example.gold.distorted} ({example.gold.distortion_type})")
