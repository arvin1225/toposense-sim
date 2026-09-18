"""Run the registered H2 benchmark."""

from __future__ import annotations

import argparse
import json

from toposense_sim.benchmark_v2 import run_h2_benchmark


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="artifacts/confirmatory-h2")
    parser.add_argument("--seed-start", type=int, default=2000)
    parser.add_argument("--seeds", type=int, default=100)
    parser.add_argument("--bootstrap", type=int, default=5000)
    args = parser.parse_args()
    result = run_h2_benchmark(
        args.out,
        seed_start=args.seed_start,
        seeds_per_family=args.seeds,
        bootstrap_resamples=args.bootstrap,
    )
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
