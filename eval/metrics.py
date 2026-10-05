"""Metrics for distortion detection (binary: is the claim distorted?)."""

from __future__ import annotations


def detection_metrics(preds: list[bool], golds: list[bool]) -> dict[str, float]:
    if len(preds) != len(golds):
        raise ValueError("preds and golds must have the same length")
    tp = sum(p and g for p, g in zip(preds, golds, strict=True))
    fp = sum(p and not g for p, g in zip(preds, golds, strict=True))
    fn = sum(g and not p for p, g in zip(preds, golds, strict=True))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    correct = sum(p == g for p, g in zip(preds, golds, strict=True))
    accuracy = correct / len(golds) if golds else 0.0
    return {
        "n": len(golds),
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }
