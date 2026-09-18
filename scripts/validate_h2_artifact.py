"""Validate an H2 artifact directory."""

from __future__ import annotations

import argparse
import json

from toposense_sim.validation_v2 import validate_h2_artifact


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default="artifacts/confirmatory-h2")
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    report = validate_h2_artifact(args.path, quick=args.quick)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["integrity"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

