"""Exploratory bounded-loop stress study with analytic derivative bounds."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from toposense_bounds import certify_winding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/bounded-loop-study")
    args = parser.parse_args()
    rows, timings = [], []
    families = ("clear_loop", "near_origin", "high_frequency", "missing_sector", "multimode")
    for family in families:
        for seed in range(40):
            rng = np.random.default_rng(7100 + seed)
            k = (-1 if seed % 2 else 1) * (17 if family == "high_frequency" else 1)
            bias = 0.97 if family == "near_origin" else 0.15
            phase = rng.uniform(-np.pi, np.pi)
            harmonic = 0.18 if family == "multimode" else 0.0
            curve = lambda t: bias + np.exp(1j * (k * t + phase)) + harmonic * np.exp(-3j * t)
            bound = abs(k) + 3 * harmonic
            dense = curve(np.linspace(0, 2*np.pi, 16384, endpoint=False))
            truth = int(round(np.sum(np.angle(np.roll(dense, -1) * np.conj(dense))) / (2*np.pi)))
            for budget in (8, 16, 32):
                angles = np.linspace(0, 2*np.pi, budget, endpoint=False)
                if family == "missing_sector":
                    angles = angles[(angles < 0.6) | (angles > 3.1)]
                errors = np.full(len(angles), 0.035)
                noise = rng.uniform(0, 0.035, len(angles)) * np.exp(1j * rng.uniform(0, 2*np.pi, len(angles)))
                observed = curve(angles) + noise
                start = time.perf_counter_ns()
                result = certify_winding(angles, observed, errors, derivative_bound=bound)
                timings.append((time.perf_counter_ns() - start) / 1e6)
                for method, symbol in (("polygon", result.polygon_winding), ("bounded_tube", result.winding)):
                    rows.append({"family": family, "seed": seed, "budget": budget, "samples": len(angles), "method": method,
                                 "released": symbol is not None, "winding": symbol, "received_winding": truth,
                                 "wrong_release": symbol is not None and symbol != truth, "derivative_bound": bound,
                                 "minimum_margin": result.minimum_margin})
    args.out.mkdir(parents=True, exist_ok=True)
    csv_path = args.out / "trials.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {"study": "bounded received-loop winding", "status": "exploratory analytic-model stress test", "scenes": 600, "rows": len(rows), "methods": {}, "by_family": {},
               "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
               "source_sha256": hashlib.sha256((ROOT / "src/toposense_bounds/tube.py").read_bytes()).hexdigest()}
    def metrics(items):
        return {"trials": len(items), "releases": sum(r["released"] for r in items), "wrong_releases": sum(r["wrong_release"] for r in items), "coverage": sum(r["released"] for r in items)/len(items)}
    for method in ("polygon", "bounded_tube"):
        summary["methods"][method] = metrics([r for r in rows if r["method"] == method])
    for family in families:
        summary["by_family"][family] = {m: metrics([r for r in rows if r["method"] == m and r["family"] == family]) for m in summary["methods"]}
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    (args.out / "timing.json").write_text(json.dumps({"evaluations": len(timings), "median_ms": float(np.median(timings)), "p95_ms": float(np.quantile(timings, .95)), "note": "Local wall-clock measurements; hardware dependent."}, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if summary["methods"]["bounded_tube"]["wrong_releases"]:
        raise SystemExit("Bounded-loop regression: incorrect release under declared bounds")


if __name__ == "__main__":
    main()
