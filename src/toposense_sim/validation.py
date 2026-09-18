"""Independent artifact integrity and deterministic replay checks."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .benchmark import METHODS, evaluate_trial
from .config import CONFIRMATORY_FAMILIES
from .field import synthesize_field


def _bool(value: str) -> bool:
    return value.lower() == "true"


def validate_artifact(path: str | Path, *, quick: bool = False) -> dict[str, object]:
    root = Path(path)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    with (root / "benchmark.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    seed_start = int(manifest["seed_start"])
    checks = {
        "benchmark_hash": hashlib.sha256((root / "benchmark.csv").read_bytes()).hexdigest() == manifest["benchmark_sha256"],
        "summary_hash": hashlib.sha256((root / "summary.json").read_bytes()).hexdigest() == manifest["summary_sha256"],
        "row_count": len(rows) == int(manifest["row_count"]),
        "seed_range": all(seed_start <= int(row["seed"]) < seed_start + int(manifest["seeds_per_family"]) for row in rows),
        "families": set(row["family"] for row in rows) == set(CONFIRMATORY_FAMILIES),
        "methods": set(row["method"] for row in rows) == set(METHODS),
        "sample_budget": all(int(row["samples_used"]) <= int(manifest["maximum_sample_budget"]) for row in rows),
        "finite_metrics": all(np.isfinite(float(value)) for metrics in summary["overall"].values() for value in metrics.values() if isinstance(value, (int, float))),
        "balanced_symbols": all(
            len({int(row["true_winding"]) for row in rows if row["family"] == family and row["method"] == "polygon_unconditional"}) == 5
            for family in CONFIRMATORY_FAMILIES
        ),
        "oracle_correct": all(_bool(row["correct"]) for row in rows if row["method"] == "oracle_dense"),
    }
    field_a = synthesize_field(seed_start, "compound_shift")
    field_b = synthesize_field(seed_start, "compound_shift")
    checks["field_replay_exact"] = bool(np.array_equal(field_a.received_stokes, field_b.received_stokes))
    if not quick:
        index = {(row["family"], int(row["seed"]), row["method"]): row for row in rows}
        replay_ok = True
        final_offset = int(manifest["seeds_per_family"]) - 1
        for family, offset in (("blur_crosstalk", 0), ("sector_dropout", min(3, final_offset)), ("compound_shift", min(6, final_offset))):
            seed = seed_start + offset
            for replay in evaluate_trial(seed, family):
                stored = index[(family, seed, replay["method"])]
                replay_ok &= _bool(stored["released"]) == bool(replay["released"])
                replay_ok &= int(stored["observed_winding"]) == int(replay["observed_winding"])
                replay_ok &= abs(float(stored["certificate_margin"]) - float(replay["certificate_margin"])) < 1e-12
        checks["row_replay_exact"] = bool(replay_ok)
    report = {"integrity": all(checks.values()), "registered_success": bool(summary["registered_success"]), "checks": checks, "manifest": manifest}
    (root / "validation-report.json").write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return report
