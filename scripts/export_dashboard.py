"""Export exact confirmatory loops, samples, decisions and aggregate metrics."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from toposense_sim.certificate import certify_observation
from toposense_sim.config import CONFIRMATORY_FAMILIES
from toposense_sim.field import synthesize_field
from toposense_sim.receiver import acquire_adaptive, acquire_uniform


ROOT = Path(__file__).resolve().parents[1]


def floats(array: np.ndarray, digits: int = 6) -> list:
    return np.round(array.astype(float), digits).tolist()


def main() -> None:
    summary = json.loads((ROOT / "artifacts" / "confirmatory" / "summary.json").read_text(encoding="utf-8"))
    with (ROOT / "artifacts" / "confirmatory" / "benchmark.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    representatives = []
    for family in CONFIRMATORY_FAMILIES:
        polygon_rows = [row for row in rows if row["family"] == family and row["method"] == "polygon_unconditional"]
        chosen = next((row for row in polygon_rows if row["false_release"].lower() == "true"), polygon_rows[0])
        seed = int(chosen["seed"])
        field = synthesize_field(seed, family)
        uniform = acquire_uniform(seed, family, field=field)
        adaptive = acquire_adaptive(seed, family, field=field)
        result = certify_observation(adaptive)
        method_rows = {row["method"]: row for row in rows if row["family"] == family and int(row["seed"]) == seed}
        representatives.append(
            {
                "family": family,
                "seed": seed,
                "trueWinding": field.true_winding,
                "receivedDenseWinding": field.received_dense_winding,
                "ideal": floats(field.ideal_stokes[::16]),
                "received": floats(field.received_stokes[::16]),
                "uniform": {"angles": floats(uniform.nominal_angles), "stokes": floats(uniform.stokes), "bounds": floats(uniform.angular_error_bounds)},
                "adaptive": {"angles": floats(adaptive.nominal_angles), "stokes": floats(adaptive.stokes), "bounds": floats(adaptive.angular_error_bounds), "dropped": adaptive.dropped_count},
                "certificate": result.as_dict(),
                "methods": {
                    method: {
                        "released": row["released"].lower() == "true",
                        "correct": row["correct"].lower() == "true",
                        "observedWinding": int(row["observed_winding"]),
                        "releasedWinding": int(row["released_winding"]) if row["released_winding"] else None,
                        "margin": float(row["certificate_margin"]),
                    }
                    for method, row in method_rows.items()
                },
                "receiver": {
                    "photons": field.config.photons_per_analyzer,
                    "naCutoff": field.config.na_cutoff_mode,
                    "crosstalk": field.config.crosstalk,
                    "projectedBias": field.config.projected_bias,
                    "dropoutWidth": field.config.dropout_width_rad,
                    "idealHighModeFraction": field.ideal_high_mode_fraction,
                },
            }
        )
    payload = {
        "source": "artifacts/confirmatory/benchmark.csv",
        "summary": summary,
        "representatives": representatives,
        "methodLabels": {
            "polygon_unconditional": "Unconditional polygon",
            "margin_only": "Margin only",
            "global_certificate": "Global certificate",
            "local_certificate": "Local certificate",
            "uniform_support_certificate": "Uniform support",
            "adaptive_support_certificate": "Adaptive support",
        },
    }
    output = ROOT / "web" / "public" / "data"
    output.mkdir(parents=True, exist_ok=True)
    (output / "receiver.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"output": str(output / "receiver.json"), "representatives": len(representatives)}, indent=2))


if __name__ == "__main__":
    main()
