"""H2 value-of-information benchmark and propagation audit."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from .benchmark import _code_hash, _result_row
from .certificate import certify_observation, evaluate_baseline
from .config import CONFIRMATORY_FAMILIES
from .field import synthesize_field
from .metrics import paired_bootstrap_goodput, summarize_rows, wilson_upper
from .receiver import acquire_adaptive, acquire_uniform, acquire_value_adaptive
from .spectral_reference import audit_propagation


METHODS_H2 = (
    "uniform_support_certificate",
    "adaptive_support_certificate",
    "voi_support_certificate",
    "voi_no_support",
    "voi_global_support",
    "oracle_dense",
)


def evaluate_trial_h2(seed: int, family: str) -> list[dict[str, object]]:
    field = synthesize_field(seed, family)
    uniform = acquire_uniform(seed, family, field=field)
    adaptive = acquire_adaptive(seed, family, field=field)
    voi = acquire_value_adaptive(seed, family, field=field)
    evaluated = [
        (uniform, certify_observation(uniform, method="uniform_support_certificate", support_gate=True)),
        (adaptive, certify_observation(adaptive, method="adaptive_support_certificate", support_gate=True)),
        (voi, certify_observation(voi, method="voi_support_certificate", support_gate=True)),
        (voi, certify_observation(voi, method="voi_no_support", support_gate=False)),
        (
            voi,
            certify_observation(voi, method="voi_global_support", local_uncertainty=False, support_gate=True),
        ),
        (uniform, evaluate_baseline(uniform, "oracle_dense")),
    ]
    return [_result_row(field, observation, result) for observation, result in evaluated]


def summarize_h2(rows: list[dict[str, object]], bootstrap_resamples: int) -> dict[str, object]:
    overall = {method: summarize_rows([row for row in rows if row["method"] == method]) for method in METHODS_H2}
    by_family = {
        family: {
            method: summarize_rows([row for row in rows if row["family"] == family and row["method"] == method])
            for method in METHODS_H2
        }
        for family in CONFIRMATORY_FAMILIES
    }
    voi = [row for row in rows if row["method"] == "voi_support_certificate"]
    adaptive = [row for row in rows if row["method"] == "adaptive_support_certificate"]
    voi_summary = overall["voi_support_certificate"]
    adaptive_summary = overall["adaptive_support_certificate"]
    false_upper = wilson_upper(int(voi_summary["wrong_releases"]), int(voi_summary["n"]))
    paired = paired_bootstrap_goodput(voi, adaptive, resamples=bootstrap_resamples, seed=20260810)
    coverage_delta = float(voi_summary["coverage"]) - float(adaptive_summary["coverage"])
    goodput_relative = (float(voi_summary["certified_goodput"]) - float(adaptive_summary["certified_goodput"])) / max(
        float(adaptive_summary["certified_goodput"]), 1e-12
    )
    hypotheses = {
        "T5_pass": int(voi_summary["wrong_releases"]) == 0 and false_upper <= 0.01,
        "T6_pass": float(paired["difference"]) > 0.0 and float(paired["ci_low"]) > 0.0,
        "T7_pass": (coverage_delta >= 0.03 or goodput_relative >= 0.10)
        and int(voi_summary["wrong_releases"]) == 0
        and false_upper <= 0.01,
        "T8_pass": all(int(row["samples_used"]) <= 32 for row in rows if row["method"] != "oracle_dense"),
    }
    return {
        "overall": overall,
        "by_family": by_family,
        "voi_false_release_wilson_upper": false_upper,
        "paired_voi_minus_adaptive_goodput": paired,
        "coverage_difference": coverage_delta,
        "relative_goodput_improvement": goodput_relative,
        "hypotheses": hypotheses,
        "registered_success": all(hypotheses.values()),
    }


def run_h2_benchmark(
    output_dir: str | Path,
    *,
    seed_start: int = 2000,
    seeds_per_family: int = 100,
    bootstrap_resamples: int = 5000,
) -> dict[str, object]:
    if seed_start not in {500, 2000}:
        raise ValueError("registered H2 starts are 500 (exploratory) and 2000 (confirmatory)")
    if seed_start == 2000 and seeds_per_family != 100:
        raise ValueError("full H2 confirmation requires exactly 100 seeds per family")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows = [
        row
        for family in CONFIRMATORY_FAMILIES
        for seed in range(seed_start, seed_start + seeds_per_family)
        for row in evaluate_trial_h2(seed, family)
    ]
    csv_path = output / "benchmark_h2.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = summarize_h2(rows, bootstrap_resamples)
    audits = [audit_propagation(seed_start + offset, family).__dict__ for offset, family in enumerate(CONFIRMATORY_FAMILIES)]
    maximum_error = max(float(audit["maximum_complex_error"]) for audit in audits)
    summary["propagation_audit"] = {
        "cases": audits,
        "maximum_complex_error": maximum_error,
        "all_windings_match": all(bool(audit["winding_match"]) for audit in audits),
        "T9_pass": maximum_error < 1e-10 and all(bool(audit["winding_match"]) for audit in audits),
    }
    summary["registered_success"] = bool(summary["registered_success"] and summary["propagation_audit"]["T9_pass"])
    summary_path = output / "summary_h2.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    manifest = {
        "artifact": "TopoSense-Sim H2 confirmatory benchmark" if seed_start == 2000 else "TopoSense-Sim H2 exploratory benchmark",
        "protocol": "experiments/H2-value-of-information/protocol.md",
        "seed_start": seed_start,
        "seeds_per_family": seeds_per_family,
        "families": list(CONFIRMATORY_FAMILIES),
        "methods": list(METHODS_H2),
        "row_count": len(rows),
        "maximum_sample_budget": 32,
        "bootstrap_resamples": bootstrap_resamples,
        "voi_weights": {"global_gain": 1.0, "local_gain": 0.22, "gap_exploration": 0.018},
        "acquisition_schedule": "alternating support-recovery and VOI; support-recovery first",
        "code_sha256": _code_hash(root),
        "benchmark_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
    }
    (output / "manifest_h2.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"rows": rows, "summary": summary, "manifest": manifest}
