"""Command-line entry points."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .benchmark import run_benchmark
from .validation import validate_artifact


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="toposense")
    commands = parser.add_subparsers(dest="command", required=True)
    benchmark = commands.add_parser("benchmark")
    benchmark.add_argument("--out", type=Path, default=Path("artifacts/confirmatory"))
    benchmark.add_argument("--quick", action="store_true")
    validate = commands.add_parser("validate")
    validate.add_argument("--artifact", type=Path, default=Path("artifacts/confirmatory"))
    validate.add_argument("--quick", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "benchmark":
        result = run_benchmark(
            args.out,
            seed_start=0 if args.quick else 1000,
            seeds_per_family=5 if args.quick else 100,
            bootstrap_resamples=200 if args.quick else 5000,
        )
        print(json.dumps({"rows": result["manifest"]["row_count"], "registered_success": result["summary"]["registered_success"]}, indent=2))
        return 0
    report = validate_artifact(args.artifact, quick=args.quick)
    print(json.dumps(report, indent=2))
    return 0 if report["integrity"] else 1
