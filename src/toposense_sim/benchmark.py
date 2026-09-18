"""Frozen composed-shift benchmark and immutable artifact export."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from .certificate import CertificateResult, certify_observation, evaluate_baseline
from .config import CONFIRMATORY_FAMILIES
from .field import OpticalField, synthesize_field
from .metrics import paired_bootstrap_goodput, summarize_rows, wilson_upper
from .receiver import Observation, acquire_adaptive, acquire_uniform


METHODS = (
    "polygon_unconditional",
    "margin_only",
    "global_certificate",
    "local_certificate",
    "uniform_support_certificate",
    "adaptive_support_certificate",
    "adaptive_no_support",
    "adaptive_no_calibration",
    "adaptive_global_support",
    "oracle_dense",
)


def _result_row(field: OpticalField, observation: Observation, result: CertificateResult) -> dict[str, object]:
    released = result.decision.value == "RELEASE"
    config = field.config
    support_truth = bool(
        field.ideal_high_mode_fraction > 0.08
        or config.dropout_width_rad > 0.0
        or field.received_dense_winding != field.true_winding
        or config.na_cutoff_mode < config.registered_mode_limit
    )
    row: dict[str, object] = {
        "family": config.family,
        "seed": field.seed,
        "method": result.method,
        "true_winding": field.true_winding,
        "received_dense_winding": field.received_dense_winding,
        "observed_winding": result.observed_winding,
        "released_winding": result.winding if result.winding is not None else "",
        "released": released,
        "correct": result.correct,
        "false_release": released and not result.correct,
        "samples_used": observation.attempted_count,
        "valid_samples": len(observation.stokes),
        "dropped_samples": observation.dropped_count,
        "uncertainty_covered_fraction": observation.uncertainty_covered_fraction,
        "certificate_margin": result.certificate_margin,
        "minimum_projected_radius": result.minimum_projected_radius,
        "maximum_gap_rad": result.maximum_gap_rad,
        "maximum_phase_step_rad": result.maximum_phase_step_rad,
        "support_residual": result.support_residual,
        "edge_mode_fraction": result.edge_mode_fraction,
        "transfer_headroom": result.transfer_headroom,
        "support_violation_truth": support_truth,
        "topology_changed_by_receiver": field.received_dense_winding != field.true_winding,
        "ideal_high_mode_fraction": field.ideal_high_mode_fraction,
        "received_high_mode_fraction": field.received_high_mode_fraction,
        "gates": json.dumps(result.gates, sort_keys=True),
    }
    row.update(config.as_dict())
    return row


def evaluate_trial(seed: int, family: str) -> list[dict[str, object]]:
    field = synthesize_field(seed, family)
    uniform = acquire_uniform(seed, family, field=field)
    adaptive = acquire_adaptive(seed, family, field=field)
    evaluated: list[tuple[Observation, CertificateResult]] = [
        (uniform, evaluate_baseline(uniform, "polygon_unconditional")),
        (uniform, evaluate_baseline(uniform, "margin_only")),
        (uniform, certify_observation(uniform, method="global_certificate", local_uncertainty=False, support_gate=False)),
        (uniform, certify_observation(uniform, method="local_certificate", local_uncertainty=True, support_gate=False)),
        (uniform, certify_observation(uniform, method="uniform_support_certificate", local_uncertainty=True, support_gate=True)),
        (adaptive, certify_observation(adaptive, method="adaptive_support_certificate", local_uncertainty=True, support_gate=True)),
        (adaptive, certify_observation(adaptive, method="adaptive_no_support", local_uncertainty=True, support_gate=False)),
        (
            adaptive,
            certify_observation(
                adaptive,
                method="adaptive_no_calibration",
                local_uncertainty=True,
                support_gate=True,
                include_calibration_residual=False,
            ),
        ),
        (adaptive, certify_observation(adaptive, method="adaptive_global_support", local_uncertainty=False, support_gate=True)),
        (uniform, evaluate_baseline(uniform, "oracle_dense")),
    ]
    return [_result_row(field, observation, result) for observation, result in evaluated]


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _code_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted((root / "src" / "toposense_sim").glob("*.py")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def summarize_benchmark(rows: list[dict[str, object]], bootstrap_resamples: int) -> dict[str, object]:
    overall = {method: summarize_rows([row for row in rows if row["method"] == method]) for method in METHODS}
    by_family = {
        family: {method: summarize_rows([row for row in rows if row["family"] == family and row["method"] == method]) for method in METHODS}
        for family in CONFIRMATORY_FAMILIES
    }
    adaptive = [row for row in rows if row["method"] == "adaptive_support_certificate"]
    global_rows = [row for row in rows if row["method"] == "global_certificate"]
    adaptive_no_support = [row for row in rows if row["method"] == "adaptive_no_support"]
    target_families = {"high_mode_na", "sector_dropout"}
    support_subset = [row for row in adaptive if row["family"] in target_families]
    no_support_subset = [row for row in adaptive_no_support if row["family"] in target_families]
    adaptive_summary = overall["adaptive_support_certificate"]
    global_summary = overall["global_certificate"]
    false_upper = wilson_upper(int(adaptive_summary["wrong_releases"]), int(adaptive_summary["n"]))
    goodput_bootstrap = paired_bootstrap_goodput(adaptive, global_rows, resamples=bootstrap_resamples)
    relative_goodput = (float(adaptive_summary["certified_goodput"]) - float(global_summary["certified_goodput"])) / max(
        float(global_summary["certified_goodput"]), 1e-12
    )
    support_metrics = summarize_rows(support_subset)
    no_support_metrics = summarize_rows(no_support_subset)
    false_reduction = (
        float(no_support_metrics["false_release_probability"]) - float(support_metrics["false_release_probability"])
    ) / max(float(no_support_metrics["false_release_probability"]), 1e-12)
    coverage_loss = float(no_support_metrics["coverage"]) - float(support_metrics["coverage"])
    hypotheses = {
        "T1_pass": float(overall["polygon_unconditional"]["false_release_probability"]) >= 0.05,
        "T2_pass": false_upper <= 0.01,
        "T3_pass": relative_goodput >= 0.20 and goodput_bootstrap["ci_low"] > 0.0 and false_upper <= 0.01,
        "T4_pass": false_reduction >= 0.50 and coverage_loss <= 0.15,
    }
    return {
        "overall": overall,
        "by_family": by_family,
        "false_release_wilson_upper": false_upper,
        "relative_goodput_improvement": relative_goodput,
        "paired_goodput_difference": goodput_bootstrap,
        "support_gate_false_release_reduction": false_reduction,
        "support_gate_coverage_loss": coverage_loss,
        "hypotheses": hypotheses,
        "registered_success": bool(hypotheses["T2_pass"] and hypotheses["T3_pass"]),
    }


def run_benchmark(
    output_dir: str | Path,
    *,
    seed_start: int = 1000,
    seeds_per_family: int = 100,
    bootstrap_resamples: int = 5000,
) -> dict[str, object]:
    if seed_start not in {0, 1000}:
        raise ValueError("registered starts are 0 (exploratory) and 1000 (confirmatory)")
    if seed_start == 1000 and seeds_per_family != 100:
        raise ValueError("full confirmation requires exactly 100 seeds per family")
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    rows = [row for family in CONFIRMATORY_FAMILIES for seed in range(seed_start, seed_start + seeds_per_family) for row in evaluate_trial(seed, family)]
    csv_path = output / "benchmark.csv"
    _write_csv(csv_path, rows)
    summary = summarize_benchmark(rows, bootstrap_resamples)
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    root = Path(__file__).resolve().parents[2]
    manifest = {
        "artifact": "TopoSense-Sim confirmatory benchmark" if seed_start == 1000 else "TopoSense-Sim exploratory benchmark",
        "protocol": "experiments/H1-certified-goodput/protocol.md",
        "seed_start": seed_start,
        "seeds_per_family": seeds_per_family,
        "families": list(CONFIRMATORY_FAMILIES),
        "methods": list(METHODS),
        "row_count": len(rows),
        "maximum_sample_budget": 32,
        "bootstrap_resamples": bootstrap_resamples,
        "code_sha256": _code_hash(root),
        "benchmark_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "summary_sha256": hashlib.sha256(summary_path.read_bytes()).hexdigest(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"rows": rows, "summary": summary, "manifest": manifest}
