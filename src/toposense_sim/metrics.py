"""Selective receiver metrics, Wilson bounds and paired family bootstrap."""

from __future__ import annotations

import numpy as np


BITS_PER_SYMBOL = float(np.log2(5.0))


def summarize_rows(rows: list[dict[str, object]]) -> dict[str, float | int]:
    if not rows:
        return {}
    released = np.array([bool(row["released"]) for row in rows])
    correct = np.array([bool(row["correct"]) for row in rows])
    false_release = released & ~correct
    return {
        "n": len(rows),
        "coverage": float(np.mean(released)),
        "erasure_rate": float(np.mean(~released)),
        "false_release_probability": float(np.mean(false_release)),
        "conditional_error": float(np.mean(~correct[released])) if np.any(released) else 0.0,
        "certified_goodput": float(np.mean(released & correct) * BITS_PER_SYMBOL),
        "mean_samples_used": float(np.mean([int(row["samples_used"]) for row in rows])),
        "support_violation_rate": float(np.mean([bool(row["support_violation_truth"]) for row in rows])),
        "uncertainty_coverage": float(np.mean([float(row["uncertainty_covered_fraction"]) for row in rows])),
        "wrong_releases": int(np.sum(false_release)),
        "correct_releases": int(np.sum(released & correct)),
    }


def wilson_upper(errors: int, total: int, confidence: float = 0.95) -> float:
    if total <= 0:
        return 1.0
    z = 1.6448536269514722 if confidence == 0.95 else 1.959963984540054
    p = errors / total
    denominator = 1.0 + z * z / total
    center = p + z * z / (2.0 * total)
    radius = z * np.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    return float((center + radius) / denominator)


def paired_bootstrap_goodput(
    rows_a: list[dict[str, object]],
    rows_b: list[dict[str, object]],
    *,
    resamples: int = 5000,
    seed: int = 20260803,
) -> dict[str, float]:
    keys_a = [(str(row["family"]), int(row["seed"])) for row in rows_a]
    keys_b = [(str(row["family"]), int(row["seed"])) for row in rows_b]
    if keys_a != keys_b:
        raise ValueError("paired rows must be aligned")
    good_a = np.array([bool(row["released"]) and bool(row["correct"]) for row in rows_a], dtype=float) * BITS_PER_SYMBOL
    good_b = np.array([bool(row["released"]) and bool(row["correct"]) for row in rows_b], dtype=float) * BITS_PER_SYMBOL
    families = np.array([str(row["family"]) for row in rows_a])
    family_indices = [np.flatnonzero(families == family) for family in sorted(set(families))]
    rng = np.random.default_rng(seed)
    values = np.empty(resamples, dtype=float)
    for iteration in range(resamples):
        sampled = np.concatenate([rng.choice(indices, size=len(indices), replace=True) for indices in family_indices])
        values[iteration] = float(np.mean(good_a[sampled] - good_b[sampled]))
    difference = float(np.mean(good_a - good_b))
    return {"difference": difference, "ci_low": float(np.quantile(values, 0.025)), "ci_high": float(np.quantile(values, 0.975))}
