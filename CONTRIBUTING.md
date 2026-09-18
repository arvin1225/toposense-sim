# Contributing

Contributions are welcome when they preserve the receiver's measurement, budget, and certification contracts.

## Before opening a change

1. Describe the optical mechanism, acquisition policy, or certificate boundary that motivates the change.
2. State whether the change affects propagation, noisy measurement, adaptive sampling, decoding, or a frozen protocol.
3. Never overwrite committed confirmatory outputs to fit revised code. Result-affecting work requires a new protocol and artifact identity.

## Development checks

```bash
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python scripts/validate_artifact.py --artifact artifacts/confirmatory --quick
python scripts/validate_h2_artifact.py artifacts/confirmatory-h2
python -m build
cd web && pnpm install --frozen-lockfile && pnpm run build
```

## Pull requests

- add a regression test for every changed scientific contract;
- preserve the equal measurement budget across compared acquisition policies;
- keep evaluator-only truth out of operational acquisition decisions;
- retain erasures, false releases, and failed registered hypotheses;
- document schema or protocol migrations;
- keep public documentation and interface text in English;
- do not generalize projected-boundary results to a full two-dimensional topological certificate.
