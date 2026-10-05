"""Trace one committed sample example end-to-end (needs only an OpenAI-compatible endpoint)."""

from citation_tracer.cli import main

if __name__ == "__main__":
    main(["trace", "--method", "single_hop", "--id", "toy-001"])
