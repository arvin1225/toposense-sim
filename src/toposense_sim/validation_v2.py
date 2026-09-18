"""Independent integrity, contract and replay checks for H2 artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

from .benchmark import _code_hash
from .benchmark_v2 import METHODS_H2, evaluate_trial_h2
from .config import CONFIRMATORY_FAMILIES


def _bool(value: str) -> bool:
    return value.lower() == "true"


def validate_h2_artifact(path: str | Path, *, quick: bool = False) -> dict[str, object]:
    root = Path(path)
    manifest_path = root / "manifest_h2.json"
    summary_path = root / "summary_h2.json"
    csv_path = root / "benchmark_h2.csv"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seed_start = int(manifest["seed_start"])
    seeds_per_family = int(manifest["seeds_per_family"])
    root_repo = Path(__file__).resolve().parents[2]
    pair_counts = Counter((row["family"], int(row["seed"]), row["method"]) for row in rows)
    expected_keys = {
        (family, seed, method)
        for family in CONFIRMATORY_FAMILIES
        for seed in range(seed_start, seed_start + seeds_per_family)
        for method in METHODS_H2
    }
    checks: dict[str, bool] = {
        "benchmark_hash": hashlib.sha256(csv_path.read_bytes()).hexdigest() == manifest["benchmark_sha256"],
        "summary_hash": hashlib.sha256(summary_path.read_bytes()).hexdigest() == manifest["summary_sha256"],
        "code_hash": _code_hash(root_repo) == manifest["code_sha256"],
        "row_count": len(rows) == int(manifest["row_count"]),
        "complete_pairing": set(pair_counts) == expected_keys and all(count == 1 for count in pair_counts.values()),
        "families": set(row["family"] for row in rows) == set(CONFIRMATORY_FAMILIES),
        "methods": set(row["method"] for row in rows) == set(METHODS_H2),
        "sample_budget": all(int(row["samples_used"]) <= int(manifest["maximum_sample_budget"]) for row in rows),
        "oracle_correct": all(_bool(row["correct"]) for row in rows if row["method"] == "oracle_dense"),
        "finite_rows": all(
            np.isfinite(float(row[key]))
            for row in rows
            for key in ("certificate_margin", "maximum_gap_rad", "support_residual", "uncertainty_covered_fraction")
        ),
        "propagation_contract": bool(summary["propagation_audit"]["T9_pass"]),
    }
    for method in METHODS_H2:
        subset = [row for row in rows if row["method"] == method]
        correct = sum(_bool(row["released"]) and _bool(row["correct"]) for row in subset)
        wrong = sum(_bool(row["released"]) and not _bool(row["correct"]) for row in subset)
        recorded = summary["overall"][method]
        checks[f"summary_counts_{method}"] = correct == int(recorded["correct_releases"]) and wrong == int(
            recorded["wrong_releases"]
        )
    if not quick:
        index = {(row["family"], int(row["seed"]), row["method"]): row for row in rows}
        replay_ok = True
        final_offset = seeds_per_family - 1
        for family, offset in (
            ("blur_crosstalk", 0),
            ("high_mode_na", min(3, final_offset)),
            ("compound_shift", min(6, final_offset)),
        ):
            seed = seed_start + offset
            for replay in evaluate_trial_h2(seed, family):
                stored = index[(family, seed, str(replay["method"]))]
                replay_ok &= _bool(stored["released"]) == bool(replay["released"])
                replay_ok &= int(stored["observed_winding"]) == int(replay["observed_winding"])
                replay_ok &= abs(float(stored["certificate_margin"]) - float(replay["certificate_margin"])) < 1e-12
        checks["row_replay_exact"] = bool(replay_ok)
    report = {
        "integrity": all(checks.values()),
        "registered_success": bool(summary["registered_success"]),
        "checks": checks,
        "manifest": manifest,
    }
    (root / "validation-report-h2.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report

